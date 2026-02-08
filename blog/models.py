from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from markdown import markdown as render_markdown
import bleach

from .image_variants import get_cropped_image_variant


ALLOWED_HTML_TAGS = [
    "p", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "b", "i", "u", "s", "mark",
    "ul", "ol", "li", "blockquote",
    "pre", "code",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
]

ALLOWED_HTML_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height", "loading", "decoding"],
}

ALLOWED_HTML_PROTOCOLS = ["http", "https", "mailto"]

FEATURED_IMAGE_CARD_SIZE = (800, 450)
FEATURED_IMAGE_HERO_SIZE = (1600, 900)
FEATURED_IMAGE_FOCUS_VALIDATORS = [MinValueValidator(0), MaxValueValidator(100)]


class Category(models.Model):
    """Blog post category for organizing content."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Category Name",
        help_text="Unique category name (max 100 characters)"
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL Slug",
        help_text="URL-friendly version of name (auto-generated if empty)"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Optional category description"
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
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Blog post tag for flexible classification."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Tag Name",
        help_text="Unique tag name (max 50 characters)"
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL Slug",
        help_text="URL-friendly version of name"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/tag/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def post_count(self):
        """Return number of published posts with this tag."""
        return self.posts.filter(status='published').count()


class Post(models.Model):
    """Main blog post model."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Core content fields
    title = models.CharField(
        max_length=200,
        verbose_name="Post Title",
        help_text="Post title (max 200 characters)"
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL Slug",
        help_text="URL-friendly version of title (must be unique)"
    )

    content_markdown = models.TextField(
        blank=True,
        verbose_name="Post Content (Markdown)",
        help_text="Primary authoring field. Markdown will be converted to sanitized HTML automatically."
    )

    content = models.TextField(
        blank=True,
        verbose_name="Post Content",
        help_text="Rendered/sanitized HTML for frontend output. Filled automatically from Markdown when provided."
    )

    excerpt = models.TextField(
        blank=True,
        max_length=500,
        verbose_name="Excerpt",
        help_text="Short summary (max 500 characters, auto-generated if empty)"
    )

    # Publishing workflow
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Status",
        help_text="Post publication status"
    )

    # Author (using Django's built-in User model)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='blog_posts',
        verbose_name="Author"
    )

    # Taxonomy
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="Category"
    )

    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='posts',
        verbose_name="Tags"
    )

    # Media
    featured_image = models.ImageField(
        upload_to='blog/featured/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Featured Image",
        help_text="Optional featured image (uploaded to media/blog/featured/YYYY/MM/)"
    )
    featured_image_focus_x = models.PositiveSmallIntegerField(
        default=50,
        validators=FEATURED_IMAGE_FOCUS_VALIDATORS,
        verbose_name="Image Focus X (%)",
        help_text="Horizontal crop focus from left (0) to right (100)."
    )
    featured_image_focus_y = models.PositiveSmallIntegerField(
        default=50,
        validators=FEATURED_IMAGE_FOCUS_VALIDATORS,
        verbose_name="Image Focus Y (%)",
        help_text="Vertical crop focus from top (0) to bottom (100)."
    )

    # SEO fields
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Description",
        help_text="SEO meta description (max 160 characters, auto-generated if empty)"
    )

    meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Meta Title",
        help_text="SEO title (recommended up to 60 characters, auto-generated from title if empty)"
    )

    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta Keywords",
        help_text="SEO keywords, comma-separated (max 255 characters)"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Published At",
        help_text="Date/time when post was published (auto-set on first publish)"
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['-published_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=['draft', 'published']),
                name='valid_post_status'
            )
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        markdown_content = (self.content_markdown or "").strip()
        if markdown_content:
            rendered_html = render_markdown(
                markdown_content,
                extensions=["extra", "sane_lists", "nl2br"],
            )
            self.content = bleach.clean(
                rendered_html,
                tags=ALLOWED_HTML_TAGS,
                attributes=ALLOWED_HTML_ATTRIBUTES,
                protocols=ALLOWED_HTML_PROTOCOLS,
                strip=True,
            )

        plain_text_content = " ".join(strip_tags(self.content or "").split())

        # Auto-generate excerpt if not provided
        if not self.excerpt and plain_text_content:
            self.excerpt = (
                f"{plain_text_content[:497]}..."
                if len(plain_text_content) > 500
                else plain_text_content
            )

        # Auto-generate meta_description if not provided
        if not self.meta_description and self.excerpt:
            clean_excerpt = " ".join(strip_tags(self.excerpt).split())
            self.meta_description = (
                f"{clean_excerpt[:157]}..."
                if len(clean_excerpt) > 160
                else clean_excerpt
            )

        if not self.meta_title:
            self.meta_title = (
                f"{self.title[:57]}..."
                if len(self.title) > 60
                else self.title
            )

        # Set published_at timestamp when first published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if post is published."""
        return self.status == 'published'

    @property
    def comment_count(self):
        """Return number of approved comments."""
        return self.comments.filter(is_approved=True).count()

    def get_next_post(self):
        """Get next published post by published_at date."""
        return Post.objects.filter(
            status='published',
            published_at__gt=self.published_at
        ).order_by('published_at').first()

    def get_previous_post(self):
        """Get previous published post by published_at date."""
        return Post.objects.filter(
            status='published',
            published_at__lt=self.published_at
        ).order_by('-published_at').first()

    @cached_property
    def featured_image_card_url(self):
        """Return cropped featured image URL for blog card previews."""
        if not self.featured_image:
            return ""
        crop_centering = self._featured_image_crop_centering()
        return get_cropped_image_variant(
            self.featured_image,
            variant_name="card",
            size=FEATURED_IMAGE_CARD_SIZE,
            centering=crop_centering,
            version_token=self._featured_image_focus_token(),
        )

    @cached_property
    def featured_image_hero_url(self):
        """Return cropped featured image URL for blog post detail pages."""
        if not self.featured_image:
            return ""
        crop_centering = self._featured_image_crop_centering()
        return get_cropped_image_variant(
            self.featured_image,
            variant_name="hero",
            size=FEATURED_IMAGE_HERO_SIZE,
            centering=crop_centering,
            version_token=self._featured_image_focus_token(),
        )

    def _featured_image_crop_centering(self):
        x = max(0, min(100, self.featured_image_focus_x or 50)) / 100
        y = max(0, min(100, self.featured_image_focus_y or 50)) / 100
        return (x, y)

    def _featured_image_focus_token(self):
        x = max(0, min(100, self.featured_image_focus_x or 50))
        y = max(0, min(100, self.featured_image_focus_y or 50))
        return f"fx{x}_fy{y}"


class Comment(models.Model):
    """User comment on blog posts with moderation."""

    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Post"
    )

    # Commenter info (for non-authenticated users)
    author_name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Commenter's name"
    )

    author_email = models.EmailField(
        verbose_name="Email",
        help_text="Commenter's email (not displayed publicly)"
    )

    author_url = models.URLField(
        blank=True,
        verbose_name="Website",
        help_text="Optional website URL"
    )

    # Authenticated user (optional)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_comments',
        verbose_name="User",
        help_text="Authenticated user (if logged in)"
    )

    # Comment content
    content = models.TextField(
        verbose_name="Comment",
        help_text="Comment content"
    )

    # Moderation
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Approved",
        help_text="Approve comment for public display"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    # IP address (for spam prevention)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address",
        help_text="Commenter's IP address (for moderation)"
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved', '-created_at']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.get_author_name()} on {self.post.title}"

    def get_author_name(self):
        """Return authenticated user's name or provided name."""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.author_name

    def get_author_email(self):
        """Return authenticated user's email or provided email."""
        if self.user:
            return self.user.email
        return self.author_email

    def approve(self):
        """Approve comment."""
        self.is_approved = True
        self.save(update_fields=['is_approved', 'updated_at'])

    def unapprove(self):
        """Unapprove comment."""
        self.is_approved = False
        self.save(update_fields=['is_approved', 'updated_at'])
