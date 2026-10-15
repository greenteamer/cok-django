# Blog Cover Generator

## Overview

Staff-only tool that produces blog cover images (featured / Open Graph images)
from an editable HTML/CSS layout. Text is edited directly on the image in the
browser; the result is exported as PNG or JPEG.

**Scope**: Producing cover image files. The tool does NOT upload or attach the
image to a post — download the file and set it as the post's `featured_image`
in the admin.

**Entry points**:
- View: `blog/views.py` → `cover_generator`
- Template: `templates/blog/cover_generator.html` (layout, styles and editor script in one file)
- URL: `/admin/tools/cover/` (name: `cover_generator`), also linked in the admin sidebar under **Blog → Cover generator**

---

## Usage

1. `make up`, log in to `/admin/` as a staff user.
2. Open **Blog → Cover generator**, or `/admin/tools/cover/?post=<id>` to prefill from a post.
3. Click any text on the image and edit it.
4. To color text: select it, then press a color swatch in the toolbar
   (`Accent` = title accent color, `Clear` = remove color).
5. Choose file name, format (PNG / JPEG) and scale (1600×900 or @2x 3200×1800), press **Download**.
6. Upload the file as the post's featured image.

---

## Behavior

### Prefill from a post

`?post=<id>` (numeric). If the post exists:

| Canvas element | Source |
|----------------|--------|
| Title | `post.title` (plain text, escaped) |
| Chips (top-left) | First 3 `post.tags` names |
| Badge (bottom-right) | `post.category.name`, falls back to `npm` |
| File name | `<post.slug>-cover` |

Unknown or invalid `post` → default sample layout (no error).
The terminal block always starts from the sample content and must be edited by hand.

### Editable elements

- Chips — editable; toolbar `+` / `−` adds/removes chips
- Terminal tab title and terminal body (multi-line, Enter adds a line)
- Title, badge (single-line, Enter finishes editing)
- Toggles: hide terminal, hide corner brackets
- Paste is always inserted as plain text

### Drafts

Edits are autosaved to `localStorage` under `cover-draft:<post id>` (or
`cover-draft:default`) — per browser, per post. **Reset** discards the draft and
restores the server-rendered defaults. Drafts are not stored on the server.

### Export

- Rendered client-side by [`html-to-image`](https://github.com/bubkoo/html-to-image) `1.11.11`
  (loaded from `cdn.jsdelivr.net`), after `document.fonts.ready`.
- The canvas `#cover` is a fixed 1600×900 px element; the on-screen preview is
  only CSS-scaled, so export size never depends on the browser window.
- JPEG quality 0.92; PNG is lossless.
- Fonts: JetBrains Mono (mono) and Plus Jakarta Sans (title) from Google Fonts.

---

## Customizing the design

All visual tokens live in the `<style>` block of the template:

- Canvas palette: CSS variables on `#cover` (`--bg`, `--dot`, `--ink`, `--accent`, `--bracket`)
- Terminal token colors: `.t-*` classes; to add a color, add a `.t-<name>` class,
  a toolbar swatch with `data-color="t-<name>"`, and the class name to `COLOR_CLASSES` in the script
- Positions of blocks are absolute pixel values for the 1600×900 canvas

---

## Constraints

- Access: `staff_member_required` (anonymous → redirect to admin login)
- Requires internet access in the editor's browser (CDN script + Google Fonts)
- Not part of the public site: `noindex`, under `/admin/` (disallowed in `robots.txt`)
- Fixed aspect ratio 16:9; other sizes (e.g. 1200×630) require layout changes
