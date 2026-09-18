# DocuAgent AI — Full Development Plan

**Document ID:** PLAN-001  
**Version:** 1.0.0  
**Status:** Active  
**Last Updated:** September 2026  
**Owner:** Engineering Lead  
**Audience:** Engineering Team, Product Management, Project Stakeholders

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Development Methodology](#2-development-methodology)
3. [Team Structure & Roles](#3-team-structure--roles)
4. [Phase Overview](#4-phase-overview)
5. [Phase 1 — Project Foundation & Environment Setup](#5-phase-1--project-foundation--environment-setup)
6. [Phase 2 — Backend Core & LangGraph Agents](#6-phase-2--backend-core--langgraph-agents)
7. [Phase 3 — Playwright Browser Automation Engine](#7-phase-3--playwright-browser-automation-engine)
8. [Phase 4 — Frontend React Application](#8-phase-4--frontend-react-application)
9. [Phase 5 — Integration & End-to-End Pipeline](#9-phase-5--integration--end-to-end-pipeline)
10. [Phase 6 — Quality, Security & Hardening](#10-phase-6--quality-security--hardening)
11. [Phase 7 — Deployment & DevOps](#11-phase-7--deployment--devops)
12. [Phase 8 — Testing & QA](#12-phase-8--testing--qa)
13. [Phase 9 — Documentation & Knowledge Transfer](#13-phase-9--documentation--knowledge-transfer)
14. [Phase 10 — Release & Post-Launch](#14-phase-10--release--post-launch)
15. [Milestone Summary](#15-milestone-summary)
16. [Risk Register](#16-risk-register)
17. [Dependencies Map](#17-dependencies-map)
18. [Definition of Done](#18-definition-of-done)

---

## 1. Project Summary

| Field              | Value                                                                    |
| ------------------ | ------------------------------------------------------------------------ |
| **Project Name**   | DocuAgent AI — AI-Powered Dynamic User Manual Generator                  |
| **Version Target** | v1.0.0 General Availability                                              |
| **Start Date**     | October 2026                                                             |
| **Target GA Date** | December 2026 (10-week sprint plan)                                      |
| **Tech Stack**     | React · FastAPI · LangGraph · Playwright · Ollama Cloud · Redis · Celery |
| **Deployment**     | Docker Compose (MVP) → Kubernetes (Scale)                                |
| **Team Size**      | 4–6 engineers                                                            |

---

## 2. Development Methodology

- **Framework:** Agile Scrum with 2-week sprints.
- **Sprint Ceremonies:** Sprint Planning (Monday) · Daily Standup (15 min) · Sprint Review (Friday) · Retrospective (Friday).
- **Source Control:** Git with `main` (production), `develop` (integration), and `feature/*` / `fix/*` branches.
- **Code Review:** Minimum 1 peer review required before merging to `develop`. 2 reviews for `develop → main`.
- **CI/CD:** GitHub Actions pipeline — automated lint, type-check, unit tests, and Docker build on every push.
- **Issue Tracking:** GitHub Issues with labels: `feature`, `bug`, `security`, `chore`, `documentation`.

---

## 3. Team Structure & Roles

| Role                      | Responsibilities                                             | Count |
| ------------------------- | ------------------------------------------------------------ | ----- |
| **Backend Engineer**      | FastAPI, LangGraph agents, Celery, Redis, Ollama integration | 2     |
| **Frontend Engineer**     | React SPA, Monaco Editor, Zustand, SSE/WebSocket hooks       | 1     |
| **DevOps Engineer**       | Docker Compose, Nginx, CI/CD, monitoring, security           | 1     |
| **QA Engineer**           | Test planning, E2E testing, performance testing              | 1     |
| **Tech Lead / Architect** | Architecture decisions, code reviews, cross-cutting concerns | 1     |

---

## 4. Phase Overview

```
WEEK  1   2   3   4   5   6   7   8   9   10
      │───│───│───│───│───│───│───│───│───│
P1    ████
P2        ████████
P3            ████████
P4        ████████████
P5                    ████
P6                        ████
P7                    ████████
P8                            ████
P9    ████████████████████████████████████████  (ongoing)
P10                               ████████████

P1 = Foundation & Setup       P6 = Quality & Security
P2 = Backend & Agents         P7 = DevOps & Deployment
P3 = Browser Automation       P8 = Testing & QA
P4 = Frontend SPA             P9 = Documentation
P5 = E2E Integration          P10 = Release & Post-Launch
```

| Phase        | Name                                 | Duration | Sprint             |
| ------------ | ------------------------------------ | -------- | ------------------ |
| **Phase 1**  | Foundation & Environment Setup       | 1 week   | Sprint 1 (partial) |
| **Phase 2**  | Backend Core & LangGraph Agents      | 2 weeks  | Sprint 1–2         |
| **Phase 3**  | Playwright Browser Automation Engine | 2 weeks  | Sprint 2–3         |
| **Phase 4**  | Frontend React Application           | 3 weeks  | Sprint 1–3         |
| **Phase 5**  | Integration & End-to-End Pipeline    | 1 week   | Sprint 4           |
| **Phase 6**  | Quality, Security & Hardening        | 1 week   | Sprint 4–5         |
| **Phase 7**  | Deployment & DevOps                  | 2 weeks  | Sprint 4–5         |
| **Phase 8**  | Testing & QA                         | 1 week   | Sprint 5           |
| **Phase 9**  | Documentation                        | Ongoing  | All sprints        |
| **Phase 10** | Release & Post-Launch                | 1 week   | Sprint 5           |

---

## 5. Phase 1 — Project Foundation & Environment Setup

**Duration:** Week 1  
**Owner:** Tech Lead + DevOps Engineer  
**Goal:** All engineers can clone, run, and contribute to the project from day one.

### 5.1 Repository & Project Structure

- [x] Initialize Git monorepo with `/backend`, `/frontend`, `/deploy`, `/docs`, `/scripts` structure.
- [x] Configure `.gitignore` for Python (`venv`, `__pycache__`, `.env`) and Node (`node_modules`, `dist`).
- [x] Add repository `README.md` with quickstart instructions and architecture diagram link.
- [x] Set up branch protection rules on `main` and `develop`.
- [x] Configure GitHub Actions CI pipeline skeleton (lint + build triggers).

### 5.2 Backend Environment

- [x] Initialize Python 3.11 project with `pyproject.toml` (or `setup.py`).
- [x] Create `requirements.txt` with all pinned dependencies (FastAPI, LangGraph, Playwright, Celery, etc.).
- [x] Create `requirements-dev.txt` with dev dependencies (pytest, mypy, ruff, httpx test client).
- [x] Set up virtual environment instructions in `README.md`.
- [x] Create `.env.example` with all required environment variable keys (no values).
- [x] Configure `ruff` for Python linting and `mypy` for type checking.
- [x] Initialize `app/` package with `main.py`, `config.py`, `models/`, `api/`, `agents/`, `tasks/`, `utils/` directories.

### 5.3 Frontend Environment

- [x] Initialize React + Vite + TypeScript project: `npm create vite@latest frontend -- --template react-ts`.
- [x] Install and configure Tailwind CSS + PostCSS.
- [x] Install and initialize `shadcn/ui` component library.
- [x] Install core dependencies: Zustand, Axios, Monaco Editor, react-markdown, Lucide Icons.
- [x] Configure ESLint + Prettier for TypeScript.
- [x] Create `.env.example` for frontend environment variables.
- [x] Set up `src/` directory structure (`components/`, `hooks/`, `store/`, `api/`, `types/`, `utils/`).

### 5.4 Infrastructure Setup

- [x] Install Docker Desktop / Docker Engine + Docker Compose on all developer machines.
- [x] Create base `docker-compose.dev.yml` for local development (Redis + backend + frontend with hot-reload).
- [x] Pull and verify Ollama Cloud endpoint connectivity: `curl ${OLLAMA_BASE_URL}/api/tags`.
- [x] Pull required LLM models (Llama 3.3 70B, Qwen 2.5 72B) to Ollama Cloud instance.
- [x] Verify Playwright Chromium install: `playwright install chromium && playwright install-deps`.
- [ ] Set up shared development Redis instance.

### 5.5 Communication & Tooling

- [ ] Create project board (GitHub Projects or Jira) with Phases and task cards.
- [ ] Set up team communication channel (Slack/Teams) with `#docuagent-dev`, `#docuagent-alerts`.
- [x] Define and document Git commit message convention (Conventional Commits).
- [x] Configure pre-commit hooks: `ruff`, `mypy`, `eslint`, `prettier`.

---

## 6. Phase 2 — Backend Core & LangGraph Agents

**Duration:** Weeks 1–3  
**Owner:** Backend Engineers (×2) + Tech Lead  
**Goal:** All 5 LangGraph agents functional; FastAPI orchestrator receiving and processing requests.

### 6.1 FastAPI Application Core

- [x] Implement `app/main.py` — FastAPI application instance, middleware, exception handlers, CORS configuration.
- [x] Implement `app/config.py` — Pydantic `Settings` class loading all env vars with validation.
- [x] Implement `app/middleware/auth.py` — Bearer token authentication middleware.
- [x] Implement `app/middleware/logging.py` — Structured JSON logging + `SensitiveDataFilter`.
- [x] Implement `app/middleware/rate_limit.py` — `slowapi` rate limiting per endpoint.
- [x] Implement `GET /health` endpoint — service liveness check returning version and timestamp.

### 6.2 Data Models & Schemas

- [x] Define `StepSchema` Pydantic model (index, description, action_type, target_selector, input_value, expected_url, domain_context, selector_hints).
- [x] Define `ChatMessage` Pydantic model (role, content, timestamp).
- [x] Define `ManualState` TypedDict (all fields per specification in DOC-003).
- [x] Define `GenerateRequest` Pydantic model with validators (URL format, script min length).
- [x] Define `ChatRequest` Pydantic model.
- [x] Define `GenerateResponse`, `ChatResponse`, `JobStatusResponse` response models.
- [x] Define `ErrorResponse` standardized error schema.

### 6.3 LangGraph State Machine Setup

- [x] Install and configure LangGraph + LangChain Core + langchain-ollama.
- [x] Implement `app/graph/state.py` — `ManualState` TypedDict with all fields.
- [ ] Implement `app/graph/graph.py` — `StateGraph` initialization, node registration, edge definitions.
- [x] Implement `route_after_quality_review()` conditional edge function.
- [x] Configure `MemorySaver` checkpointer for development.
- [x] Configure `RedisCheckpointer` for production.
- [ ] Implement HITL `interrupt_before=["chat_refiner_node"]` configuration.
- [ ] Write unit tests for graph topology (verify node connections and conditional routing).

### 6.4 Agent 1 — Script & Domain Analyzer

- [x] Implement `app/agents/analyzer.py` — `analyze_script_node` function.
- [x] Implement `ChatOllama` client initialization with Qwen 2.5 72B.
- [x] Write Script Analyzer system prompt (per DOC-003 §12.1).
- [x] Implement Pydantic output parser for `list[StepSchema]` JSON response.
- [x] Implement retry logic (max 2 retries) for JSON parsing failures.
- [x] Implement domain context detection from script text.
- [ ] Test with sample scripts across 5 different domains (E-commerce, CRM, Admin Portal, Finance, SaaS).

### 6.5 Agent 2 — Playwright Visual Capturer (Orchestration Node)

- [ ] Implement `app/agents/capture_agent.py` — `capture_screenshots_node` function.
- [ ] Connect state machine to `PlaywrightCaptureEngine` context manager (Phase 3).
- [ ] Implement sequential iteration over `structured_steps` mapping actions to browser execution.
- [ ] Populate `screenshot_assets` mapping (`{step_index: asset_path}`) in `ManualState`.
- [ ] Implement credential scrubbing: wipe `state["credentials"] = {}` immediately after authentication.
- [ ] Implement fault isolation registering errors in `error_states` without aborting pipeline.

### 6.6 Agent 3 — Technical Writer & Layout Agent

- [x] Implement `app/agents/writer.py` — `compile_markdown_node` function.
- [x] Implement `ChatOllama` client initialization with Llama 3.3 70B.
- [x] Write Technical Writer system prompt (per DOC-003 §12.2) with domain-specific tone modes.
- [x] Implement Markdown template assembly (Prerequisites, Overview, Step sections, Troubleshooting).
- [x] Implement screenshot asset injection into Markdown image references.
- [x] Implement `quality_feedback` application when document is being re-compiled after QA rejection.
- [ ] Test output quality across 3 domain types.

### 6.7 Agent 4 — Quality & Verification Agent

- [x] Implement `app/agents/reviewer.py` — `quality_review_node` function.
- [x] Implement quality review checklist evaluation prompt (step completeness, screenshot coverage, tone consistency, logical flow).
- [x] Implement `quality_approved` flag setting and `quality_feedback` note generation on rejection.
- [x] Implement retry counter with max 3 retries before force-approval.
- [ ] Test rejection/retry cycle with intentionally poor Markdown input.

### 6.8 Agent 5 — Conversational Refiner Agent

- [x] Implement `app/agents/refiner.py` — `chat_refiner_node` function.
- [x] Implement edit classification logic (text edit / structural edit / re-capture trigger).
- [x] Implement `update_specific_section()` — Markdown section-level surgical update utility.
- [x] Implement re-capture trigger response (set `recapture_step_index` in response when applicable).
- [x] Write Conversational Refiner system prompt (per DOC-003 §12.3).
- [ ] Test 10 different natural language edit request types.

### 6.9 Task Queue (Celery + Redis)

- [ ] Implement `app/tasks/celery_app.py` — Celery application instance with Redis broker/backend.
- [ ] Implement `app/tasks/generate_manual.py` — `generate_manual` Celery task wrapping LangGraph execution.
- [ ] Implement `app/tasks/recapture_step.py` — `recapture_step` Celery task.
- [ ] Implement `app/tasks/export_document.py` — `export_document` Celery task (WeasyPrint, Pandoc).
- [ ] Implement `app/tasks/cleanup.py` — `cleanup_expired_jobs` periodic task with Celery Beat.
- [ ] Configure task routing (generation, capture, export queues).

### 6.10 API Endpoints — Generation & Job Management

- [x] Implement `POST /api/v1/generate` — validate request, enqueue Celery task, return `job_id` + `session_id`.
- [x] Implement `GET /api/v1/jobs/{job_id}` — job status poll endpoint.
- [x] Implement `DELETE /api/v1/jobs/{job_id}` — job cancellation + asset cleanup.
- [x] Implement `POST /api/v1/jobs/{job_id}/assets/{step_index}` — screenshot upload replacement.
- [x] Implement `POST /api/v1/recapture/{job_id}/{step_index}` — single step re-capture trigger.

### 6.11 API Endpoints — Streaming & Chat

- [ ] Implement `GET /api/v1/stream/{job_id}` — SSE endpoint with Redis PubSub event relay.
- [ ] Implement SSE event publisher in LangGraph agent callbacks.
- [ ] Implement `POST /api/v1/chat/{session_id}` — REST chat endpoint (fallback for non-WS clients).
- [ ] Implement `WS /api/v1/ws/chat/{session_id}` — WebSocket chat endpoint with heartbeat handling.

### 6.12 Export Engine

- [ ] Implement `app/utils/export.py` — Markdown → HTML via Pandoc.
- [ ] Implement Markdown → PDF via WeasyPrint with custom CSS stylesheet.
- [ ] Implement base64 screenshot embedding for standalone HTML export.
- [ ] Implement `GET /api/v1/export/{job_id}?format={format}` endpoint.
- [ ] Test PDF output quality with embedded images across 3 document sizes.

---

## 7. Phase 3 — Playwright Browser Automation Engine (Agent 2 Core Subsystem)

**Duration:** Weeks 2–4  
**Owner:** Backend Engineer (Playwright specialist)  
**Goal:** Fully functional browser automation engine with highlight injection, fallback handling, and all action types implemented.

### 7.1 Core Engine

- [ ] Implement `app/playwright/engine.py` — `PlaywrightCaptureEngine` class with `async with` context manager.
- [ ] Implement Chromium browser initialization with all required launch arguments.
- [ ] Implement `BrowserContext` creation with viewport, locale, timezone, and `ignore_https_errors=True`.
- [ ] Implement engine configuration loading from environment variables.

### 7.2 Authentication Methods

- [ ] Implement `authenticate()` — form-based username/password login with fallback selector chain.
- [ ] Implement `inject_session()` — browser localStorage/sessionStorage token injection.
- [ ] Implement credential scrubbing: `state["credentials"] = {}` immediately after authentication.
- [ ] Test authentication against 3 different login form patterns (standard, email-only, SSO redirect).

### 7.3 Action Dispatcher

- [ ] Implement `execute_action()` — main dispatcher mapping `action_type` to handler.
- [ ] Implement `_action_navigate()` — `page.goto()` with `networkidle` wait state.
- [ ] Implement `_action_click()` — element location + `scroll_into_view_if_needed()` + click + wait.
- [ ] Implement `_action_type()` — input clear + `type()` with 50ms human-like delay.
- [ ] Implement `_action_scroll()` — `scrollIntoView` JavaScript evaluation.
- [ ] Implement `_action_wait()` — configurable `page.wait_for_timeout()`.
- [ ] Implement `_action_authenticate()` — delegation to `authenticate()` method.

### 7.4 Element Location & Selector Chain

- [ ] Implement `_locate_element()` — primary selector + `selector_hints` fallback chain.
- [ ] Implement 10-second per-selector timeout with `page.wait_for_selector()`.
- [ ] Implement `ElementNotFoundError` custom exception.
- [ ] Test fallback chain resolution against 5 different UI element types.

### 7.5 Dynamic Highlight Engine

- [ ] Implement `highlight_element()` — CSS outline injection via `page.evaluate()`.
- [ ] Implement existing highlight cleanup before new injection.
- [ ] Implement `scrollIntoView` to center viewport.
- [ ] Implement `4px solid #06b6d4` cyan outline style.
- [ ] Implement `0 0 0 8px rgba(6,182,212,0.2)` glow box-shadow.
- [ ] Implement `rgba(0,0,0,0.15)` semi-transparent overlay on body.
- [ ] Implement `cleanup_highlights()` — remove all injected styles and overlays after capture.
- [ ] Visually verify highlight on 10 different element types (button, input, link, dropdown, table row, modal, sidebar item, tab, checkbox, card).

### 7.6 Screenshot Capture

- [ ] Implement `capture_screenshot()` — `page.screenshot()` with PNG format, `animations="disabled"`.
- [ ] Implement screenshot output directory creation (`/assets/{job_id}/`).
- [ ] Implement `step_{index:03d}.png` naming convention.
- [ ] Implement fallback screenshot naming: `step_{index:03d}_fallback.png`.
- [ ] Verify screenshots at 1440×900 viewport resolution.

### 7.7 Fallback Strategy

- [ ] Implement selector failure detection and fallback screenshot capture.
- [ ] Implement `error_states[step_index]` error message registration.
- [ ] Implement pipeline continuation after individual step failure (no abort).
- [ ] Implement anti-bot detection heuristic (CAPTCHA page title/URL pattern check).
- [ ] Implement full pipeline text-only fallback (all steps produce `[Insert Screenshot Here]` placeholders).

### 7.8 SSRF Protection

- [ ] Implement `validate_target_url()` — private IP range blocking (10.x, 172.16.x, 192.168.x, 127.x, 169.254.x, ::1).
- [ ] Implement scheme validation (HTTP/HTTPS only — reject `file://`, `ftp://`, `javascript:`).
- [ ] Implement Playwright route interceptor to abort requests to private IPs mid-session.
- [ ] Test SSRF protection with 10 different malicious URL patterns.

### 7.9 Integration with Agent 2

- [ ] Implement `app/agents/capture_agent.py` — `capture_screenshots_node` LangGraph node.
- [ ] Implement iteration over `structured_steps` with per-step action → highlight → capture sequence.
- [ ] Implement `screenshot_assets` dict population in state.
- [ ] Implement credential scrub immediately after authentication.

---

## 8. Phase 4 — Frontend React Application

**Duration:** Weeks 1–4 (parallel with backend)  
**Owner:** Frontend Engineer  
**Goal:** Complete React SPA with all screens, real-time streaming, chat interface, and export functionality.

### 8.1 Application Shell & Layout

- [ ] Implement `AppShell.tsx` — root layout with sidebar + main content area.
- [ ] Implement `Sidebar.tsx` — navigation links, project branding, status indicators.
- [ ] Configure Tailwind dark mode (`class` strategy) and base theme tokens.
- [ ] Implement responsive breakpoints (desktop-first, minimum 768px).
- [ ] Implement global error boundary component.

### 8.2 Script Input Form

- [ ] Implement `ScriptInputForm.tsx` — textarea for workflow script (min 10 chars), URL input, credential fields.
- [ ] Implement credential field type (`password`) with no autocomplete attribute.
- [ ] Implement `OptionsPanel.tsx` — checkboxes for output format selection, language dropdown.
- [ ] Implement form validation (required fields, URL format check, script minimum length).
- [ ] Implement credential state clearing after form submission (React state, not store).
- [ ] Implement "Generate Manual" button loading state while job is in progress.

### 8.3 Zustand State Store

- [ ] Implement `useManualStore.ts` with full schema (jobId, sessionId, jobStatus, markdownContent, stepStatuses, chatHistory, isChatLoading, exportFormats).
- [ ] Implement all action creators (setJobId, setSessionId, setJobStatus, setMarkdownContent, updateStepStatus, addChatMessage, setChatLoading, reset).
- [ ] Write unit tests for all store actions and state transitions.

### 8.4 Split-Screen Editor

- [ ] Implement `SplitScreen.tsx` — resizable two-pane layout with drag handle.
- [ ] Implement `EditorPane.tsx` — Monaco Editor wrapper (markdown language, vs-dark theme, wordWrap on, minimap off, automaticLayout on).
- [ ] Implement two-way binding: Monaco `value` ← Zustand `markdownContent`; `onChange` → `setMarkdownContent`.
- [ ] Implement diff-aware external update (restore cursor position after SSE-driven content change).
- [ ] Implement `PreviewPane.tsx` — `react-markdown` with `remark-gfm` plugin and custom image renderer.
- [ ] Implement custom image renderer wrapping screenshots in `ScreenshotImage` component.
- [ ] Implement `ScreenshotImage.tsx` — click overlay with "Re-Capture" and "Upload Replacement" actions.

### 8.5 Progress Tracking UI

- [ ] Implement `ProgressBar.tsx` — animated progress bar driven by `jobStatus` and `stepStatuses`.
- [ ] Implement `StepStatus.tsx` — per-step status badge (pending → captured → fallback/error) with color coding.
- [ ] Implement pipeline stage labels (Analyzing → Capturing → Compiling → Reviewing → Ready).
- [ ] Implement spinner/loading overlay during generation.

### 8.6 Chat Panel

- [ ] Implement `ChatPanel.tsx` — collapsible side panel, message list with auto-scroll to bottom.
- [ ] Implement `ChatMessage.tsx` — user/assistant message bubbles with role-based styling.
- [ ] Implement `ChatInput.tsx` — multi-line textarea with Send button; submit on Enter (Shift+Enter for newline).
- [ ] Implement "Agent is thinking..." animated placeholder while `isChatLoading` is true.
- [ ] Implement chat history persistence in Zustand store across refinement turns.

### 8.7 API Client Layer

- [ ] Implement `src/api/client.ts` — Axios instance with baseURL, timeout, Authorization header.
- [ ] Implement `generateManual()` — POST /api/v1/generate.
- [ ] Implement `sendChatMessage()` — POST /api/v1/chat/{session_id}.
- [ ] Implement `triggerRecapture()` — POST /api/v1/recapture/{job_id}/{step_index}.
- [ ] Implement `getJobStatus()` — GET /api/v1/jobs/{job_id}.
- [ ] Implement `downloadExport()` — GET /api/v1/export/{job_id}?format= with blob response.
- [ ] Implement `uploadReplacementScreenshot()` — POST multipart/form-data.
- [ ] Implement Axios response interceptor for standardized error handling and user-facing error toasts.

### 8.8 SSE Stream Consumer Hook

- [ ] Implement `useSSEStream.ts` — `EventSource` connection lifecycle tied to `jobId`.
- [ ] Implement all SSE event type handlers (pipeline_started, script_analyzed, capture_progress, draft_compiled, quality_approved, document_ready, document_updated, job_failed).
- [ ] Implement SSE connection cleanup on component unmount.
- [ ] Implement SSE reconnection on error (max 3 attempts with 2s backoff).

### 8.9 WebSocket Chat Hook

- [ ] Implement `useWebSocket.ts` — `WebSocket` connection lifecycle tied to `sessionId`.
- [ ] Implement `sendMessage()` function (enqueue to store + send over WS).
- [ ] Implement 30-second ping/pong heartbeat.
- [ ] Implement WebSocket reconnection on drop.
- [ ] Implement message handler for `agent_response`, `recapture_started`, `recapture_complete`, `error` types.

### 8.10 Export Bar

- [ ] Implement `ExportBar.tsx` — three download buttons (Markdown `.md`, HTML `.html`, PDF `.pdf`).
- [ ] Implement download buttons disabled until `jobStatus === "completed"` or `"awaiting_input"`.
- [ ] Implement `useExport.ts` hook — Blob download via object URL.
- [ ] Implement download progress indicator (spinner on button while fetch in progress).

### 8.11 Error States & Notifications

- [ ] Implement toast notification system (shadcn/ui Toast).
- [ ] Implement error toasts for API failures, SSE disconnections, and job failures.
- [ ] Implement fallback UI when `job_failed` SSE event received (show error message + retry button).

---

## 9. Phase 5 — Integration & End-to-End Pipeline

**Duration:** Week 4  
**Owner:** Tech Lead + All Engineers  
**Goal:** Full pipeline runs end-to-end from script submission to document export with no manual intervention.

### 9.1 Frontend–Backend Integration

- [ ] Connect `ScriptInputForm` submit to `generateManual()` API call → store job_id + session_id.
- [ ] Connect `useSSEStream` hook to auto-start after successful job submission.
- [ ] Verify SSE events propagate correctly to Zustand store and trigger UI updates.
- [ ] Connect `document_ready` SSE event to Monaco Editor content population.
- [ ] Connect `ChatPanel` to `useWebSocket` hook using stored `sessionId`.
- [ ] Verify `document_updated` SSE events after chat refinement update editor content.

### 9.2 Agent Pipeline Integration

- [ ] Verify end-to-end flow: script → Agent 1 → Agent 2 (Playwright) → Agent 3 → Agent 4 → HITL.
- [ ] Verify SSE events are published at each pipeline stage transition.
- [ ] Verify Agent 5 triggered by chat message via WebSocket → state update → SSE `document_updated`.
- [ ] Verify quality rejection loop: Agent 4 rejects → Agent 3 re-compiles → Agent 4 approves.
- [ ] Verify force-approval after 3 consecutive quality rejections.

### 9.3 Credential Flow Verification

- [ ] Confirm credentials reach Playwright engine correctly.
- [ ] Confirm credentials are scrubbed from `ManualState` before first checkpoint.
- [ ] Confirm credentials never appear in any log output.
- [ ] Confirm credentials are never present in Redis state dump.

### 9.4 Screenshot Asset Flow

- [ ] Verify screenshots saved to correct `/assets/{job_id}/step_{index:03d}.png` paths.
- [ ] Verify `screenshot_assets` dict populated correctly in state.
- [ ] Verify Markdown output references correct relative image paths.
- [ ] Verify screenshot assets served correctly via Nginx `/assets/` location.
- [ ] Verify manual screenshot replacement upload → preview refresh flow.

### 9.5 Export Flow

- [ ] Verify Markdown export downloads correct content.
- [ ] Verify HTML export embeds all screenshots as base64 inline images.
- [ ] Verify PDF export renders all steps with screenshots, formatting, and callout boxes.
- [ ] Test exports on documents of 5, 15, and 30 steps.

---

## 10. Phase 6 — Quality, Security & Hardening

**Duration:** Week 4–5  
**Owner:** Tech Lead + DevOps Engineer  
**Goal:** System passes all security requirements and NFR targets.

### 10.1 Security Implementation

- [ ] Enable `SensitiveDataFilter` on all Python log handlers.
- [ ] Implement SSRF protection (`validate_target_url()`) on all URL inputs.
- [ ] Implement Playwright route interceptor blocking internal IP ranges.
- [ ] Implement Redis `requirepass` authentication in all environments.
- [ ] Implement job ownership validation on all job/session endpoints.
- [ ] Implement TLS 1.2+ enforcement in Nginx configuration.
- [ ] Add security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options).
- [ ] Run `pip audit` and `npm audit`; resolve all HIGH/CRITICAL findings.
- [ ] Run OWASP ZAP baseline scan against staging deployment.

### 10.2 Performance Tuning

- [ ] Profile LLM inference latency (target ≤ 30s per agent call); adjust `temperature` and `timeout`.
- [ ] Profile Playwright per-step capture latency (target ≤ 12s/step); tune selector timeouts.
- [ ] Profile PDF export latency (target ≤ 15s); optimize WeasyPrint CSS.
- [ ] Implement Monaco Editor lazy loading to improve frontend TTI.
- [ ] Implement SSE event debouncing on frontend to prevent rapid re-render thrashing.
- [ ] Verify API p95 latency for `/generate` acceptance ≤ 500ms under 10 concurrent requests.

### 10.3 Error Handling & Resilience

- [ ] Implement Celery task `autoretry_for=(ConnectionError, TimeoutError)` with exponential backoff.
- [ ] Implement LLM API retry decorator (max 3 retries, exponential backoff).
- [ ] Implement Playwright `ElementNotFoundError` catch → fallback screenshot → pipeline continuation.
- [ ] Implement `quality_retry_count` guard preventing infinite quality review loops.
- [ ] Test all failure injection scenarios from DOC-009 §5.1 fault tolerance table.
- [ ] Verify graceful degradation: complete text-only manual generated when all captures fail.

### 10.4 Code Quality

- [ ] Achieve ≥ 80% Python unit test coverage (pytest with coverage report).
- [ ] Achieve ≥ 70% TypeScript component test coverage (Vitest + React Testing Library).
- [ ] Pass mypy strict type checking with zero errors.
- [ ] Pass ruff linting with zero errors.
- [ ] Pass ESLint + TypeScript strict mode with zero errors.

---

## 11. Phase 7 — Deployment & DevOps

**Duration:** Weeks 4–5 (parallel with Phase 6)  
**Owner:** DevOps Engineer  
**Goal:** Production-ready Docker Compose deployment with monitoring, alerting, and CI/CD.

### 11.1 Dockerfiles

- [ ] Write `backend/Dockerfile` — Python 3.11 slim base, venv, Playwright deps, app copy, Gunicorn CMD.
- [ ] Write `backend/Dockerfile.worker` — same base as backend, Celery worker CMD.
- [ ] Write `frontend/Dockerfile` — Node 20 builder stage → Nginx alpine serving stage.
- [ ] Verify all Docker images build without errors.
- [ ] Verify Docker image sizes are within acceptable bounds (backend < 2GB with Playwright, frontend < 50MB).

### 11.2 Docker Compose Production

- [ ] Write `docker-compose.yml` (production) with all services (redis, backend, worker, flower, frontend, nginx).
- [ ] Configure named volumes (redis_data, screenshot_assets, export_files, frontend_dist).
- [ ] Configure internal Docker network (no public exposure except Nginx ports 80/443).
- [ ] Configure `depends_on` with health check conditions.
- [ ] Configure `restart: always` on all services.
- [ ] Configure `security_opt: no-new-privileges:true` on all services.
- [ ] Test `docker compose up -d` brings all services healthy.

### 11.3 Nginx Configuration

- [ ] Write production `nginx.conf` with HTTP→HTTPS redirect, TLS configuration, upstream proxies.
- [ ] Configure SSE location block with `proxy_buffering off` and 600s `proxy_read_timeout`.
- [ ] Configure WebSocket location block with `Upgrade` and `Connection` headers.
- [ ] Configure `/assets/` static serving with 1-hour cache headers.
- [ ] Configure Celery Flower proxy with `auth_basic` protection.
- [ ] Configure rate limiting zones.
- [ ] Configure security headers on all responses.
- [ ] Test with SSL Labs to achieve A+ rating.

### 11.4 CI/CD Pipeline

- [ ] Implement GitHub Actions workflow: `.github/workflows/ci.yml`.
  - Trigger: push to `develop` or `main`, PRs to `develop`.
  - Jobs: lint (ruff, mypy, eslint) → unit tests → build Docker images → push to registry (on `main` only).
- [ ] Implement `.github/workflows/deploy.yml`.
  - Trigger: push to `main` after CI passes.
  - Jobs: SSH to server → `docker compose pull` → `docker compose up -d` → health check verification.
- [ ] Configure GitHub Secrets for: `DOCKER_REGISTRY_TOKEN`, `SSH_DEPLOY_KEY`, `SERVER_HOST`, `OLLAMA_BASE_URL`, `API_TOKEN`.

### 11.5 Monitoring & Observability

- [ ] Integrate `prometheus-fastapi-instrumentator` into FastAPI app for metrics endpoint `/metrics`.
- [ ] Deploy Prometheus + Grafana (as additional Docker Compose services in `docker-compose.monitoring.yml`).
- [ ] Create Grafana dashboards: API latency, job success rate, Celery queue depth, Redis memory.
- [ ] Configure Prometheus alert rules (per NFR §9.4 alerting table).
- [ ] Configure alert notification channel (email/Slack webhook).
- [ ] Configure Celery Flower for task monitoring at `/flower/`.

### 11.6 Backup Automation

- [ ] Write daily Redis backup cron script → copy `dump.rdb` to `/backups/`.
- [ ] Write 6-hourly screenshot asset rsync cron script → S3 or NFS.
- [ ] Test backup restore procedure.
- [ ] Document recovery runbooks for each P0 failure scenario.

---

## 12. Phase 8 — Testing & QA

**Duration:** Week 5  
**Owner:** QA Engineer + All Engineers  
**Goal:** System passes all functional, performance, and security test suites.

### 12.1 Unit Tests

- [ ] Agent 1 unit tests: parse 10 different script styles; verify `StepSchema` output.
- [ ] Agent 3 unit tests: verify Markdown structure (Prerequisites, Overview, Steps, Troubleshooting).
- [ ] Agent 4 unit tests: verify approval logic and feedback generation.
- [ ] Agent 5 unit tests: verify selective section update for 10 different edit request types.
- [ ] Playwright engine unit tests: mock `page` object, verify all action types and highlight injection.
- [ ] URL validator unit tests: 10 valid URLs pass; 10 malicious URLs blocked.
- [ ] Export utility tests: verify Markdown, HTML, and PDF output format correctness.
- [ ] FastAPI endpoint unit tests: all endpoints with valid and invalid inputs.

### 12.2 Integration Tests

- [ ] Full LangGraph pipeline integration test (mock Ollama responses + mock Playwright).
- [ ] SSE stream integration test: verify all event types emitted in correct order.
- [ ] WebSocket chat integration test: message → agent response → state update cycle.
- [ ] Redis checkpointer integration test: save state → retrieve state → verify field equality.
- [ ] Celery task integration test: enqueue → execute → verify result.
- [ ] Export pipeline integration test: complete Markdown → HTML → PDF conversion.

### 12.3 End-to-End Tests (Playwright — UI Testing)

- [ ] E2E Test 1: Submit 5-step script → verify progress SSE events → verify document in editor.
- [ ] E2E Test 2: Submit job with invalid URL → verify error toast displayed.
- [ ] E2E Test 3: Send chat message "translate to French" → verify editor content updated.
- [ ] E2E Test 4: Click "Re-Capture" on step 2 image → verify SSE recapture events → verify new image.
- [ ] E2E Test 5: Upload replacement screenshot → verify preview updates without page reload.
- [ ] E2E Test 6: Export as PDF → verify file downloads with correct filename.
- [ ] E2E Test 7: 25-step workflow → verify all steps have content and screenshots or placeholders.
- [ ] E2E Test 8: Simulate Playwright selector failure → verify fallback placeholder in document.

### 12.4 Performance Tests

- [ ] Load test: 5 concurrent 10-step generation jobs → verify all complete within 5 minutes.
- [ ] API stress test: 100 concurrent `/health` + `/jobs` poll requests → verify p95 ≤ 200ms.
- [ ] Chat latency test: 20 concurrent chat sessions → verify median response ≤ 10 seconds.
- [ ] Frontend load test: measure LCP, TTI with Lighthouse; verify LCP ≤ 2.5s, TTI ≤ 3.5s.

### 12.5 Security Tests

- [ ] Penetration test: attempt unauthenticated API access → verify 401 on all endpoints.
- [ ] Penetration test: attempt cross-job data access with different token → verify 403.
- [ ] SSRF test: submit private IP target URL → verify request blocked before Playwright launch.
- [ ] Log audit: generate manual with known credentials → grep logs for credential string → verify zero occurrences.
- [ ] Rate limit test: exceed 10 req/s rate limit → verify 429 responses.
- [ ] XSS test: submit script with HTML injection → verify sanitized output in preview.

---

## 13. Phase 9 — Documentation & Knowledge Transfer

**Duration:** Ongoing throughout all sprints  
**Owner:** All Engineers (primary owners per domain)  
**Goal:** Complete, accurate, and reviewed technical documentation suite.

- [ ] Review all 10 documents in `/docs/` for accuracy against final implementation.
- [ ] Update `04_api_reference.md` with any endpoint changes discovered during development.
- [ ] Update `02_architecture_design.md` with any ADR changes made during development.
- [ ] Write developer `CONTRIBUTING.md` with branch strategy, commit conventions, and code review guidelines.
- [ ] Write operational `RUNBOOK.md` for each P0 failure scenario.
- [ ] Record internal demo video of full pipeline (script input → generation → chat refinement → PDF export).
- [ ] Conduct knowledge transfer session with all team members on multi-agent architecture.
- [ ] Conduct knowledge transfer session on Playwright engine and highlight injection.
- [ ] Conduct knowledge transfer session on deployment and monitoring setup.

---

## 14. Phase 10 — Release & Post-Launch

**Duration:** Week 5 (end) + ongoing  
**Owner:** Tech Lead + DevOps Engineer  
**Goal:** Smooth GA release with zero critical bugs and active monitoring.

### 14.1 Pre-Release Checklist

- [ ] All P0 test cases passing.
- [ ] Security hardening checklist (DOC-008 §12) fully completed.
- [ ] Docker Compose production stack verified healthy on target server.
- [ ] SSL Labs A+ rating achieved.
- [ ] Monitoring dashboards and alerts active and verified.
- [ ] Backup and recovery procedure tested.
- [ ] All team members have access to production monitoring.
- [ ] Rollback procedure documented and tested.

### 14.2 Release Process

- [ ] Create release branch: `release/v1.0.0` from `develop`.
- [ ] Bump version numbers: `pyproject.toml`, `package.json`, `docs/README.md`.
- [ ] Run full test suite on release branch.
- [ ] Merge `release/v1.0.0` → `main` (with 2 reviewer approvals).
- [ ] Tag release: `git tag -a v1.0.0 -m "DocuAgent AI v1.0.0 GA"`.
- [ ] CI/CD triggers deployment to production server.
- [ ] Verify production health checks pass within 5 minutes of deployment.
- [ ] Publish GitHub Release with changelog.

### 14.3 Post-Launch Monitoring (First 2 Weeks)

- [ ] Monitor error rate daily (target < 5%).
- [ ] Monitor job success rate daily (target ≥ 95%).
- [ ] Monitor API p95 latency (target ≤ 500ms for synchronous endpoints).
- [ ] Triage any P0 bugs within 24 hours.
- [ ] Collect first-user feedback and create GitHub Issues for v1.1 backlog.
- [ ] Review and prune Redis keys at end of week 2.

---

## 15. Milestone Summary

| Milestone                          | Target Date   | Success Criteria                                               |
| ---------------------------------- | ------------- | -------------------------------------------------------------- |
| **M1: Environment Ready**          | Week 1, Day 5 | All engineers running project locally; CI pipeline green       |
| **M2: Backend Agents Complete**    | Week 3, Day 5 | All 5 LangGraph agents functional; unit tests passing          |
| **M3: Playwright Engine Complete** | Week 3, Day 5 | Full highlight capture working; all fallbacks tested           |
| **M4: Frontend MVP Complete**      | Week 3, Day 5 | All UI screens implemented; SSE and WS hooks functional        |
| **M5: E2E Pipeline Working**       | Week 4, Day 3 | Full flow from submit to PDF export with no manual steps       |
| **M6: Security Hardening**         | Week 4, Day 5 | All security checklist items ✅; OWASP ZAP baseline clean      |
| **M7: Production Deployment**      | Week 5, Day 2 | Docker Compose stack live; monitoring active; CI/CD verified   |
| **M8: QA Complete**                | Week 5, Day 4 | All P0 test cases passing; performance targets met             |
| **M9: v1.0.0 GA Release**          | Week 5, Day 5 | Git tag v1.0.0; production deployment verified; docs published |

---

## 16. Risk Register

| #   | Risk                                                                 | Likelihood | Impact | Mitigation                                                                        |
| --- | -------------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------- |
| R1  | Ollama Cloud latency exceeds 120s timeout for 70B models             | Medium     | High   | Pre-test inference latency; use Qwen 2.5 72B as faster fallback; increase timeout |
| R2  | Target staging app uses heavy anti-bot detection blocking Playwright | High       | Medium | Implement graceful text-only fallback; document limitation clearly                |
| R3  | LLM JSON output parsing failures causing agent retry loops           | Medium     | Medium | Strict Pydantic output parsers with explicit retry prompts                        |
| R4  | Redis memory exhaustion under load                                   | Low        | High   | Configure `maxmemory` with `allkeys-lru`; monitor closely                         |
| R5  | Playwright Chromium memory leak in long-running worker               | Medium     | Medium | Implement periodic worker restart (Celery `--max-tasks-per-child=50`)             |
| R6  | WeasyPrint PDF rendering issues with complex layouts                 | Medium     | Low    | Test early with sample documents; fallback to Pandoc HTML                         |
| R7  | Frontend SSE connection drops in corporate proxy environments        | Medium     | Medium | Implement SSE reconnection logic; offer polling fallback                          |
| R8  | Scope creep extending development beyond Week 10                     | Medium     | High   | Strict backlog management; defer v1.1 features explicitly                         |
| R9  | SSL certificate provisioning delay for production domain             | Low        | High   | Provision certificate in Week 4; use Let's Encrypt with auto-renewal              |
| R10 | Team member unavailability during critical sprint                    | Low        | High   | Document all implementation decisions; pair programming for critical paths        |

---

## 17. Dependencies Map

```
Phase 1 (Foundation)
    │
    ├──► Phase 2 (Backend) ──► Phase 5 (Integration)
    │         │                       │
    │         └──► Phase 3 (Browser)──┘
    │
    ├──► Phase 4 (Frontend) ──► Phase 5 (Integration)
    │
    └──► Phase 7 (DevOps) ──► Phase 5 (Integration)
                │
                └──► Phase 10 (Release)

Phase 5 (Integration)
    │
    ├──► Phase 6 (Security & Quality)
    ├──► Phase 8 (Testing & QA)
    └──► Phase 9 (Documentation review)
              │
              └──► Phase 10 (Release)
```

**External Dependencies:**

| Dependency                                     | Blocking Phase   | Mitigation if Unavailable                           |
| ---------------------------------------------- | ---------------- | --------------------------------------------------- |
| Ollama Cloud endpoint access                   | Phase 2 (Week 1) | Use local Ollama with smaller models (Llama 3.2 8B) |
| Staging application URL for Playwright testing | Phase 3 (Week 2) | Use internal demo app (e.g., TodoMVC, Juice Shop)   |
| Production server provisioning                 | Phase 7 (Week 4) | Use local Docker Compose as fallback                |
| SSL certificate for production domain          | Phase 7 (Week 5) | Use self-signed for pre-release testing             |

---

## 18. Definition of Done

A feature, task, or phase is **Done** when:

- [ ] All acceptance criteria for the task are met.
- [ ] Code is peer-reviewed and approved by ≥ 1 reviewer (≥ 2 for main branch merges).
- [ ] Unit tests written and passing (coverage contribution maintained at ≥ 80% backend, ≥ 70% frontend).
- [ ] Linting and type checking passing with zero errors.
- [ ] No new `HIGH` or `CRITICAL` vulnerabilities introduced (verified by `pip audit` / `npm audit`).
- [ ] Relevant documentation updated (API reference, architecture docs, README).
- [ ] CI/CD pipeline green on the feature branch.
- [ ] Acceptance tested on the local development environment (Docker Compose).
- [ ] Any security-sensitive changes reviewed by Tech Lead.

---

_Document ID: PLAN-001 · Version: 1.0.0 · DocuAgent AI Development Plan_  
_See companion document: [Master Checklist & TODO](./CHECKLIST_TODO.md)_
