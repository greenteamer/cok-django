from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from projects.models import Project


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ["home", "post_list", "resume", "project_list"]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status="published").order_by("-published_at")

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at
