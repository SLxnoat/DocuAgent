"""
Export tasks for DocuAgent AI Celery workers.
Executes background document compilation and rendering (Markdown, HTML, PDF).
"""

from __future__ import annotations

from typing import Any

from app.celery import celery_app
from app.services.export_service import export_document
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.export_tasks.export_manual")
def export_manual(self, job_id: str, fmt: str) -> dict[str, Any]:
    """
    Celery task to compile and export a manual into markdown, html, or pdf format.
    """
    logger.info("Starting background export task for job %s, format %s", job_id, fmt)

    from app.services.job_store import job_store

    job = job_store.get(job_id)
    if not job:
        logger.error("Job %s not found in job_store for export", job_id)
        return {"success": False, "error": f"Job {job_id} not found"}

    markdown_content = job.get("markdown_content")
    if not markdown_content:
        logger.error("No markdown_content for job %s", job_id)
        return {"success": False, "error": f"No markdown content for job {job_id}"}

    try:
        export_file = export_document(job_id=job_id, markdown_content=markdown_content, fmt=fmt)
        logger.info("Export completed for job %s (%s): %s", job_id, fmt, export_file)
        return {
            "success": True,
            "job_id": job_id,
            "format": fmt,
            "file_path": str(export_file),
        }
    except Exception as exc:
        logger.error("Export failed for job %s (%s): %s", job_id, fmt, exc)
        raise self.retry(exc=exc, countdown=5, max_retries=2) from exc
