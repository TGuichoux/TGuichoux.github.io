> Current release: local JPEG posters are already included. Set each `poster:`
> in `_data/videos.yml` to its exact `/assets/posters/...jpg` path. Edit
> `_data/frontpage.yml` for the home H1 and home browser-tab title. Run
> `bash scripts/serve.sh` for a source-pinned clean preview. See README.md and
> `docs/POSTER-TITLE-VALIDATION.md` for the complete instructions and test limits.

# Editing the website content and appearance

**Current appearance and carousel guide:** see `README.md`, especially
“Change font sizes”, “Change the width and line spacing”, and “Video carousels”.
All font sizes and width settings are centralized in `assets/css/main.css`.
`chapter-template.md` is preserved unchanged and excluded from publication.

This file is the day-to-day editing guide for the supplementary-material website.
It deliberately covers **only what is displayed on the website**: text, metadata,
figures, videos, links, navigation labels, interface wording, and visual styling.

You do **not** need to understand Jekyll, Liquid, HTML, CSS, or JavaScript for normal
scientific content edits. Most changes happen in Markdown (`.md`) and YAML (`.yml`)
files, which is the intended maintenance workflow for this project.

---

## 1. The short version: which files do I normally edit?

For almost all routine updates, use only these files and folders:

| What you want to change | Edit this |
| --- | --- |
| Your name, role, institution, biography, portrait, profile links | `_data/author.yml` |
| Thesis title, institution, degree, year, supervisors, abstract, thesis links, citation | `_data/thesis.yml` |
| Main menu labels and destinations | `_data/navigation.yml` |
| Video titles, numbering, captions, video URLs, posters, downloads | `_data/videos.yml` |
| Home-page introductory paragraph | `index.md` |
| Thesis-overview explanatory text | `thesis/index.md` |
| Chapter titles, descriptions, text, headings, equations, figures, video placement, references | `_chapters/*.md` |
| Papers-index introductory text | `papers/index.md` |
| Paper title, authors, venue, year, abstract, supplementary text, figures, video placement, links, citation | `_papers/*.md` |
| Figure image files | `assets/images/` |
| Video poster images | `assets/posters/` |
| Small downloadable files | `downloads/` |

If you only want to replace scientific content, **you normally do not edit**
`_layouts/`, `_includes/`, `assets/css/`, or `assets/js/`.

---

## 2. Display-related file organization

Only the files that influence what visitors see are shown below.

```text
supplementary-website/
│
├── index.md                         # Home-page text
│
├── thesis/
│   └── index.md                     # Thesis-overview additional text
│
├── papers/
│   └── index.md                     # Papers-index introduction
│
├── _data/
│   ├── author.yml                   # Name, bio, affiliation, portrait, profile links
│   ├── thesis.yml                   # Thesis metadata, abstract, links, BibTeX
│   ├── navigation.yml               # Top navigation labels and links
│   └── videos.yml                   # All video metadata
│
├── _chapters/
│   ├── chapter-01.md                # Chapter 1 content
│   ├── chapter-02.md                # Chapter 2 content
│   ├── chapter-03.md
│   ├── chapter-04.md
│   └── chapter-05.md
│
├── _papers/
│   ├── paper-01.md                  # Paper 1 content + metadata
│   ├── paper-02.md
│   └── paper-03.md
│
├── assets/
│   ├── images/                      # Figures, avatar, favicon, other images
│   ├── posters/                     # Video poster images
│   ├── css/
│   │   └── main.css                 # Colors, spacing, typography, responsive layout
│   └── js/
│       ├── site.js                  # Small interface behavior + citation copy text
│       └── math.js                  # Equation rendering configuration
│
├── downloads/                       # Small PDFs, text files, supplementary downloads
│
├── _layouts/                        # Overall page structures and fixed interface wording
│   ├── default.html
│   ├── home.html
│   ├── thesis.html
│   ├── chapter.html
│   ├── papers.html
│   └── paper.html
│
└── _includes/                       # Reusable visible components
    ├── header.html
    ├── footer.html
    ├── author-profile.html
    ├── navigation.html
    ├── breadcrumbs.html
    ├── chapter-list.html
    ├── chapter-pagination.html
    ├── paper-list.html
    ├── paper_metadata.html
    ├── resource-links.html
    ├── figure.html
    ├── video.html
    ├── video-group.html
    └── citation.html
```

The important distinction is:

```text
YOUR CONTENT
Markdown + YAML + media files
        │
        ▼
DISPLAY COMPONENTS
layouts + includes + CSS
        │
        ▼
WHAT THE VISITOR SEES
```

For routine thesis/paper updates, stay in the **YOUR CONTENT** layer.

---

# 3. Editing the author information shown across the site

Edit:

```text
_data/author.yml
```

Current structure:

```yaml
name: "[ACADEMIC NAME]"
role: "[ACADEMIC ROLE]"
institution: "[INSTITUTION]"
department: "[DEPARTMENT]"
bio: "[A short academic biography. Add your research area and affiliation here.]"
avatar: "/assets/images/IMG_2954.jpeg"
email: ""
orcid: ""
scholar: ""
github: ""
```

These values are reused automatically in several places.

| Field | Where it appears |
| --- | --- |
| `name` | Top-left site title, author sidebar, thesis author line, footer |
| `role` | Author sidebar |
| `institution` | Author sidebar |
| `department` | Author sidebar |
| `bio` | Author sidebar |
| `avatar` | Author portrait |
| `email` | Sidebar link, if not empty |
| `orcid` | Sidebar link, if not empty |
| `scholar` | Google Scholar link, if not empty |
| `github` | GitHub link, if not empty |

### Replace the portrait

Put your image in:

```text
assets/images/
```

For example:

```text
assets/images/profile.jpg
```

Then change:

```yaml
avatar: "/assets/images/profile.jpg"
```

---

# 4. Editing the main navigation

Edit:

```text
_data/navigation.yml
```

Current structure:

```yaml
main:
  - title: Home
    url: /
  - title: Thesis
    url: /thesis/
  - title: Papers
    url: /papers/
```

Change `title` to rename what appears in the top menu.

For example:

```yaml
main:
  - title: Home
    url: /
  - title: Dissertation
    url: /thesis/
  - title: Publications
    url: /papers/
```

Do not change a `url` unless you also intentionally change the corresponding
page address.

---

# 5. Editing the home page

The home page combines several sources.

## Home-page main title

Edit:

```text
_data/thesis.yml
```

Field:

```yaml
title: "[THESIS TITLE]"
```

## Home-page introductory text

Edit:

```text
index.md
```

Everything below its opening `---` block is normal Markdown text and can be
rewritten freely.

## Home-page thesis information

The institution and year come from:

```text
_data/thesis.yml
```

The chapter list is generated automatically from:

```text
_chapters/*.md
```

The paper list is generated automatically from:

```text
_papers/*.md
```

You do not manually maintain those lists.

## Fixed home-page interface text

These texts are currently stored in:

```text
_layouts/home.html
```

This includes visible wording such as:

- `PhD thesis & research papers`
- `Supplementary material`
- `Explore the thesis`
- `View papers`
- `The thesis`
- `Associated papers`
- `All papers`

Edit that file only if you want to change these interface labels.

---

# 6. Editing thesis metadata

Edit:

```text
_data/thesis.yml
```

Current fields include:

```yaml
title: "[THESIS TITLE]"
subtitle: "PhD thesis · Supplementary material"
institution: "[INSTITUTION]"
degree: "[DEGREE / DISCIPLINE]"
year: "[YEAR]"
defense_date: "[DEFENSE DATE]"
supervisors:
  - "[SUPERVISOR NAME]"
  - "[CO-SUPERVISOR NAME]"
abstract: >-
  [THESIS ABSTRACT PLACEHOLDER]
pdf: ""
code: ""
doi: ""
bibtex: |
  @phdthesis{...}
```

### What is displayed from this file?

| Field | Displayed as |
| --- | --- |
| `title` | Thesis title on home and thesis pages |
| `subtitle` | Subtitle below thesis title |
| `institution` | Thesis metadata + home page |
| `degree` | Thesis metadata |
| `year` | Thesis metadata + home page |
| `defense_date` | Thesis metadata |
| `supervisors` | Supervisor list |
| `abstract` | Thesis abstract |
| `pdf` | PDF button when populated |
| `code` | Code button when populated |
| `doi` | DOI button when populated |
| `bibtex` | Citation / BibTeX block |

Leave unused link fields as an empty string:

```yaml
pdf: ""
```

Do not put text such as `[PDF LINK]` into a URL field.

---

# 7. Editing the thesis overview page

The thesis overview is built from two places.

## Main metadata and abstract

Edit:

```text
_data/thesis.yml
```

## Additional explanatory text

Edit:

```text
thesis/index.md
```

For example, this is where you can explain how the supplementary materials are
organized or how chapter numbering corresponds to the thesis manuscript.

## Fixed thesis-page interface wording

Edit:

```text
_layouts/thesis.html
```

This controls fixed visible labels such as:

- `Thesis overview`
- `Institution`
- `Degree`
- `Supervisors`
- `Year`
- `Defense`
- `Abstract`
- `Chapters`

The actual values next to those labels still come from `_data/thesis.yml`.

---

# 8. Editing a thesis chapter

Each chapter is one Markdown file:

```text
_chapters/chapter-01.md
_chapters/chapter-02.md
...
```

A chapter contains two parts:

1. **front matter** at the top, between `---` lines;
2. **page content** below it.

Example:

```markdown
---
title: '[CHAPTER TITLE]'
uid: ch01
chapter_number: 1
description: '[SHORT CHAPTER DESCRIPTION]'
videos:
- ch01-s1
- ch01-s2
pdf: ''
code: ''
---

## Introduction

Your chapter text goes here.

## Supplementary figures

Your figure components go here.

## Supplementary videos

Your video components go here.
```

## Chapter front-matter fields

| Field | Purpose |
| --- | --- |
| `title` | Visible chapter title |
| `uid` | Internal unique ID; keep unique |
| `chapter_number` | Visible chapter number and chapter ordering |
| `description` | Short subtitle/description shown on chapter lists and page header |
| `videos` | Optional list of video keys used by the page |
| `pdf` | Optional PDF link |
| `code` | Optional code link |

## Chapter body

Below the front matter, write ordinary Markdown.

### Heading

```markdown
## Supplementary experiments
```

### Subheading

```markdown
### Experiment A
```

### Paragraph

```markdown
This section describes the supplementary experiment.
```

### Bullet list

```markdown
- first item
- second item
- third item
```

### Link

```markdown
[Visible link text](https://example.com)
```

### Internal link to another item on the same page

```markdown
[See Figure 1.S1](#fig-ch01-s1)
```

The chapter list, sidebar chapter navigation, and previous/next buttons update
automatically from the chapter files.

---

# 9. Adding, renaming, reordering, or removing a chapter

## Rename a chapter

Change its `title` in the chapter file:

```yaml
title: 'New chapter title'
```

## Change its order

Change:

```yaml
chapter_number: 3
```

Chapter numbers must remain unique.

## Add a chapter

Duplicate one existing chapter file, for example:

```text
_chapters/chapter-05.md
```

and save the copy as:

```text
_chapters/chapter-06.md
```

Then change at minimum:

```yaml
title: '[CHAPTER 6 TITLE]'
uid: ch06
chapter_number: 6
description: '[CHAPTER 6 DESCRIPTION]'
```

## Remove a chapter

Delete its file from `_chapters/`.

It disappears automatically from the thesis lists and navigation.

---

# 10. Editing the papers index

Edit the introductory text here:

```text
papers/index.md
```

The publication list itself is generated automatically from:

```text
_papers/*.md
```

## Fixed papers-index wording

Edit:

```text
_layouts/papers.html
```

This currently contains labels such as:

- `Research publications`
- `Papers`
- `Supplementary material, organized by publication.`
- `Publications`

---

# 11. Editing a paper

Each paper is one file:

```text
_papers/paper-01.md
_papers/paper-02.md
_papers/paper-03.md
```

A paper file contains both its bibliographic metadata and its supplementary
content.

Example structure:

```markdown
---
title: '[PAPER TITLE]'
uid: p01
order: 1
authors:
- '[AUTHOR 1]'
- '[AUTHOR 2]'
venue: '[JOURNAL / CONFERENCE]'
year: '[YEAR]'
description: '[SHORT PAPER SUMMARY]'
doi: ''
pdf: ''
arxiv: ''
code: ''
download: ''
math: true
bibtex: |
  @article{...}
---

## Abstract

Your abstract goes here.

## Supplementary material

Your supplementary content goes here.
```

## Paper metadata fields

| Field | Purpose |
| --- | --- |
| `title` | Paper title |
| `uid` | Unique internal identifier |
| `order` | Ordering on the papers page |
| `authors` | Author list |
| `venue` | Journal or conference |
| `year` | Publication year |
| `description` | Short summary used on paper lists |
| `doi` | DOI link |
| `pdf` | Paper PDF link |
| `arxiv` | arXiv link |
| `code` | Repository link |
| `download` | Additional downloadable material |
| `math` | Enables equation rendering when `true` |
| `bibtex` | Citation displayed at the bottom |

## Fixed paper-page wording

Edit:

```text
_layouts/paper.html
```

This currently includes:

- `Paper · Supplementary material`
- `Return to all papers`

Other paper-list labels come from `_includes/paper-list.html`.

---

# 12. Adding, renaming, reordering, or removing a paper

## Rename

Change:

```yaml
title: 'New paper title'
```

## Reorder

Change:

```yaml
order: 2
```

Each paper should use a unique order number.

## Add a paper

Duplicate an existing file, for example:

```text
_papers/paper-03.md
```

Save the new one as:

```text
_papers/paper-04.md
```

Then change at minimum:

```yaml
title: '[PAPER 4 TITLE]'
uid: p04
order: 4
```

## Remove a paper

Delete its file from `_papers/`.

It disappears automatically from all generated publication lists.

---

# 13. Adding or replacing a figure

Put the image file in:

```text
assets/images/
```

Example:

```text
assets/images/chapter4-comparison.png
```

Then, in the relevant chapter or paper Markdown file, use:

```liquid
{% include figure.html
   src="/assets/images/chapter4-comparison.png"
   id="Figure 4.S1"
   label="fig-ch04-s1"
   caption="Caption displayed under the figure."
   alt="Short accessibility description of the figure."
%}
```

## Figure options

### Wide figure

```liquid
{% include figure.html
   src="/assets/images/chapter4-comparison.png"
   id="Figure 4.S1"
   label="fig-ch04-s1"
   caption="Caption displayed under the figure."
   alt="Short accessibility description of the figure."
   layout="wide"
%}
```

### Limit the displayed width

```liquid
{% include figure.html
   src="/assets/images/chapter4-comparison.png"
   id="Figure 4.S1"
   label="fig-ch04-s1"
   caption="Caption displayed under the figure."
   alt="Short accessibility description of the figure."
   width=700
%}
```

### Add a full-resolution link

```liquid
{% include figure.html
   src="/assets/images/chapter4-comparison.png"
   id="Figure 4.S1"
   label="fig-ch04-s1"
   caption="Caption displayed under the figure."
   alt="Short accessibility description of the figure."
   link="/assets/images/chapter4-comparison-full.png"
%}
```

The visible figure number is controlled by `id`.

The internal link target is controlled by `label`.

For example:

```markdown
[See Figure 4.S1](#fig-ch04-s1)
```

---

# 14. Editing videos

Video metadata is stored in `_data/videos.yml`. For example, this is a real
entry already present in the supplied website:

```yaml
ch06-6_1:
  number: Video 6.1
  title: 'Segment A-421'
  caption: ''
  src: 'https://zenodo.org/records/23059630/files/A-421.mp4'
  poster: ''
  download: ''
  archive: ''
  track: ''
  transcript: ''
```

| Field | Meaning |
| --- | --- |
| `number` | Visible figure/video identifier; do not renumber automatically |
| `title` | Optional title; leave empty when not needed |
| `caption` | Optional caption below the player, supporting Markdown |
| `src` | Direct MP4 URL or a local MP4 path |
| `poster` | Optional real image shown before playback |
| `download` | Optional source/download link |
| `archive` | Optional archive-record link |
| `track` | Optional WebVTT subtitle file |
| `transcript` | Optional transcript link |

An empty `src` omits the video. Without a manually specified poster, a matching
entry in `_data/video_posters.yml` supplies a generated local JPEG. Otherwise
the native player lazily shows the first video frame; no dummy image is used.
See the main README for `scripts/generate_posters.rb` and the delivery limitations.
The video number supplies the accessible player label when its title is empty.

Place a standalone video with:

```liquid
{% include video.html key="ch06-6_1" %}
```

Do not reuse a key twice on one page; its fragment identifier must remain unique.
The same entry may be used on different pages. Keep all existing keys and
numbers stable for cross-references.

---

# 15. Changing a source or adding a real poster

Normally, only `_data/videos.yml` needs editing. Point `src` to the direct MP4,
not the archive's HTML record page. Put an actual thumbnail into `assets/posters/`
and use its path for `poster`; otherwise leave `poster: ""`.

Local asset paths begin with `/assets/` and omit the repository name because the
URL helper adds the site's base path. Existing Zenodo URLs were preserved.
No media was re-encoded by this update. Playback and seeking should be checked
against the actual host before publication.

---

# 16. Grouped-video carousels

Existing `video-group.html` calls now render one video at a time:

```liquid
{% include video-group.html
   keys="ch04-4_1,ch04-4_2,ch04-4_3"
   columns=3
   label="Speech-gesture generation capabilities"
%}
```

The former `columns` parameter is accepted but ignored; it no longer selects a
grid. Existing chapter and paper bodies do not need to be rewritten. New groups
can omit that parameter. The order of keys sets the slide order.

YAML-array input also remains supported:

```yaml
comparison_videos:
  - ch04-4_1
  - ch04-4_2
  - ch04-4_3
```

```liquid
{% include video-group.html keys=page.comparison_videos label="Method comparison" %}
```

Each group has Previous/Next buttons, a current-position counter, and a direct
video selector. A one-video group has no redundant controls. Empty groups are
omitted. Moving away pauses the previous video, and links to non-first videos
reveal the correct slide. Native horizontal scroll-snap supports swiping and
trackpads. Without JavaScript, horizontal scrolling and per-slide anchor links
remain available. Printing displays all slides vertically. There is no autoplay
or automatic rotation. See `README.md`
for keyboard operation, printing, and complete behavior.

Carousel and first-frame preview interaction is in `assets/js/carousel.js`; its markup is in
`_includes/video-group.html`; presentation is in `assets/css/main.css`.

---

# 17. Editing equations

Chapter pages already enable mathematics.

Paper pages need:

```yaml
math: true
```

in their front matter.

Inline equation example:

```text
The model predicts $$y = f_\theta(x)$$ for each input.
```

Displayed equation example:

```text
$$
\mathcal{L}(\theta) = \frac{1}{N}\sum_{i=1}^{N}\|f_\theta(x_i)-y_i\|_2^2.
$$
```

---

# 18. Editing citations

## Thesis citation

Edit:

```text
_data/thesis.yml
```

Field:

```yaml
bibtex: |
  @phdthesis{...}
```

## Paper citation

Edit the `bibtex` field in the relevant file:

```text
_papers/paper-XX.md
```

The site automatically places the citation in a collapsible `Citation / BibTeX`
box.

---

# 19. Editing PDF, DOI, code, arXiv, and download buttons

The reusable resource component supports these fields:

```yaml
pdf: ""
doi: ""
arxiv: ""
code: ""
download: ""
```

For example:

```yaml
pdf: "/downloads/my-paper.pdf"
doi: "10.1234/example.12345"
arxiv: "https://arxiv.org/abs/0000.00000"
code: "https://github.com/username/repository"
download: "/downloads/supplementary-results.zip"
```

The visible button labels (`PDF`, `DOI`, `arXiv`, `Code`, `Download material`)
are defined in:

```text
_includes/resource-links.html
```

Edit that include only if you want to rename those interface labels.

---

# 20. Editing visible interface wording

Most scientific text lives in Markdown/YAML. A smaller set of **site interface
labels** is intentionally stored in layout/include files.

Use this table when you want to change one of those labels.

| Visible wording / element | File |
| --- | --- |
| Browser tab site suffix, generic site description | `_config.yml` |
| Top-left name | `_data/author.yml` |
| Main navigation labels | `_data/navigation.yml` |
| Home-page eyebrow, buttons, section labels | `_layouts/home.html` |
| `Skip to content` accessibility link | `_layouts/default.html` |
| Thesis metadata labels (`Institution`, `Degree`, etc.) | `_layouts/thesis.html` |
| Chapter eyebrow `Thesis · Chapter XX` | `_layouts/chapter.html` |
| Papers-page fixed headings | `_layouts/papers.html` |
| Paper eyebrow and return link | `_layouts/paper.html` |
| Sidebar labels such as `Email`, `ORCID`, `Google Scholar`, `GitHub` | `_includes/author-profile.html` |
| Sidebar `Thesis chapters` / `Thesis overview` | `_includes/author-profile.html` |
| Sidebar generic note `Thesis & papers / Supplementary research material` | `_includes/author-profile.html` |
| Breadcrumb wording (`Home`, `Thesis`, `Papers`, `Chapter`) | `_includes/breadcrumbs.html` |
| `Previous chapter`, `Next chapter`, `Return to thesis overview` | `_includes/chapter-pagination.html` |
| Paper-list `Paper XX` and `Supplementary material` | `_includes/paper-list.html` |
| Resource-button labels | `_includes/resource-links.html` |
| `Citation / BibTeX`, `Copy BibTeX` | `_includes/citation.html` |
| Figure link `Full-resolution figure` | `_includes/figure.html` |
| Video fallback text and media-link labels | `_includes/video.html` |
| Footer wording and theme attribution | `_includes/footer.html` |
| Citation-copy success/error messages | `assets/js/site.js` |
| Carousel controls, native scrolling, first-frame previews | `assets/js/carousel.js` |

This is the complete practical map for changing visible wording that is not
already stored in the normal content files.

---

# 21. Editing colors, fonts, spacing, widths, and responsive layout

All styling remains in **`assets/css/main.css`**. Edit existing values in its
opening `:root` block. The full, current category reference is in **`README.md`**;
it includes all H1–H6 sizes, body text, captions, navigation, metadata, citations,
buttons, footer, print text, font families, line heights, and responsive behavior.

The most common settings are:

```css
--font-size-root: 106.25%;     /* 17px with a default browser size of 16px */
--font-size-body: 1rem;
--font-size-h1: clamp(1.9rem, 3vw, 2.65rem);
--font-size-h2: 1.45rem;
--font-size-h3: 1.15rem;
--font-size-h4: 1.05rem;
--font-size-caption: .94rem;
--font-size-caption-title: .96rem;
--shell-width: 1400px;
--prose-width: 80ch;
--sidebar-width: 204px;
--sidebar-gap: 64px;
--page-gutter: 28px;
--page-gutter-mobile: 20px;
--line-height-body: 1.7;
--line-height-caption: 1.65;
```

`--shell-width` controls the maximum overall width of header, content/sidebar,
and footer. `--prose-width` separately limits text paragraphs and ordinary
figures. A larger shell does not remove the prose cap. Wide figures and video
carousels use the main column. All sizes remain constrained by the viewport.

For example, change `--shell-width` to `1500px` to widen the whole site, or
`--font-size-caption` to `1rem` to make caption text approximately 17px.
Global `rem`-based sizes follow `--font-size-root`. Some list/index titles have
specialized tokens, documented in the README, rather than inheriting generic
H2/H3 sizes. Mobile rules use these same font-size categories.

The existing palette is preserved: `--global-base-color`, `--global-bg-color`,
`--global-text-color`, `--global-text-muted`, `--global-link-color`,
`--global-border-color`, and `--global-footer-bg-color`. Font families remain
`--sans-serif` and `--monospace`.

Save while Jekyll is running, then refresh the browser. Use Command-Shift-R for
a hard refresh if needed. Never edit `_site/assets/css/main.css`, because the
next build overwrites generated output.

---

# 22. Editing the footer

Edit:

```text
_includes/footer.html
```

The author's name comes automatically from:

```text
_data/author.yml
```

The rest of the footer wording is currently written directly in
`_includes/footer.html`.

---

# 23. Placeholder removal, indexing, and the preserved template

The temporary-content notice, missing-resource badges, placeholder citation
warning, dummy posters/figures, and dummy notes download have been removed.
Empty optional values no longer create dummy visible content. The old
`placeholder_mode` flag is no longer used.

The original search-indexing restriction is separately preserved in
`_config.yml`:

```yaml
noindex: true
```

Set `noindex: false` when the site should be indexable, then restart Jekyll and
rebuild/redeploy. This changes robots directives, not access permissions.

`chapter-template.md` is kept byte-for-byte unchanged at the user's request,
including its original instructional examples. It is excluded from Jekyll's
published output. The separate `examples/` starters now use empty fields and
are also excluded. Replace all template-only content and paths in a copied
chapter before publishing it. The protected template itself need not be edited.

---

# 24. Editing the browser title and site description

Edit:

```text
_config.yml
```

Fields:

```yaml
title: "Academic supplementary material"
description: "Supplementary figures, videos, and notes for a PhD thesis and associated papers."
lang: en
```

The browser tab combines the current page title with `site.title`.

For example:

```text
Chapter title · Academic supplementary material
```

---

# 25. Files you should normally NOT edit for content

These are presentation-system files rather than scientific content:

```text
_layouts/
_includes/
assets/css/main.css
assets/js/site.js
assets/js/math.js
```

You **can** edit them, and the sections above explain what visible content they
control, but changing them affects several pages at once.

A useful rule is:

> If you want to change **what a thesis chapter or paper says**, edit Markdown/YAML.
>
> If you want to change **how every page of a certain type looks or what the interface calls something**, edit layouts/includes/CSS.

---

# 26. Files that are generated and should never be edited manually

Do not edit content inside:

```text
_site/
```

That directory contains generated HTML. Any manual changes there will be lost.

Always edit the corresponding source file instead.

---

# 27. Fast lookup: “I want to change…”

| I want to change… | Go to… |
| --- | --- |
| My name | `_data/author.yml` |
| My portrait | `_data/author.yml` + `assets/images/` |
| My biography | `_data/author.yml` |
| Top menu wording | `_data/navigation.yml` |
| Thesis title | `_data/thesis.yml` |
| Thesis abstract | `_data/thesis.yml` |
| Supervisor names | `_data/thesis.yml` |
| Thesis PDF link | `_data/thesis.yml` |
| Home-page introductory paragraph | `index.md` |
| Home-page button wording | `_layouts/home.html` |
| Thesis overview explanatory paragraph | `thesis/index.md` |
| A chapter title | corresponding `_chapters/chapter-XX.md` |
| A chapter subtitle/summary | `description` in the chapter file |
| Chapter text | corresponding `_chapters/chapter-XX.md` |
| Chapter order | `chapter_number` in the chapter file |
| Previous/next chapter button wording | `_includes/chapter-pagination.html` |
| A paper title | corresponding `_papers/paper-XX.md` |
| Paper authors | corresponding `_papers/paper-XX.md` |
| Paper venue/year | corresponding `_papers/paper-XX.md` |
| Paper abstract | corresponding `_papers/paper-XX.md` |
| Paper ordering | `order` in the paper file |
| Paper DOI/PDF/code/arXiv | corresponding `_papers/paper-XX.md` |
| A figure image | `assets/images/` + page Markdown |
| A figure caption | page Markdown |
| Figure numbering | `id` in the figure include call |
| Video title/caption/number | `_data/videos.yml` |
| Video file URL | `_data/videos.yml` |
| Video poster | `_data/videos.yml` + `assets/posters/` |
| Which videos appear on a page | chapter/paper Markdown |
| Two/three-column video layout | chapter/paper Markdown |
| Citation/BibTeX | `_data/thesis.yml` or corresponding paper file |
| Footer text | `_includes/footer.html` |
| Link/button labels such as PDF/DOI/Code | `_includes/resource-links.html` |
| Accent color | `assets/css/main.css` |
| Main text width | `assets/css/main.css` → `--prose-width` |
| Overall site width | `assets/css/main.css` → `--shell-width` |
| Fonts | `assets/css/main.css` |
| Mobile layout | responsive section at the bottom of `assets/css/main.css` |
| Preview notice | `_layouts/default.html` + `_config.yml` |
| Browser title suffix | `_config.yml` |

---

# 28. Recommended editing workflow

For day-to-day work, think of the site in this order:

```text
1. Update author/thesis/paper metadata in YAML
2. Write or edit page text in Markdown
3. Add figures to assets/images/
4. Add video metadata to _data/videos.yml
5. Place figures/videos in the desired chapter or paper Markdown file
6. Only edit layouts/includes/CSS if you want to change the interface itself
```

The goal is that almost all scientific updates remain simple content edits rather
than front-end development.
