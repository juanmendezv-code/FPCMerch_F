#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py ensure_catalog
python manage.py sync_catalog_images
python manage.py collectstatic --noinput
