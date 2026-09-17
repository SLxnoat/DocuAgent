"""
WebSocket endpoint for bidirectional chat with Agent 5 (Chat Refiner Agent).
"""

import asyncio
import contextlib
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.chat_refiner import chat_refiner_node
from app.langgraph_config import get_checkpointer
from app.state import ManualState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for chat interactions with Agent 5.

    Args:
        websocket: The WebSocket connection.
        session_id: The session ID used to identify the state.
    """
    await websocket.accept()
    logger.info(f"WebSocket connection opened for session_id: {session_id}")

    # Get the checkpointer
    checkpointer = get_checkpointer()

    try:
        # Try to load the state for this session_id (as thread_id)
        # We assume the state has been saved by the LangGraph workflow
        # up to the point of the chat_refiner_node (i.e., after quality_review_node).
        state_dict = None
        try:
            # The checkpointer.get_tuple returns a tuple (checkpoint, metadata, parent_checkpoint, etc.)
            # We are interested in the checkpoint (which is the state).
            # Note: The checkpointer might not have the state if the workflow hasn't reached this point.
            # We'll try to get the state and if it doesn't exist, we'll wait a bit and try again?
            # For simplicity, we'll try once and if not found, we'll return an error.
            state_tuple = checkpointer.get_tuple({"configurable": {"thread_id": session_id}})
            if state_tuple is not None:
                state_dict = state_tuple.checkpoint  # This is the state dict
                logger.info(f"Loaded state for session_id: {session_id}")
            else:
                logger.warning(f"No state found for session_id: {session_id} in checkpointer")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "State not found. Please ensure the workflow has been started and paused at the chat refinement stage.",
                    }
                )
                await websocket.close()
                return
        except Exception as e:
            logger.error(f"Error loading state for session_id {session_id}: {e}")
            await websocket.send_json(
                {
                    "type": "error",
                    "message": f"Failed to load state: {e!s}",
                }
            )
            await websocket.close()
            return

        # Convert the dict to a ManualState (TypedDict) - we'll treat it as a dict for simplicity
        # Since ManualState is a TypedDict, we can use the dict directly as long as it has the required fields.
        state: ManualState = state_dict  # type: ignore

        # Main loop: receive messages, process them, and send back updates
        while True:
            # Wait for a message from the client with a timeout to allow for keep-alive pings
            try:
                # We'll wait for a message for 15 seconds (same as the heartbeat interval in SSE)
                # If we don't get a message in 15 seconds, we'll send a ping to keep the connection alive.
                data = await asyncio.wait_for(websocket.receive_text(), timeout=15.0)
            except TimeoutError:
                # No message received in 15 seconds, send a ping to keep the connection alive
                try:
                    await websocket.ping()
                    # Wait for a pong (we don't need to do anything with the pong, just waiting for it confirms the connection is alive)
                    # We'll wait for a pong for 5 seconds
                    pong_waiter = await websocket.pong()
                    await asyncio.wait_for(pong_waiter, timeout=5.0)
                    logger.debug(f"Ping/pong successful for session_id: {session_id}")
                    continue  # Go back to waiting for a message
                except TimeoutError:
                    logger.warning(
                        f"Ping/pong timeout for session_id: {session_id}. Closing connection."
                    )
                    await websocket.close(code=1001, reason="Keep-alive timeout")
                    return
                except Exception as e:
                    logger.error(f"Error during ping/pong for session_id {session_id}: {e}")
                    await websocket.close(code=1011, reason="Internal error")
                    return
            except WebSocketDisconnect:
                logger.info(f"WebSocket connection closed for session_id: {session_id}")
                break

            # If we got here, we have a message
            try:
                message = json.loads(data)
                if message.get("type") == "chat_message":
                    content = message.get("content", "")
                    if not content:
                        await websocket.send_json(
                            {"type": "error", "message": "Empty message received"}
                        )
                        continue

                    logger.info(
                        f"Received chat message for session_id {session_id}: {content[:100]}"
                    )

                    # Add the message to the chat history
                    # We need to append a ChatMessage with role="user" and the content, and a timestamp.
                    # We'll create a simple dict for the ChatMessage (since we don't have the ChatMessage class imported here? We do have it in state.py, but we can import it).
                    # However, to avoid circular imports, we'll create a dict that matches the ChatMessage structure.
                    # The ChatMessage is defined in models.py, but we can avoid importing it by using a dict.
                    # The state expects a list of ChatMessage, but we can store dicts and hope that the TypedDict is not enforced at runtime.
                    # Alternatively, we can import ChatMessage from models.
                    # Let's import it to be safe.
                    from datetime import datetime

                    from app.models import ChatMessage

                    chat_message = ChatMessage(
                        role="user",
                        content=content,
                        timestamp=datetime.now(),
                    )
                    # Get the current chat history and append the new message
                    chat_history = state.get("chat_history", [])
                    chat_history.append(chat_message)
                    state["chat_history"] = chat_history

                    # Process the message with the chat_refiner_node
                    updated_state = chat_refiner_node(state)

                    # Save the updated state back to the checkpointer
                    checkpointer.put(
                        {"configurable": {"thread_id": session_id}},
                        updated_state,
                        {},  # metadata
                        "1",  # version
                    )

                    # Prepare a response to send back to the client
                    response = {}

                    # If the markdown content has changed, send it back
                    if updated_state.get("markdown_content") != state.get("markdown_content"):
                        response["type"] = "markdown_update"
                        response["markdown"] = updated_state["markdown_content"]

                    # If a recapture step index is set, send a recapture request
                    recapture_step_index = updated_state.get("recapture_step_index")
                    if recapture_step_index is not None and recapture_step_index != state.get(
                        "recapture_step_index"
                    ):
                        response["type"] = "recapture_request"
                        response["step_index"] = recapture_step_index

                    # If we have a response, send it back
                    if response:
                        await websocket.send_json(response)

                    # Update the state for the next iteration
                    state = updated_state

                else:
                    await websocket.send_json(
                        {"type": "error", "message": f"Unknown message type: {message.get('type')}"}
                    )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON received"})
            except Exception as e:
                logger.error(f"Error processing message for session_id {session_id}: {e}")
                await websocket.send_json({"type": "error", "message": f"Internal error: {e!s}"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for session_id: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session_id {session_id}: {e}")
        with contextlib.suppress(Exception):
            await websocket.send_json({"type": "error", "message": f"WebSocket error: {e!s}"})
    finally:
        # Clean up: we don't close the checkpointer here because it's shared
        pass
