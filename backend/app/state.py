"""
ManualState TypedDict for LangGraph multi-agent state machine.
Note: The credentials field contains sensitive data and MUST be purged (set to empty dict)
after use by the capture_screenshots_node (Agent 2) to prevent persistence in checkpointers.
"""

from typing import Any, TypedDict

from .models import ChatMessage, StepSchema


class ManualState(TypedDict):
    """State definition for the DocuAgent LangGraph workflow."""

    raw_input_script: str
    target_url: str
    credentials: dict[str, Any]  # Auth credentials (purge after use by Agent 2)
    structured_steps: list[StepSchema]
    screenshot_assets: dict[int, str]  # step_index -> file_path
    markdown_content: str
    chat_history: list[ChatMessage]
    execution_logs: list[str]
    quality_approved: bool
    error_states: dict[str, Any]
    quality_feedback: str | None  # Structured feedback from quality review (Agent 4)
