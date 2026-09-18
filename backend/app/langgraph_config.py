"""
LangGraph configuration for DocuAgent AI.
Handles checkpointer setup for development and production environments.
Includes conditional edge evaluators for the LangGraph state machine.
Constructs the StateGraph with all nodes and edges for the DocuAgent workflow.
"""

import json
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver

try:
    from langgraph.checkpoint.redis import RedisSaver
except ImportError:
    try:
        from langgraph_checkpoint_redis import RedisSaver
    except ImportError:
        RedisSaver = None

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.capture_agent import capture_screenshots_node
from app.analyze_script import analyze_script_node
from app.chat_refiner import chat_refiner_node
from app.config import settings
from app.quality_review import quality_review_node
from app.state import ManualState
from app.technical_writer import compile_markdown_node


def get_checkpointer():
    """
    Get the appropriate checkpointer based on the environment.

    Returns:
        MemorySaver for development, RedisSaver for production (or fallback to MemorySaver)
    """
    if settings.app_env == "production" and RedisSaver is not None:
        try:
            # Production: Use RedisSaver with connection from settings
            return RedisSaver.from_conn_string(
                conn_string=settings.redis_url,
                ttl=settings.asset_retention_hours * 3600,  # Convert hours to seconds
            )
        except Exception:
            return MemorySaver()
    else:
        # Development/testing: Use in-memory MemorySaver
        return MemorySaver()


def get_development_checkpointer() -> MemorySaver:
    """
    Get development checkpointer using MemorySaver.

    Returns:
        MemorySaver instance for development use
    """
    return MemorySaver()


def get_production_checkpointer():
    """
    Get production checkpointer using RedisSaver.

    Returns:
        RedisSaver instance for production use, or MemorySaver fallback
    """
    if RedisSaver is not None:
        try:
            return RedisSaver.from_conn_string(
                conn_string=settings.redis_url,
                ttl=settings.asset_retention_hours * 3600,  # Convert hours to seconds
            )
        except Exception:
            return MemorySaver()
    return MemorySaver()


def route_after_quality_review(
    state: ManualState,
) -> Literal["compile_markdown_node", "chat_refiner_node", "__end__"]:
    """
    Conditional edge evaluator for the quality review node.
    Determines the next step based on the quality review output and retry attempts.

    Args:
        state: The current ManualState.

    Returns:
        The name of the next node to call:
          - "compile_markdown_node": If quality review failed and we have remaining attempts (loop back for revision).
          - "chat_refiner_node": If quality review passed OR if we have exhausted all attempts (forced approval).
          - "__end__": If we are done and should exit the graph (though in this workflow, we might not use this directly).

    Logic:
      1. Parse the quality_feedback JSON string from the state.
      2. Check if the overall_pass is True (all criteria >= 80).
      3. If overall_pass is True, proceed to chat_refiner_node (or potentially to export, but per TODO we go to chat_refiner_node for human interaction).
      4. If overall_pass is False, check the quality_review_attempts:
            If attempts < 3, loop back to compile_markdown_node for revision (increment attempts in the state? Actually, we should increment when we enter the quality review node? We'll handle attempts in the node itself, but we can check here and decide to loop).
            If attempts >= 3, force approval and proceed to chat_refiner_node.
    """
    # Initialize attempts if not present (should be initialized elsewhere, but safe guard)
    attempts = state.get("quality_review_attempts", 0)

    # If there is no quality_feedback, we assume we just entered the quality review node for the first time?
    # But actually, the quality_feedback is set by the quality review node.
    # We'll assume that when we are in this evaluator, the quality_feedback has been set.
    quality_feedback_str = state.get("quality_feedback")
    if not quality_feedback_str:
        # No feedback yet, we should not be here? Or we are at the first entrance?
        # For safety, we treat as failed and allow a retry if attempts < 3.
        # But ideally, the quality review node should set the feedback.
        # We'll treat as failed and check attempts.
        overall_pass = False
    else:
        try:
            feedback_dict = json.loads(quality_feedback_str)
        except (json.JSONDecodeError, TypeError):
            # If we cannot parse, treat as failed
            overall_pass = False
        else:
            # Check if all four criteria are >= 80
            completeness = feedback_dict.get("completeness", {}).get("score", 0)
            screenshot_coverage = feedback_dict.get("screenshot_coverage", {}).get("score", 0)
            tone_consistency = feedback_dict.get("tone_consistency", {}).get("score", 0)
            logical_sequencing = feedback_dict.get("logical_sequencing", {}).get("score", 0)
            overall_pass = (
                completeness >= 80
                and screenshot_coverage >= 80
                and tone_consistency >= 80
                and logical_sequencing >= 80
            )

    # If the review passed, we proceed to the chat refiner node (for human interaction) or potentially to export.
    # According to the TODO, after quality review we go to chat_refiner_node for human interaction.
    if overall_pass:
        return "chat_refiner_node"

    # If the review failed, we check if we have remaining attempts.
    # We allow up to 3 attempts (meaning 2 retries after the first attempt?).
    # The TODO says: "maximum 3 re-generation attempts before forced approval"
    # This implies: initial attempt + up to 3 re-generations = 4 total? Or 3 total attempts?
    # We'll interpret as: we allow the quality review to fail up to 3 times, then we force approval.
    # So if attempts < 3, we loop back for another attempt.
    # Note: We are counting the number of times we have gone through the quality review and failed.
    # We will increment the attempts in the quality review node? Or we can increment it here when we decide to loop?
    # Let's increment the attempts when we are about to loop back, so that the next time we see this evaluator, we know how many attempts we've had.
    # However, we are in a pure function; we cannot modify the state. We must return the next node and let the node update the state.
    # Therefore, we will not increment the attempts here. Instead, we will rely on the quality review node to increment the attempts when it runs.
    # But we don't have the quality review node yet.
    # For the purpose of this evaluator, we will assume that the state's quality_review_attempts has been updated by the quality review node.
    # We'll check the attempts from the state.
    if attempts < 3:
        # We have remaining attempts, so we loop back to the compile_markdown_node for revision.
        return "compile_markdown_node"
    else:
        # We have exhausted all attempts, force approval and proceed to chat_refiner_node.
        return "chat_refiner_node"


def create_docuagent_graph() -> CompiledStateGraph:
    """
    Create and compile the DocuAgent LangGraph workflow with all nodes and edges.

    Returns:
        CompiledStateGraph: The compiled DocuAgent workflow graph
    """
    # Initialize the state graph with our ManualState schema
    workflow = StateGraph(ManualState)

    # Add all the agent nodes
    workflow.add_node("analyze_script_node", analyze_script_node)
    workflow.add_node("capture_screenshots_node", capture_screenshots_node)
    workflow.add_node("compile_markdown_node", compile_markdown_node)
    workflow.add_node("quality_review_node", quality_review_node)
    workflow.add_node("chat_refiner_node", chat_refiner_node)

    # Set the entry point to start with script analysis
    workflow.set_entry_point("analyze_script_node")

    # Add edges between nodes in sequence
    workflow.add_edge("analyze_script_node", "capture_screenshots_node")
    workflow.add_edge("capture_screenshots_node", "compile_markdown_node")
    workflow.add_edge("compile_markdown_node", "quality_review_node")

    # Add conditional edge from quality review node
    workflow.add_conditional_edges(
        "quality_review_node",
        route_after_quality_review,
        {
            "compile_markdown_node": "compile_markdown_node",
            "chat_refiner_node": "chat_refiner_node",
            "__end__": END,
        },
    )

    # After chat refiner node, we can either end or loop back for more refinements
    # For now, we'll end after the chat refiner node (human interaction point)
    workflow.add_edge("chat_refiner_node", END)

    # Get the appropriate checkpointer
    checkpointer = get_checkpointer()

    # Compile the graph with interrupt handling
    # We interrupt before the chat_refiner_node to allow for human interaction
    app = workflow.compile(checkpointer=checkpointer, interrupt_before=["chat_refiner_node"])

    return app
