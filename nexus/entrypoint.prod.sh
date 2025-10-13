#!/bin/sh

# Set Elasticsearch host
ES_HOST="http://es-nexus:9200"
MAX_RETRIES=20
SLEEP_INTERVAL=3

echo "Waiting for Elasticsearch at $ES_HOST..."

COUNT=0
while ! curl -s $ES_HOST >/dev/null 2>&1; do
    # COUNT=$((COUNT+1))
    # if [ $COUNT -ge $MAX_RETRIES ]; then
    #     echo "ERROR: Elasticsearch did not start in time!"
    #     exit 1
    # fi
    # echo "Elasticsearch not ready, retrying in $SLEEP_INTERVAL seconds..."
    sleep $SLEEP_INTERVAL
done

echo "Elasticsearch is up! Running migrations, collecting static files, and indexing..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py search_index --rebuild -f

echo "Starting Django..."
exec "$@"
