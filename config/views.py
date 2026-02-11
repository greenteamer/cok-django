"""
Views for the main config app.
"""

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.db import connection

from django.shortcuts import render
from blog.models import Post
from resume.models import Profile
from projects.models import Project


def home(request):
    """
    Home page view.

    Displays:
    - Active profile with skills and experiences
    - Recent blog posts
    """
    # Get active profile
    profile = Profile.objects.filter(is_active=True).first()

    projects = Project.objects.filter(is_featured=True).prefetch_related("tags")

    recent_posts = (
        Post.objects.filter(status="published")
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")[:3]
    )

    # Get experiences if profile exists
    experiences = []
    skills = []
    if profile:
        experiences = profile.experiences.all()
        skills = profile.skills.all()

    context = {
        "profile": profile,
        "projects": projects,
        "experiences": experiences,
        "skills": skills,
        "recent_posts": recent_posts,
    }

    return render(request, "home.html", context)


def health_check(request):
    """
    Health check endpoint for Railway and monitoring.

    Returns 200 with DB status. Does not require authentication.
    Used by Railway to verify the service is running.
    """
    status = {"status": "ok", "database": "ok"}
    http_status = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        status["database"] = f"error: {type(e).__name__}"
        http_status = 503

    return JsonResponse(status, status=http_status)


def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, "404.html", status=404)


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /ckeditor/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(content), content_type="text/plain")
