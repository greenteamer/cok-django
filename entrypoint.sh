#!/bin/bash

# Wait for PostgreSQL to be ready (with timeout)
echo "Waiting for PostgreSQL..."
DB_HOST="${DB_HOST:-${PGHOST:-db}}"
DB_PORT="${DB_PORT:-${PGPORT:-5432}}"
DB_WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-30}"

echo "Connecting to ${DB_HOST}:${DB_PORT} (timeout: ${DB_WAIT_TIMEOUT}s)..."

SECONDS=0
while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
  if [ "$SECONDS" -ge "$DB_WAIT_TIMEOUT" ]; then
    echo "ERROR: PostgreSQL not available at ${DB_HOST}:${DB_PORT} after ${DB_WAIT_TIMEOUT}s"
    echo "Check DB_HOST/DB_PORT environment variables and database service status"
    exit 1
  fi
  sleep 0.5
done
echo "PostgreSQL started on ${DB_HOST}:${DB_PORT} (waited ${SECONDS}s)"

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
