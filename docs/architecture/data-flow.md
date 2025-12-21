# Data Flow

This document describes how data moves through the system at runtime.

## HTTP Request Flow

### Production Request Flow

```
1. User Browser
   │
   │ HTTPS Request
   ▼
2. Cloudflare CDN
   │ - DDoS protection
   │ - SSL/TLS termination (to Cloudflare)
   │ - SSL/TLS encryption (to origin)
   │
   │ HTTPS Request
   ▼
3. Nginx (Host)
   │ - SSL/TLS termination (from Cloudflare)
   │ - Request routing
   │ - Static file serving (if /static/ or /media/)
   │
   ├─▶ Static Files (if path matches /static/ or /media/)
   │   - Serve from /var/www/coreofkeen.com/staticfiles/
   │   - Return to user
   │
   │ HTTP Request (if dynamic)
   ▼
4. Gunicorn (Container: web)
   │ - Worker selection (round-robin)
   │ - HTTP to WSGI translation
   │
   │ WSGI Call
   ▼
5. Django Middleware Stack
   │ - SecurityMiddleware
   │ - WhiteNoiseMiddleware (only if DEBUG=True)
   │ - SessionMiddleware
   │ - CommonMiddleware
   │ - CsrfViewMiddleware
   │ - AuthenticationMiddleware
   │ - MessageMiddleware
   │ - ClickjackingMiddleware
   │
   │ Request Object
   ▼
6. URL Resolver (config/urls.py)
   │ - Pattern matching
   │ - View function lookup
   │
   │ Matched View
   ▼
7. View Function
   │ - Business logic
   │ - Database queries
   │ - Template rendering
   │
   │ SQL Queries (if needed)
   ▼
8. Django ORM
   │ - Query construction
   │ - Query optimization
   │
   │ SQL over TCP (port 5432)
   ▼
9. PostgreSQL (Container: db)
   │ - Query parsing
   │ - Query execution
   │ - Transaction management
   │
   │ Query Results
   ▼
10. View Function (continued)
    │ - Process results
    │ - Render template or serialize data
    │
    │ Response Object
    ▼
11. Django Middleware Stack (response phase)
    │ - MessageMiddleware
    │ - SessionMiddleware (set cookie)
    │ - SecurityMiddleware (set headers)
    │
    │ HTTP Response
    ▼
12. Gunicorn
    │ - WSGI to HTTP translation
    │
    │ HTTP Response
    ▼
13. Nginx
    │ - Add proxy headers
    │ - Compression (if enabled)
    │
    │ HTTP Response
    ▼
14. Cloudflare
    │ - Caching (if enabled)
    │ - Minification
    │ - SSL/TLS encryption
    │
    │ HTTPS Response
    ▼
15. User Browser
```

### Development Request Flow

```
1. User Browser
   │
   │ HTTP Request (localhost:8000)
   ▼
2. Gunicorn (Container: web)
   │ - Worker selection
   │ - HTTP to WSGI translation
   │
   ▼
3. Django Middleware Stack
   │ - All middleware including WhiteNoiseMiddleware
   │
   ▼
4. [Same as production from step 6 onwards]
```

**Key Difference**: In development:
- No Nginx (direct access to Gunicorn)
- No Cloudflare
- WhiteNoise serves static files
- DEBUG=True enables additional middleware and error pages

## Static File Flow

### Development (DEBUG=True)

```
Request: /static/admin/css/base.css
   ▼
WhiteNoiseMiddleware
   │ - Check if path starts with STATIC_URL (/static/)
   │ - Locate file in STATIC_ROOT (staticfiles/)
   │ - Serve file directly
   ▼
Response: 200 OK with CSS content
```

### Production (DEBUG=False)

```
Request: /static/admin/css/base.css
   ▼
Nginx
   │ - Match location /static/
   │ - Serve from /var/www/coreofkeen.com/staticfiles/
   │ - Never reaches Django
   ▼
Response: 200 OK with CSS content
```

**Performance**: Nginx serves static files 10-100x faster than Django.

## Media File Upload Flow

```
1. User submits form with file upload
   │
   │ POST /upload/ (multipart/form-data)
   ▼
2. Nginx
   │ - client_max_body_size 100M (size limit)
   │ - Proxy to Gunicorn
   │
   ▼
3. Django View
   │ - request.FILES['uploaded_file']
   │ - File validation
   │ - Save file
   │
   ▼
4. FileField.save()
   │ - Generate unique filename
   │ - Write to MEDIA_ROOT (/app/media/)
   │
   ▼
5. Django ORM
   │ - Save file path to database
   │
   │ SQL INSERT
   ▼
6. PostgreSQL
   │ - Store metadata (file path, not file content)
   │
   ▼
7. Response to user with success message
```

**File Storage**:
- Files are stored in `/app/media/` inside container
- File paths are stored in database
- For production, should use object storage (S3, etc.)

## Database Query Flow

### Simple Query

```python
# View code
users = User.objects.filter(is_active=True)
```

```
1. Django ORM QuerySet
   │ - Lazy evaluation (no SQL yet)
   │
   │ users.count() or list(users)
   ▼
2. Django ORM Compiler
   │ - Build SQL query
   │ - Apply filters, ordering
   │
   │ SQL: SELECT * FROM auth_user WHERE is_active = true
   ▼
3. psycopg2 Adapter
   │ - Connection pooling
   │ - Query parameterization
   │
   │ TCP connection to db:5432
   ▼
4. PostgreSQL
   │ - Parse query
   │ - Query planner
   │ - Execute
   │
   │ Result set
   ▼
5. psycopg2
   │ - Fetch rows
   │ - Type conversion
   │
   ▼
6. Django ORM
   │ - Hydrate model instances
   │ - Return QuerySet
   │
   ▼
7. View code continues with user objects
```

### Transaction Flow

```python
from django.db import transaction

with transaction.atomic():
    user.save()
    profile.save()
```

```
1. transaction.atomic() enter
   │
   │ BEGIN TRANSACTION
   ▼
2. PostgreSQL
   │ - Start transaction
   │
   ▼
3. user.save()
   │ - SQL INSERT/UPDATE
   │ - Transaction not committed
   │
   ▼
4. profile.save()
   │ - SQL INSERT/UPDATE
   │ - Transaction not committed
   │
   ▼
5. transaction.atomic() exit (no exception)
   │
   │ COMMIT
   ▼
6. PostgreSQL
   │ - Commit transaction
   │ - Changes are permanent
```

**On Exception**:
```
5. transaction.atomic() exit (exception raised)
   │
   │ ROLLBACK
   ▼
6. PostgreSQL
   │ - Rollback transaction
   │ - Changes are discarded
```

## Session Management Flow

### Session Read (Request)

```
1. Request arrives with Cookie: sessionid=abc123
   │
   ▼
2. SessionMiddleware (process_request)
   │ - Extract sessionid from cookie
   │
   │ SQL: SELECT * FROM django_session WHERE session_key = 'abc123'
   ▼
3. PostgreSQL
   │ - Return session data (pickled Python dict)
   │
   ▼
4. SessionMiddleware
   │ - Unpickle session data
   │ - Attach to request.session
   │
   ▼
5. View code
   │ - Can read/write request.session['key']
```

### Session Write (Response)

```
1. View modifies request.session['cart'] = [...]
   │
   ▼
2. SessionMiddleware (process_response)
   │ - Check if session was modified
   │ - Pickle session data
   │
   │ SQL: UPDATE django_session SET session_data = '...', expire_date = '...'
   ▼
3. PostgreSQL
   │ - Update session row
   │
   ▼
4. SessionMiddleware
   │ - Set sessionid cookie in response
   │
   ▼
5. Response to client with Set-Cookie header
```

## Authentication Flow

### Login Flow

```
1. User submits login form
   │ POST /admin/login/
   │ username=admin, password=secret
   ▼
2. Django View (django.contrib.auth.views.LoginView)
   │ - Validate CSRF token
   │ - Authenticate user
   │
   │ SQL: SELECT * FROM auth_user WHERE username = 'admin'
   ▼
3. PostgreSQL
   │ - Return user row (hashed password)
   │
   ▼
4. Django authenticate()
   │ - Check password hash (bcrypt)
   │ - Return User object or None
   │
   ▼
5. Django login()
   │ - Create session
   │ - Set request.session['_auth_user_id'] = user.id
   │
   │ SQL: INSERT INTO django_session (...)
   ▼
6. PostgreSQL
   │ - Store session
   │
   ▼
7. Response with sessionid cookie
   │ Set-Cookie: sessionid=xyz789
   ▼
8. User browser stores cookie
```

### Authenticated Request

```
1. Request with Cookie: sessionid=xyz789
   │
   ▼
2. SessionMiddleware
   │ - Load session from database
   │ - request.session['_auth_user_id'] = 1
   │
   ▼
3. AuthenticationMiddleware
   │ - Read user ID from session
   │
   │ SQL: SELECT * FROM auth_user WHERE id = 1
   ▼
4. PostgreSQL
   │ - Return user row
   │
   ▼
5. AuthenticationMiddleware
   │ - Attach user to request.user
   │
   ▼
6. View code
   │ - Access request.user
   │ - Check permissions
```

## Error Flow

### Application Error (500)

```
1. View raises Exception
   │
   ▼
2. Middleware catches exception
   │
   ▼
3. Django Error Handler
   │ - Log error to stdout
   │ - Render error page
   │   - DEBUG=True: Full traceback
   │   - DEBUG=False: Generic 500 page
   │
   ▼
4. Response 500 Internal Server Error
```

### Database Error

```
1. View executes query
   │
   ▼
2. Django ORM
   │ - SQL query
   │
   ▼
3. PostgreSQL unavailable or error
   │ - Connection refused
   │ - Or SQL syntax error
   │
   ▼
4. psycopg2 raises DatabaseError
   │
   ▼
5. Django Error Handler
   │ - Log error
   │ - Return 500 (or retry if connection pool)
```

See `runtime/error-handling.md` for error handling strategies.

## Container Startup Flow

See `runtime/lifecycle.md` for detailed container startup sequence.

```
1. docker-compose up
   │
   ▼
2. Start db container
   │ - PostgreSQL initialization
   │
   ▼
3. Start web container
   │ - Run entrypoint.sh
   │ - Wait for database (nc -z db 5432)
   │ - Run migrations
   │ - Collect static files
   │ - Start Gunicorn
   │
   ▼
4. System ready to accept requests
```

## Data Persistence

### Persistent Data

Data that survives container restarts:

1. **PostgreSQL Data**: `/var/lib/postgresql/data` (Docker volume `postgres_data`)
2. **Static Files**: `/var/www/coreofkeen.com/staticfiles/` (host filesystem)
3. **Media Files**: `/var/www/coreofkeen.com/media/` (host filesystem)

### Ephemeral Data

Data lost on container restart:

1. **Application Code**: Re-copied from host (dev) or image (prod)
2. **Log Files**: Logged to stdout (captured by Docker or external logging)
3. **Temp Files**: Any files in `/tmp` or `/app` (except volumes)

## Logging Flow

```
1. Django code
   │ - logger.info('message')
   │
   ▼
2. Python logging module
   │ - Format message
   │
   ▼
3. StreamHandler (stdout)
   │
   ▼
4. Docker captures stdout
   │ - docker logs <container>
   │
   ▼
5. Host log driver
   │ - json-file (default)
   │ - Or external logging (syslog, etc.)
```

**Production Consideration**: Use external log aggregation (CloudWatch, Datadog, etc.)

See `ops/logging.md` for logging configuration.

---

Last Updated: 2025-12-21
