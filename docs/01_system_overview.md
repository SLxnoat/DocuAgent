# System Overview

**Document ID:** DOC-001  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** All Stakeholders

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Core Value Proposition](#3-core-value-proposition)
4. [System Goals & Objectives](#4-system-goals--objectives)
5. [High-Level Architecture](#5-high-level-architecture)
6. [Key Capabilities](#6-key-capabilities)
7. [Stakeholder Map](#7-stakeholder-map)
8. [Document Conventions](#8-document-conventions)

---

## 1. Executive Summary

**DocuAgent AI** (AI-Powered Dynamic User Manual Generator) is an autonomous, enterprise-grade documentation platform that converts raw, unstructured workflow scripts into publication-ready user manuals — complete with annotated UI screenshots — with minimal human effort.

The system combines three core technology pillars:

| Pillar | Technology | Purpose |
|--------|-----------|---------|
| **Intelligent Orchestration** | LangGraph Multi-Agent State Machine | Coordinates specialized AI agents through a cyclical, stateful pipeline |
| **LLM Inference** | Ollama Cloud (Llama 3.3 70B / Qwen 2.5 72B) | Generates accurate, context-aware technical content |
| **Browser Automation** | Playwright Python SDK | Executes live UI workflows and captures annotated screenshots |

The result is a fully formatted technical document delivered in **Markdown**, **HTML**, and **PDF** formats, with an embedded conversational interface for iterative human refinement.

---

## 2. Problem Statement

### 2.1 The Documentation Gap in Modern Software

Modern enterprise applications and SaaS platforms operate under continuous deployment schedules where features change weekly or even daily. Traditional documentation processes fail to keep pace with this velocity for the following reasons:

- **Labor Intensity:** Manual documentation requires dedicated technical writers who must operate the application step-by-step, capture screenshots manually, annotate images, and format documents.
- **Error Proneness:** Human-driven processes introduce inconsistencies in terminology, screenshot accuracy, and step sequencing.
- **Rapid Obsolescence:** Published manuals become outdated within weeks of a new release, requiring costly revision cycles.
- **Scalability Limitations:** Growing product lines multiply the documentation burden linearly without additional staffing.

### 2.2 The Cost of the Status Quo

| Metric | Traditional Approach | DocuAgent AI |
|--------|---------------------|-------------|
| Time to produce a 20-step manual | 4–8 hours | < 10 minutes |
| Screenshot annotation effort | Manual per step | Automated |
| Re-documentation after UI change | Full manual revision | Targeted re-capture |
| Multi-format export | Manual conversion | One-click export |

---

## 3. Core Value Proposition

### 3.1 Non-Rule-Based Dynamic Adaptation

DocuAgent AI eliminates rigid templates. Rather than relying on fixed document structures, the system uses large language models (LLMs) to dynamically infer:

- **Target Audience:** End-users, administrators, developers, or executives.
- **Application Domain:** E-commerce, Financial Dashboards, CRM, Admin Portals, SaaS Platforms.
- **Documentation Tone:** Formal technical writing, simplified end-user guides, or developer API documentation.
- **Structural Layout:** Automatically selects appropriate heading hierarchies, callout box placement, and prerequisite sections.

### 3.2 Automated Visual Capture

The integrated Playwright browser engine replaces manual screenshotting entirely:

- Navigates live staging environments using provided credentials.
- Injects dynamic CSS highlight borders (cyan, `4px solid #06b6d4`) around target UI elements.
- Applies semi-transparent overlays to de-emphasize non-target regions.
- Auto-scrolls elements into center viewport before capture.
- Maps each screenshot to its corresponding document step index.

### 3.3 Conversational Document Refinement

Users interact with their generated documentation through a state-aware chat interface:

- Request targeted textual edits without regenerating the entire document.
- Trigger selective re-capture of specific steps when UI has changed.
- Translate the entire document or specific sections into other languages.
- Add, reorder, or remove document sections through natural language commands.

### 3.4 Enterprise Security & Privacy

- Staging credentials are held **in-memory only** for the duration of the Playwright execution session.
- All LLM API communications use **TLS-encrypted channels**.
- Ollama Cloud does not retain customer prompts for model training.
- No sensitive credential data is persisted to state storage or logs.

---

## 4. System Goals & Objectives

### 4.1 Primary Objectives

| # | Objective | Target Metric |
|---|-----------|--------------|
| 1 | **End-to-End Automation** | Reduce documentation creation time by **≥ 80%** |
| 2 | **Dynamic & Un-opinionated Generation** | Support all major software categories without hardcoded rules |
| 3 | **High Visual Accuracy** | Every manual step features an annotated screenshot targeting the correct UI element |
| 4 | **Iterative Human Collaboration** | Allow targeted edits via natural language without full regeneration |
| 5 | **Multi-Format Exporting** | Produce clean Markdown, standalone HTML, and PDF with embedded graphics |

### 4.2 Secondary Objectives

- Provide real-time progress streaming to the frontend via Server-Sent Events (SSE).
- Enable concurrent manual generation for multi-tenant enterprise environments.
- Maintain graceful degradation — text-only output when browser automation encounters obstacles.

---

## 5. High-Level Architecture

DocuAgent AI is structured as a **decoupled, asynchronous micro-architecture** with five principal layers:

```
┌────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                            │
│           React (Vite) + Tailwind CSS + Monaco Editor              │
└──────────────────────────────────┬─────────────────────────────────┘
                                   │  REST / SSE / WebSocket
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER                             │
│                      FastAPI Orchestrator                          │
└──────────────────┬────────────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
┌─────────────────────┐   ┌─────────────────────────────┐
│  LANGGRAPH STATE    │   │   PLAYWRIGHT CAPTURE ENGINE │
│  MACHINE            │◄──►│   Headless Chromium         │
│  (5 AI Agents)      │   │   DOM Injector & Highlighter│
└────────┬────────────┘   └─────────────┬───────────────┘
         │                              │
  Ollama Cloud API                      ▼
         ▼                 ┌────────────────────────────┐
┌─────────────────────┐   │  MEDIA & STORAGE ASSETS    │
│  LLM INFERENCE      │   │  Screenshot Storage         │
│  Llama 3.3 70B      │   │  Export Engine (WeasyPrint) │
│  Qwen 2.5 72B       │   └────────────────────────────┘
└─────────────────────┘
```

For the detailed component interaction diagram and data flow specifications, refer to the [Architecture Design Document](./02_architecture_design.md).

---

## 6. Key Capabilities

| Capability | Description |
|-----------|-------------|
| **Script Parsing** | Converts unstructured text workflows into structured JSON DAGs |
| **Live UI Navigation** | Authenticates and navigates live staging environments |
| **Visual Element Highlighting** | Applies real-time CSS highlights to target UI elements |
| **Screenshot Capture** | Captures high-resolution, annotated step screenshots |
| **Technical Writing** | Synthesizes action metadata into professional Markdown documentation |
| **Quality Review** | AI-driven review for logical flow, tone, and visual accuracy |
| **Chat-based Editing** | Natural language commands for targeted document modification |
| **Multi-format Export** | Generates Markdown, HTML, and PDF outputs |
| **Streaming Progress** | Real-time pipeline progress via SSE |
| **Fault Tolerance** | Graceful degradation with text placeholders on capture failures |

---

## 7. Stakeholder Map

| Role | Primary Concerns | Recommended Reading |
|------|-----------------|-------------------|
| **Product Manager** | Capabilities, roadmap, ROI | This document + [Future Roadmap](./10_future_roadmap.md) |
| **Backend Engineer** | Agents, APIs, integrations | [Architecture Design](./02_architecture_design.md) + [Multi-Agent Spec](./03_multi_agent_specification.md) + [API Reference](./04_api_reference.md) |
| **Frontend Engineer** | UI components, API contracts | [Frontend Developer Guide](./06_frontend_developer_guide.md) + [API Reference](./04_api_reference.md) |
| **DevOps / SRE** | Deployment, scaling, monitoring | [Deployment & Operations Guide](./07_deployment_operations.md) + [NFRs](./09_non_functional_requirements.md) |
| **Security Engineer** | Credential handling, data privacy | [Security & Data Privacy](./08_security_data_privacy.md) |
| **QA Engineer** | Capture engine, fallback behavior | [Browser Automation Engine](./05_browser_automation_engine.md) |
| **Technical Writer** | System output quality | This document + [Multi-Agent Spec](./03_multi_agent_specification.md) |

---

## 8. Document Conventions

| Convention | Usage |
|-----------|-------|
| `Code font` | Command names, endpoint paths, environment variables, configuration keys |
| **Bold** | First introduction of key technical terms and critical emphasis |
| *Italic* | Document titles, supplementary context |
| `[DOC-XXX]` | Cross-reference to other documents in this suite |
| ⚠️ **Warning** | Critical operational warnings |
| 💡 **Tip** | Best practices and efficiency guidance |
| 📌 **Note** | Supplementary clarification |
| 🔒 **Security** | Security-sensitive content |

---

*→ Next: [Architecture Design Document](./02_architecture_design.md)*

---

*Document ID: DOC-001 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
