#!/usr/bin/env bash
# start-server.sh

python manage.py waitdb 
python manage.py migrate 
python manage.py loaddata admin_theme_data.json 
cd /opt/app/ 
pwd 
./start-server.sh