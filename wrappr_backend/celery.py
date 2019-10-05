from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wrappr_backend.settings')

os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

import configurations

configurations.setup()

app = Celery('wrappr')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
