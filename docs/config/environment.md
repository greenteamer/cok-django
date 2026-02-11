# Environment Configuration

This document defines all environment variables used by the application.

## Overview

Configuration is managed via environment variables following 12-factor app principles.

**Configuration File**: `.env` (loaded by python-decouple)

**Template**: `.env.example`

**Loading Mechanism**: `python-decouple` library reads `.env` and provides defaults

## Environment Variables Reference

### Django Core Settings

#### SECRET_KEY

**Type**: String

**Required**: Yes (in production)

**Default**: `'django-insecure-change-this-in-production'` (development only)

**Purpose**: Cryptographic signing key for sessions, cookies, CSRF tokens

**Example**:
```bash
SECRET_KEY=your-secret-key-here-change-in-production
```

**Production Value**:
Generate a secure random key:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Security**: NEVER commit this to version control. Treat as a password.

---

#### DEBUG

**Type**: Boolean

**Required**: No

**Default**: `False`

**Purpose**: Enable/disable debug mode

**Example**:
```bash
DEBUG=False
```

**Valid Values**: `True`, `False`, `1`, `0`, `true`, `false`

**Behavior**:
- `DEBUG=True`:
  - Detailed error pages with tracebacks
  - WhiteNoise serves static files
  - Security settings disabled
  - NOT FOR PRODUCTION

- `DEBUG=False`:
  - Generic error pages
  - Security middleware enabled
  - Static files must be served by Nginx
  - REQUIRED FOR PRODUCTION

**Security**: ALWAYS set to `False` in production.

---

#### ALLOWED_HOSTS

**Type**: Comma-separated string

**Required**: Yes (when DEBUG=False)

**Default**: `'localhost,127.0.0.1'`

**Purpose**: Hostnames that Django will serve (prevents Host header attacks)

**Example**:
```bash
ALLOWED_HOSTS=localhost,127.0.0.1,coreofkeen.com,www.coreofkeen.com
```

**Production Value**:
- Include your domain(s)
- Include server IP if accessing directly
- Include `localhost` only if needed for local access

**Security**: Prevents DNS rebinding and Host header injection attacks.

---

### Database Settings

All database settings are passed to PostgreSQL container and Django.

#### DB_NAME

**Type**: String

**Required**: No

**Default**: `'django_db'`

**Purpose**: PostgreSQL database name

**Example**:
```bash
DB_NAME=django_db
```

---

#### DB_USER

**Type**: String

**Required**: No

**Default**: `'django_user'`

**Purpose**: PostgreSQL username

**Example**:
```bash
DB_USER=django_user
```

---

#### DB_PASSWORD

**Type**: String

**Required**: Yes (in production)

**Default**: `'password'` (insecure default for development)

**Purpose**: PostgreSQL password

**Example**:
```bash
DB_PASSWORD=strong_password_here
```

**Production Value**:
Generate a strong random password:
```bash
openssl rand -base64 32
```

**Security**: NEVER use default password in production.

---

#### DB_HOST

**Type**: String

**Required**: No

**Default**: `'db'` (Docker Compose service name)

**Purpose**: PostgreSQL hostname

**Example**:
```bash
DB_HOST=db
```

**Values**:
- `db` - Docker Compose service name (default)
- External hostname if using managed database (RDS, etc.)

---

#### DB_PORT

**Type**: Integer

**Required**: No

**Default**: `5432`

**Purpose**: PostgreSQL port

**Example**:
```bash
DB_PORT=5432
```

---

### Startup Settings

#### DB_WAIT_TIMEOUT

**Type**: Integer (seconds)

**Required**: No

**Default**: `30`

**Purpose**: Maximum time (in seconds) the entrypoint script waits for PostgreSQL to become available before exiting with an error. Prevents infinite container hang when the database is unreachable.

**Example**:
```bash
DB_WAIT_TIMEOUT=30
```

**Behavior**:
- If PostgreSQL responds within the timeout, startup continues normally
- If PostgreSQL does not respond, the container exits with code 1 and logs a clear error message
- On Railway, this allows the orchestrator to detect the failure and restart the container

**When to adjust**: Increase if your database takes longer to start (e.g., after large migrations or restores). Decrease for faster failure detection.

---

## Environment Profiles

### Development Environment

Recommended `.env` for local development:

```bash
# Django settings
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

**Characteristics**:
- Debug mode enabled
- Insecure defaults acceptable
- Detailed error messages
- WhiteNoise serves static files

---

### Production Environment

Recommended `.env` for production:

```bash
# Django settings
SECRET_KEY=<generate-with-get_random_secret_key>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,coreofkeen.com,www.coreofkeen.com

# Database settings
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=<generate-strong-random-password>
DB_HOST=db
DB_PORT=5432
```

**Characteristics**:
- Debug mode disabled
- Strong secrets
- Security middleware enabled
- Nginx serves static files

**Security Checklist**:
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] Strong `DB_PASSWORD` (20+ random characters)
- [ ] Correct `ALLOWED_HOSTS` (no wildcards)
- [ ] `.env` file not in version control
- [ ] `.env` file permissions: `chmod 600 .env`

---

## Configuration Loading

### How Configuration is Loaded

1. **Docker Compose** reads `.env` and passes to containers
2. **Dockerfile** sets environment variables in container
3. **Django settings.py** uses `python-decouple` to read variables
4. **Fallback** to default values if variable not set

### Code Example

From `config/settings.py`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

**Behavior**:
- `config('KEY')` - Reads `KEY` from environment or `.env` file
- `default='value'` - Use this value if not set
- `cast=bool` - Convert string to boolean

---

## Environment Variable Precedence

Configuration is resolved in this order (highest to lowest priority):

1. **Container environment variables** (set by Docker at runtime)
2. **`.env` file** (loaded by docker-compose)
3. **Default values** in `settings.py`

**Example**:
```bash
# In .env file
DEBUG=True

# In shell
export DEBUG=False

# Result: DEBUG=False (shell variable wins)
```

---

## Configuration Validation

### Startup Validation

Django validates configuration on startup:

1. **SECRET_KEY**: Warns if using default in production
2. **ALLOWED_HOSTS**: Must be set if `DEBUG=False`
3. **Database connection**: Fails if cannot connect

### Manual Validation

Check configuration:
```bash
docker-compose exec web python manage.py check --deploy
```

This runs Django's deployment checklist and warns about:
- Security settings
- Middleware configuration
- Database settings

---

## Security Best Practices

### Secret Management

1. **Never commit `.env` to version control**
   - `.env` is in `.gitignore`
   - Use `.env.example` as template

2. **Use strong random values**
   - `SECRET_KEY`: 50+ characters
   - `DB_PASSWORD`: 20+ characters
   - Use cryptographically secure random generator

3. **Rotate secrets regularly**
   - Change `SECRET_KEY` invalidates all sessions
   - Change `DB_PASSWORD` requires container restart

4. **Limit access to `.env` file**
   ```bash
   chmod 600 .env
   chown <app-user>:<app-group> .env
   ```

### Production Hardening

1. **Set restrictive `ALLOWED_HOSTS`**
   - Never use `*` wildcard
   - List only your actual domains

2. **Enable all security settings**
   - Automatic when `DEBUG=False`
   - See `security/overview.md`

3. **Use HTTPS only**
   - Cloudflare SSL mode: "Full (strict)"
   - Let's Encrypt certificate on origin server

---

## Troubleshooting

### Issue: "DisallowedHost" error

**Cause**: Request Host header not in `ALLOWED_HOSTS`

**Solution**: Add the hostname to `ALLOWED_HOSTS`

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

---

### Issue: Database connection refused

**Cause**: `DB_HOST` or `DB_PORT` incorrect, or database not running

**Solution**:
1. Check database is running: `docker-compose ps`
2. Verify `DB_HOST=db` (Docker service name)
3. Check logs: `docker-compose logs db`

---

### Issue: Static files not loading (404)

**Cause**: `DEBUG=False` but Nginx not serving static files

**Solution**:
1. Run `make collectstatic`
2. Copy to Nginx directory: `sudo cp -r staticfiles /var/www/coreofkeen.com/`
3. Check Nginx config points to correct path

---

### Issue: Infinite redirect loop

**Cause**: Cloudflare SSL mode misconfigured

**Solution**:
1. Set Cloudflare SSL/TLS mode to **"Full (strict)"**
2. Ensure Let's Encrypt certificate installed on server
3. Check `SECURE_PROXY_SSL_HEADER` in settings

---

## Adding New Configuration

To add a new environment variable:

1. **Add to `.env.example`** with example/default value
2. **Document in this file** (follow format above)
3. **Add to `settings.py`** with `config()`
4. **Update affected documentation**

**Example**:

```python
# In settings.py
EMAIL_HOST = config('EMAIL_HOST', default='localhost')

# In .env.example
EMAIL_HOST=smtp.example.com

# In this document
#### EMAIL_HOST
**Type**: String
**Required**: No
**Default**: `'localhost'`
**Purpose**: SMTP server hostname for sending email
```

---

## Environment Variables Not Used (Yet)

These variables may be added in the future:

- `REDIS_URL` - Redis connection string (for caching)
- `CELERY_BROKER_URL` - Message broker for background tasks
- `AWS_ACCESS_KEY_ID` - AWS credentials for S3 storage
- `SENTRY_DSN` - Error tracking with Sentry
- `EMAIL_HOST`, `EMAIL_PORT` - Email configuration

When adding these, update this document and `docs/README.md`.

---

Last Updated: 2026-02-12
