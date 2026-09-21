# Text Utilities (`config/text.py`)

Shared helpers for turning user-entered markup into plain text.

---

## Purpose

Some model fields are **plain-text by contract**: they are rendered with Django
autoescaping in cards, `<meta>` tags and JSON-LD. If HTML tags, Markdown syntax
or HTML entities are stored in them, readers see the markup literally
(e.g. `<a href="...">` or `&mdash;`).

`config/text.py` is the single place that defines how markup becomes plain text.
Models normalize such fields in `save()` using these helpers, so the database
always holds clean text and templates stay simple.

---

## API

### `markup_to_text(value) -> str`

Converts a Markdown / HTML fragment (or plain text) to a single line of plain text.

1. Renders Markdown (`extra`, `sane_lists`); raw HTML passes through
2. Strips all tags
3. Decodes HTML entities (`&mdash;` → `—`, `&amp;` → `&`)
4. Collapses whitespace to single spaces

Use for **user-entered** summary fields.

```python
markup_to_text('See <a href="/x/">part 1</a> &mdash; `let x = 1`')
# 'See part 1 — let x = 1'
```

### `html_to_text(value) -> str`

Steps 2–4 only. Use for values that are **already HTML** (e.g. rendered
`Post.content`), so Markdown syntax inside them is not re-interpreted.

### `truncate_text(value, max_length) -> str`

Returns `value` unchanged if it fits; otherwise cuts to `max_length - 3`
characters and appends `...` (result length is exactly `max_length`).

---

## Where It Is Used

| Field | Source when empty | Max length |
|-------|-------------------|------------|
| `blog.Post.excerpt` | `html_to_text(content)` | 500 |
| `blog.Post.meta_description` | `excerpt` | 160 |

Also used by migration `blog/0005_post_plain_text_summaries` to clean existing rows.

---

## Adding a New Plain-Text Field

When a field is displayed as plain text but may receive pasted HTML/Markdown:

1. In the model's `save()`: `self.field = truncate_text(markup_to_text(self.field), N)`
2. Add a data migration that applies the same normalization to existing rows
3. Render the field with autoescaping (no `|safe`)
4. Document the invariant in the module's doc and add the field to the table above

---

## Security Notes

- Output is **not** HTML-safe by itself: decoded entities may produce `<`, `>`, `&`.
  Safety comes from template autoescaping (and `|escapejs` in JSON-LD).
- Never mark these values `|safe`.

---

**Last Updated**: 2026-09-21
