# Project Overview

## Purpose

This is a production-ready Django 5.0 web application template designed for deployment in containerized environments.

The project provides a solid foundation for building scalable web applications with:

- Modern Django 5.0 framework
- PostgreSQL database
- Containerized deployment via Docker
- Production-grade WSGI server (Gunicorn)
- Reverse proxy with Nginx
- SSL/TLS support via Cloudflare and Certbot

## Goals

1. **Production-Ready**: Configured with security best practices and production-grade components
2. **Easy Deployment**: Single-command deployment using Docker Compose
3. **Scalability**: Designed to scale horizontally with container orchestration
4. **Developer-Friendly**: Clear separation of concerns, environment-based configuration
5. **Security-First**: Built-in security headers, SSL support, secure session management

## Non-Goals

This project does NOT aim to:

- Provide a full-featured CMS (it's a foundation, not a complete product)
- Include frontend framework (bring your own React/Vue/etc)
- Provide multi-tenancy out of the box
- Include complex business logic (domain-agnostic template)

## Mental Model

Think of this project as:

```
[User] → [Nginx Reverse Proxy] → [Gunicorn WSGI] → [Django App] → [PostgreSQL]
                ↓
         [Static Files]
```

The architecture follows standard Django deployment patterns:

1. **Nginx** handles SSL termination, static file serving, and load balancing
2. **Gunicorn** runs multiple Django worker processes
3. **Django** handles business logic and dynamic content
4. **PostgreSQL** provides ACID-compliant data persistence
5. **Docker** ensures environment consistency across dev/staging/prod

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Django | 5.0.1 | Web application framework |
| Database | PostgreSQL | 15 | Primary data store |
| WSGI Server | Gunicorn | 21.2.0 | Python WSGI HTTP server |
| Reverse Proxy | Nginx | Latest | HTTP server and reverse proxy |
| Containerization | Docker | - | Application containerization |
| Orchestration | Docker Compose | 3.8 | Multi-container orchestration |
| Static Files | WhiteNoise | 6.6.0 | Static file serving |
| Configuration | python-decouple | 3.8 | Environment variable management |
| Database Driver | psycopg2-binary | 2.9.9 | PostgreSQL adapter |

## Project Scope

### What This Project Includes

- Django project structure (`config/` package)
- Database configuration with PostgreSQL
- Docker containerization (Dockerfile, docker-compose.yml)
- Nginx reverse proxy configuration
- Environment-based settings management
- Static file handling with WhiteNoise
- Production security settings
- Admin interface
- User authentication system (Django built-in)

### What You Need to Add

- Business domain models
- Custom views and templates
- API endpoints (REST/GraphQL if needed)
- Frontend framework integration
- Custom middleware
- Background task processing (Celery, etc.)
- Caching layer (Redis, Memcached)
- Monitoring and observability tools

## Domain

This is a **domain-agnostic** template project.

The codebase does not assume any specific business domain.

You are expected to:

1. Create Django apps for your domain (e.g., `users`, `products`, `orders`)
2. Define domain models in those apps
3. Implement business logic
4. Create API endpoints or views

The project provides the infrastructure foundation only.

## Key Characteristics

### Stateless Application

The Django application layer is designed to be stateless:

- No local file storage (use object storage for uploads)
- Session data in database (can be moved to Redis)
- No assumption of single-instance deployment

### 12-Factor App Compliant

The project follows 12-factor app principles:

- Configuration via environment variables
- Explicit dependency declaration (requirements.txt)
- Stateless processes
- Log to stdout
- Admin processes via management commands

### Environment Parity

The same Docker images run in:

- Local development
- Staging environments
- Production environments

Only environment variables change between environments.

## Quick Start Reference

For developers new to the project:

1. Read `guides/setup.md` for local development setup
2. Read `architecture/system.md` to understand component structure
3. Read `config/environment.md` for configuration options
4. Read `guides/deployment.md` for production deployment

## Assumptions and Constraints

### Assumptions

1. You have Docker and Docker Compose installed
2. You have basic Django knowledge
3. You use PostgreSQL (not SQLite or MySQL)
4. You deploy to Linux-based servers
5. You use Nginx as reverse proxy (not Apache or Caddy)

### Constraints

1. Python 3.11+ required
2. PostgreSQL 15+ required
3. Docker 20.10+ required
4. Minimum 1GB RAM for production deployment
5. Russian locale and Europe/Moscow timezone (configurable)

## Success Metrics

This project is successful if:

1. You can deploy to production in under 10 minutes
2. You can add new Django apps without modifying infrastructure
3. Static files are served efficiently without Django involvement
4. Database connections are properly pooled and managed
5. Application scales horizontally by adding more containers

## Questions This Documentation Answers

Navigate to specific documentation files to answer:

- **"How do I set up local development?"** → `guides/setup.md`
- **"What environment variables are required?"** → `config/environment.md`
- **"How do components interact?"** → `architecture/data-flow.md`
- **"How do I deploy to production?"** → `guides/deployment.md`
- **"What security features are enabled?"** → `security/overview.md`
- **"How does the application start?"** → `runtime/lifecycle.md`

---

Last Updated: 2025-12-21
