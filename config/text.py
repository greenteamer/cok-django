"""Plain-text normalization for user-entered summary fields.

Fields such as ``Post.excerpt`` and ``Post.meta_description`` are rendered
with Django autoescaping (cards, ``<meta>`` tags, JSON-LD). They MUST hold
plain text: any HTML tags, Markdown syntax or HTML entities stored there would
be shown to readers verbatim (e.g. ``<a href="...">`` or ``&mdash;``).
"""

import html

from django.utils.html import strip_tags
from markdown import markdown as render_markdown


def html_to_text(value):
    """Strip tags, decode entities and collapse whitespace into one line."""
    text = html.unescape(strip_tags(value or ""))
    return " ".join(text.split())


def markup_to_text(value):
    """Convert a Markdown/HTML fragment (or plain text) to one-line plain text."""
    if not value:
        return ""
    return html_to_text(render_markdown(value, extensions=["extra", "sane_lists"]))


def truncate_text(value, max_length):
    """Truncate to ``max_length`` characters, ending with "..." when cut."""
    if len(value) <= max_length:
        return value
    return f"{value[:max_length - 3]}..."
