# API Overview

This document describes the API philosophy, structure, and guidelines.

## Current State

**Status**: No public API currently implemented

The project currently provides:
- Django Admin interface (built-in)
- No REST API endpoints
- No GraphQL endpoints

This document defines how APIs should be structured when implemented.

---

## API Philosophy

When building APIs for this project, follow these principles:

### 1. RESTful Design

Use standard REST principles:
- Resources are nouns (e.g., `/products/`, not `/getProducts/`)
- HTTP methods indicate action (GET, POST, PUT, PATCH, DELETE)
- Stateless requests (no server-side session for API)
- Consistent URL structure

### 2. API Versioning

Always version APIs from the start:
- URL versioning: `/api/v1/products/`
- Header versioning: `Accept: application/vnd.myapp.v1+json`

**Recommended**: URL versioning (simpler, more visible)

### 3. Authentication

For future API implementation:
- **Token-based auth** (JWT or Django REST Framework tokens)
- **OAuth 2.0** for third-party integrations
- **API keys** for server-to-server communication

Do NOT use:
- Session-based auth (not suitable for APIs)
- Basic auth over HTTP (only over HTTPS if used)

### 4. Error Handling

Return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Enter a valid email address."]
    }
  }
}
```

### 5. Pagination

Paginate list endpoints:
- Default page size: 20
- Max page size: 100
- Provide pagination metadata

```json
{
  "count": 150,
  "next": "https://api.example.com/products/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Recommended Tools

### Django REST Framework (DRF)

**Recommendation**: Use DRF for REST APIs

**Why**:
- Battle-tested and widely used
- Built-in serialization, pagination, filtering
- Authentication and permissions
- Browsable API for development

**Installation**:
```bash
# Add to requirements.txt
djangorestframework==3.14.0
```

**Configuration**:
```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

### GraphQL (Optional)

For complex data fetching needs, consider GraphQL with Graphene-Django.

**Installation**:
```bash
# Add to requirements.txt
graphene-django==3.1.5
```

**When to use**:
- Multiple related resources in single request
- Client-driven data fetching
- Real-time updates (with subscriptions)

**When NOT to use**:
- Simple CRUD operations (use REST)
- Caching is critical (REST is easier to cache)

---

## API Structure

### URL Conventions

```
/api/v1/                      # API root
/api/v1/products/             # List and create products
/api/v1/products/{id}/        # Retrieve, update, delete product
/api/v1/products/{id}/reviews/  # Nested resource
/api/v1/auth/token/           # Obtain auth token
/api/v1/auth/refresh/         # Refresh token
```

### HTTP Methods

| Method | Endpoint | Action | Response |
|--------|----------|--------|----------|
| GET | `/api/v1/products/` | List all products | 200 OK |
| POST | `/api/v1/products/` | Create product | 201 Created |
| GET | `/api/v1/products/{id}/` | Retrieve product | 200 OK |
| PUT | `/api/v1/products/{id}/` | Full update | 200 OK |
| PATCH | `/api/v1/products/{id}/` | Partial update | 200 OK |
| DELETE | `/api/v1/products/{id}/` | Delete product | 204 No Content |

### Status Codes

Use appropriate HTTP status codes:

**Success**:
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE

**Client Errors**:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid auth
- `403 Forbidden` - Authenticated but not permitted
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error

**Server Errors**:
- `500 Internal Server Error` - Unexpected error
- `503 Service Unavailable` - Temporary unavailability

---

## API Security

### Authentication

**Token Authentication** (DRF):

```python
# myapp/views.py
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid credentials'}, status=400)
```

**Usage**:
```bash
# Obtain token
curl -X POST https://api.example.com/api/v1/auth/token/ \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl https://api.example.com/api/v1/products/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

### Rate Limiting

Prevent abuse with rate limiting:

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}
```

---

### CORS (Cross-Origin Resource Sharing)

For frontend SPAs on different domains:

```bash
# Add to requirements.txt
django-cors-headers==4.3.0
```

```python
# config/settings.py
INSTALLED_APPS = [
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Development: Allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# Production: Whitelist specific origins
CORS_ALLOWED_ORIGINS = [
    "https://frontend.example.com",
]
```

---

## API Documentation

### Auto-Generated Docs

Use OpenAPI/Swagger for API documentation:

```bash
# Add to requirements.txt
drf-spectacular==0.26.5
```

```python
# config/settings.py
INSTALLED_APPS = [
    'drf_spectacular',
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# config/urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

Access docs at: `https://example.com/api/docs/`

---

## API Testing

### Example Test

```python
# myapp/tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from myapp.models import Product

class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'pass')
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        data = {'name': 'Test Product', 'price': '99.99'}
        response = self.client.post('/api/v1/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

## API Compatibility

### Breaking Changes

Avoid breaking changes in existing API versions.

**Breaking changes**:
- Removing fields
- Changing field types
- Changing URL structure
- Changing authentication method

**When unavoidable**:
1. Create new API version (`/api/v2/`)
2. Deprecate old version with notice period
3. Document migration path

### Non-Breaking Changes

Safe to make:
- Adding new fields (with default values)
- Adding new endpoints
- Adding optional parameters
- Relaxing validation rules

---

## API Performance

### N+1 Query Problem

**Bad**:
```python
# Causes N+1 queries
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
```

**Good**:
```python
# Use select_related
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
```

---

### Caching

Cache expensive endpoints:

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
@api_view(['GET'])
def product_list(request):
    # ...
```

Or use Redis with django-redis (see ADR-008).

---

## Monitoring

Track API metrics:
- Response times
- Error rates
- Request volumes
- Authentication failures

Consider tools:
- Sentry for error tracking
- Datadog/New Relic for APM
- Django-prometheus for metrics

---

## Next Steps

When implementing an API:

1. Choose framework (recommended: DRF)
2. Update `requirements.txt`
3. Configure settings
4. Create serializers
5. Create viewsets
6. Define URLs
7. Add authentication
8. Write tests
9. Generate documentation
10. Update `api/http.md` with endpoints

See Django REST Framework documentation: https://www.django-rest-framework.org/

---

Last Updated: 2025-12-21
