# DocuAgent AI — Master Implementation Checklist & TODO

**Document ID:** CHK-001  
**Version:** 1.0.0  
**Status:** Active  
**Companion Document:** [Full Development Plan](./DEVELOPMENT_PLAN.md)  
**Last Updated:** September 2026  
**Audience:** All Engineering Roles, QA, DevOps, Project Leads

---

## Table of Contents

1. [Checklist Legend & Tracking System](#1-checklist-legend--tracking-system)
2. [Phase 1: Project Foundation & Environment Setup](#2-phase-1-project-foundation--environment-setup)
3. [Phase 2: Backend Architecture & FastAPI Core](#3-phase-2-backend-architecture--fastapi-core)
4. [Phase 3: LangGraph Multi-Agent State Machine](#4-phase-3-langgraph-multi-agent-state-machine)
5. [Phase 4: Playwright Browser Automation Engine](#5-phase-4-playwright-browser-automation-engine)
6. [Phase 5: Task Queue, Workers & Streaming (Celery/Redis/SSE)](#6-phase-5-task-queue-workers--streaming-celeryredissse)
7. [Phase 6: Frontend React SPA & Monaco Editor](#7-phase-6-frontend-react-spa--monaco-editor)
8. [Phase 7: End-to-End Pipeline & Media Engine](#8-phase-7-end-to-end-pipeline--media-engine)
9. [Phase 8: Security, Guardrails & Credential Scrubbing](#9-phase-8-security-guardrails--credential-scrubbing)
10. [Phase 9: Quality Assurance, Testing & Validation](#10-phase-9-quality-assurance-testing--validation)
11. [Phase 10: Infrastructure, Docker, CI/CD & Deployment](#11-phase-10-infrastructure-docker-cicd--deployment)
12. [Sprint-by-Sprint Execution Tracker](#12-sprint-by-sprint-execution-tracker)

---

## 1. Checklist Legend & Tracking System

Use standard Markdown task checkboxes to track progress:

- `[ ]` Open / Pending
- `[/]` In Progress
- `[x]` Completed
- `[!]` Blocked / Impeded

Each item is categorized by priority tag:

- **[P0]**: Critical path item; blocks release or dependent subsystems.
- **[P1]**: High priority; expected for standard operation.
- **[P2]**: Polish, optimization, or nice-to-have extension.

---

## 2. Phase 1: Project Foundation & Environment Setup

### 2.1 Monorepo & Git Governance

- [x] **[P0]** Initialize Git repository and directory tree (`/backend`, `/frontend`, `/docs`, `/scripts`, `/deploy`).
- [x] **[P0]** Configure `.gitignore` for Python (`.venv`, `__pycache__`, `*.pyc`), Node (`node_modules`, `dist`), and runtime assets (`assets/*`, `exports/*`).
- [x] **[P1]** Establish branch protection rules for `main` and `develop` requiring status checks and approvals.
- [x] **[P1]** Set up Pre-commit hooks (`pre-commit install`) with Ruff, Black/Flake8, ESLint, Prettier.
- [x] **[P2]** Configure commit linter enforcing Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).

### 2.2 Backend Environment Bootstrap

- [x] **[P0]** Verify Python 3.11+ environment and virtual environment tooling (`python3.11 -m venv .venv`).
- [x] **[P0]** Pin backend dependencies in `backend/requirements.txt` (FastAPI, Uvicorn, LangGraph, Playwright, Celery, Redis, Pydantic).
- [x] **[P0]** Pin developer dependencies in `backend/requirements-dev.txt` (pytest, pytest-asyncio, mypy, ruff, httpx).
- [x] **[P0]** Create `backend/.env.example` defining all required configuration variables.
- [x] **[P1]** Configure `pyproject.toml` with strict Ruff and Mypy rule configurations.

### 2.3 Frontend Environment Bootstrap

- [x] **[P0]** Initialize React 18+ Vite project with TypeScript (`npm create vite@latest frontend -- --template react-ts`).
- [x] **[P0]** Configure Tailwind CSS 3+ with PostCSS and Autoprefixer.
- [x] **[P0]** Install and configure `shadcn/ui` primitives and `lucide-react` icon library.
- [x] **[P0]** Install core dependencies: `zustand`, `@monaco-editor/react`, `axios`, `react-markdown`, `remark-gfm`.
- [x] **[P1]** Create `frontend/.env.example` defining API endpoints and feature flags.
- [x] **[P1]** Set up TypeScript configuration (`tsconfig.json`) in strict mode.

### 2.4 Infrastructure & Tooling Prerequisites

- [x] **[P0]** Verify Docker and Docker Compose v2.20+ installation.
- [x] **[P0]** Test network connectivity and authentication to Ollama Cloud LLM endpoint.
- [x] **[P0]** Verify availability of models `llama3.3:70b` and `qwen2.5:72b` on Ollama Cloud instance.
- [x] **[P0]** Run initial Playwright headless installation verification (`playwright install chromium && playwright install-deps`).

---

## 3. Phase 2: Backend Architecture & FastAPI Core

### 3.1 Config, Logging & Middleware

- [x] **[P0]** Implement `backend/app/config.py` using `pydantic-settings` to parse and validate all environment variables.
- [x] **[P0]** Implement `SensitiveDataFilter` in `backend/app/utils/logging.py` to redact credentials and tokens from logs.
- [x] **[P0]** Implement custom structured JSON logging middleware emitting timestamp, log level, request ID, and message.
- [x] **[P0]** Implement Bearer token verification middleware in `backend/app/middleware/auth.py`.
- [x] **[P1]** Implement CORS middleware with explicit allowed origins for local and staging domains.
- [x] **[P1]** Implement API rate limiting using `slowapi` on generation endpoints.

### 3.2 Data Models & Pydantic Schemas

- [x] **[P0]** Define `StepSchema` model with `index`, `description`, `action_type`, `target_selector`, `input_value`, `expected_url`, `domain_context`, `selector_hints`.
- [x] **[P0]** Define `ChatMessage` model (`role`, `content`, `timestamp`).
- [x] **[P0]** Define `GenerateRequest` model with input validation (minimum script length, valid URL).
- [x] **[P0]** Define `GenerateResponse`, `JobStatusResponse`, and `ChatResponse` models.
- [x] **[P0]** Define standard `ErrorResponse` schema matching DOC-004 specification.

### 3.3 REST API Endpoints

- [x] **[P0]** Implement `GET /health` with system status, active version, and timestamp.
- [x] **[P0]** Implement `POST /api/v1/generate` to accept payload, validate URL, trigger task, and return `job_id` + `session_id`.
- [x] **[P0]** Implement `GET /api/v1/jobs/{job_id}` for polling job execution state and metadata.
- [x] **[P1]** Implement `DELETE /api/v1/jobs/{job_id}` to terminate active execution and purge temporary assets.
- [x] **[P1]** Implement `POST /api/v1/recapture/{job_id}/{step_index}` to trigger targeted single-step re-execution.
- [x] **[P1]** Implement `POST /api/v1/jobs/{job_id}/assets/{step_index}` for multipart screenshot replacement uploads.

---

## 4. Phase 3: LangGraph Multi-Agent State Machine

### 4.1 State Definition & Checkpointing

- [x] **[P0]** Define `ManualState` TypedDict with fields: `raw_input_script`, `target_url`, `credentials`, `structured_steps`, `screenshot_assets`, `markdown_content`, `chat_history`, `execution_logs`, `quality_approved`, `error_states`.
- [x] **[P0]** Configure development checkpointer using `MemorySaver`.
- [x] **[P0]** Configure production checkpointer using `RedisSaver` (`langgraph.checkpoint.redis`).
- [x] **[P0]** Ensure `credentials` dictionary is purged from state prior to checkpointer serialization.

### 4.2 Agent 1: Script & Domain Analyzer (`analyze_script_node`)

- [x] **[P0]** Configure LLM client with Qwen 2.5 72B for JSON and structured reasoning.
- [x] **[P0]** Implement prompt template extracting actionable UI interactions into a JSON DAG of `StepSchema` objects.
- [x] **[P0]** Implement domain classification logic (E-commerce, CRM, SaaS, Admin Portal, Finance).
- [x] **[P1]** Add selector heuristic synthesis providing 2–3 fallback selectors per step.
- [x] **[P1]** Add automatic retry and recovery for malformed LLM JSON output.

### 4.3 Agent 2: Playwright Visual Capturer (`capture_screenshots_node`)

- [x] **[P0]** Implement `capture_screenshots_node` in `backend/app/agents/capture_agent.py` orchestrating browser automation.
- [x] **[P0]** Connect state machine to `PlaywrightCaptureEngine` async context manager.
- [x] **[P0]** Iterate over `structured_steps` and execute browser action dispatch, highlight injection, and viewport capture sequence.
- [x] **[P0]** Map captured screenshots to `screenshot_assets` dictionary (`{step_index: asset_path}`) in `ManualState`.
- [x] **[P0]** Enforce immediate credential scrubbing (`state["credentials"] = {}`) immediately after browser authentication.
- [x] **[P1]** Register per-step capture errors into `error_states` and provide fallback placeholder handling without breaking pipeline.

### 4.4 Agent 3: Technical Writer & Layout Agent (`compile_markdown_node`)

- [x] **[P0]** Configure LLM client with Llama 3.3 70B for technical document synthesis.
- [x] **[P0]** Implement prompt structuring standard sections: Prerequisites, System Overview, Step-by-Step Walkthrough, and Troubleshooting.
- [x] **[P0]** Map screenshot assets (`screenshot_assets[step_index]`) to corresponding Markdown image markdown tags.
- [x] **[P1]** Format callout blocks (`> 💡 Tip:`, `> ⚠️ Warning:`, `> 📌 Note:`).
- [x] **[P1]** Implement logic to consume `quality_feedback` when re-compiling after a quality rejection loop.

### 4.5 Agent 4: Quality & Verification Agent (`quality_review_node`)

- [x] **[P0]** Implement evaluation prompt auditing completeness, screenshot coverage, tone consistency, and logical sequencing.
- [x] **[P0]** Implement conditional edge evaluator `route_after_quality_review()`.
- [x] **[P0]** Implement loop guard enforcing maximum 3 re-generation attempts before forced approval.
- [x] **[P1]** Populate structured `quality_feedback` notes on review failure.

### 4.6 Agent 5: Conversational Refiner Agent (`chat_refiner_node`)

- [x] **[P0]** Implement chat edit classifier distinguishing text edits, structural revisions, and recapture triggers.
- [x] **[P0]** Implement surgical Markdown section updater replacing only affected heading blocks.
- [x] **[P1]** Implement full-document translation logic preserving structure and image links.
- [x] **[P1]** Handle recapture signals returning `recapture_step_index` to orchestrator.

### 4.7 Graph Compilation & Interrupt Handling

- [x] **[P0]** Construct `StateGraph(ManualState)` wiring all nodes and conditional edges.
- [x] **[P0]** Set `interrupt_before=["chat_refiner_node"]` to halt graph execution for human interaction.
- [x] **[P0]** Implement resumption workflow upon receipt of new chat messages or re-run requests.

---

## 5. Phase 4: Playwright Browser Automation Engine (Agent 2 Infrastructure)

### 5.1 Async Automation Harness

- [x] **[P0]** Implement `PlaywrightCaptureEngine` async context manager (`__aenter__` / `__aexit__`).
- [x] **[P0]** Configure Chromium launch arguments (`--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`, `--window-size=1440,900`).
- [x] **[P0]** Configure browser context with viewport (1440×900), locale (`en-US`), and `ignore_https_errors=True`.
- [x] **[P0]** Enforce SSRF protection in `validate_target_url()` blocking loopback and RFC 1918 private subnets.

### 5.2 Authentication & Session Injector

- [x] **[P0]** Implement form login handler finding username/password inputs via robust selector chains.
- [x] **[P0]** Implement pre-authenticated storage injection (`localStorage`, `sessionStorage`, cookies).
- [x] **[P0]** Ensure staging credentials in `ManualState.credentials` are cleared immediately following authentication.

### 5.3 Action Execution Dispatcher

- [x] **[P0]** Implement `execute_action()` dispatcher supporting `navigate`, `click`, `type`, `scroll`, `wait`, `authenticate`.
- [x] **[P0]** Implement human-like type delay (30–50ms) to bypass basic UI input debounce issues.
- [x] **[P0]** Implement automatic scroll-into-view before click and input actions.
- [x] **[P1]** Implement intelligent wait states (`wait_for_load_state("networkidle")` with fallback to `"domcontentloaded"`).

### 5.4 Dynamic Highlight & Overlay Injector

- [x] **[P0]** Implement real-time DOM styling injecting cyan border (`outline: 4px solid #06b6d4`).
- [x] **[P0]** Inject element glow effect (`box-shadow: 0 0 0 8px rgba(6, 182, 212, 0.2)`).
- [x] **[P0]** Inject dimming backdrop overlay (`rgba(0, 0, 0, 0.15)`) on non-target elements.
- [x] **[P0]** Implement `cleanup_highlights()` to remove injected DOM artifacts before taking subsequent steps.

### 5.5 Capture & Fallback Engine

- [x] **[P0]** Capture viewport PNG screenshots saved to `assets/{job_id}/step_{index:03d}.png`.
- [x] **[P0]** Implement selector timeout fallback (try primary → try selector hints → capture general viewport fallback).
- [x] **[P0]** Record failure diagnostics in `state["error_states"][step.index]` without breaking pipeline execution.
- [x] **[P1]** Implement full text-only fallback generating placeholder tags (`[Insert Screenshot Here: ...]`) if browser crashes or encounters CAPTCHA.

### 5.6 Agent 2 Integration & State Coordination

- [x] **[P0]** Implement `app/agents/capture_agent.py` binding `capture_screenshots_node` to `PlaywrightCaptureEngine`.
- [x] **[P0]** Implement per-step event publishing for SSE streaming (`capture_progress`) via Redis Pub/Sub.
- [x] **[P0]** Verify staging credentials in `ManualState.credentials` are purged immediately following authentication.
- [x] **[P1]** Integrate target element highlight verification against common frontend component patterns.

---

## 6. Phase 5: Task Queue, Workers & Streaming (Celery/Redis/SSE)

### 6.1 Task Distribution & Celery Configuration

- [x] **[P0]** Configure Celery app with Redis broker (`redis://redis:6379/1`) and result backend (`redis://redis:6379/2`).
- [x] **[P0]** Define dedicated queues: `generation`, `capture`, `export`.
- [x] **[P0]** Implement `generate_manual` Celery task wrapping LangGraph pipeline execution.
- [x] **[P0]** Configure worker auto-restart policies (`--max-tasks-per-child=50`) to prevent Chromium memory accumulation.
- [x] **[P1]** Implement `cleanup_expired_jobs` periodic Celery Beat task removing assets older than retention TTL (24h).

### 6.2 Real-time Progress Streaming (SSE)

- [x] **[P0]** Implement `GET /api/v1/stream/{job_id}` Server-Sent Events endpoint using `EventSourceResponse`.
- [x] **[P0]** Implement Redis PubSub publisher inside LangGraph agent lifecycle callbacks.
- [x] **[P0]** Standardize SSE event payloads: `pipeline_started`, `script_analyzed`, `capture_progress`, `draft_compiled`, `quality_approved`, `document_ready`, `job_failed`.
- [x] **[P1]** Add heartbeat ping events every 15s to keep proxy connections alive.

### 6.3 Bidirectional Chat (WebSocket)

- [x] **[P0]** Implement `WS /api/v1/ws/chat/{session_id}` WebSocket handler.
- [x] **[P0]** Handle client incoming message validation and dispatch to Agent 5.
- [x] **[P0]** Stream agent document updates back over WebSocket connection.
- [x] **[P1]** Implement keep-alive ping/pong framing.

---

## 7. Phase 6: Frontend React SPA & Monaco Editor

### 7.1 Layout & State Store

- [x] **[P0]** Implement `AppShell` with navigation sidebar, status headers, and workspace container.
- [x] **[P0]** Implement `useManualStore` (Zustand) tracking `jobId`, `sessionId`, `jobStatus`, `markdownContent`, `stepStatuses`, `chatHistory`.
- [x] **[P1]** Add dark mode theme toggling with Tailwind CSS classes.
- [x] **[P1]** Add persistent settings storage (preferred output format, default language).

### 7.2 Workflow Script Input

- [x] **[P0]** Implement `ScriptInputForm` with script textarea, staging URL input, and credential inputs.
- [x] **[P0]** Sanitize credential inputs to ensure values are wiped from React state immediately upon dispatch.
- [x] **[P0]** Add client-side validation rules (URL format, script minimum 10 characters).
- [ ] **[P1]** Add options panel (language selector, output formats selector).

### 7.3 Split-Screen Editor & Preview

- [ ] **[P0]** Implement `SplitScreen` resizable divider container.
- [ ] **[P0]** Integrate `@monaco-editor/react` configured for Markdown, dark theme, word wrap, and synchronized value binding.
- [ ] **[P0]** Implement cursor position preservation when external updates modify Monaco content.
- [ ] **[P0]** Implement `PreviewPane` rendering Markdown via `react-markdown` and `remark-gfm`.
- [ ] **[P0]** Implement `ScreenshotImage` component in preview supporting click-to-recapture and manual upload overlays.

### 7.4 Live Progress & Chat Interface

- [ ] **[P0]** Implement `useSSEStream` custom hook handling automatic reconnection and store dispatches.
- [ ] **[P0]** Implement `ProgressBar` and `StepStatus` badges visualizing step-by-step progress.
- [ ] **[P0]** Implement `ChatPanel` with conversational bubble history, auto-scroll, and message composer.
- [ ] **[P0]** Implement `useWebSocket` hook maintaining persistent bidirectional connection.
- [ ] **[P1]** Add typing indicator ("DocuAgent is refining the document...").

### 7.5 Export Control Bar

- [ ] **[P0]** Implement `ExportBar` with download triggers for Markdown (`.md`), HTML (`.html`), and PDF (`.pdf`).
- [ ] **[P0]** Implement `useExport` hook streaming file downloads via Blob object URLs.
- [ ] **[P1]** Display export generation spinners during conversion process.

---

## 8. Phase 7: End-to-End Pipeline & Media Engine

### 8.1 Export Engine Subsystem

- [ ] **[P0]** Implement Pandoc Markdown-to-HTML conversion utility.
- [ ] **[P0]** Implement base64 inline image embedding for standalone single-file HTML distributions.
- [ ] **[P0]** Implement WeasyPrint HTML-to-PDF compiler with custom print stylesheet (`backend/app/templates/pdf_style.css`).
- [ ] **[P0]** Implement `GET /api/v1/export/{job_id}?format={format}` endpoint streaming binary response.
- [ ] **[P1]** Optimize PDF page breaks (prevent orphan headings and split screenshot cards).

### 8.2 Media Asset Pipeline

- [ ] **[P0]** Enforce structured file organization (`assets/{job_id}/step_{index:03d}.png`).
- [ ] **[P0]** Expose static assets route in FastAPI / Nginx with cache headers.
- [ ] **[P1]** Implement image thumbnail generation for quick chat previews.
- [ ] **[P1]** Implement manual upload endpoint overwriting existing step screenshot asset.

---

## 9. Phase 8: Security, Guardrails & Credential Scrubbing

### 9.1 Credential Protection & Data Isolation

- [ ] **[P0]** Audit Python code to guarantee staging credentials are never serialized, written to disk, or logged.
- [ ] **[P0]** Verify `credentials` field exclusion in Pydantic models (`exclude=True`).
- [x] **[P0]** Verify credential stripping in `capture_screenshots_node` before LangGraph checkpoint saving.
- [ ] **[P0]** Confirm Redis checkpoint state does not contain plaintext credentials.

### 9.2 Network & Input Guardrails

- [ ] **[P0]** Implement SSRF IP validation blocking private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`).
- [ ] **[P0]** Implement Playwright route interception to reject redirects to internal network hosts.
- [ ] **[P0]** Sanitize Markdown preview rendering to neutralize Cross-Site Scripting (XSS).
- [ ] **[P0]** Enforce non-enumerable UUIDv4 identifiers for `job_id` and `session_id`.

### 9.3 Hardening & Audit

- [ ] **[P0]** Run `pip audit` and fix all high/critical vulnerabilities.
- [ ] **[P0]** Run `npm audit` on frontend dependencies and resolve critical alerts.
- [ ] **[P1]** Configure security headers: HSTS, CSP, X-Frame-Options, X-Content-Type-Options.
- [ ] **[P1]** Perform OWASP ZAP baseline vulnerability scan.

---

## 10. Phase 9: Quality Assurance, Testing & Validation

### 10.1 Automated Unit Tests

- [ ] **[P0]** Unit tests for Agent 1 (Script Analyzer) on 5 sample input workflows.
- [ ] **[P0]** Unit tests for Agent 3 (Technical Writer) verifying Markdown structure.
- [ ] **[P0]** Unit tests for Agent 4 (Quality Reviewer) approval and rejection logic.
- [ ] **[P0]** Unit tests for Agent 5 (Refiner) section-level replacements.
- [ ] **[P0]** Unit tests for URL validation and SSRF blocking rules.
- [ ] **[P0]** Unit tests for Zustand store actions and state transitions.

### 10.2 Integration & Pipeline Tests

- [ ] **[P0]** Integration test of the full LangGraph cyclic graph with mocked LLM responses.
- [ ] **[P0]** Integration test of Playwright highlight injection and screenshot capture against local mock HTML pages.
- [ ] **[P0]** Integration test of SSE streaming event emission from Celery worker through Redis to FastAPI client.
- [ ] **[P0]** Integration test of export generation (Markdown, HTML, PDF).

### 10.3 End-to-End Functional Tests

- [ ] **[P0]** Complete user flow: Submit script → Wait for generation → Inspect in editor → Export PDF.
- [ ] **[P0]** Refinement flow: Submit chat message → Verify targeted Markdown edit in Monaco editor.
- [ ] **[P0]** Re-capture flow: Click re-capture on screenshot → Verify updated asset in preview.
- [ ] **[P1]** Fault tolerance test: Run workflow with invalid CSS selector → Verify fallback screenshot and document completion.

### 10.4 Performance & Stress Tests

- [ ] **[P1]** Run k6 load test: 5 concurrent 10-step generation workflows completed within 5 minutes.
- [ ] **[P1]** Run API stress test: 100 concurrent health and status checks with p95 ≤ 200ms.
- [ ] **[P1]** Verify frontend Core Web Vitals (LCP ≤ 2.5s, TTI ≤ 3.5s).

---

## 11. Phase 10: Infrastructure, Docker, CI/CD & Deployment

### 11.1 Containerization

- [ ] **[P0]** Write `backend/Dockerfile` with Python 3.11, system dependencies for Playwright, and Gunicorn runner.
- [ ] **[P0]** Write `backend/Dockerfile.worker` for Celery task processing.
- [ ] **[P0]** Write `frontend/Dockerfile` multi-stage build (Node build → Nginx static serve).
- [ ] **[P0]** Create root `docker-compose.yml` defining `backend`, `worker`, `frontend`, `redis`, `nginx`, `flower`.
- [ ] **[P0]** Verify named volume persistence for Redis data, screenshots, and export files.

### 11.2 Reverse Proxy & Networking

- [ ] **[P0]** Configure `nginx/nginx.conf` with reverse proxy for `/api/`, static assets `/assets/`, and frontend SPA fallback routing.
- [ ] **[P0]** Configure Nginx SSE directives (`proxy_buffering off`, `proxy_read_timeout 600s`).
- [ ] **[P0]** Configure Nginx WebSocket upgrade headers for `/api/v1/ws/`.
- [ ] **[P1]** Configure SSL/TLS termination with modern cipher suites.

### 11.3 CI/CD Automation

- [ ] **[P0]** Implement GitHub Actions workflow for linting, typing, and unit test execution on pull requests.
- [ ] **[P1]** Implement Docker image build and registry push workflow upon merging to `main`.
- [ ] **[P1]** Implement automated staging deployment via SSH webhook or runner.

### 11.4 Operations & Observability

- [ ] **[P1]** Enable Prometheus metrics endpoint in FastAPI using `prometheus-fastapi-instrumentator`.
- [ ] **[P1]** Set up Celery Flower dashboard for background task visibility.
- [ ] **[P1]** Implement automated Redis RDB backup script via cron.
- [ ] **[P1]** Document system runbook covering service recovery, logs inspection, and credential rotation.

---

## 12. Sprint-by-Sprint Execution Tracker

| Sprint       | Timeline  | Focus Area                     | Deliverables & Milestones                                                           | Status |
| ------------ | --------- | ------------------------------ | ----------------------------------------------------------------------------------- | ------ |
| **Sprint 1** | Week 1–2  | Foundation & Core Backend      | Project bootstrap, FastAPI app, Agent 1 & Agent 3, Playwright capture basics        | `[ ]`  |
| **Sprint 2** | Week 3–4  | Multi-Agent Machine & Frontend | Agent 4 & Agent 5, LangGraph graph, Monaco Editor, Zustand store, SSE hook          | `[ ]`  |
| **Sprint 3** | Week 5–6  | Playwright Highlighting & HITL | Dynamic CSS highlight engine, chat WebSocket, fallback engine, manual upload        | `[ ]`  |
| **Sprint 4** | Week 7–8  | Integration, Celery & Export   | Celery task queues, WeasyPrint PDF export, full pipeline integration, security pass | `[ ]`  |
| **Sprint 5** | Week 9–10 | QA, Docker, Hardening & GA     | End-to-end testing, Docker Compose stack, Nginx TLS, load testing, v1.0.0 Release   | `[ ]`  |

---

_Document ID: CHK-001 · Version: 1.0.0 · DocuAgent AI Master Checklist & TODO_  
_Reference: [Full Development Plan](./DEVELOPMENT_PLAN.md) · [System Architecture](./02_architecture_design.md)_
