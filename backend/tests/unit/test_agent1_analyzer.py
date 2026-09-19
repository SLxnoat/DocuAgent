"""
Unit tests for Agent 1: Script & Domain Analyzer across 5 distinct sample workflows.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.analyzer_agent import (
    analyze_script_node,
)
from app.state import ManualState


@pytest.fixture
def base_state() -> ManualState:
    return {
        "job_id": "test-job-001",
        "session_id": "test-sess-001",
        "target_url": "https://staging.example.com",
        "raw_input_script": "",
        "credentials": {},
        "structured_steps": [],
        "screenshot_assets": {},
        "markdown_content": "",
        "chat_history": [],
        "execution_logs": [],
        "quality_approved": False,
        "error_states": {},
        "quality_feedback": None,
        "quality_review_attempts": 0,
        "recapture_step_index": None,
    }


@pytest.mark.asyncio
async def test_workflow_1_ecommerce_checkout(base_state):
    """Workflow 1: E-commerce product search and checkout."""
    script = (
        "1. Open the shop home page and search for 'Wireless Headphones'.\n"
        "2. Click the first product card in the search results.\n"
        "3. Click 'Add to Cart' button.\n"
        "4. Navigate to cart and click 'Proceed to Checkout'."
    )
    base_state["raw_input_script"] = script

    mock_llm_json = {
        "domain": "E-Commerce",
        "steps": [
            {
                "index": 0,
                "description": "Search for Wireless Headphones in the search bar",
                "action_type": "type",
                "target_selector": "input#search",
                "input_value": "Wireless Headphones",
                "selector_hints": [".search-input", "input[name='q']"],
            },
            {
                "index": 1,
                "description": "Click the first product result card",
                "action_type": "click",
                "target_selector": ".product-card:first-child",
                "input_value": "",
                "selector_hints": [".product-item", "a.product-link"],
            },
            {
                "index": 2,
                "description": "Add product to cart",
                "action_type": "click",
                "target_selector": "button#add-to-cart",
                "input_value": "",
                "selector_hints": [".btn-cart", "button[data-action='add-to-cart']"],
            },
        ],
    }

    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=mock_llm_json
        ),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
    ):
        result = await analyze_script_node(base_state)

    steps = result["structured_steps"]
    assert len(steps) == 3
    assert steps[0]["action_type"] == "type"
    assert steps[0]["domain_context"] == "E-Commerce"
    assert steps[1]["action_type"] == "click"


@pytest.mark.asyncio
async def test_workflow_2_crm_lead_creation(base_state):
    """Workflow 2: CRM customer lead creation and tagging."""
    script = (
        "Log into CRM dashboard. Go to Leads. Click 'New Lead'.\n"
        "Fill lead name, company, email. Click 'Save Lead'."
    )
    base_state["raw_input_script"] = script

    mock_llm_json = {
        "domain": "CRM",
        "steps": [
            {
                "index": 0,
                "description": "Click Leads tab in CRM navigation",
                "action_type": "click",
                "target_selector": "a[href='/leads']",
                "selector_hints": [".nav-leads", "#menu-leads"],
            },
            {
                "index": 1,
                "description": "Click New Lead button",
                "action_type": "click",
                "target_selector": "button#btn-new-lead",
                "selector_hints": [".create-lead-btn"],
            },
        ],
    }

    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=mock_llm_json
        ),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
    ):
        result = await analyze_script_node(base_state)

    steps = result["structured_steps"]
    assert len(steps) == 2
    assert steps[0]["domain_context"] == "CRM"


@pytest.mark.asyncio
async def test_workflow_3_saas_user_management(base_state):
    """Workflow 3: SaaS team member invite and permissions."""
    script = (
        "Navigate to Organization Settings.\n"
        "Click Members tab.\n"
        "Enter team member email and select 'Admin' role.\n"
        "Click 'Send Invitation'."
    )
    base_state["raw_input_script"] = script

    mock_llm_json = {
        "domain": "SaaS Platform",
        "steps": [
            {
                "index": 0,
                "description": "Navigate to Settings",
                "action_type": "click",
                "target_selector": "a#settings",
            },
            {
                "index": 1,
                "description": "Select Members tab",
                "action_type": "click",
                "target_selector": "#tab-members",
            },
            {
                "index": 2,
                "description": "Enter email to invite",
                "action_type": "type",
                "target_selector": "input#invite-email",
            },
            {
                "index": 3,
                "description": "Send Invitation",
                "action_type": "click",
                "target_selector": "button#submit-invite",
            },
        ],
    }

    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=mock_llm_json
        ),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
    ):
        result = await analyze_script_node(base_state)

    steps = result["structured_steps"]
    assert len(steps) == 4
    assert steps[2]["action_type"] == "type"


@pytest.mark.asyncio
async def test_workflow_4_admin_portal_security(base_state):
    """Workflow 4: Admin Portal security policy updates."""
    script = (
        "Access admin security portal.\n"
        "Toggle Two-Factor Authentication enforcement.\n"
        "Set session timeout to 15 minutes.\n"
        "Click Save Policy Changes."
    )
    base_state["raw_input_script"] = script

    mock_llm_json = {
        "domain": "Admin Portal",
        "steps": [
            {
                "index": 0,
                "description": "Enable 2FA toggle",
                "action_type": "click",
                "target_selector": "input#enforce-2fa",
            },
            {
                "index": 1,
                "description": "Set session timeout",
                "action_type": "type",
                "target_selector": "input#timeout",
            },
            {
                "index": 2,
                "description": "Save security policies",
                "action_type": "click",
                "target_selector": "button#save-policy",
            },
        ],
    }

    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=mock_llm_json
        ),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
    ):
        result = await analyze_script_node(base_state)

    steps = result["structured_steps"]
    assert len(steps) == 3


@pytest.mark.asyncio
async def test_workflow_5_financial_reporting_fallback(base_state):
    """Workflow 5: Financial statement export with LLM failure fallback."""
    script = "Open financial overview.\nFilter by Q3 2026 dates.\nClick Export Statement as CSV."
    base_state["raw_input_script"] = script

    # Simulate LLM failure to verify graceful fallback step generation
    with (
        patch("app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=None),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
    ):
        result = await analyze_script_node(base_state)

    steps = result["structured_steps"]
    assert len(steps) >= 3
    assert steps[0]["action_type"] == "navigate"
