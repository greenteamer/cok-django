"""
Views for resume app.
"""

from django.shortcuts import render
from django.http import HttpResponse, Http404
import logging

from .models import Profile
from .pdf_generator import generate_resume_pdf

logger = logging.getLogger(__name__)


def export_resume_pdf(request):
    """
    Export active profile as PDF resume.

    GET /resume/export/pdf/

    Returns:
        HttpResponse: PDF file attachment

    Raises:
        Http404: If no active profile or PDF generation fails
    """
    try:
        # Get active profile
        profile = Profile.objects.filter(is_active=True).first()

        if not profile:
            logger.warning("PDF export attempted with no active profile")
            raise Http404("No active resume profile found.")

        # Generate PDF
        buffer = generate_resume_pdf(profile)

        # Create HTTP response with PDF
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"{profile.full_name.replace(' ', '_')}_Resume.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        buffer.close()

        logger.info(f"PDF resume generated successfully for profile: {profile.full_name}")
        return response

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise Http404("Failed to generate PDF resume. Please try again later.")
