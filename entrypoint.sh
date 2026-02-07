#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
DB_HOST="${DB_HOST:-${PGHOST:-db}}"
DB_PORT="${DB_PORT:-${PGPORT:-5432}}"

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started on ${DB_HOST}:${DB_PORT}"

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
