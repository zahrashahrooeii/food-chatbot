#!/bin/bash

# Make migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 chatbot_project.wsgi:application 