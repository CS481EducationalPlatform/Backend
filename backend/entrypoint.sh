#!/bin/sh

# Print important environment variables at the start for debugging
echo ""
echo "======================================================"
echo "INITIAL ENVIRONMENT VARIABLES"
echo "======================================================"
echo "DATABASE_URL: $(if [ -n "$DATABASE_URL" ]; then echo "EXISTS (value hidden)"; else echo "NOT SET"; fi)"
echo "======================================================"
echo ""

# Debug directly reading the environment variables
echo "Direct environment variable reading:"
printenv | grep DJANGO_SUPERUSER | cut -d= -f1
echo "DJANGO_SUPERUSER_PASSWORD is directly defined: $(if printenv | grep -q DJANGO_SUPERUSER_PASSWORD; then echo "YES"; else echo "NO"; fi)"
echo ""

# Store original DATABASE_URL to ensure it's preserved
ORIGINAL_DATABASE_URL="$DATABASE_URL"

# Source environment variables if .env exists in the app root
if [ -f "/backend_app/.env" ]; then
    echo "Loading environment variables from /backend_app/.env"
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [ -z "$key" ] || [ "${key#\#}" != "$key" ] && continue
        # Export the variable
        export "$key=$value"
    done < "/backend_app/.env"
fi

# Check for Render secret files in /etc/secrets/
if [ -d "/etc/secrets" ]; then
    echo "Checking for Render secret files in /etc/secrets/"
    if [ -f "/etc/secrets/.env" ]; then
        echo "Loading environment variables from /etc/secrets/.env"
        while IFS='=' read -r key value; do
            # Skip empty lines and comments
            [ -z "$key" ] || [ "${key#\#}" != "$key" ] && continue
            # Export the variable
            export "$key=$value"
        done < "/etc/secrets/.env"
    fi

    # Also check for individual environment variable files
    if [ -f "/etc/secrets/DJANGO_SUPERUSER_USERNAME" ]; then
        export DJANGO_SUPERUSER_USERNAME=$(cat /etc/secrets/DJANGO_SUPERUSER_USERNAME)
        echo "Loaded DJANGO_SUPERUSER_USERNAME from secret file"
    fi
    
    if [ -f "/etc/secrets/DJANGO_SUPERUSER_EMAIL" ]; then
        export DJANGO_SUPERUSER_EMAIL=$(cat /etc/secrets/DJANGO_SUPERUSER_EMAIL)
        echo "Loaded DJANGO_SUPERUSER_EMAIL from secret file"
    fi
    
    if [ -f "/etc/secrets/DJANGO_SUPERUSER_PASSWORD" ]; then
        export DJANGO_SUPERUSER_PASSWORD=$(cat /etc/secrets/DJANGO_SUPERUSER_PASSWORD)
        echo "Loaded DJANGO_SUPERUSER_PASSWORD from secret file"
    fi
fi

# Try direct capture of environment variables
# Save password from environment directly
DIRECT_PASSWORD=$(printenv DJANGO_SUPERUSER_PASSWORD)
if [ -n "$DIRECT_PASSWORD" ]; then
    echo "Captured password directly from environment variable"
    # Re-export it to ensure it's available
    export DJANGO_SUPERUSER_PASSWORD="$DIRECT_PASSWORD"
fi

# Restore the original DATABASE_URL if it was set
if [ -n "$ORIGINAL_DATABASE_URL" ]; then
    export DATABASE_URL="$ORIGINAL_DATABASE_URL"
    echo "Restored original DATABASE_URL from Render"
fi

# Set database connection variables from DATABASE_URL if available
if [ -n "$DATABASE_URL" ]; then
    echo "Extracting database connection details from DATABASE_URL"
    # Extract database connection details from DATABASE_URL
    DATABASE_HOST=$(echo $DATABASE_URL | awk -F[@//] '{print $4}')
    DATABASE_PORT=$(echo $DATABASE_URL | awk -F[:] '{print $4}' | awk -F[/] '{print $1}')
    DATABASE_USER=$(echo $DATABASE_URL | awk -F[:@] '{print $2}')
    
    echo "Extracted DATABASE_HOST: $DATABASE_HOST"
    echo "Extracted DATABASE_PORT: $DATABASE_PORT"
    echo "Extracted DATABASE_USER: $DATABASE_USER"
else
    echo "WARNING: DATABASE_URL is not set!"
fi

# Use default values if not set
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}
DATABASE_USER=${DATABASE_USER:-postgres}

echo "Using DATABASE_HOST: $DATABASE_HOST"
echo "Using DATABASE_PORT: $DATABASE_PORT"
echo "Using DATABASE_USER: $DATABASE_USER"

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

# Debug: Print environment variables for troubleshooting
echo ""
echo "======================================================"
echo "ENVIRONMENT VARIABLES DEBUG"
echo "======================================================"
echo "DJANGO_SUPERUSER_USERNAME exists: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "YES"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_EMAIL exists: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "YES"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_PASSWORD exists: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "YES"; else echo "NO"; fi)"
echo "Direct password capture exists: $(if [ -n "$DIRECT_PASSWORD" ]; then echo "YES"; else echo "NO"; fi)"
echo "======================================================"
echo ""

# Try to create superuser using direct password if standard variable is not available
if [ -z "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DIRECT_PASSWORD" ]; then
    echo "Using directly captured password instead of environment variable"
    export DJANGO_SUPERUSER_PASSWORD="$DIRECT_PASSWORD"
fi

# Create Django admin superuser
echo ""
echo "======================================================"
echo "CREATING DJANGO ADMIN SUPERUSER"
echo "======================================================"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/updating superuser: $DJANGO_SUPERUSER_USERNAME"
    # Try direct approach without Python code
    echo "Attempting to create superuser using direct approach..."
    DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" python manage.py createsuperuser --noinput --username="$DJANGO_SUPERUSER_USERNAME" --email="$DJANGO_SUPERUSER_EMAIL" || echo "Direct approach failed, trying alternative method"
    
    # Backup approach using Python code
    python -c "
import os
import django
import sys
django.setup()
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

print(f'Debug - Python environment variables:')
print(f'Username available: {username is not None}')
print(f'Email available: {email is not None}')
print(f'Password available: {password is not None}')

if username and email and password:
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
else:
    print(f'Missing required environment variables:')
    print(f'Username: {username is not None}')
    print(f'Email: {email is not None}')
    print(f'Password: {password is not None}')
"
else
    echo "WARNING: Superuser not created. Required environment variables not set."
    echo "Please ensure DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD are set."
fi
echo "======================================================"
echo ""

# Execute the main command
exec "$@"
