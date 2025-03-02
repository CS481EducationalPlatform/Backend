#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to start..."
sleep 5

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
