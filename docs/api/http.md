# HTTP Endpoints

This document lists all HTTP endpoints in the application.

## Current Endpoints

### Public Pages

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/` | `home` | `config.views.home` | Home page: profile, featured projects, recent posts |
| `/blog/` | `post_list` | `blog.views.post_list` | Published posts, paginated (`?page=`) |
| `/blog/<slug>/` | `post_detail` | `blog.views.post_detail` | Published post (404 for drafts) |
| `/projects/` | `project_list` | `projects.views.project_list` | Projects list |
| `/projects/<slug>/` | `project_detail` | `projects.views.project_detail` | Project page |
| `/resume/` | `resume` | `resume.views.resume_page` | Resume page |
| `/resume/export/pdf/` | `export_resume_pdf` | `resume.views.export_resume_pdf` | Resume as PDF |
| `/sitemap.xml` | `sitemap` | Django sitemaps | Blog, projects, static pages |
| `/robots.txt` | `robots_txt` | `config.views.robots_txt` | Disallows `/admin/`, `/ckeditor/` |

`/robots`, `/robots/`, `/robots.txt/`, `/sitemap`, `/sitemap/`, `/sitemap.xml/` permanently redirect to the canonical URLs.

### Staff / Internal

| URL | Description |
|-----|-------------|
| `/admin/` | Django Admin (Unfold) |
| `/admin/tools/cover/` | Blog cover generator (see below) |
| `/ckeditor/` | CKEditor upload endpoints (staff) |
| `/health/` | Health check (see below) |

Source of truth: `config/urls.py`.

### Django Admin

**URL**: `/admin/`

**Purpose**: Administrative interface for managing database content

**Authentication**: Django session-based authentication (username/password)

**Methods**: GET, POST (via admin interface)

**Access**: Staff accounts (`is_staff`)

**Features**:
- User management
- Group and permission management
- Database browsing and editing
- Model history and audit log

### Blog Cover Generator

**URL**: `/admin/tools/cover/`

**Method**: GET

**Authentication**: Django admin session

**Permissions**: Staff users (`is_staff`); anonymous users are redirected to `/admin/login/`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `post` | integer | No | Post ID to prefill title, tags and category; unknown IDs fall back to defaults |

**Response**: HTML editor page. Images are generated in the browser, not on the server.

See [`modules/cover-generator.md`](../modules/cover-generator.md).

---

## Future API Endpoints

When REST API is implemented, endpoints will be documented here.

### Expected Structure

```
/api/v1/                      # API root, returns available endpoints
/api/v1/auth/token/           # Obtain authentication token
/api/v1/auth/refresh/         # Refresh authentication token
/api/v1/users/                # User resource (CRUD)
/api/v1/users/{id}/           # Specific user
```

---

## Endpoint Template

When adding new endpoints, document them in this format:

---

### Endpoint Name

**URL**: `/api/v1/resource/`

**Method**: GET

**Authentication**: Required (Token)

**Permissions**: Authenticated users

**Description**: Brief description of what this endpoint does

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number for pagination (default: 1) |
| `page_size` | integer | No | Items per page (default: 20, max: 100) |
| `search` | string | No | Search query |

**Request Example**:
```bash
curl https://api.example.com/api/v1/resource/?page=1&search=test \
  -H "Authorization: Token abc123"
```

**Success Response** (200 OK):
```json
{
  "count": 50,
  "next": "https://api.example.com/api/v1/resource/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Example",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication credentials were not provided."
  }
}
```

---

## Static and Media Endpoints

### Static Files

**URL Pattern**: `/static/*`

**Method**: GET

**Authentication**: None (public)

**Handler**: WhiteNoise (Railway production), Nginx (self-hosted)

**Purpose**: Serve CSS, JavaScript, images for Django admin and apps

**Example**:
```
/static/admin/css/base.css
/static/admin/js/jquery.js
```

**Cache Headers**: Set by WhiteNoise/Nginx for performance

---

### Media Files

**URL Pattern**: `/media/*`

**Method**: GET

**Authentication**: None (public by default, can be protected)

**Handler**: Django when `DEBUG=True` or `SERVE_MEDIA=True` (Railway production), Nginx (self-hosted), or R2 public domain when `USE_R2=True`

**Purpose**: Serve user-uploaded files

**Example**:
```
/media/uploads/user_avatar.jpg
/media/documents/report.pdf
```

**Security Note**: For sensitive files, implement view-based permissions rather than direct file access.

---

## Health Check Endpoint

### GET /health/

Application health check for Railway and external monitoring.

**URL**: `/health/`

**Method**: GET

**Authentication**: None (public)

**Permissions**: None

**Description**: Returns application and database status. Used by Railway's health check (configured in Railway service settings) to verify the service is running and responsive. Returns HTTP 200 when healthy, HTTP 503 when database is unreachable.

**Request Example**:
```bash
curl https://coreofkeen.com/health/
```

**Success Response** (200 OK):
```json
{
  "status": "ok",
  "database": "ok"
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "status": "ok",
  "database": "error: OperationalError"
}
```

**Implementation**: `config/views.py` → `health_check()` view, registered in `config/urls.py`.

**Railway Integration**: Set as Healthcheck Path in Railway service settings (timeout 120 s). See [`guides/deployment-railway.md`](../guides/deployment-railway.md).

---

## URL Routing

URL configuration lives in `config/urls.py` (see [Current Endpoints](#current-endpoints) for the full list).

Static and media routes appended at the end:

- `/static/` — Django serves it only when `DEBUG=True`; in production WhiteNoise middleware serves collected files from `STATIC_ROOT`
- `/media/` — Django serves `MEDIA_ROOT` when `DEBUG=True` or `SERVE_MEDIA=True` (Railway production); self-hosted setups serve it from Nginx

---

## Cross-Origin Resource Sharing (CORS)

Currently, CORS is not configured as there are no API endpoints.

When API is added, configure CORS using `django-cors-headers` (see `api/overview.md`).

---

## Rate Limiting

Currently, no rate limiting is implemented.

For future API endpoints, implement rate limiting to prevent abuse (see `api/overview.md`).

---

## SSL/TLS Enforcement

In production (`DEBUG=False`), all HTTP requests are redirected to HTTPS.

See `security/overview.md` for security configuration.

---

## Endpoint Discovery

When REST API is implemented with Django REST Framework, the API root will provide endpoint discovery:

**Example** (future):
```bash
curl https://api.example.com/api/v1/
```

**Response**:
```json
{
  "users": "https://api.example.com/api/v1/users/",
  "products": "https://api.example.com/api/v1/products/",
  "orders": "https://api.example.com/api/v1/orders/"
}
```

---

## API Versioning

When multiple API versions exist, document each version separately:

### API v1 (Current)
- Endpoints listed above

### API v2 (Future)
- Breaking changes documented here

---

## Resume Export

### GET /resume/export/pdf/

Export active resume profile as PDF with professional formatting.

**URL**: `/resume/export/pdf/`

**Method**: GET

**Authentication**: None (public)

**Permissions**: None

**Description**: Generates and downloads a professional PDF resume from the active profile in the database. Uses ReportLab with two-column layout.

**Query Parameters**: None

**Request Example**:
```bash
curl -O http://localhost:8000/resume/export/pdf/
# Downloads: Aleksandr_Korovkin_Resume.pdf
```

**Success Response** (200 OK):
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="<FullName>_Resume.pdf"`
- **Body**: Binary PDF file

**Error Responses**:

404 Not Found - No active profile:
```
No active resume profile found.
```

404 Not Found - Generation failed:
```
Failed to generate PDF resume. Please try again later.
```

**Notes**:
- Only the active profile (`is_active=True`) is exported
- PDF includes: experiences, skills, certifications, achievements, profile photo
- Layout: Two-column professional resume format (main content + sidebar)
- Technology: ReportLab 4.0.9 with programmatic PDF generation
- Generation time: ~500ms for typical resume

**Implementation Details**:
See [`docs/modules/resume-pdf-export.md`](../modules/resume-pdf-export.md) for architecture.

---

## Changelog

When endpoints change, document changes here:

### 2026-02-12
- Added health check endpoint (`GET /health/`)
- Health check verifies database connectivity, returns JSON status

### 2026-01-07
- Added PDF resume export endpoint (`GET /resume/export/pdf/`)
- Implemented ReportLab-based PDF generation

### 2025-12-21
- Initial documentation
- Only Django Admin available

---

Last Updated: 2026-02-12
