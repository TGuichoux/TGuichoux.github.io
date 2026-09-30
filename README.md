# Academic supplementary-material website

A Jekyll website for the thesis and research papers, retaining the existing
AcademicPages / Minimal Mistakes-inspired design, navigation, content, figures,
mathematics, citations, and media URLs. There is no Node build, database, CMS,
or Python launcher requirement.

## Stage 3: permanent links to individual videos

Every rendered video has a permanent fragment anchor derived from its existing
`_data/videos.yml` key. The URL opens the **website page**, selects the correct
carousel slide when necessary, and scrolls to the video. Playback stays paused;
a local static poster is shown without fetching the MP4 until Play is pressed.
No generated LaTeX file, redirect page, or new runtime dependency is needed.

### Construct a link manually

Use the **published page URL plus the actual HTML ID**, not the MP4 filename,
caption, displayed number, or carousel position. For this site's existing keys,
Jekyll's current `slugify` convention replaces the underscore with a hyphen:

```text
YAML key:        ch06-6_10
HTML ID:        ch06-6-10
Local URL:      http://127.0.0.1:4000/thesis/chapter-06/#ch06-6-10
Published URL:  https://USERNAME.github.io/REPOSITORY/thesis/chapter-06/#ch06-6-10
```

Replace the example hostname/repository with your actual public address. Do not
put a localhost address into the final manuscript. For a root-domain site, omit
`/REPOSITORY`. The site does not need to know the deployment hostname to resolve
a fragment. Existing `_config.yml` `url` and `baseurl` settings still apply.

These are real destinations present in this source, relative to the site root:

| Destination | Page and anchor |
| --- | --- |
| Chapter 2, standalone Video 2.1 | `/thesis/chapter-02/#ch02-2-1` |
| Chapter 4, Video 4.1 in its carousel | `/thesis/chapter-04/#ch04-4-1` |
| Chapter 6, A-421 (first slide) | `/thesis/chapter-06/#ch06-6-1` |
| Chapter 6, C-93 (middle slide) | `/thesis/chapter-06/#ch06-6-5` |
| Chapter 6, G-93 (last slide) | `/thesis/chapter-06/#ch06-6-10` |
| Chapter 6, the standalone G-93 example | `/thesis/chapter-06/#ch06-6-13` |
| Paper 1, the reused Video 4.1 example | `/papers/paper-01/#ch04-4-1` |

Previous/Next and the dropdown browse slides without rewriting the address
bar. To link a different video, use that video's own key/anchor; do not simply
copy a URL left over from a previously linked slide.

A chapter and a paper can reuse the same key: these are different **page URLs**.
HTML IDs must be unique within each individual page. Do not insert the same key
twice on the same page. If the same MP4 needs two occurrences on one page, retain
separate existing keys, as with `ch06-6_10` and `ch06-6_13`; these address different
places even though both show G-93.

### Put a clickable icon in the LaTeX manuscript

Load these packages in your document preamble (do not load a package twice if
your thesis template already includes it):

```latex
\usepackage{fontawesome5}
\usepackage{hyperref}
```

Then write the link manually in the text. Replace the example hostname and
repository before compiling the published PDF:

```latex
This example is about G-93 (Video 6.10)~
\href{https://USERNAME.github.io/REPOSITORY/thesis/chapter-06/#ch06-6-10}{\faPlayCircle}.
```

The existing manuscript's link style/color applies. This release does **not**
create or require `video-links.tex`, or any other LaTeX mapping file. Click a
compiled PDF link once after deployment to confirm the public hostname and
repository path; those values are not configured in the uploaded source.

### Keep published links permanent

Once a URL is cited in the thesis PDF, keep both its **page permalink** and its
**video key/HTML ID** stable. Do not rename the key when renumbering a video or
reordering carousel slides. Editing its title, caption, number, poster, or MP4
source does not change the anchor. Do not change the template's `slugify`
convention for existing keys. Changing/removing the key or page path breaks
published links unless you retain a compatible destination.

### Navigation behavior

Direct links work for standalone videos and every carousel position. They also
work after changing the fragment on an already-open page, with Back/Forward, and
when clicking the same link again after manually choosing another slide. A
repeated same-fragment click does not add a duplicate history entry. Other-page
links, new tabs, modifier-clicks, download links, ordinary section anchors, and
unknown/malformed fragments retain normal browser behavior.

Opening a video link pauses any currently playing site video without resetting
its playback position. Carousel selection reuses the existing navigation code;
Previous/Next, the selector, counter, keyboard, touch, static posters and Retry
are retained. Navigation initializes from the script at the end of the body,
without waiting for remote MathJax or a video host. Returning from the browser's
back/forward cache reapplies the link; a normal late page-load event does not
undo a manual slide change.

With JavaScript disabled, the native horizontal track and anchor links remain
available; enhanced counters/selectors are not enabled. With JavaScript, deep
links center the video when it fits, or align the player near the top of a short
viewport. Long captions do not push the player out of view. For the first three seconds
after following a link, the page also corrects displacement from lazy-loading
figures. That correction stops immediately on user input, so it cannot fight
manual scrolling, playback, or carousel navigation. It does not wait for images
or external services to finish loading.

### Validate deep links after editing the site

Build and validate both deployment modes from the site folder:

```bash
bundle exec jekyll build --baseurl "" --destination _site
ruby scripts/check.rb --baseurl "" _site
bundle exec jekyll build --baseurl "/repository-test" --destination _site-repository
ruby scripts/check.rb --baseurl "/repository-test" _site-repository
```

Optional development-only browser tests (Python and Node are **not** needed by
Jekyll, the published site, or readers):

```bash
python3 -m pip install playwright beautifulsoup4 pillow
python3 -m playwright install chromium
python3 scripts/test_video_links.py --site _site --report docs/validation/local-video-links.json
python3 scripts/test_video_links.py --site _site-repository --baseurl /repository-test --report docs/validation/repository-video-links.json
node scripts/test_video_link_urls.cjs
python3 scripts/test_carousel.py --site _site --report docs/validation/local-carousel.json
```

The link tests discover all rendered video anchors; they check initial links,
hash changes, geometry, static-image decoding, paused playback, repeated links,
Back/Forward, malformed fragments and no-JavaScript fallback. The URL-routing
unit tests additionally cover absolute/relative URLs, query strings, repository
paths, modifier-clicks and new tabs. `docs/STAGE3-VALIDATION.md` records the actual
release checks and their environment limitations. Earlier validation reports
are historical and do not certify this new source.

## Static posters and homepage title — retained behavior

The JPEGs you supplied are included in **`assets/posters/`**. All **43 video
entries** have an explicit local `poster:` value; repeated videos share the same
JPEG, for **40 distinct referenced images**. They are displayed through the native
HTML `poster` attribute with `preload="none"`. Viewing a poster does not need an
MP4 download, JavaScript, a Zenodo connection, or a cross-origin canvas.

The supplied duck image is named **`gelina-duck_female.jpg`** (underscore).
Its entry now points to that exact filename. Its MP4 URL has NOT been renamed.
Local poster URLs honor Jekyll's `baseurl` and have a build-time cache version,
so replacing a JPEG at the same path becomes visible after a rebuild.

Edit **`_data/frontpage.yml`** to change both the visible home H1 and the home
browser-tab title:

```yaml
title: "Téo Guichoux's personal space"
```

The shared `_includes/home-title.html` handles both locations, with
`_config.yml`'s `title` as a fallback when the data title is absent or blank.
The masthead and sidebar name still come from **`_data/author.yml`**; chapter and
paper browser-tab titles still use their own front matter plus `_config.yml`.
The home H1 uses the existing `--font-size-home-h1` CSS variable.

In the uploaded source the home heading already rendered this YAML text on a
fresh build; the browser-tab title did not. A missing heading across an old
preview was not reproduced, so it is not attributed to a YAML or Liquid defect.
Always stop the older server and start this source tree before checking edits.

The latest executed checks and their limits are in
**`docs/POSTER-TITLE-VALIDATION.md`**. Reports with older names describe older
releases and are retained for history, not as evidence for this release.

## Earlier layout and carousel changes

| Requested change | Result |
| --- | --- |
| Slightly larger text | The default base size is **17px** instead of 16px; heading and interface sizes are centralized and adjustable. |
| More readable captions | Caption text is approximately **16px** instead of 12.3px; bold caption labels are approximately **16.3px**. |
| Wider site | The overall maximum width is **1400px** instead of 1180px. Ordinary prose is capped at **80ch** instead of 70ch. |
| Carousels for grouped videos | Native horizontal scroll-snap, swipe/trackpad support, independent Previous/Next controls, counter, selector, keyboard navigation, and a no-JavaScript link fallback. |
| First-frame previews | Videos without a custom/static poster lazily display their first frame in the native player. A supplied FFmpeg script can generate persistent local JPEG posters for all entries. |
| Remove placeholders | Preview banners, dummy media/posters/downloads, missing-resource badges, placeholder citation notes, and unused scaffold video IDs are removed. |
| Keep the chapter template | **`chapter-template.md` is byte-for-byte unchanged.** It is excluded from the published site. |

The chapter and paper body text, real figures, video numbering, captions, video
URLs, bibliography entries, and their order have not been rewritten. Empty
optional titles and captions stay empty; no scientific content has been invented.
Existing search-indexing restrictions are also preserved, separately from the
removed preview interface; see [Search indexing](#search-indexing).

## Quick start

Extract this release into a **new folder**, rather than merging it with an older
copy. Open Terminal in the extracted folder containing `_config.yml` and `Gemfile`:

```bash
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll clean
bundle exec jekyll serve --livereload --baseurl ""
```

Open **http://127.0.0.1:4000**. Leave Terminal running while editing; stop it with
**Control-C**. Do not double-click an HTML file or open a `file://` URL. The site
needs to be served so its asset paths resolve correctly.

No `_site/`, `vendor/bundle`, `.bundle`, or machine-specific installed gems are
shipped in this ZIP. `bundle install` creates the appropriate dependencies on
**your** Mac. Source changes are made outside `_site/`, which Jekyll regenerates.

For an existing running server, stop it first, then run the clean/serve commands
above in the **new** folder. Refresh the browser after restarting. CSS and local
JavaScript URLs include a build version to avoid reusing an older carousel script.
Changing `_config.yml` always requires a restart.

A safer launcher pins the source directory to this release, checks the local
assets, cleans stale output, and then starts Jekyll:

```bash
bash scripts/serve.sh
```

It prints `Serving source: ...`. Verify that path is the folder you are editing.
It must be run after stopping the previous server; it does not kill other
processes or silently switch ports. From another directory, invoke the script
by its full path in quotes. Reload the page with **Command-Shift-R** after switching
releases. Do not edit `_site/` or keep a second old preview server on port 4000.

### Diagnose a missing poster or title

Run `ruby scripts/check.rb --source-only` to check the **source** assets. For a
local root-path build, run:

```bash
bundle exec jekyll build --baseurl ""
ruby scripts/check.rb --baseurl "" _site
```

After the server starts, open `/assets/posters/A-421.jpg` on the same local origin.
If it returns 404, inspect the `Serving source:` path and the case/spelling of the
filename. The release's source checker rejects missing referenced assets rather
than silently hiding them. The chapter-4 duck preview intentionally maps the
hyphenated MP4 name to the supplied underscore-named JPEG.

For a repository deployment, put the repository prefix in `_config.yml`'s
`baseurl`, **not** in the `poster:` values. For example, a poster stored as
`/assets/posters/A-421.jpg` becomes `/REPOSITORY/assets/posters/A-421.jpg` in the
rendered page. Commit the JPEGs as well as `_data/videos.yml`.

### What to check immediately

Open **http://127.0.0.1:4000/thesis/chapter-06/**. Its first video group has
**10 slides**, with Previous/Next, a `1 / 10` counter, and **Go to video**. Next
shows Segment A-564 and `2 / 10`. Swipe on a caption or scroll horizontally with
a trackpad to browse. Groups containing only one video intentionally have no
carousel controls.

For this release's actual test results and limitations, read
**`docs/POSTER-TITLE-VALIDATION.md`**. Older reports describe older releases.

## Test the poster and title fixes locally

The site itself still needs only Ruby/Jekyll. The optional browser regression
tools use Python and Playwright; the carousel playback tests also need FFmpeg.

```bash
python3 -m pip install playwright PyYAML Pillow beautifulsoup4
python3 -m playwright install chromium
bundle exec jekyll build --baseurl ""
ruby scripts/check.rb --baseurl "" _site
python3 scripts/test_posters.py --site _site
python3 scripts/test_carousel.py --site _site
python3 scripts/test_template_fixtures.py
```

`test_posters.py` requests every referenced local resource over HTTP, checks
source JPEGs and the rendered `poster` paths, compares actual player screenshots
with their JPEGs, checks the home heading and tab, and repeats with JavaScript
disabled. It rejects any MP4 request before playback. It does not substitute
synthetic posters for your images.

`test_carousel.py` tests all pages and each carousel, keyboard/touch/mouse
navigation, playback pause/position, load failure/retry, unrelated script failure,
print, and a 21-second idle-poster check. Only playback uses a synthetic test
MP4; the site's real media URLs and JPEGs are never changed.

`test_template_fixtures.py` makes temporary source copies to test editing or
removing the frontpage title, title escaping, poster precedence and generated
fallbacks, missing-asset detection, and launcher path handling.

To check a repository-style deployment separately:

```bash
bundle exec jekyll build --baseurl "/thesis-supplement" --destination _site-subpath
ruby scripts/check.rb --baseurl "/thesis-supplement" _site-subpath
python3 scripts/test_posters.py --site _site-subpath --baseurl "/thesis-supplement"
python3 scripts/test_carousel.py --site _site-subpath --baseurl "/thesis-supplement" --widths "390,1440"
```

The Python scripts normally navigate a real local HTTP server. The optional
`--offline-dom` mode is only for restricted test environments and explicitly
reports that it does not test top-level HTTP browser navigation. See the current
validation report for the exact mode actually executed during preparation.

## Change font sizes

### The one file to edit

Open **`assets/css/main.css`**. At the top, find the `:root { ... }` block.
Every font-size category has a named `--font-size-...` variable, with an inline
comment explaining what it affects. **Edit the existing values there.** There
is no need to edit every heading selector or to change layout templates.

### Change the global scale

```css
--font-size-root: 106.25%;
```

With a browser default of 16px, `100%` is 16px, `106.25%` is 17px (the supplied
setting), `112.5%` is 18px, and `125%` is 20px. The percentage respects a reader's
own browser base-font preference. Most sizes below use `rem`, so they scale with
this root setting. Fixed pixel-based layout widths do not change with it.

`--font-size-body` changes ordinary text independently. It does **not** change
headings whose sizes use `rem`. For example, at the current root, `1.05rem` is
approximately 17.85px for paragraphs while the H2 size remains separately set.

### Headings, body, and captions

| Category | CSS variable | Current value |
| --- | --- | --- |
| Global scale: 17px with the usual 16px browser default | `--font-size-root` | `106.25%` |
| Paragraphs, lists, blockquotes, and inherited body text | `--font-size-body` | `1rem` |
| Page and article H1 headings | `--font-size-h1` | `clamp(1.9rem, 3vw, 2.65rem)` |
| Home-page H1, when used | `--font-size-home-h1` | `clamp(2rem, 3.8vw, 2.9rem)` |
| H2 section headings | `--font-size-h2` | `1.45rem` |
| H3 subsection headings | `--font-size-h3` | `1.15rem` |
| H4 headings, including experiment/model labels | `--font-size-h4` | `1.05rem` |
| H5 headings | `--font-size-h5` | `1rem` |
| H6 headings | `--font-size-h6` | `.95rem` |
| Home and index section headings | `--font-size-section-heading` | `1.35rem` |
| Introductory text below a page title | `--font-size-deck` | `1.1rem` |
| Figure and video caption text | `--font-size-caption` | `.94rem` |
| Bold figure/video number and title | `--font-size-caption-title` | `.96rem` |
| Links below figures and videos | `--font-size-media-link` | `.86rem` |

For example, edit these lines within the existing `:root` block:

```css
--font-size-body: 1rem;        /* 17px at the supplied root size */
--font-size-h1: clamp(2rem, 3vw, 2.8rem);
--font-size-h2: 1.5rem;
--font-size-h3: 1.2rem;
--font-size-h4: 1.1rem;
--font-size-caption: 1rem;     /* Make caption paragraphs 17px */
--font-size-caption-title: 1rem;
```

These are example edits, not the shipped defaults. At the supplied root, the
shipped H2/H3/H4 sizes are approximately 24.65/19.55/17.85px. In Markdown, `#`,
`##`, `###`, and `####` correspond to H1, H2, H3, and H4. The page layout already
supplies the page H1; use H2 and lower in normal chapter/paper content.

`clamp(minimum, preferred, maximum)` lets H1 headings adapt to screen width;
`3vw` is the fluid term. For a fixed H1 size, replace the entire value with,
for example, `2.6rem`. Normal body/caption values are not responsive clamps.

Some contexts deliberately have their own heading tokens. The home-page and
index section titles use `--font-size-section-heading`; paper titles in lists
use `--font-size-publication-title`; chapter-list titles use
`--font-size-chapter-list-title`. These take precedence over generic H2/H3
sizes in those contexts. The home heading uses `.home-header h1` and
`--font-size-home-h1`; the Papers and Thesis section headings remain H2s.

### All remaining text categories

These settings are also in the same `:root` block. Mobile rules reuse the same
category tokens instead of silently overriding them with unrelated sizes.

| Category | CSS variable | Current value |
| --- | --- | --- |
| Top-left site/author title | `--font-size-site-title` | `1rem` |
| Main navigation links | `--font-size-nav` | `.95rem` |
| Sidebar biography and profile links | `--font-size-sidebar` | `.9rem` |
| Author name in the sidebar | `--font-size-author-name` | `1rem` |
| Author role | `--font-size-author-role` | `.87rem` |
| Author affiliation | `--font-size-author-affiliation` | `.85rem` |
| Optional sidebar note | `--font-size-sidebar-note` | `.85rem` |
| Small auxiliary labels and status messages | `--font-size-small` | `.82rem` |
| Breadcrumb navigation | `--font-size-breadcrumb` | `.82rem` |
| Uppercase page and paper labels | `--font-size-eyebrow` | `.73rem` |
| Main call-to-action buttons | `--font-size-button` | `.9rem` |
| Supplementary-material and secondary action links | `--font-size-text-link` | `.9rem` |
| Section counts and small links | `--font-size-section-meta` | `.82rem` |
| Section introductory metadata | `--font-size-section-intro` | `.87rem` |
| Chapter numbers in the chapter list | `--font-size-chapter-number` | `.88rem` |
| Chapter titles on the thesis overview | `--font-size-chapter-list-title` | `1.02rem` |
| Chapter descriptions on the thesis overview | `--font-size-chapter-list-description` | `.89rem` |
| Paper titles on the home page and papers index | `--font-size-publication-title` | `1.12rem` |
| Paper author lists | `--font-size-paper-authors` | `.94rem` |
| Publication venue and year | `--font-size-paper-venue` | `.86rem` |
| Paper descriptions on index pages | `--font-size-publication-description` | `.92rem` |
| PDF, DOI, Code, and download buttons | `--font-size-resource-link` | `.82rem` |
| Author on the thesis overview | `--font-size-thesis-author` | `1rem` |
| Institution, degree, supervisors, year, and defense date | `--font-size-thesis-metadata` | `.92rem` |
| Chapter links in the sidebar | `--font-size-chapter-nav` | `.8rem` |
| Chapter-menu heading and overview link | `--font-size-chapter-nav-heading` | `.83rem` |
| Previous and next chapter titles | `--font-size-pagination` | `.91rem` |
| Previous/next labels and overview return link | `--font-size-pagination-label` | `.82rem` |
| Return-to-papers link | `--font-size-return-link` | `.91rem` |
| On-this-page table of contents | `--font-size-toc` | `.88rem` |
| Inline code, relative to its surrounding text | `--font-size-code` | `.9em` |
| Citation / BibTeX disclosure label | `--font-size-citation-summary` | `.9rem` |
| BibTeX code block | `--font-size-citation-code` | `.87rem` |
| Copy BibTeX button | `--font-size-copy-button` | `.84rem` |
| Validation or content-warning text | `--font-size-warning` | `.9rem` |
| Carousel buttons, counter, and video selector | `--font-size-carousel-control` | `.86rem` |
| Footer text | `--font-size-footer` | `.81rem` |
| Theme attribution in the footer | `--font-size-footer-credit` | `.76rem` |
| Body text when printing; the previous default is retained | `--font-size-print` | `11pt` |

Inline code uses `em`, so it scales with its surrounding text. The BibTeX block
has its own `--font-size-citation-code`; its nested code element inherits that
size. Mathematical notation follows its surrounding text through the existing
MathJax integration. Native browser video controls, browser menus, and fullscreen
player UI are controlled by the browser rather than this stylesheet.

Font families remain unchanged: `--sans-serif` controls ordinary text and
`--monospace` controls code and chapter-number labels. No font files or external
font-loading dependency have been added.

## Change the width and line spacing

Open the same **`assets/css/main.css` → `:root`** block.

| What it controls | CSS variable | Current value |
| --- | --- | --- |
| Maximum width of the whole site, including header, sidebar, main column, and footer | `--shell-width` | `1400px` |
| Maximum width of ordinary academic text | `--prose-width` | `80ch` |
| Desktop author/sidebar column | `--sidebar-width` | `204px` |
| Desktop gap between sidebar and main content | `--sidebar-gap` | `64px` |
| Left and right padding on desktop/tablet | `--page-gutter` | `28px` |
| Left and right padding at 640px and below | `--page-gutter-mobile` | `20px` |
| Maximum line length of long page titles | `--page-title-width` | `30ch` |
| Maximum line length of paper titles on index pages | `--publication-title-width` | `65ch` |
| Paragraph and list line spacing | `--line-height-body` | `1.7` |
| Heading line spacing | `--line-height-heading` | `1.25` |
| Figure and video caption line spacing | `--line-height-caption` | `1.65` |
| Compact sidebar, introductory text, and metadata line spacing | `--line-height-ui` | `1.55` |
| Code-block line spacing | `--line-height-code` | `1.6` |

### Make the entire site wider or narrower

Edit:

```css
--shell-width: 1400px;
```

For example, `1280px` is narrower; `1500px` or `1600px` is wider. This is a
**maximum**, not a forced viewport width: the site still fits smaller screens.
The masthead, two-column desktop layout, and footer use the same value and
remain aligned.

To remove the desktop cap entirely, use `--shell-width: 100%;`. The page gutters
still provide space at the edges. Very wide content may be harder to read, so
normal prose has a separate cap.

### Make only the text column wider

```css
--prose-width: 80ch;
```

`ch` is approximately the width of the font's zero character; it is not a pixel
measurement. For shorter lines, try `72ch`; for longer lines, try `88ch`. Use
`100%` to let ordinary prose occupy the whole available main column. Increasing
`--shell-width` alone does not remove the prose limit.

Figures with `layout="wide"` and the video carousels use the available main
column, not the prose cap. A figure's explicit `width=...` parameter remains an
additional maximum and can still make that figure narrower. Long page titles
also have their own `--page-title-width` cap.

### Sidebar, margins, and line spacing

On a wide desktop, the main column is approximately:

```text
shell width − (2 × page gutter) − sidebar width − sidebar gap
1400       − (2 × 28)         − 204           − 64 = 1076px
```

At 1050px and below, the sidebar width/gap are capped at 185px/38px. Below
960px, the sidebar stacks above the page. At 640px and below, the horizontal
padding uses `--page-gutter-mobile`. These existing layout breakpoints are
retained in the responsive section of the stylesheet.

To loosen caption spacing without increasing letters, change
`--line-height-caption`, for example from `1.65` to `1.75`. Change
`--line-height-body` for paragraph/list spacing and `--line-height-heading`
for heading spacing. These values are unitless multipliers of the font size.

### Preview an appearance change

Save the CSS while `bundle exec jekyll serve --livereload` is running, then
inspect a chapter on desktop and on a narrow window. If a cached stylesheet
persists, use **Command-Shift-R**. Check a long title, a figure caption, and a
carousel before publishing.

## Video carousels

### Existing groups do not need to be rewritten

The existing include name and key order are retained:

```liquid
{% include video-group.html
   keys="ch04-4_1,ch04-4_2,ch04-4_3"
   columns=3
   label="Speech-gesture generation capabilities"
%}
```

This now displays a **one-video-at-a-time carousel**, not a three-column grid.
The old `columns` argument is accepted for compatibility but **has no effect**.
There is no reason to remove it from existing chapter or paper text.

New includes can omit it:

```liquid
{% include video-group.html
   keys="ch04-4_1,ch04-4_2,ch04-4_3"
   label="Speech-gesture generation capabilities"
%}
```

A YAML list works too:

```yaml
comparison_videos:
  - ch04-4_1
  - ch04-4_2
  - ch04-4_3
```

```liquid
{% include video-group.html keys=page.comparison_videos label="Method comparison" %}
```

The order of keys determines the slide order. Each group is independent. The
same video may be reused on different pages; do not include the same key twice
on one page because its figure ID must remain unique.

### Viewer controls and behavior

The carousel is a **native horizontal scrollport** with CSS scroll snapping. One
full-width slide occupies the viewport. Other slides are not hidden or removed.
Previous/Next and **Go to video** move to a slide; the counter follows the actual
scroll position. It stops at the first/last slide instead of looping.

Use a horizontal trackpad gesture, a touch swipe, or the horizontal scrollbar.
A caption can also be dragged with a mouse. Use the caption area for gestures
when a phone's native video controls intercept touches over the player itself.
Normal vertical scrolling is preserved.

Tab reaches the controls and scrollport. Enter/Space activate buttons. With a
button or the scrollport focused, Left/Right move one slide and Home/End jump to
the boundaries. Native video and select controls keep their own keyboard keys.

There is **no autoplay or automatic rotation**. Moving away pauses the previous
video without resetting its position. Captions and resource links travel with
the corresponding video. Existing figure IDs and direct video links are kept.
Changing the window size keeps the selected slide aligned.

With JavaScript disabled or unavailable, native horizontal scrolling still works
and each slide has real Previous/Next anchor links. Only the enhanced shared
buttons and selector are absent. Printing shows every slide vertically.
One-video groups remain ordinary videos; empty groups are omitted.

The carousel script is **`assets/js/carousel.js`**, loaded independently at the
end of the document. It does not wait for `site.js`, MathJax, a video download,
`canplay`, or a remote library. The controls are created by Jekyll, not assembled
at runtime. If enhancement fails, the native track and fallback links remain.

### Video metadata and real posters

Edit `_data/videos.yml`, not the generated HTML. For example, this is an
existing video from the supplied registry:

```yaml
ch06-6_1:
  number: Video 6.1
  title: 'Segment A-421'
  caption: ''
  src: 'https://zenodo.org/records/23059630/files/A-421.mp4'
  poster: '/assets/posters/A-421.jpg'
  download: ''
  archive: ''
  track: ''
  transcript: ''
```

`number` is the visible identifier. `title` and `caption` are optional. Caption
text supports Markdown. `src` must be a direct playable MP4 URL or a local path.
An empty `src` omits the video entirely; no dummy player, placeholder card, or
caption-only slide appears. Unknown keys are reported by `scripts/check.rb`.

A non-empty `poster` remains a manually specified image. Otherwise the include
looks for a matching generated poster in `_data/video_posters.yml`. If neither
exists, the native video element lazily loads metadata and seeks to the first
frame when it approaches the viewport. **No canvas extraction or cross-origin
pixel access is used.** No autoplay is needed, and the original MP4 URL is kept.

The player initially has `preload="none"`; the preview script requests metadata
for nearby/selected videos rather than eagerly loading every clip. Static posters
avoid that pre-playback video request altogether. A slow host can delay a dynamic
preview. If a video fails to load, an inline error, original-file link, and Retry
button appear; carousel navigation remains usable.

**This release includes your actual supplied JPEGs**, not synthetic
replacements. You do not need to regenerate them. Their bytes and filenames are
preserved; only the duck entry's path was corrected. Live Zenodo playback is not
certified by the local-poster tests. The following generator remains available
for future videos; an explicit `poster:` value takes precedence over its output.

#### Generate static posters for every video

FFmpeg is needed only for this optional one-time generation, not for viewing or
building the website. On macOS with Homebrew:

```bash
brew install ffmpeg
ruby scripts/generate_posters.rb
bundle exec jekyll build
```

The script reads `_data/videos.yml`, processes **40 distinct sources for the
43 current entries**, extracts the actual first decoded frame, and writes:

- JPEG files in `assets/posters/` (duplicate source URLs share one JPEG).
- `_data/video_posters.yml`, mapping each entry to its source and local poster.
- `docs/poster-generation.json`, with success/failure details for each source.

It does not rewrite your video registry, numbering, titles, captions, or URLs.
Only successful extractions are added to the manifest; a failure never produces
a fake or broken poster. Re-running reuses existing frames. `--force` regenerates
them when a video has changed at the same URL. An originally black first frame
is preserved as black rather than replaced by an invented representative frame.

Use your already-downloaded MP4s to avoid network access. Their basenames must
match the source URL filenames:

```bash
ruby scripts/generate_posters.rb --local-dir "/absolute/path/to/your/mp4-files"
bundle exec jekyll build
```

To inspect the source list without downloading, or process only one entry:

```bash
ruby scripts/generate_posters.rb --dry-run
ruby scripts/generate_posters.rb --only ch06-6_1
```

Commit `assets/posters/` **and** `_data/video_posters.yml` with the website. Do not
commit full MP4s unless that is a deliberate hosting decision. Local poster URLs
use the same base-path helper as the other assets and work on project Pages sites.
A manually specified `poster` in `_data/videos.yml` takes precedence over the
generated manifest.

Optional `download`, `archive`, and `transcript` values become links. `track`
points to a WebVTT file, with optional `track_language` and `track_label`. Leave
unused values empty. Native players retain `controls` and `playsinline`.

The templates can also render a single standalone video:

```liquid
{% include video.html key="ch06-6_1" %}
```

Use direct MP4 files rather than HTML record/preview pages for `src`. Optional
archive links can still point to the record page. External playback, seeking,
subtitle cross-origin behavior, and downloads depend on the media host and
browser; the local checks do not certify them.

## Placeholder removal and the protected template

The published pages no longer contain the former content-preview notice,
placeholder citation warning, missing-resource badges, dummy figure/video
images, or dummy notes download. Optional empty fields remain empty; no
replacement biography, caption, citation, or research text has been generated.

`assets/placeholders/` and `downloads/placeholder-notes.txt` were removed.
Obsolete `ch04-s...` / `p01-s...` lists in unused front matter were removed;
the real inline video groups and all real media entries are preserved.

**`chapter-template.md` is the explicit exception.** Its original bytes,
including its instructional examples and placeholder references, are preserved.
It is listed in `_config.yml` under `exclude`, so Jekyll does not publish a
`chapter-template.html` page. Keep it as an authoring reference; a copied
chapter must receive valid titles, content, figure paths, and registered video
keys before publication. The removed dummy files are not reintroduced by the
template. The separately provided `examples/` starters contain empty fields
instead of fabricated content and are also excluded from publication.

`README.md`, `README-CONTENT.md`, examples, and engineering notes are local
project documentation, not public website pages.

## The files you will normally edit

| What to change | File or folder |
| --- | --- |
| All font sizes, appearance, widths, and line spacing | `assets/css/main.css`, especially `:root` |
| Author name, biography, portrait, affiliation, profile links | `_data/author.yml` |
| Home heading, where used | `_data/frontpage.yml` |
| Home introductory text | `index.md` |
| Thesis title, abstract, institution, supervisors, resources, citation | `_data/thesis.yml` |
| Thesis-overview page source | `thesis/index.md` and `_layouts/thesis.html` |
| Chapter body, captions, and video-group placement | `_chapters/*.md` |
| Paper metadata, body, and BibTeX | `_papers/*.md` |
| Papers-index introduction | `papers/index.md` |
| Video numbers, titles, captions, URLs, posters, and subtitles | `_data/videos.yml` |
| Real figures and posters | `assets/images/`, `assets/posters/` |
| Small downloadable resources | `downloads/` |
| Global navigation labels | `_data/navigation.yml` |
| Browser title, site URL, base path, indexing | `_config.yml` |
| Reusable carousel markup / interaction | `_includes/video-group.html`, `assets/js/carousel.js` |
| Native first-frame preview and video-load errors | `_includes/video.html`, `assets/js/carousel.js` |
| Generate permanent first-frame posters | `scripts/generate_posters.rb` |

Paper metadata remains in each paper's front matter, not a separate registry.
The longer content-editing guide is `README-CONTENT.md`; its sections on
appearance and videos point back to the settings documented here.

## Add a chapter or paper

The current source contains chapters 2, 4, 5, and 6, and papers 1–5. To add a
new document without overwriting one of those files, for example:

```bash
cp examples/chapter.md _chapters/chapter-07.md
cp examples/paper.md _papers/paper-06.md
```

Fill in `title`, a unique `uid`, and a positive unique `chapter_number` or
`order`. Fill in paper authors, venue, year, description, and citation as needed.
Titles and IDs are required; empty optional descriptions/captions are allowed.
Add the real body text, figures, and registered video keys. Remove unused empty
section headings in a copied starter before publishing.

A chapter filename determines its URL: `_chapters/chapter-07.md` becomes
`/thesis/chapter-07/`. Paper filenames work the same way under `/papers/`.
Navigation lists and chapter pagination are generated automatically. Changing a
title does not change its URL; keep filenames stable after publication.

## Figures, mathematical notation, citations, and downloads

### Figures

Keep actual figure files in `assets/images/` and use the existing include:

```liquid
{% include figure.html
   src="/assets/images/mel.png"
   id="Figure 2.2"
   label="fig-ch02-s1"
   caption="Example speech segment. *Top:* waveform. *Bottom:* Mel spectrogram."
   layout="wide"
%}
```

`id` is the displayed number; `label` is the unique fragment identifier. Keep
them stable for manuscript cross-references. `alt` can provide a separate image
description; otherwise the include derives it from the caption. Optional
`width=800` caps a figure at 800px; optional `link` adds a full-resolution link.
An empty source produces no figure. A nonempty local path must point to a real
file; the checker reports missing local assets.

### Mathematics

Chapters retain math support by default. Set `math: true` in a paper's front
matter when needed. The existing MathJax 3.2.2 configuration is unchanged.
Use double-dollar delimiters, including for inline expressions:

```text
The prediction is $$y = f_\theta(x)$$.
```

For a display equation, use blank lines before and after:

```text
$$
\mathcal{L}(\theta) = \frac{1}{N}\sum_{i=1}^{N}\|f_\theta(x_i)-y_i\|_2^2.
$$
```

MathJax loads from the existing CDN. With no network access, raw mathematical
delimiters may remain visible. This update has not changed the formulas.

### Citations and resources

Thesis BibTeX lives in `_data/thesis.yml`; paper BibTeX stays in each paper's
front matter. YAML `|` preserves its line breaks. The collapsible citation
component and copy button retain their manual-copy fallback. An empty citation
produces no citation block. Real entries with double BibTeX braces are accepted
by the validation script.

Optional `pdf`, `doi`, `arxiv`, `code`, and `download` fields only generate a
button when a real value is supplied. Leave unused fields empty. Local paths
start with `/` and must not include the repository name; the URL helper adds
`baseurl`. For ordinary local Markdown links, use the existing filter:

```liquid
[Thesis overview]({{ '/thesis/' | relative_url }})
```

Small real PDFs or notes can go in `downloads/`; keep large MOV masters outside
the repository. The supplied `mov2mp4.py`, `loudness_normalizer.py`, and
`pdf2png.py` utilities are retained unchanged. This update did not run or alter
your media-conversion pipeline.

## First-time setup on macOS

Use Ruby **3.3.x**, not macOS's system Ruby. The existing project pins Jekyll
**4.4.1**, WEBrick **1.9.1**, and records Bundler **2.6.9** in its supplied
`Gemfile.lock`. The Gemfile, lockfile, and deployment workflow are unchanged.

If already set up for the previous version, use the quick-start commands.
Otherwise, install Apple's development tools if needed:

```bash
xcode-select --install
```

Install Homebrew using its official instructions if `brew --version` does not
work. Then install Ruby:

```bash
brew install ruby@3.3
```

For the default zsh shell, add this line once to `~/.zshrc`:

```bash
export PATH="$(brew --prefix ruby@3.3)/bin:$(brew --prefix)/lib/ruby/gems/3.3.0/bin:$PATH"
```

Reload the shell configuration and verify the selected Ruby:

```bash
source ~/.zshrc
ruby --version
which ruby
gem install bundler -v 2.6.9 --no-document
```

Ruby should report 3.3.x and should not resolve to `/usr/bin/ruby`. Do not use
`sudo gem install` to work around a wrong Ruby installation. For Bash, use
`~/.bash_profile` instead of `~/.zshrc`.

In the website folder:

```bash
bundle _2.6.9_ config set --local path vendor/bundle
bundle _2.6.9_ install
bundle exec jekyll serve --livereload --baseurl ""
```

Keep the supplied `Gemfile.lock`; do not routinely delete it. Bundler installs
the appropriate native dependencies for the current machine. Cached vendor
files from another operating system are not a substitute for `bundle install`.
No new JavaScript or Ruby dependency was added for the carousel.

## Build and validate

Stop the local development server before a separate build in the same folder:

```bash
JEKYLL_ENV=production bundle exec jekyll build
bundle exec ruby scripts/check.rb
```

The source-only check also works without installing Jekyll:

```bash
ruby scripts/check.rb --source-only
```

To check a project-site base path:

```bash
JEKYLL_ENV=production bundle exec jekyll build --baseurl /test-repository --destination _site-path-test
bundle exec ruby scripts/check.rb --baseurl /test-repository _site-path-test
```

The checker validates YAML, required IDs/titles, duplicate keys and IDs, actual
video-group references, local assets, internal links/fragments, base paths, and
accidental publication of placeholder media or the protected template. Empty
optional descriptions, titles, and captions are valid. Numbering supplied by
the author is not automatically changed.

It is a local sanity check, not a remote link crawler, codec test, or formal
accessibility audit. Updated test evidence and limitations are in
**`docs/CAROUSEL-VALIDATION.md`**. The older `docs/UPDATE-VALIDATION.md`, `docs/QA.md`, and engineering documents
are retained as historical notes rather than current delivery status.

### Optional browser regression tests

These are development tools only; Python, Playwright, and FFmpeg are not needed
to view the site. They generate a clearly synthetic test clip, intercept the
remote MP4 requests, and exercise the actual built HTML/CSS/JavaScript. No fixture
is substituted into the delivered website or saved in its content/assets.

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
bundle exec jekyll build --baseurl ""
python3 scripts/test_carousel.py --site _site
```

The default run serves the build on localhost and checks six viewport widths,
every multi-video group, Previous/Next, selection, keyboard operation, trackpad,
touch swipe, no-JavaScript links, first-frame decoding, pause/resume position,
error handling, direct links, resize, and print layout. It writes
`docs/carousel-browser-results.json` and returns a nonzero exit code on failure.
Live Zenodo availability and MathJax rendering are deliberately outside these
controlled browser tests.

`--offline-dom` is a special test harness for restricted environments where
browser navigation is prohibited. It renders the built HTML, routes unchanged
assets into the browser, and exercises controls there; **it is not a substitute
for validating normal HTTP navigation**. This is the mode used for this release's
recorded internal browser checks. See the validation report for exact scope.

## GitHub Pages deployment

The existing `.github/workflows/pages.yml` is retained. In repository settings,
select **Pages → Build and deployment → Source → GitHub Actions**. Push the
source to `main`, including hidden configuration files and the lockfile. Do not
commit `_site/`, caches, or `vendor/`.

The workflow validates source, builds at both the root and a test subpath,
obtains the actual Pages URL, then builds and deploys the Pages artifact.
Pull requests validate without publishing. Check the **Actions** tab for build
errors or approvals. This update did not push changes or run your hosted workflow.

For an already connected repository, the routine is:

```bash
bundle exec jekyll serve --livereload
# After reviewing, stop the server with Control-C.
JEKYLL_ENV=production bundle exec jekyll build
bundle exec ruby scripts/check.rb
git add .
git commit -m "Improve readability and add video carousels"
git push
```

For a newly created empty remote repository, initialize once with `git init`,
set the branch to `main`, and add your actual repository URL as `origin` before
the first push. Do not reinitialize an existing clone or overwrite its remote.
If using a default branch other than `main`, update the existing workflow's
branch filters and `refs/heads/main` conditions.

### URL settings

| Hosting mode | `url` | `baseurl` |
| --- | --- | --- |
| Local preview | `""` | `""` |
| Repository Pages | Your account's HTTPS Pages origin | `"/repository-name"` |
| Account Pages or custom domain | The site's HTTPS origin | `""` |

Do not add a trailing slash to `url`. The supplied Actions workflow derives
production values from GitHub Pages; `_config.yml` can remain convenient for
local work. A custom domain must also be configured with the correct DNS and
Pages settings; this package does not create DNS records.

### Search indexing

The original site blocked indexing. That behavior is preserved without any
visible preview banner through this setting in `_config.yml`:

```yaml
noindex: true
```

It controls both the robots meta tag and `robots.txt`. To allow indexing when
the site is ready, set `noindex: false`, restart Jekyll, rebuild, and redeploy.
The old `placeholder_mode` flag has been removed; it is no longer the appearance
or publication switch. A robots directive is not access control.

## Attribution and implementation references

Original attribution remains in `LICENSE` and `NOTICE.md`. The carousel is a
small native-JavaScript enhancement; the Markdown/Liquid authoring workflow and
plain-CSS structure are retained.

- [Jekyll configuration and exclusions](https://jekyllrb.com/docs/configuration/options/)
- [WAI carousel pattern](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)
- [Jekyll on macOS](https://jekyllrb.com/docs/installation/macos/)
- [Homebrew](https://brew.sh/)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [MathJax 3 configuration](https://docs.mathjax.org/en/v3.2/web/configuration.html)
