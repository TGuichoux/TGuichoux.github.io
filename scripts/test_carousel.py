#!/usr/bin/env python3
"""Browser regression tests for the built site.

Normal mode serves the exact Jekyll output over localhost. The optional
--offline-dom mode is for environments that prohibit top-level browser
navigation: it loads the exact rendered HTML with set_content and rewrites only
root-relative resource URLs to an intercepted test origin. The actual CSS/JS
files are served unchanged. This mode does NOT verify HTTP navigation.

Remote video requests are fulfilled with a generated four-second H.264 fixture,
without CORS headers. MathJax is stubbed; these tests do not validate its renderer
or the live Zenodo service. Nothing is written into the site's content/assets.

Requires Python 3, Playwright, and FFmpeg. No Python dependency is used by Jekyll.
"""
from __future__ import annotations
import argparse
import base64
import functools
import http.server
import json
import mimetypes
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time
from urllib.parse import unquote, urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default="_site", type=Path)
    parser.add_argument("--baseurl", default="")
    parser.add_argument("--browser-executable")
    parser.add_argument("--offline-dom", action="store_true")
    parser.add_argument("--widths", default="375,390,640,768,1024,1440")
    parser.add_argument("--report", default="docs/carousel-browser-results.json", type=Path)
    parser.add_argument("--skip-special", action="store_true")
    parser.add_argument("--special-only", action="store_true", help="Skip the page matrix; run targeted behavior checks only.")
    parser.add_argument("--special-tests", default="", help="Comma-separated names to select targeted behavior checks.")
    args = parser.parse_args()
    root = args.site.resolve()
    if not root.is_dir():
        parser.error("Build Jekyll first; --site must point to its output directory.")
    base = args.baseurl.rstrip("/")
    widths = [int(w) for w in args.widths.split(",")]
    report = {"mode": "offline rendered DOM" if args.offline_dom else "localhost HTTP", "baseurl": base,
              "widths": widths, "browser": "", "video_source": "synthetic H.264 fixture; no Access-Control-Allow-Origin header",
              "external_limitations": "Live Zenodo downloads and MathJax rendering are not tested.", "checks": [], "failures": []}

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_: object) -> None:
            pass

        def do_GET(self) -> None:
            if base and self.path.startswith(base + "/"):
                self.path = self.path[len(base):]
            super().do_GET()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = "https://site.test" if args.offline_dom else f"http://127.0.0.1:{server.server_port}"

    with tempfile.TemporaryDirectory(prefix="carousel-tests-") as temp:
        fixture = Path(temp) / "test.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc2=size=640x360:rate=25:duration=4", "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
                        "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", "-y", str(fixture)], check=True)
        media = fixture.read_bytes()
        with sync_playwright() as pw:
            kwargs = {"headless": True}
            if args.browser_executable:
                kwargs["executable_path"] = args.browser_executable
            browser = pw.chromium.launch(**kwargs)
            report["browser"] = "Chromium " + browser.version

            def make_page(width: int, javascript: bool = True, fail_media: bool = False,
                          block_site_js: bool = False, hold_math: bool = False, legacy: bool = False):
                context = browser.new_context(viewport={"width": width, "height": 1000},
                                              is_mobile=width <= 640, has_touch=width <= 640,
                                              java_script_enabled=javascript)
                page = context.new_page()
                page.set_default_timeout(6000)
                errors = []
                pending = []
                requests = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                if legacy:
                    page.add_init_script("window.ResizeObserver = undefined; window.IntersectionObserver = undefined;")
                    if args.offline_dom:
                        page.evaluate("window.ResizeObserver = undefined; window.IntersectionObserver = undefined;")

                def handle(route):
                    parsed = urlparse(route.request.url)
                    requests.append(route.request.url)
                    if parsed.netloc == "cdn.jsdelivr.net":
                        if hold_math:
                            pending.append(route)
                        else:
                            route.fulfill(body="/* MathJax intentionally not part of this media test. */", content_type="application/javascript")
                        return
                    if parsed.netloc == "zenodo.org" and parsed.path.lower().endswith(".mp4"):
                        if fail_media:
                            route.fulfill(status=503, body="Deliberate media-host failure fixture.")
                        else:
                            range_value = route.request.headers.get("range", "")
                            match = re.fullmatch(r"bytes=(\d+)-(\d*)", range_value)
                            headers = {"accept-ranges": "bytes"}
                            if match:
                                start = int(match.group(1)); end = min(int(match.group(2)) if match.group(2) else len(media)-1, len(media)-1)
                                headers["content-range"] = f"bytes {start}-{end}/{len(media)}"
                                route.fulfill(status=206, body=media[start:end+1], content_type="video/mp4", headers=headers)
                            else:
                                route.fulfill(body=media, content_type="video/mp4", headers=headers)
                        return
                    if parsed.netloc == "site.test":
                        path = unquote(parsed.path)
                        if base and path.startswith(base + "/"):
                            path = path[len(base):]
                        file = root / path.lstrip("/")
                        if block_site_js and file.name == "site.js":
                            route.abort()
                        elif file.is_file():
                            route.fulfill(path=str(file), content_type=mimetypes.guess_type(file)[0] or "application/octet-stream")
                        else:
                            route.fulfill(status=404, body="Missing test asset")
                        return
                    if block_site_js and parsed.path.endswith("/assets/js/site.js"):
                        route.abort()
                    else:
                        route.continue_()

                page.route("**/*", handle)
                return context, page, errors, pending, requests

            def load(page, relative: Path, timeout: int = 15000):
                if args.offline_dom:
                    text = (root / relative).read_text(encoding="utf-8")
                    text = re.sub(r'\b(src|href|poster)="(/[^\"]*)"', lambda m: f'{m[1]}="{origin}{m[2]}"', text)
                    page.set_content(text, wait_until="load", timeout=timeout)
                else:
                    urlpath = relative.as_posix()
                    if urlpath.endswith("index.html"):
                        urlpath = urlpath[:-10]
                    page.goto(origin + base + "/" + urlpath, wait_until="load", timeout=timeout)

            def assert_slide(page, carousel, index: int):
                # Wait for native scroll events/animation frames to update the toolbar.
                ident = carousel.get_attribute("id")
                page.wait_for_function("a => document.getElementById(a.id).dataset.activeSlide === String(a.index+1)",
                                       arg={"id": ident, "index": index}, timeout=4000)
                # A browser's native ArrowRight scrolling can briefly move a
                # focused, unloaded video before CSS scroll-snap settles back.
                page.wait_for_function("""a => {
                  const c = document.getElementById(a.id);
                  const t = c.querySelector('[data-carousel-slides]');
                  const s = t.querySelectorAll('[data-carousel-slide]')[a.index];
                  return Math.abs(s.getBoundingClientRect().left - t.getBoundingClientRect().left) <= 2;
                }""", arg={"id": ident, "index": index}, timeout=4000)
                state = carousel.evaluate("""c => {
                  const t=c.querySelector('[data-carousel-slides]'), s=[...t.querySelectorAll('[data-carousel-slide]')];
                  const index=Number(c.dataset.activeSlide)-1, r=s[index].getBoundingClientRect(), tr=t.getBoundingClientRect();
                  return {active:index,n:s.length,select:c.querySelector('select').value,
                    counter:c.querySelector('[data-carousel-counter]').textContent.trim(),
                    offset:Math.abs(r.left-tr.left),width:Math.abs(r.width-tr.width),
                    hidden:s.some(x=>x.hidden),previous:c.querySelector('[data-carousel-previous]').getAttribute('aria-disabled'),
                    next:c.querySelector('[data-carousel-next]').getAttribute('aria-disabled')};
                }""")
                assert state["active"] == index, state
                assert state["select"] == str(index), state
                assert state["counter"] == f"{index+1} / {state['n']}", state
                assert state["offset"] <= 2 and state["width"] <= 2, state
                assert not state["hidden"], state
                assert state["previous"] == str(index == 0).lower(), state
                assert state["next"] == str(index == state["n"]-1).lower(), state

            pages = sorted(root.rglob("*.html"))
            for width in ([] if args.special_only else widths):
                for file in pages:
                    relative = file.relative_to(root)
                    print("Testing", relative, width, flush=True)
                    context, page, errors, pending, requests = make_page(width)
                    try:
                        load(page, relative)
                        page.wait_for_function("document.documentElement.dataset.carouselVersion === '3.2.0'")
                        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
                        assert not overflow, "Page has horizontal overflow outside the carousel."
                        groups = page.locator("[data-video-carousel]")
                        traversed = 0
                        for group_index in range(groups.count()):
                            carousel = groups.nth(group_index)
                            n = carousel.locator("[data-carousel-slide]").count()
                            assert n > 1
                            carousel.locator("[data-carousel-next]").scroll_into_view_if_needed()
                            assert_slide(page, carousel, 0)
                            for index in range(1, n):
                                carousel.locator("[data-carousel-next]").click()
                                assert_slide(page, carousel, index)
                            carousel.locator("[data-carousel-next]").click(force=True)
                            assert_slide(page, carousel, n-1)
                            for index in range(n-2, -1, -1):
                                carousel.locator("[data-carousel-previous]").click()
                                assert_slide(page, carousel, index)
                            carousel.locator("[data-carousel-select]").select_option(str(n-1))
                            assert_slide(page, carousel, n-1)
                            carousel.locator("[data-carousel-slides]").focus()
                            page.keyboard.press("Home"); assert_slide(page, carousel, 0)
                            page.keyboard.press("ArrowRight"); assert_slide(page, carousel, 1)
                            page.keyboard.press("End"); assert_slide(page, carousel, n-1)
                            page.keyboard.press("Home"); assert_slide(page, carousel, 0)
                            traversed += n
                        assert not errors, errors
                        report["checks"].append({"test": "page and full carousel traversal", "page": str(relative), "width": width,
                                                 "carousels": groups.count(), "slides": traversed, "status": "passed"})
                    except Exception as error:
                        report["failures"].append({"test": "page traversal", "page": str(relative), "width": width, "error": str(error)})
                        print("FAIL", relative, width, error, flush=True)
                    finally:
                        context.close()
                print("Completed width", width, flush=True)

            if not args.skip_special:
                chapter = Path("thesis/chapter-06/index.html")
                specials = ["poster and playback pause", "trackpad and resize", "touch swipe", "no JavaScript",
                            "failed media host", "unavailable site.js", "pending MathJax", "missing observers", "deep link", "initial deep link", "mouse drag", "video keyboard", "independent groups", "print", "idle static posters", "deep link pauses playback", "same-link replay stays paused"]
                if args.special_tests:
                    selected = {item.strip() for item in args.special_tests.split(",")}
                    unknown = selected.difference(specials)
                    if unknown:
                        raise ValueError("Unknown special tests: " + ", ".join(sorted(unknown)))
                    specials = [name for name in specials if name in selected]
                for name in specials:
                    print("Special test:", name, flush=True)
                    context, page, errors, pending, requests = make_page(
                        390 if name == "touch swipe" else 1440, javascript=name != "no JavaScript",
                        fail_media=name == "failed media host", block_site_js=name == "unavailable site.js",
                        hold_math=name == "pending MathJax", legacy=name == "missing observers")
                    try:
                        try:
                            if name == "initial deep link" and args.offline_dom:
                                page.evaluate("location.hash='ch06-6-8'")
                            current_chapter = Path("thesis/chapter-04/index.html") if name == "independent groups" else chapter
                            load(page, current_chapter, 700 if name == "pending MathJax" else 15000)
                        except PlaywrightTimeout:
                            if name != "pending MathJax":
                                raise
                        carousel = page.locator("[data-video-carousel]").first
                        track = carousel.locator("[data-carousel-slides]")
                        video = carousel.locator("video").first
                        if name == "poster and playback pause":
                            video.scroll_into_view_if_needed()
                            if video.get_attribute("poster"):
                                assert not any(urlparse(url).path.lower().endswith(".mp4") for url in requests), requests
                                assert video.evaluate("v=>v.paused && v.currentTime === 0")
                            else:
                                page.wait_for_function("document.querySelector('video').readyState >= 2 && !document.querySelector('video').seeking")
                            video.evaluate("async v=>{v.muted=true;await v.play();}")
                            state = video.evaluate("v=>({w:v.videoWidth,h:v.videoHeight,origin:new URL(v.currentSrc).origin})")
                            assert state["w"] == 640 and state["h"] == 360, state
                            assert state["origin"] == "https://zenodo.org", state
                            page.wait_for_timeout(350)
                            carousel.locator("[data-carousel-next]").click()
                            paused_time = video.evaluate("v=>{if(!v.paused)throw Error('Hidden audio is still playing');return v.currentTime;}")
                            assert paused_time > 0.1
                            page.wait_for_timeout(200)
                            carousel.locator("[data-carousel-previous]").click()
                            assert abs(video.evaluate("v=>v.currentTime")-paused_time) < 0.03
                        elif name == "deep link pauses playback":
                            video.scroll_into_view_if_needed()
                            video.evaluate("async v=>{v.muted=true;await v.play();}")
                            page.wait_for_timeout(350)
                            before = video.evaluate("v=>v.currentTime")
                            assert before > 0.1
                            page.evaluate("location.hash='ch06-6-13'")
                            page.wait_for_timeout(150)
                            assert video.evaluate("v=>v.paused")
                            saved = video.evaluate("v=>v.currentTime")
                            assert saved >= before
                            assert page.locator("#ch06-6-13 video").evaluate("v=>v.paused && v.currentTime===0")
                            page.evaluate("location.hash='ch06-6-1'")
                            assert_slide(page, carousel, 0)
                            assert video.evaluate("v=>v.paused")
                            assert abs(video.evaluate("v=>v.currentTime")-saved) < 0.03
                        elif name == "same-link replay stays paused":
                            page.evaluate("location.hash='ch06-6-1'")
                            assert_slide(page, carousel, 0)
                            video.evaluate("async v=>{v.muted=true;await v.play();}")
                            page.wait_for_timeout(300)
                            page.evaluate("(()=>{const a=document.createElement('a');a.href='#ch06-6-1';a.id='qa-repeated-link';a.textContent='Video';document.body.prepend(a);})()")
                            before = page.evaluate("history.length")
                            page.locator("#qa-repeated-link").click()
                            page.wait_for_timeout(100)
                            assert video.evaluate("v=>v.paused && v.currentTime>0")
                            assert page.evaluate("history.length") == before
                            assert_slide(page, carousel, 0)
                        elif name == "trackpad and resize":
                            track.scroll_into_view_if_needed()
                            box = track.bounding_box()
                            page.mouse.move(box["x"]+box["width"]/2, box["y"]+30)
                            page.mouse.wheel(box["width"]*1.1, 0)
                            page.wait_for_timeout(800)
                            assert int(carousel.get_attribute("data-active-slide")) > 1
                            carousel.locator("select").select_option("6")
                            page.set_viewport_size({"width": 768, "height": 1000})
                            page.wait_for_timeout(250)
                            assert_slide(page, carousel, 6)
                        elif name == "touch swipe":
                            # A real browser touch sequence on the caption, not a JS scroll assignment.
                            caption = carousel.locator("figcaption").first
                            caption.scroll_into_view_if_needed()
                            box = caption.bounding_box()
                            session = context.new_cdp_session(page)
                            x = box["x"]+box["width"]*.88; y = box["y"]+15
                            session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y}]})
                            for step in range(1, 9):
                                session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x-box["width"]*.8*step/8, "y": y}]})
                                page.wait_for_timeout(25)
                            session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                            page.wait_for_timeout(700)
                            assert int(carousel.get_attribute("data-active-slide")) >= 2
                        elif name == "no JavaScript":
                            assert not carousel.locator("[data-carousel-controls]").is_visible()
                            assert track.evaluate("t=>t.scrollWidth>t.clientWidth*2")
                            carousel.locator("[data-carousel-link]").first.click()
                            page.wait_for_timeout(250)
                            assert track.evaluate("t=>t.scrollLeft>t.clientWidth*.9")
                        elif name == "failed media host":
                            video.scroll_into_view_if_needed()
                            # Static posters must not contact the host until play.
                            video.evaluate("v=>{v.muted=true;v.play().catch(()=>{});}")
                            carousel.locator("[data-video-status]").first.wait_for(state="visible")
                            carousel.locator("[data-video-retry]").first.click()
                            assert video.get_attribute("poster")
                            carousel.locator("[data-carousel-next]").click()
                            assert_slide(page, carousel, 1)
                        elif name in {"unavailable site.js", "pending MathJax", "missing observers"}:
                            carousel.locator("[data-carousel-next]").click()
                            assert_slide(page, carousel, 1)
                            if name == "missing observers":
                                assert page.evaluate("typeof window.IntersectionObserver") == "undefined"
                            if name == "pending MathJax":
                                assert len(pending) > 0, "No MathJax request was held open."
                        elif name == "deep link":
                            page.evaluate("location.hash='ch06-6-8'")
                            page.wait_for_timeout(300)
                            assert_slide(page, carousel, 7)
                        elif name == "initial deep link":
                            if not args.offline_dom:
                                page.goto(origin + base + "/thesis/chapter-06/#ch06-6-8", wait_until="load")
                            assert_slide(page, carousel, 7)
                        elif name == "mouse drag":
                            caption = carousel.locator("figcaption").first
                            caption.scroll_into_view_if_needed()
                            box = caption.bounding_box()
                            x = box["x"] + box["width"]*.88
                            y = box["y"] + 12
                            page.mouse.move(x, y); page.mouse.down()
                            page.mouse.move(x-box["width"]*.75, y, steps=12)
                            page.mouse.up(); page.wait_for_timeout(200)
                            assert_slide(page, carousel, 1)
                        elif name == "video keyboard":
                            video.focus()
                            page.keyboard.press("ArrowRight")
                            assert_slide(page, carousel, 0)
                        elif name == "independent groups":
                            other = page.locator("[data-video-carousel]").nth(1)
                            carousel.locator("select").select_option("2")
                            other.locator("select").select_option("1")
                            assert_slide(page, carousel, 2)
                            assert_slide(page, other, 1)
                        elif name == "idle static posters":
                            assert video.get_attribute("poster")
                            # A loadstart notification is possible even when
                            # preload=none suspends fetching. Do not call load():
                            # that is an explicit request to reset/load media.
                            video.evaluate("v=>v.dispatchEvent(new Event('loadstart'))")
                            page.wait_for_timeout(21000)
                            assert not carousel.locator("[data-video-status]").first.is_visible()
                            assert video.evaluate("v=>v.paused && v.currentTime === 0 && v.preload === 'none'")
                            assert not any(urlparse(url).path.lower().endswith(".mp4") for url in requests), requests
                            carousel.locator("[data-carousel-next]").click()
                            assert_slide(page, carousel, 1)
                        elif name == "print":
                            page.emulate_media(media="print")
                            assert track.evaluate("t=>getComputedStyle(t).display") == "block"
                            assert not carousel.locator("[data-carousel-controls]").is_visible()
                            assert carousel.locator("[data-carousel-slide]").count() == 10
                        assert not errors, errors
                        report["checks"].append({"test": name, "status": "passed"})
                    except Exception as error:
                        report["failures"].append({"test": name, "error": str(error)})
                        print("FAIL", name, error, flush=True)
                    finally:
                        for route in pending:
                            try:
                                route.abort()
                            except Exception:
                                pass
                        context.close()
            browser.close()
    server.shutdown()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    report["passed"] = len(report["checks"])
    report["failed"] = len(report["failures"])
    args.report.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(f"{report['passed']} checks passed; {report['failed']} failed. Report: {args.report}")
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
