"""
Resume PDF Generator

This module generates professional resume PDFs using ReportLab.
Uses two-column layout with main content on left and sidebar on right.
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    FrameBreak, Image as RLImage, Table, TableStyle
)
from reportlab.lib import colors
from PIL import Image as PILImage, ImageDraw
import logging

from .pdf_styles import get_styles, html_to_flowables, strip_html_tags

logger = logging.getLogger(__name__)

# Unicode diamond character for achievements
DIAMOND_CHAR = '◆'


def create_circular_photo(image_path, size=100):
    """
    Create circular profile photo for PDF.

    Args:
        image_path (str): Path to image file
        size (int): Diameter in pixels

    Returns:
        BytesIO: Buffer with PNG image, or None if error
    """
    try:
        # Open and resize image
        img = PILImage.open(image_path)
        img = img.convert('RGB')
        img = img.resize((size, size), PILImage.LANCZOS)

        # Create circular mask
        mask = PILImage.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        # Apply mask
        output = PILImage.new('RGBA', (size, size))
        output.paste(img, (0, 0))
        output.putalpha(mask)

        # Save to buffer
        buffer = BytesIO()
        output.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"Failed to create circular photo: {e}")
        return None


def generate_header_section(profile, styles):
    """
    Generate header section with name, title, contacts, and photo.

    Args:
        profile: Profile model instance
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    # Name
    flowables.append(Paragraph(profile.full_name, styles['name']))

    # Professional title
    flowables.append(Paragraph(profile.title, styles['professional_title']))

    # Contact information (email, LinkedIn, location)
    contact_parts = []
    if profile.email:
        contact_parts.append(profile.email)
    if profile.linkedin_url:
        contact_parts.append(f'<link href="{profile.linkedin_url}">LinkedIn</link>')
    if profile.location:
        contact_parts.append(profile.location)

    if contact_parts:
        contact_text = ' | '.join(contact_parts)
        flowables.append(Paragraph(contact_text, styles['contact']))

    flowables.append(Spacer(1, 12))

    return flowables


def generate_experience_section(experiences, styles):
    """
    Generate experience section with job history.

    Args:
        experiences: QuerySet of Experience instances
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    if not experiences:
        return flowables

    # Section heading
    flowables.append(Paragraph('EXPERIENCE', styles['section_heading']))

    for exp in experiences:
        # Job title
        flowables.append(Paragraph(exp.position, styles['job_title']))

        # Company name and location
        company_text = exp.company
        if exp.location:
            company_text += f', {exp.location}'
        flowables.append(Paragraph(company_text, styles['company']))

        # Date range
        start_date_str = exp.start_date.strftime('%B %Y')
        if exp.is_current:
            date_text = f'{start_date_str} - Present'
        else:
            end_date_str = exp.end_date.strftime('%B %Y') if exp.end_date else ''
            date_text = f'{start_date_str} - {end_date_str}'

        flowables.append(Paragraph(date_text, styles['date']))

        # Company description (if provided)
        if exp.company_description:
            flowables.append(Paragraph(exp.company_description, styles['body']))

        # Job description (convert HTML to flowables)
        if exp.description:
            description_flowables = html_to_flowables(
                exp.description,
                styles['body'],
                styles['bullet']
            )
            flowables.extend(description_flowables)

        flowables.append(Spacer(1, 12))

    return flowables


def generate_summary_section(profile, styles):
    """
    Generate professional summary section.

    Args:
        profile: Profile model instance
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    if not profile.summary:
        return flowables

    # Section heading
    flowables.append(Paragraph('SUMMARY', styles['section_heading']))

    # Summary text (strip HTML for simplicity)
    summary_text = strip_html_tags(profile.summary)
    flowables.append(Paragraph(summary_text, styles['body']))

    flowables.append(Spacer(1, 12))

    return flowables


def generate_achievements_section(achievements, styles):
    """
    Generate key achievements section with diamond icons.

    Args:
        achievements: QuerySet of Achievement instances
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    if not achievements:
        return flowables

    # Section heading
    flowables.append(Paragraph('KEY ACHIEVEMENTS', styles['section_heading']))

    for achievement in achievements:
        # Achievement title with diamond icon
        title_text = f'{DIAMOND_CHAR} {achievement.title}'
        flowables.append(Paragraph(title_text, styles['achievement']))

        # Achievement description
        flowables.append(Paragraph(achievement.description, styles['achievement_desc']))

    flowables.append(Spacer(1, 12))

    return flowables


def generate_certifications_section(certifications, styles):
    """
    Generate certifications section.

    Args:
        certifications: QuerySet of Certification instances
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    if not certifications:
        return flowables

    # Section heading
    flowables.append(Paragraph('CERTIFICATIONS', styles['section_heading']))

    for cert in certifications:
        # Certification name and provider
        cert_text = f'<b>{cert.name}</b>'
        flowables.append(Paragraph(cert_text, styles['list_item']))

        provider_text = cert.provider
        if cert.date_obtained:
            provider_text += f' - {cert.date_obtained.strftime("%Y")}'

        flowables.append(Paragraph(provider_text, styles['body']))
        flowables.append(Spacer(1, 4))

    flowables.append(Spacer(1, 12))

    return flowables


def generate_skills_section(skills, styles):
    """
    Generate skills section grouped by category.

    Args:
        skills: QuerySet of Skill instances
        styles: Dictionary of ParagraphStyles

    Returns:
        list: List of flowables
    """
    flowables = []

    if not skills:
        return flowables

    # Section heading
    flowables.append(Paragraph('SKILLS', styles['section_heading']))

    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category = skill.category or 'Other'
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill.name)

    # Display skills by category
    for category, skill_names in skills_by_category.items():
        if category and category != 'Other':
            flowables.append(Paragraph(f'<b>{category}</b>', styles['list_item']))

        # List skills
        skills_text = ', '.join(skill_names)
        flowables.append(Paragraph(skills_text, styles['body']))
        flowables.append(Spacer(1, 6))

    return flowables


def generate_resume_pdf(profile):
    """
    Generate professional resume PDF from profile data.

    Args:
        profile: Profile model instance

    Returns:
        BytesIO: Buffer containing PDF data

    Raises:
        Exception: If PDF generation fails
    """
    try:
        # Create buffer
        buffer = BytesIO()

        # Get styles
        styles = get_styles()

        # Create document with two-column layout
        doc = BaseDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )

        # Define frames
        # Main frame (left column) - 4.5 inches wide
        main_frame = Frame(
            x1=0.75*inch,
            y1=0.5*inch,
            width=4.5*inch,
            height=10*inch,
            id='main',
            showBoundary=0
        )

        # Sidebar frame (right column) - 2.5 inches wide
        sidebar_frame = Frame(
            x1=5.55*inch,  # 0.75 + 4.5 + 0.3 (gutter)
            y1=0.5*inch,
            width=2.5*inch,
            height=10*inch,
            id='sidebar',
            showBoundary=0
        )

        # Create page template with both frames
        page_template = PageTemplate(
            id='TwoColumn',
            frames=[main_frame, sidebar_frame]
        )

        doc.addPageTemplates([page_template])

        # ===========================================================
        # BUILD FLOWABLES
        # ===========================================================

        flowables = []

        # --- MAIN COLUMN (LEFT) ---

        # Header section (name, title, contacts)
        flowables.extend(generate_header_section(profile, styles))

        # Profile photo (if exists)
        if profile.photo:
            try:
                photo_buffer = create_circular_photo(profile.photo.path, size=100)
                if photo_buffer:
                    photo_image = RLImage(photo_buffer, width=1.2*inch, height=1.2*inch)
                    flowables.append(photo_image)
                    flowables.append(Spacer(1, 12))
            except Exception as e:
                logger.warning(f"Could not add profile photo: {e}")

        # Experience section
        experiences = profile.experiences.all()
        flowables.extend(generate_experience_section(experiences, styles))

        # --- SWITCH TO SIDEBAR (RIGHT COLUMN) ---
        flowables.append(FrameBreak())

        # Summary section
        flowables.extend(generate_summary_section(profile, styles))

        # Achievements section
        achievements = profile.achievements.all()
        flowables.extend(generate_achievements_section(achievements, styles))

        # Certifications section
        certifications = profile.certifications.all()
        flowables.extend(generate_certifications_section(certifications, styles))

        # Skills section
        skills = profile.skills.all()
        flowables.extend(generate_skills_section(skills, styles))

        # ===========================================================
        # BUILD PDF
        # ===========================================================

        doc.build(flowables)

        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise
