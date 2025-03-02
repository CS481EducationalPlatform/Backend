#!/usr/bin/env bash
# Exit on error
set -o errexit

# Change to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install additional required packages for Render
pip install gunicorn uvicorn

# Generate SECRET_KEY if not set
if [ -z "${SECRET_KEY}" ]; then
    echo "SECRET_KEY is not set. Generating a new one..."
    export SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    echo "A new SECRET_KEY has been generated. Please set this in your Render environment variables:"
    echo $SECRET_KEY
fi

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if environment variables are set
if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD}" ]] && [[ -n "${DJANGO_SUPERUSER_EMAIL}" ]]; then
    python manage.py createsuperuser --noinput
fi 