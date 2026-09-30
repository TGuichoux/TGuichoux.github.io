# Readability and carousel update — validation record

Date: 30 September 2026. Source: `supplementary-website-stage2.zip`.
This record describes this update. The other engineering and QA documents are
retained as historical project documentation.

## Scope and preservation

The visual palette, original content structure, navigation, research text,
figures, formulas, citations, media URLs, numbering, and ordering are retained.
Only readability, layout-width controls, grouped-video presentation, removal
of preview scaffolding, and their documentation/validation were changed.

- All nine chapter/paper Markdown bodies match the supplied archive byte for
  byte. Front matter other than unused scaffold video lists also matches.
- All **43** video records retain their original source URLs, numbers, titles,
  captions, download/archive links, and subtitle/transcript fields. Only dummy
  poster references were cleared. Blank optional content was not invented.
- Real image/PDF assets, author data, math configuration, media utility scripts,
  Gemfile, Gemfile.lock, existing workflow, license, and notices are preserved.
- The existing `vendor/` dependency files are preserved. No new front-end or
  Ruby dependency is required for the carousel.
- `chapter-template.md` matches the original bytes, including its instructional
  placeholders. It is now excluded from publication. Its SHA-256 is:

```text
580fb1877a77aef31acb8c5677059e3d894befb19db7df6d884cfb8620fc471c
```

## Completed checks

| Check | Result |
| --- | --- |
| Source metadata, YAML, local asset validation | Passed with `ruby scripts/check.rb --source-only`. |
| Jekyll production render at the root | Passed using the supplied Jekyll 4.4.1 / Liquid / Kramdown source. |
| Root output: IDs, local links, fragments, media and page references | Passed with `ruby scripts/check.rb _site`. |
| Production render under `/__path-test` | Passed; generated separately outside the source folder. |
| Subdirectory output/link validation | Passed with `ruby scripts/check.rb --baseurl /__path-test /mnt/data/site-path-test`. The absolute path was test-environment-only. |
| JavaScript syntax | Passed with `node --check assets/js/site.js`. |
| Responsive rendering | All 13 generated pages checked at 320, 375, 640, 960, 1440, and 1920 CSS-pixel widths: **78 page/viewport combinations**, without document-level horizontal overflow. |
| Actual grouped videos | 19 rendered groups: 13 multi-video carousels and 6 single-video groups. All show one active slide; only multi-video groups receive controls. |
| Carousel controls | Previous/Next, direct selection, arrow keys, Home/End, and first/last boundaries passed for every multi-video group. |
| Existing video fragment links | Initial non-first-slide links, hash changes, and re-clicking the current fragment after changing slides passed. |
| Media state | A synthetic local MP4 played in the actual HTML video component. Navigating away paused it; returning preserved position and did not autoplay. This was not a test of the remote research videos. |
| No-JavaScript fallback | All 13 Chapter 6 videos remain visible and reachable; no nonfunctional carousel controls are shown. |
| Print fallback | All slides in the 10-video group become visible; carousel controls are hidden. |
| Component input cases | YAML arrays, a single key, empty groups, blank/unknown sources, optional poster markup, and empty figures rendered as intended. Fixtures were created outside the delivered source. |
| Placeholder cleanup | No published dummy media, missing-resource badges, preview notice, dummy notes file, or published chapter template. |
| Runtime JavaScript exceptions | None in the offline browser checks. |

The rendered output contains 55 video elements because some of the same 43
registered videos are presented both in a chapter and in a paper. These uses
were retained, not deduplicated or renumbered.

## How the checks were performed, and limits

The production pages were rendered by the supplied Jekyll engine. Network
installation was unavailable in the test container, so cached dependency source
was loaded directly; the required native protobuf extension was compiled in a
separate test-runtime folder. Website dependencies and their versions were not
modified. A fresh macOS `bundle install` was not performed here.

The managed browser blocks navigation to local HTTP/file pages. Browser checks
therefore loaded the **actual generated HTML in memory**, embedded its exact
local CSS/JavaScript and local image bytes, and disabled external network
requests. No browser security policy was changed. The remote MathJax loader was
omitted only in this test harness; the delivered MathJax setup is unchanged.
Screenshots were also inspected for the home page, a figure page, and desktop
and mobile carousels.

These checks **do not verify remote Zenodo playback, network seeking, external
links/downloads, remote subtitle loading, CDN mathematics rendering, or a live
GitHub Pages deployment**. The synthetic video check verifies the pause/position
logic, not the remote research media. Safari/Firefox, a formal screen-reader
audit, and hosted end-to-end navigation were not tested. No source was pushed,
no external account was changed, and nothing was deployed.

For normal local validation, use the build/serve/check commands in `README.md`.
Try real video playback and math rendering in the intended browser before
publishing. Search indexing remains blocked by `noindex: true`, preserving the
previous setting independently of the removed preview banner.

## Files deliberately removed

```text
assets/placeholders/avatar.svg
assets/placeholders/figure-placeholder.svg
assets/placeholders/video-placeholder.svg
downloads/placeholder-notes.txt
```

The rebuilt `_site/` also no longer contains their generated copies, the old
published chapter-template page, or rendered authoring documentation. Build
caches and operating-system metadata (`.DS_Store`, `__MACOSX`, AppleDouble files)
are omitted from the delivery archive. They are not website content.

Extract this archive into a new folder, rather than merging it over an old
copy; a merge does not delete old dummy files. The meaningful source files and
supplied dependencies not listed as changed/removed below are unchanged.

## Modified source files

```text
README-CONTENT.md
README.md
_chapters/chapter-04.md
_chapters/chapter-05.md
_chapters/chapter-06.md
_config.yml
_data/author.yml
_data/videos.yml
_includes/author-profile.html
_includes/citation.html
_includes/figure.html
_includes/paper-list.html
_includes/paper_metadata.html
_includes/resource-links.html
_includes/video-group.html
_includes/video.html
_layouts/chapter.html
_layouts/default.html
_layouts/paper.html
_layouts/thesis.html
_papers/paper-01.md
assets/css/main.css
assets/js/site.js
examples/chapter.md
examples/paper.md
robots.txt
scripts/check.rb
```

This validation record is the only newly added source document. `_site/` is
regenerated output, not the editing source. Test harnesses, synthetic media,
compiled test dependencies, and alternate-basepath builds are not shipped.
