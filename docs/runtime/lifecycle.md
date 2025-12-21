# Application Lifecycle

This document describes what happens when the application starts, runs, and shuts down.

## Container Startup Sequence

When you run `docker-compose up`, this sequence occurs:

### 1. Docker Compose Initialization

```bash
docker-compose up -d
```

**What happens**:
1. Reads `docker-compose.yml`
2. Reads `.env` file for environment variables
3. Creates Docker network (`cokdjango_default`)
4. Creates Docker volumes (`postgres_data`)
5. Starts containers in dependency order

---

### 2. Database Container Startup (`db`)

**Image**: `postgres:15-alpine`

**Startup sequence**:
1. Container starts
2. PostgreSQL initialization checks if data directory exists
3. If first run (no existing data):
   - Initialize database cluster
   - Create database user from `DB_USER`
   - Create database from `DB_NAME`
   - Set password from `DB_PASSWORD`
4. Start PostgreSQL server on port 5432
5. Ready to accept connections

**Logs** (`docker-compose logs db`):
```
PostgreSQL init process complete; ready for start up.
LOG: database system is ready to accept connections
```

**Duration**: 5-15 seconds (first run), 2-5 seconds (subsequent runs)

---

### 3. Web Container Startup (`web`)

**Image**: Built from `Dockerfile`

**Build phase** (first time or after `--build`):
1. Pull `python:3.11-slim` base image
2. Install system packages (postgresql-client, netcat-openbsd)
3. Install Python packages from `requirements.txt`
4. Copy application code to `/app`
5. Create `staticfiles` directory

**Runtime phase**:
1. Container starts
2. Execute `entrypoint.sh` script
3. Wait for database (see below)
4. Run migrations
5. Collect static files
6. Execute main command (Gunicorn)

---

### 4. Entrypoint Script Execution

**File**: `entrypoint.sh`

**Script contents**:
```bash
#!/bin/bash

# 1. Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# 2. Apply database migrations
python manage.py migrate --noinput

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Execute main command (Gunicorn)
exec "$@"
```

**What happens**:

#### 4.1 Database Wait Loop

Checks if PostgreSQL is accepting connections using `netcat`.

**Why**: PostgreSQL container may start before it's ready to accept connections.

**Retry**: Every 0.1 seconds until success.

**Typical duration**: 1-3 seconds.

---

#### 4.2 Database Migrations

```bash
python manage.py migrate --noinput
```

**What happens**:
1. Django connects to database
2. Checks `django_migrations` table for applied migrations
3. Compares with migration files in `*/migrations/` directories
4. Applies any unapplied migrations in order
5. Records applied migrations in database

**First run**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  ... (more migrations)
```

**Subsequent runs** (no new migrations):
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

**Duration**: 2-10 seconds (first run), <1 second (subsequent)

---

#### 4.3 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

**What happens**:
1. Django scans `STATICFILES_DIRS` and app static directories
2. Copies all static files to `STATIC_ROOT` (`staticfiles/`)
3. WhiteNoise processes files (compression, caching)

**Output**:
```
120 static files copied to '/app/staticfiles', 2 unmodified.
```

**Duration**: 1-3 seconds

**Note**: `--noinput` skips confirmation prompt.

---

### 5. Gunicorn Startup

**Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3`

**What happens**:
1. Gunicorn master process starts
2. Loads Django application via `config.wsgi:application`
3. Spawns 3 worker processes (pre-fork model)
4. Each worker loads Django settings and apps
5. Binds to `0.0.0.0:8000` (accessible from outside container)
6. Ready to accept HTTP requests

**Logs**:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000 (1)
[INFO] Using worker: sync
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
```

**Worker processes**:
- Each worker handles requests independently
- Workers don't share memory (stateless)
- If a worker crashes, Gunicorn restarts it

**Duration**: 3-5 seconds

---

## Request Handling Lifecycle

When a request arrives:

```
1. Nginx (production) or direct → Gunicorn
2. Gunicorn selects worker (round-robin)
3. Worker invokes Django WSGI application
4. Django middleware stack (request phase)
   - SecurityMiddleware
   - WhiteNoiseMiddleware
   - SessionMiddleware (load session from database)
   - CsrfViewMiddleware
   - AuthenticationMiddleware (load user from session)
   - MessageMiddleware
5. URL resolver matches request path to view
6. View function executes
   - Business logic
   - Database queries (if needed)
   - Template rendering or JSON serialization
7. Django middleware stack (response phase)
   - MessageMiddleware
   - SessionMiddleware (save session to database)
   - SecurityMiddleware (add security headers)
8. Response returned to Gunicorn
9. Gunicorn sends HTTP response to client
```

**Duration**: Typically 10-500ms depending on complexity.

See `architecture/data-flow.md` for detailed request flow.

---

## Shutdown Sequence

When you run `docker-compose down`:

### 1. Signal Handling

```bash
docker-compose down
```

**What happens**:
1. Docker sends `SIGTERM` to containers
2. Containers have 10 seconds to gracefully shut down
3. If not stopped, Docker sends `SIGKILL` (force kill)

---

### 2. Gunicorn Graceful Shutdown

**On receiving SIGTERM**:
1. Gunicorn master stops accepting new requests
2. Waits for in-flight requests to complete (up to 30 seconds)
3. Signals workers to shut down
4. Workers finish current requests
5. Workers exit
6. Master process exits

**Logs**:
```
[INFO] Handling signal: term
[INFO] Worker exiting (pid: 8)
[INFO] Worker exiting (pid: 9)
[INFO] Worker exiting (pid: 10)
[INFO] Shutting down: Master
```

---

### 3. PostgreSQL Graceful Shutdown

**On receiving SIGTERM**:
1. PostgreSQL stops accepting new connections
2. Completes active transactions
3. Flushes buffers to disk
4. Shuts down cleanly

**Logs**:
```
LOG: received fast shutdown request
LOG: aborting any active transactions
LOG: background worker "logical replication launcher" exited
LOG: shutting down
LOG: database system is shut down
```

---

### 4. Container Cleanup

1. Containers are stopped
2. Network is removed (if no other containers use it)
3. Volumes are retained (data persists)

**To remove volumes** (deletes all data):
```bash
docker-compose down -v
```

---

## Health Checks

Currently, no health checks are configured.

**Recommendation**: Add health check to `docker-compose.yml`:

```yaml
services:
  web:
    # ... existing config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

This allows Docker to monitor application health and restart if unhealthy.

---

## Auto-Restart Behavior

Containers are configured with `restart: unless-stopped`:

**Behavior**:
- Restart if exits with error
- Restart if host machine reboots
- Don't restart if manually stopped

**To disable auto-restart**:
```yaml
restart: "no"
```

---

## Initialization Tasks

### One-Time Setup Tasks

After first deployment:

```bash
# Create superuser
make createsuperuser

# Optional: Load initial data
docker-compose exec web python manage.py loaddata initial_data.json
```

### Recurring Tasks

After code updates:

```bash
# Apply new migrations
make migrate

# Collect static files
make collectstatic
sudo cp -r staticfiles /var/www/coreofkeen.com/
```

---

## Background Tasks

Currently, no background task processing is configured.

**Future**: Add Celery for background tasks (see ADR-009).

**When needed**:
1. Add Celery to requirements
2. Add Redis/RabbitMQ message broker
3. Create Celery worker container
4. Define tasks in `tasks.py`

---

## Scheduled Tasks

For periodic tasks:

**Option 1: Django Management Commands + Cron**

```bash
# Create management command
# myapp/management/commands/send_daily_emails.py

# Add to cron
0 9 * * * cd ~/apps/cokdjango && docker-compose exec -T web python manage.py send_daily_emails
```

**Option 2: Celery Beat** (when Celery is added)

```python
# config/celery.py
app.conf.beat_schedule = {
    'send-daily-emails': {
        'task': 'myapp.tasks.send_daily_emails',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

---

## Logging During Lifecycle

All logs go to stdout/stderr and are captured by Docker.

**View logs**:
```bash
# Follow all logs
make logs

# Follow specific container
docker-compose logs -f web
docker-compose logs -f db

# View logs since timestamp
docker-compose logs --since 2025-01-15T10:00:00

# Last N lines
docker-compose logs --tail 100 web
```

See `ops/logging.md` for detailed logging configuration.

---

## Performance During Startup

**Total startup time**: ~15-30 seconds (first run with build)

**Breakdown**:
- Docker image build: 2-5 minutes (first time only)
- Database initialization: 5-15 seconds (first time)
- Database startup: 2-5 seconds
- Wait for database: 1-3 seconds
- Migrations: 2-10 seconds (first time), <1 second (subsequent)
- Collect static: 1-3 seconds
- Gunicorn startup: 3-5 seconds

**Optimization**:
- Pre-build images and push to registry
- Use health checks to verify readiness
- Warm up database connections

---

## Zero-Downtime Deployment

For production zero-downtime deployments:

1. **Blue-Green Deployment**:
   - Deploy new version alongside old
   - Switch traffic when ready
   - Keep old version running briefly

2. **Rolling Updates** (with multiple instances):
   - Update one instance at a time
   - Load balancer routes to healthy instances

3. **Docker Compose** (current setup):
   - Build new image
   - `docker-compose up -d` updates containers
   - Brief downtime during restart (~5 seconds)

---

Last Updated: 2025-12-21
