"""
Views for the blog app.

URL Structure:
- /blog/<slug>/ - Individual post detail page
- Reserved paths: 'category', 'tag', 'archive', 'author' for future features
"""

from django.shortcuts import render, get_object_or_404
from .models import Post


def post_detail(request, slug):
    """
    Post detail view.

    URL: /blog/<slug>/

    Displays a single blog post by slug.
    Only published posts are accessible.
    """
    post = get_object_or_404(Post, slug=slug, status='published')

    # Get next and previous posts
    next_post = post.get_next_post()
    previous_post = post.get_previous_post()

    context = {
        'post': post,
        'next_post': next_post,
        'previous_post': previous_post,
    }

    return render(request, 'blog/post_detail.html', context)
