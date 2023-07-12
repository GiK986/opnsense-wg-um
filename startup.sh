#!/bin/sh
# This script is run at startup to start the application.
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --config gunicorn-cfg.py core.wsgi