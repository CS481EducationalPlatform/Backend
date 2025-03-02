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