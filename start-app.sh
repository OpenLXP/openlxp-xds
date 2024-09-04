#!/usr/bin/env bash
# start-server.sh

python manage.py waitdb 
python manage.py migrate 
python manage.py createcachetable 
python manage.py collectstatic
python manage.py loaddata admin_theme_data.json 
python manage.py loaddata openlxp_email_subject.json 
python manage.py loaddata openlxp_email.json 
cd /tmp/app/ 
pwd 
./start-server.sh
