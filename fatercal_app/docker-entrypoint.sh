#!/bin/bash
set -e

# certification uniquement la premiere fois
#certbot --apache -d fatercal.ird.nc

echo "Test the postgres connection..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_DB -c '\l'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
>&2 echo "Postgres is up - continuing"

#echo "Collect static files..."
python3 /app/manage.py collectstatic --noinput

# create django schema if not already exist
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_DB -d $POSTGRES_DB -c 'CREATE SCHEMA IF NOT EXISTS django;'

#echo "Apply database migrations (if needed)..."
python3 /app/manage.py migrate auth --database=django
python3 /app/manage.py migrate admin --database=django
python3 /app/manage.py migrate contenttypes --database=django
python3 /app/manage.py migrate dashboard --database=django
python3 /app/manage.py migrate jet --database=django
python3 /app/manage.py migrate sessions --database=django
python3 /app/manage.py migrate fatercal

exec "$@"
