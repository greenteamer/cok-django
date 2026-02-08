from django.shortcuts import get_object_or_404, render

from .models import Project


def project_list(request):
    projects = Project.objects.prefetch_related("tags").order_by("order", "-created_at")
    context = {"projects": projects}
    return render(request, "projects/project_list.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project.objects.prefetch_related("tags"), slug=slug)
    context = {"project": project}
    return render(request, "projects/project_detail.html", context)
