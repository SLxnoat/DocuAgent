"""
Agent 2: Playwright Visual Capturer for DocuAgent AI.
Orchestrates browser automation to capture screenshots based on structured steps.
"""

import random

from app.action_dispatcher import execute_action
from app.capture_engine import capture_screenshot_with_fallback
from app.dynamic_highlight_injector import (
    cleanup_highlights,
    inject_highlight_effects,
    remove_highlight_effects,
)
from app.playwright_capture_engine import PlaywrightCaptureEngine
from app.state import ManualState, clear_credentials
from app.storage_injector import inject_storage
from app.utils.sse_publisher import publish_sse_event
from app.utils.url_validator import validate_target_url


async def capture_screenshots_node(state: ManualState) -> ManualState:
    """
    Orchestrate browser automation to capture screenshots based on structured steps.
    This is Agent 2 in the DocuAgent LangGraph workflow.

    Args:
        state: The current ManualState containing job data and structured steps

    Returns:
        Updated ManualState with screenshot_assets populated and credentials cleared
    """
    # Create a copy of state to avoid mutating the original
    current_state = dict(state)

    # Extract required fields from state
    job_id = current_state.get("job_id")
    session_id = current_state.get("session_id")
    target_url = current_state.get("target_url")
    credentials = current_state.get("credentials", {})
    structured_steps = current_state.get("structured_steps", [])

    # Validate required fields
    if not job_id:
        raise ValueError("job_id is required in state")
    if not session_id:
        raise ValueError("session_id is required in state")
    if not target_url:
        raise ValueError("target_url is required in state")
    if not structured_steps:
        raise ValueError("structured_steps is required in state")

    # Validate target URL for SSRF protection
    validate_target_url(target_url)

    # Initialize screenshot_assets dictionary if not present
    if "screenshot_assets" not in current_state:
        current_state["screenshot_assets"] = {}

    # Initialize error_states dictionary if not present
    if "error_states" not in current_state:
        current_state["error_states"] = {}

    # Use PlaywrightCaptureEngine as an async context manager
    async with PlaywrightCaptureEngine() as engine:
        page = engine.page
        context = engine.context

        if not page or not context:
            raise RuntimeError("Failed to initialize Playwright browser")

        try:
            # Publish pipeline started event
            job_id = current_state.get("job_id")
            if job_id:
                try:
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="pipeline_started",
                        data={
                            "target_url": current_state.get("target_url"),
                            "session_id": current_state.get("session_id"),
                        },
                    )
                except Exception as e:
                    # Don't let publishing errors break the node
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning("Failed to publish pipeline_started event: %s", e)

            # Publish navigation start event
            await publish_sse_event(
                job_id=job_id,
                event_type="screenshot_capture_started",
                data={
                    "job_id": job_id,
                    "step_index": -1,  # Special index for overall job events
                    "capture_event_type": "navigate_started",
                    "url": target_url,
                },
            )

            # Navigate to target URL
            await execute_action(
                page=page, action_type="navigate", params={"url": target_url}, context=context
            )

            # Publish navigation completed event
            await publish_sse_event(
                job_id=job_id,
                event_type="screenshot_capture_started",
                data={
                    "job_id": job_id,
                    "step_index": -1,
                    "capture_event_type": "navigate_completed",
                    "url": target_url,
                },
            )

            # Handle authentication if credentials are provided
            if credentials and isinstance(credentials, dict):
                username = credentials.get("username")
                password = credentials.get("password")
                storage_data = credentials.get("storage")

                if username and password:
                    # Publish authentication start event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": -1,
                            "capture_event_type": "authenticate_started",
                            "username": username,
                        },
                    )

                    # Perform authentication
                    await execute_action(
                        page=page,
                        action_type="authenticate",
                        params={
                            "username": username,
                            "password": password,
                            "storage": storage_data,
                        },
                        context=context,
                    )

                    # Publish authentication completed event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": -1,
                            "capture_event_type": "authenticate_completed",
                            "username": username,
                        },
                    )

                    # Inject storage data if provided
                    if storage_data and context:
                        await inject_storage(context, storage_data)

            # Process each structured step
            for step_index, step in enumerate(structured_steps):
                try:
                    # Publish step start event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "step_started",
                            "action_type": getattr(step, "action_type", None),
                            "target_selector": getattr(step, "target_selector", None),
                        },
                    )

                    # Clear highlights from previous step
                    await cleanup_highlights(page)

                    # Extract step data from StepSchema
                    action_type = getattr(step, "action_type", None)
                    target_selector = getattr(step, "target_selector", None)
                    input_value = getattr(step, "input_value", None)
                    selector_hints = getattr(step, "selector_hints", [])

                    # Get step description for placeholder generation
                    step_description = f"Step {step_index}"
                    try:
                        if hasattr(step, "description"):
                            step_description = f"Step {step_index}: {step.description}"
                        elif isinstance(step, dict) and "description" in step:
                            step_description = f"Step {step_index}: {step['description']}"
                    except Exception:
                        # If we can't get the description, just use the step index
                        pass

                    # If we have a target selector, highlight the target element
                    if target_selector and action_type in ["click", "type"]:
                        try:
                            await inject_highlight_effects(page, target_selector)
                            # Publish highlight injected event
                            await publish_sse_event(
                                job_id=job_id,
                                event_type="screenshot_capture_started",
                                data={
                                    "job_id": job_id,
                                    "step_index": step_index,
                                    "capture_event_type": "highlight_injected",
                                    "selector": target_selector,
                                },
                            )
                            # Small delay to let user see the highlight
                            await page.wait_for_timeout(100)
                        except Exception as highlight_error:
                            # Highlight failure shouldn't stop the process
                            error_states = current_state["error_states"].copy()
                            error_states[f"highlight_{step_index}"] = {
                                "error": str(highlight_error),
                                "error_type": type(highlight_error).__name__,
                                "step_index": step_index,
                                "job_id": job_id,
                                "timestamp": str(step_index),
                                "highlight_error": True,
                            }
                            current_state["error_states"] = error_states
                            # Publish highlight failed event
                            await publish_sse_event(
                                job_id=job_id,
                                event_type="screenshot_capture_started",
                                data={
                                    "job_id": job_id,
                                    "step_index": step_index,
                                    "capture_event_type": "highlight_failed",
                                    "selector": target_selector,
                                    "error": str(highlight_error),
                                },
                            )

                    # Execute the action if specified
                    if (
                        action_type and action_type != "wait"
                    ):  # wait is handled separately if needed
                        # Publish action start event
                        await publish_sse_event(
                            job_id=job_id,
                            event_type="screenshot_capture_started",
                            data={
                                "job_id": job_id,
                                "step_index": step_index,
                                "capture_event_type": "action_started",
                                "action_type": action_type,
                                "selector": target_selector,
                                "has_input": input_value is not None,
                            },
                        )

                        # Prepare params for action_dispatcher
                        params = {}
                        if target_selector:
                            params["selector"] = target_selector
                        if input_value is not None:  # Allow empty string but not None
                            params["text"] = input_value

                        await execute_action(
                            page=page, action_type=action_type, params=params, context=context
                        )

                        # Publish action completed event
                        await publish_sse_event(
                            job_id=job_id,
                            event_type="screenshot_capture_started",
                            data={
                                "job_id": job_id,
                                "step_index": step_index,
                                "capture_event_type": "action_completed",
                                "action_type": action_type,
                                "selector": target_selector,
                                "has_input": input_value is not None,
                            },
                        )

                    # Capture screenshot with fallback mechanism
                    # For screenshot capture, we try to capture the element if selector exists,
                    # otherwise fall back to viewport
                    primary_selector = target_selector if target_selector else "body"

                    # Publish screenshot capture start event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "screenshot_capture_started",
                            "primary_selector": primary_selector,
                            "has_selector_hints": len(selector_hints) > 0,
                        },
                    )

                    screenshot_path = await capture_screenshot_with_fallback(
                        page=page,
                        job_id=job_id,
                        step_index=step_index,
                        primary_selector=primary_selector,
                        selector_hints=selector_hints,
                        state=current_state,
                        step_description=step_description,
                    )

                    # Update screenshot_assets in state
                    current_state["screenshot_assets"][step_index] = screenshot_path

                    # Publish screenshot captured event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "screenshot_captured",
                            "file_path": screenshot_path,
                            "is_element_screenshot": target_selector is not None,
                        },
                    )

                    # Clear highlights after capturing screenshot
                    await remove_highlight_effects(page)
                    # Publish highlight removed event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "highlight_removed",
                        },
                    )

                    # Add delay between steps to simulate human interaction
                    await page.wait_for_timeout(random.randint(500, 1500))

                    # Publish step completed event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "step_completed",
                            "screenshot_path": screenshot_path,
                            "success": True,
                        },
                    )

                except Exception as step_error:
                    # Record step failure but continue with other steps
                    error_states = current_state["error_states"].copy()
                    error_states[str(step_index)] = {
                        "error": str(step_error),
                        "error_type": type(step_error).__name__,
                        "step_index": step_index,
                        "job_id": job_id,
                        "timestamp": str(step_index),
                        "step_data": {
                            "action_type": action_type,
                            "target_selector": target_selector,
                            "input_value": input_value,
                            "selector_hints": selector_hints,
                        }
                        if "action_type" in locals()
                        else {},
                    }
                    current_state["error_states"] = error_states

                    # Publish step failed event
                    await publish_sse_event(
                        job_id=job_id,
                        event_type="screenshot_capture_started",
                        data={
                            "job_id": job_id,
                            "step_index": step_index,
                            "capture_event_type": "step_failed",
                            "error": str(step_error),
                            "error_type": type(step_error).__name__,
                        },
                    )

                    # Still try to capture a viewport screenshot for debugging purposes
                    try:
                        screenshot_path = await capture_screenshot_with_fallback(
                            page=page,
                            job_id=job_id,
                            step_index=step_index,
                            primary_selector="body",
                            selector_hints=[],
                            state=current_state,
                            step_description=step_description,
                        )
                        current_state["screenshot_assets"][step_index] = screenshot_path

                        # Publish screenshot captured (fallback) event
                        await publish_sse_event(
                            job_id=job_id,
                            event_type="screenshot_capture_started",
                            data={
                                "job_id": job_id,
                                "step_index": step_index,
                                "capture_event_type": "screenshot_captured_fallback",
                                "file_path": screenshot_path,
                                "reason": "viewport_fallback_after_step_failure",
                            },
                        )
                    except Exception:
                        # If even viewport capture fails, generate a placeholder
                        # Try to get the step description for a more meaningful placeholder
                        step_description = f"Step {step_index}"
                        try:
                            if step_index < len(structured_steps):
                                step_obj = structured_steps[step_index]
                                if hasattr(step_obj, "description"):
                                    step_description = f"Step {step_index}: {step_obj.description}"
                                elif isinstance(step_obj, dict) and "description" in step_obj:
                                    step_description = (
                                        f"Step {step_index}: {step_obj['description']}"
                                    )
                        except Exception:
                            # If we can't get the description, just use the step index
                            pass

                        # Create and store the placeholder indicator
                        placeholder_indicator = f"PLACEHOLDER:{step_description}"
                        current_state["screenshot_assets"][step_index] = placeholder_indicator

                        # Publish placeholder generated event
                        await publish_sse_event(
                            job_id=job_id,
                            event_type="screenshot_capture_started",
                            data={
                                "job_id": job_id,
                                "step_index": step_index,
                                "capture_event_type": "placeholder_generated",
                                "placeholder_text": step_description,
                                "reason": "all_capture_methods_failed",
                            },
                        )

            # Clear credentials after use for security
            current_state = clear_credentials(current_state)

            # Publish job completed event
            await publish_sse_event(
                job_id=job_id,
                event_type="screenshot_capture_started",
                data={
                    "job_id": job_id,
                    "step_index": -1,
                    "capture_event_type": "job_completed",
                    "total_steps": len(structured_steps),
                    "successful_steps": len(
                        [
                            i
                            for i in range(len(structured_steps))
                            if i in current_state.get("screenshot_assets", {})
                            and not str(current_state["screenshot_assets"][i]).startswith(
                                "PLACEHOLDER:"
                            )
                        ]
                    ),
                },
            )

            return current_state

        except Exception as e:
            # If we have a browser error, clear credentials anyway for security
            error_state = clear_credentials(current_state)

            # Publish job failed event
            await publish_sse_event(
                job_id=job_id,
                event_type="screenshot_capture_started",
                data={
                    "job_id": job_id,
                    "step_index": -1,
                    "capture_event_type": "job_failed",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            # Record the overall error
            if "error_states" not in error_state:
                error_state["error_states"] = {}
            error_state["error_states"]["browser_automation_error"] = {
                "error": str(e),
                "error_type": type(e).__name__,
                "job_id": job_id,
                "timestamp": "browser_automation",
                "step_index": -1,
            }

            raise
