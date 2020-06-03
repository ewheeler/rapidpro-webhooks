#!/bin/bash -e
mkdir -p /var/log/webhooks
python manage.py db upgrade

# nginx settings
# sets FORWARDED_ALLOW_IPS to 127.0.0.1 if not set
# FORWARDED_ALLOW_IPS="${FORWARDED_ALLOW_IPS:-127.0.0.1}"

if [[ "$*" == "worker" ]];then
    exec celery -A rapidpro_webhooks.core worker \
        --concurrency=4 \
        --max-tasks-per-child=1 \
        --loglevel=${CELERY_LOGLEVEL} \
        --autoscale=${CELERY_AUTOSCALE} \
        --pidfile /var/run/celery.pid

elif [[ "$*" == "rapidpro-webhooks" ]];then
    exec gunicorn manage:app \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --access-logfile - \
        --log-level debug
else
    echo error
    exec "$@"
fi