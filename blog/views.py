"""
Views for the blog app.

URL Structure:
- /blog/ - All posts list page
- /blog/<slug>/ - Individual post detail page
- Reserved paths: 'category', 'tag', 'archive', 'author' for future features
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post


def post_list(request):
    """
    Blog post list view.

    URL: /blog/

    Displays all published posts ordered by published date.
    """
    posts_qs = (
        Post.objects.filter(status="published")
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
    paginator = Paginator(posts_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    if page_obj.number == 1:
        canonical_url = request.build_absolute_uri(request.path)
    else:
        canonical_url = request.build_absolute_uri(f"{request.path}?page={page_obj.number}")

    prev_page_url = None
    next_page_url = None
    if page_obj.has_previous():
        prev_page = page_obj.previous_page_number()
        prev_relative_url = (
            request.path if prev_page == 1 else f"{request.path}?page={prev_page}"
        )
        prev_page_url = request.build_absolute_uri(prev_relative_url)
    if page_obj.has_next():
        next_relative_url = f"{request.path}?page={page_obj.next_page_number()}"
        next_page_url = request.build_absolute_uri(next_relative_url)

    context = {
        "posts": page_obj.object_list,
        "page_obj": page_obj,
        "canonical_url": canonical_url,
        "prev_page_url": prev_page_url,
        "next_page_url": next_page_url,
    }

    return render(request, "blog/post_list.html", context)


def post_detail(request, slug):
    """
    Post detail view.

    URL: /blog/<slug>/

    Displays a single blog post by slug.
    Only published posts are accessible.
    """
    post = get_object_or_404(
        Post.objects.select_related("author", "category").prefetch_related("tags"),
        slug=slug,
        status="published",
    )

    # Get next and previous posts
    next_post = post.get_next_post()
    previous_post = post.get_previous_post()

    context = {
        "post": post,
        "next_post": next_post,
        "previous_post": previous_post,
        "canonical_url": request.build_absolute_uri(post.get_absolute_url()),
    }

    return render(request, "blog/post_detail.html", context)
