#!/bin/sh

# Print important environment variables for debugging
echo ""
echo "======================================================"
echo "ENVIRONMENT VARIABLES CHECK"
echo "======================================================"
echo "DATABASE_URL: $(if [ -n "$DATABASE_URL" ]; then echo "EXISTS (value hidden)"; else echo "NOT SET"; fi)"
echo "DJANGO_SUPERUSER_USERNAME: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "SET"; else echo "NOT SET"; fi)"
echo "DJANGO_SUPERUSER_EMAIL: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "SET"; else echo "NOT SET"; fi)"
echo "DJANGO_SUPERUSER_PASSWORD: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "SET (hidden)"; else echo "NOT SET"; fi)"
echo "======================================================"
echo ""

# Extract database connection details from DATABASE_URL
if [ -n "$DATABASE_URL" ]; then
    DATABASE_HOST=$(echo $DATABASE_URL | awk -F[@//] '{print $4}')
    DATABASE_PORT=$(echo $DATABASE_URL | awk -F[:] '{print $4}' | awk -F[/] '{print $1}')
    DATABASE_USER=$(echo $DATABASE_URL | awk -F[:@] '{print $2}')

    echo "Using DATABASE_HOST: $DATABASE_HOST"
    echo "Using DATABASE_PORT: $DATABASE_PORT"
    echo "Using DATABASE_USER: $DATABASE_USER"
else
    echo "WARNING: DATABASE_URL is not set!"
    DATABASE_HOST="localhost"
    DATABASE_PORT="5432"
    DATABASE_USER="postgres"
fi

# Wait for the database to be ready
echo "Waiting for PostgreSQL to start..."
for i in $(seq 1 30); do
    pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" && break
    echo "Waiting for PostgreSQL... ${i}/30"
    sleep 2
done

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create Django superuser using environment variables conditionally
echo ""
echo "======================================================"
echo "CREATING DJANGO SUPERUSER IF NOT EXISTS"
echo "======================================================"
if ! python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists()"; then
    python manage.py createsuperuser --noinput
fi
echo "======================================================"
echo ""

# Execute the main command (e.g., running the application)
exec "$@"
