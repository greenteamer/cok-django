from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Profile(models.Model):
    """Personal profile information for resume."""

    full_name = models.CharField(
        max_length=200,
        verbose_name="Full Name",
        help_text="Full name (max 200 characters)"
    )

    title = models.CharField(
        max_length=300,
        verbose_name="Professional Title",
        help_text="Professional title/headline (max 300 characters)"
    )

    email = models.EmailField(
        verbose_name="Email Address",
        help_text="Contact email address"
    )

    linkedin_url = models.URLField(
        blank=True,
        verbose_name="LinkedIn URL",
        help_text="LinkedIn profile URL (optional)"
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Location",
        help_text="Current location (city, country)"
    )

    summary = RichTextUploadingField(
        verbose_name="Professional Summary",
        help_text="Professional summary and key highlights"
    )

    photo = models.ImageField(
        upload_to='resume/photos/',
        blank=True,
        null=True,
        verbose_name="Profile Photo",
        help_text="Profile photo (optional, uploaded to media/resume/photos/)"
    )

    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Set active profile (only one profile should be active)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ['-is_active', '-updated_at']
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.title}"

    def save(self, *args, **kwargs):
        # Ensure only one profile is active
        if self.is_active:
            Profile.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Experience(models.Model):
    """Work experience entry for resume."""

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='experiences',
        verbose_name="Profile"
    )

    position = models.CharField(
        max_length=200,
        verbose_name="Position Title",
        help_text="Job position/role title (max 200 characters)"
    )

    company = models.CharField(
        max_length=200,
        verbose_name="Company Name",
        help_text="Company/organization name (max 200 characters)"
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Location",
        help_text="Job location (city, country)"
    )

    start_date = models.DateField(
        verbose_name="Start Date",
        help_text="Employment start date"
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
        help_text="Employment end date (leave empty for current position)"
    )

    description = RichTextUploadingField(
        verbose_name="Description",
        help_text="Job responsibilities and achievements"
    )

    company_description = models.TextField(
        blank=True,
        verbose_name="Company Description",
        help_text="Brief company description (optional)"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order for display (lower numbers first)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ['order', '-start_date']
        indexes = [
            models.Index(fields=['profile', 'order']),
            models.Index(fields=['profile', '-start_date']),
        ]

    def __str__(self):
        return f"{self.position} at {self.company}"

    @property
    def is_current(self):
        """Check if this is a current position."""
        return self.end_date is None

    @property
    def duration(self):
        """Get formatted duration string."""
        from datetime import date
        end = self.end_date or date.today()
        years = (end.year - self.start_date.year)
        months = (end.month - self.start_date.month)

        if months < 0:
            years -= 1
            months += 12

        parts = []
        if years > 0:
            parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months > 0:
            parts.append(f"{months} month{'s' if months > 1 else ''}")

        return " ".join(parts) if parts else "Less than a month"


class Skill(models.Model):
    """Technical or professional skill."""

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name="Profile"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Skill Name",
        help_text="Skill or technology name (max 100 characters)"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Category",
        help_text="Skill category for grouping (optional)"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order for display (lower numbers first)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['order', 'category', 'name']
        indexes = [
            models.Index(fields=['profile', 'order']),
            models.Index(fields=['profile', 'category']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'name'],
                name='unique_skill_per_profile'
            )
        ]

    def __str__(self):
        if self.category:
            return f"{self.name} ({self.category})"
        return self.name


class Certification(models.Model):
    """Professional certification or course completion."""

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='certifications',
        verbose_name="Profile"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Certification Name",
        help_text="Certification or course name (max 200 characters)"
    )

    provider = models.CharField(
        max_length=200,
        verbose_name="Provider/Organization",
        help_text="Issuing organization or platform (max 200 characters)"
    )

    date_obtained = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date Obtained",
        help_text="Date when certification was obtained (optional)"
    )

    credential_url = models.URLField(
        blank=True,
        verbose_name="Credential URL",
        help_text="URL to verify credential (optional)"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order for display (lower numbers first)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['order', '-date_obtained']
        indexes = [
            models.Index(fields=['profile', 'order']),
        ]

    def __str__(self):
        return f"{self.name} - {self.provider}"


class Achievement(models.Model):
    """Key achievement or accomplishment."""

    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name="Profile"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Achievement Title",
        help_text="Brief achievement title (max 200 characters)"
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed achievement description"
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icon Name",
        help_text="Icon name for visual display (optional, e.g., 'trophy', 'star')"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order for display (lower numbers first)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['profile', 'order']),
        ]

    def __str__(self):
        return self.title
