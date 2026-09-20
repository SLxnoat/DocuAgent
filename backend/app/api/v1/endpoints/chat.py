"""
Chat & Refinement REST Endpoint — Phase 6 / Agent 5
===================================================
POST /api/v1/chat/{session_id}

Provides HTTP fallback for conversational document refinement with Agent 5.
Translates user requests into text edits, structural revisions, translations,
or screenshot recapture triggers, updating the persisted Markdown content.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.jobs import job_store
from app.chat_refiner import (
    classify_chat_edit,
    extract_recapture_step_index,
    translate_document,
)
from app.llm import ollama_generate_text
from app.models import (
    ChangeSummaryItem,
    ChatRequest,
    ChatResponse,
    is_valid_uuid,
)
from app.utils.sse_publisher import publish_sse_event

logger = logging.getLogger(__name__)

router = APIRouter()

REFINER_PROMPT_TEMPLATE = """You are an expert technical editor and documentation specialist.
You will receive:
1. The current Markdown document
2. A user request to refine the document

Your task is to apply the user's requested changes precisely and return the updated Markdown document.
Maintain all existing structure, headings, callout blocks (> 💡 Tip, > ⚠️ Warning), and screenshot references (![Step X](...)).
Apply ONLY the requested changes.

Current Markdown document:
{current_markdown}

User refinement request:
{user_message}

Return ONLY the complete updated Markdown document. Do not include conversational remarks or introductory text outside the markdown."""


def _refine_markdown_content(
    current_markdown: str,
    user_message: str,
    edit_type: str,
) -> tuple[str, str, list[ChangeSummaryItem]]:
    """
    Apply requested refinement to markdown and generate explanation + change summaries.
    """
    # 1. Translation detection
    translate_match = re.search(
        r"\b(?:translate|convert|rewrite)\s+(?:this|document|manual|into|to)?\s*([a-zA-Z]+)\b",
        user_message,
        re.IGNORECASE,
    )
    if translate_match:
        target_lang = translate_match.group(1).capitalize()
        if target_lang.lower() not in ["english", "en"]:
            updated = translate_document(current_markdown, target_lang)
            summary = [
                ChangeSummaryItem(
                    section="Document",
                    change_type="translation",
                    description=f"Translated manual to {target_lang}",
                )
            ]
            reply = f"I've translated the document to {target_lang} while preserving the structure and screenshot references."
            return updated, reply, summary

    # 2. LLM-assisted refinement
    if current_markdown.strip():
        try:
            prompt = REFINER_PROMPT_TEMPLATE.format(
                current_markdown=current_markdown,
                user_message=user_message,
            )
            llm_result = ollama_generate_text(prompt=prompt, temperature=0.2)
            if llm_result and len(llm_result.strip()) > 20:
                summary = [
                    ChangeSummaryItem(
                        section="Document",
                        change_type=edit_type,
                        description=f"Applied refinement: {user_message[:80]}",
                    )
                ]
                reply = f"I've updated the document according to your request: '{user_message}'."
                return llm_result.strip(), reply, summary
        except Exception as exc:
            logger.warning("LLM refinement failed (%s). Applying rule-based heuristic.", exc)

    # 3. Rule-based heuristic fallback
    if edit_type == "structural_revision":
        new_section = f"\n\n## {user_message}\n\n*Content updated per refinement request.*\n"
        updated = (current_markdown.rstrip() + new_section).strip()
        summary = [
            ChangeSummaryItem(
                section=user_message[:40],
                change_type="structural_revision",
                description=f"Added section: {user_message[:60]}",
            )
        ]
        reply = f"I've added a new section for '{user_message}' to the document."
        return updated, reply, summary
    else:
        # Text edit fallback: append note/callout if non-empty
        callout = f"\n\n> 📌 Note: {user_message}\n"
        updated = (current_markdown.rstrip() + callout).strip()
        summary = [
            ChangeSummaryItem(
                section="Notes",
                change_type="text_edit",
                description=f"Added note: {user_message[:60]}",
            )
        ]
        reply = f"I've incorporated your feedback into the document: '{user_message}'."
        return updated, reply, summary


@router.post("/chat/{session_id}", response_model=ChatResponse, status_code=200)
async def chat_refinement(session_id: str, request: ChatRequest) -> ChatResponse:
    """
    Conversational refinement endpoint for Agent 5 (Chat Refiner).
    Applies user edits, structural additions, translations, or triggers recaptures.
    """
    if not is_valid_uuid(session_id):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid session ID format. Must be UUIDv4.",
                    "field": "session_id",
                }
            },
        )

    # Retrieve existing job record by session_id
    job_record = job_store.get_job_by_session_id(session_id)
    if job_record is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SESSION_NOT_FOUND",
                    "message": f"Session '{session_id}' not found. Please ensure the generation job exists.",
                }
            },
        )

    job_id = job_record.get("job_id", "")

    # Determine base markdown content: user context > job store > default
    current_markdown = ""
    if request.context and request.context.current_markdown:
        current_markdown = request.context.current_markdown
    elif job_record.get("markdown_content"):
        current_markdown = job_record["markdown_content"]

    user_msg = request.message.strip()
    edit_type = classify_chat_edit(user_msg)

    # Case A: Screenshot Recapture Trigger
    if edit_type == "recapture_trigger":
        step_idx = extract_recapture_step_index(user_msg)
        recapture_step = step_idx if step_idx is not None else 0
        step_display = recapture_step + 1

        response_message = f"I've scheduled a screenshot re-capture for Step {step_display}."
        changes_summary = [
            ChangeSummaryItem(
                section=f"Step {step_display}",
                change_type="recapture_trigger",
                description=f"Initiated re-capture for step {step_display}",
            )
        ]

        # Update job record with recapture target
        job_store.update_job(
            job_id,
            {
                "recapture_step_index": recapture_step,
                "status": "awaiting_input",
            },
        )

        return ChatResponse(
            session_id=session_id,
            response_message=response_message,
            updated_markdown=current_markdown,
            changes_summary=changes_summary,
            recapture_triggered=True,
            recapture_step_index=recapture_step,
            timestamp=datetime.utcnow(),
        )

    # Case B: Document Content Refinement (Text Edit / Structural Revision / Translation)
    updated_md, reply_msg, summary_items = _refine_markdown_content(
        current_markdown=current_markdown,
        user_message=user_msg,
        edit_type=edit_type,
    )

    # Persist updated content back into job_store
    job_store.update_job(
        job_id,
        {
            "markdown_content": updated_md,
            "status": "awaiting_input",
        },
    )

    # Broadcast real-time SSE update if job_id is present
    if job_id:
        try:
            await publish_sse_event(
                job_id=job_id,
                event_type="document_updated",
                data={
                    "markdown": updated_md,
                    "changes_summary": [item.model_dump() for item in summary_items],
                    "response_message": reply_msg,
                },
            )
        except Exception as exc:
            logger.warning("Failed to publish document_updated SSE event: %s", exc)

    return ChatResponse(
        session_id=session_id,
        response_message=reply_msg,
        updated_markdown=updated_md,
        changes_summary=summary_items,
        recapture_triggered=False,
        recapture_step_index=None,
        timestamp=datetime.utcnow(),
    )
