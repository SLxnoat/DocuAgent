import logging
import uuid

from fastapi import APIRouter

from app.models import GenerateRequest, GenerateResponse
from app.tasks.generation_tasks import generate_manual as generate_manual_task

from .jobs import create_job_record

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate_manual(request: GenerateRequest):
    """
    Accepts a generation request, validates input, triggers a Celery task,
    and returns a job_id and session_id for tracking.
    """
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    target_url = request.get_target_url()

    # Create the job record in the store
    create_job_record(job_id, session_id)

    try:
        generate_manual_task.delay(
            job_id=job_id,
            session_id=session_id,
            target_url=target_url,
            credentials=request.credentials or {},
            raw_input_script=request.script,
        )
        logger.info(f"Dispatched generate_manual task for job_id={job_id}")
    except Exception as exc:
        logger.warning(
            f"Could not dispatch Celery task for job {job_id} (broker may be offline): {exc}"
        )

    return GenerateResponse(job_id=job_id, session_id=session_id)
