"""
Technical Writer & Layout Agent (Agent 3) for DocuAgent AI.
Implements the compile_markdown_node for the LangGraph state machine.
"""

import json

from .llm import ollama_generate_text
from .prompts import COMPILE_MARKDOWN_PROMPT
from .state import ManualState
from .utils.sse_publisher import publish_sse_event


def compile_markdown_node(state: ManualState) -> ManualState:
    """
    LangGraph node for Agent 3: Technical Writer & Layout Agent.
    Synthesizes a comprehensive technical document based on workflow steps and screenshot assets.

    Args:
        state: The current ManualState.

    Returns:
        Updated ManualState with markdown_content set.
    """
    # Publish event: pipeline_started? Or script_analyzed?
    # Since this agent is responsible for compiling the markdown, we can publish:
    #   - "draft_compiled" when the draft is ready
    # But note: the checklist has "script_analyzed" for Agent 1 and "draft_compiled" for Agent 3.

    # We'll publish "script_analyzed" here? Actually, the script analysis is done by Agent 1.
    # We don't have access to Agent 1's output in this node? We do have the structured_steps in the state.

    # Let's publish "script_analyzed" at the beginning of this node to indicate that the script has been analyzed
    # and we are ready to compile the draft.
    # However, note that the state already has the structured_steps, which is the output of Agent 1.

    # We'll publish a "script_analyzed" event with the structured_steps in the data.
    job_id = state.get("job_id")
    if job_id:
        try:
            publish_sse_event(
                job_id=job_id,
                event_type="script_analyzed",
                data={
                    "structured_steps": state.get("structured_steps", []),
                },
            )
        except Exception as e:
            # Don't let publishing errors break the node
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("Failed to publish script_analyzed event: %s", e)

    # Determine the domain context from target_url and raw_input_script
    # We'll reuse the classify_domain function from llm.py if available, or create a simple version
    try:
        from .llm import classify_domain

        domain_context = classify_domain(state["target_url"], state["raw_input_script"])
    except ImportError:
        # Fallback if classify_domain is not available
        domain_context = "web application"

    # Prepare the prompt for the LLM
    prompt = COMPILE_MARKDOWN_PROMPT.format(
        structured_steps=json.dumps(state["structured_steps"], indent=2),
        screenshot_assets=json.dumps(state["screenshot_assets"], indent=2),
        domain_context=domain_context,
        raw_input_script=state["raw_input_script"],
        markdown_content=state.get("markdown_content", ""),
        quality_feedback=state.get("quality_feedback", ""),
    )

    # Call the LLM to get the markdown document
    try:
        markdown_content = ollama_generate_text(
            prompt=prompt,
            temperature=0.3,  # Moderate temperature for balanced creativity and consistency
            max_retries=2,
        )
    except Exception as e:
        # In case of failure, we provide a basic markdown structure
        markdown_content = f"""# Technical Documentation

## Prerequisites
*Documentation generation failed due to LLM error: {e}*

## System Overview
Unable to generate system overview due to documentation generation failure.

## Step-by-Step Walkthrough
*See structured steps in state for workflow details.*

## Troubleshooting
*Documentation generation failed. Please check system logs and try again.*
"""

    # Publish event: draft_compiled
    job_id = state.get("job_id")
    if job_id:
        try:
            publish_sse_event(
                job_id=job_id,
                event_type="draft_compiled",
                data={
                    "markdown_length": len(markdown_content) if markdown_content else 0,
                },
            )
        except Exception as e:
            # Don't let publishing errors break the node
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("Failed to publish draft_compiled event: %s", e)

    # Publish event: document_ready
    job_id = state.get("job_id")
    if job_id:
        try:
            publish_sse_event(
                job_id=job_id,
                event_type="document_ready",
                data={
                    "markdown_length": len(markdown_content) if markdown_content else 0,
                },
            )
        except Exception as e:
            # Don't let publishing errors break the node
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("Failed to publish document_ready event: %s", e)

    # Return the updated state
    return {
        **state,
        "markdown_content": markdown_content,
    }
