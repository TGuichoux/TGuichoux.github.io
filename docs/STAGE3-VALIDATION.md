# Stage 3 validation: permanent video deep links

## Source and delivered feature

Input: `supplementary-website 2.zip`, supplied in this conversation.
Output: `supplementary-webstie-stage3.zip` (the requested filename).
Runtime carousel script: version 3.2.0. No new runtime dependency.

All existing video IDs and page paths are retained. A link to
`/thesis/chapter-06/#ch06-6-10` reveals G-93 at slide 10/10. A link to
`/thesis/chapter-06/#ch06-6-13` reveals its separate standalone occurrence.
Both remain paused; navigating does not reset a previously played video.
No LaTeX mapping file or redirect page is generated.

## Results

| Check | Actual result |
| --- | --- |
| Jekyll rendering and the existing source/build checker | Passed at the root and `/repository-test`; 13 HTML pages per build. |
| Deep-link browser tests | **938 passed, 0 failed**: 469 in each deployment mode. |
| Full page/carousel/media regression tests | **190 passed, 0 failed**: 13 pages × 6 widths × 2 builds, plus 17 targeted cases per build. |
| URL-routing unit fixtures executing production JavaScript | **29 passed, 0 failed**. |
| Existing title/poster/template/launcher fixtures | **12 passed, 0 failed**. The launcher fixture mocks Bundler; it is not a real serve session. |
| Independent localhost HTTP requests | **138 HTTP 200 responses, 0 failures** across both builds. |
| Original versus new rendered pages | Text, every HTML ID, video URLs and poster paths unchanged on **13 pages**. |
| Source preservation | **156 of 160 original source files byte-identical**; four intentionally modified original files; no source files removed. |
| Protected chapter template | **Byte-for-byte identical** to the uploaded ZIP. |
| JavaScript, Python, Ruby and launcher syntax | Passed. |

The deep-link inventory contains **55 rendered video placements**, representing
**43 distinct video IDs**. Twelve IDs are reused on both a chapter and a paper;
this is valid because each document has its own URL. There are no duplicate HTML
IDs within any generated page. The complete destination inventory is in
`validation/stage3-deep-links-root.json` and its repository counterpart.

### Deep-link matrix details

The six widths are 375, 390, 640, 768, 1024, and 1440 pixels. For each deployment
mode, tests open each of the 55 placements with its fragment already present at
390px and 1440px (110 cases), then navigate to every placement on an already-open
page at all six widths (330 cases). The remaining 29 cases cover history,
repeated links, source reuse, malformed/encoded fragments, rapid notifications,
viewport changes, failure isolation, late layout changes and no-JavaScript use.

Each enhanced link check verifies the requested video, carousel alignment and
counter/selector, visible player geometry, a decoded local JPEG, paused state,
zero playback time for an unplayed clip, and no unexpected page overflow or
JavaScript exception. **No MP4 was requested by the static-preview/deep-link
matrix.** No-JavaScript cases compare native-player screenshot pixels against
the actual local JPEG rather than attempting a script-based image loader.

History tests exercise real `location.hash`, `history.back()` and
`history.forward()` inside the browser's same document. The repeated-link case
changes a slide manually, clicks its original link again, and verifies the
correct slide without a duplicate history entry. Duplicate MP4 sources retain
independent destinations. Sixty-one rapid fragment notifications resolve to the
last requested target. URL-routing unit fixtures also cover full, root-relative
and page-relative URLs at root and repository paths, query strings, modifier
clicks, new tabs, downloads, unknown IDs and malformed percent encoding.

### Regression caught and fixed before delivery

The first full matrix caught a real vertical-positioning problem at 640px,
768px and 1024px: lazy figures above the standalone G-93 example expanded after
the initial scroll and pushed the player partly below the viewport. The release
now realigns the arrival during a bounded three-second settling period. A single
ResizeObserver and captured image-load events handle that reflow; the observer
and pending frame are cancelled immediately on user input. There is no endless
polling and no waiting for a remote video or MathJax request.

The final matrix includes late 600px layout-shift checks, a legacy-observer
fallback case, and a check that a manual carousel selection is not undone by a
subsequent layout change. An ordinary late `pageshow` does not reselect a video;
a persisted `pageshow` reapplies the destination. The latter is an event-level
simulation, not a certification of the browser's real back/forward cache.

### Existing media and navigation coverage

The 190 regression cases cover every page at six widths in both builds,
Previous/Next and boundaries, dropdown selection, keyboard navigation, real
browser touch sequences and mouse/trackpad gestures, resize handling, independent
groups, print layout, no-JavaScript fallback, a blocked menu script, a pending
MathJax request, missing observer APIs, poster display, playback pausing without
rewinding, host-failure/Retry wiring, an idle poster beyond the loading timeout,
and both new hash-navigation playback cases. The playback tests use a generated
four-second H.264/AAC fixture, including byte-range responses and no CORS headers.
They do **not** stream the user's live Zenodo videos.

## Environment and limitations

Browser: **Chromium 144.0.7559.96** on Linux through Playwright.

Top-level browser HTTP navigation is blocked by this execution environment
(`ERR_BLOCKED_BY_ADMINISTRATOR`). The browser tests therefore use their documented
`--offline-dom` mode: the actual generated Jekyll HTML is loaded with
`set_content`, and only root-relative resource URLs are prefixed with an
intercepted test origin. CSS, JavaScript and JPEGs are the actual build files,
not reimplementations. Localhost HTTP responses are verified independently.
This is **not** a real end-to-end PDF click through a deployed GitHub Pages site.

Network access to RubyGems is unavailable. Builds use the real cached Jekyll
4.4.1, Liquid 4.0.4 and Kramdown 2.5.2 rendering pipeline through an external
QA driver. The unused Sass converter is omitted because its cached native
dependency targets macOS; this website has no Sass/SCSS. The source `Gemfile`,
`Gemfile.lock` and `.ruby-version` are unchanged. No build driver, dependency
shim, cached gems or machine-specific bundle is in the delivered archive.
A fresh `bundle install` and a normal `bundle exec jekyll serve` process were not
certified here.

Actual macOS Safari, iOS/Android devices, Firefox, live Zenodo playback, external
MathJax rendering, real cross-document/bfcache restoration, the user's PDF viewer
and the eventual public hostname/repository are not certified by these tests.
The arrival correction is intentionally bounded; images or third-party layout
changes occurring after three seconds are not forcibly recentered. User input
always takes priority. These limits are not counted as passed tests.

## Source changes

| File | Change |
| --- | --- |
| `assets/js/carousel.js` | Extend the existing hash navigation, reuse slide selection, preserve history, support standalone/repeated links, pause without rewind, and stabilize initial layout. |
| `assets/css/main.css` | Add anchor scroll margins only. Font sizes, widths and normal layout rules are unchanged. |
| `README.md` | Add permanent-link construction, examples, manual LaTeX use, stability rules, behavior and test commands. |
| `scripts/test_carousel.py` | Update the version assertion and add two hash/playback regression cases. |
| `scripts/test_video_links.py` | New browser deep-link matrix and edge-case tests, with ordinary HTTP mode available for local use. |
| `scripts/test_video_link_urls.cjs` | New URL-routing unit tests against the actual production script. |
| `docs/STAGE3-VALIDATION.md`, `docs/validation/stage3-*`, `docs/stage3-screenshots/` | This report, machine-readable results, source checksums and screenshots. |

All `_data`, `_chapters`, `_papers`, `_includes`, `_layouts`, image and poster
files are unchanged. Source chapter/paper text, captions, visible numbering,
video keys and MP4 URLs are preserved. Only generated `_site` output, caches and
macOS ZIP metadata were omitted from packaging; these are not website sources.

`chapter-template.md` SHA-256:

```text
580fb1877a77aef31acb8c5677059e3d894befb19db7df6d884cfb8620fc471c
```

## Packaging and repeatability

The full matrices above were run on source extracted from a clean candidate ZIP,
not just a working directory. The final delivery is also extracted into a new
directory, checked against `validation/stage3-source-sha256.json`, rebuilt at both
base paths, and subjected to a further direct-link pass before delivery. Extra
final-package results are supplied alongside the ZIP rather than changing its
already-tested contents.

The checksum manifest covers all non-documentation source files, including
README, tests and dependency declarations. Documentation/results are excluded
from that manifest to avoid recursive self-checksumming. The separate source
preservation report compares the original uploaded ZIP to the revised source.

To reproduce the main checks with a normal Ruby/Bundler installation:

```bash
bundle install
bundle exec jekyll build --baseurl "" --destination _site
ruby scripts/check.rb --baseurl "" _site
bundle exec jekyll build --baseurl "/repository-test" --destination _site-repository
ruby scripts/check.rb --baseurl "/repository-test" _site-repository

python3 -m pip install playwright beautifulsoup4 pillow
python3 -m playwright install chromium
python3 scripts/test_video_links.py --site _site --report docs/validation/local-video-links.json
python3 scripts/test_video_links.py --site _site-repository --baseurl /repository-test --report docs/validation/repository-video-links.json
node scripts/test_video_link_urls.cjs
python3 scripts/test_carousel.py --site _site --report docs/validation/local-carousel.json
python3 scripts/test_carousel.py --site _site-repository --baseurl /repository-test --report docs/validation/repository-carousel.json
```

FFmpeg is required by the existing carousel/media regression script. The test
dependencies above are optional development tools, not website dependencies.
Normal test mode uses real localhost browser navigation; only use
`--offline-dom` when an environment explicitly requires that reduced-scope mode.

Screenshots: `stage3-screenshots/deep-link-390.png` and
`stage3-screenshots/deep-link-1440.png` show the selected middle slide and its
native static poster. The README lists actual first, middle, last and standalone
URLs. Do not put a localhost URL into a published manuscript.
