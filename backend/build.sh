#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install additional required packages for Render
pip install gunicorn uvicorn

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
