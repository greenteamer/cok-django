# Resume PDF Export Module

## Overview

**Purpose:** Generate an ATS-friendly PDF resume from the active profile using ReportLab

**Technology:** ReportLab 4.0.9 (pure Python PDF generation)

**Entry Point:** `GET /resume.pdf` (URL name `export_resume_pdf`; the old `/resume/export/pdf/` permanently redirects here)

**Links to it:** home hero "Resume (PDF)", home "Download PDF Resume" band, `/resume/` buttons, the site-wide Contact block and the footer.

---

## Why ATS-friendly

Recruiters' applicant-tracking systems parse PDFs as text and rank by exact skill names and
standard section headings. Two-column layouts, tables, icons and photos break that parsing.
The PDF is therefore deliberately plain:

- one column, US Letter, 0.7" margins
- standard PDF fonts (Helvetica family), black / dark-gray text
- no photo, icons, tables or images; plain "•" bullets; thin rules under headings only
- standard headings: **SUMMARY, SKILLS, EXPERIENCE, EDUCATION, LANGUAGES, CERTIFICATIONS, KEY ACHIEVEMENTS**
- links are written out as visible text (`linkedin.com/in/...`), because ATS read text, not hrefs
- PDF metadata: title "<Name> — Resume", author, subject (headline), keywords

---

## Data Sources

| Part | Source |
|------|--------|
| Name, headline, engagement, contacts, availability, summary text | `config/identity.py` (same as the site hero — see [`site-identity.md`](./site-identity.md)) |
| Skills | `profile.skills` grouped with `group_skills_by_category()` (advanced / type-level last) |
| Experience | `profile.experiences` (position, company, location, dates, `company_description`, `description` HTML) |
| Education, Languages | `profile.education`, `profile.languages` |
| Certifications, Key Achievements | `profile.certifications`, `profile.achievements` |

The profile's `title`, `summary` (rich text) and `email` are **not** used by the PDF; the summary
is the short value proposition from `config/identity.py`. Empty sections are omitted.

---

## Layout (top to bottom)

1. Name (20pt bold)
2. `HEADLINE | ENGAGEMENT`
3. Contact line: email | location | site | LinkedIn | GitHub (| Telegram when set)
4. Availability line
5. SUMMARY — `VALUE_PROP` + `TOOLING_LINE`
6. SKILLS — one `Category: a, b, c` line per category
7. EXPERIENCE — "Position — Company", "Location | Mon YYYY – Present", optional italic company note, then bullets. Each `<p>`/`<li>` of the CKEditor HTML becomes one bullet. The job header is kept together with its first bullet (`KeepTogether`).
8. EDUCATION, LANGUAGES, CERTIFICATIONS, KEY ACHIEVEMENTS (when present)

The current content renders to about 3 pages.

---

## Technical Implementation

### Files

- `resume/views.py` — `export_resume_pdf()`: active profile → PDF, `Content-Disposition: inline; filename="<Full_Name>_Resume.pdf"`, `X-Robots-Tag: noindex, nofollow`
- `resume/pdf_generator.py` — `generate_resume_pdf(profile)` and one `generate_*_section()` per section; builds with `SimpleDocTemplate`
- `resume/pdf_styles.py` — `get_styles()`, `pdf_text()` / `pdf_markup()`, `HTMLToParagraphs`, `html_to_flowables()`

### Text sanitizing (`pdf_text`, `pdf_markup`)

The standard fonts only cover WinAnsi (cp1252). `pdf_text()` maps the characters the content
uses (`→` → `->`, drops `↗`, `◆`, `✓`, emoji) and removes anything else outside cp1252, so no
blank boxes appear and copy/paste stays clean. `pdf_markup()` additionally XML-escapes the text
for ReportLab paragraph markup (e.g. `P&L`). All database and identity text goes through these.

### HTML to PDF

`HTMLToParagraphs` (an `HTMLParser`) supports `<p>`, `<ul>/<ol>`, `<li>`, `<strong>/<b>`,
`<em>/<i>`, `<br>`. With `paragraphs_as_bullets=True` (used for experience) every `<p>` is a
bullet too. Other tags are ignored; their text is kept.

---

## Error Handling

| Case | Result |
|------|--------|
| No active profile | 404 "No active resume profile found." (logged as warning) |
| Generation error | 404 "Failed to generate PDF resume. Please try again later." (logged with traceback, logger `resume.views` / `resume.pdf_generator`) |

---

## Performance

Generated on every request (~500ms, in-memory `BytesIO`), no caching. Fine for current traffic;
cache the bytes keyed on profile `updated_at` if it ever matters.

---

## Checking the output locally

```bash
make up
curl -o /tmp/resume.pdf http://localhost:8000/resume.pdf
pdftotext -layout /tmp/resume.pdf - | head -40   # what an ATS will "see"
```

`pdftotext` (poppler) is optional; any PDF viewer's "select all + copy" works too.

---

## Related Documentation

- **Resume Models:** [`resume.md`](./resume.md)
- **Site identity / contacts:** [`site-identity.md`](./site-identity.md)
- **API Reference:** [`../api/http.md`](../api/http.md)

---

**Last Updated:** 2026-10-19
