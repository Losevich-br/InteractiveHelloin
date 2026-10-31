#!/usr/bin/env bash
# Сборка на Render: зависимости, статика, миграции и создание ведущего.
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py ensure_superuser
