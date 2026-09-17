"""
Notification tasks for DocuAgent AI Celery workers.
"""

from celery.utils.log import get_task_logger

from app.celery import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_job_completion")
def send_job_completion(self, job_id: str, recipient: str, message: str):
    """
    Celery task to send job completion notifications.

    Args:
        job_id: Unique identifier for the job
        recipient: Notification recipient (email, webhook URL, etc.)
        message: Notification message

    Returns:
        dict: Result containing success status
    """
    try:
        logger.info(f"Sending job completion notification for job {job_id} to {recipient}")

        # This would integrate with email service, Slack webhook, etc.
        # For now, we'll just log the notification
        logger.info(f"Notification sent to {recipient}: {message}")

        return {
            "success": True,
            "job_id": job_id,
            "recipient": recipient,
            "message": "Notification sent successfully",
        }

    except Exception as exc:
        logger.error(f"Failed to send notification for job {job_id}: {exc}")
        raise self.retry(exc=exc) from exc


@celery_app.task(name="app.tasks.notification_tasks.send_progress_update")
def send_progress_update(job_id: str, step_index: int, progress_data: dict):
    """
    Celery task to send progress updates during job processing.

    Args:
        job_id: Unique identifier for the job
        step_index: Current step index
        progress_data: Progress information to send

    Returns:
        dict: Result containing success status
    """
    try:
        logger.debug(f"Sending progress update for job {job_id}, step {step_index}")

        # This would send updates via WebSocket, SSE, or other real-time mechanisms
        # For now, we'll just log the progress
        logger.debug(f"Progress update for job {job_id}: {progress_data}")

        return {"success": True, "job_id": job_id, "step_index": step_index}

    except Exception as exc:
        logger.error(f"Failed to send progress update for job {job_id}: {exc}")
        # Don't retry progress updates as they're time-sensitive
        return {"success": False, "job_id": job_id, "error": str(exc)}
