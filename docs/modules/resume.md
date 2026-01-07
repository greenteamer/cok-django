# Resume Module Documentation

## Overview

The `resume` Django app provides complete resume/CV management functionality including professional profile, work experience, skills, certifications, and achievements.

**Scope**: Professional resume content management with support for multiple profiles and organized data display

**Entry Point**: `resume/models.py` for data models, `resume/admin.py` for admin interface

---

## Models

### Profile

**Purpose**: Main professional profile and personal information

**Location**: `resume/models.py:5`

**Key Fields**:
- `full_name`: CharField(max_length=200) - Full name
- `title`: CharField(max_length=300) - Professional title/headline
- `email`: EmailField - Contact email address
- `linkedin_url`: URLField(blank=True) - LinkedIn profile URL (optional)
- `location`: CharField(max_length=200, blank=True) - Current location (city, country)
- `summary`: RichTextUploadingField - Professional summary and key highlights with **WYSIWYG editor** (CKEditor)
- `photo`: ImageField(upload_to='resume/photos/', blank=True, null=True) - Profile photo (optional)
- `is_active`: BooleanField(default=True) - Active profile flag (only one profile should be active)

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp
- `updated_at`: DateTimeField(auto_now=True) - Last update timestamp

**Relationships**:
- Has many: Experience, Skill, Certification, Achievement (reverse relations)

**Model Methods**:
- `save()`: Ensures only one profile is active at a time (deactivates all other profiles when this one is activated)
- `__str__()`: Returns "{full_name} - {title}"

**Business Logic**:
- **Single Active Profile**: Only one profile can be active at a time. When a profile is activated, all other profiles are automatically deactivated.

**Meta Options**:
- `ordering = ['-is_active', '-updated_at']` - Active profile first, then by most recent
- Index on `is_active` for performance

---

### Experience

**Purpose**: Work experience entries with position details

**Location**: `resume/models.py:86`

**Key Fields**:
- `profile`: ForeignKey('Profile', on_delete=CASCADE) - Associated profile
- `position`: CharField(max_length=200) - Job position/role title
- `company`: CharField(max_length=200) - Company/organization name
- `location`: CharField(max_length=200, blank=True) - Job location (city, country)
- `start_date`: DateField - Employment start date
- `end_date`: DateField(null=True, blank=True) - Employment end date (null for current positions)
- `description`: RichTextUploadingField - Job responsibilities and achievements with **WYSIWYG editor** (CKEditor)
- `company_description`: TextField(blank=True) - Brief company description (optional)
- `order`: PositiveIntegerField(default=0) - Display order (lower numbers first)

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp
- `updated_at`: DateTimeField(auto_now=True) - Last update timestamp

**Relationships**:
- Belongs to: Profile (CASCADE on delete)

**Model Methods**:
- `is_current` (property): Returns True if end_date is None (current position)
- `duration` (property): Returns formatted duration string (e.g., "2 years 5 months")
- `__str__()`: Returns "{position} at {company}"

**Duration Calculation**:
The `duration` property calculates employment duration from start_date to end_date (or current date if ongoing), returning a human-readable string like "2 years 5 months".

**Meta Options**:
- `ordering = ['order', '-start_date']` - By display order, then most recent first
- Indexes on `(profile, order)` and `(profile, -start_date)` for performance

---

### Skill

**Purpose**: Technical or professional skills

**Location**: `resume/models.py:192`

**Key Fields**:
- `profile`: ForeignKey('Profile', on_delete=CASCADE) - Associated profile
- `name`: CharField(max_length=100) - Skill or technology name
- `category`: CharField(max_length=100, blank=True) - Skill category for grouping (optional)
- `order`: PositiveIntegerField(default=0) - Display order (lower numbers first)

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp

**Relationships**:
- Belongs to: Profile (CASCADE on delete)

**Model Methods**:
- `__str__()`: Returns "{name} ({category})" if category exists, otherwise just name

**Constraints**:
- UniqueConstraint on `(profile, name)` - Prevents duplicate skills per profile

**Meta Options**:
- `ordering = ['order', 'category', 'name']` - By display order, then category, then alphabetically
- Indexes on `(profile, order)` and `(profile, category)` for performance

---

### Certification

**Purpose**: Professional certifications or course completions

**Location**: `resume/models.py:247`

**Key Fields**:
- `profile`: ForeignKey('Profile', on_delete=CASCADE) - Associated profile
- `name`: CharField(max_length=200) - Certification or course name
- `provider`: CharField(max_length=200) - Issuing organization or platform
- `date_obtained`: DateField(null=True, blank=True) - Date when certification was obtained (optional)
- `credential_url`: URLField(blank=True) - URL to verify credential (optional)
- `order`: PositiveIntegerField(default=0) - Display order (lower numbers first)

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp

**Relationships**:
- Belongs to: Profile (CASCADE on delete)

**Model Methods**:
- `__str__()`: Returns "{name} - {provider}"

**Meta Options**:
- `ordering = ['order', '-date_obtained']` - By display order, then most recent first
- Index on `(profile, order)` for performance

---

### Achievement

**Purpose**: Key achievements or accomplishments

**Location**: `resume/models.py:305`

**Key Fields**:
- `profile`: ForeignKey('Profile', on_delete=CASCADE) - Associated profile
- `title`: CharField(max_length=200) - Brief achievement title
- `description`: TextField - Detailed achievement description
- `icon`: CharField(max_length=50, blank=True) - Icon name for visual display (optional, e.g., 'trophy', 'star')
- `order`: PositiveIntegerField(default=0) - Display order (lower numbers first)

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp

**Relationships**:
- Belongs to: Profile (CASCADE on delete)

**Model Methods**:
- `__str__()`: Returns title

**Meta Options**:
- `ordering = ['order', 'title']` - By display order, then alphabetically
- Index on `(profile, order)` for performance

---

## Admin Interface

All models use Unfold admin theme for enhanced UI.

### ProfileAdmin

**Location**: `resume/admin.py:51`

**Features**:
- List display: full_name, title, email, location, is_active, updated_at
- List filters: is_active, created_at, updated_at
- Search on full_name, title, email, summary
- Inline editing for all related models (Experience, Skill, Certification, Achievement)
- Bulk actions: "Activate selected profile", "Deactivate selected profiles"
- Active profile indicator in list view

**Fieldsets**:
1. Personal Information: full_name, title, email, linkedin_url, location
2. Professional Summary: summary (CKEditor)
3. Profile Photo (collapsed): photo
4. Status: is_active
5. Metadata (collapsed): created_at, updated_at

**Inlines**:
- ExperienceInline: Stacked inline for work experiences
- SkillInline: Tabular inline for skills
- CertificationInline: Tabular inline for certifications
- AchievementInline: Stacked inline for achievements

**Custom Actions**:
- `make_active`: Activates selected profile (only one can be selected)
- `make_inactive`: Deactivates selected profiles

**Business Logic**:
The `make_active` action ensures only one profile is selected before activation. Multiple selections will show an error.

---

### ExperienceAdmin

**Location**: `resume/admin.py:114`

**Features**:
- List display: position, company, location, start_date, end_date, is_current, profile, order
- List filters: profile, start_date, end_date
- Search on position, company, location, description
- Date hierarchy navigation by start_date
- Read-only duration display field
- Query optimization with select_related

**Fieldsets**:
1. Position Information: profile, position, company, location
2. Employment Period: start_date, end_date, duration_display (read-only)
3. Description: description, company_description
4. Display: order
5. Metadata (collapsed): created_at, updated_at

**Custom Display**:
- `duration_display`: Shows calculated employment duration from model's `duration` property

---

### SkillAdmin

**Location**: `resume/admin.py:163`

**Features**:
- List display: name, category, profile, order
- List filters: profile, category
- Search on name, category
- Query optimization with select_related

**Fieldsets**:
1. Skill Information: profile, name, category
2. Display: order
3. Metadata (collapsed): created_at

---

### CertificationAdmin

**Location**: `resume/admin.py:191`

**Features**:
- List display: name, provider, date_obtained, profile, order
- List filters: profile, provider, date_obtained
- Search on name, provider
- Date hierarchy navigation by date_obtained
- Query optimization with select_related

**Fieldsets**:
1. Certification Information: profile, name, provider, date_obtained, credential_url
2. Display: order
3. Metadata (collapsed): created_at

---

### AchievementAdmin

**Location**: `resume/admin.py:226`

**Features**:
- List display: title, icon, profile, order
- List filters: profile, icon
- Search on title, description
- Query optimization with select_related

**Fieldsets**:
1. Achievement Information: profile, title, description, icon
2. Display: order
3. Metadata (collapsed): created_at

---

## Configuration

### Required Settings

Configured in `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'resume',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Unfold Sidebar Navigation

Resume section added to `config/settings.py` UNFOLD configuration:

```python
{
    "title": "Resume",
    "separator": True,
    "items": [
        {"title": "Profile", "icon": "account_circle", "link": "/admin/resume/profile/"},
        {"title": "Experience", "icon": "work", "link": "/admin/resume/experience/"},
        {"title": "Skills", "icon": "code", "link": "/admin/resume/skill/"},
        {"title": "Certifications", "icon": "school", "link": "/admin/resume/certification/"},
        {"title": "Achievements", "icon": "emoji_events", "link": "/admin/resume/achievement/"},
    ],
},
```

### Required Dependencies

In `requirements.txt`:
- `Pillow==10.1.0` - Required for ImageField support (profile photo)
- `django-ckeditor==6.7.3` - Rich text WYSIWYG editor for summary and descriptions

### CKEditor Configuration

CKEditor provides a rich text editor for Profile `summary` and Experience `description` fields.

**Settings** (`config/settings.py`):

```python
INSTALLED_APPS = [
    # ...
    'ckeditor',
    'ckeditor_uploader',
    # ...
]

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 400,
        'width': '100%',
    },
}
```

---

## Media File Handling

**Profile Photos**:
- Upload path: `media/resume/photos/`
- Example: `media/resume/photos/profile.jpg`

**Storage**: Local filesystem (for production, consider S3/object storage)

**URL Access**: Via `MEDIA_URL` configured in settings

---

## Database Schema

### Tables

1. **resume_profile**: Professional profiles
   - Primary key: id (BigAutoField)
   - Indexes: is_active

2. **resume_experience**: Work experience entries
   - Primary key: id (BigAutoField)
   - Foreign keys: profile_id (resume_profile)
   - Indexes: (profile, order), (profile, -start_date)

3. **resume_skill**: Skills
   - Primary key: id (BigAutoField)
   - Foreign keys: profile_id (resume_profile)
   - Unique constraints: (profile, name)
   - Indexes: (profile, order), (profile, category)

4. **resume_certification**: Certifications
   - Primary key: id (BigAutoField)
   - Foreign keys: profile_id (resume_profile)
   - Indexes: (profile, order)

5. **resume_achievement**: Achievements
   - Primary key: id (BigAutoField)
   - Foreign keys: profile_id (resume_profile)
   - Indexes: (profile, order)

### Foreign Key Relationships

```
resume_profile
    ↓ [CASCADE]
    ├── resume_experience
    ├── resume_skill
    ├── resume_certification
    └── resume_achievement
```

**Deletion Behavior**:
- Delete Profile: All related experiences, skills, certifications, and achievements cascade delete

---

## Usage Examples

### Creating a Profile (Admin Interface)

1. Navigate to `/admin/resume/profile/add/`
2. Fill in personal information (full_name, title, email, linkedin_url, location)
3. Write professional summary in summary field (CKEditor)
4. Optionally upload profile photo
5. Set is_active to True (this will be the active profile)
6. Add experiences, skills, certifications, and achievements using inline forms
7. Save

**Single Active Profile**:
When you set is_active=True, all other profiles are automatically deactivated. Only one profile can be active at a time.

### Adding Work Experience

**Option 1: Inline (from Profile admin page)**
1. Edit profile in admin
2. Scroll to "Experiences" inline section
3. Click "Add another Experience"
4. Fill in position, company, dates, description
5. Set order for display sequence
6. Save profile

**Option 2: Direct (from Experience admin page)**
1. Navigate to `/admin/resume/experience/add/`
2. Select profile
3. Fill in all fields
4. Save

**Duration Calculation**:
Leave end_date empty for current positions. The duration field will automatically display the calculated time from start_date to present.

### Managing Skills by Category

Skills can be organized into categories (e.g., "Frontend", "Backend", "Tools"):

1. Create skills with category field
2. Skills are automatically grouped by category in display
3. Use order field to control display sequence within categories

---

## Security Considerations

### Profile Photo Uploads

**Current Protection**:
- Pillow validates image format
- Files stored outside STATIC_ROOT
- Upload path organized by purpose

**Additional Recommendations**:
1. Add file size limits in settings:
   ```python
   FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
   ```

2. Add file extension validation in models (future enhancement)

### CKEditor Security

See Blog module documentation for detailed CKEditor security considerations.

**Current Usage**: Summary and description fields are only editable by admin users, making the security risk minimal.

---

## Performance Optimization

### Query Optimization

All admin classes implement query optimization with `select_related`:

```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related('profile')
```

This reduces database queries when listing experiences, skills, certifications, and achievements.

### Index Usage

**Critical queries and their indexes**:

1. **Active profile**:
   - Query: `Profile.objects.filter(is_active=True).first()`
   - Index: `is_active`

2. **Profile experiences by order**:
   - Query: `profile.experiences.all()`
   - Index: `(profile, order)`

3. **Profile skills by category**:
   - Query: `profile.skills.filter(category='Frontend')`
   - Index: `(profile, category)`

---

## Testing Strategy

**Not yet implemented.**

Future test coverage should include:

### Model Tests (`resume/tests/test_models.py`)
- Single active profile constraint
- Duration calculation for experiences
- is_current property for ongoing positions
- Unique skill per profile constraint
- Cascade deletion of related objects

### Admin Tests (`resume/tests/test_admin.py`)
- All models registered in admin
- Inline forms display and save correctly
- make_active action enforces single selection
- Query optimization (check number of queries)

### Integration Tests (`resume/tests/test_integration.py`)
- Create complete profile with all related data
- Profile activation/deactivation workflow
- Photo upload and storage
- Order field affects display sequence

---

## Future Enhancements

Potential additions:

1. **Multiple Language Support**: Support for multilingual resumes
2. **PDF Export**: Generate PDF resume from profile data
3. **Public Resume URL**: Shareable public-facing resume page
4. **Resume Templates**: Multiple visual templates for resume display
5. **Skill Proficiency Levels**: Add proficiency rating (e.g., Beginner, Intermediate, Expert)
6. **Project Portfolio**: Add separate model for projects with screenshots
7. **Education Section**: Add education history (degrees, institutions)
8. **References**: Add professional references section
9. **Resume Analytics**: Track views and downloads
10. **Import/Export**: Import from LinkedIn, export to JSON/XML
11. **Version History**: Track changes to profile over time
12. **Custom Sections**: Allow adding arbitrary custom sections

---

## Troubleshooting

### Profile Photo Not Uploading

**Symptom**: Photo field shows error or file not saved

**Solutions**:
1. Ensure Pillow is installed: `pip install Pillow==10.1.0`
2. Rebuild Docker containers: `docker-compose down && docker-compose build && docker-compose up -d`
3. Check MEDIA_ROOT directory exists and is writable: `mkdir -p media/resume/photos`
4. Check file size (default Django limit: 2.5MB)
5. Verify image format is supported (JPEG, PNG, GIF, WebP)

### Multiple Active Profiles

**Symptom**: More than one profile shows is_active=True

**Root Cause**: Manual database modification or migration issue

**Solutions**:
1. Use admin "Activate selected profile" action on desired profile
2. Or manually via Django shell:
   ```python
   from resume.models import Profile
   Profile.objects.update(is_active=False)  # Deactivate all
   profile = Profile.objects.get(id=1)
   profile.is_active = True
   profile.save()  # This will be the only active one
   ```

### Duplicate Skill Error

**Symptom**: Error "Skill with this Profile and Name already exists"

**Root Cause**: UniqueConstraint on (profile, name)

**Solutions**:
1. Use different skill name
2. Check if skill already exists in the profile
3. Update existing skill instead of creating new one

### Duration Not Displaying

**Symptom**: Duration field shows as "-" or empty

**Root Cause**: start_date is None or invalid

**Solutions**:
1. Ensure start_date is set
2. Check date format is valid
3. For current positions, leave end_date empty (do not set to future date)

### Migration Errors

**Symptom**: "No such column" or "relation does not exist" errors

**Solutions**:
1. Ensure migrations are created: `python manage.py makemigrations resume`
2. Apply migrations: `python manage.py migrate resume`
3. Check migration status: `python manage.py showmigrations resume`
4. If using Docker: `docker-compose run --rm web python manage.py migrate resume`

---

## API Endpoints

### PDF Export Endpoint

**Endpoint:** `GET /resume/export/pdf/`

**Purpose:** Generate and download PDF version of active resume profile

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="FirstName_LastName_Resume.pdf"`

**Success (200):**
- Returns PDF file with comprehensive resume layout

**Error Cases:**
- `404`: No active profile exists
- `404`: PDF generation failed (check server logs)

**Implementation Details:**
See [`docs/modules/resume-pdf-export.md`](./resume-pdf-export.md) for complete architecture and technical details.

**Technology:** ReportLab 4.0.9 with two-column layout

**Related Code:**
- View: `resume/views.py:export_resume_pdf()`
- Generator: `resume/pdf_generator.py`
- Styles: `resume/pdf_styles.py`

---

## Migration History

### 0001_initial

**Created**: 2025-12-23

**Changes**:
- Created Profile model with fields: full_name, title, email, linkedin_url, location, summary, photo, is_active, created_at, updated_at
- Created Experience model with fields: profile, position, company, location, start_date, end_date, description, company_description, order, created_at, updated_at
- Created Skill model with fields: profile, name, category, order, created_at
- Created Certification model with fields: profile, name, provider, date_obtained, credential_url, order, created_at
- Created Achievement model with fields: profile, title, description, icon, order, created_at
- Created indexes on profile relationships and ordering fields
- Created UniqueConstraint on Skill (profile, name)

---

## Related Documentation

- **Architecture**: See `docs/architecture/system.md` for Django app organization
- **Configuration**: See `docs/config/environment.md` for environment variables
- **Deployment**: See `docs/guides/deployment.md` for production deployment with media files
- **Blog Module**: See `docs/modules/blog.md` for similar admin patterns and CKEditor usage

---

**Last Updated**: 2025-12-23
