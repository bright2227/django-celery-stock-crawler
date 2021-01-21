from __future__ import absolute_import, unicode_literals
from celery import Celery
from crawl.settings import db_url
import django
import os
import redis


pool = redis.ConnectionPool(host='redis', port=6379, decode_responses=True)
re = redis.Redis(connection_pool=pool)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawl.settings')

# app = Celery('crawl', backend='redis://redis:6379/1', broker='amqp://rabbitmq:5672/')
app = Celery('crawl', backend='redis://redis:6379/1', broker='redis://redis:6379/0')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')



# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task
def add(x, y):
    return x + y
