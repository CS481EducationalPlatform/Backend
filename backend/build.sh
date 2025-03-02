#!/usr/bin/env bash
# Exit on error
set -o errexit

# Change to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install additional required packages for Render
pip install gunicorn uvicorn

# Ensure SECRET_KEY is set before Django starts
if [ -z "${SECRET_KEY}" ]; then
    echo "Generating new SECRET_KEY..."
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
fi

# Create or update .env file
echo "SECRET_KEY='${SECRET_KEY}'" > .env
echo "DEBUG=False" >> .env

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if environment variables are set
if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD}" ]] && [[ -n "${DJANGO_SUPERUSER_EMAIL}" ]]; then
    python manage.py createsuperuser --noinput
fi 