#!/bin/sh
echo "Waiting for PostgreSQL to start..."
sleep 5
python manage.py migrate
python manage.py collectstatic --noinput
exec "$@"
