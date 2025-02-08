#!/bin/sh
echo "Waiting for PostgreSQL to start..."
sleep 5
exec "$@"
