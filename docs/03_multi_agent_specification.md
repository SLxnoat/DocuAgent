# Multi-Agent Design Specification

**Document ID:** DOC-003  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Backend Engineers, ML Engineers

---

## Table of Contents

1. [Overview](#1-overview)
2. [State Schema Definition](#2-state-schema-definition)
3. [Agent Graph Topology](#3-agent-graph-topology)
4. [Agent 1: Script & Domain Analyzer](#4-agent-1-script--domain-analyzer)
5. [Agent 2: Playwright Visual Capturer](#5-agent-2-playwright-visual-capturer)
6. [Agent 3: Technical Writer & Layout Agent](#6-agent-3-technical-writer--layout-agent)
7. [Agent 4: Quality & Verification Agent](#7-agent-4-quality--verification-agent)
8. [Agent 5: Conversational Refiner Agent](#8-agent-5-conversational-refiner-agent)
9. [Human-in-the-Loop (HITL) Mechanism](#9-human-in-the-loop-hitl-mechanism)
10. [State Persistence & Checkpointing](#10-state-persistence--checkpointing)
11. [Error Handling & Agent Recovery](#11-error-handling--agent-recovery)
12. [Agent Prompt Templates](#12-agent-prompt-templates)

---

## 1. Overview

DocuAgent AI's core intelligence is orchestrated through a **LangGraph State Machine** — a directed, cyclical graph of specialized AI agents. Each agent is a discrete computational node that receives the shared `ManualState`, performs a focused task, and returns an updated state to the graph.

### 1.1 Design Principles

- **Single Responsibility:** Each agent performs exactly one well-scoped function.
- **Stateless Computation:** Agents do not maintain internal state between calls; all context is sourced from `ManualState`.
- **Deterministic Routing:** Graph edges use conditional logic to route execution between agents based on state fields (e.g., `quality_approved`).
- **Interrupt-Compatible:** The graph supports `interrupt_before` and `interrupt_after` checkpoints for HITL pauses.

### 1.2 Agent Roster

| Agent       | Node Name                  | Primary Role                                      |
| ----------- | -------------------------- | ------------------------------------------------- |
| **Agent 1** | `analyze_script_node`      | Script parsing & structured step DAG generation   |
| **Agent 2** | `capture_screenshots_node` | Browser automation & screenshot collection        |
| **Agent 3** | `compile_markdown_node`    | Technical content synthesis & Markdown formatting |
| **Agent 4** | `quality_review_node`      | Automated quality gate & document approval        |
| **Agent 5** | `chat_refiner_node`        | Conversational human-in-the-loop document editing |

---

## 2. State Schema Definition

The `ManualState` TypedDict is the single source of truth passed through the agent graph. All agents read from and write to this shared schema.

```python
from typing import TypedDict, Optional
from dataclasses import dataclass

@dataclass
class StepSchema:
    index: int                    # Step sequence number (1-based)
    description: str              # Human-readable step description
    action_type: str              # "click" | "type" | "navigate" | "scroll" | "wait"
    target_selector: str          # CSS/XPath selector for the target UI element
    input_value: Optional[str]    # Value to type (for "type" actions)
    expected_url: Optional[str]   # Expected URL after navigation (for validation)
    domain_context: str           # Inferred domain (e.g., "E-commerce", "CRM")
    selector_hints: list[str]     # Fallback selectors if primary fails


@dataclass
class ChatMessage:
    role: str        # "user" | "assistant"
    content: str
    timestamp: str


class ManualState(TypedDict):
    # Input fields (populated at job submission)
    raw_input_script: str              # Original unstructured workflow text
    target_url: str                    # Staging application base URL
    credentials: dict                  # {"username": ..., "password": ...} — in-memory only

    # Processing fields (populated during pipeline execution)
    structured_steps: list[StepSchema]        # Parsed DAG of UI interactions
    screenshot_assets: dict[int, str]         # {step_index: "/assets/{job_id}/step_N.png"}
    markdown_content: str                     # Current compiled Markdown document

    # Conversational fields
    chat_history: list[ChatMessage]           # Multi-turn refinement dialogue

    # Control & audit fields
    execution_logs: list[str]                 # Agent activity log entries
    quality_approved: bool                    # Set True by Agent 4 on pass
    quality_feedback: Optional[str]           # Agent 4 review notes (used on loop)
    error_states: dict[int, str]              # {step_index: "error description"}
    job_id: str                               # Unique job identifier
    session_id: str                           # Chat session identifier
```

---

## 3. Agent Graph Topology

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │   analyze_script_node  │  (Agent 1)
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ capture_screenshots_  │  (Agent 2)
                    │       node            │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  compile_markdown_    │  (Agent 3) ◄──────────────────┐
                    │       node            │                               │
                    └───────────┬───────────┘                               │
                                │                                           │
                                ▼                                           │
                    ┌───────────────────────┐                               │
                    │  quality_review_node  │  (Agent 4)                    │
                    └───────────┬───────────┘                               │
                                │                                           │
                    ┌───────────┴─────────┐                                 │
                    │ quality_approved?   │                                 │
                    └───┬─────────────────┘                                 │
                        │ YES              │ NO (with feedback)             │
                        ▼                 └───────────────────────────────►┘
                  HUMAN INTERRUPT                    (Max 3 retries)
                        │
                        ▼
              ┌─────────────────────┐
              │  [User inspects     │
              │   document in UI]   │
              └─────────┬───────────┘
                        │ User sends chat message
                        ▼
              ┌─────────────────────┐
              │  chat_refiner_node  │  (Agent 5)
              └─────────┬───────────┘
                        │
                        ▼ (back to HUMAN INTERRUPT — awaiting next input)
                      END (on user export action)
```

### 3.1 Conditional Edge Logic

```python
def route_after_quality_review(state: ManualState) -> str:
    """Route based on quality approval result."""
    if state["quality_approved"]:
        return "human_interrupt"
    elif state.get("quality_retry_count", 0) >= 3:
        # Force pass after max retries to prevent infinite loop
        return "human_interrupt"
    else:
        return "compile_markdown_node"
```

---

## 4. Agent 1: Script & Domain Analyzer

### 4.1 Agent Summary

| Property                | Value                                   |
| ----------------------- | --------------------------------------- |
| **Node Name**           | `analyze_script_node`                   |
| **Role**                | Context Extraction & Execution Planning |
| **Preferred LLM**       | Qwen 2.5 72B                            |
| **Input State Fields**  | `raw_input_script`, `target_url`        |
| **Output State Fields** | `structured_steps`, `execution_logs`    |

### 4.2 Functional Description

Agent 1 is the entry point of the pipeline. It receives the raw, unstructured user-provided workflow script and transforms it into a structured, machine-executable JSON Directed Acyclic Graph (DAG) of UI interaction steps.

**Core Tasks:**

1. Parse free-form text to identify discrete UI actions (clicks, form inputs, navigation events).
2. Infer CSS/XPath selectors for each target UI element based on contextual description.
3. Detect the application domain (E-commerce, CRM, Financial Dashboard, Admin Portal, SaaS).
4. Identify the target URL, authentication requirements, and expected page transitions.
5. Generate fallback selector hints for robustness.

### 4.3 Input/Output Contract

**Input Example (raw_input_script):**

```
Go to https://app.example.com and log in with admin credentials.
Navigate to the Users section from the left sidebar.
Click "Add New User" button.
Fill in the user's full name, email address, and assign the "Editor" role.
Click "Save" and verify the confirmation toast appears.
```

**Output Example (structured_steps):**

```json
[
  {
    "index": 1,
    "description": "Navigate to application login page",
    "action_type": "navigate",
    "target_selector": null,
    "input_value": "https://app.example.com/login",
    "expected_url": "https://app.example.com/login",
    "domain_context": "Admin Portal",
    "selector_hints": []
  },
  {
    "index": 2,
    "description": "Enter administrator credentials and log in",
    "action_type": "authenticate",
    "target_selector": "input[name='username']",
    "input_value": "{credentials.username}",
    "expected_url": "https://app.example.com/dashboard",
    "domain_context": "Admin Portal",
    "selector_hints": ["#username", "input[type='email']"]
  },
  {
    "index": 3,
    "description": "Click 'Users' section in the left sidebar",
    "action_type": "click",
    "target_selector": "nav a[href='/users']",
    "input_value": null,
    "expected_url": "https://app.example.com/users",
    "domain_context": "Admin Portal",
    "selector_hints": ["[data-testid='sidebar-users']", "a:has-text('Users')"]
  }
]
```

### 4.4 Error Conditions

| Condition                  | Behavior                                                        |
| -------------------------- | --------------------------------------------------------------- |
| Ambiguous step description | Agent requests clarification; logs a `[AMBIGUOUS_STEP]` warning |
| No URL detected            | Uses `target_url` from state as base URL for all steps          |
| Malformed JSON output      | Pydantic validation triggers retry (max 2 retries)              |

---

## 5. Agent 2: Playwright Visual Capturer

### 5.1 Agent Summary

| Property                | Value                                                 |
| ----------------------- | ----------------------------------------------------- |
| **Node Name**           | `capture_screenshots_node`                            |
| **Role**                | Live Application Execution & Image Collection         |
| **Preferred LLM**       | N/A (orchestration only — calls Playwright engine)    |
| **Input State Fields**  | `structured_steps`, `credentials`, `target_url`       |
| **Output State Fields** | `screenshot_assets`, `error_states`, `execution_logs` |

### 5.2 Functional Description

Agent 2 acts as the coordinator between the LangGraph state machine and the Playwright browser automation engine. It iterates over each step in `structured_steps` and dispatches browser commands to capture annotated screenshots.

> 📌 **Note:** Agent 2 does not call an LLM. It is a pure orchestration agent that interfaces with the Playwright Python SDK.

**Core Tasks:**

1. Initialize a Playwright browser context with optional credential injection.
2. Execute each `StepSchema` action (click, type, navigate, scroll).
3. Locate target selectors and inject CSS highlight styles.
4. Capture a full-page or viewport screenshot after each step.
5. Register file paths in `screenshot_assets` indexed by `step.index`.
6. Handle selector failures gracefully per the fallback strategy.

### 5.3 Screenshot Naming Convention

```
/assets/{job_id}/step_{index:03d}.png

Example:
  /assets/job_abc123/step_001.png
  /assets/job_abc123/step_002.png
```

For the full Playwright implementation specification, refer to [Browser Automation Engine](./05_browser_automation_engine.md).

### 5.4 Error Registration

When a step fails (selector not found, navigation timeout), Agent 2 registers the error without stopping the pipeline:

```python
state["error_states"][step.index] = "Selector 'nav a[href=/users]' not found after 30s timeout."
state["screenshot_assets"][step.index] = "/assets/{job_id}/step_003_fallback.png"
```

---

## 6. Agent 3: Technical Writer & Layout Agent

### 6.1 Agent Summary

| Property                | Value                                                                     |
| ----------------------- | ------------------------------------------------------------------------- |
| **Node Name**           | `compile_markdown_node`                                                   |
| **Role**                | Content Generation & Technical Formatting                                 |
| **Preferred LLM**       | Llama 3.3 70B                                                             |
| **Input State Fields**  | `structured_steps`, `screenshot_assets`, `target_url`, `quality_feedback` |
| **Output State Fields** | `markdown_content`, `execution_logs`                                      |

### 6.2 Functional Description

Agent 3 synthesizes the structured step data and screenshot asset index into a professionally formatted Markdown user manual. It applies standard technical writing frameworks to ensure the document is publication-ready.

**Core Tasks:**

1. Generate a document header with title, prerequisites section, and overview.
2. Format each step as a numbered section with:
   - Step title and action description.
   - Inline screenshot reference using relative path.
   - Callout boxes for warnings, tips, or critical notes.
   - Expected outcome statement.
3. Append a Troubleshooting section for any steps registered in `error_states`.
4. Apply tone and structure appropriate to the inferred `domain_context`.
5. If `quality_feedback` is present (on a re-run), apply targeted improvements.

### 6.3 Markdown Document Structure

```markdown
# [Document Title]

## Prerequisites

- [List of prerequisites inferred from domain context and steps]

## Overview

[Brief paragraph describing the workflow and its purpose]

---

## Step 1: [Step Description]

![Step 1 Screenshot](../assets/{job_id}/step_001.png)

[Detailed instruction prose]

> **💡 Tip:** [Contextual advice or efficiency note]

**Expected Result:** [What the user should see after completing this step]

---

## Step 2: [Step Description]

...

---

## Troubleshooting

### [Issue Title for failed step]

**Symptom:** [Described error condition]
**Resolution:** [Suggested fix or workaround]
[Placeholder if screenshot unavailable: ![Insert Screenshot Here: Description]()]
```

### 6.4 Domain-Specific Writing Modes

| Domain              | Tone                          | Special Sections                          |
| ------------------- | ----------------------------- | ----------------------------------------- |
| E-commerce          | Clear, consumer-friendly      | Shopping cart guidance, payment notes     |
| Financial Dashboard | Formal, precise               | Data accuracy warnings, audit trail notes |
| CRM                 | Professional, process-focused | Workflow notes, field validation tips     |
| Admin Portal        | Technical, concise            | Permission requirements, role-based notes |
| SaaS Platform       | Modern, efficient             | Feature flags, plan-specific notes        |

---

## 7. Agent 4: Quality & Verification Agent

### 7.1 Agent Summary

| Property                | Value                                                       |
| ----------------------- | ----------------------------------------------------------- |
| **Node Name**           | `quality_review_node`                                       |
| **Role**                | Verification & Document Polish                              |
| **Preferred LLM**       | Llama 3.3 70B                                               |
| **Input State Fields**  | `markdown_content`, `structured_steps`, `screenshot_assets` |
| **Output State Fields** | `quality_approved`, `quality_feedback`, `execution_logs`    |

### 7.2 Functional Description

Agent 4 acts as an AI-powered technical editor, reviewing the compiled Markdown document against a structured quality rubric before it is presented to the user.

**Quality Review Checklist:**

| Check                        | Description                                                                |
| ---------------------------- | -------------------------------------------------------------------------- |
| **Step Completeness**        | Every `structured_steps` entry has a corresponding section in the document |
| **Screenshot Coverage**      | Every section references a valid screenshot (or a fallback placeholder)    |
| **Logical Flow**             | Steps are sequenced coherently; prerequisites are complete                 |
| **Tone Consistency**         | Document maintains consistent tone throughout                              |
| **Terminology Accuracy**     | UI element names match the step descriptions                               |
| **Callout Appropriateness**  | Tips and warnings are contextually relevant                                |
| **Troubleshooting Coverage** | All `error_states` entries have troubleshooting entries                    |

### 7.3 Approval Logic

```python
def quality_review_node(state: ManualState) -> ManualState:
    review_prompt = build_review_prompt(state)
    response = llm.invoke(review_prompt)

    if response.approved:
        state["quality_approved"] = True
        state["quality_feedback"] = None
    else:
        state["quality_approved"] = False
        state["quality_feedback"] = response.feedback_notes
        state["quality_retry_count"] = state.get("quality_retry_count", 0) + 1

    return state
```

---

## 8. Agent 5: Conversational Refiner Agent

### 8.1 Agent Summary

| Property                | Value                                                                       |
| ----------------------- | --------------------------------------------------------------------------- |
| **Node Name**           | `chat_refiner_node`                                                         |
| **Role**                | Interactive Human-in-the-Loop Document Editor                               |
| **Preferred LLM**       | Qwen 2.5 72B                                                                |
| **Input State Fields**  | `markdown_content`, `chat_history`, `structured_steps`, `screenshot_assets` |
| **Output State Fields** | `markdown_content`, `chat_history`, `execution_logs`                        |

### 8.2 Functional Description

Agent 5 handles all user-initiated refinement requests received through the chat interface. Rather than triggering a full pipeline re-run, it performs **surgical, targeted updates** to the existing Markdown document based on natural language commands.

### 8.3 Edit Classification Matrix

| Request Type                            | Classification         | Agent Behavior                                            |
| --------------------------------------- | ---------------------- | --------------------------------------------------------- |
| "Fix the wording in step 3"             | **Text Edit**          | LLM rewrites only the Step 3 section                      |
| "Add a warning about data loss"         | **Text Edit**          | Inserts callout box at specified location                 |
| "Translate the entire manual to French" | **Text Edit**          | Full document re-rendered in French                       |
| "Move step 5 before step 3"             | **Structural Edit**    | Reorders Markdown sections, renumbers                     |
| "Add a new step after step 4"           | **Structural Edit**    | Inserts new section with placeholder image                |
| "Re-take the screenshot for step 2"     | **Re-capture Trigger** | Calls Playwright for step 2 only; updates asset           |
| "Make the tone more formal"             | **Text Edit**          | Re-passes full document through LLM with tone instruction |

### 8.4 Selective Update Strategy

To minimize latency and avoid unnecessary LLM processing, Agent 5 identifies the affected document segment using Markdown section boundaries and updates only that portion:

```python
def update_specific_section(markdown: str, section_index: int, new_content: str) -> str:
    """Replace only the targeted step section in the Markdown document."""
    sections = split_by_heading(markdown, level=2)
    sections[section_index] = new_content
    return join_sections(sections)
```

---

## 9. Human-in-the-Loop (HITL) Mechanism

### 9.1 Interrupt Point Configuration

The HITL interrupt is configured on the LangGraph graph after the quality review passes:

```python
graph = StateGraph(ManualState)
graph.add_node("quality_review_node", quality_review_node)
graph.add_node("chat_refiner_node", chat_refiner_node)

# Interrupt BEFORE chat_refiner_node — allows UI to display document first
graph.compile(interrupt_before=["chat_refiner_node"])
```

### 9.2 HITL Execution Flow

```
LangGraph reaches HUMAN INTERRUPT
         │
         ▼
SSE event: {"type": "document_ready", "markdown": "...full content..."}
         │
         ▼
Frontend renders document in split-screen editor
         │
         ▼
User inspects and optionally types in chat panel
         │
         ▼
Frontend sends: POST /api/v1/chat/{session_id}
         │
         ▼
FastAPI resumes LangGraph graph with updated state
         │
         ▼
chat_refiner_node executes targeted update
         │
         ▼
SSE event: {"type": "document_updated", "markdown": "...updated content..."}
         │
         ▼
Frontend refreshes editor content
```

### 9.3 Session Continuity

The LangGraph `thread_id` (equivalent to `session_id`) maintains the full conversation context across multiple user chat turns. This allows Agent 5 to understand the cumulative history of edits when processing subsequent requests.

---

## 10. State Persistence & Checkpointing

### 10.1 Checkpointer Configuration

| Environment | Checkpointer        | Configuration                      |
| ----------- | ------------------- | ---------------------------------- |
| Development | `MemorySaver`       | In-process, no external dependency |
| Production  | `RedisCheckpointer` | Redis with 24h TTL per session     |

### 10.2 Production Checkpointer Setup

```python
from langgraph.checkpoint.redis import RedisSaver

checkpointer = RedisSaver.from_conn_string(
    conn_string="redis://redis:6379",
    ttl=86400  # 24 hours
)

graph = graph.compile(checkpointer=checkpointer)
```

### 10.3 Security: Credential Field Handling

The `credentials` field in `ManualState` is **never persisted** to the Redis checkpointer. It is populated in-memory at job start and cleared immediately after Agent 2 completes:

```python
def capture_screenshots_node(state: ManualState) -> ManualState:
    # ... perform browser automation using state["credentials"] ...

    # Scrub credentials from state before returning
    state["credentials"] = {}
    return state
```

---

## 11. Error Handling & Agent Recovery

### 11.1 Agent-Level Error Handling

| Error Type                   | Recovery Strategy                                       |
| ---------------------------- | ------------------------------------------------------- |
| LLM response parsing failure | Retry up to 2 times with corrected output format hint   |
| Playwright selector timeout  | Log to `error_states`, use fallback viewport screenshot |
| Network error (LLM API)      | Exponential backoff, 3 retries                          |
| Quality review infinite loop | Force approve after 3 consecutive quality failures      |
| Export conversion failure    | Return Markdown as fallback; log export error           |

### 11.2 Dead Letter Queue

Jobs that fail after all retries are moved to a Celery dead-letter queue for manual inspection. The user receives an SSE event with `{"type": "job_failed", "error": "description"}` and can retry the job from the frontend.

---

## 12. Agent Prompt Templates

### 12.1 Script Analyzer System Prompt

```
You are a meticulous software workflow analyst. Your task is to parse the provided
user workflow description and extract a structured JSON array of UI interaction steps.

For each step, identify:
- The action type (navigate, click, type, scroll, wait, authenticate)
- The most likely CSS or XPath selector for the target element
- 2-3 alternative fallback selectors
- The expected resulting state or URL
- The application domain context

Return ONLY a valid JSON array matching the StepSchema. Do not include any prose.
```

### 12.2 Technical Writer System Prompt

```
You are a senior technical writer specializing in enterprise software documentation.
Your task is to synthesize the provided UI interaction steps and screenshot index
into a professional, publication-ready user manual in Markdown format.

Apply the following standards:
- Use clear, active-voice instructions ("Click the Save button." not "The Save button should be clicked.")
- Include Prerequisites and Overview sections
- Use numbered steps with descriptive H2 headings
- Reference each screenshot using the provided file path
- Add contextually appropriate callout boxes (💡 Tip, ⚠️ Warning)
- Include Expected Result statements after each step
- Match tone to the detected domain context: {domain_context}

If quality_feedback is provided, apply ALL specified improvements precisely.
```

### 12.3 Conversational Refiner System Prompt

```
You are an expert document editor integrated into a technical writing tool.
You will receive:
1. The current Markdown document
2. A user request in the chat_history
3. The original structured steps for context

Your task is to apply ONLY the user's requested changes precisely and return the
updated Markdown. Do not modify sections unrelated to the user's request unless
explicitly instructed. If the user requests a re-capture, set the "recapture_step"
field in your JSON response to the step index.

Maintain the document's existing formatting, heading hierarchy, and style unless
the user specifically asks you to change them.
```

---

_← Previous: [Architecture Design Document](./02_architecture_design.md)_  
_→ Next: [API Reference](./04_api_reference.md)_

---

_Document ID: DOC-003 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite_
