"""
Unit tests for Agent 5: Conversational Refiner.
Verifies edit classification, surgical section replacements, and recapture extraction.
"""

from __future__ import annotations

from app.chat_refiner import (
    classify_chat_edit,
    extract_recapture_step_index,
    update_markdown_sections,
)


def test_classify_chat_edit_types():
    """Verify classification of chat messages into text_edit, structural_revision, or recapture_trigger."""
    # Recapture triggers
    assert classify_chat_edit("Please recapture the screenshot for step 1") == "recapture_trigger"
    assert classify_chat_edit("Retake screenshot 2") == "recapture_trigger"
    assert classify_chat_edit("reshoot step 0") == "recapture_trigger"

    # Structural revisions
    assert (
        classify_chat_edit("Add a new step after step 2 for verification") == "structural_revision"
    )
    assert classify_chat_edit("Delete the troubleshooting section") == "structural_revision"
    assert classify_chat_edit("Reorder step 1 and step 2") == "structural_revision"

    # Text edits
    assert classify_chat_edit("Change the title to 'User Guide'") == "text_edit"
    assert classify_chat_edit("Fix the typo in the first sentence") == "text_edit"
    assert classify_chat_edit("Make the tone more casual and friendly") == "text_edit"


def test_extract_step_index_from_recapture_message():
    """Verify extraction of step indices from natural language recapture requests."""
    # 1-based UI references map to 0-based internal step indices
    assert extract_recapture_step_index("Please recapture step 1") == 0
    assert extract_recapture_step_index("Please recapture step 2") == 1
    assert extract_recapture_step_index("Retake step 3 image") == 2
    assert extract_recapture_step_index("Reshoot step 16") == 15
    assert extract_recapture_step_index("Just retake the whole thing") is None


def test_update_markdown_sections_surgical_replacement():
    """Verify update_markdown_sections updates only target headers without modifying untouched sections."""
    original_md = """# Application User Manual

## Prerequisites
- Node.js 18+
- npm 9+

## System Overview
This system provides high-speed automated document generation.

## Step-by-Step Walkthrough
### Step 1: Initialize
Run the start command.

## Troubleshooting
Check console logs if startup fails.
"""

    updates = {
        "Prerequisites": "\n- Node.js 20+ LTS\n- pnpm 8+\n- Docker 24+\n",
        "Troubleshooting": "\nInspect /var/log/docuagent.log for detailed stack traces.\n",
    }

    updated = update_markdown_sections(original_md, updates)

    # Replaced sections
    assert "Node.js 20+ LTS" in updated
    assert "pnpm 8+" in updated
    assert "/var/log/docuagent.log" in updated

    # Untouched sections must be preserved exactly
    assert "## System Overview" in updated
    assert "This system provides high-speed automated document generation." in updated
    assert "### Step 1: Initialize" in updated
    assert "Run the start command." in updated


def test_update_markdown_sections_case_insensitive_matching():
    """Verify update_markdown_sections matches headers regardless of case."""
    original = "## Prerequisites\nOld content\n\n## Overview\nOverview text"
    updates = {"prerequisites": "\nNew prerequisite content\n"}

    result = update_markdown_sections(original, updates)
    assert "New prerequisite content" in result
    assert "Overview text" in result
