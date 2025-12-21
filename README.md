# Django Docker Project

Production-ready Django 5.0 application template with Docker, PostgreSQL, Gunicorn, and Nginx.

## Features

- **Django 5.0** - Modern Python web framework
- **PostgreSQL 15** - Reliable ACID-compliant database
- **Docker** - Containerized deployment
- **Gunicorn** - Production WSGI server
- **Nginx** - Reverse proxy and static file serving
- **Security-first** - HTTPS, secure headers, CSRF protection
- **12-factor app** - Environment-based configuration

## Quick Start (5 minutes)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd cokdjango

# 2. Create environment file
cp .env.example .env
# Default values work for development

# 3. Start application
make setup

# Or manually:
# docker-compose up --build -d
# docker-compose exec web python manage.py migrate
# docker-compose exec web python manage.py createsuperuser
```

### Access

- **Application**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

### Common Commands

```bash
make up              # Start containers
make down            # Stop containers
make logs            # View logs
make shell           # Access container shell
make migrate         # Run database migrations
make test            # Run tests (when implemented)
```

See `Makefile` for all available commands.

---

## Documentation

**📚 Complete documentation available in [`docs/`](./docs/README.md)**

### Quick Links

- **[Project Overview](./docs/overview.md)** - Purpose, goals, and technology stack
- **[Local Setup Guide](./docs/guides/setup.md)** - Detailed development setup
- **[Deployment Guide](./docs/guides/deployment.md)** - Production deployment on Ubuntu
- **[Architecture](./docs/architecture/system.md)** - System architecture and components
- **[Configuration](./docs/config/environment.md)** - Environment variables reference
- **[Security](./docs/security/overview.md)** - Security model and best practices

---

## Project Structure

```
.
├── config/              # Django project settings
│   ├── settings.py      # Main configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI entry point
├── docs/                # 📚 Complete documentation
├── nginx/               # Nginx configuration
├── staticfiles/         # Collected static files
├── docker-compose.yml   # Container orchestration
├── Dockerfile           # Django container
├── Makefile             # Development commands
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

---

## Development Workflow

1. **Make changes** to code
2. **Test locally**: Changes auto-reload in development
3. **Run migrations** if models changed: `make migrate`
4. **Check logs** if needed: `make logs`
5. **Run tests**: `make test` (when implemented)

See [Development Guide](./docs/guides/setup.md) for details.

---

## Production Deployment

**Quick summary** (see [full deployment guide](./docs/guides/deployment.md)):

1. **Server**: Ubuntu 20.04+ with Docker installed
2. **Environment**: Configure `.env` with production secrets
3. **Deploy**: `make build && make migrate`
4. **Nginx**: Configure SSL with Let's Encrypt
5. **Cloudflare**: Set SSL mode to "Full (strict)"

**Important**: Always set `DEBUG=False` in production!

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Django | 5.0.1 | Web application framework |
| Database | PostgreSQL | 15 | Primary data store |
| WSGI Server | Gunicorn | 21.2.0 | Python WSGI HTTP server |
| Reverse Proxy | Nginx | Latest | HTTP server and static files |
| Containerization | Docker | 20.10+ | Application containers |
| Static Files | WhiteNoise | 6.6.0 | Static file serving |

See [Architecture Documentation](./docs/architecture/system.md) for detailed component descriptions.

---

## Security

Production security features (enabled when `DEBUG=False`):

- ✅ HTTPS enforcement
- ✅ Secure cookies (session, CSRF)
- ✅ Security headers (XSS, clickjacking, MIME sniffing protection)
- ✅ CSRF protection
- ✅ Password hashing (PBKDF2)
- ✅ SQL injection protection (ORM parameterization)

See [Security Documentation](./docs/security/overview.md) for complete security model.

---

## Troubleshooting

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Database connection refused

```bash
# Check database status
docker-compose ps db
docker-compose logs db

# Restart database
docker-compose restart db
```

### Static files not loading

```bash
# Recollect static files
make collectstatic
```

For more troubleshooting, see:
- [Setup Guide](./docs/guides/setup.md#troubleshooting)
- [Deployment Guide](./docs/guides/deployment.md#troubleshooting-production-issues)
- [Error Handling](./docs/runtime/error-handling.md)

---

## Contributing

1. Read [Architecture Documentation](./docs/architecture/system.md)
2. Follow [Development Guide](./docs/guides/setup.md)
3. Write tests (see [Testing Guide](./docs/guides/testing.md))
4. Update documentation when needed

---

## License

MIT

---

## Resources

- **Documentation**: [`docs/README.md`](./docs/README.md) - Start here for complete documentation
- **Django**: https://docs.djangoproject.com/
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

**Need help?** Check the [documentation](./docs/README.md) or open an issue.
