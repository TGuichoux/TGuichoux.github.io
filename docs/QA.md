# Validation record — 30 September 2026

## Overall status

**Source prepared; Stage 1 acceptance pending a genuine Jekyll build and runtime
check.** A successful Jekyll build, original baseline run, macOS launch, live
reload, and GitHub Pages publication are not claimed.

## Environment and installation attempts

The preparation machine provided Ruby 3.3.8, Bundler 2.5.22 (invoked as
`bundle3.3`), and WEBrick 1.9.1. Jekyll was not installed. The RubyGems host could
not be reached from the execution environment.

The untouched uploaded template was unpacked separately and inspected first.
Its baseline `bundle3.3 install --local` returned:

```text
Could not find gem 'jekyll' in locally installed gems.
```

The adapted project's `bundle3.3 install --local` returned:

```text
Could not find gem 'jekyll (= 4.4.1)' in locally installed gems.
```

Consequently, no dependency graph or fabricated `Gemfile.lock` is provided.
The networked first installation must generate the lockfile; commit it after
successful verification.

## Checks actually passed

| Check | Result and scope |
| --- | --- |
| Ruby validator syntax | `ruby -c scripts/check.rb` passed |
| JavaScript syntax | `node --check` passed for `site.js` and `math.js`; Node was used only as a preparation checker, not as a project dependency |
| Source metadata | `ruby scripts/check.rb --source-only` passed: YAML syntax/duplicate keys, chapter and paper identifiers/order, video keys, referenced local assets |
| Negative source/build checks | 12 intentional faults were rejected: duplicate chapter/paper UIDs, chapter number, duplicate YAML key, malformed YAML, missing figure, missing poster, unknown video, missing link, missing fragment, duplicate DOM ID, empty link |
| Source restoration | All deliberate negative-test mutations were restored; clean source check passed again |
| Design-preview routes | Independent HTML rendering produced 12 routes, including a 404 page |
| Placeholder counts | 16 figure placements and 21 video placeholder cards; no empty-source `<video>` players |
| Internal paths | Source/build checker passed on independent HTML at both the root and `/__path-test`, including local resources and fragments |
| Responsive layout | 60 page/width combinations in Chromium: all 12 pages at 360, 390, 768, 1024, 1440 CSS pixels; no document-wide horizontal overflow |
| Basic semantics | One main landmark and one H1 per page; images supplied with alt attributes |
| Media layouts | Three/two-column grids on suitable desktop widths; one column at mobile width |
| Chapter menu | Open on desktop, collapsed on mobile, user toggle worked; available without JavaScript |
| Pagination | First/middle/last chapter previous/next targets and edge conditions checked |
| Citation | Expand/collapse and manual-selection copy fallback exercised |
| Keyboard | Skip link received keyboard focus; target main is focusable |
| Long metadata | Long paper title and 15-author list wrapped without overflow at 390px |
| JavaScript errors | No uncaught errors during the isolated layout/interaction checks |

## What the visual checks do and do not establish

The separate design preview is **not `_site` output**. It was rendered from the
project's source by a temporary preparation-only implementation of the small
Liquid subset used here, with Markdown-it rather than Kramdown. This helper is
not distributed as project code and is not a required runtime.

The available Chromium browser blocked both HTTP and file-URL navigation by
administrative policy. To inspect layout without changing that policy, the
prepared HTML was supplied directly to the browser DOM, with the project's same
CSS/JavaScript inlined and local SVGs encoded as data URLs. All route targets
were checked separately against files on disk. The browser checks therefore do
**not** prove actual HTTP/file navigation, external fetching, secure clipboard
writes, real Liquid execution, real Kramdown conversion, or Jekyll serving.

The provided screenshots are design-only layout captures. The preview ZIP has
file-relative links for opening `index.html` after extraction. Its static link
targets were checked, but file-URL opening was not executable in this restricted
browser. Its visible notice identifies it as a design preview.

MathJax CDN typesetting was not verified. The source emits mathematical examples
and loads a pinned MathJax configuration; visible raw TeX in an offline preview
is not evidence that the real typesetter ran.

## Required technical acceptance on a networked machine

From the source project, using the documented Ruby/Bundler setup:

```bash
bundle install
bundle exec ruby scripts/check.rb --source-only
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
bundle exec ruby scripts/check.rb --baseurl ""
JEKYLL_ENV=production bundle exec jekyll build --baseurl /test-repository --destination _site-path-test
bundle exec ruby scripts/check.rb --baseurl /test-repository _site-path-test
bundle exec jekyll serve --livereload
```

Open the local site, inspect equations, test navigation and responsive media in
Safari and Chromium, save a chapter edit and verify live reload. Check a real
MP4/poster/caption sample in a later media stage; placeholders cannot establish
codec or hosting compatibility. Enable Pages/Actions and inspect an actual
successful build/deploy run. The supplied workflow performs root/subpath builds
and validation before publication, but it has not been executed here.

These checks should be completed before treating Stage 1 as accepted or
populating the whole media collection.
