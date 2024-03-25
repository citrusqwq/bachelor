#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput --clear

gunicorn ViViPlayer.wsgi:application --bind 0.0.0.0:8000 &
P1=$!
uvicorn ViViPlayer.asgi:application --reload --host 0.0.0.0 --port 9000 &
P2=$!
wait $P1 $P2