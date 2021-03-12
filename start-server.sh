#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd openlxp-xds; python manage.py createsuperuser --no-input)
fi
(cd openlxp-xds; gunicorn openlxp_xds_project.wsgi --reload --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
