#!/usr/bin/env bash
set -o errexit

echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo "=== Verificando configuración ==="
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-No configurado}"
echo "DATABASE_URL: ${DATABASE_URL:-No configurada}"

echo "=== Recolectando archivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== Aplicando migraciones ==="
python manage.py migrate --noinput

echo "=== Build completado exitosamente ==="