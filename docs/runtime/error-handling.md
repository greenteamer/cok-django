# Error Handling

This document describes how errors are handled throughout the system.

## Error Handling Philosophy

1. **Fail fast** - Detect errors early and loudly
2. **Log errors** - All errors are logged for debugging
3. **Graceful degradation** - Show user-friendly messages
4. **Never expose sensitive data** - No stack traces or internal details in production

---

## Error Levels

### Application Errors (500)

**Cause**: Unhandled exceptions in Django code

**Examples**:
- Python syntax errors
- Uncaught exceptions in views
- Database query errors
- Third-party library errors

**Behavior**:

**Development** (`DEBUG=True`):
- Full traceback displayed in browser
- Detailed error page with local variables
- Helpful for debugging

**Production** (`DEBUG=False`):
- Generic 500 error page
- No sensitive information exposed
- Error logged to stdout

**Error Page Template**: `templates/500.html` (if created)

**Default Django 500 page**: "Server Error (500)"

---

### Client Errors (4xx)

#### 404 Not Found

**Cause**: URL doesn't match any pattern in `urlpatterns`

**Behavior**:
- Django displays 404 page
- Not logged as error (expected behavior)

**Development**: Shows which URL patterns were tried

**Production**: Generic 404 page

**Custom Template**: `templates/404.html`

**Example**:
```html
<!-- templates/404.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found</title>
</head>
<body>
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/">Go Home</a>
</body>
</html>
```

---

#### 403 Forbidden

**Cause**: User doesn't have permission to access resource

**Behavior**:
- Django displays 403 page
- Logged as warning

**Custom Template**: `templates/403.html`

---

#### 400 Bad Request

**Cause**: Malformed request (e.g., invalid POST data)

**Behavior**:
- Django returns 400 status
- Logged as warning

**Custom Template**: `templates/400.html`

---

### Database Errors

#### Connection Errors

**Cause**: PostgreSQL not reachable

**Error**: `django.db.utils.OperationalError: could not connect to server`

**Handling**:
1. `entrypoint.sh` waits for database on startup
2. If database goes down during runtime:
   - Request fails with 500
   - Error logged
   - User sees generic error page

**Prevention**:
- Ensure database container is running
- Use connection pooling (Django default)
- Monitor database health

**Recovery**:
```bash
# Check database status
docker-compose ps db

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

---

#### Query Errors

**Cause**: Invalid SQL or constraint violations

**Examples**:
- `IntegrityError` - Unique constraint violation
- `DataError` - Data too long for field
- `OperationalError` - Syntax error in query

**Handling**:

**In views** (recommended):
```python
from django.db import IntegrityError
from django.http import JsonResponse

def create_user(request):
    try:
        user = User.objects.create(username=username)
        return JsonResponse({'status': 'success'})
    except IntegrityError:
        return JsonResponse({'error': 'Username already exists'}, status=400)
```

**Unhandled**:
- Results in 500 error
- Logged to stdout
- Transaction rolled back automatically

---

## Exception Handling in Views

### Try-Except Pattern

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def process_payment(request):
    try:
        amount = float(request.POST.get('amount'))
        # Process payment
        return JsonResponse({'status': 'success'})
    except ValueError:
        # Invalid amount format
        return JsonResponse({'error': 'Invalid amount'}, status=400)
    except PaymentError as e:
        # Expected business error
        logger.warning(f"Payment failed: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error in payment: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
```

**Best Practices**:
1. Catch specific exceptions first
2. Log unexpected errors with traceback (`exc_info=True`)
3. Return appropriate HTTP status codes
4. Don't expose internal error details to users

---

## Django Middleware Exception Handling

Django catches exceptions in middleware stack:

```
Request
  ↓
Middleware (request phase)
  ↓
View (exception raised here)
  ↓
Middleware (exception phase) ← Catches exception
  ↓
Error handler (500, 404, etc.)
  ↓
Response
```

**Custom Error Handling Middleware**:

```python
# myapp/middleware.py
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Log all exceptions
        logger.error(f"Exception on {request.path}", exc_info=True)

        # Optionally send to external service (Sentry, etc.)
        # sentry_sdk.capture_exception(exception)

        # Return None to use default error handling
        return None
```

**Register middleware**:
```python
# config/settings.py
MIDDLEWARE = [
    'myapp.middleware.ErrorHandlingMiddleware',
    # ... other middleware
]
```

---

## Logging Errors

All errors are logged using Python's logging module.

**Default Django logging** (configured in `settings.py`):

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

**What gets logged**:
- `django.request` - All 5xx errors and warnings
- `django.security` - Security-related warnings
- `django.db.backends` - SQL queries (if level=DEBUG)

**Usage in code**:
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical error")
```

See `ops/logging.md` for detailed logging configuration.

---

## Error Monitoring

### Current State

Errors are logged to stdout and captured by Docker.

**View logs**:
```bash
docker-compose logs web | grep ERROR
```

---

### Recommended: External Error Tracking

For production, use external error tracking service:

#### Sentry (Recommended)

**Installation**:
```bash
# Add to requirements.txt
sentry-sdk==1.38.0
```

**Configuration**:
```python
# config/settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=config('SENTRY_DSN', default=''),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,   # Don't send user data
    )
```

**Benefits**:
- Automatic error grouping
- Stack traces with context
- Release tracking
- Performance monitoring
- Alerts and notifications

---

## Transaction Management

Django automatically wraps each request in a database transaction.

**Behavior**:
- All database operations in a view are in one transaction
- If view raises exception, transaction is rolled back
- If view completes successfully, transaction is committed

**Explicit transaction control**:

```python
from django.db import transaction

def transfer_money(from_account, to_account, amount):
    with transaction.atomic():
        # All or nothing: both succeed or both rolled back
        from_account.balance -= amount
        from_account.save()

        to_account.balance += amount
        to_account.save()
```

**On exception**:
```python
try:
    with transaction.atomic():
        # Operations here
        if error:
            raise ValueError("Something wrong")
except ValueError as e:
    # Transaction already rolled back
    logger.error(f"Transaction failed: {e}")
```

---

## Validation Errors

### Form Validation

```python
from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    price = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be positive")
        return price

# In view
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Process valid data
            return redirect('success')
        else:
            # form.errors contains validation errors
            return render(request, 'form.html', {'form': form})
```

**Validation errors are NOT logged** (expected user input errors).

---

### Model Validation

```python
from django.core.exceptions import ValidationError
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.price <= 0:
            raise ValidationError({'price': 'Price must be positive'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs validation
        super().save(*args, **kwargs)
```

---

## Retry Logic

For transient errors (network issues, temporary database unavailability):

```python
import time
from django.db import OperationalError

def robust_database_operation():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Perform operation
            result = SomeModel.objects.create(...)
            return result
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database error, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error("Database operation failed after retries", exc_info=True)
                raise
```

---

## Graceful Degradation

When a non-critical feature fails, degrade gracefully:

```python
def get_user_recommendations(user):
    try:
        # Call recommendation service
        recommendations = recommendation_api.get(user.id)
        return recommendations
    except Exception as e:
        # Log error but don't break page
        logger.error(f"Recommendation service failed: {e}")
        # Return fallback
        return Product.objects.filter(featured=True)[:5]
```

**Principle**: Core functionality should work even if auxiliary features fail.

---

## Error Responses for APIs

When building APIs, return consistent error responses:

```python
from django.http import JsonResponse

def api_error_response(message, code, status=400, details=None):
    response = {
        'error': {
            'code': code,
            'message': message,
        }
    }
    if details:
        response['error']['details'] = details

    return JsonResponse(response, status=status)

# Usage
def create_product_api(request):
    try:
        # Process request
        pass
    except ValidationError as e:
        return api_error_response(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status=400,
            details=e.message_dict
        )
    except Exception as e:
        logger.error("Unexpected error", exc_info=True)
        return api_error_response(
            message="Internal server error",
            code="INTERNAL_ERROR",
            status=500
        )
```

---

## Testing Error Handling

Always test error paths:

```python
from django.test import TestCase
from django.db import IntegrityError

class ProductTest(TestCase):
    def test_duplicate_product_name_raises_error(self):
        Product.objects.create(name="Test", price=10)

        with self.assertRaises(IntegrityError):
            Product.objects.create(name="Test", price=20)

    def test_view_handles_invalid_input(self):
        response = self.client.post('/create/', {'price': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
```

---

## Debugging Errors

### Development

1. **Django Debug Toolbar**:
   ```bash
   # Add to requirements.txt
   django-debug-toolbar==4.2.0
   ```

   Shows SQL queries, cache hits, templates used.

2. **Django Extensions**:
   ```bash
   # Add to requirements.txt
   django-extensions==3.2.3
   ```

   Enhanced shell, graph models, etc.

---

### Production

1. **Check logs**:
   ```bash
   docker-compose logs web --tail 100
   ```

2. **Access Django shell**:
   ```bash
   docker-compose exec web python manage.py shell
   ```

3. **Database queries**:
   ```bash
   docker-compose exec db psql -U django_user django_db
   ```

4. **Check Sentry** (if configured) for detailed error reports.

---

## Common Errors and Solutions

### "DisallowedHost at /"

**Cause**: Request Host header not in `ALLOWED_HOSTS`

**Solution**: Add hostname to `ALLOWED_HOSTS` in `.env`

---

### "CSRF verification failed"

**Cause**: CSRF token missing or invalid

**Solution**:
- Include `{% csrf_token %}` in forms
- For AJAX, send CSRF token in headers
- Exempt view if external API: `@csrf_exempt`

---

### "TemplateDoesNotExist"

**Cause**: Template file not found

**Solution**:
- Check template path in `DIRS` setting
- Verify file exists in `templates/` directory
- Check for typos in template name

---

Last Updated: 2025-12-21
