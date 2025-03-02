#!/bin/sh

# Source environment variables if .env exists
if [ -f "/backend_app/.env" ]; then
    set -a
    . /backend_app/.env
    set +a
fi

# Set database connection variables from DATABASE_URL if available
if [ -n "$DATABASE_URL" ]; then
    # Extract database connection details from DATABASE_URL
    DATABASE_HOST=$(echo $DATABASE_URL | awk -F[@//] '{print $4}')
    DATABASE_PORT=$(echo $DATABASE_URL | awk -F[:] '{print $4}' | awk -F[/] '{print $1}')
    DATABASE_USER=$(echo $DATABASE_URL | awk -F[:@] '{print $2}')
fi

# Use default values if not set
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}
DATABASE_USER=${DATABASE_USER:-postgres}

# Wait for database to be ready
echo "Waiting for PostgreSQL to start..."
for i in $(seq 1 30); do
    pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER && break
    echo "Waiting for PostgreSQL... ${i}/30"
    sleep 2
done

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
