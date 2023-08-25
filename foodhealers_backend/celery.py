from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

CELERY_ENABLED = True

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodhealers_backend.settings')
app = Celery('foodhealers_backend')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'daily-pending-events-email-notification': {
        'task': 'pending_events_email',
        'schedule': crontab(hour=12, minute=0),
    },

    'daily-event-status-check-notification': {
        'task': 'checking_event_status',
        'schedule': crontab(minute=0, hour='*/2'),
    },
}

