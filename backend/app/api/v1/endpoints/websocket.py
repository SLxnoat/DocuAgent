"""
WebSocket Endpoint for Conversational Document Refinement (Agent 5)
===================================================================
wss://{host}/api/v1/ws/chat/{session_id}?token={api_token}

Implements bi-directional streaming communication between user and Agent 5:
  • Client → Server: "user_message", "ping"
  • Server → Client: "typing_start", "agent_response", "typing_stop", "pong", "error"
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.v1.endpoints.chat import _refine_markdown_content
from app.api.v1.endpoints.jobs import job_store
from app.chat_refiner import classify_chat_edit, extract_recapture_step_index
from app.langgraph_config import get_checkpointer
from app.models import ChangeSummaryItem, is_valid_uuid
from app.utils.sse_publisher import publish_sse_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    Bi-directional WebSocket endpoint for conversational refinement with Agent 5.
    Conforms strictly to DOC-004 Section 11 specifications.
    """
    await websocket.accept()
    logger.info("WebSocket connection established for session_id: %s", session_id)

    checkpointer = get_checkpointer()

    try:
        # Validate session ID format
        if not is_valid_uuid(session_id):
            await websocket.send_json(
                {
                    "type": "error",
                    "message": f"Invalid session ID format '{session_id}'. Must be UUIDv4.",
                }
            )
            await websocket.close(code=1008, reason="Invalid session ID")
            return

        # Continuous message processing loop
        while True:
            try:
                # Wait for client message with 25s timeout
                raw_data = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)
            except TimeoutError:
                # Keepalive timeout: perform WebSocket protocol ping/pong
                try:
                    await websocket.send_json({"type": "ping"})
                    continue
                except Exception:
                    logger.info(
                        "WebSocket keepalive ping failed for session %s. Closing.", session_id
                    )
                    break
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected for session_id: %s", session_id)
                break

            # Parse incoming JSON payload
            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            msg_type = message.get("type", "")

            # ── 1. Keepalive Ping / Pong ──────────────────────────────────────
            if msg_type == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )
                continue
            elif msg_type == "pong":
                continue

            # ── 2. User Chat Message ──────────────────────────────────────────
            elif msg_type in ("user_message", "chat_message"):
                content = message.get("content", "").strip()
                if not content:
                    await websocket.send_json(
                        {"type": "error", "message": "Message content cannot be empty"}
                    )
                    continue

                # Notify client that agent has started processing
                await websocket.send_json({"type": "typing_start"})

                try:
                    # Retrieve existing job state from Redis job_store or checkpointer
                    job_record = job_store.get_job_by_session_id(session_id)
                    job_id = job_record.get("job_id", "") if job_record else ""

                    current_markdown = ""
                    if job_record and job_record.get("markdown_content"):
                        current_markdown = job_record["markdown_content"]
                    elif message.get("context", {}).get("current_markdown"):
                        current_markdown = message["context"]["current_markdown"]

                    # Determine intent
                    edit_type = classify_chat_edit(content)

                    # Case A: Screenshot Recapture
                    if edit_type == "recapture_trigger":
                        step_idx = extract_recapture_step_index(content)
                        recapture_step = step_idx if step_idx is not None else 0
                        step_display = recapture_step + 1

                        reply_text = (
                            f"I've initiated a screenshot re-capture for Step {step_display}."
                        )
                        summaries = [
                            ChangeSummaryItem(
                                section=f"Step {step_display}",
                                change_type="recapture_trigger",
                                description=f"Initiated re-capture for step {step_display}",
                            )
                        ]

                        if job_id:
                            job_store.update_job(
                                job_id,
                                {
                                    "recapture_step_index": recapture_step,
                                    "status": "awaiting_input",
                                },
                            )

                        # Send DOC-004 compliant agent_response
                        await websocket.send_json(
                            {
                                "type": "agent_response",
                                "content": reply_text,
                                "updated_markdown": current_markdown,
                                "changes_summary": [s.model_dump() for s in summaries],
                                "recapture_triggered": True,
                                "recapture_step_index": recapture_step,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                    # Case B: Document Refinement
                    else:
                        updated_md, reply_text, summaries = _refine_markdown_content(
                            current_markdown=current_markdown,
                            user_message=content,
                            edit_type=edit_type,
                        )

                        # Persist to Redis job_store
                        if job_id:
                            job_store.update_job(
                                job_id,
                                {
                                    "markdown_content": updated_md,
                                    "status": "awaiting_input",
                                },
                            )

                            # Also sync to LangGraph checkpointer if active
                            with contextlib.suppress(Exception):
                                checkpointer.put(
                                    {"configurable": {"thread_id": session_id}},
                                    {"markdown_content": updated_md},
                                    {},
                                    "1",
                                )

                            # Broadcast SSE event for synchronized multi-tab updates
                            try:
                                await publish_sse_event(
                                    job_id=job_id,
                                    event_type="document_updated",
                                    data={
                                        "markdown": updated_md,
                                        "changes_summary": [s.model_dump() for s in summaries],
                                        "response_message": reply_text,
                                    },
                                )
                            except Exception as exc:
                                logger.warning("SSE publish failed during WS refinement: %s", exc)

                        # Send DOC-004 compliant agent_response
                        await websocket.send_json(
                            {
                                "type": "agent_response",
                                "content": reply_text,
                                "updated_markdown": updated_md,
                                "changes_summary": [s.model_dump() for s in summaries],
                                "recapture_triggered": False,
                                "recapture_step_index": None,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                except Exception as proc_exc:
                    logger.exception(
                        "Error processing chat refinement for session %s: %s", session_id, proc_exc
                    )
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Refinement processing failed: {proc_exc!s}",
                        }
                    )
                finally:
                    # Signal typing completion
                    await websocket.send_json({"type": "typing_stop"})

            # ── 3. Unsupported Message Type ───────────────────────────────────
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unsupported message type '{msg_type}'. Expected 'user_message' or 'ping'.",
                    }
                )

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed cleanly for session_id: %s", session_id)
    except Exception as exc:
        logger.error("Unhandled WebSocket exception for session_id %s: %s", session_id, exc)
        with contextlib.suppress(Exception):
            await websocket.send_json(
                {"type": "error", "message": f"Internal server error: {exc!s}"}
            )
