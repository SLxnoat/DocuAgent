import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.models import GenerateRequest, GenerateResponse
from app.tasks.generation_tasks import generate_manual as generate_manual_task
from app.utils.url_validator import validate_target_url

from .jobs import create_job_record

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate_manual(request: GenerateRequest):
    """
    Accepts a generation request, validates input and target URL against SSRF,
    triggers a Celery task, and returns a job_id and session_id for tracking.
    """
    target_url = request.get_target_url()

    # SSRF Guardrail: Validate URL does not target loopback or private networks
    try:
        validate_target_url(target_url)
    except Exception as exc:
        logger.warning("SSRF blocked or invalid target_url: %s (%s)", target_url, exc)
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Target URL failed security validation: {exc}",
                    "field": "target_url",
                }
            },
        ) from exc

    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Create the job record in the store
    create_job_record(job_id, session_id)

    try:
        generate_manual_task.delay(
            job_id=job_id,
            session_id=session_id,
            target_url=target_url,
            credentials=request.credentials or {},
            raw_input_script=request.script,
            options=request.options or {},
        )
        logger.info("Dispatched generate_manual task for job_id=%s", job_id)
    except Exception as exc:
        logger.warning(
            "Could not dispatch Celery task for job %s (broker may be offline): %s",
            job_id,
            exc,
        )

    return GenerateResponse(job_id=job_id, session_id=session_id)
