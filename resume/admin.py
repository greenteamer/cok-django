from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.inlines.admin import StackedInline, TabularInline

from .models import Profile, Experience, Skill, Certification, Achievement


class ExperienceInline(StackedInline):
    """Inline display of work experiences on Profile admin page."""

    model = Experience
    extra = 0
    fields = [
        ('position', 'company'),
        ('start_date', 'end_date'),
        'location',
        'description',
        'company_description',
        'order'
    ]
    ordering = ['order', '-start_date']


class SkillInline(TabularInline):
    """Inline display of skills on Profile admin page."""

    model = Skill
    extra = 0
    fields = ['name', 'category', 'order']
    ordering = ['order', 'category', 'name']


class CertificationInline(TabularInline):
    """Inline display of certifications on Profile admin page."""

    model = Certification
    extra = 0
    fields = ['name', 'provider', 'date_obtained', 'credential_url', 'order']
    ordering = ['order', '-date_obtained']


class AchievementInline(StackedInline):
    """Inline display of achievements on Profile admin page."""

    model = Achievement
    extra = 0
    fields = ['title', 'description', 'icon', 'order']
    ordering = ['order', 'title']


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    """Admin interface for resume profile using Unfold."""

    list_display = [
        'full_name',
        'title',
        'email',
        'location',
        'is_active',
        'updated_at'
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['full_name', 'title', 'email', 'summary']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'title', 'email', 'linkedin_url', 'location')
        }),
        ('Professional Summary', {
            'fields': ('summary',)
        }),
        ('Profile Photo', {
            'fields': ('photo',),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    inlines = [ExperienceInline, SkillInline, CertificationInline, AchievementInline]

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        """Bulk action to activate profile (only one will remain active)."""
        if queryset.count() > 1:
            self.message_user(
                request,
                'Only one profile can be active. Please select a single profile.',
                level='error'
            )
            return

        profile = queryset.first()
        profile.is_active = True
        profile.save()
        self.message_user(request, f'{profile.full_name} is now active.')
    make_active.short_description = 'Activate selected profile'

    def make_inactive(self, request, queryset):
        """Bulk action to deactivate profiles."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} profile(s) deactivated.')
    make_inactive.short_description = 'Deactivate selected profiles'


@admin.register(Experience)
class ExperienceAdmin(ModelAdmin):
    """Admin interface for work experience using Unfold."""

    list_display = [
        'position',
        'company',
        'location',
        'start_date',
        'end_date',
        'is_current',
        'profile',
        'order'
    ]
    list_filter = ['profile', 'start_date', 'end_date']
    search_fields = ['position', 'company', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'duration_display']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Position Information', {
            'fields': ('profile', 'position', 'company', 'location')
        }),
        ('Employment Period', {
            'fields': ('start_date', 'end_date', 'duration_display')
        }),
        ('Description', {
            'fields': ('description', 'company_description')
        }),
        ('Display', {
            'fields': ('order',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def duration_display(self, obj):
        """Display formatted duration."""
        return obj.duration
    duration_display.short_description = 'Duration'

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('profile')


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    """Admin interface for skills using Unfold."""

    list_display = ['name', 'category', 'profile', 'order']
    list_filter = ['profile', 'category']
    search_fields = ['name', 'category']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Skill Information', {
            'fields': ('profile', 'name', 'category')
        }),
        ('Display', {
            'fields': ('order',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('profile')


@admin.register(Certification)
class CertificationAdmin(ModelAdmin):
    """Admin interface for certifications using Unfold."""

    list_display = [
        'name',
        'provider',
        'date_obtained',
        'profile',
        'order'
    ]
    list_filter = ['profile', 'provider', 'date_obtained']
    search_fields = ['name', 'provider']
    readonly_fields = ['created_at']
    date_hierarchy = 'date_obtained'

    fieldsets = (
        ('Certification Information', {
            'fields': ('profile', 'name', 'provider', 'date_obtained', 'credential_url')
        }),
        ('Display', {
            'fields': ('order',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('profile')


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    """Admin interface for achievements using Unfold."""

    list_display = ['title', 'icon', 'profile', 'order']
    list_filter = ['profile', 'icon']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Achievement Information', {
            'fields': ('profile', 'title', 'description', 'icon')
        }),
        ('Display', {
            'fields': ('order',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('profile')
