"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from .sitemaps import BlogPostSitemap, ProjectSitemap, StaticViewSitemap
from .views import home, robots_txt, custom_404
from blog.views import post_list, post_detail
from resume.views import export_resume_pdf, resume_page
from projects.views import project_detail, project_list

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogPostSitemap,
    "projects": ProjectSitemap,
}

urlpatterns = [
    path("", home, name="home"),
    path("resume/", resume_page, name="resume"),
    path("resume/export/pdf/", export_resume_pdf, name="export_resume_pdf"),
    path("projects/", project_list, name="project_list"),
    path("projects/<slug:slug>/", project_detail, name="project_detail"),
    path("blog/", post_list, name="post_list"),
    path("blog/<slug:slug>/", post_detail, name="post_detail"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("robots", RedirectView.as_view(pattern_name="robots_txt", permanent=True)),
    path("robots/", RedirectView.as_view(pattern_name="robots_txt", permanent=True)),
    path("robots.txt/", RedirectView.as_view(pattern_name="robots_txt", permanent=True)),
    path(
        "sitemap",
        RedirectView.as_view(pattern_name="sitemap", permanent=True),
        name="sitemap_compat",
    ),
    path("sitemap/", RedirectView.as_view(pattern_name="sitemap", permanent=True)),
    path("sitemap.xml/", RedirectView.as_view(pattern_name="sitemap", permanent=True)),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

handler404 = custom_404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
