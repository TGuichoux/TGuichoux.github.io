# Supplied template analysis

## Provenance and baseline

Source: the user's `academicpages.github.io-master.zip`, with ZIP comment/commit
`3d28cd27d0551b3d9dd8132f207538355fbbc7cc`. The archive was extracted separately;
the original files were not overwritten. Its README, Gemfile, configuration,
layouts, includes, Sass, JavaScript, Dockerfile, package metadata, license, and
bundled light-theme screenshot were inspected before implementation.

The README and its bundled `images/themes/homepage-light.png` establish the
selected visual reference. That image is a screenshot supplied in the archive,
**not** a baseline rendering produced during this implementation.

`bundle3.3 install --local` failed: `Could not find gem 'jekyll' in locally
installed gems`. Installing Bundler from RubyGems also failed because the host
could not be resolved. There was no reachable package registry in this
preparation environment. A working unmodified baseline was therefore **not
established**, and that acceptance item remains open.

## What the archive actually specifies

| Area | Observed in the uploaded archive |
| --- | --- |
| Theme lineage | AcademicPages, based on Minimal Mistakes; in-repository layouts rather than a theme gem |
| Jekyll version | Not pinned directly; Gemfile includes both unversioned `jekyll` and `github-pages`; no resolved version can be claimed without installation |
| Ruby | Dockerfile uses `ruby:3.2`; no universal Ruby version requirement established by the source |
| Bundler | Dockerfile installs `2.3.26`; not a statement that this is required for the adaptation |
| Extra gem pin | `connection_pool 2.5.0` |
| Gemfile plugins | feed, sitemap, redirect-from, jemoji, WEBrick and the full github-pages bundle |
| Additional configured plugins | gist and paginate |
| Collections | Teaching, publications, portfolio, talks, plus blog pages/posts |
| Layouts | Default, single, archive and specialized collection/CV layouts |
| CSS | `assets/css/main.scss` imports `_sass` theme tokens, reset/base, component files, Susy and Breakpoint vendor code |
| JavaScript | jQuery, greedy navigation, theme switching; optional Plotly dependency |
| Node tasks | Uglify builds the JS bundle; onchange watches JS sources |
| Typography | System sans-serif text, optional serif/monospace families, Academicons and Font Awesome assets |
| Responsive model | Masthead plus author sidebar, breakpoint-based layout, collapsible greedy navigation |
| Deployment assumptions | GitHub Pages-oriented source and configuration; many optional portfolio/blog features |

## Visual adaptation

Retained: white background; teal accent family; charcoal/gray system typography;
thin masthead rule; author portrait/profile at left; readable main column;
archive-style publication rows; restrained headings and captions; light-gray
footer; existing component naming where useful.

The original base accent `#2f7f93` is retained. Link text is slightly darkened
relative to the original light link color to improve readability on white.
The original column concept is implemented with native CSS Grid rather than
Susy. The masthead is in normal document flow rather than fixed, avoiding
content offsets on small screens. The sidebar is sticky on desktop and compact
above the content on tablets/phones. A simple three-link navigation replaces
greedy navigation. This keeps the selected visual character while removing the
old layout/tooling dependencies.

Removed: blog posts, comments and comment-provider code, analytics, social-share
widgets, talk maps, talk/teaching/CV collections, example publications, draft
content, RSS plugins, unused icon font files, jQuery, Plotly, JS minification,
Node package files, Sass vendor frameworks, theme-switching variants, Docker
and dev-container machinery, and original repository-maintenance workflows.

Added: chapters and papers collections, YAML media records, scientific components,
per-chapter navigation, thesis metadata, optional resource links, citation copy
support, root/subpath-aware URLs, a Pages deployment workflow, source/build
checks, and a non-specialist editing guide. Original MIT attribution is retained.
