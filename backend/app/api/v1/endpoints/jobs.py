import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.models import JobStatusResponse, is_valid_uuid
from app.services.job_store import job_store

logger = logging.getLogger(__name__)

router = APIRouter()


def create_job_record(job_id: str, session_id: str) -> dict:
    """
    Create a new job record in Redis/store with initial pending status.
    """
    return job_store.create_job(job_id, session_id)


def _cleanup_old_files(directory: str, retention_hours: int) -> None:
    """
    Clean up files older than the retention period.

    Args:
        directory: Directory to clean up
        retention_hours: Number of hours to retain files
    """
    import time
    from pathlib import Path

    current_time = time.time()
    cutoff_time = current_time - (retention_hours * 3600)

    try:
        directory_path = Path(directory)
        for file_path in directory_path.iterdir():
            # Check if it's a file (not a directory)
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    file_path.unlink()
    except Exception:
        pass


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status and metadata of a job by job_id.
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format. Must be UUIDv4.")

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = job_store[job_id]
    # Map the stored data to the JobStatusResponse model
    return JobStatusResponse(
        job_id=job_data["job_id"],
        status=job_data["status"],
        progress=job_data["progress"],
        step_statuses=job_data["step_statuses"],
        result_url=job_data["result_url"],
        error=job_data["error"],
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and terminate active execution if any.
    Purges temporary assets associated with the job.
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format. Must be UUIDv4.")

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = job_store.get(job_id)
    if job_data and job_data.get("celery_task_id"):
        try:
            from app.celery import celery_app

            celery_app.control.revoke(job_data["celery_task_id"], terminate=True)
        except Exception:
            pass

    # Purge temporary assets associated with this job
    try:
        assets_dir = Path(settings.assets_dir) / job_id
        if assets_dir.exists():
            import shutil

            shutil.rmtree(assets_dir, ignore_errors=True)

        exports_dir = Path(settings.exports_dir) / job_id
        if exports_dir.exists():
            import shutil

            shutil.rmtree(exports_dir, ignore_errors=True)
    except Exception:
        pass

    # Remove job from store
    del job_store[job_id]

    return {"message": f"Job {job_id} has been deleted successfully", "job_id": job_id}


class RecaptureRequest(BaseModel):
    selector_override: str | None = None
    custom_screenshot_path: str | None = None


@router.post("/recapture/{job_id}/{step_index}", status_code=202)
async def recapture_step(
    job_id: str,
    step_index: int,
    payload: RecaptureRequest | None = None,
):
    """
    Trigger targeted single-step re-execution for a specific job and step.
    Implements DOC-004 Section 9 contract. Dispatches capture_tasks.recapture_step.
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format. Must be UUIDv4.")

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    if step_index < 0:
        raise HTTPException(status_code=400, detail="Step index must be non-negative")

    override = payload.selector_override if payload else None
    custom_path = payload.custom_screenshot_path if payload else None

    # Dispatch Celery background task to recapture queue
    try:
        from app.tasks.capture_tasks import recapture_step as celery_recapture_step

        celery_recapture_step.delay(
            job_id=job_id,
            step_index=step_index,
            selector_override=override,
            custom_screenshot_path=custom_path,
        )
    except Exception as exc:
        logger.warning("Could not dispatch Celery recapture task: %s", exc)

    return {
        "job_id": job_id,
        "step_index": step_index,
        "status": "recapture_queued",
        "stream_url": f"/api/v1/stream/{job_id}",
    }


@router.post("/jobs/{job_id}/assets/{step_index}")
async def upload_screenshot(job_id: str, step_index: int, file: UploadFile = File(...)):
    """
    Upload a replacement screenshot for a specific job and step.
    The screenshot will be saved as assets/{job_id}/step_{step_index:03d}.png
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format. Must be UUIDv4.")

    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    if step_index < 0:
        raise HTTPException(status_code=400, detail="Step index must be non-negative")

    # Validate file type (optional but recommended)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Create the assets directory for this job if it doesn't exist
    assets_dir = Path(settings.assets_dir) / job_id
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Define the file path
    file_path = assets_dir / f"step_{step_index:03d}.png"

    # Save the uploaded file
    try:
        contents = await file.read()
        with file_path.open("wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e!s}") from e
    finally:
        await file.close()

    # Update job's updated_at timestamp
    job_store.update_job(job_id, {"updated_at": datetime.utcnow()})

    # TODO: In a full implementation, we might want to:
    # 1. Validate that step_index is within the actual number of steps for this job
    # 2. Update the step status to indicate the asset has been replaced (if needed)
    # 3. Trigger a re-processing of the step if the workflow depends on the asset
    # 4. Return the relative path or URL to the uploaded asset

    return {
        "message": f"Screenshot uploaded successfully for job {job_id}, step {step_index}",
        "job_id": job_id,
        "step_index": step_index,
        "filename": file.filename,
        "saved_path": str(file_path),
        "content_type": file.content_type,
    }
