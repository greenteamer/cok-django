"""
ReportLab PDF Styles

Paragraph styles and HTML/text helpers for the ATS-friendly resume PDF
(see resume/pdf_generator.py and docs/modules/resume-pdf-export.md).

ATS constraints that shape these styles:
- one column, standard PDF fonts (Helvetica), black/dark-gray text only
- no icons, tables or images; plain bullets ("•")
- text must survive copy/paste, so everything goes through `pdf_text()`
"""

from html import escape
from html.parser import HTMLParser

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph


COLOR_TEXT = HexColor('#111111')
COLOR_MUTED = HexColor('#444444')

FONT = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_ITALIC = 'Helvetica-Oblique'


# =============================================================================
# TEXT SANITIZING
# =============================================================================

# Characters outside the standard PDF fonts' WinAnsi encoding render as
# blank boxes; map the ones the resume content uses, drop the rest (emoji).
_REPLACEMENTS = {
    '→': '->',
    '←': '<-',
    '↗': '',
    '◆': '',
    '✓': '',
    ' ': ' ',
}


def pdf_text(text):
    """Return `text` restricted to characters Helvetica can render."""
    if not text:
        return ''
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode('cp1252', errors='ignore').decode('cp1252')


def pdf_markup(text):
    """Sanitize plain text and escape it for ReportLab paragraph markup."""
    return escape(pdf_text(text), quote=False)


# =============================================================================
# PARAGRAPH STYLES
# =============================================================================

def get_styles():
    """
    Get all paragraph styles for the resume PDF.

    Returns:
        dict: style_name -> ParagraphStyle
    """
    def style(name, **kwargs):
        defaults = dict(fontName=FONT, fontSize=10, leading=13.5, textColor=COLOR_TEXT, alignment=TA_LEFT)
        defaults.update(kwargs)
        return ParagraphStyle(name, **defaults)

    return {
        'name': style('ResumeName', fontName=FONT_BOLD, fontSize=20, leading=24, spaceAfter=2),
        'headline': style('Headline', fontSize=11.5, leading=15, spaceAfter=4),
        'contact': style('Contact', fontSize=9, leading=12, textColor=COLOR_MUTED, spaceAfter=2),
        'section_heading': style(
            'SectionHeading', fontName=FONT_BOLD, fontSize=11.5, leading=14, spaceBefore=12, spaceAfter=3
        ),
        'job_title': style('JobTitle', fontName=FONT_BOLD, fontSize=10.5, leading=13.5, spaceBefore=6),
        'job_meta': style('JobMeta', fontSize=9, leading=12, textColor=COLOR_MUTED, spaceAfter=2),
        'company_note': style('CompanyNote', fontName=FONT_ITALIC, fontSize=9, leading=12, textColor=COLOR_MUTED, spaceAfter=2),
        'body': style('Body', spaceAfter=4),
        'bullet': style('Bullet', leftIndent=12, bulletIndent=2, spaceAfter=2.5),
        'skills_line': style('SkillsLine', spaceAfter=2.5),
    }


# =============================================================================
# HTML TO REPORTLAB CONVERSION
# =============================================================================

class HTMLToParagraphs(HTMLParser):
    """
    Convert CKEditor HTML to ReportLab Paragraph flowables.

    Supports: <p>, <ul>/<ol>, <li>, <strong>/<b>, <em>/<i>, <br>.
    With `paragraphs_as_bullets=True`, every <p> becomes a bullet too
    (experience descriptions are written as one paragraph per achievement).
    """

    def __init__(self, style_body, style_bullet, paragraphs_as_bullets=False):
        super().__init__(convert_charrefs=True)
        self.style_body = style_body
        self.style_bullet = style_bullet
        self.paragraphs_as_bullets = paragraphs_as_bullets
        self.flowables = []
        self.current_text = ""

    def _flush(self, bullet):
        text = " ".join(self.current_text.split())
        if text and text not in ('<b></b>', '<i></i>'):
            if bullet:
                self.flowables.append(Paragraph(text, self.style_bullet, bulletText='•'))
            else:
                self.flowables.append(Paragraph(text, self.style_body))
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag in ('ul', 'ol', 'p', 'li'):
            self._flush(bullet=self.paragraphs_as_bullets)
        elif tag == 'br':
            self._flush(bullet=self.paragraphs_as_bullets)
        elif tag in ('strong', 'b'):
            self.current_text += '<b>'
        elif tag in ('em', 'i'):
            self.current_text += '<i>'

    def handle_endtag(self, tag):
        if tag == 'li':
            self._flush(bullet=True)
        elif tag == 'p':
            self._flush(bullet=self.paragraphs_as_bullets)
        elif tag in ('strong', 'b'):
            self.current_text += '</b>'
        elif tag in ('em', 'i'):
            self.current_text += '</i>'

    def handle_data(self, data):
        self.current_text += pdf_markup(data)

    def get_flowables(self):
        self._flush(bullet=self.paragraphs_as_bullets)
        return self.flowables


def html_to_flowables(html_content, style_body, style_bullet, paragraphs_as_bullets=False):
    """
    Convert HTML content to a list of ReportLab flowables.

    Args:
        html_content (str): HTML string
        style_body (ParagraphStyle): Style for body paragraphs
        style_bullet (ParagraphStyle): Style for bullet points
        paragraphs_as_bullets (bool): Render <p> blocks as bullets

    Returns:
        list: Paragraph flowables
    """
    if not html_content:
        return []

    parser = HTMLToParagraphs(style_body, style_bullet, paragraphs_as_bullets)
    parser.feed(html_content)
    return parser.get_flowables()
