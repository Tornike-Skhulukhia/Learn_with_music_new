#! /bin/bash

echo "starting app"

# wait for DB
wait-for-it -t 30 -s postgres:5432

# make sure database tables exist and are ready
python -m base.startapp_script

# start app
python /app/manage.py runserver 0.0.0.0:8000

# gunicorn --bind 0.0.0.0:8000 --config app.gunicorn.conf.py config.wsgi  # add gunicorn later
