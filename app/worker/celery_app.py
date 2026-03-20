from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.autodiscover_tasks(["app.worker"], force=True)

celery_app.conf.beat_schedule = {
    "dispatch-every-1-min": {
        "task": "dispatch_reminders_batch",
        "schedule": 60.0,
    },
}

celery_app.conf.timezone = "UTC"