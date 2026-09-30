# Poster and homepage-title validation

Date: 2026-09-30. Input: `supplementary-website-stage2(1).zip`.

## What was actually wrong, and what was not reproduced

The uploaded registry named `/assets/posters/gelina-duck-female.jpg` for
`ch04-4_3`, but the supplied image is `gelina-duck_female.jpg` (underscore).
The source checker reproduced this single missing local asset. The fix changes
only that entry's `poster` value; the MP4 source URL is unchanged.

The other 42 entries already referenced existing JPEGs. An original-source build
and a browser check showed the A-421 poster correctly before the repair. The
blanket failure of every poster reported on the user's machine was **not
reproduced**. A stale generated site, a different source folder/server, or a
browser-specific issue remains a possibility, not a proven diagnosis. This
release includes a source-pinned clean launcher and local poster cache versions.

The original home layout already rendered `site.data.frontpage.title` as an H2.
A fresh original-source build displayed “Téo Guichoux's personal space” visibly.
However, the browser-tab title was `Home · Academic supplementary material`,
coming from `index.md` and `_config.yml`, not from the frontpage data. The shared
`_includes/home-title.html` now supplies both the visible home H1 and home tab.
An absent or blank data title falls back to the site title, then to `Home`.
The masthead/sidebar name remains controlled by `_data/author.yml`.

A separate regression existed after removal of `data-first-frame`: the old
JavaScript attached error/retry listeners only to players with that attribute.
It now initializes error/retry handling for all media-video players, but only
opts into dynamic first-frame loading when there is no static poster. Static
previews keep `preload="none"` and make no automatic MP4 request. An idle
`loadstart` notification does not cause a spurious error 20 seconds later.

Regression testing also caught native ArrowRight scrolling an unloaded player's
surrounding carousel. Before metadata is available, the handler prevents that
unintended left/right scroll; loaded players retain their native keyboard
handling. The carousel's existing navigation and pause-position behavior remain.

## Executed results against a fresh archive extraction

The production source was packaged, extracted into a new directory, built at
both `/` and `/thesis-supplement`, and tested there. Final packaging only added
or updated excluded documentation/evidence. Tested production hashes are in
`validation/poster-title-tested-source-sha256.json`.

| Check | Result |
| --- | --- |
| Actual Jekyll rendering at root and repository path | Passed; 13 HTML pages each, subject to the build-harness limits below. |
| Source metadata, duplicate keys/IDs, local assets, internal links/fragments, and baseurl | Passed for both builds. |
| Explicit poster mappings | All 43 entries resolve to 40 distinct existing JPEGs. |
| JPEG preservation | All 42 supplied poster JPEGs remain byte-identical; two are extra unreferenced assets retained from the input. |
| Rendered players | All 55 player occurrences (some videos appear in both paper and thesis pages) have the correct static poster and `preload="none"`. |
| Independent local HTTP requests | 81 root + 81 repository-path requests, all HTTP 200; JPEG content types and decoding also checked. |
| Actual poster screenshot-to-JPEG comparisons | 220 root + 220 repository-path comparisons, all passed. |
| Image-test modes | 390px and 1440px, each with JavaScript enabled and disabled, on both paths. |
| MP4 requests during static-preview checks | Zero, including traversal to every player. |
| Responsive page/carousel traversal | 13 pages × 6 widths = 78 cases passed. |
| Additional repository-path carousel traversal | 13 pages × 2 widths = 26 cases passed. |
| Targeted interaction checks | 15 passed. |
| Template/validation/launcher fixtures | 12 passed. |
| JavaScript, Ruby and shell syntax | Checked with Node, Ruby and Bash. |
| Protected chapter template | Byte-for-byte unchanged. |

The screenshot check decodes the actual referenced JPEG and compares it with the
unobscured part of the native player's screenshot, excluding the lower native
control overlay. All images are the user's supplied images, not test patterns.
The maximum observed mean absolute RGB-channel difference was **4.8577**
on a 0–255 scale; the acceptance threshold was 12. File identity, source-to-poster
mapping, natural dimensions and unchanged source/built bytes were separately
verified. This verifies display of the supplied JPEGs; it does not independently
prove they are the first frame of the remotely hosted MP4s.

### Fifteen targeted interaction checks

Static poster and playback pause/position; trackpad navigation and resize; touch
swipe; no-JavaScript fallback links; failed media host and retry wiring;
unavailable `site.js`; pending MathJax; missing observer APIs; changed hash;
initial deep link; mouse drag; video keyboard isolation; independent groups;
print layout; and 21 seconds of idle static-poster display following a simulated
`loadstart` notification. No idle MP4 request or false load-error notice occurred.

Playback tests use a clearly synthetic four-second H.264/AAC fixture in place of
remote responses, without CORS headers. It is not shipped in the website. The
actual JPEGs remain in place during these tests. A failed-host response is
intentional and is not evidence about Zenodo's current availability.

### Twelve fixture checks

Editing the title (including Unicode, quotes and HTML-sensitive characters);
blank title fallback; missing data-file fallback; both titles blank; explicit
poster precedence; matching generated-poster fallback; stale generated poster
rejection; local query-string/base-path handling; external poster URL handling;
missing-image detection; incorrect built-heading detection; and launcher source
resolution in a directory with spaces. The launcher test mocks `bundle` to
verify command orchestration and runs the real Ruby source validator; it is not
a real Bundler/Jekyll server installation test.

## Environment and limits

Browser: **Chromium 144.0.7559.96 on Linux**, through Playwright. Widths used for the full
matrix: 375, 390, 640, 768, 1024 and 1440px. Mobile viewport/touch emulation was
used; a physical phone, macOS Safari/WebKit and Firefox were not tested.

Top-level browser navigation is blocked by the preparation environment. Browser
checks therefore used the scripts' documented **`--offline-dom`** mode: the exact
rendered HTML is loaded into the browser and only root-relative resource URLs
are given an intercepted test origin. CSS, JavaScript and JPEG bytes are the
actual unchanged build output. Independent HTTP checks serve the same built files
from a local static server. These are not end-to-end browser navigation tests of
`jekyll serve` on macOS.

RubyGems network access was unavailable. The real Jekyll 4.4.1, Liquid 4.0.4 and
Kramdown 2.5.2 libraries cached in the earlier supplied archive were used to run
Jekyll's rendering pipeline. The unused Sass converter was not loaded because
its cached native dependency targets macOS; this website contains no Sass/SCSS.
Ruby's installed JSON library was used. **A fresh `bundle install` and normal
`bundle exec jekyll serve` process were not certified in this environment.**
No cached gems, dependency shims, runtime harness, or machine-specific bundle is
included in the delivered website. The original Gemfile and lockfile are intact.

Live Zenodo video playback, remote paper links and MathJax's external renderer
were not verified. Static previews do not require any of them. The poster tests
stub external mathematics and reject MP4 requests before playback. Do not read
older validation documents as results for this release.

## Changed source files

`_data/videos.yml` (one poster path), `_includes/video.html`,
`_layouts/home.html`, `_layouts/default.html`, `assets/js/carousel.js`,
`scripts/check.rb`, `scripts/test_carousel.py`, `README.md`, and
`README-CONTENT.md`.

Added source: `_includes/home-title.html`, `scripts/serve.sh`,
`scripts/test_posters.py`, and `scripts/test_template_fixtures.py`.
New documentation, test JSON and screenshots are under `docs/` and are excluded
from the public build by the unchanged `_config.yml`.

All chapter and paper Markdown, captions/numbering/ordering, MP4 URLs, existing
image/PDF/JPEG bytes, frontpage data, CSS (including font/width settings),
navigation, configuration, Gemfile/lockfile, deployment workflow and other
unlisted original files are unchanged. No original source file was removed.
macOS archive metadata and generated caches are not redistributed.

`chapter-template.md` SHA-256:

```text
580fb1877a77aef31acb8c5677059e3d894befb19db7df6d884cfb8620fc471c
```

## Reproduce locally

From the extracted folder, after installing its normal Ruby dependencies:

```bash
bundle exec jekyll build --baseurl ""
ruby scripts/check.rb --baseurl "" _site
python3 scripts/test_posters.py --site _site
python3 scripts/test_carousel.py --site _site
python3 scripts/test_template_fixtures.py
bundle exec jekyll build --baseurl "/thesis-supplement" --destination _site-subpath
ruby scripts/check.rb --baseurl "/thesis-supplement" _site-subpath
python3 scripts/test_posters.py --site _site-subpath --baseurl "/thesis-supplement"
python3 scripts/test_carousel.py --site _site-subpath --baseurl "/thesis-supplement" --widths "390,1440"
```

The README lists optional Python/Playwright/FFmpeg test dependencies. Normal
user-run tests use a real localhost browser session, without `--offline-dom`.

For a clean preview, stop the old server and run `bash scripts/serve.sh` in this
release. Check the printed `Serving source:` path. Edit `_data/frontpage.yml` and
`_data/videos.yml`, not `_site/`. Refresh the browser after switching folders.

Machine-readable results are in `validation/poster-title-*.json`. Visual evidence
is in `validation/poster-title-screenshots/`, including the visible home title,
first carousel slide, Next selecting A-564, and the corrected duck poster, at
390px and 1440px.
