#!/bin/sh
# This script is run at startup to start the application.
python manage.py migrate
python manage.py runserver 0.0.0.0:8000