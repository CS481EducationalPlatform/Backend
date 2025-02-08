from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_project.settings")

backend_app = Celery("backend_project")
backend_app.config_from_object("django.conf:settings", namespace="CELERY")
backend_app.autodiscover_tasks()
