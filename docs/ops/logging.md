# Logging

This document describes the logging strategy, configuration, and best practices for the application.

## Logging Philosophy

1. **Log to stdout** - All logs go to stdout/stderr (Docker captures them)
2. **Structured logs** - Use consistent format for parsing
3. **Appropriate levels** - Use correct log level for each message
4. **No sensitive data** - Never log passwords, tokens, or PII
5. **Actionable logs** - Logs should help debugging and monitoring

---

## Current Logging Configuration

### Django Logging

Currently using Django's default logging configuration.

**Log handlers**:
- Console (stdout/stderr)

**Log levels**:
- Development: `DEBUG`
- Production: `INFO` for application, `ERROR` for requests

**Log format**: Plain text with timestamp, level, module, message

---

## Recommended Logging Configuration

Add to `config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
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
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Log Levels

### When to Use Each Level

#### DEBUG

**Use for**: Detailed diagnostic information

**Example**:
```python
logger.debug(f"Processing order {order_id} with items: {items}")
logger.debug(f"Database query: {query}")
```

**Visibility**: Only in development (`DEBUG=True`)

---

#### INFO

**Use for**: General informational messages

**Example**:
```python
logger.info(f"User {user.username} logged in")
logger.info(f"Email sent to {recipient}")
logger.info(f"Scheduled task started: {task_name}")
```

**Visibility**: Development and production

---

#### WARNING

**Use for**: Unexpected but recoverable situations

**Example**:
```python
logger.warning(f"Retry attempt {attempt} for API call")
logger.warning(f"Deprecated function called: {func_name}")
logger.warning(f"Configuration missing, using default: {default_value}")
```

**Visibility**: Development and production

---

#### ERROR

**Use for**: Errors that don't crash the application

**Example**:
```python
logger.error(f"Payment processing failed: {error}", exc_info=True)
logger.error(f"Failed to send email to {recipient}")
logger.error(f"Database connection lost, retrying...")
```

**Visibility**: Development and production

**Note**: Use `exc_info=True` to include stack trace

---

#### CRITICAL

**Use for**: Critical errors that may cause service degradation

**Example**:
```python
logger.critical(f"Database unavailable, service degraded")
logger.critical(f"External API down: {api_name}")
```

**Visibility**: Development and production

---

## Logging in Code

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(f"Processing order {order.id}")

    try:
        # Business logic
        result = charge_payment(order)
        logger.info(f"Payment successful for order {order.id}")
        return result
    except PaymentError as e:
        logger.error(f"Payment failed for order {order.id}: {e}", exc_info=True)
        raise
```

---

### Structured Logging

For better log parsing, use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(
        "Processing order",
        extra={
            'order_id': order.id,
            'user_id': order.user_id,
            'amount': float(order.total),
            'items_count': order.items.count(),
        }
    )
```

**With JSON formatter** (requires `python-json-logger`):
```json
{
  "asctime": "2025-01-15 10:30:45",
  "name": "myapp.orders",
  "levelname": "INFO",
  "message": "Processing order",
  "order_id": 123,
  "user_id": 456,
  "amount": 99.99,
  "items_count": 3
}
```

---

### Request Logging

Log all requests (automatically via `django.request` logger):

**Automatic logging**:
- 4xx errors: WARNING level
- 5xx errors: ERROR level

**Custom middleware for additional logging**:

```python
# myapp/middleware.py
import logging
import time

logger = logging.getLogger('requests')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        logger.info(
            f"{request.method} {request.path} {response.status_code}",
            extra={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': duration,
                'user': request.user.username if request.user.is_authenticated else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR'),
            }
        )

        return response
```

**Register middleware**:
```python
# config/settings.py
MIDDLEWARE = [
    'myapp.middleware.RequestLoggingMiddleware',
    # ... other middleware
]
```

---

### Security-Sensitive Logging

**Never log**:
- Passwords
- API tokens/keys
- Credit card numbers
- Personal identification numbers
- Session IDs

**Bad**:
```python
logger.info(f"User login: {username}, password: {password}")  # NEVER DO THIS
logger.debug(f"API request with token: {api_token}")  # NEVER DO THIS
```

**Good**:
```python
logger.info(f"User login attempt: {username}")
logger.debug(f"API request with token: {'*' * 20}")  # Masked
```

---

## Viewing Logs

### Docker Logs

All application logs go to Docker stdout:

```bash
# View all logs
docker-compose logs

# Follow logs (live tail)
docker-compose logs -f

# Logs for specific service
docker-compose logs web
docker-compose logs db

# Last N lines
docker-compose logs --tail 100 web

# Logs since timestamp
docker-compose logs --since 2025-01-15T10:00:00

# Logs with timestamps
docker-compose logs -t
```

---

### Filtering Logs

```bash
# Show only errors
docker-compose logs web | grep ERROR

# Show specific module
docker-compose logs web | grep "myapp.orders"

# Show specific user activity
docker-compose logs web | grep "user_id=123"
```

---

### Production Log Management

In production, logs should be sent to external service for:
- Long-term storage
- Search and filtering
- Alerting
- Visualization

**Options**:
1. **CloudWatch** (AWS)
2. **Datadog**
3. **Papertrail**
4. **Loggly**
5. **Elasticsearch + Kibana** (self-hosted)

---

## Log Aggregation

### Docker Logging Drivers

Configure in `docker-compose.yml`:

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Drivers available**:
- `json-file` (default) - Logs to JSON files
- `syslog` - Send to syslog
- `journald` - systemd journal
- `awslogs` - AWS CloudWatch
- `splunk` - Splunk

---

### JSON Logging for Production

For structured logging, use JSON format:

**Install**:
```bash
# Add to requirements.txt
python-json-logger==2.0.7
```

**Configure**:
```python
LOGGING = {
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    # ... rest of config
}
```

**Output**:
```json
{"asctime": "2025-01-15 10:30:45", "name": "myapp", "levelname": "INFO", "message": "Order processed"}
```

**Benefits**:
- Easy to parse programmatically
- Works well with log aggregation tools
- Structured data for filtering

---

## Database Query Logging

**Enable SQL logging** (development only):

```python
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

**Output**:
```
(0.001) SELECT * FROM auth_user WHERE id = 1; args=(1,)
```

**Warning**: Very verbose, use only for debugging

**Production alternative**: Use Django Debug Toolbar or django-silk

---

## Performance Logging

Log slow requests:

```python
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')

class SlowRequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            if duration > 1.0:  # Log if request took > 1 second
                logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration:.2f}s",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'status_code': response.status_code,
                    }
                )
        return response
```

---

## Log Rotation

### Docker JSON Logs

Configure max size and file count:

```yaml
services:
  web:
    logging:
      options:
        max-size: "10m"
        max-file: "3"
```

This keeps up to 3 files of 10MB each (30MB total).

---

### File-Based Logs

If using file handler:

```python
'handlers': {
    'file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/app/logs/django.log',
        'maxBytes': 1024 * 1024 * 10,  # 10MB
        'backupCount': 5,  # Keep 5 backup files
    },
}
```

**Creates**:
- `django.log` (current)
- `django.log.1` (oldest)
- `django.log.2`
- ...
- `django.log.5` (newest backup)

---

## Monitoring and Alerting

### What to Monitor

1. **Error rate**: Spike in 5xx errors
2. **Warning rate**: Unusual warnings
3. **Response time**: Slow requests
4. **User activity**: Login failures, suspicious patterns

---

### Alerting Examples

**With CloudWatch** (AWS):
- Alert when error rate > 10/min
- Alert when response time > 5s

**With Datadog**:
- Create monitor for log pattern
- Alert on specific error messages

**With Sentry**:
- Automatic error grouping
- Email/Slack alerts for new errors

---

## Log Analysis

### Common Log Queries

```bash
# Count errors in last hour
docker-compose logs --since 1h web | grep ERROR | wc -l

# Find all 500 errors
docker-compose logs web | grep "Internal Server Error"

# Find specific user activity
docker-compose logs web | grep "user_id=123"

# Most common errors
docker-compose logs web | grep ERROR | sort | uniq -c | sort -rn
```

---

### Tools

**Local development**:
- `grep`, `awk`, `sed`
- `jq` for JSON logs

**Production**:
- Kibana (Elasticsearch)
- CloudWatch Insights
- Datadog Logs
- Splunk

---

## Testing Logging

Verify logging in tests:

```python
import logging
from django.test import TestCase

class LoggingTest(TestCase):
    def test_logging_on_error(self):
        with self.assertLogs('myapp', level='ERROR') as cm:
            # Trigger error
            process_order(invalid_order)

        # Verify log message
        self.assertIn('Payment failed', cm.output[0])
```

---

## Best Practices

1. **Use logger per module**:
   ```python
   logger = logging.getLogger(__name__)
   ```

2. **Include context**:
   ```python
   logger.error(f"Failed to process order {order.id}", extra={'order_id': order.id})
   ```

3. **Use appropriate level**:
   - Don't log INFO as ERROR
   - Don't log DEBUG in production

4. **Log exceptions with traceback**:
   ```python
   logger.error("Error occurred", exc_info=True)
   ```

5. **Don't log in loops** (performance impact):
   ```python
   # Bad
   for item in items:
       logger.debug(f"Processing {item}")  # Too verbose

   # Good
   logger.info(f"Processing {len(items)} items")
   ```

6. **Use lazy formatting**:
   ```python
   # Good (string formatted only if logged)
   logger.debug("User %s logged in", username)

   # Less good (always formats string)
   logger.debug(f"User {username} logged in")
   ```

---

Last Updated: 2025-12-21
