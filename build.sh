#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
pip install -r backend/requirements.txt

# Navigate to the backend directory
cd backend

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create Django admin superuser using our custom command
echo ""
echo "======================================================"
echo "STARTING DJANGO ADMIN SUPERUSER CREATION"
echo "======================================================"
echo "Environment variables:"
echo "DJANGO_SUPERUSER_USERNAME: ${DJANGO_SUPERUSER_USERNAME:-not set}"
echo "DJANGO_SUPERUSER_EMAIL: ${DJANGO_SUPERUSER_EMAIL:-not set}"
echo "DJANGO_SUPERUSER_PASSWORD: ${DJANGO_SUPERUSER_PASSWORD:+set but not shown}"
echo ""

python manage.py create_admin_superuser

echo ""
echo "======================================================"
echo "COMPLETED DJANGO ADMIN SUPERUSER CREATION"
echo "======================================================"
echo ""

# Output success message
echo "Build completed successfully!"
