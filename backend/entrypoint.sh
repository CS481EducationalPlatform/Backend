#!/bin/sh

# Load environment variables from .env if it exists
if [ -f .env ]; then
    . .env
fi

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to start..."
sleep 5

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
