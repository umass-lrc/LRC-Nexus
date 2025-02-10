#!/bin/sh

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch..."
while ! curl -s http://es-nexus:9200 >/dev/null; do
  sleep 3
done

echo "Elasticsearch is up! Running migrations, collecting static files, and indexing..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py search_index --rebuild -f

echo "Starting Django..."
exec "$@"
