# coding: utf-8

from __future__ import absolute_import, unicode_literals
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project}.settings')

import raven
from raven.contrib.celery import register_signal, register_logger_signal

import celery
# from celery.schedules import crontab


class Celery(celery.Celery):
    def on_configure(self):
        client = raven.Client('')
        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)
        # hook into the Celery error handler
        register_signal(client)

app = celery.Celery('{project}')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.imports += (
)

# 配置可见性超时为一周，可以满足时差在一周内的延时任务
app.conf.broker_transport_options = {
    'visibility_timeout': 604800,
}

app.conf.beat_schedule = {
}
