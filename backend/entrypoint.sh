#!/bin/sh

# Source environment variables if .env exists
if [ -f "/backend_app/.env" ]; then
    . /backend_app/.env
fi

# Wait for database to be ready (using pg_isready)
echo "Waiting for PostgreSQL to start..."
until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER
do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
