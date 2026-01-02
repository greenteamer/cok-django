# Blog Module Documentation

## Overview

The `blog` Django app provides complete blogging functionality including posts, categories, tags, and commenting system.

**Scope**: Content management for blog posts with SEO support and moderation tools

**Entry Point**: `blog/models.py` for data models, `blog/admin.py` for admin interface

---

## Models

### Post

**Purpose**: Main blog post content

**Location**: `blog/models.py:108`

**Key Fields**:
- `title`: CharField(max_length=200) - Post title
- `slug`: SlugField(max_length=200, unique=True) - URL-friendly identifier (auto-generated from title)
- `content`: RichTextUploadingField - Full post content with **WYSIWYG editor** (CKEditor) supporting rich text formatting and image uploads
- `excerpt`: TextField(max_length=500, blank=True) - Short summary (auto-generated from content if empty)
- `status`: CharField(max_length=10, choices=['draft', 'published'], default='draft') - Publication status
- `author`: ForeignKey('auth.User', on_delete=PROTECT) - Post author
- `category`: ForeignKey('Category', on_delete=SET_NULL, null=True, blank=True) - Post category
- `tags`: ManyToManyField('Tag', blank=True) - Post tags
- `featured_image`: ImageField(upload_to='blog/featured/%Y/%m/', blank=True, null=True) - Featured image

**SEO Fields**:
- `meta_description`: CharField(max_length=160, blank=True) - SEO meta description (auto-generated from excerpt)
- `meta_keywords`: CharField(max_length=255, blank=True) - Comma-separated keywords

**Timestamps**:
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp
- `updated_at`: DateTimeField(auto_now=True) - Last update timestamp
- `published_at`: DateTimeField(null=True, blank=True) - Publication timestamp (set on first publish)

**Relationships**:
- Belongs to: User (author), Category (optional)
- Has many: Tags (ManyToMany), Comments (reverse relation)

**Model Methods**:
- `save()`: Auto-generates slug from title, excerpt from content, meta_description from excerpt, and sets published_at on first publish
- `is_published` (property): Returns True if status is 'published'
- `comment_count` (property): Returns count of approved comments
- `get_next_post()`: Returns next published post by published_at date
- `get_previous_post()`: Returns previous published post by published_at date
- `get_absolute_url()`: Returns URL path for the post

**Constraints**:
- Unique slug constraint
- CheckConstraint: status must be 'draft' or 'published'

**Indexes**:
- On `slug` for URL lookups
- On `status, published_at` for published post queries
- On `author, status` for author's drafts
- On `-published_at` for recent posts ordering

---

### Category

**Purpose**: Hierarchical organization of blog posts

**Location**: `blog/models.py:1`

**Key Fields**:
- `name`: CharField(max_length=100, unique=True) - Category name
- `slug`: SlugField(max_length=100, unique=True) - URL-friendly identifier (auto-generated from name)
- `description`: TextField(blank=True) - Optional category description
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp
- `updated_at`: DateTimeField(auto_now=True) - Last update timestamp

**Relationships**:
- Has many: Posts (reverse relation: `posts`)

**Model Methods**:
- `save()`: Auto-generates slug from name if not provided
- `get_absolute_url()`: Returns URL path for the category
- `__str__()`: Returns category name

**Meta Options**:
- `ordering = ['name']` - Categories ordered alphabetically
- Indexes on `slug` and `name` for performance

---

### Tag

**Purpose**: Flexible, non-hierarchical post classification

**Location**: `blog/models.py:60`

**Key Fields**:
- `name`: CharField(max_length=50, unique=True) - Tag name
- `slug`: SlugField(max_length=50, unique=True) - URL-friendly identifier (auto-generated from name)
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp

**Relationships**:
- Belongs to many: Posts (ManyToMany)

**Model Methods**:
- `save()`: Auto-generates slug from name if not provided
- `post_count` (property): Returns count of published posts with this tag
- `get_absolute_url()`: Returns URL path for the tag
- `__str__()`: Returns tag name

**Meta Options**:
- `ordering = ['name']` - Tags ordered alphabetically
- Index on `slug` for URL lookups

---

### Comment

**Purpose**: User commenting on blog posts with moderation support

**Location**: `blog/models.py:297`

**Key Fields**:
- `post`: ForeignKey('Post', on_delete=CASCADE) - Associated blog post
- `user`: ForeignKey('auth.User', on_delete=SET_NULL, null=True, blank=True) - Authenticated user (optional)
- `author_name`: CharField(max_length=100) - Commenter's name (for anonymous users)
- `author_email`: EmailField - Commenter's email (not displayed publicly)
- `author_url`: URLField(blank=True) - Optional website URL
- `content`: TextField - Comment content
- `is_approved`: BooleanField(default=False) - Moderation flag
- `ip_address`: GenericIPAddressField(null=True, blank=True) - IP address for spam prevention
- `created_at`: DateTimeField(auto_now_add=True) - Creation timestamp
- `updated_at`: DateTimeField(auto_now=True) - Last update timestamp

**Relationships**:
- Belongs to: Post (CASCADE on delete), User (optional, SET_NULL on delete)

**Model Methods**:
- `get_author_name()`: Returns authenticated user's name or provided author_name
- `get_author_email()`: Returns authenticated user's email or provided author_email
- `approve()`: Sets is_approved=True and saves
- `unapprove()`: Sets is_approved=False and saves
- `__str__()`: Returns formatted string with author and post title

**Design**: Supports both authenticated and anonymous commenters. Authenticated users have their User FK set; anonymous users have author_name/email fields filled.

**Meta Options**:
- `ordering = ['-created_at']` - Newest comments first
- Indexes on `post, is_approved, -created_at`, `is_approved`, and `-created_at` for query performance

---

## Views

### post_list

**Purpose**: Display all published blog posts

**Location**: `blog/views.py:14`

**URL Pattern**: `/blog/` (name: `post_list`)

**Template**: `templates/blog/post_list.html`

**Query Logic**:
- Fetches all posts with status='published'
- Orders by published_at descending (newest first)

**Context Variables**:
- `posts`: QuerySet of all published Post instances

**Design**:
- Only published posts are shown
- No pagination implemented yet (future enhancement)
- Grid layout matching home page Writing section

**Template Features**:
- Hero section with blog title and description
- Responsive grid of post cards
- Each card shows: featured image, date, category, title, excerpt, tags
- Cards link to individual post detail pages
- Empty state message if no posts exist

**SEO**:
- Generic blog description in meta tags
- All posts indexed on single page (consider pagination for large blogs)

---

### post_detail

**Purpose**: Display a single published blog post

**Location**: `blog/views.py:31`

**URL Pattern**: `/blog/<slug>/` (name: `post_detail`)

**Template**: `templates/blog/post_detail.html`

**Parameters**:
- `slug` (str): Post slug from URL

**Query Logic**:
- Fetches post by slug AND status='published' (404 if not found or draft)
- Retrieves next and previous published posts using `get_next_post()` and `get_previous_post()`

**Context Variables**:
- `post`: The Post instance
- `next_post`: Next published post (or None)
- `previous_post`: Previous published post (or None)

**Design**:
- Only published posts are accessible
- Draft posts return 404 to prevent unauthorized access
- Post navigation allows readers to browse chronologically

**Template Features**:
- Hero section with post title, category badge, author, date, and tags
- Featured image display (if available)
- Full post content with rich text formatting (CKEditor output)
- Previous/Next post navigation
- Back to all posts link
- Responsive design matching home page style

**SEO**:
- Uses `post.meta_description` for page description
- Includes structured post metadata (author, date, category)
- Semantic HTML for better search indexing

---

## Admin Interface

All models use Unfold admin theme for enhanced UI.

### CategoryAdmin

**Location**: `blog/admin.py:8`

**Features**:
- List display: name, slug, post_count, created_at
- Prepopulated slug field (auto-fills from name)
- Search on name and description
- Collapsed timestamps fieldset
- Custom `post_count` method showing number of posts in category

**Fieldsets**:
1. Category Information: name, slug, description
2. Timestamps (collapsed): created_at, updated_at

---

### TagAdmin

**Location**: `blog/admin.py:33`

**Features**:
- List display: name, slug, post_count, created_at
- Prepopulated slug field (auto-fills from name)
- Search on name
- Collapsed metadata fieldset
- Uses Tag model's `post_count` property

**Fieldsets**:
1. Tag Information: name, slug
2. Metadata (collapsed): created_at

---

### PostAdmin

**Location**: `blog/admin.py:73`

**Features**:
- List display: title, author, category, status, published_at, comment_count, created_at
- List filters: status, category, created_at, published_at, author
- Search on title, content, excerpt
- Prepopulated slug field (auto-fills from title)
- Filter horizontal for tags (dual listbox UI)
- Date hierarchy navigation by published_at
- Inline comment moderation (CommentInline)
- Bulk actions: "Publish selected posts", "Mark selected posts as draft"
- Query optimization with select_related and prefetch_related

**Fieldsets**:
1. Post Content: title, slug, content, excerpt
2. Publishing: status, author, published_at
3. Organization: category, tags
4. Media (collapsed): featured_image
5. SEO (collapsed): meta_description, meta_keywords
6. Metadata (collapsed): created_at, updated_at

**Custom Actions**:
- `make_published`: Bulk publish posts
- `make_draft`: Bulk unpublish posts

**Inline**:
- CommentInline: Tabular inline showing comments with author, content preview, approval status, and created_at

---

### CommentAdmin

**Location**: `blog/admin.py:159`

**Features**:
- List display: author_display, post, content_preview, is_approved, created_at
- List filters: is_approved, created_at, post
- Search on author_name, author_email, content, post__title
- All fields readonly except is_approved (comments are not editable, only moderatable)
- Bulk actions: "Approve selected comments", "Unapprove selected comments"
- Query optimization with select_related

**Fieldsets**:
1. Comment Information: post, content
2. Author Information: user, author_name, author_email, author_url, ip_address
3. Moderation: is_approved
4. Timestamps (collapsed): created_at, updated_at

**Custom Actions**:
- `approve_comments`: Bulk approve comments
- `unapprove_comments`: Bulk unapprove comments

**Custom Display**:
- `author_display`: Shows authenticated user's name or anonymous author_name
- `content_preview`: Shows first 100 characters of comment

---

## Configuration

### Required Settings

Already configured in `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'blog',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Unfold Sidebar Navigation

Blog section added to `config/settings.py` UNFOLD configuration:

```python
{
    "title": "Blog",
    "separator": True,
    "items": [
        {"title": "Posts", "icon": "article", "link": "/admin/blog/post/"},
        {"title": "Categories", "icon": "folder", "link": "/admin/blog/category/"},
        {"title": "Tags", "icon": "label", "link": "/admin/blog/tag/"},
        {"title": "Comments", "icon": "comment", "link": "/admin/blog/comment/"},
    ],
},
```

### Required Dependencies

In `requirements.txt`:
- `Pillow==10.1.0` - Required for ImageField support
- `django-ckeditor==6.7.3` - Rich text WYSIWYG editor for post content

**Security Note**: Current version includes CKEditor 4.22.1. While this version has known security warnings, the risk is minimal for single-admin usage. CKEditor 4.25.1-lts (secure version) is not yet available in django-ckeditor package. Monitor updates at: https://github.com/django-ckeditor/django-ckeditor

### CKEditor Configuration

CKEditor provides a rich text editor for the Post `content` field in the admin interface.

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

**Features**:
- Full rich text formatting (bold, italic, underline, colors, etc.)
- Lists (numbered, bulleted), blockquotes, indentation
- Links and anchors
- **Image uploads** directly in the editor
- Tables and horizontal rules
- Text alignment (left, center, right, justify)
- Special characters and smileys
- Source code view (HTML)

**Image Uploads**:
- Path: `media/uploads/` (configurable via `CKEDITOR_UPLOAD_PATH`)
- Backend: Pillow for image processing
- Accessible via: `/ckeditor/upload/` endpoint

**URL Configuration** (`config/urls.py`):
```python
urlpatterns = [
    path("ckeditor/", include("ckeditor_uploader.urls")),
]
```

---

## Media File Handling

**Featured Images**:
- Upload path: `media/blog/featured/{YEAR}/{MONTH}/`
- Example: `media/blog/featured/2025/12/image.jpg`
- Automatically organized by year and month

**Storage**: Local filesystem (for production, consider S3/object storage)

**URL Access**: Via `MEDIA_URL` configured in settings

---

## Database Schema

### Tables

1. **blog_category**: Categories
   - Primary key: id (BigAutoField)
   - Unique constraints: name, slug
   - Indexes: slug, name

2. **blog_tag**: Tags
   - Primary key: id (BigAutoField)
   - Unique constraints: name, slug
   - Indexes: slug

3. **blog_post**: Posts
   - Primary key: id (BigAutoField)
   - Foreign keys: author_id (auth_user), category_id (blog_category)
   - Unique constraints: slug
   - Indexes: slug, (status, published_at), (author, status), -published_at
   - Check constraint: status IN ('draft', 'published')

4. **blog_post_tags**: ManyToMany relation (Post ↔ Tag)
   - Composite index on (post_id, tag_id)

5. **blog_comment**: Comments
   - Primary key: id (BigAutoField)
   - Foreign keys: post_id (blog_post), user_id (auth_user, nullable)
   - Indexes: (post, is_approved, -created_at), is_approved, -created_at

### Foreign Key Relationships

```
auth_user ←──[PROTECT]──── blog_post
                              ↓ [CASCADE]
                         blog_comment

blog_category ←──[SET_NULL]──── blog_post

blog_tag ←──[M2M]──── blog_post
```

**Deletion Behavior**:
- Delete User: Protected (cannot delete if user has posts)
- Delete Post: Comments cascade delete
- Delete Category: Posts set category to NULL
- Delete Tag: Removed from posts (M2M unlink)

---

## Usage Examples

### Creating a Post (Admin Interface)

1. Navigate to `/admin/blog/post/add/`
2. Fill in title (slug auto-generates)
3. Write content in content field
4. Optionally fill excerpt and SEO fields (auto-generate if left empty)
5. Select author, category, tags
6. Upload featured image (optional)
7. Set status to "Published" or leave as "Draft"
8. Save

**Auto-generation behavior**:
- Slug: generated from title if empty
- Excerpt: first 497 characters of content if empty
- Meta description: first 157 characters of excerpt if empty
- Published_at: set to current time when first published (not updated on subsequent saves)

### Moderating Comments

**Option 1: Inline (from Post admin page)**
1. Edit post in admin
2. Scroll to "Comments" inline section
3. Check "Approved" checkbox for valid comments
4. Save post

**Option 2: Bulk (from Comment list page)**
1. Navigate to `/admin/blog/comment/`
2. Filter by "is_approved = False" (unapproved comments)
3. Select comments to approve
4. Choose "Approve selected comments" action
5. Click "Go"

---

## Security Considerations

### Comment Moderation

- **Default**: All comments start with `is_approved=False`
- Requires manual approval by admin before public display
- IP address logged for spam tracking
- Both authenticated and anonymous comments supported

### Author Permissions

Use Django's built-in permission system:

**Recommended Permission Groups**:

1. **Blog Authors**:
   - Permissions: `blog.add_post`, `blog.change_post`, `blog.view_post`
   - Limitation: Should only edit own posts (requires custom admin override)

2. **Blog Editors**:
   - Permissions: All blog permissions
   - Can edit any post, moderate comments

3. **Comment Moderators**:
   - Permissions: `blog.view_comment`, `blog.change_comment`
   - Can approve/reject comments only

### CKEditor Security

**Current Version**: CKEditor 4.22.1 (bundled with django-ckeditor 6.7.3)

**Status**: This version has known security advisories and is not the latest LTS version (4.25.1-lts).

**Risk Assessment for Single-Admin Usage**:
- ✅ **Low Risk**: You control all content input through admin interface
- ✅ **XSS Protection**: Django templates auto-escape output by default
- ⚠️ **Consideration**: Avoid using `|safe` filter without sanitization

**Risk Assessment for Multi-User/Public Scenarios**:
- ⚠️ **Higher Risk**: Multiple admins could introduce malicious content
- ⚠️ **Public Forms**: Never expose CKEditor to unauthenticated users
- ⚠️ **Content Display**: Always sanitize HTML when showing to public

**Mitigation Strategies**:
1. **Limit access** - Restrict admin access to trusted users only
2. **Content sanitization** - Use `bleach` library for public content display:
   ```python
   import bleach
   clean_content = bleach.clean(post.content, tags=allowed_tags)
   ```
3. **Monitor updates** - Check https://github.com/django-ckeditor/django-ckeditor for CKEditor 4.25.1-lts
4. **Template safety** - Use Django's auto-escaping (avoid `|safe` without sanitization)

**Update Path**:
- CKEditor 4.25.1-lts integration in django-ckeditor is pending
- Monitor package releases for security updates
- Alternative: Consider django-tinymce4-lite or Quill if immediate update required

**Current Recommendation for Your Use Case**:
Since you're the only admin user, the risk is **minimal**. The security warnings primarily affect public-facing or multi-user scenarios.

### File Upload Security

**Current Protection**:
- Pillow validates image format
- Files stored outside STATIC_ROOT
- Upload path organized by date

**Additional Recommendations**:
1. Add file size limits in settings:
   ```python
   FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
   ```

2. Add file extension validation in models (future enhancement)

### Email Privacy

- **Never display `author_email` publicly**
- Use only for admin contact/moderation purposes
- GDPR consideration: implement data deletion on request

---

## Performance Optimization

### Query Optimization

**PostAdmin** implements query optimization:
```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related('category', 'author').prefetch_related('tags')
```

**CommentAdmin** implements query optimization:
```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related('post', 'user')
```

### Index Usage

**Critical queries and their indexes**:

1. **Published posts by date**:
   - Query: `Post.objects.filter(status='published').order_by('-published_at')`
   - Index: `(status, published_at)` and `-published_at`

2. **Author's posts**:
   - Query: `Post.objects.filter(author=user, status='draft')`
   - Index: `(author, status)`

3. **Slug lookup**:
   - Query: `Post.objects.get(slug='my-post')`
   - Index: `slug` (unique)

4. **Approved comments for post**:
   - Query: `Comment.objects.filter(post=post, is_approved=True)`
   - Index: `(post, is_approved, -created_at)`

---

## Testing Strategy

**Not yet implemented.**

Future test coverage should include:

### Model Tests (`blog/tests/test_models.py`)
- Slug auto-generation for Category, Tag, Post
- Excerpt auto-generation from content
- Meta description auto-generation from excerpt
- published_at set only on first publish (not on updates)
- Status validation (CheckConstraint)
- Comment author methods (get_author_name, get_author_email)
- Post navigation methods (get_next_post, get_previous_post)

### Admin Tests (`blog/tests/test_admin.py`)
- All models registered in admin
- Prepopulated fields work correctly
- Bulk actions execute successfully
- Inline comments display and save
- Query optimization (check number of queries)

### Integration Tests (`blog/tests/test_integration.py`)
- Create post with category and tags
- Comment approval workflow
- Cascade deletion behavior
- Image upload and storage

---

## Future Enhancements

Potential additions:

1. ~~**Rich Text Editor**~~: ✅ **IMPLEMENTED** - CKEditor with image upload support
2. ~~**Post List Page**~~: ✅ **IMPLEMENTED** - All posts view at `/blog/`
3. **Pagination**: Add pagination to post list (e.g., 10 posts per page)
4. **Post Scheduling**: Schedule posts for future publication
5. **View Counter**: Track post view counts
6. **Related Posts**: Auto-suggest related posts by category/tags
7. **Comment Threading**: Nested reply support
8. **Spam Protection**: Integrate Akismet or similar service
9. **RSS Feed**: Auto-generate RSS feed from published posts
10. **Sitemap**: Auto-generate XML sitemap for SEO
11. **Draft Preview**: Public preview URL for draft posts
12. **Post Versions**: Track content revisions
13. **Slug Versioning**: Auto-append numbers to duplicate slugs (e.g., "my-post-2")
14. **Author Profiles**: Extend User model with bio, avatar, social links
15. **Search**: Full-text search across posts
16. **Category/Tag Pages**: Filter posts by category or tag

---

## Troubleshooting

### Featured Image Not Uploading

**Symptom**: Image field shows error or file not saved

**Solutions**:
1. Ensure Pillow is installed: `pip install Pillow==10.1.0`
2. Rebuild Docker containers: `docker-compose down && docker-compose build && docker-compose up -d`
3. Check MEDIA_ROOT directory exists and is writable: `mkdir -p media/blog/featured`
4. Check file size (default Django limit: 2.5MB)
5. Verify image format is supported (JPEG, PNG, GIF, WebP)

### Slug Conflicts

**Symptom**: Error "Post with this Slug already exists"

**Root Cause**: Two posts with same title generate identical slugs

**Solutions**:
1. Use unique title
2. Manually edit slug to be unique in admin
3. Consider adding date to slug: `my-post-2025-12-22`
4. **Future**: Implement automatic slug versioning (see Future Enhancements)

### Comments Not Appearing

**Symptom**: Comment submitted but not visible publicly

**Root Cause**: Default `is_approved=False` for new comments

**Solutions**:
1. Check `is_approved` flag in admin
2. Approve comment via admin interface
3. Implement auto-approval for authenticated users (custom logic)

### Published_at Not Updating

**Symptom**: published_at timestamp doesn't change when re-publishing

**Root Cause**: Intentional design - published_at is set only on first publish

**Explanation**: This is correct behavior. The published_at field represents the original publication date, not the last update. Use `updated_at` for modification tracking.

### Migration Errors

**Symptom**: "No such column" or "relation does not exist" errors

**Solutions**:
1. Ensure migrations are created: `python manage.py makemigrations blog`
2. Apply migrations: `python manage.py migrate blog`
3. Check migration status: `python manage.py showmigrations blog`
4. If using Docker: `docker-compose exec web python manage.py migrate blog`

---

## URL Endpoints

### Implemented

**Post List View**:
```
/blog/                         # All posts list page (public)
```

**URL Configuration**: `config/urls.py:27`

**Access Control**: Only published posts are shown

**Integration**:
- Home page "View all posts" link (`templates/home.html:155`)
- Post detail page "Back to all posts" link (`templates/blog/post_detail.html:88`)

---

**Post Detail View**:
```
/blog/<slug>/                  # Post detail page (public)
```

**URL Configuration**: `config/urls.py:28`

**Example**: `/blog/my-first-post/`

**Access Control**: Only published posts are accessible (drafts return 404)

**Integration**:
- Home page post cards (`templates/home.html`) link via `post.get_absolute_url()`
- Blog list page post cards (`templates/blog/post_list.html`) link via `post.get_absolute_url()`

**URL Structure Rationale**:
- `/blog/` - Main blog index
- `/blog/<slug>/` - Simple, clean URLs for individual posts
- Reserved short paths for future features: `category`, `tag`, `archive`, `author`
- SEO-friendly: shorter URLs perform better
- Follows common blog conventions (WordPress, Ghost, Medium, etc.)

### Future Endpoints

Not yet implemented:
- `/blog/category/<slug>/` - Category posts
- `/blog/tag/<slug>/` - Tag posts
- `/blog/archive/<year>/` or `/blog/<year>/<month>/` - Date-based archives
- `/blog/author/<username>/` - Author's posts
- `/blog/<slug>/comment/` - Comment submission endpoint (POST)
- Pagination for `/blog/` (e.g., `/blog/page/2/`)
- REST API via Django REST Framework

---

## Migration History

### 0001_initial

**Created**: 2025-12-22

**Changes**:
- Created Category model with fields: name, slug, description, created_at, updated_at
- Created Tag model with fields: name, slug, created_at
- Created Post model with fields: title, slug, content, excerpt, status, author, category, tags, featured_image, meta_description, meta_keywords, created_at, updated_at, published_at
- Created Comment model with fields: post, author_name, author_email, author_url, user, content, is_approved, created_at, updated_at, ip_address
- Created indexes on slug fields for all models
- Created composite indexes for Post queries
- Created CheckConstraint for Post status validation
- Created ManyToMany table for Post-Tag relationship

### 0002_alter_post_content

**Created**: 2025-12-22

**Changes**:
- Altered Post.content field from TextField to RichTextUploadingField
- Added CKEditor WYSIWYG editor support for post content
- Enabled image uploads directly in the editor

---

## Related Documentation

- **Architecture**: See `docs/architecture/project-structure.md` for Django app organization
- **Configuration**: See `docs/config/environment.md` for environment variables
- **Deployment**: See `docs/guides/deployment.md` for production deployment with media files

---

**Last Updated**: 2025-12-31
