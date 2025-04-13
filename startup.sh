#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Create and activate virtual environment
python -m venv antenv
source antenv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn whitenoise

# Make migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (non-interactive)
echo "Creating superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123!')
EOF

echo "Starting Gunicorn..."
# Start Gunicorn with proper settings for Azure
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout 600 --access-logfile - --error-logfile - chatbot_project.wsgi:application 