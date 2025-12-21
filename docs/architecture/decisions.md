# Architecture Decision Records (ADRs)

This document records significant architectural decisions made in this project.

Each decision includes context, the decision itself, and consequences.

## ADR-001: Use Docker for Deployment

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need consistent environment across development, staging, and production
- Want to avoid "works on my machine" problems
- Need to package application with all dependencies
- Want to enable easy scaling

**Decision**: Use Docker containers with Docker Compose for orchestration

**Alternatives Considered**:
1. **Traditional deployment** (pip install on bare metal) - Rejected due to environment drift
2. **Virtual machines** - Rejected due to overhead and slow startup
3. **Kubernetes** - Rejected as overkill for single-server deployment

**Consequences**:

Positive:
- Environment parity between dev and prod
- Easy to scale horizontally
- Easy to update dependencies
- Portable across hosting providers

Negative:
- Requires Docker knowledge
- Additional abstraction layer
- Slightly more complex local setup

**Implementation**:
- `Dockerfile` for web container
- `docker-compose.yml` for orchestration
- `entrypoint.sh` for container initialization

---

## ADR-002: PostgreSQL as Primary Database

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need ACID-compliant relational database
- Need to handle complex queries and relationships
- Want production-grade reliability
- Need JSON field support for future flexibility

**Decision**: Use PostgreSQL 15 as the primary database

**Alternatives Considered**:
1. **SQLite** - Rejected due to concurrency limitations and not suitable for production
2. **MySQL** - Rejected due to weaker PostgreSQL features (better JSON, window functions, etc.)
3. **MongoDB** - Rejected due to lack of ACID guarantees and relational integrity

**Consequences**:

Positive:
- ACID compliance
- Strong data integrity with foreign keys
- Excellent performance for complex queries
- JSON field support for semi-structured data
- Battle-tested in production environments

Negative:
- More resource-intensive than SQLite
- Requires separate container/service
- More complex backup/restore procedures

**Implementation**:
- PostgreSQL 15 Alpine image for smaller footprint
- Docker volume for data persistence
- Connection via psycopg2-binary adapter

---

## ADR-003: Gunicorn as WSGI Server

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Django development server is not suitable for production
- Need production-grade WSGI server
- Need to handle concurrent requests
- Want graceful worker management

**Decision**: Use Gunicorn with 3 worker processes

**Alternatives Considered**:
1. **uWSGI** - Rejected due to more complex configuration
2. **mod_wsgi** - Rejected due to Apache dependency
3. **Django runserver** - Rejected as explicitly not for production

**Consequences**:

Positive:
- Simple configuration
- Pre-fork worker model for stability
- Graceful worker restart
- Battle-tested in production
- Python-based (no compilation needed)

Negative:
- No built-in static file serving (need Nginx)
- Workers don't share memory (can't use in-process cache)

**Worker Count Calculation**:
- Formula: `(2 * CPU_CORES) + 1`
- Current: 3 workers (assumes 1 CPU core)
- Adjust based on server resources

**Implementation**:
- Command: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3`
- Can add `--timeout 30` for long-running requests

---

## ADR-004: Nginx as Reverse Proxy

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need SSL termination
- Need to serve static files efficiently
- Want to add HTTP headers
- Want to enable future load balancing

**Decision**: Use Nginx as reverse proxy in front of Gunicorn

**Alternatives Considered**:
1. **Direct Gunicorn exposure** - Rejected due to lack of SSL, static file serving
2. **Apache** - Rejected due to higher resource usage
3. **Caddy** - Rejected due to less familiarity and documentation

**Consequences**:

Positive:
- Extremely fast static file serving
- SSL/TLS termination
- Can add caching, compression, rate limiting
- Can load balance across multiple Gunicorn instances
- Battle-tested and well-documented

Negative:
- Additional component to configure
- Another potential point of failure
- Requires separate configuration file

**Implementation**:
- Nginx on host machine (not in container)
- Configuration in `nginx/nginx.conf`
- Proxies to `web:8000` container

---

## ADR-005: WhiteNoise for Static File Serving

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need to serve static files in development
- Want fallback for production if Nginx misconfigured
- Want to simplify deployment
- Need to serve collected static files

**Decision**: Use WhiteNoise middleware for static file serving

**Alternatives Considered**:
1. **Django static file serving** - Rejected as inefficient and not for production
2. **CDN only** - Rejected as requires external service
3. **No fallback** - Rejected as risky

**Consequences**:

Positive:
- Works in both development and production
- No configuration needed
- Efficient compression and caching
- Fallback if Nginx fails

Negative:
- Slightly slower than Nginx (but still fast)
- Uses application resources

**Implementation**:
- Middleware: `whitenoise.middleware.WhiteNoiseMiddleware`
- Placed after `SecurityMiddleware`
- In production, Nginx serves files first (WhiteNoise is fallback)

---

## ADR-006: Environment Variables for Configuration

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need to change configuration between environments (dev/staging/prod)
- Don't want secrets in version control
- Want to follow 12-factor app principles
- Need to configure database, allowed hosts, etc.

**Decision**: Use environment variables loaded from `.env` file via python-decouple

**Alternatives Considered**:
1. **Hardcoded settings** - Rejected due to security and inflexibility
2. **Multiple settings files** - Rejected due to complexity and duplication
3. **Config files (YAML/JSON)** - Rejected as less standard than env vars

**Consequences**:

Positive:
- Clear separation of code and config
- Easy to change per environment
- Secrets not in version control
- Standard practice (12-factor app)

Negative:
- Need to manage .env file
- Environment variables can be harder to validate

**Implementation**:
- `.env.example` as template
- `.env` in `.gitignore`
- `python-decouple` for reading env vars with defaults
- All environment-specific config in `config/environment.md`

---

## ADR-007: Django 5.0 as Web Framework

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need modern web framework with ORM, admin, authentication
- Want active community and ecosystem
- Need stability and long-term support
- Want to use Python

**Decision**: Use Django 5.0 (LTS considerations for future)

**Alternatives Considered**:
1. **Flask** - Rejected due to lack of built-in ORM, admin, auth
2. **FastAPI** - Rejected due to async-first design not needed here
3. **Django 4.2 LTS** - Considered but chose 5.0 for latest features

**Consequences**:

Positive:
- Batteries-included framework
- Excellent ORM and admin interface
- Strong security defaults
- Large ecosystem of packages

Negative:
- More opinionated than microframeworks
- Learning curve for Django-specific patterns
- Heavier than minimal frameworks

**Implementation**:
- Django 5.0.1
- Standard project structure with `config/` package
- Can migrate to Django 4.2 LTS if needed for support

---

## ADR-008: No Caching Layer (Yet)

**Status**: Accepted (with future reconsideration)

**Date**: 2025-12-21

**Context**:
- Caching adds complexity
- Current scale doesn't require caching
- Want to start simple
- Can add later if needed

**Decision**: Do not include Redis or Memcached in initial setup

**Alternatives Considered**:
1. **Redis for caching** - Deferred until performance issues appear
2. **Database query caching** - Django ORM caching sufficient for now

**Consequences**:

Positive:
- Simpler architecture
- Fewer components to manage
- Lower resource usage
- Easier to reason about data freshness

Negative:
- May need to add later if performance issues
- Migrations stored in database (slower than Redis)

**Future Considerations**:
- Add Redis when:
  - Response times exceed 500ms consistently
  - Database queries become bottleneck
  - Need session caching for scalability

---

## ADR-009: No Background Task Queue (Yet)

**Status**: Accepted (with future reconsideration)

**Date**: 2025-12-21

**Context**:
- Background tasks add complexity (Celery, Redis/RabbitMQ)
- No current requirement for async processing
- Want to start simple

**Decision**: Do not include Celery or background task processing

**Alternatives Considered**:
1. **Celery + Redis** - Deferred until needed
2. **Django-Q** - Deferred until needed

**Consequences**:

Positive:
- Simpler architecture
- Fewer components to manage
- No need for message broker

Negative:
- Long-running tasks will block workers
- No email sending in background (yet)

**Future Considerations**:
- Add Celery when:
  - Email sending is required
  - Report generation takes >5 seconds
  - Need scheduled tasks beyond Django management commands

**Current Workaround**:
- Use `manage.py` commands for one-off tasks
- Can run in separate container if needed

---

## ADR-010: Russian Locale and Europe/Moscow Timezone

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Target audience is Russian-speaking users
- Server located in Russia or serving Russian users
- Need consistent timezone for datetime handling

**Decision**: Set `LANGUAGE_CODE = 'ru-ru'` and `TIME_ZONE = 'Europe/Moscow'`

**Consequences**:

Positive:
- Admin interface in Russian
- Dates formatted for Russian users
- Consistent timezone handling

Negative:
- Need to change for international deployments

**Implementation**:
- `LANGUAGE_CODE = 'ru-ru'`
- `TIME_ZONE = 'Europe/Moscow'`
- `USE_TZ = True` (store UTC in database, display in Moscow time)

---

## ADR-011: Security Settings for Production

**Status**: Accepted

**Date**: 2025-12-21

**Context**:
- Need to protect against common web vulnerabilities
- Django provides security middleware
- Want to enable best practices by default

**Decision**: Enable production security settings when `DEBUG=False`

**Implementation**:
```python
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

**Consequences**:

Positive:
- Protection against:
  - XSS attacks (X-XSS-Protection)
  - Clickjacking (X-Frame-Options)
  - MIME sniffing (X-Content-Type-Options)
  - SSL stripping (redirect to HTTPS)
- Secure cookies (only sent over HTTPS)

Negative:
- Requires HTTPS in production
- Cloudflare SSL mode must be "Full (strict)"

See `security/overview.md` for details.

---

## Decision Review Process

These decisions should be reviewed:

1. **When adding major features** - Does the decision still hold?
2. **When performance issues arise** - Should we add caching or background tasks?
3. **When scaling beyond single server** - Do we need Kubernetes, external DB?
4. **Annually** - Are the technologies still best practice?

To propose a new decision or revisit an existing one:
1. Add a new ADR with status "Proposed"
2. Discuss with team
3. Update status to "Accepted" or "Rejected"
4. Update affected documentation

---

Last Updated: 2025-12-21
