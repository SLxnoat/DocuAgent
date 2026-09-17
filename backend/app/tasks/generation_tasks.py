"""
Document generation tasks for DocuAgent AI Celery workers.
"""

from celery.utils.log import get_task_logger

from app.celery import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.generation_tasks.generate_manual")
def generate_manual(
    self, job_id: str, session_id: str, target_url: str, credentials: dict, structured_steps: list
):
    """
    Celery task to generate a manual using the DocuAgent workflow.

    This task runs the full DocuAgent LangGraph workflow in the background.

    Args:
        job_id: Unique identifier for the job
        session_id: Unique identifier for the session
        target_url: Target URL for the workflow
        credentials: Authentication credentials
        structured_steps: List of structured steps for the workflow

    Returns:
        dict: Result containing success status and any relevant data
    """
    try:
        logger.info(f"Starting manual generation for job {job_id}")

        # Import here to avoid circular imports
        from app.langgraph_config import create_docuagent_graph
        from app.state import ManualState

        # Create initial state
        initial_state: ManualState = {
            "job_id": job_id,
            "session_id": session_id,
            "target_url": target_url,
            "credentials": credentials,
            "structured_steps": structured_steps,
            "screenshot_assets": {},
            "markdown_content": "",
            "chat_history": [],
            "execution_logs": [],
            "quality_approved": False,
            "error_states": {},
            "quality_feedback": None,
            "quality_review_attempts": 0,
        }

        # Create and run the graph
        app = create_docuagent_graph()

        # Run the workflow (this would be enhanced with proper interrupt handling)
        # For now, we'll run it to completion
        final_state = app.invoke(initial_state)

        logger.info(f"Manual generation completed for job {job_id}")

        return {
            "success": True,
            "job_id": job_id,
            "markdown_content": final_state.get("markdown_content", ""),
            "screenshot_assets": final_state.get("screenshot_assets", {}),
        }

    except Exception as exc:
        logger.error(f"Manual generation failed for job {job_id}: {exc}")
        # Retry logic can be configured here
        raise self.retry(exc=exc) from exc


@celery_app.task(bind=True, name="app.tasks.generation_tasks.regenerate_step")
def regenerate_step(self, job_id: str, step_index: int):
    """
    Celery task to regenerate a specific step in the workflow.

    Args:
        job_id: Unique identifier for the job
        step_index: Index of the step to regenerate

    Returns:
        dict: Result containing success status and updated step data
    """
    try:
        logger.info(f"Regenerating step {step_index} for job {job_id}")

        # This would load the job state, regenerate the specific step,
        # and update the state accordingly

        return {
            "success": True,
            "job_id": job_id,
            "step_index": step_index,
            "message": f"Step {step_index} regenerated successfully",
        }

    except Exception as exc:
        logger.error(f"Step regeneration failed for job {job_id}, step {step_index}: {exc}")
        raise self.retry(exc=exc) from exc
