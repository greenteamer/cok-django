# HTTP Endpoints

This document lists all HTTP endpoints in the application.

## Current Endpoints

Currently, the application provides only the Django Admin interface.

### Django Admin

**URL**: `/admin/`

**Purpose**: Administrative interface for managing database content

**Authentication**: Django session-based authentication (username/password)

**Methods**: GET, POST (via admin interface)

**Access**: Superuser accounts only

**Features**:
- User management
- Group and permission management
- Database browsing and editing
- Model history and audit log

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

**Handler**: Nginx (production), WhiteNoise (development)

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

**Handler**: Nginx (production), Django (development)

**Purpose**: Serve user-uploaded files

**Example**:
```
/media/uploads/user_avatar.jpg
/media/documents/report.pdf
```

**Security Note**: For sensitive files, implement view-based permissions rather than direct file access.

---

## Health Check Endpoint

**Recommendation**: Add a health check endpoint for monitoring.

**Example Implementation**:

```python
# config/urls.py
from django.http import JsonResponse

def health_check(request):
    # Optional: check database connectivity
    from django.db import connection
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        "status": "ok",
        "database": db_status,
    })

urlpatterns = [
    path('health/', health_check),
    # ...
]
```

**Usage**:
```bash
curl https://example.com/health/
```

**Response**:
```json
{
  "status": "ok",
  "database": "ok"
}
```

---

## URL Routing

Current URL configuration is in `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# In development, serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Note**: In production, Nginx handles static and media files (see `architecture/system.md`).

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

## Changelog

When endpoints change, document changes here:

### 2025-12-21
- Initial documentation
- Only Django Admin available

---

Last Updated: 2025-12-21
