# SYSTEM REQUIREMENTS SPECIFICATION & ARCHITECTURE PROPOSAL

## PROJECT TITLE
**AI-Powered Dynamic User Manual Generator (DocuAgent AI)**  
*Autonomous Multi-Agent Systems, Browser Automation, and Conversational Document Refinement*

---

## 1. EXECUTIVE SUMMARY & PROJECT OVERVIEW

### 1.1 Executive Summary
Modern enterprise applications, SaaS platforms, and software ecosystems evolve rapidly. Traditional technical documentation methods struggle to maintain pace with continuous deployment schedules. Manual creation of user manuals—involving step-by-step drafting, manual screenshot capture, annotations, formatting, and proofreading—is labor-intensive, error-prone, and prone to obsolescence.

The **AI-Powered Dynamic User Manual Generator (DocuAgent AI)** provides an end-to-end, autonomous solution that converts raw, unstructured textual scripts or user workflows into professional, publication-ready user manuals with automatic UI screenshots and visual highlights.

Leveraging a **Multi-Agent Architecture using LangGraph**, **Ollama Cloud LLM Inference**, and **Playwright Browser Automation**, the system interprets dynamic workflows, executes them in real time within live web environments, captures annotated screenshots, formats comprehensive step-by-step technical guides, and provides an interactive conversational interface for human-in-the-loop document editing.

### 1.2 Core Value Proposition
* **Non-Rule-Based Dynamic Adaptation:** Eliminates rigid templates by using LLMs to infer target audience, context, application domains, and UI workflows dynamically.
* **Automated Visual Capture:** Replaces manual screenshotting with an autonomous Playwright engine capable of navigating dynamic DOM elements and applying real-time visual highlight borders around targeted UI elements.
* **Conversational Document Refinement:** Integrates a state-aware chatbot (LangGraph Human-in-the-Loop) allowing users to modify, translate, or expand specific document nodes without regenerating the entire manual.
* **Enterprise Security & Privacy:** Operates with Ollama Cloud endpoints, ensuring data isolation and secure handling of staging credentials.

---

## 2. SYSTEM GOALS & OBJECTIVES

### 2.1 Primary Objectives
1. **End-to-End Automation:** Reduce technical documentation creation time by over 80% through automated script parsing, visual capture, and technical writing.
2. **Dynamic & Un-opinionated Generation:** Support diverse software types (SaaS, Admin Dashboards, Enterprise Workflows) without relying on hardcoded rules or static document templates.
3. **High Visual Accuracy:** Ensure every step in the manual features accurate, annotated screenshots pointing directly to the UI elements referenced in the text.
4. **Iterative Human Collaboration:** Enable technical writers and product managers to interactively query and refine generated documentation via natural language.
5. **Multi-Format Exporting:** Produce clean Markdown, standalone HTML, and publication-ready PDF manuals with embedded high-resolution graphics.

---

## 3. HIGH-LEVEL SYSTEM ARCHITECTURE & WORKFLOW

The system employs a decoupled, asynchronous micro-architecture comprising a React Single Page Application (SPA), a FastAPI Orchestration Backend, a LangGraph State Machine, a Playwright Capture Engine, and an Ollama Cloud Inference cluster.

```
+-----------------------------------------------------------------------------------+
|                                 FRONTEND LAYER                                   |
|                  React (Vite) + Tailwind CSS + Monaco Editor                      |
+-----------------------------------------------------------------------------------+
                                          │
                                    REST / SSE / WS
                                          ▼
+-----------------------------------------------------------------------------------+
|                                  BACKEND LAYER                                    |
|                                FastAPI Orchestrator                               |
+-----------------------------------------------------------------------------------+
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
+-----------------------------------+           +-----------------------------------+
|      LANGGRAPH STATE MACHINE      |           |     PLAYWRIGHT CAPTURE ENGINE     |
|  - Script Analyzer Agent          |           |  - Headless Chromium Driver       |
|  - Technical Writer Agent         |◄─────────►|  - DOM Injector & Highlighter     |
|  - Media Specialist Agent         |           |  - Auth & Session Storage         |
|  - Quality / Editor Agent         |           +-----------------------------------+
|  - Conversational Refiner Agent   |                             │
+-----------------------------------+                             │
                  │                                               │
            Ollama Cloud API                                      ▼
                  ▼                             +-----------------------------------+
+-----------------------------------+           |      MEDIA & STORAGE ASSETS       |
|    OLLAMA CLOUD LLM INFERENCE     |           |  - Screenshot Asset Storage       |
|  (Llama 3.3 70B / Qwen 2.5 72B)   |           |  - Export Engine (WeasyPrint)     |
+-----------------------------------+           +-----------------------------------+
```

### 3.1 Architectural Execution Pipeline
1. **Script Analysis Phase:** Raw user input (text, unstructured instructions) is processed to build a structured JSON Directed Acyclic Graph (DAG) of actionable UI steps and DOM selection targets.
2. **Automated Visual Capture Phase:** Playwright executes the generated DAG against target application URLs, injects CSS visual indicators around target selectors, and saves step screenshots.
3. **Content Synthesis Phase:** Technical Writer and Media Agents synthesize raw action details and screenshot metadata into a Markdown document structured with Prerequisites, Walkthroughs, Callout Boxes, and Troubleshooting notes.
4. **Human-in-the-Loop Refinement Phase:** The user inspects the output in a split-screen editor and uses the embedded chat interface to request targeted edits.

---

## 4. MULTI-AGENT ARCHITECTURE (LANGGRAPH STATE MACHINE)

The core processing logic is orchestrated using **LangGraph**, enabling dynamic cyclical loops, state persistence, and interrupt handling.

### 4.1 State Schema Definition
The shared execution state (`ManualState`) maintains system knowledge across agent transfers:
* **Raw Input Script:** Original text provided by the user.
* **Target URL & Credentials:** Staging application endpoints and authentication data.
* **Structured Steps:** Extracted JSON sequence of UI interactions and visual highlight selectors.
* **Screenshot Assets:** Index-mapped file paths to visual assets.
* **Markdown Content:** Current compiled version of the technical document.
* **Chat History & Logs:** Multi-turn dialogue logs for contextual refinement.

### 4.2 Agent Breakdown & Responsibilities

#### Agent 1: Script & Domain Analyzer Agent
* **Role:** Context Extraction & Execution Planning.
* **Functionality:** Parses unstructured text scripts into explicit step JSON schemas. Detects target URLs, input values, button clicks, expected page transitions, and target domain context (e.g., E-commerce, Financial Dashboard, CRM).
* **Output:** Structured step-by-step DAG with selector hints.

#### Agent 2: Playwright Visual Capturer Agent
* **Role:** Live Application Execution & Image Collection.
* **Functionality:** Calls the browser automation engine. Executes browser interactions, injects dynamic styles into target DOM elements (e.g., dynamic bounding boxes), captures screenshots, and maps image file paths to step indexes in state.

#### Agent 3: Technical Writer & Layout Agent
* **Role:** Content Generation & Formatting.
* **Functionality:** Merges structured action steps with screenshot asset tags. Formats instructions into clean Markdown using standard technical writing frameworks (Prerequisites, Step-by-Step Actions, Callouts, Tips).

#### Agent 4: Quality & Verification Agent
* **Role:** Verification & Polish.
* **Functionality:** Reviews generated Markdown for logical flow, missing steps, clarity, tone consistency, and correct image placement. Re-triggers compilation if deficiencies are found.

#### Agent 5: Conversational Refiner Agent
* **Role:** Interactive Human-in-the-Loop Processor.
* **Functionality:** Listens for user prompt inputs in the chat panel (e.g., "Add troubleshooting steps for step 2"). Selectively updates relevant nodes in the state without executing unnecessary full re-runs.

---

## 5. AUTOMATED UI CAPTURE ENGINE

### 5.1 Playwright Integration Architecture
The Visual Capture Engine runs headlessly within the Python backend using Playwright Sync/Async APIs.

### 5.2 Dynamic Highlight Engine
To draw user attention to specific UI elements within manual screenshots, the engine applies real-time DOM modifications prior to capturing snapshots:
* Injects dynamic CSS outlines (`outline: 4px solid #06b6d4`).
* Applies temporary semi-transparent overlays on non-target UI components.
* Auto-scrolls target elements into the center of the viewport (`scrollIntoViewIfNeeded`).

### 5.3 Fallback Strategies
* **Selector Timeout Strategy:** If a target selector fails to resolve within a given timeout, the engine logs a warning, takes a general viewport screenshot, and proceeds without failing the entire pipeline.
* **User Manual Replacement:** Users can click on any generated image in the React editor to re-capture or upload a replacement file manually.

---

## 6. INTERACTIVE CHATBOT INTEGRATION

### 6.1 State-Preserving Chat Architecture
The embedded chatbot uses LangGraph's state persistence layer (`MemorySaver` / Redis Checkpointer). When a user requests an edit:
1. The user query is passed to the **Conversational Refiner Agent** along with current `markdown_content` and `chat_history`.
2. The agent identifies whether the request requires:
   * **Text-Only Edits:** Modifying wording, adding callouts, or translating languages.
   * **Structural Edits:** Re-ordering steps or adding new chapters.
   * **Re-capture Trigger:** Re-running Playwright for specific steps.
3. Only affected sections of the Markdown tree are updated, keeping latency low.

---

## 7. TECHNOLOGY STACK

| Layer | Technology | Justification |
|---|---|---|
| **Frontend Framework** | React (Vite) | High performance, fast HMR, component isolation |
| **Styling** | Tailwind CSS + CSS Modules | Rapid modern design, responsive layouts, dark mode |
| **UI Components** | shadcn/ui + Lucide Icons | Accessible, enterprise-grade styled UI primitives |
| **State Management** | Zustand | Light-weight client state and chat history management |
| **Editor Component** | Monaco Editor / `@uiw/react-md-editor` | Dual-pane syntax highlighted Markdown and live rendering |
| **Backend Framework** | FastAPI (Python 3.11+) | Asynchronous execution, native Pydantic support, high throughput |
| **Agent Orchestration**| LangGraph + LangChain Core | State machine support, cyclic workflows, Human-in-the-Loop |
| **Browser Automation** | Playwright Python SDK | Modern headless browser capture, multi-browser compatibility |
| **LLM Inference Engine**| Ollama Cloud API | Enterprise privacy, cost efficiency, fast local/cloud execution |
| **Primary LLMs** | Llama 3.3 (70B) / Qwen 2.5 (72B) | Exceptional technical writing, instruction following, and JSON generation |
| **Document Exporting** | WeasyPrint + Pandoc | High-fidelity Markdown-to-PDF/HTML rendering with CSS support |

---

## 8. COMPLETE USER JOURNEY & OPERATIONAL WORKFLOW

```
 [User] Input Workflow Script & Staging Credentials
   │
   ▼
 [React UI] Clicks "Generate User Manual"
   │
   ▼
 [FastAPI] Endpoint `/api/v1/generate` receives payload
   │
   ▼
 [LangGraph] `analyze_script_node` creates structured JSON steps
   │
   ▼
 [Playwright] Launches browser, navigates, highlights DOM, captures PNGs
   │
   ▼
 [LangGraph] `compile_markdown_node` drafts rich technical documentation
   │
   ▼
 [React UI] Displays Live Split-Screen: Editor (Left) & Preview (Right)
   │
   ▼
 [User Interface] Conversational Chat Panel for iterative adjustments
   │  └─ "Translate to French" ──► Agent edits Markdown directly
   │  └─ "Re-take step 2 image" ─► Playwright re-captures step 2
   ▼
 [Export Engine] User downloads finalized PDF / HTML / Markdown manual
```

---

## 9. NON-FUNCTIONAL REQUIREMENTS

### 9.1 Scalability & Performance
* **Parallel Execution:** Playwright visual capture sessions run in asynchronous worker pools via Celery/Redis tasks for multi-tenant throughput.
* **Response Streaming:** Chat responses and logs are streamed to the React UI via Server-Sent Events (SSE) for low perceived latency.

### 9.2 Security & Credential Protection
* **Credential Isolation:** Staging passwords provided for browser authentication are held in memory only for the duration of the Playwright execution cycle and scrubbed from state persistence logs.
* **Ollama Cloud Data Privacy:** All API communications with Ollama Cloud endpoints use encrypted TLS channels without storing customer prompts for LLM training.

### 9.3 Reliability & Fault Tolerance
* **Graceful Degradation:** If browser automation fails due to dynamic anti-bot protection or changing UI selectors, the system generates text placeholders (`[Insert Screenshot Here: Description]`) ensuring manual document generation completes uninterrupted.

---

## 10. FUTURE ENHANCEMENT ROADMAP

1. **Multimodal LLM Vision Verification:** Integrate vision-capable LLMs (e.g., LLaVA or Qwen-VL) to automatically review captured screenshots and verify if UI changes match the intended script actions.
2. **Video Manual Generation:** Convert captured Playwright browser actions into animated GIF or MP4 walkthrough clips embedded directly within digital manuals.
3. **Automated Jira / Confluence Integration:** Directly push generated Markdown user manuals to enterprise knowledge bases like Confluence, Notion, or GitBook via REST API webhooks.