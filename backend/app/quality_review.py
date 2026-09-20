"""
Quality Review Agent (Agent 4) for DocuAgent AI.
Implements the quality_review_node for the LangGraph state machine.
"""

import json
from typing import Any

from .llm import classify_domain, ollama_generate_json_with_retry
from .prompts import QUALITY_REVIEW_PROMPT
from .state import ManualState
from .utils.sse_publisher import publish_sse_event


async def quality_review_node(state: ManualState) -> ManualState:
    """
    LangGraph node for Agent 4: Quality & Verification Agent.
    Evaluates the generated document for quality and provides structured feedback.
    Increments the quality review attempt counter.

    Args:
        state: The current ManualState.

    Returns:
        Updated ManualState with quality_feedback set and quality_review_attempts incremented.
    """
    job_id = state.get("job_id")
    if job_id:
        try:
            await publish_sse_event(
                job_id=job_id,
                event_type="quality_review_started",
                data={},
            )
        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(
                "Failed to publish quality_review_started event: %s", e
            )

    # Determine the domain context from target_url and raw_input_script
    domain_context = classify_domain(state["target_url"], state["raw_input_script"])

    # Prepare the prompt for the LLM
    prompt = QUALITY_REVIEW_PROMPT.format(
        structured_steps=json.dumps(state["structured_steps"], indent=2),
        screenshot_assets=json.dumps(state["screenshot_assets"], indent=2),
        domain_context=domain_context,
        raw_input_script=state["raw_input_script"],
        markdown_content=state["markdown_content"],
    )

    # Call the LLM to get the quality feedback in JSON format
    try:
        feedback_dict: dict[str, Any] = ollama_generate_json_with_retry(
            prompt=prompt,
            temperature=0.1,  # Low temperature for consistent JSON output
            max_retries=2,
        )
    except Exception as e:
        # In case of failure, we provide a fallback feedback structure
        feedback_dict = {
            "completeness": {"score": 0, "feedback": f"LLM call failed: {e!s}"},
            "screenshot_coverage": {"score": 0, "feedback": "LLM call failed"},
            "tone_consistency": {"score": 0, "feedback": "LLM call failed"},
            "logical_sequencing": {"score": 0, "feedback": "LLM call failed"},
            "overall_pass": False,
            "summary": "Quality review failed due to LLM error.",
        }

    # Convert the feedback dictionary to a JSON string for storage in the state
    quality_feedback_str = json.dumps(feedback_dict)

    # Increment the quality review attempt counter
    current_attempts = state.get("quality_review_attempts", 0)
    new_attempts = current_attempts + 1

    # Calculate overall pass status
    overall_pass = bool(feedback_dict.get("overall_pass", False))

    # Prepare the updated state
    updated_state = {
        **state,
        "quality_feedback": quality_feedback_str,
        "quality_review_attempts": new_attempts,
        "quality_approved": overall_pass,
    }

    # Publish event: quality_approved if the review passes
    job_id = state.get("job_id")
    if job_id:
        try:
            if overall_pass:
                await publish_sse_event(
                    job_id=job_id,
                    event_type="quality_approved",
                    data={
                        "feedback": feedback_dict,
                    },
                )
            else:
                await publish_sse_event(
                    job_id=job_id,
                    event_type="quality_loop",
                    data={
                        "retry_count": new_attempts,
                        "feedback": feedback_dict,
                    },
                )
        except Exception as e:
            # Don't let publishing errors break the node
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("Failed to publish quality_approved event: %s", e)

    return updated_state
