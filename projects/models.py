from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    """
    Represents a technology or tag associated with a project.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """
    Represents a portfolio project.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(help_text="Short description displayed on cards.")
    image = models.ImageField(upload_to="projects/", help_text="Project screenshot or mockup.")
    external_link = models.URLField(blank=True, help_text="Link to the live project or repo.")
    case_study_link = models.URLField(blank=True, help_text="Link to a detailed case study.")
    
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage.")
    order = models.IntegerField(default=0, help_text="Order of display (lower numbers first).")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)