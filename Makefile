.PHONY: build up down restart logs shell migrate makemigrations createsuperuser collectstatic test clean

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

# Run tests
test:
	docker-compose exec web python manage.py test

# Clean up containers and volumes
clean:
	docker-compose down -v

# Initial setup
setup: build migrate createsuperuser
	@echo "Setup complete! Access the app at http://localhost"

# Database backup
backup:
	docker-compose exec db pg_dump -U django_user django_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Show status
status:
	docker-compose ps
