"""
Views for the main config app.
"""

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

    projects = Project.objects.filter(is_featured=True).all()

    recent_posts = Post.objects.filter(status="published").order_by("-published_at")[:3]

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
