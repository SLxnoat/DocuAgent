"""
Agent 1: Script & Domain Analyzer for DocuAgent AI.
Transforms unstructured workflow scripts into a structured JSON DAG of StepSchema objects.
"""

import logging
from typing import Any

from app.llm import ollama_generate_json_with_retry
from app.models import StepSchema
from app.prompts import SCRIPT_ANALYSIS_PROMPT
from app.state import ManualState
from app.utils.sse_publisher import publish_sse_event

logger = logging.getLogger(__name__)


def _parse_step_object(
    raw_step: dict[str, Any], index: int, domain: str = "web application"
) -> dict[str, Any]:
    """Ensure a step dictionary conforms strictly to StepSchema."""
    return {
        "index": raw_step.get("index", index),
        "description": str(raw_step.get("description", f"Step {index}")),
        "action_type": str(raw_step.get("action_type", "navigate")),
        "target_selector": str(raw_step.get("target_selector") or ""),
        "input_value": str(raw_step.get("input_value") or ""),
        "expected_url": str(raw_step.get("expected_url") or ""),
        "domain_context": str(raw_step.get("domain_context") or domain),
        "selector_hints": list(raw_step.get("selector_hints") or []),
    }


def _create_fallback_steps(raw_script: str, target_url: str) -> list[dict[str, Any]]:
    """Create basic structured steps if LLM inference fails."""
    lines = [line.strip() for line in raw_script.strip().splitlines() if line.strip()]
    if not lines:
        lines = ["Navigate to application and inspect workflow"]

    steps: list[dict[str, Any]] = [
        {
            "index": 0,
            "description": f"Navigate to {target_url}",
            "action_type": "navigate",
            "target_selector": "body",
            "input_value": target_url,
            "expected_url": target_url,
            "domain_context": "web application",
            "selector_hints": ["body", "html"],
        }
    ]

    for idx, line in enumerate(lines, start=1):
        action = "click"
        if any(w in line.lower() for w in ["type", "enter", "fill", "input", "write"]):
            action = "type"
        elif any(w in line.lower() for w in ["navigate", "open", "go to", "visit"]):
            action = "navigate"
        elif any(w in line.lower() for w in ["wait", "pause"]):
            action = "wait"

        steps.append(
            {
                "index": idx,
                "description": line,
                "action_type": action,
                "target_selector": "body",
                "input_value": "",
                "expected_url": target_url,
                "domain_context": "web application",
                "selector_hints": ["body"],
            }
        )

    return steps


async def analyze_script_node(state: ManualState) -> ManualState:
    """
    LangGraph node for Agent 1: Script & Domain Analyzer.
    Parses the raw input script into structured execution steps.
    """
    current_state = dict(state)
    job_id = current_state.get("job_id", "")
    target_url = current_state.get("target_url", "")
    raw_script = current_state.get("raw_input_script", "")

    # Notify start of pipeline
    if job_id:
        await publish_sse_event(
            job_id=job_id,
            event_type="pipeline_started",
            data={"target_url": target_url},
        )

    # If steps are already pre-populated, preserve and publish
    if current_state.get("structured_steps"):
        if job_id:
            await publish_sse_event(
                job_id=job_id,
                event_type="script_analyzed",
                data={
                    "total_steps": len(current_state["structured_steps"]),
                    "structured_steps": current_state["structured_steps"],
                },
            )
        return current_state

    prompt = SCRIPT_ANALYSIS_PROMPT.format(raw_input_script=raw_script)

    parsed_steps: list[dict[str, Any]] = []
    try:
        response_json = ollama_generate_json_with_retry(
            prompt=prompt,
            temperature=0.1,
            max_retries=2,
        )

        domain = "web application"
        if isinstance(response_json, list):
            step_items = response_json
        elif isinstance(response_json, dict):
            domain = str(response_json.get("domain") or "web application")
            step_items = (
                response_json.get("steps")
                or response_json.get("actions")
                or response_json.get("workflow")
                or [response_json]
            )
        else:
            step_items = []

        for i, item in enumerate(step_items):
            if isinstance(item, dict):
                parsed_steps.append(_parse_step_object(item, i, domain=domain))

    except Exception as exc:
        logger.warning(
            "Agent 1 LLM extraction failed or timed out: %s. Using heuristic fallback steps.", exc
        )
        parsed_steps = _create_fallback_steps(raw_script, target_url)

    if not parsed_steps:
        parsed_steps = _create_fallback_steps(raw_script, target_url)

    # Convert to StepSchema validation if needed
    structured_steps = [StepSchema(**s).model_dump() for s in parsed_steps]
    current_state["structured_steps"] = structured_steps

    # Record in execution logs
    logs = list(current_state.get("execution_logs", []))
    logs.append(
        f"Agent 1 (Script Analyzer) extracted {len(structured_steps)} structured interaction steps."
    )
    current_state["execution_logs"] = logs

    # Publish script_analyzed SSE event
    if job_id:
        await publish_sse_event(
            job_id=job_id,
            event_type="script_analyzed",
            data={
                "total_steps": len(structured_steps),
                "structured_steps": structured_steps,
            },
        )

    return current_state
