import uuid

from fastapi import APIRouter

from app.models import GenerateRequest, GenerateResponse

from .jobs import create_job_record

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate_manual(request: GenerateRequest):
    """
    Accepts a generation request, validates input, triggers a Celery task,
    and returns a job_id and session_id for tracking.
    """
    # The request has already been validated by Pydantic (script length, URL validity)
    # For now, we generate dummy IDs. In a real implementation, we would:
    # 1. Create a job record in the store (via create_job_record).
    # 2. Send a Celery task to process the generation.
    # 3. Return the job_id and session_id.

    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Create the job record in the store
    create_job_record(job_id, session_id)

    # TODO: Trigger Celery task here
    # Example: generate_manual_task.delay(job_id=job_id, session_id=session_id, script=request.script, url=str(request.url), ...)

    return GenerateResponse(job_id=job_id, session_id=session_id)
