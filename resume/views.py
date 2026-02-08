"""
Views for resume app.
"""

from django.shortcuts import render, get_object_or_404
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
        response["X-Robots-Tag"] = "noindex, nofollow"

        buffer.close()

        logger.info(f"PDF resume generated successfully for profile: {profile.full_name}")
        return response

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise Http404("Failed to generate PDF resume. Please try again later.")


def resume_page(request):
    """
    Resume page view.

    GET /resume/

    Displays:
        - Active profile information
        - Work experiences
        - Skills grouped by category
        - Certifications
        - Key achievements

    Returns:
        HttpResponse: Rendered resume page

    Raises:
        Http404: If no active profile found
    """
    # Get active profile or 404
    profile = get_object_or_404(Profile, is_active=True)

    # Get related data
    experiences = profile.experiences.all()
    skills = profile.skills.all()
    certifications = profile.certifications.all()
    achievements = profile.achievements.all()

    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category = skill.category or 'Other'
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    context = {
        'profile': profile,
        'experiences': experiences,
        'skills': skills,
        'skills_by_category': skills_by_category,
        'certifications': certifications,
        'achievements': achievements,
    }

    return render(request, 'resume/resume.html', context)
