"""
Export Endpoint — Phase 7
=========================
GET /api/v1/export/{job_id}?format={markdown|html|pdf}

Generates (or serves from cache) the document in the requested format and
streams it back as a binary response with proper Content-Type and
Content-Disposition headers.

Job markdown content is retrieved from the in-memory job_store (Phase 7)
or from the persisted export cache if the store is cold (e.g. after restart).
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.models import is_valid_uuid
from app.services.export_service import (
    CONTENT_TYPES,
    FILE_EXTENSIONS,
    SUPPORTED_FORMATS,
    export_document,
    get_export_path,
)

from .jobs import job_store  # shared in-memory store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/export/{job_id}")
async def export_job(
    job_id: str,
    format: str = Query(
        ...,
        description="Export format: markdown, html, or pdf",
        examples=["markdown", "html", "pdf"],
    ),
) -> FileResponse:
    """
    Generate and download the manual for *job_id* in the specified *format*.

    - **markdown**: Returns the raw ``.md`` source.
    - **html**: Returns a standalone ``.html`` file with base64-inlined screenshots.
    - **pdf**: Returns a print-ready ``.pdf`` generated via WeasyPrint.

    The first call for each format triggers conversion; subsequent calls are
    served from the on-disk cache without re-processing.
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid job ID format. Must be UUIDv4.",
                }
            },
        )

    fmt = format.lower().strip()

    # ── Validate format ──────────────────────────────────────────────────────
    if fmt not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "EXPORT_FORMAT_UNSUPPORTED",
                    "message": (
                        f"Unsupported export format '{fmt}'. "
                        f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
                    ),
                }
            },
        )

    # ── Validate job exists ───────────────────────────────────────────────────
    if job_id not in job_store:
        # Check if we have a cached export file even without a live store entry
        cached = get_export_path(job_id, fmt)
        if cached.exists():
            logger.info("Serving cached export (cold store): job=%s fmt=%s", job_id, fmt)
            return _build_response(job_id, fmt, cached)

        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job '{job_id}' not found.",
                }
            },
        )

    job_data = job_store[job_id]
    job_status = job_data.get("status", "")

    # ── Check job is in an exportable state ──────────────────────────────────
    exportable_statuses = {"completed", "awaiting_input", "refining"}
    if job_status not in exportable_statuses:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "JOB_STILL_PROCESSING",
                    "message": (
                        f"Job '{job_id}' is still processing (status: {job_status}). "
                        "Export is available once the job reaches 'completed' or "
                        "'awaiting_input' status."
                    ),
                }
            },
        )

    # ── Retrieve markdown content ─────────────────────────────────────────────
    markdown_content: str = job_data.get("markdown_content", "")
    if not markdown_content:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "JOB_STILL_PROCESSING",
                    "message": "Markdown content is not yet available for this job.",
                }
            },
        )

    # ── Generate (or serve cached) export ────────────────────────────────────
    try:
        out_path: Path = export_document(
            job_id=job_id,
            markdown_content=markdown_content,
            fmt=fmt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": {"message": str(exc)}}) from exc
    except RuntimeError as exc:
        logger.exception("Export generation failed: job=%s fmt=%s", job_id, fmt)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    return _build_response(job_id, fmt, out_path)


def _build_response(job_id: str, fmt: str, file_path: Path) -> FileResponse:
    """Construct a FileResponse with correct Content-Type and Content-Disposition."""
    ext = FILE_EXTENSIONS[fmt]
    filename = f"manual_{job_id}.{ext}"
    return FileResponse(
        path=str(file_path),
        media_type=CONTENT_TYPES[fmt],
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Export-Format": fmt,
        },
    )
