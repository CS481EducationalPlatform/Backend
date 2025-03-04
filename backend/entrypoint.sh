#!/bin/sh

# Source environment variables if .env exists
if [ -f "/backend_app/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [ -z "$key" ] || [ "${key#\#}" != "$key" ] && continue
        # Export the variable
        export "$key=$value"
    done < "/backend_app/.env"
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

# Create Django admin superuser
echo ""
echo "======================================================"
echo "CREATING DJANGO ADMIN SUPERUSER"
echo "======================================================"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/updating superuser: $DJANGO_SUPERUSER_USERNAME"
    python -c "
import os
import django
django.setup()
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f'Superuser {username} updated successfully')
    else:
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser {username} created successfully')
except Exception as e:
    print(f'Error creating/updating superuser: {e}')
"
else
    echo "WARNING: Superuser not created. Required environment variables not set."
    echo "Please ensure DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD are set."
fi
echo "======================================================"
echo ""

# Execute the main command
exec "$@"
