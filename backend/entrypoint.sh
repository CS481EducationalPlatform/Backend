#!/bin/sh

# Print important environment variables at the start for debugging
echo ""
echo "======================================================"
echo "INITIAL ENVIRONMENT VARIABLES"
echo "======================================================"
echo "DATABASE_URL: $(if [ -n "$DATABASE_URL" ]; then echo "EXISTS (value hidden)"; else echo "NOT SET"; fi)"
echo "DJANGO_SUPERUSER_PASSWORD exists: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "YES"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_USERNAME exists: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "YES"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_EMAIL exists: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "YES"; else echo "NO"; fi)"
echo "======================================================"
echo ""

# Investigate strange behavior where username is found but password is not
echo "Debug investigation - why is username found but not password:"
echo "Environment variables list (grep):"
printenv | grep -E "DJANGO_SUPERUSER_USERNAME|DJANGO_SUPERUSER_EMAIL|DJANGO_SUPERUSER_PASSWORD" | cut -d= -f1
echo "Checking /etc/environment:"
if [ -f "/etc/environment" ]; then
    echo "Contents of /etc/environment:"
    cat /etc/environment | grep -E "DJANGO_SUPERUSER"
else
    echo "/etc/environment does not exist"
fi
echo ""

# Store original DATABASE_URL to ensure it's preserved
ORIGINAL_DATABASE_URL="$DATABASE_URL"

# Check for .env file in ROOT directory first (this is where the variables are)
if [ -f "/.env" ]; then
    echo "Loading environment variables from ROOT /.env"
    # First, let's look at what's in this file
    echo "Contents of /.env (grep for DJANGO):"
    grep -E "DJANGO_SUPERUSER" /.env
    set -a
    . /.env
    set +a
    echo "After loading /.env:"
    echo "DJANGO_SUPERUSER_USERNAME: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_EMAIL: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_PASSWORD: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "SET"; else echo "NOT SET"; fi)"
fi

# Also check for .env in the current directory
if [ -f ".env" ]; then
    echo "Loading environment variables from current directory .env"
    echo "Contents of .env (grep for DJANGO):"
    grep -E "DJANGO_SUPERUSER" .env
    set -a
    . ./.env
    set +a
    echo "After loading ./.env:"
    echo "DJANGO_SUPERUSER_USERNAME: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_EMAIL: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_PASSWORD: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "SET"; else echo "NOT SET"; fi)"
fi

# Source environment variables if .env exists in the app root
if [ -f "/backend_app/.env" ]; then
    echo "Loading environment variables from /backend_app/.env"
    echo "Contents of /backend_app/.env (grep for DJANGO):"
    grep -E "DJANGO_SUPERUSER" /backend_app/.env
    set -a
    . /backend_app/.env
    set +a
    echo "After loading /backend_app/.env:"
    echo "DJANGO_SUPERUSER_USERNAME: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_EMAIL: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "SET"; else echo "NOT SET"; fi)"
    echo "DJANGO_SUPERUSER_PASSWORD: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "SET"; else echo "NOT SET"; fi)"
fi

# Debug: Print environment variables for troubleshooting
echo ""
echo "======================================================"
echo "ENVIRONMENT VARIABLES DEBUG"
echo "======================================================"
echo "DJANGO_SUPERUSER_USERNAME exists: $(if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then echo "YES (value: $DJANGO_SUPERUSER_USERNAME)"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_EMAIL exists: $(if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then echo "YES (value: $DJANGO_SUPERUSER_EMAIL)"; else echo "NO"; fi)"
echo "DJANGO_SUPERUSER_PASSWORD exists: $(if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "YES (length: ${#DJANGO_SUPERUSER_PASSWORD})"; else echo "NO"; fi)"
# Show password with redacted characters to debug format issues
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    PASSWORD_LENGTH=${#DJANGO_SUPERUSER_PASSWORD}
    echo "Password format check: ${PASSWORD_LENGTH} chars, starts with: ${DJANGO_SUPERUSER_PASSWORD:0:1}XXXXX, ends with: XXXXX${DJANGO_SUPERUSER_PASSWORD: -1}"
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

# Create superuser with custom management command
echo ""
echo "======================================================"
echo "RUNNING CUSTOM MANAGEMENT COMMAND TO CREATE SUPERUSER"
echo "======================================================"
# Run our custom management command which handles environment variable issues
python manage.py create_admin_superuser
echo "======================================================"
echo ""

# Execute the main command
exec "$@"
