"""
Technical Writer & Layout Agent (Agent 3) for DocuAgent AI.
Implements the compile_markdown_node for the LangGraph state machine.
"""

import json

from .llm import ollama_generate_text
from .prompts import COMPILE_MARKDOWN_PROMPT
from .state import ManualState


def compile_markdown_node(state: ManualState) -> ManualState:
    """
    LangGraph node for Agent 3: Technical Writer & Layout Agent.
    Synthesizes a comprehensive technical document based on workflow steps and screenshot assets.

    Args:
        state: The current ManualState.

    Returns:
        Updated ManualState with markdown_content set.
    """
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

    # Return the updated state
    return {
        **state,
        "markdown_content": markdown_content,
    }
