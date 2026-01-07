# Resume PDF Export Module

## Overview

**Purpose:** Generate professional PDF resumes from database content using ReportLab

**Technology:** ReportLab 4.0.9 (pure Python PDF generation)

**Entry Point:** `GET /resume/export/pdf/`

---

## Architecture

### Components

**PDF Generation Pipeline:**
```
User Request → View → PDF Generator → ReportLab → PDF Response
```

**Files:**
- `resume/views.py` - HTTP view handler (`export_resume_pdf`)
- `resume/pdf_generator.py` - Core PDF generation logic
- `resume/pdf_styles.py` - ReportLab styles (colors, fonts, paragraph styles)
- `config/urls.py` - URL routing

### Data Flow

1. User clicks "Download PDF Resume" button on home page
2. Request sent to `/resume/export/pdf/`
3. View retrieves active Profile with related data (experiences, skills, certifications, achievements)
4. PDF generator creates two-column layout with ReportLab
5. HTTP response with `Content-Disposition: attachment` triggers download

---

## PDF Layout

### Two-Column Design

**Page Size:** US Letter (8.5" × 11")

**Left Column (Main - 4.5"):**
- Header (name, title, contacts, photo)
- Experience section with job history

**Right Column (Sidebar - 2.5"):**
- Professional summary
- Key achievements with diamond icons
- Certifications
- Skills grouped by category

**Implementation:**
```python
# Two frames for two-column layout
main_frame = Frame(x1=0.75*inch, y1=0.5*inch, width=4.5*inch, height=10*inch)
sidebar_frame = Frame(x1=5.55*inch, y1=0.5*inch, width=2.5*inch, height=10*inch)
```

Frames switch via `FrameBreak()` flowable.

---

## Technical Implementation

### HTML to PDF Conversion

**Challenge:** Experience descriptions contain HTML from CKEditor

**Solution:** Custom HTML parser converts to ReportLab Paragraph flowables

**Supported Tags:** `<p>`, `<ul>`, `<li>`, `<strong>`, `<b>`, `<em>`, `<i>`, `<br>`

**Example:**
```html
<ul>
  <li>Increased efficiency by <strong>30%</strong></li>
  <li>Led team of 5 developers</li>
</ul>
```

Converts to:
```
• Increased efficiency by 30%
• Led team of 5 developers
```

### Profile Photo Processing

**Steps:**
1. Open image with Pillow
2. Resize to 100×100px
3. Create circular mask with ImageDraw
4. Convert to ReportLab Image flowable
5. Place in header section

**Error Handling:** If photo processing fails, continue without photo (logged as warning)

### Styling

**Color Palette:**
- Primary Blue (#2563eb) - Name, titles
- Dark Gray (#1f2937) - Body text
- Light Gray (#6b7280) - Meta information
- Accent Blue (#3b82f6) - Achievements, links

**Fonts:**
- Helvetica (regular)
- Helvetica-Bold (headings, job titles)

**Font Sizes:**
- Name: 24pt
- Professional Title: 11pt
- Section Headings: 14pt
- Body Text: 10pt

---

## API

### Endpoint

**URL:** `GET /resume/export/pdf/`

**Authentication:** None (public endpoint)

**Parameters:** None

**Response:**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="<FullName>_Resume.pdf"`
- **Status Codes:**
  - `200 OK` - PDF generated successfully
  - `404 Not Found` - No active profile or generation failed

**Example:**
```bash
curl -O http://localhost:8000/resume/export/pdf/
# Downloads: Aleksandr_Korovkin_Resume.pdf
```

---

## Usage

### User Flow

1. Visit home page
2. Scroll to "Download My Resume" section (between Hero and Technologies)
3. Click "Download PDF Resume" button
4. PDF downloads automatically with filename: `{FirstName}_{LastName}_Resume.pdf`

### Admin Configuration

**Prerequisites:**
1. Create active Profile (`is_active=True`) via Django Admin
2. Add experiences, skills, certifications, achievements
3. Optionally upload profile photo

**Only ONE profile can be active** - this determines which resume is exported

---

## Error Handling

### Error Scenarios

1. **No Active Profile**
   - Returns 404: "No active resume profile found."
   - Logged as warning

2. **PDF Generation Failure**
   - Returns 404: "Failed to generate PDF resume."
   - Logged as error with full traceback

3. **Missing Profile Photo**
   - Skips photo, continues generation
   - No error to user

4. **Corrupted Image File**
   - Catches exception during Pillow processing
   - Skips photo, continues generation
   - Logged as warning

5. **HTML Parsing Errors**
   - Fallback: strip all HTML tags, use plain text
   - Continues generation

### Logging

**Logger:** `resume.pdf_generator`

**Log Levels:**
- `INFO` - Successful PDF generation
- `WARNING` - Non-critical issues (missing photo, etc.)
- `ERROR` - PDF generation failures

---

## Code Structure

### pdf_generator.py Functions

**Main Function:**
- `generate_resume_pdf(profile)` - Orchestrates PDF generation, returns BytesIO buffer

**Section Generators:**
- `generate_header_section()` - Name, title, contacts
- `generate_experience_section()` - Job history with HTML conversion
- `generate_summary_section()` - Professional summary
- `generate_achievements_section()` - Achievements with diamond icons
- `generate_certifications_section()` - Certifications list
- `generate_skills_section()` - Skills grouped by category

**Helper Functions:**
- `create_circular_photo()` - Photo processing with Pillow

### pdf_styles.py

**Exports:**
- `get_styles()` - Returns dictionary of all ParagraphStyle objects
- `html_to_flowables()` - Converts HTML to list of Paragraph flowables
- `strip_html_tags()` - Strips HTML, returns plain text
- `HTMLToParagraphs` class - Custom HTML parser

---

## Performance

**Generation Time:** ~500ms for typical resume (5 experiences, 20 skills)

**Memory Usage:** Minimal (operates in-memory with BytesIO buffer)

**Database Queries:** Optimized with `select_related` and `prefetch_related`

---

## Security

**Public Access:** No authentication required (resume is public information)

**Input Validation:** None needed (generates from trusted database content)

**XSS Protection:** HTML content from CKEditor is trusted (admin-only input)

**File Upload:** Profile photos validated by Django and Pillow

---

## Dependencies

**Required Packages:**
- `reportlab==4.0.9` - PDF generation
- `Pillow==10.1.0` - Image processing (already installed)

**System Dependencies:** None (pure Python)

---

## Troubleshooting

### PDF Not Downloading

**Symptom:** 404 error when clicking button

**Solutions:**
1. Check active profile exists: `Profile.objects.filter(is_active=True).count()`
2. Check server logs: `make logs`
3. Verify URL pattern in `config/urls.py`

### PDF Layout Issues

**Symptom:** Content overflow or incorrect spacing

**Solutions:**
1. Check `pdf_styles.py` for spacing constants
2. Adjust Frame dimensions in `pdf_generator.py`
3. Test with different content lengths

### Photo Not Rendering

**Symptom:** PDF generates but no photo appears

**Solutions:**
1. Check photo file exists: `profile.photo.path`
2. Check file permissions
3. Verify image format (JPEG, PNG supported)
4. Check server logs for Pillow errors

### Unicode/Encoding Errors

**Symptom:** Special characters render incorrectly

**Solutions:**
1. Helvetica font supports Western European characters
2. For Cyrillic/Asian: add custom fonts to ReportLab
3. Update `pdf_styles.py` font definitions

---

## Future Enhancements

**Potential additions:**

1. **Multiple Templates** - Different visual styles
2. **Custom PDF Configuration** - User selects sections to include
3. **Internationalization** - Multi-language support
4. **PDF Caching** - Cache generated PDFs for performance
5. **Custom Fonts** - Support for non-Latin scripts
6. **A4 Page Size Option** - Toggle between US Letter and A4
7. **Color Themes** - Different color schemes
8. **QR Code** - Add QR code linking to online portfolio

---

## Related Documentation

- **Resume Models:** See `docs/modules/resume.md` for data structure
- **API Reference:** See `docs/api/http.md` for endpoint details
- **Configuration:** See `docs/config/environment.md` for settings

---

**Last Updated:** 2026-01-07
