#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py collectstatic --noinput
RUN_PORT="8000"

python manage.py migrate --noinput
gunicorn core.wsgi:application --bind "0.0.0.0:${RUN_PORT}" --daemon --access-logfile /dev/stdout --capture-output --log-level warn

nginx -g 'daemon off;error_log /dev/stdout warn;'
exec "$@"
