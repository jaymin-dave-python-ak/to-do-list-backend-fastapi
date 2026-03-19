from celery import Celery
from app.core.config import settings


celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.task_routes = {}

# This tells Celery where to look for tasks
celery_app.autodiscover_tasks(["app.service"], related_name="email_service", force=True)
