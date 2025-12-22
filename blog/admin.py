from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.inlines.admin import TabularInline

from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin interface for blog categories using Unfold."""

    list_display = ['name', 'slug', 'post_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def post_count(self, obj):
        """Display number of posts in category."""
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    """Admin interface for blog tags using Unfold."""

    list_display = ['name', 'slug', 'post_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'slug')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


class CommentInline(TabularInline):
    """Inline display of comments on Post admin page."""

    model = Comment
    extra = 0
    fields = ['author_name_display', 'content_preview', 'is_approved', 'created_at']
    readonly_fields = ['author_name_display', 'content_preview', 'created_at']
    can_delete = True

    def content_preview(self, obj):
        """Show first 100 characters of comment."""
        if obj.content:
            return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return "-"
    content_preview.short_description = 'Comment'

    def author_name_display(self, obj):
        """Display commenter name."""
        return obj.get_author_name()
    author_name_display.short_description = 'Author'


@admin.register(Post)
class PostAdmin(ModelAdmin):
    """Admin interface for blog posts using Unfold."""

    list_display = [
        'title',
        'author',
        'category',
        'status',
        'published_at',
        'comment_count_display',
        'created_at'
    ]
    list_filter = [
        'status',
        'category',
        'created_at',
        'published_at',
        'author'
    ]
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']

    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Publishing', {
            'fields': ('status', 'author', 'published_at')
        }),
        ('Organization', {
            'fields': ('category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image',),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    inlines = [CommentInline]

    actions = ['make_published', 'make_draft']

    def comment_count_display(self, obj):
        """Display comment count."""
        return obj.comment_count
    comment_count_display.short_description = 'Comments'

    def make_published(self, request, queryset):
        """Bulk action to publish posts."""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} post(s) marked as published.')
    make_published.short_description = 'Publish selected posts'

    def make_draft(self, request, queryset):
        """Bulk action to unpublish posts."""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} post(s) marked as draft.')
    make_draft.short_description = 'Mark selected posts as draft'

    def get_queryset(self, request):
        """Optimize queries with select_related and prefetch_related."""
        qs = super().get_queryset(request)
        return qs.select_related('category', 'author').prefetch_related('tags')


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """Admin interface for blog comments using Unfold."""

    list_display = [
        'author_display',
        'post',
        'content_preview',
        'is_approved',
        'created_at'
    ]
    list_filter = [
        'is_approved',
        'created_at',
        'post'
    ]
    search_fields = [
        'author_name',
        'author_email',
        'content',
        'post__title'
    ]
    readonly_fields = [
        'post',
        'user',
        'author_name',
        'author_email',
        'author_url',
        'content',
        'ip_address',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'content')
        }),
        ('Author Information', {
            'fields': ('user', 'author_name', 'author_email', 'author_url', 'ip_address')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['approve_comments', 'unapprove_comments']

    def author_display(self, obj):
        """Display author name."""
        return obj.get_author_name()
    author_display.short_description = 'Author'

    def content_preview(self, obj):
        """Show first 100 characters of comment."""
        if obj.content:
            return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return "-"
    content_preview.short_description = 'Comment'

    def approve_comments(self, request, queryset):
        """Bulk approve comments."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comment(s) approved.')
    approve_comments.short_description = 'Approve selected comments'

    def unapprove_comments(self, request, queryset):
        """Bulk unapprove comments."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comment(s) unapproved.')
    unapprove_comments.short_description = 'Unapprove selected comments'

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('post', 'user')
