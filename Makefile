.PHONY: build up down restart logs shell migrate makemigrations createsuperuser collectstatic fix-permissions deploy-static deploy test clean dev-setup setup-nginx css-install css-build css-watch css-prod

# Build and start containers
build:
	docker-compose up --build -d

# Start containers
up:
	docker-compose up -d

# Stop containers
down:
	docker-compose down

# Restart containers
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Shell into web container
shell:
	docker-compose exec web bash

# Django shell
djshell:
	docker-compose exec web python manage.py shell

# Run migrations
migrate:
	docker-compose exec web python manage.py migrate

# Create migrations
makemigrations:
	docker-compose exec web python manage.py makemigrations

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Fix file permissions for nginx (production only)
fix-permissions:
	@echo "Fixing file permissions for nginx..."
	./scripts/fix-permissions.sh
	@echo "✓ Permissions fixed!"

# Deploy static files to Nginx (production only)
# Note: Requires one-time setup (see docs/guides/deployment.md)
deploy-static:
	@echo "Collecting static files..."
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "Fixing file permissions..."
	./scripts/fix-permissions.sh
	@echo "Reloading Nginx..."
	sudo systemctl reload nginx
	@echo "✓ Static files deployed successfully!"

# Run tests
test:
	docker-compose exec web python manage.py test

# Clean up containers and volumes
clean:
	docker-compose down -v

# Initial setup (development)
setup: css-install css-build build migrate createsuperuser
	@echo "Setup complete! Access the app at http://localhost:8000"

# Full deployment (production)
deploy: css-prod down build migrate deploy-static
	@echo "✓ Deployment complete!"
	@echo "  Check status: make status"
	@echo "  View logs: make logs"

# Database backup
backup:
	docker-compose exec db pg_dump -U django_user django_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Show status
status:
	docker-compose ps

# Setup local development environment (for LSP/IDE support)
dev-setup:
	@echo "Setting up local development environment..."
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	else \
		echo "Virtual environment already exists"; \
	fi
	@echo "Installing dependencies..."
	@.venv/bin/pip install --upgrade pip -q
	@.venv/bin/pip install -r requirements.txt -q
	@echo "✓ Local development environment ready!"
	@echo "  Restart your LSP/IDE to use .venv/bin/python interpreter"

# Generate Nginx configuration from template (production)
setup-nginx:
	@echo "Generating Nginx configuration..."
	./scripts/setup-nginx.sh

# ============================================
# Frontend/CSS Commands
# ============================================

# Install Node.js dependencies
css-install:
	@echo "Installing Node.js dependencies..."
	npm install
	@echo "✓ Dependencies installed!"

# Build CSS (one-time)
css-build:
	@echo "Building CSS..."
	npm run css:build
	@echo "✓ CSS built successfully!"

# Watch and rebuild CSS on changes (development)
css-watch:
	@echo "Starting CSS watch mode..."
	@echo "Press Ctrl+C to stop"
	npm run css:watch

# Build production CSS (minified)
css-prod:
	@echo "Building production CSS..."
	npm run css:prod
	@echo "✓ Production CSS built successfully!"
