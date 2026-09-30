#!/usr/bin/env python3
"""Validate actual static poster pixels, frontpage title, and built HTTP resources.

Requires Playwright, PyYAML, Pillow and BeautifulSoup4 (tests only).
Normal mode serves the unmodified Jekyll output on localhost. --offline-dom is
for environments that prohibit browser top-level navigation: only root-relative
URLs are prefixed with an intercepted test origin. Actual site CSS/JS/JPEG bytes
are used. HTTP requests are independently checked against a local static server.
External scripts are stubbed and MP4 requests are rejected: poster tests must not
need either. This does not certify live Zenodo playback or MathJax rendering.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import mimetypes
from pathlib import Path
import re
import threading
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

from bs4 import BeautifulSoup
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--site', type=Path, default=Path('_site'))
    parser.add_argument('--baseurl', default='')
    parser.add_argument('--widths', default='390,1440')
    parser.add_argument('--offline-dom', action='store_true')
    parser.add_argument('--browser-executable')
    parser.add_argument('--report', type=Path, default=Path('docs/validation/poster-title-assets.json'))
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    source, root = args.source.resolve(), args.site.resolve()
    base = args.baseurl.rstrip('/')
    if not (root / 'index.html').is_file():
        parser.error('--site must point to a built Jekyll output directory')
    widths = [int(item) for item in args.widths.split(',')]
    report: dict = {'baseurl': base, 'browser_mode': 'offline rendered DOM' if args.offline_dom else 'localhost navigation',
                    'http_mode': 'independent local static HTTP server', 'widths': widths,
                    'checks': [], 'failures': [], 'posters': [], 'http': []}
    videos = yaml.safe_load((source / '_data/videos.yml').read_text(encoding='utf-8'))
    config = yaml.safe_load((source / '_config.yml').read_text(encoding='utf-8'))
    frontpage = yaml.safe_load((source / '_data/frontpage.yml').read_text(encoding='utf-8')) or {}
    home_title = str(frontpage.get('title') or '').strip() or str(config.get('title') or '').strip() or 'Home'
    pages = sorted(root.rglob('*.html'))
    by_src = {v['src']: v['poster'] for v in videos.values() if v.get('src')}
    poster_paths = sorted(set(by_src.values()))
    report.update(video_entries=len(videos), unique_referenced_posters=len(poster_paths), html_pages=len(pages), home_title=home_title)

    def check(name: str, function) -> None:
        try:
            value = function()
            report['checks'].append({'test': name, 'status': 'passed', 'details': value})
        except Exception as error:
            report['failures'].append({'test': name, 'error': str(error)})
            print('FAIL:', name, str(error), flush=True)

    def local_path(url: str) -> Path:
        path = unquote(urlsplit(url).path)
        if base:
            assert path == base or path.startswith(base + '/'), f'URL ignores baseurl: {url}'
            path = path[len(base):]
        file = (root / path.lstrip('/')).resolve()
        assert root == file or root in file.parents, f'URL escapes build: {url}'
        return file

    def verify_source_assets():
        for path in poster_paths:
            file = source / path.lstrip('/')
            with Image.open(file) as image:
                assert image.format == 'JPEG', str(file)
                image.verify()
            built = root / path.lstrip('/')
            assert built.read_bytes() == file.read_bytes(), f'Asset changed during build: {path}'
        return {'decoded_jpegs': len(poster_paths), 'unchanged_built_jpegs': len(poster_paths)}
    check('source JPEG decoding and unchanged built bytes', verify_source_assets)

    local_urls: set[str] = set()
    occurrence_count = 0
    for file in pages:
        relative = file.relative_to(root).as_posix()
        local_urls.add(base + '/' + relative)
        document = BeautifulSoup(file.read_text(encoding='utf-8'), 'html.parser')
        for element in document.find_all(True):
            for attribute in ('src', 'href', 'poster'):
                value = element.get(attribute)
                if value and value.startswith('/') and not value.startswith('//'):
                    local_urls.add(value.split('#', 1)[0])
        for video in document.select('.media-video video'):
            occurrence_count += 1
            def validate_markup(v=video, name=relative):
                assert v.source, f'{name}: source missing'
                original_src = v.source['src']
                expected = by_src[original_src]
                assert v.get('poster'), f'{name}: missing poster for {original_src}'
                assert urlsplit(v['poster']).path == base + expected, (name, v['poster'], expected)
                assert v.get('preload') == 'none', name
                assert not v.has_attr('data-first-frame'), name
                assert local_path(v['poster']).is_file(), v['poster']
                return {'page': name, 'src': original_src, 'poster': v['poster']}
            check(f'markup poster {relative} #{occurrence_count}', validate_markup)
    report['rendered_video_occurrences'] = occurrence_count

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_: object) -> None:
            pass

        def do_GET(self) -> None:
            if base:
                if self.path.startswith(base + '/'):
                    self.path = self.path[len(base):]
                else:
                    self.send_error(404, 'Outside configured baseurl')
                    return
            super().do_GET()

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    http_origin = f'http://127.0.0.1:{server.server_port}'
    try:
        def verify_http():
            for url in sorted(local_urls):
                with urlopen(http_origin + url, timeout=10) as response:
                    payload = response.read()
                    content_type = response.headers.get_content_type()
                    assert response.status == 200, url
                    if '/assets/posters/' in url:
                        assert content_type == 'image/jpeg', (url, content_type)
                        with Image.open(io.BytesIO(payload)) as image:
                            image.verify()
                    report['http'].append({'url': url, 'status': response.status, 'type': content_type})
            return {'requests': len(report['http']), 'all_200': True}
        check('HTTP pages and all referenced local resources', verify_http)

        with sync_playwright() as playwright:
            launch = {'headless': True}
            if args.browser_executable:
                launch['executable_path'] = args.browser_executable
            browser = playwright.chromium.launch(**launch)
            report['browser'] = 'Chromium ' + browser.version
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)

            # Both regular and JavaScript-disabled rendering must show real JPEGs.
            for javascript in (True, False):
                for width in widths:
                    context = browser.new_context(viewport={'width': width, 'height': 1000},
                                                  java_script_enabled=javascript, device_scale_factor=1)
                    page = context.new_page()
                    page.set_default_timeout(6000)
                    errors: list[str] = []
                    media_requests: list[str] = []
                    missing: list[str] = []
                    page.on('pageerror', lambda error: errors.append(str(error)))

                    def handle(route):
                        parsed = urlsplit(route.request.url)
                        if parsed.netloc == 'site.test':
                            try:
                                file = local_path(route.request.url)
                                if file.is_file():
                                    route.fulfill(path=str(file), content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream')
                                else:
                                    missing.append(route.request.url)
                                    route.fulfill(status=404, body='Missing local asset')
                            except Exception as error:
                                missing.append(str(error))
                                route.fulfill(status=404, body='Invalid local asset path')
                        elif parsed.path.lower().endswith('.mp4'):
                            media_requests.append(route.request.url)
                            route.fulfill(status=503, body='No MP4 is needed to display a local JPEG poster')
                        elif parsed.netloc == 'cdn.jsdelivr.net':
                            route.fulfill(body='/* External mathematics intentionally excluded. */', content_type='application/javascript')
                        else:
                            route.continue_()

                    page.route('**/*', handle)
                    for file in pages:
                        relative = file.relative_to(root).as_posix()
                        def verify_page():
                            if args.offline_dom:
                                text = file.read_text(encoding='utf-8')
                                text = re.sub(r'\b(src|href|poster)="(/[^\"]*)"',
                                              lambda m: f'{m[1]}="https://site.test{m[2]}"', text)
                                page.set_content(text, wait_until='load')
                            else:
                                page.goto(http_origin + base + '/' + relative, wait_until='load')
                            if relative == 'index.html':
                                assert page.locator('#home-title').is_visible()
                                assert page.locator('#home-title').inner_text().strip() == home_title
                                assert page.title() == home_title
                                assert page.locator('main h1').count() == 1
                                if args.screenshots and javascript:
                                    page.screenshot(path=str(args.screenshots / f'home-{width}.png'), full_page=True)
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), relative
                            players = page.locator('.media-video video')
                            for index in range(players.count()):
                                video = players.nth(index)
                                video.scroll_into_view_if_needed()
                                metadata = video.evaluate('''async v => {
                                    const image = new Image(); image.src = v.poster;
                                    await image.decode();
                                    return {poster: v.poster, width: image.naturalWidth, height: image.naturalHeight,
                                      paused: v.paused, time: v.currentTime, preload: v.preload,
                                      background: getComputedStyle(v).backgroundColor};
                                }''')
                                assert metadata['width'] > 0 and metadata['height'] > 0
                                assert metadata['paused'] and metadata['time'] == 0 and metadata['preload'] == 'none'
                                screenshot = Image.open(io.BytesIO(video.screenshot())).convert('RGB')
                                expected = Image.open(local_path(metadata['poster'])).convert('RGB')
                                scale = min(screenshot.width / expected.width, screenshot.height / expected.height)
                                expected = expected.resize((round(expected.width * scale), round(expected.height * scale)), Image.Resampling.LANCZOS)
                                rgb = tuple(int(n) for n in re.findall(r'\d+', metadata['background'])[:3])
                                reference = Image.new('RGB', screenshot.size, rgb)
                                reference.paste(expected, ((reference.width - expected.width)//2, (reference.height - expected.height)//2))
                                # Native controls cover the bottom of a paused video; compare the unobscured image.
                                crop = (5, 5, screenshot.width - 5, max(10, min(round(screenshot.height*.55), screenshot.height-75)))
                                error = sum(ImageStat.Stat(ImageChops.difference(screenshot.crop(crop), reference.crop(crop))).mean)/3
                                assert error < 12, f'Poster pixels mismatch {metadata["poster"]}: mean RGB error {error:.3f}'
                                report['posters'].append({'page': relative, 'index': index, 'width': width,
                                                          'javascript': javascript, 'poster': metadata['poster'],
                                                          'decoded_width': metadata['width'], 'decoded_height': metadata['height'],
                                                          'mean_pixel_error': round(error, 4)})
                                if args.screenshots and javascript:
                                    if (relative == 'thesis/chapter-06/index.html' and index == 0) or (relative == 'thesis/chapter-04/index.html' and index == 2):
                                        name = 'carousel' if 'chapter-06' in relative else 'duck-poster'
                                        video.screenshot(path=str(args.screenshots / f'{name}-{width}.png'))
                            assert not errors, errors
                            assert not missing, missing
                            assert not media_requests, media_requests
                            return {'page': relative, 'width': width, 'javascript': javascript, 'poster_pixels_checked': players.count(), 'mp4_requests': 0}
                        check(f'browser {relative} {width}px JS={javascript}', verify_page)
                    context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    report['passed'] = len(report['checks'])
    report['failed'] = len(report['failures'])
    report['pixel_comparisons'] = len(report['posters'])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"{report['passed']} passed; {report['failed']} failed; {report['pixel_comparisons']} poster pixel checks; {len(report['http'])} HTTP responses", flush=True)
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
