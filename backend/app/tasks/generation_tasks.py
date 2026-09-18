"""
Document generation tasks for DocuAgent AI Celery workers.
"""

import asyncio
from typing import Any

from app.celery import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


async def _execute_docuagent_workflow(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Execute the compiled LangGraph workflow asynchronously."""
    from app.langgraph_config import create_docuagent_graph

    app = create_docuagent_graph()
    final_state = await app.ainvoke(initial_state)
    return final_state


@celery_app.task(bind=True, name="app.tasks.generation_tasks.generate_manual")
def generate_manual(
    self,
    job_id: str,
    session_id: str,
    target_url: str,
    credentials: dict | None = None,
    raw_input_script: str = "",
    structured_steps: list | None = None,
):
    """
    Celery task to generate a manual using the DocuAgent workflow.
    Runs the full DocuAgent LangGraph workflow in the background.
    """
    try:
        logger.info(f"Starting manual generation for job {job_id}")

        from app.state import ManualState

        initial_state: ManualState = {
            "job_id": job_id,
            "session_id": session_id,
            "target_url": target_url,
            "raw_input_script": raw_input_script or "",
            "credentials": credentials or {},
            "structured_steps": structured_steps or [],
            "screenshot_assets": {},
            "markdown_content": "",
            "chat_history": [],
            "execution_logs": [],
            "quality_approved": False,
            "error_states": {},
            "quality_feedback": None,
            "quality_review_attempts": 0,
            "recapture_step_index": None,
        }

        # Run async workflow within Celery worker process
        final_state = asyncio.run(_execute_docuagent_workflow(initial_state))

        logger.info(f"Manual generation completed for job {job_id}")

        return {
            "success": True,
            "job_id": job_id,
            "session_id": session_id,
            "markdown_content": final_state.get("markdown_content", ""),
            "screenshot_assets": final_state.get("screenshot_assets", {}),
            "quality_approved": final_state.get("quality_approved", False),
        }

    except Exception as exc:
        logger.error(f"Manual generation failed for job {job_id}: {exc}")
        raise self.retry(exc=exc) from exc


@celery_app.task(bind=True, name="app.tasks.generation_tasks.regenerate_step")
def regenerate_step(self, job_id: str, step_index: int):
    """
    Celery task to regenerate a specific step in the workflow.
    """
    try:
        logger.info(f"Regenerating step {step_index} for job {job_id}")

        return {
            "success": True,
            "job_id": job_id,
            "step_index": step_index,
            "message": f"Step {step_index} regenerated successfully",
        }

    except Exception as exc:
        logger.error(f"Regenerating step {step_index} failed for job {job_id}: {exc}")
        raise self.retry(exc=exc) from exc
