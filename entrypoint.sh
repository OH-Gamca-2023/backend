#!/bin/bash
set -euo pipefail

python manage.py wait_for_database
python manage.py migrate --force-color

if [ "${1:-prod}" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000 --force-color
elif [ "${1:-prod}" = "huey" ]; then
  exec python manage.py run_huey
else
  python manage.py collectstatic --no-input
  exec gunicorn --bind 0.0.0.0:8000 --access-logfile - --log-file - --error-logfile - --workers 4 backend.wsgi
fi
