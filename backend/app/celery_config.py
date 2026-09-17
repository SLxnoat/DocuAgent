"""
Celery configuration for DocuAgent AI.
Configures Celery app with Redis broker and result backend for task distribution.
"""

from celery import Celery

from app.config import settings

# Create Celery instance
celery_app = Celery(
    "docuagent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.generation_tasks",  # For document generation tasks
        "app.tasks.capture_tasks",  # For capture-related tasks
        "app.tasks.export_tasks",  # For export-related tasks
        "app.tasks.notification_tasks",  # For notification tasks
        "app.tasks.maintenance_tasks",  # For maintenance tasks
    ],
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.celery_task_timeout_seconds,
    task_soft_time_limit=settings.celery_task_timeout_seconds - 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=settings.celery_max_tasks_per_child,
    worker_disable_rate_limits=False,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        # Route tasks to specific queues if needed
        "app.tasks.generation_tasks.*": {"queue": "generation"},
        "app.tasks.capture_tasks.*": {"queue": "capture"},
        "app.tasks.export_tasks.*": {"queue": "export"},
    },
)

# Optional: Configure task annotations for specific tasks
celery_app.conf.task_annotations = {
    "*": {"rate_limit": "10/s"},  # Default rate limit
    "app.tasks.generation_tasks.generate_document": {
        "rate_limit": "2/m",  # Limit document generation to 2 per minute
        "time_limit": 600,  # 10 minutes max for generation
    },
}

if __name__ == "__main__":
    celery_app.start()
