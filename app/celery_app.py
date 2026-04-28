from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "image_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL,
)

celery_app.conf.update(
    include=["app.tasks.image_processing"],
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multipart=1,  # para procesamiento de archivos pesados
    task_acks_late=True,  # reenvia tarea si el worker muere
    task_rejec_on_worker_lost=True,
)
