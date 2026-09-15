# Architecture Design Document

**Document ID:** DOC-002  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Backend Engineers, System Architects

---

## Table of Contents

1. [Architecture Philosophy](#1-architecture-philosophy)
2. [System Component Overview](#2-system-component-overview)
3. [Detailed Architecture Diagram](#3-detailed-architecture-diagram)
4. [Frontend Layer](#4-frontend-layer)
5. [Backend Orchestration Layer](#5-backend-orchestration-layer)
6. [LangGraph State Machine Layer](#6-langgraph-state-machine-layer)
7. [Playwright Capture Engine Layer](#7-playwright-capture-engine-layer)
8. [LLM Inference Layer](#8-llm-inference-layer)
9. [Media & Storage Layer](#9-media--storage-layer)
10. [Communication Protocols](#10-communication-protocols)
11. [Execution Pipeline](#11-execution-pipeline)
12. [Technology Stack Reference](#12-technology-stack-reference)
13. [Architecture Decision Records](#13-architecture-decision-records)

---

## 1. Architecture Philosophy

DocuAgent AI is designed around four core architectural principles:

| Principle | Description |
|-----------|-------------|
| **Decoupled Layers** | Each system layer communicates through well-defined interfaces, allowing independent scaling and replacement |
| **Asynchronous Execution** | All long-running operations (browser automation, LLM inference) run asynchronously to maintain UI responsiveness |
| **State Persistence** | A centralized shared state (`ManualState`) ensures all agents have consistent, synchronized knowledge |
| **Graceful Degradation** | Every failure path produces a usable partial output rather than a hard error |

---

## 2. System Component Overview

DocuAgent AI comprises five principal architectural layers and their sub-components:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: FRONTEND                                                              │
│  React (Vite) SPA · Tailwind CSS · Zustand · Monaco Editor · shadcn/ui         │
└─────────────────────────────────────────────────────────────────────────────────┘
                              ↕ REST · SSE · WebSocket
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Layer 2: BACKEND ORCHESTRATOR                                                  │
│  FastAPI (Python 3.11+) · Pydantic · Celery · Redis                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                    ↕                                    ↕
┌──────────────────────────────────┐   ┌────────────────────────────────────────┐
│  Layer 3: LANGGRAPH STATE MACHINE│   │  Layer 4: PLAYWRIGHT CAPTURE ENGINE    │
│  5 Specialized AI Agents         │   │  Headless Chromium · DOM Injector      │
│  MemorySaver / Redis Checkpointer│   │  Auth Session · Screenshot Capture     │
└────────────────┬─────────────────┘   └────────────────────────────────────────┘
                 │ Ollama Cloud API
┌────────────────▼─────────────────┐   ┌────────────────────────────────────────┐
│  Layer 5a: LLM INFERENCE         │   │  Layer 5b: MEDIA & STORAGE             │
│  Llama 3.3 70B · Qwen 2.5 72B    │   │  Screenshot Assets · WeasyPrint · PDF  │
└──────────────────────────────────┘   └────────────────────────────────────────┘
```

---

## 3. Detailed Architecture Diagram

```
                        ┌─────────────────────────────────────────────┐
                        │              FRONTEND LAYER                  │
                        │                                             │
                        │  ┌───────────────┐  ┌──────────────────┐  │
                        │  │  Script Input │  │  Chat Interface  │  │
                        │  │  Form + URL   │  │  (Chat Panel)    │  │
                        │  └───────┬───────┘  └────────┬─────────┘  │
                        │          │                   │             │
                        │  ┌───────▼───────────────────▼──────────┐  │
                        │  │     Split-Screen Editor               │  │
                        │  │  Monaco (Left) | Preview (Right)      │  │
                        │  └───────────────────────────────────────┘  │
                        │          │  Zustand State Store              │
                        └──────────┼──────────────────────────────────┘
                                   │
                     REST POST /api/v1/generate
                     SSE  GET  /api/v1/stream/{job_id}
                     WS   WS   /api/v1/chat/{session_id}
                                   │
                        ┌──────────▼──────────────────────────────────┐
                        │          FASTAPI ORCHESTRATOR               │
                        │                                             │
                        │  ┌──────────────┐  ┌─────────────────────┐ │
                        │  │  /generate   │  │  /chat              │ │
                        │  │  endpoint    │  │  endpoint           │ │
                        │  └──────┬───────┘  └──────────┬──────────┘ │
                        │         │                     │            │
                        │  ┌──────▼─────────────────────▼──────────┐ │
                        │  │     Celery Task Queue (Redis Broker)   │ │
                        │  └──────────────────┬─────────────────────┘ │
                        └─────────────────────┼────────────────────── ┘
                                              │
                   ┌──────────────────────────┴───────────────────────────┐
                   │                                                      │
        ┌──────────▼──────────────────────┐       ┌──────────────────────▼────┐
        │     LANGGRAPH STATE MACHINE     │       │  PLAYWRIGHT CAPTURE ENGINE │
        │                                 │       │                            │
        │  ManualState (Shared Context)   │       │  ┌──────────────────────┐  │
        │  ┌─────────────────────────┐   │       │  │  Chromium (Headless) │  │
        │  │  Agent 1: Analyzer     │   │       │  │  Session Manager     │  │
        │  │  Agent 2: Capturer     │◄──┼───────┼──│  DOM Injector        │  │
        │  │  Agent 3: Writer       │   │       │  │  Highlight Engine    │  │
        │  │  Agent 4: QA Reviewer  │   │       │  │  Screenshot Saver    │  │
        │  │  Agent 5: Refiner      │   │       │  └──────────────────────┘  │
        │  └─────────────────────────┘   │       └────────────────────────────┘
        │                                 │
        │  Ollama Cloud API (TLS)         │       ┌────────────────────────────┐
        └─────────────────┬───────────────┘       │  MEDIA & STORAGE           │
                          │                       │  /assets/screenshots/      │
              ┌───────────▼────────────┐          │  WeasyPrint PDF Engine     │
              │  OLLAMA CLOUD          │          │  Pandoc Markdown → HTML    │
              │  Llama 3.3 70B         │          └────────────────────────────┘
              │  Qwen 2.5 72B          │
              └────────────────────────┘
```

---

## 4. Frontend Layer

### 4.1 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Build Tool | Vite | Latest |
| UI Framework | React | 18+ |
| Styling | Tailwind CSS + CSS Modules | 3+ |
| Component Library | shadcn/ui + Lucide Icons | Latest |
| State Management | Zustand | 4+ |
| Code Editor | Monaco Editor / @uiw/react-md-editor | Latest |

### 4.2 Application Structure

The React SPA is organized into four primary functional areas:

```
src/
├── components/
│   ├── ScriptInput/       # Workflow script input form & credential fields
│   ├── Editor/            # Monaco split-screen Markdown editor
│   ├── Preview/           # Real-time Markdown preview renderer
│   ├── Chat/              # Conversational refinement panel
│   └── ExportBar/         # Download buttons (MD / HTML / PDF)
├── store/
│   └── useManualStore.ts  # Zustand global state (markdown, chat history, job status)
├── hooks/
│   ├── useSSEStream.ts    # Server-Sent Events consumer for live progress
│   └── useWebSocket.ts    # WebSocket client for chat session
└── api/
    └── client.ts          # Axios REST client for FastAPI endpoints
```

### 4.3 Data Flow Within Frontend

```
User Input Form
     │
     ▼
POST /api/v1/generate
     │
     ▼
SSE Stream ──► useSSEStream hook ──► Zustand store update ──► UI re-render
     │
     ▼
Markdown content available in Editor (left pane) + Preview (right pane)
     │
     ▼
User types in Chat Panel ──► WebSocket ──► POST /api/v1/chat
     │
     ▼
Targeted Markdown node updated ──► Store update ──► Editor refresh
```

---

## 5. Backend Orchestration Layer

### 5.1 FastAPI Application

The FastAPI backend serves as the central orchestrator routing requests to the appropriate processing layers.

**Core Responsibilities:**
- Accepting and validating incoming generation requests.
- Delegating long-running generation jobs to Celery task workers.
- Managing SSE streaming channels for real-time progress delivery.
- Maintaining WebSocket connections for the chat interface.
- Serving completed Markdown content and triggering export conversion.

### 5.2 Asynchronous Task Architecture

Long-running tasks (full manual generation, bulk re-captures) are offloaded to **Celery** workers backed by a **Redis** message broker. This prevents HTTP request timeouts and enables multi-tenant concurrency.

```
FastAPI Request Handler
         │
         ▼
  Celery Task Enqueue ──► Redis Broker ──► Celery Worker Process
                                                    │
                                                    ▼
                                        LangGraph execution begins
                                                    │
                                                    ▼
                                       SSE events published to Redis PubSub
                                                    │
                                                    ▼
                                   FastAPI SSE endpoint reads & forwards to client
```

### 5.3 Key API Endpoints (Summary)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate` | Submit a new manual generation job |
| `GET` | `/api/v1/stream/{job_id}` | Subscribe to SSE progress stream |
| `GET` | `/api/v1/jobs/{job_id}` | Poll job status |
| `POST` | `/api/v1/chat/{session_id}` | Send a refinement chat message |
| `GET` | `/api/v1/export/{job_id}` | Download final document in specified format |
| `POST` | `/api/v1/recapture/{job_id}/{step_index}` | Re-trigger Playwright for a single step |

> 📌 **Full endpoint specifications with request/response schemas are in [API Reference](./04_api_reference.md).**

---

## 6. LangGraph State Machine Layer

### 6.1 State Schema (`ManualState`)

The `ManualState` TypedDict is the shared execution context passed between all agents:

```python
class ManualState(TypedDict):
    raw_input_script: str              # Original user-provided workflow text
    target_url: str                    # Staging application URL
    credentials: dict                  # Auth credentials (in-memory only, not persisted)
    structured_steps: list[StepSchema] # Parsed JSON DAG of UI actions
    screenshot_assets: dict[int, str]  # step_index → file_path mapping
    markdown_content: str              # Current compiled Markdown document
    chat_history: list[ChatMessage]    # Multi-turn conversation log
    execution_logs: list[str]          # Internal agent activity log
    quality_approved: bool             # Quality gate flag
    error_states: dict                 # Per-step error registry
```

### 6.2 Agent Graph Topology

```
START
  │
  ▼
analyze_script_node (Agent 1)
  │
  ▼
capture_screenshots_node (Agent 2) ◄──────────────────┐
  │                                                    │
  ▼                                              (Re-capture triggered)
compile_markdown_node (Agent 3)                        │
  │                                                    │
  ▼                                                    │
quality_review_node (Agent 4)                          │
  │                                                    │
  ├── [Approved] ──► HUMAN INTERRUPT ◄── chat_refiner_node (Agent 5)
  │                       │
  └── [Rejected] ──────────┘ (Loop back to compile_markdown_node)
```

### 6.3 State Persistence

- **Development/Single Instance:** `MemorySaver` checkpointer (in-process memory).
- **Production/Multi-tenant:** `RedisCheckpointer` — persists state to Redis with TTL-based expiry, enabling fault recovery and session resume.

For full agent specifications, see [Multi-Agent Design Specification](./03_multi_agent_specification.md).

---

## 7. Playwright Capture Engine Layer

### 7.1 Engine Architecture

The Playwright engine operates as a **managed subprocess** controlled by the LangGraph Playwright Visual Capturer Agent. It uses the Playwright Python Async API with a persistent browser context.

### 7.2 Execution Sequence

```
Agent 2 calls capture_step(step: StepSchema)
  │
  ▼
Browser context initialized (Chromium headless)
  │
  ▼
Authentication performed (session storage injected if credentials provided)
  │
  ▼
Navigation to target URL
  │
  ▼
Target selector located (with timeout fallback)
  │
  ├── [Found] ──► CSS highlight injected → viewport scroll → screenshot saved
  │
  └── [Not Found / Timeout] ──► Warning logged → full viewport screenshot saved
  │
  ▼
Screenshot file path registered in ManualState.screenshot_assets[step_index]
```

For detailed highlight injection logic and fallback strategies, see [Browser Automation Engine](./05_browser_automation_engine.md).

---

## 8. LLM Inference Layer

### 8.1 Ollama Cloud Integration

All LLM inference calls are made to **Ollama Cloud** endpoints via the LangChain `ChatOllama` interface.

**Configuration:**

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url="https://ollama-cloud.example.com",
    model="llama3.3:70b",
    temperature=0.2,          # Low temperature for deterministic technical writing
    streaming=True,           # Enables SSE token streaming to frontend
    timeout=120,
)
```

### 8.2 Model Selection Strategy

| Agent | Preferred Model | Rationale |
|-------|----------------|-----------|
| Script Analyzer | Qwen 2.5 72B | Superior JSON schema generation and instruction following |
| Technical Writer | Llama 3.3 70B | Best-in-class technical prose quality |
| Quality Reviewer | Llama 3.3 70B | Strong reasoning for logical consistency checks |
| Conversational Refiner | Qwen 2.5 72B | Fast response for interactive chat latency requirements |

### 8.3 Prompt Engineering

Each agent uses a structured prompt template with:
- **System Message:** Agent role definition and output format constraints.
- **Human Message:** Current task context injected from `ManualState`.
- **Output Parser:** Pydantic model or JSON parser for structured output validation.

---

## 9. Media & Storage Layer

### 9.1 Screenshot Storage

Screenshots are saved to a local filesystem path during development. In production, this should be backed by an S3-compatible object store.

```
assets/
└── {job_id}/
    ├── step_001.png
    ├── step_002.png
    ├── step_003.png
    └── ...
```

### 9.2 Export Engine

| Format | Tool | Description |
|--------|------|-------------|
| **Markdown** | Native | Direct state content, UTF-8 encoded |
| **HTML** | Pandoc | Pandoc converts Markdown with embedded base64 image support |
| **PDF** | WeasyPrint | High-fidelity HTML-to-PDF with CSS styling and embedded images |

---

## 10. Communication Protocols

| Interface | Protocol | Direction | Purpose |
|-----------|---------|-----------|---------|
| Job submission | REST (HTTPS POST) | Client → Server | Submit generation request |
| Progress monitoring | SSE (HTTP/1.1) | Server → Client | Stream pipeline events |
| Chat interface | WebSocket (WSS) | Bidirectional | Real-time chat with agent |
| Job status poll | REST (HTTPS GET) | Client → Server | Fallback status polling |
| Export download | REST (HTTPS GET) | Client → Server | Retrieve final document |
| LLM inference | HTTPS (REST) | Server → Ollama Cloud | Token generation |
| Task queue | Redis RESP | Internal | Celery task broker |

---

## 11. Execution Pipeline

The end-to-end execution pipeline from user input to final document:

```
Step 1: User submits workflow script + target URL + credentials
         ↓
Step 2: FastAPI validates input → enqueues Celery task → returns job_id
         ↓
Step 3: Frontend opens SSE stream on /api/v1/stream/{job_id}
         ↓
Step 4: LangGraph → analyze_script_node
         LLM parses script → structured JSON steps DAG
         SSE: "Script analyzed. N steps identified."
         ↓
Step 5: LangGraph → capture_screenshots_node
         Playwright executes each step, highlights elements, captures PNGs
         SSE: "Captured step 1/N... step 2/N..."
         ↓
Step 6: LangGraph → compile_markdown_node
         Technical Writer Agent merges steps + screenshots → Markdown
         SSE: "Document draft compiled."
         ↓
Step 7: LangGraph → quality_review_node
         QA Agent reviews → approves or loops back to Step 6
         SSE: "Quality review passed."
         ↓
Step 8: LangGraph reaches HUMAN INTERRUPT checkpoint
         Frontend receives full Markdown content via SSE
         Split-screen editor becomes active
         ↓
Step 9: [Optional] User sends chat messages → Conversational Refiner Agent
         Targeted document nodes updated → Editor refreshed
         ↓
Step 10: User clicks Export → WeasyPrint/Pandoc generates PDF/HTML → Download
```

---

## 12. Technology Stack Reference

| Layer | Technology | Version | Justification |
|-------|-----------|---------|--------------|
| Frontend Framework | React (Vite) | 18+ | Fast HMR, component isolation, large ecosystem |
| Styling | Tailwind CSS + CSS Modules | 3+ | Rapid design, responsive layouts, dark mode |
| UI Components | shadcn/ui + Lucide Icons | Latest | Accessible, enterprise-grade UI primitives |
| State Management | Zustand | 4+ | Lightweight, minimal boilerplate client state |
| Editor | Monaco Editor / @uiw/react-md-editor | Latest | Syntax-highlighted Markdown with live preview |
| Backend | FastAPI (Python 3.11+) | 0.100+ | Async, Pydantic support, high throughput |
| Agent Orchestration | LangGraph + LangChain Core | Latest | State machine, cyclic workflows, HITL |
| Browser Automation | Playwright Python SDK | 1.40+ | Modern headless browser, multi-browser |
| LLM Inference | Ollama Cloud API | Latest | Enterprise privacy, fast cloud execution |
| Primary LLMs | Llama 3.3 70B / Qwen 2.5 72B | Latest | Technical writing, JSON generation |
| Task Queue | Celery + Redis | 5+ | Async worker pool, multi-tenant support |
| Export (PDF) | WeasyPrint | 60+ | High-fidelity PDF with CSS support |
| Export (HTML) | Pandoc | 3+ | Standards-compliant HTML conversion |
| State Persistence | Redis (Checkpointer) | 7+ | LangGraph production checkpointing |

---

## 13. Architecture Decision Records

### ADR-001: LangGraph over Custom Orchestration

**Decision:** Use LangGraph for agent orchestration.  
**Rationale:** LangGraph provides built-in support for cyclical agent loops, state persistence (checkpointing), and Human-in-the-Loop interrupt handling — all of which would require significant custom engineering otherwise.  
**Trade-offs:** Additional framework dependency; steeper initial learning curve for team members unfamiliar with LangGraph.

### ADR-002: Playwright over Selenium

**Decision:** Use Playwright Python SDK for browser automation.  
**Rationale:** Playwright supports modern web standards (Shadow DOM, dynamic SPA rendering), has faster execution, and provides native async support. Selenium's legacy architecture introduces unnecessary complexity.  
**Trade-offs:** Less community tooling history versus Selenium in enterprise QA environments.

### ADR-003: Ollama Cloud over OpenAI API

**Decision:** Use Ollama Cloud for LLM inference.  
**Rationale:** Enterprise data privacy requirements prohibit sending customer workflow data to third-party LLM providers. Ollama Cloud provides dedicated endpoints with TLS encryption and no training data retention.  
**Trade-offs:** Requires infrastructure management of Ollama Cloud endpoints versus turnkey OpenAI API access.

### ADR-004: SSE over WebSocket for Progress Streaming

**Decision:** Use Server-Sent Events (SSE) for pipeline progress and WebSocket only for bidirectional chat.  
**Rationale:** SSE is unidirectional (server → client) and simpler to implement for one-way progress streaming. WebSockets are reserved for the chat panel where bidirectional low-latency communication is required.

---

*← Previous: [System Overview](./01_system_overview.md)*  
*→ Next: [Multi-Agent Design Specification](./03_multi_agent_specification.md)*

---

*Document ID: DOC-002 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
