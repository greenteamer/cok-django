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
    live_url = models.URLField(
        blank=True, help_text="The running product: App Store page, website or demo. Shown as “Live ↗”."
    )
    source_url = models.URLField(blank=True, help_text="Source code repository. Shown as “Source ↗”.")
    case_study_url = models.URLField(
        blank=True, help_text="A write-up about the project (article or blog post). Shown as “Case study ↗”."
    )
    
    role = models.CharField(
        max_length=200,
        blank=True,
        help_text="My role on the project, e.g. “Lead React Native Developer (via TSS Paratransit)”. "
        "Shown in the “My role / Impact / Stack” block on the project page.",
    )
    impact = models.TextField(
        blank=True,
        help_text="What I did and what changed, one bullet per line. Shown under “Impact” on the project page.",
    )

    tags = models.ManyToManyField(
        Tag, related_name="projects", blank=True, help_text="Technologies. Shown on cards and as “Stack”."
    )
    
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

    def get_absolute_url(self):
        return f"/projects/{self.slug}/"

    @property
    def impact_items(self):
        """`impact` split into non-empty lines (leading “- ” / “• ” stripped)."""
        lines = (line.strip().lstrip("-•").strip() for line in self.impact.splitlines())
        return [line for line in lines if line]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
