#!/bin/bash
set -e

echo "Test the postgres connection..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_DB -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - continuing"

#echo "Collect static files..."
python3 /app/manage.py collectstatic --noinput

#echo "Apply database migrations (if needed)..."
python3 /app/manage.py migrate

exec "$@"