"""
ReportLab PDF Styles

This module defines all styling constants and ParagraphStyle objects
for resume PDF generation.
"""

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from html.parser import HTMLParser
from html import unescape


# =============================================================================
# COLOR PALETTE (based on reference PDF)
# =============================================================================

COLOR_PRIMARY_BLUE = HexColor('#2563eb')    # Blue for name/title
COLOR_TEXT_DARK = HexColor('#1f2937')       # Dark gray for text
COLOR_TEXT_LIGHT = HexColor('#6b7280')      # Light gray for meta info
COLOR_ACCENT = HexColor('#3b82f6')          # Accent blue
COLOR_WHITE = HexColor('#ffffff')           # White


# =============================================================================
# FONT SIZES
# =============================================================================

FONT_SIZE_NAME = 24
FONT_SIZE_TITLE = 11
FONT_SIZE_HEADING = 14
FONT_SIZE_SUBHEADING = 12
FONT_SIZE_BODY = 10
FONT_SIZE_SMALL = 8


# =============================================================================
# PARAGRAPH STYLES
# =============================================================================

def get_styles():
    """
    Get all paragraph styles for resume PDF.

    Returns:
        dict: Dictionary of style_name -> ParagraphStyle
    """
    styles = getSampleStyleSheet()

    # Name style (main header)
    style_name = ParagraphStyle(
        'ResumeName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=FONT_SIZE_NAME,
        textColor=COLOR_PRIMARY_BLUE,
        spaceAfter=6,
        leading=28,
        alignment=TA_LEFT,
    )

    # Professional title style
    style_professional_title = ParagraphStyle(
        'ProfessionalTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_TITLE,
        textColor=COLOR_PRIMARY_BLUE,
        spaceAfter=12,
        leading=14,
        alignment=TA_LEFT,
    )

    # Contact info style
    style_contact = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_SMALL,
        textColor=COLOR_TEXT_LIGHT,
        spaceAfter=8,
        leading=10,
        alignment=TA_LEFT,
    )

    # Section heading style (EXPERIENCE, SKILLS, etc.)
    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=FONT_SIZE_HEADING,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=8,
        spaceBefore=12,
        leading=16,
        alignment=TA_LEFT,
    )

    # Job title style
    style_job_title = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=FONT_SIZE_SUBHEADING,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=2,
        leading=14,
        alignment=TA_LEFT,
    )

    # Company name style
    style_company = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_BODY,
        textColor=COLOR_TEXT_LIGHT,
        spaceAfter=2,
        leading=12,
        alignment=TA_LEFT,
    )

    # Date range style
    style_date = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_SMALL,
        textColor=COLOR_TEXT_LIGHT,
        spaceAfter=4,
        leading=10,
        alignment=TA_LEFT,
    )

    # Body text style
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_BODY,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=6,
        leading=13,
        alignment=TA_LEFT,
    )

    # Bullet list item style
    style_bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_BODY,
        textColor=COLOR_TEXT_DARK,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=4,
        leading=13,
        alignment=TA_LEFT,
    )

    # Achievement title style
    style_achievement = ParagraphStyle(
        'Achievement',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=FONT_SIZE_BODY,
        textColor=COLOR_ACCENT,
        spaceAfter=2,
        leading=12,
        alignment=TA_LEFT,
    )

    # Achievement description style
    style_achievement_desc = ParagraphStyle(
        'AchievementDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_SMALL,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=8,
        leading=10,
        alignment=TA_LEFT,
    )

    # Certification/Skill item style
    style_list_item = ParagraphStyle(
        'ListItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=FONT_SIZE_BODY,
        textColor=COLOR_TEXT_DARK,
        spaceAfter=4,
        leading=12,
        alignment=TA_LEFT,
    )

    return {
        'name': style_name,
        'professional_title': style_professional_title,
        'contact': style_contact,
        'section_heading': style_section_heading,
        'job_title': style_job_title,
        'company': style_company,
        'date': style_date,
        'body': style_body,
        'bullet': style_bullet,
        'achievement': style_achievement,
        'achievement_desc': style_achievement_desc,
        'list_item': style_list_item,
    }


# =============================================================================
# HTML TO REPORTLAB CONVERSION
# =============================================================================

class HTMLToParagraphs(HTMLParser):
    """
    Convert simple HTML to ReportLab Paragraph flowables.

    Supports: <p>, <ul>, <li>, <strong>, <b>, <em>, <i>, <br>
    """

    def __init__(self, style_body, style_bullet):
        super().__init__()
        self.style_body = style_body
        self.style_bullet = style_bullet
        self.flowables = []
        self.current_text = ""
        self.in_list = False
        self.in_list_item = False
        self.in_paragraph = False

    def handle_starttag(self, tag, attrs):
        if tag == 'ul' or tag == 'ol':
            self.in_list = True
            # Flush any pending paragraph text
            if self.current_text.strip():
                from reportlab.platypus import Paragraph
                self.flowables.append(Paragraph(self.current_text.strip(), self.style_body))
                self.current_text = ""
        elif tag == 'li':
            self.in_list_item = True
        elif tag == 'p':
            self.in_paragraph = True
        elif tag == 'br':
            self.current_text += '<br/>'
        elif tag in ['strong', 'b']:
            self.current_text += '<b>'
        elif tag in ['em', 'i']:
            self.current_text += '<i>'

    def handle_endtag(self, tag):
        if tag == 'ul' or tag == 'ol':
            self.in_list = False
        elif tag == 'li':
            if self.current_text.strip():
                from reportlab.platypus import Paragraph
                # Create bullet paragraph
                text = f"• {self.current_text.strip()}"
                self.flowables.append(Paragraph(text, self.style_bullet))
                self.current_text = ""
            self.in_list_item = False
        elif tag == 'p':
            if self.current_text.strip():
                from reportlab.platypus import Paragraph
                self.flowables.append(Paragraph(self.current_text.strip(), self.style_body))
                self.current_text = ""
            self.in_paragraph = False
        elif tag in ['strong', 'b']:
            self.current_text += '</b>'
        elif tag in ['em', 'i']:
            self.current_text += '</i>'

    def handle_data(self, data):
        self.current_text += unescape(data)

    def get_flowables(self):
        # Flush any remaining text
        if self.current_text.strip():
            from reportlab.platypus import Paragraph
            self.flowables.append(Paragraph(self.current_text.strip(), self.style_body))
        return self.flowables


def html_to_flowables(html_content, style_body, style_bullet):
    """
    Convert HTML content to list of ReportLab flowables.

    Args:
        html_content (str): HTML string
        style_body (ParagraphStyle): Style for body paragraphs
        style_bullet (ParagraphStyle): Style for bullet points

    Returns:
        list: List of Paragraph flowables
    """
    if not html_content:
        return []

    parser = HTMLToParagraphs(style_body, style_bullet)
    parser.feed(html_content)
    return parser.get_flowables()


def strip_html_tags(html_content):
    """
    Strip all HTML tags from content, leaving plain text.

    Args:
        html_content (str): HTML string

    Returns:
        str: Plain text
    """
    from html import unescape
    import re

    if not html_content:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_content)
    # Unescape HTML entities
    text = unescape(text)
    # Normalize whitespace
    text = ' '.join(text.split())

    return text
