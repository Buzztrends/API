pip install -r requirements.txt

gunicorn --bind "0.0.0.0:80" -w 2 "wsgi:app"
