#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd /tmp/app/openlxp-xds/app; python manage.py createsuperuser --no-input)
fi
(cd /tmp/app/openlxp-xds/app; gunicorn openlxp_xds_project.wsgi --reload --user 1001 --bind 0.0.0.0:8100 --workers 3)
