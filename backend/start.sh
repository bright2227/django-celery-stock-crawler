python manage.py runscript add_api_names
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
uwsgi -d --ini uwsgi.ini
chmod 755 ./--ini
rm /var/run/celerybeat.pid  # if you restart docker-compose after building it, you may ecounter error that celerybeat.pid is existed.
supervisord -c supervisord.conf

