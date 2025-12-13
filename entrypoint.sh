#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()

u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

if u and p:
    if not User.objects.filter(username=u).exists():
        User.objects.create_superuser(username=u, email=e, password=p)
        print('Superuser created:', u)
    else:
        print('Superuser already exists:', u)
"

gunicorn config.wsgi:application --bind 0.0.0.0:8000

exec "$@"
