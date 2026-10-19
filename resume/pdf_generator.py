"""
Resume PDF Generator

Builds the ATS-friendly resume served at /resume.pdf with ReportLab.

Layout rules (see docs/modules/resume-pdf-export.md):
- one column, US Letter, standard fonts, no photo, icons or tables
- standard section headings ATS parsers look for:
  SUMMARY, SKILLS, EXPERIENCE, EDUCATION, LANGUAGES, CERTIFICATIONS
- name, headline and contacts come from config/identity.py, the same
  source as the home page and /resume/; everything else from the database
"""

from io import BytesIO
import logging

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate

from config import identity
from .models import group_skills_by_category
from .pdf_styles import get_styles, html_to_flowables, pdf_markup

logger = logging.getLogger(__name__)

MARGIN = 0.7 * inch


def _link(url, label=None):
    """Clickable link whose visible text is the URL itself (ATS reads text, not hrefs)."""
    label = label or url.replace("https://", "").replace("www.", "").rstrip("/")
    return f'<link href="{pdf_markup(url)}">{pdf_markup(label)}</link>'


def generate_header_section(profile, styles):
    """Name, headline, contact line and availability."""
    flowables = [
        Paragraph(pdf_markup(identity.NAME), styles["name"]),
        Paragraph(pdf_markup(f"{identity.HEADLINE} | {identity.ENGAGEMENT}"), styles["headline"]),
    ]

    contacts = [
        _link(f"mailto:{identity.EMAIL}", identity.EMAIL),
        pdf_markup(identity.LOCATION),
        _link(identity.SITE_URL),
        _link(identity.LINKEDIN_URL),
        _link(identity.GITHUB_URL),
    ]
    if identity.TELEGRAM_HANDLE:
        contacts.append(_link(f"https://t.me/{identity.TELEGRAM_HANDLE}", f"Telegram @{identity.TELEGRAM_HANDLE}"))
    flowables.append(Paragraph(" | ".join(contacts), styles["contact"]))
    flowables.append(Paragraph(pdf_markup(identity.AVAILABILITY), styles["contact"]))
    return flowables


def section_heading(title, styles):
    """Upper-case heading with a thin rule under it."""
    return [
        Paragraph(title.upper(), styles["section_heading"]),
        HRFlowable(width="100%", thickness=0.6, color=HexColor("#999999"), spaceBefore=0, spaceAfter=4),
    ]


def generate_summary_section(profile, styles):
    """Positioning from config/identity.py (the same words as the site hero)."""
    text = f"{identity.VALUE_PROP} {identity.TOOLING_LINE}"
    return section_heading("Summary", styles) + [Paragraph(pdf_markup(text), styles["body"])]


def generate_skills_section(skills, styles):
    """One "Category: a, b, c" line per category, advanced / type-level last."""
    groups = group_skills_by_category(skills)
    if not groups:
        return []
    flowables = section_heading("Skills", styles)
    for category, category_skills in groups.items():
        names = ", ".join(pdf_markup(s.name) for s in category_skills)
        flowables.append(Paragraph(f"<b>{pdf_markup(category)}:</b> {names}", styles["skills_line"]))
    return flowables


def _date_range(exp):
    start = exp.start_date.strftime("%b %Y")
    end = "Present" if exp.is_current else exp.end_date.strftime("%b %Y")
    return f"{start} – {end}"


def generate_experience_section(experiences, styles):
    """Job history: title — company, location | dates, then bullets."""
    if not experiences:
        return []
    flowables = section_heading("Experience", styles)
    for exp in experiences:
        meta = " | ".join(part for part in [pdf_markup(exp.location), _date_range(exp)] if part)
        head = [
            Paragraph(f"{pdf_markup(exp.position)} — {pdf_markup(exp.company)}", styles["job_title"]),
            Paragraph(meta, styles["job_meta"]),
        ]
        if exp.company_description:
            head.append(Paragraph(pdf_markup(exp.company_description), styles["company_note"]))
        body = html_to_flowables(exp.description, styles["body"], styles["bullet"], paragraphs_as_bullets=True)
        # Keep the job header with its first bullet so a page never ends on a title.
        flowables.append(KeepTogether(head + body[:1]))
        flowables.extend(body[1:])
    return flowables


def generate_education_section(education, styles):
    if not education:
        return []
    flowables = section_heading("Education", styles)
    for edu in education:
        title = f"{pdf_markup(edu.degree)}, {pdf_markup(edu.institution)}" if edu.degree else pdf_markup(edu.institution)
        meta = " | ".join(part for part in [pdf_markup(edu.location), edu.years] if part)
        flowables.append(Paragraph(f"<b>{title}</b>" + (f" — {meta}" if meta else ""), styles["skills_line"]))
    return flowables


def generate_languages_section(languages, styles):
    if not languages:
        return []
    text = "; ".join(
        f"{pdf_markup(lang.name)} ({pdf_markup(lang.proficiency)})" if lang.proficiency else pdf_markup(lang.name)
        for lang in languages
    )
    return section_heading("Languages", styles) + [Paragraph(text, styles["skills_line"])]


def generate_certifications_section(certifications, styles):
    if not certifications:
        return []
    flowables = section_heading("Certifications", styles)
    for cert in certifications:
        text = f"<b>{pdf_markup(cert.name)}</b> — {pdf_markup(cert.provider)}"
        if cert.date_obtained:
            text += f", {cert.date_obtained.strftime('%Y')}"
        flowables.append(Paragraph(text, styles["skills_line"]))
    return flowables


def generate_achievements_section(achievements, styles):
    if not achievements:
        return []
    flowables = section_heading("Key Achievements", styles)
    for achievement in achievements:
        text = f"<b>{pdf_markup(achievement.title)}.</b> {pdf_markup(achievement.description)}"
        flowables.append(Paragraph(text, styles["bullet"], bulletText="•"))
    return flowables


def generate_resume_pdf(profile):
    """
    Generate the ATS-friendly resume PDF for `profile`.

    Args:
        profile: Profile model instance

    Returns:
        BytesIO: Buffer containing PDF data

    Raises:
        Exception: If PDF generation fails
    """
    try:
        buffer = BytesIO()
        styles = get_styles()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
            title=f"{identity.NAME} — Resume",
            author=identity.NAME,
            subject=identity.HEADLINE,
            keywords="React Native, Expo, React, TypeScript, Next.js, Node.js, GraphQL, contractor",
        )

        flowables = []
        flowables.extend(generate_header_section(profile, styles))
        flowables.extend(generate_summary_section(profile, styles))
        flowables.extend(generate_skills_section(profile.skills.all(), styles))
        flowables.extend(generate_experience_section(profile.experiences.all(), styles))
        flowables.extend(generate_education_section(profile.education.all(), styles))
        flowables.extend(generate_languages_section(profile.languages.all(), styles))
        flowables.extend(generate_certifications_section(profile.certifications.all(), styles))
        flowables.extend(generate_achievements_section(profile.achievements.all(), styles))

        doc.build(flowables)

        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise
