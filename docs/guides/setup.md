# Local Development Setup

This guide walks you through setting up the project for local development.

## Prerequisites

Before you begin, ensure you have:

- **Docker** 20.10+ installed
- **Docker Compose** 2.0+ installed (or docker-compose plugin)
- **Git** (to clone the repository)
- **Code editor** (VS Code, PyCharm, etc.)

### Installing Docker

#### macOS

```bash
# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop

# Or via Homebrew
brew install --cask docker
```

#### Linux (Ubuntu/Debian)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Log out and log back in for group changes
```

#### Windows

Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Verify Installation

```bash
docker --version
# Docker version 24.0.0 or higher

docker-compose --version
# Docker Compose version 2.0.0 or higher
```

---

## Quick Start (5 minutes)

### 1. Clone or Navigate to Project

```bash
cd /path/to/cokdjango
```

### 2. Create Environment File

```bash
cp .env.example .env
```

The default `.env` values are suitable for development. No changes needed.

### 3. Start the Application

```bash
make setup
```

This command:
- Builds Docker images
- Starts database and web containers
- Runs database migrations
- Creates superuser (you'll be prompted for username/password)

**Alternative** (manual steps):
```bash
make build      # Build and start containers
make migrate    # Run database migrations
make createsuperuser  # Create admin user
```

### 4. Access the Application

Open your browser to:

- **Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin

Login with the superuser credentials you created.

---

## Detailed Setup Steps

### Step 1: Understanding the Environment

The `.env` file contains configuration. Default development values:

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

**For development**: These defaults are fine. No changes needed.

See `config/environment.md` for detailed explanation of each variable.

---

### Step 2: Build Docker Images

```bash
docker-compose up --build -d
```

**What happens**:
1. Downloads `python:3.11-slim` base image
2. Installs system dependencies (PostgreSQL client, netcat)
3. Installs Python packages from `requirements.txt`
4. Downloads `postgres:15-alpine` image
5. Creates Docker network and volumes

**Duration**: 2-5 minutes (first time only)

**Output**:
```
[+] Building 45.2s
[+] Running 3/3
 ✔ Network cokdjango_default       Created
 ✔ Container cokdjango-db-1        Started
 ✔ Container cokdjango-web-1       Started
```

---

### Step 3: Wait for Database

The `entrypoint.sh` script waits for PostgreSQL to be ready:

```bash
docker-compose logs web
```

You should see:
```
Waiting for PostgreSQL...
PostgreSQL started
Running migrations...
No migrations to apply.
```

---

### Step 4: Run Database Migrations

```bash
make migrate
```

Or manually:
```bash
docker-compose exec web python manage.py migrate
```

**What happens**:
- Creates database tables for Django apps (auth, admin, sessions, etc.)
- Applies migration files from `*/migrations/` directories

**Output**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

### Step 5: Create Superuser

```bash
make createsuperuser
```

You'll be prompted:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

**Password Requirements**:
- At least 8 characters
- Not too similar to username
- Not entirely numeric

---

### Step 6: Verify Installation

1. **Check containers are running**:
   ```bash
   make status
   # Or
   docker-compose ps
   ```

   Expected output:
   ```
   NAME                 STATUS    PORTS
   cokdjango-db-1       Up        0.0.0.0:5432->5432/tcp
   cokdjango-web-1      Up        0.0.0.0:8000->8000/tcp
   ```

2. **Access admin interface**:
   - Open http://localhost:8000/admin
   - Login with superuser credentials
   - You should see Django admin dashboard

3. **Check logs**:
   ```bash
   make logs
   ```

   No errors should appear (warnings about unapplied migrations are OK if migrations were just run).

---

## Common Development Tasks

### Starting and Stopping

```bash
# Start containers (after initial setup)
make up

# Stop containers
make down

# Restart containers
make restart

# View logs (follow mode)
make logs

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f db
```

---

### Working with Django

#### Access Django Shell

```bash
make djshell
```

Or:
```bash
docker-compose exec web python manage.py shell
```

**Usage**:
```python
from django.contrib.auth.models import User
users = User.objects.all()
print(users)
```

#### Access Container Shell

```bash
make shell
```

Or:
```bash
docker-compose exec web bash
```

Now you're inside the container and can run commands:
```bash
ls
python manage.py --help
```

---

### Creating Django Apps

```bash
docker-compose exec web python manage.py startapp myapp
```

Then:
1. Add `'myapp'` to `INSTALLED_APPS` in `config/settings.py`
2. Create models in `myapp/models.py`
3. Create migrations: `make makemigrations`
4. Apply migrations: `make migrate`

---

### Database Management

#### Create Migrations

After modifying models:

```bash
make makemigrations
```

Or:
```bash
docker-compose exec web python manage.py makemigrations
```

#### Apply Migrations

```bash
make migrate
```

#### Database Shell

```bash
docker-compose exec db psql -U django_user django_db
```

SQL commands:
```sql
\dt  -- List tables
\d auth_user  -- Describe table
SELECT * FROM auth_user;
\q  -- Quit
```

#### Database Backup

```bash
make backup
```

This creates `backup_YYYYMMDD_HHMMSS.sql` in current directory.

Or manually:
```bash
docker-compose exec db pg_dump -U django_user django_db > backup.sql
```

#### Database Restore

```bash
docker-compose exec -T db psql -U django_user django_db < backup.sql
```

#### Reset Database

**WARNING**: This deletes all data!

```bash
make clean  # Removes containers AND volumes
make build  # Rebuild
make migrate  # Recreate tables
make createsuperuser  # Recreate admin
```

---

### Static Files

In development, WhiteNoise serves static files automatically.

To collect static files (if needed):

```bash
make collectstatic
```

This copies static files from Django apps to `staticfiles/` directory.

---

## Development Workflow

Typical development workflow:

1. **Start containers**: `make up`
2. **Make code changes** in your editor
3. **Changes auto-reload** (Django development server with `--reload`)
4. **Test in browser**: http://localhost:8000
5. **Run migrations** if models changed: `make makemigrations && make migrate`
6. **Check logs** if errors: `make logs`
7. **Stop containers** when done: `make down`

---

## Troubleshooting

### Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# Or on Linux
netstat -tulpn | grep 8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

---

### Database Connection Refused

**Error**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:

1. Check database is running:
   ```bash
   docker-compose ps db
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Restart database:
   ```bash
   docker-compose restart db
   ```

4. Rebuild containers:
   ```bash
   make clean
   make build
   ```

---

### Migrations Not Applied

**Error**: `You have 18 unapplied migration(s).`

**Solution**:
```bash
make migrate
```

---

### Permission Denied Errors

**Error**: `Permission denied: '/app/staticfiles'`

**Solution** (Linux):
```bash
# Give Docker user permission to project directory
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up
```

---

### Changes Not Reflected

**Issue**: Code changes not showing in browser

**Solutions**:

1. **Hard refresh browser**: Ctrl+Shift+R or Cmd+Shift+R

2. **Check auto-reload is working**:
   ```bash
   make logs
   # Should see: "Watching for file changes with StatReloader"
   ```

3. **Restart web container**:
   ```bash
   docker-compose restart web
   ```

4. **Rebuild image** (if requirements.txt or Dockerfile changed):
   ```bash
   make build
   ```

---

### Container Exits Immediately

**Issue**: `docker-compose ps` shows container as "Exited"

**Solution**:
```bash
# Check logs for error
docker-compose logs web

# Common causes:
# 1. Syntax error in Python code
# 2. Missing dependency in requirements.txt
# 3. Database not ready (entrypoint.sh should handle this)

# Fix the error and restart
docker-compose up -d
```

---

## IDE Setup

### Local Python Environment for LSP/Autocomplete

The project runs in Docker, so dependencies are installed inside the container. To get IDE features like autocomplete, type checking, and import resolution working locally, you need a local Python virtual environment.

**Setup**:

```bash
make dev-setup
```

This command:
- Creates `.venv/` virtual environment
- Installs all dependencies from `requirements.txt`

After running, configure your IDE to use `.venv/bin/python` as the Python interpreter and restart your LSP/IDE.

**Important Notes**:
- This is ONLY for IDE/LSP support
- The application still runs in Docker
- `.venv/` is git-ignored
- `pyrightconfig.json` is included in the repository for type checker configuration

**When to run `make dev-setup` again**:
- After cloning the project (first time setup)
- After updating `requirements.txt`
- If LSP stops recognizing imports

---

## Next Steps

After setup:

1. **Read architecture docs**: `architecture/system.md`
2. **Understand data flow**: `architecture/data-flow.md`
3. **Review configuration**: `config/environment.md`
4. **Create your first Django app**: `docker-compose exec web python manage.py startapp myapp`
5. **Read testing guide**: `guides/testing.md` (when tests are added)

For production deployment, see `guides/deployment.md`.

---

Last Updated: 2025-12-21
