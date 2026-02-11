# Security Overview

This document describes the security model, threat assumptions, and security measures implemented in the project.

## Security Model

### Trust Boundaries

```
[Untrusted]           [Trusted]
Internet → Cloudflare → Nginx → Django → PostgreSQL
           [CDN/DDoS]   [Proxy] [App]    [Data]
```

**Untrusted Zone**: Internet, user browsers, potential attackers

**Trusted Zone**: Internal Docker network, application containers

---

## Security Measures

### 1. HTTPS/SSL Enforcement

**Production Configuration** (when `DEBUG=False`):

```python
# config/settings.py
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^health/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

**What this does**:
- `SECURE_PROXY_SSL_HEADER`: Trust `X-Forwarded-Proto` header from Nginx/Railway
- `SECURE_SSL_REDIRECT`: Redirect all HTTP requests to HTTPS
- `SECURE_REDIRECT_EXEMPT`: Skip SSL redirect for `/health/` (required for Railway health checks which use internal HTTP)
- `SESSION_COOKIE_SECURE`: Session cookies only sent over HTTPS
- `CSRF_COOKIE_SECURE`: CSRF cookies only sent over HTTPS

**Requirements**:
- Nginx configured with SSL certificate
- Cloudflare SSL mode: "Full (strict)"

**Protection against**:
- Man-in-the-middle attacks
- Session hijacking
- Cookie theft

**Middleware Exemptions**:

The `/health/` endpoint is exempt from SSL redirect and canonical host redirect. Railway (and other orchestrators) send internal health check requests over HTTP with internal hostnames. Without exemptions, these requests receive 301 redirects instead of 200 OK, causing health checks to fail.

- `SECURE_REDIRECT_EXEMPT = [r"^health/$"]` — skips SSL redirect for `/health/`
- `CanonicalHostMiddleware.EXEMPT_PATHS = ["/health/"]` — skips host redirect for `/health/`

This is safe because the health check endpoint returns only application status (no sensitive data).

---

### 2. Security Headers

**Configured in settings** (when `DEBUG=False`):

```python
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

**Headers sent**:

#### X-XSS-Protection

```
X-XSS-Protection: 1; mode=block
```

**Protection**: Cross-site scripting (XSS) attacks

**Behavior**: Browser blocks page if XSS detected

---

#### X-Content-Type-Options

```
X-Content-Type-Options: nosniff
```

**Protection**: MIME type sniffing attacks

**Behavior**: Browser doesn't guess content type, uses declared type

---

#### X-Frame-Options

```
X-Frame-Options: DENY
```

**Protection**: Clickjacking attacks

**Behavior**: Page cannot be embedded in iframe

**Alternative**: `SAMEORIGIN` (allow same-origin frames)

---

### 3. CSRF Protection

**Enabled by default** via `CsrfViewMiddleware`

**How it works**:
1. Server generates CSRF token for each session
2. Token stored in cookie and included in forms
3. POST/PUT/DELETE requests must include valid token
4. Server validates token on submission

**In templates**:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**For AJAX**:
```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Include in AJAX request headers
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
});
```

**Protection against**: Cross-site request forgery

---

### 4. Password Security

**Django's built-in password hashers** (in order of preference):

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Default
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

**Default**: PBKDF2 with SHA256

**Characteristics**:
- Passwords are never stored in plaintext
- Hash includes random salt (prevents rainbow table attacks)
- Computationally expensive (prevents brute force)

**Password Validators** (configured in settings):

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

**Requirements**:
- Not too similar to username/email
- At least 8 characters
- Not in common password list
- Not entirely numeric

---

### 5. SQL Injection Protection

**Django ORM parameterizes all queries**:

**Safe** (parameterized):
```python
User.objects.filter(username=user_input)
# SQL: SELECT * FROM auth_user WHERE username = %s
# Parameters: [user_input]
```

**Dangerous** (avoid raw SQL):
```python
# DON'T DO THIS
User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{user_input}'")
```

**If raw SQL is necessary**:
```python
# Use parameterization
User.objects.raw("SELECT * FROM auth_user WHERE username = %s", [user_input])
```

**Protection against**: SQL injection attacks

---

### 6. XSS Protection

**Django templates auto-escape HTML**:

```html
<!-- Variable contains: <script>alert('XSS')</script> -->
{{ user_input }}
<!-- Rendered as: &lt;script&gt;alert('XSS')&lt;/script&gt; -->
```

**Manual escaping** (if needed):
```python
from django.utils.html import escape
safe_text = escape(user_input)
```

**Mark as safe** (only for trusted content):
```html
{{ trusted_html|safe }}
```

**In JSON**:
```python
from django.utils.html import json_script

# In view
context = {'data': user_data}

# In template
{{ data|json_script:"user-data" }}
<script>
    const userData = JSON.parse(document.getElementById('user-data').textContent);
</script>
```

**Protection against**: Cross-site scripting (XSS) attacks

---

### 7. Session Security

**Session configuration**:

```python
# Production settings
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access (default)
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection (default)
SESSION_COOKIE_AGE = 1209600      # 2 weeks (default)
```

**Session storage**: PostgreSQL database (`django_session` table)

**Session expiration**: 2 weeks of inactivity

**Session invalidation**:
```python
# Logout (deletes session)
from django.contrib.auth import logout
logout(request)

# Change password (invalidates all sessions)
user.set_password(new_password)
user.save()
```

**Protection against**:
- Session hijacking
- Session fixation
- CSRF attacks

---

### 8. File Upload Security

**Current state**: No file upload functionality implemented

**When implementing file uploads**:

1. **Validate file type**:
   ```python
   from django.core.exceptions import ValidationError

   def validate_file_extension(value):
       valid_extensions = ['.jpg', '.png', '.pdf']
       if not value.name.endswith(tuple(valid_extensions)):
           raise ValidationError('Invalid file type')
   ```

2. **Limit file size**:
   ```python
   # In Nginx config
   client_max_body_size 100M;

   # In Django
   DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
   ```

3. **Store outside web root**:
   ```python
   MEDIA_ROOT = BASE_DIR / 'media'  # Not in static/
   ```

4. **Serve with X-Sendfile** (Nginx handles file serving):
   ```python
   # Don't serve files directly from Django in production
   ```

5. **Scan for malware** (production):
   - Integrate with antivirus API (ClamAV, VirusTotal)

---

### 9. Authentication Security

**Brute Force Protection**: Not currently implemented

**Recommendation**: Add django-axes or django-ratelimit

**Installation**:
```bash
# Add to requirements.txt
django-axes==6.1.1
```

**Configuration**:
```python
# config/settings.py
INSTALLED_APPS = [
    'axes',
    # ...
]

MIDDLEWARE = [
    'axes.middleware.AxesMiddleware',
    # ... after AuthenticationMiddleware
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',  # Should be first
    'django.contrib.auth.backends.ModelBackend',
]

# Lock after 5 failed attempts for 1 hour
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
```

---

### 10. Admin Interface Security

**Default Django Admin**: `/admin/`

**Security measures**:
1. **Require authentication**: Only logged-in users
2. **Require staff status**: `is_staff=True`
3. **Permissions**: Fine-grained permissions per model

**Additional recommendations**:

1. **Change admin URL**:
   ```python
   # config/urls.py
   urlpatterns = [
       path('secret-admin/', admin.site.urls),  # Not 'admin/'
   ]
   ```

2. **Enable two-factor authentication**:
   ```bash
   # Add to requirements.txt
   django-otp==1.3.0
   qrcode==7.4.2
   ```

3. **Log admin actions**:
   - Django logs all admin actions by default
   - View in `django_admin_log` table

---

## Secrets Management

### Environment Variables

**All secrets in `.env` file**:
```bash
SECRET_KEY=<random-50-chars>
DB_PASSWORD=<random-20-chars>
```

**Security checklist**:
- [ ] `.env` in `.gitignore` (never committed)
- [ ] Strong random secrets in production
- [ ] File permissions: `chmod 600 .env`
- [ ] Rotate secrets regularly

**Generate secrets**:
```bash
# SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# DB_PASSWORD
openssl rand -base64 32
```

---

### Secret Rotation

**When to rotate**:
- Suspected compromise
- Employee departure
- Regular schedule (quarterly)

**Process**:
1. Generate new secret
2. Update `.env` file
3. Restart containers: `docker-compose restart`

**Note**: Rotating `SECRET_KEY` invalidates all sessions (users must re-login)

---

## Dependency Security

### Keeping Dependencies Updated

**Check for vulnerabilities**:
```bash
# Install safety
pip install safety

# Check requirements.txt
safety check -r requirements.txt
```

**Update dependencies**:
```bash
# Update specific package
pip install --upgrade Django

# Update requirements.txt
pip freeze > requirements.txt

# Rebuild container
docker-compose up --build -d
```

**Automate** (GitHub Dependabot):
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Network Security

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**Block database port** from external access:
```bash
# Database should only be accessible from Docker network
# Don't expose port 5432 externally
```

In `docker-compose.yml` (production):
```yaml
db:
  # Remove or comment out:
  # ports:
  #   - "5432:5432"
```

---

### Docker Network Isolation

Containers communicate via internal Docker network.

**Security**:
- `db` container not accessible from internet
- Only `web` container exposes port 8000 (proxied by Nginx)

---

## Database Security

### Connection Security

**Current**: No SSL between Django and PostgreSQL (same Docker network)

**For external database** (AWS RDS, etc.):
```python
DATABASES = {
    'default': {
        # ... other settings
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

---

### Database Permissions

**Principle of least privilege**:
- Django user has full access to application database
- Django user has NO access to PostgreSQL system tables
- Django user has NO superuser privileges

---

## Monitoring and Auditing

### Security Events to Monitor

1. **Failed login attempts**
   - Multiple failures from same IP
   - Potential brute force attack

2. **Unusual database queries**
   - Large number of queries
   - Slow queries

3. **Error spikes**
   - Sudden increase in 4xx/5xx errors

4. **File access**
   - Unauthorized file access attempts

---

### Audit Logging

**Django Admin Logs** (built-in):
- All admin actions logged to `django_admin_log` table
- Includes user, action, object, timestamp

**Custom audit logging**:
```python
import logging

audit_logger = logging.getLogger('audit')

def sensitive_action(request):
    # Perform action
    audit_logger.info(
        f"User {request.user.username} performed sensitive action",
        extra={
            'user': request.user.id,
            'ip': request.META.get('REMOTE_ADDR'),
            'action': 'sensitive_action',
        }
    )
```

---

## Compliance

### GDPR Considerations

If handling EU user data:

1. **Data minimization**: Only collect necessary data
2. **User consent**: Explicit consent for data processing
3. **Right to access**: Users can request their data
4. **Right to deletion**: Users can request data deletion
5. **Data portability**: Export user data in standard format
6. **Privacy policy**: Clear privacy policy

**Django tools**:
- `django-gdpr-assist` - GDPR compliance helpers
- Data export views
- Anonymization utilities

---

## Security Checklist

### Development

- [ ] `DEBUG=True` (for development only)
- [ ] Weak secrets OK (not for production)
- [ ] HTTPS not required

---

### Production

**Configuration**:
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] Strong `DB_PASSWORD` (20+ random characters)
- [ ] `ALLOWED_HOSTS` set correctly (no wildcards)
- [ ] All security middleware enabled

**HTTPS**:
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Cloudflare SSL mode: "Full (strict)"
- [ ] HTTP redirects to HTTPS
- [ ] Secure cookies enabled

**Access Control**:
- [ ] Admin URL changed from `/admin/`
- [ ] Strong admin passwords
- [ ] SSH key-based auth (no password auth)
- [ ] Firewall configured (UFW)

**Dependencies**:
- [ ] No known vulnerabilities (`safety check`)
- [ ] Dependencies up to date
- [ ] Regular update schedule

**Monitoring**:
- [ ] Error tracking configured (Sentry)
- [ ] Log monitoring
- [ ] Failed login alerts

**Backups**:
- [ ] Database backups automated
- [ ] Backups tested (restore works)
- [ ] Backup retention policy

---

## Incident Response

If security breach suspected:

1. **Contain**:
   - Take affected system offline
   - Change all credentials
   - Block attacker IP

2. **Investigate**:
   - Review logs
   - Identify vulnerability
   - Assess data exposure

3. **Remediate**:
   - Patch vulnerability
   - Restore from clean backup if needed
   - Reset all user passwords

4. **Document**:
   - Incident report
   - Lessons learned
   - Update security procedures

---

Last Updated: 2025-12-21
