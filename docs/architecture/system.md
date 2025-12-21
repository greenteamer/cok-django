# System Architecture

## High-Level Architecture

The system follows a classic 3-tier web application architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    External Layer                        │
│  ┌──────────┐           ┌─────────────┐                │
│  │ Internet │──────────▶│  Cloudflare │                │
│  └──────────┘           └─────────────┘                │
│                               │                          │
└───────────────────────────────┼──────────────────────────┘
                                │ HTTPS
┌───────────────────────────────┼──────────────────────────┐
│                    Presentation Layer                     │
│                        ┌───────┴────────┐                │
│                        │  Nginx Proxy   │                │
│                        │  (Host/Docker) │                │
│                        └───────┬────────┘                │
│                                │                          │
└────────────────────────────────┼──────────────────────────┘
                                 │ HTTP
┌────────────────────────────────┼──────────────────────────┐
│                    Application Layer                      │
│                        ┌───────┴────────┐                │
│                        │   Gunicorn     │                │
│                        │  (3 workers)   │                │
│                        └───────┬────────┘                │
│                                │                          │
│                        ┌───────┴────────┐                │
│                        │  Django 5.0    │                │
│                        │   (config/)    │                │
│                        └───────┬────────┘                │
│                                │                          │
└────────────────────────────────┼──────────────────────────┘
                                 │ SQL
┌────────────────────────────────┼──────────────────────────┐
│                      Data Layer                           │
│                        ┌───────┴────────┐                │
│                        │  PostgreSQL 15 │                │
│                        │   (Container)  │                │
│                        └────────────────┘                │
└───────────────────────────────────────────────────────────┘
```

## Component Boundaries

### 1. Nginx (Reverse Proxy)

**Responsibility**: HTTP request routing, SSL termination, static file serving

**Location**:
- Development: Not used (direct access to Gunicorn)
- Production: Host machine or separate container

**Interfaces**:
- **Input**: HTTPS requests from Cloudflare/Internet on port 80/443
- **Output**: HTTP requests to Gunicorn on port 8000

**Configuration**: `nginx/nginx.conf`

**What it MUST do**:
- Terminate SSL/TLS connections
- Proxy dynamic requests to Gunicorn
- Serve static files from `/var/www/coreofkeen.com/staticfiles/`
- Serve media files from `/var/www/coreofkeen.com/media/`
- Set correct proxy headers (X-Forwarded-For, X-Forwarded-Proto, Host)

**What it MUST NOT do**:
- Process application logic
- Connect directly to database
- Store session data
- Perform authentication/authorization

### 2. Gunicorn (WSGI Server)

**Responsibility**: Manage Django worker processes, handle HTTP/WSGI translation

**Location**: Inside `web` Docker container

**Interfaces**:
- **Input**: HTTP requests from Nginx on port 8000
- **Output**: Database queries to PostgreSQL

**Configuration**:
- Command: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3`
- Workers: 3 (configurable)

**What it MUST do**:
- Spawn and manage Django worker processes
- Handle graceful worker restart
- Load balance requests across workers
- Translate HTTP to WSGI

**What it MUST NOT do**:
- Serve static files in production (handled by WhiteNoise/Nginx)
- Handle SSL termination
- Store application state across workers

### 3. Django Application

**Responsibility**: Business logic, request/response handling, ORM

**Location**: Inside `web` Docker container at `/app`

**Interfaces**:
- **Input**: WSGI calls from Gunicorn
- **Output**:
  - Database queries via psycopg2
  - Log messages to stdout
  - Static files via WhiteNoise (dev mode)

**Configuration**:
- Settings: `config/settings.py`
- URLs: `config/urls.py`
- WSGI: `config/wsgi.py`

**Installed Middleware** (in order):
1. `SecurityMiddleware` - Security headers
2. `WhiteNoiseMiddleware` - Static file serving
3. `SessionMiddleware` - Session management
4. `CommonMiddleware` - Common processing
5. `CsrfViewMiddleware` - CSRF protection
6. `AuthenticationMiddleware` - User authentication
7. `MessageMiddleware` - User messages
8. `ClickjackingMiddleware` - Clickjacking protection

**What it MUST do**:
- Handle all business logic
- Validate user input
- Manage database transactions
- Render templates or serialize responses
- Enforce authentication and authorization
- Log application events

**What it MUST NOT do**:
- Directly serve large files
- Perform long-running tasks synchronously (use Celery for that)
- Store uploaded files locally (use object storage)

### 4. PostgreSQL Database

**Responsibility**: Persistent data storage, ACID transactions

**Location**: Inside `db` Docker container

**Interfaces**:
- **Input**: SQL queries from Django on port 5432
- **Output**: Query results

**Configuration**:
- Environment variables in `.env`
- Volume: `postgres_data` for data persistence

**What it MUST do**:
- Store all application data
- Ensure ACID transactions
- Enforce referential integrity
- Provide connection pooling

**What it MUST NOT do**:
- Store files (images, documents) - use object storage
- Handle application logic via stored procedures (keep logic in Django)

## Docker Container Architecture

### Container: `web`

**Base Image**: `python:3.11-slim`

**Purpose**: Run Django application with Gunicorn

**Exposed Ports**: 8000

**Volumes**:
- `.:/app` - Source code (development only, bind mount)

**Depends On**: `db` container

**Entrypoint**: `/app/entrypoint.sh`

**Health Check**: None (should be added)

### Container: `db`

**Base Image**: `postgres:15-alpine`

**Purpose**: PostgreSQL database server

**Exposed Ports**: 5432

**Volumes**:
- `postgres_data:/var/lib/postgresql/data` - Persistent data storage

**Restart Policy**: `unless-stopped`

## Network Architecture

### Docker Network

All containers run in a default Docker Compose network.

**DNS Resolution**:
- `web` container can reach database at hostname `db`
- `db` is NOT accessible from outside Docker network (production)

**Port Mapping**:
- Development: `5432:5432` (db), `8000:8000` (web)
- Production: Only `8000:8000` should be exposed, Nginx proxies to it

### External Network

**Development**:
```
localhost:8000 → Gunicorn → Django
```

**Production**:
```
Internet → Cloudflare → Host Nginx (443/80) → Gunicorn (8000) → Django
```

## File System Architecture

### Container Filesystem: `web`

```
/app/
├── config/              # Django project settings
│   ├── __init__.py
│   ├── settings.py      # Main settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI entry point
│   └── asgi.py          # ASGI entry point (not used)
├── staticfiles/         # Collected static files
├── media/               # User uploaded files
├── manage.py            # Django management CLI
├── requirements.txt     # Python dependencies
├── entrypoint.sh        # Container entrypoint
└── [your apps]/         # Custom Django apps

```

### Host Filesystem: Production

```
/var/www/coreofkeen.com/
├── staticfiles/         # Static files (served by Nginx)
└── media/               # Media files (served by Nginx)

/etc/nginx/
├── sites-available/
│   └── coreofkeen.com   # Nginx config
└── sites-enabled/
    └── coreofkeen.com   # Symlink

/path/to/project/
├── .env                 # Environment variables
├── docker-compose.yml   # Container orchestration
└── [project files]
```

## Deployment Topology

### Single-Server Deployment (Current)

```
┌─────────────────────────────────────────┐
│           Ubuntu Server                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Nginx (Host)                      │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Docker Containers                 │ │
│  │  ┌──────────┐    ┌──────────────┐ │ │
│  │  │   web    │    │      db      │ │ │
│  │  │ Gunicorn │───▶│  PostgreSQL  │ │ │
│  │  │  Django  │    │              │ │ │
│  │  └──────────┘    └──────────────┘ │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Docker Volumes                    │ │
│  │  - postgres_data                   │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Scaling Options (Future)

For horizontal scaling:

1. **Multiple Web Containers**: Scale `web` service with `docker-compose up --scale web=3`
2. **External Database**: Move PostgreSQL to managed service (RDS, etc.)
3. **Load Balancer**: Add HAProxy or cloud load balancer in front of Nginx
4. **Separate Static File Server**: Use CDN for static files

## Component Communication

### Synchronous Communication

All current communication is synchronous:

1. **Nginx → Gunicorn**: HTTP/1.1, TCP
2. **Gunicorn → Django**: WSGI (in-process)
3. **Django → PostgreSQL**: PostgreSQL wire protocol, TCP

### Asynchronous Communication

None currently implemented.

For future async tasks, consider:
- Celery + Redis/RabbitMQ for background jobs
- Django Channels + Redis for WebSockets

## Dependency Graph

```
Nginx
  ↓
Gunicorn
  ↓
Django
  ↓
PostgreSQL
```

**Critical Path**: All components are in the critical path for serving requests.

**Single Points of Failure**:
- PostgreSQL database
- Single web container

**Mitigation**:
- Database backups (see `runtime/lifecycle.md`)
- Scale web containers horizontally

## State Management

### Stateless Components

- Nginx (stateless proxy)
- Gunicorn workers (stateless, share no memory)
- Django application (stateless, no local cache)

### Stateful Components

- PostgreSQL (all application state)
- Docker volumes (persistent data)

### Session State

Sessions are stored in PostgreSQL `django_session` table.

Can be moved to Redis for better performance:
- Add `django-redis` package
- Configure `SESSION_ENGINE = 'django.contrib.sessions.backends.cache'`

## Configuration Management

All environment-specific configuration is in `.env` file.

See `config/environment.md` for details.

**Configuration Hierarchy**:
1. Environment variables (`.env`)
2. Default values in `settings.py`
3. Hardcoded constants (should be minimal)

## Security Boundaries

### Trust Boundaries

1. **Internet → Nginx**: Untrusted to trusted boundary
   - SSL/TLS encryption
   - Cloudflare DDoS protection

2. **Nginx → Django**: Trusted internal communication
   - No encryption (same host or Docker network)
   - Proxy headers trusted

3. **Django → PostgreSQL**: Trusted internal communication
   - Password authentication
   - No SSL (Docker network)

### Authentication Points

- **User Authentication**: Django authentication system
- **Admin Interface**: Django admin with username/password
- **Database Access**: PostgreSQL user/password (from `.env`)

See `security/overview.md` for detailed security model.

---

Last Updated: 2025-12-21
