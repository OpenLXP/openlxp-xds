#!/usr/bin/env bash
# start-server.sh

python manage.py waitdb 
python manage.py migrate --skip-checks --database default
python manage.py createcachetable 
python manage.py loaddata admin_theme_data.json 
python manage.py loaddata openlxp_email_templates.json 
python manage.py loaddata openlxp_email_subject.json 
python manage.py loaddata openlxp_email.json 
python manage.py collectstatic --no-input
cd /opt/app/ 
pwd 
./start-server.sh