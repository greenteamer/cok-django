"""
Views for the main config app.
"""

from django.shortcuts import render
from blog.models import Post
from resume.models import Profile, Experience, Skill


def home(request):
    """
    Home page view.

    Displays:
    - Active profile with skills and experiences
    - Recent blog posts
    """
    # Get active profile
    profile = Profile.objects.filter(is_active=True).first()

    # Get recent blog posts (published ones)
    recent_posts = Post.objects.filter(status='published').order_by('-published_at')[:3]

    # Get experiences if profile exists
    experiences = []
    skills = []
    if profile:
        experiences = profile.experiences.all()[:2]
        skills = profile.skills.all()[:6]

    context = {
        'profile': profile,
        'experiences': experiences,
        'skills': skills,
        'recent_posts': recent_posts,
    }

    return render(request, 'home.html', context)
