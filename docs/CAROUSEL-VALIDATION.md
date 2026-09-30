# Carousel v3 — validation and delivery notes

Release date: 2026-09-30. Source: `supplementary-website-carousel-fix.zip` from this
conversation. This report supersedes the older carousel validation claims in the
historical engineering documents. This is a source release, not a deployed site.

## What was established about the previous release

In a controlled Chromium render of the previous archive, the Previous/Next buttons
did work. The user's exact local button failure was therefore **not reproduced**,
and the earlier Safari explanation was not established by testing.

A separate concrete limitation was reproduced: the previous chapter-6 track had
a 1076px viewport and a 1076px scroll width because inactive slides were hidden.
It could not behave as a native swipe/trackpad carousel. The replacement has a
1076px viewport and a 10760px scroll width for its ten slides at the same desktop
size. No slide is hidden. This release also removes runtime assembly of controls,
isolates the carousel script, and versions asset URLs against stale caching.

## Changes in this release

The Jekyll include now emits complete carousel markup and fallback anchor links.
`assets/js/carousel.js` independently enhances native scroll snapping with the
shared toolbar, position counter, selector, keyboard controls, mouse dragging,
first-frame previews, video-load errors, and preservation of playback position.
The script runs at the end of the document, before waiting for any deferred
external mathematics library. A failed or pending video request never gates
carousel navigation.

Video previews use the native video element and do not read a cross-origin canvas.
The player lazily loads metadata and, where necessary, seeks within the first
frame without autoplay. Generated local JPEG posters take precedence when a
matching `_data/video_posters.yml` entry exists; manually supplied posters take
precedence over both. A static-frame extraction script is included.

## Executed checks

| Check | Result |
| --- | --- |
| Jekyll 4.4.1 rendered build at `/` | Passed; 13 HTML pages |
| Jekyll 4.4.1 rendered build at `/thesis-supplement` | Passed; 13 HTML pages |
| Source metadata, duplicate keys/IDs, local assets, internal links/fragments, base paths, protected template exclusion | Passed for both builds |
| Local HTTP resource requests | 41 at root + 41 under the repository path; all returned 200 |
| Rendered-browser checks at 375, 390, 640, 768, 1024, and 1440px | 13 pages × 6 widths = 78 cases passed |
| Every multi-video group on every tested page | All 13 groups traversed forward/backward; selector and keyboard checked |
| Additional repository-path browser cases | 13 pages × 2 widths (375 and 1024px) = 26 cases passed |
| Targeted browser behavior tests | 14 passed, detailed below |
| Dynamic first-frame visual checks | Actual decoded fixture pixels visible while paused at the first frame, at 390 and 1440px |
| Local poster generator | 6 checks passed: extraction, JPEG format/dimensions, URL deduplication, reuse, explicit failure, no broken manifest entry |
| Generated-poster include branch | 5 checks passed: matching source, base-path resolution, rendered image pixels, no pre-playback MP4 request, no missing local assets |
| CSS and JavaScript syntax | Checked; JavaScript passes `node --check` |
| Original chapter template | Byte-for-byte unchanged from the original stage-2 ZIP |

The 14 targeted browser tests cover first-frame decoding and pause/position
retention, trackpad scrolling and resize, a browser touch-swipe sequence,
no-JavaScript anchor navigation, a failed media host, unavailable `site.js`, a
MathJax request deliberately held pending, missing observer APIs, a changed hash,
an initial deep link, mouse dragging, native video keyboard handling, independent
carousel groups, and print layout. The root browser run contains 92 checks in
all (78 page/width cases + 14 targeted cases), with **0 failures**. The additional
repository-path run contains 26 cases, with **0 failures**.

Machine-readable reports are preserved in `docs/validation/`. The repeatable
browser test is `scripts/test_carousel.py`. The source/internal-link check remains
`scripts/check.rb`.

## Exact test scope and limitations

**Browser:** Chromium 144.0.7559.96 on Linux, controlled with Playwright. Mobile
viewport and touch emulation were exercised. A physical phone, macOS Safari,
WebKit, and Firefox were **not** tested.

**Rendering harness:** top-level browser URL navigation is prohibited in this
environment. The browser tests therefore used `--offline-dom`: the exact rendered
HTML was loaded with `set_content`; root-relative resource URLs were resolved
through a test origin; the actual unchanged CSS and JavaScript files were supplied
to the browser. This tests layout, media decoding, and user interaction, but is
not a live navigation session against `jekyll serve`. Actual local HTTP resource
fetches were checked separately. The included test script uses normal localhost
HTTP navigation by default on an unrestricted machine.

**Build harness:** network access to RubyGems was unavailable. The Jekyll, Liquid,
and Kramdown source libraries already included in the earlier supplied archive
were used to run the real Jekyll build engine. The unused Sass converter was not
loaded because the cached native Sass dependency targets macOS; this website
contains no Sass/SCSS files and uses ordinary CSS. A fresh Bundler installation
and a normal `bundle exec jekyll serve` session were not certified here. No cached
gems or test harness modifications to Jekyll are included in the release.

**Video fixtures:** remote media requests in browser tests were fulfilled with a
clearly synthetic four-second H.264/AAC test clip, retaining a cross-origin source
URL and deliberately omitting `Access-Control-Allow-Origin`. Decoded pixel checks
confirm a real first frame rather than a blank native player. These fixtures are
not research results, are not substituted into the delivered website, and are
not bundled in its public assets. The static-poster test used a separate test-only
copy of the site.

**Live services:** attempts to retrieve the Zenodo record and an MP4 through the
available network tools failed. Consequently, **no genuine research-video JPEG
posters could be extracted here**. The release uses dynamic first-frame previews
by default and includes `scripts/generate_posters.rb` to create the actual local
posters on a machine with access to Zenodo or to the user's local MP4 files.
The live availability, filenames, codecs, seeking, and playback of the 40 distinct
Zenodo sources remain unverified. Original URLs were not guessed or corrected.
MathJax was stubbed in controlled browser tests, so CDN availability and live
mathematics rendering are also outside this validation.

## Preserved content

All chapter Markdown, all paper Markdown, all existing data YAML (including the
43-entry video registry), all real image/PDF assets, navigation, original template,
Gemfile, lockfile, and deployment workflow are unchanged. The CSS `:root` block
is byte-for-byte unchanged, preserving every font-size category, the 1400px shell,
the 80ch prose width, spacing, palette, and sidebar settings. Captions, numbering,
source URLs, ordering, mathematics, and bibliography text were not rewritten.

`chapter-template.md` SHA-256:

```text
580fb1877a77aef31acb8c5677059e3d894befb19db7df6d884cfb8620fc471c
```

Existing source files modified: `README.md`, `README-CONTENT.md`,
`_includes/video-group.html`, `_includes/video.html`, `_layouts/default.html`,
`assets/css/main.css`, and `assets/js/site.js`. Added production code:
`assets/js/carousel.js`. Added tooling: `scripts/generate_posters.rb` and
`scripts/test_carousel.py`, plus these validation documents. No installed Ruby
gems, `_site` output, Python bytecode, test videos, or synthetic posters are shipped.

## First run after extraction

Use a new directory, not an overlay on a previously served copy. From the folder
containing `_config.yml` and `Gemfile`:

```bash
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll clean
bundle exec jekyll serve --livereload --baseurl ""
```

Open `http://127.0.0.1:4000/thesis/chapter-06/`. The first group starts at `1 / 10`;
Next selects Segment A-564 and `2 / 10`. A single-video group deliberately has no
carousel toolbar. Stop the server with Control-C before switching source folders.
The README includes the complete typography/width guide and static-poster commands.
