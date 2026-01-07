from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Project, Tag


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ["title", "is_featured", "order", "created_at"]
    list_filter = ["is_featured", "tags"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags"]
    list_editable = ["is_featured", "order"]