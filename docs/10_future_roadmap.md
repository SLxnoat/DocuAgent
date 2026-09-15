# Future Roadmap

**Document ID:** DOC-010  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Product Management, Engineering Leadership, All Stakeholders

---

## Table of Contents

1. [Roadmap Overview](#1-roadmap-overview)
2. [Version Strategy](#2-version-strategy)
3. [v1.0 — Current Release](#3-v10--current-release)
4. [v1.1 — Short-Term Enhancements](#4-v11--short-term-enhancements)
5. [v2.0 — Multimodal Vision Verification](#5-v20--multimodal-vision-verification)
6. [v2.1 — Video Manual Generation](#6-v21--video-manual-generation)
7. [v2.2 — Enterprise Knowledge Base Integration](#7-v22--enterprise-knowledge-base-integration)
8. [v3.0 — Autonomous Documentation Monitoring](#8-v30--autonomous-documentation-monitoring)
9. [Backlog & Candidate Features](#9-backlog--candidate-features)
10. [Deprecation Plan](#10-deprecation-plan)

---

## 1. Roadmap Overview

The DocuAgent AI roadmap is organized around three strategic themes:

| Theme                          | Description                                                                  | Horizon     |
| ------------------------------ | ---------------------------------------------------------------------------- | ----------- |
| **🎯 Accuracy & Intelligence** | Improve the precision of AI-generated content and visual captures            | v1.1 – v2.0 |
| **🎬 Media & Format Richness** | Expand output formats from static screenshots to video and interactive media | v2.1        |
| **🔗 Enterprise Integration**  | Connect DocuAgent AI output to existing knowledge management ecosystems      | v2.2 – v3.0 |

```
Q4 2026       Q1 2027       Q2 2027       Q3 2027       Q4 2027
   │              │              │              │              │
   ▼              ▼              ▼              ▼              ▼
[v1.0 GA]    [v1.1 Patch]  [v2.0 Vision] [v2.1 Video]  [v2.2 + v3.0]
  Current     Quick wins    Multimodal    Video clips   Enterprise
  release     & fixes       LLM review    generation    integrations
```

---

## 2. Version Strategy

DocuAgent AI follows **Semantic Versioning (SemVer)**:

| Version Type      | When Used                                               | Example |
| ----------------- | ------------------------------------------------------- | ------- |
| **MAJOR** (X.0.0) | Breaking API changes or fundamental architecture shifts | v2.0.0  |
| **MINOR** (x.Y.0) | New backward-compatible features                        | v1.1.0  |
| **PATCH** (x.y.Z) | Bug fixes, security patches, performance improvements   | v1.0.1  |

**Support Policy:**

- The current major version receives full feature development and security patches.
- The previous major version receives **security patches only** for 12 months post-successor release.

---

## 3. v1.0 — Current Release

**Release Date:** Q4 2026 (General Availability)

### Included Capabilities

| Feature                                                | Status      |
| ------------------------------------------------------ | ----------- |
| Script parsing & structured DAG generation (Agent 1)   | ✅ Released |
| Playwright-based UI automation & screenshot capture    | ✅ Released |
| Dynamic CSS highlight injection                        | ✅ Released |
| Technical Writer Agent (Agent 3) — Markdown generation | ✅ Released |
| Quality Review Agent (Agent 4)                         | ✅ Released |
| Conversational Refiner Agent (Agent 5)                 | ✅ Released |
| Human-in-the-Loop interrupt mechanism                  | ✅ Released |
| Split-screen Monaco Editor + live preview              | ✅ Released |
| SSE-based real-time progress streaming                 | ✅ Released |
| WebSocket chat interface                               | ✅ Released |
| Multi-format export (Markdown, HTML, PDF)              | ✅ Released |
| Playwright selector fallback strategies                | ✅ Released |
| Graceful degradation (text-only output)                | ✅ Released |
| Celery + Redis task queue                              | ✅ Released |
| Docker Compose deployment                              | ✅ Released |

### Known Limitations (v1.0)

| Limitation                                                             | Planned Fix Version |
| ---------------------------------------------------------------------- | ------------------- |
| Manual screenshot replacement requires page reload                     | v1.1                |
| No support for applications behind corporate SSO (SAML/OAuth)          | v1.1                |
| PDF export does not support RTL languages                              | v1.1                |
| Chat session expires after Redis TTL (24h) — no session resume         | v2.0                |
| No visual verification that captured screenshot shows intended element | v2.0                |
| Only static PNG screenshots — no animated captures                     | v2.1                |

---

## 4. v1.1 — Short-Term Enhancements

**Target Release:** Q1 2027  
**Focus:** Quality of life improvements, bug fixes, and enterprise auth support.

### 4.1 SSO & OAuth Authentication Support

**Background:** Many enterprise staging environments use corporate SSO (SAML 2.0 or OAuth 2.0) for authentication, which standard form-based login does not support.

**Enhancement:** Extend the `authenticate()` method in the Playwright Capture Engine to support:

- **Cookie/Session Token Injection:** Accept pre-authenticated browser cookies from the user.
- **OAuth 2.0 Authorization Code Flow:** Playwright navigates through OAuth consent screens using provided credentials.
- **SAML Assertion Injection:** Accept a valid SAML session cookie to bypass IdP redirects.

**User Interface Change:** Add an "Authentication Method" selector in the ScriptInputForm (`Form Login`, `Cookie Injection`, `OAuth Flow`).

### 4.2 Live Screenshot Replacement (Without Page Reload)

**Background:** v1.0 requires a page reload after manual screenshot upload, disrupting the editing flow.

**Enhancement:** Implement in-place React image update using object URL replacement:

- Frontend uses `URL.createObjectURL()` to display the uploaded file immediately.
- Background API call saves the file server-side asynchronously.
- `ScreenshotImage` component updates `src` prop without parent re-render.

### 4.3 RTL Language Support for PDF Export

**Background:** Arabic, Hebrew, and Urdu manuals require right-to-left text direction in PDF rendering.

**Enhancement:** Extend the WeasyPrint export template with dynamic CSS `direction: rtl` and `text-align: right` applied when the document language code is in `RTL_LANGUAGES = {'ar', 'he', 'ur', 'fa'}`.

### 4.4 Selector Learning from User Corrections

**Background:** When users click "Re-Capture" after a selector failure, they often correct the selector manually. These corrections should improve future capture accuracy.

**Enhancement:** Store user-confirmed selectors in a lightweight per-domain selector cache (Redis Hash). When the same domain is processed in a future job, Agent 1 queries the cache and preferentially suggests cached selectors.

### 4.5 Estimated v1.1 Scope

| Feature                      | Engineering Estimate | Priority |
| ---------------------------- | -------------------- | -------- |
| SSO/OAuth authentication     | 2 weeks              | P0       |
| Live screenshot replacement  | 3 days               | P1       |
| RTL PDF export               | 1 week               | P1       |
| Selector learning cache      | 1 week               | P2       |
| Bug fixes & security patches | Ongoing              | P0       |

---

## 5. v2.0 — Multimodal Vision Verification

**Target Release:** Q2 2027  
**Focus:** Integrate vision-capable LLMs to autonomously verify screenshot accuracy.

### 5.1 Problem Statement

In v1.0, the Quality Review Agent (Agent 4) reviews only the Markdown content — it cannot inspect whether the captured screenshot visually matches the described UI element. A screenshot of the wrong element or a blank page goes undetected until the user reviews it manually.

### 5.2 Solution: Vision LLM Verification Agent

**New Agent — Agent 6: Vision Verifier**

| Property              | Value                                                            |
| --------------------- | ---------------------------------------------------------------- |
| **Node Name**         | `vision_verify_node`                                             |
| **Role**              | Screenshot–Step Consistency Verification                         |
| **LLM Model**         | LLaVA 34B or Qwen-VL 72B (vision-capable)                        |
| **Position in Graph** | After `capture_screenshots_node`; before `compile_markdown_node` |

**Workflow:**

```
For each captured screenshot:
    │
    ▼
Vision LLM receives:
    - Screenshot image (base64 encoded)
    - Step description text
    - Expected UI element description
    │
    ▼
LLM responds with:
    - match_confidence: float (0.0 – 1.0)
    - is_correct_element: bool
    - correction_suggestion: str | null
    │
    ├── match_confidence ≥ 0.85 → Accept screenshot
    │
    └── match_confidence < 0.85 → Trigger re-capture with refined selector
```

### 5.3 Expected Impact

| Metric                               | v1.0             | v2.0 Target                      |
| ------------------------------------ | ---------------- | -------------------------------- |
| Screenshot accuracy rate             | ~85% (estimated) | ≥ 97%                            |
| Auto-detected wrong-element captures | 0%               | ≥ 90% of wrong captures detected |
| Manual re-capture interventions      | Frequent         | Rare                             |

### 5.4 Vision Model Integration

```python
from langchain_ollama import ChatOllama
import base64

vision_llm = ChatOllama(
    model="llava:34b",          # Or "qwen2.5vl:72b"
    base_url=settings.OLLAMA_BASE_URL,
)

def encode_screenshot(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def vision_verify_step(step: StepSchema, screenshot_path: str) -> VerificationResult:
    image_data = encode_screenshot(screenshot_path)
    response = await vision_llm.ainvoke([
        HumanMessage(content=[
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
            {"type": "text", "text": f"Does this screenshot show: '{step.description}'? "
                                      f"Is the highlighted element '{step.target_selector}' visible and correctly highlighted? "
                                      f"Respond as JSON: {{\"match_confidence\": 0.0-1.0, \"is_correct\": true/false, \"notes\": \"...\"}}"}
        ])
    ])
    return parse_verification_response(response.content)
```

### 5.5 Additional v2.0 Features

- **Session Resume:** Allow users to continue editing a document after the 24-hour Redis TTL by persisting session metadata to a lightweight SQLite or PostgreSQL database.
- **Document Templates:** Introduce optional starting templates (API Reference, Quick Start Guide, Administrator Manual) that pre-structure the document before Agent 3 fills in the content.

---

## 6. v2.1 — Video Manual Generation

**Target Release:** Q3 2027  
**Focus:** Convert captured Playwright browser interactions into animated video clips embedded in manuals.

### 6.1 Problem Statement

Static screenshots provide accurate point-in-time views of UI state, but they cannot communicate dynamic interactions such as dropdown expansions, modal animations, or multi-step form flows that require temporal context.

### 6.2 Solution: Playwright Video Recording

Playwright natively supports browser video recording via its `recordVideo` context option. Agent 2 will be extended to optionally capture a video clip alongside each screenshot.

```python
# Playwright video recording context
context = await browser.new_context(
    record_video_dir=f"assets/{job_id}/videos/",
    record_video_size={"width": 1440, "height": 900},
)

# After step execution, save video clip
video = page.video
await video.save_as(f"assets/{job_id}/videos/step_{step_index:03d}.webm")
```

### 6.3 Output Formats

| Format   | Use Case                                         | Tool                           |
| -------- | ------------------------------------------------ | ------------------------------ |
| **WebM** | Embedding in HTML manuals                        | Playwright native recording    |
| **MP4**  | Embedding in PDF (interactive PDF) or standalone | FFmpeg conversion from WebM    |
| **GIF**  | Embedding in Markdown (GitHub-compatible)        | FFmpeg WebM → GIF (palettegen) |

### 6.4 Manual Output Changes

**Markdown format with GIF:**

```markdown
## Step 3: Add a New User

![Step 3 — Click Add New User](../assets/{job_id}/videos/step_003.gif)

Click the **Add New User** button in the toolbar...
```

**HTML format with inline video:**

```html
<video autoplay loop muted playsinline width="1440">
  <source src="../assets/{job_id}/videos/step_003.webm" type="video/webm" />
</video>
```

### 6.5 Estimated Storage Impact

| Per Job (10 steps)          | Size       |
| --------------------------- | ---------- |
| Screenshots (PNG)           | ~5 MB      |
| Video clips (WebM, 5s each) | ~20 MB     |
| GIFs (from WebM)            | ~15 MB     |
| **Total**                   | **~40 MB** |

> ⚠️ **Storage Warning:** Video generation significantly increases per-job storage requirements. Production deployments targeting this feature should provision S3-compatible object storage and implement 48-hour asset expiry for video assets.

---

## 7. v2.2 — Enterprise Knowledge Base Integration

**Target Release:** Q4 2027  
**Focus:** Directly publish generated manuals to enterprise knowledge management platforms via REST API webhooks.

### 7.1 Supported Integrations (Phase 1)

| Platform         | Integration Method                           | Authentication           |
| ---------------- | -------------------------------------------- | ------------------------ |
| **Confluence**   | Confluence REST API v2 — Create/Update Page  | API Token (Basic Auth)   |
| **Notion**       | Notion API — Create Page in Database         | Notion Integration Token |
| **GitBook**      | GitBook API — Create Space Content           | GitBook API Key          |
| **GitHub Pages** | GitHub REST API — Create/Update File in Repo | GitHub PAT               |

### 7.2 User Flow

```
User completes DocuAgent AI document
         │
         ▼
User clicks "Publish to Confluence" in ExportBar
         │
         ▼
Modal: Select Space / Parent Page / Title
         │
         ▼
POST /api/v1/publish/{job_id}
    {
      "platform": "confluence",
      "credentials": { "base_url": "...", "api_token": "..." },
      "target": { "space_key": "DOCS", "parent_page_id": "12345", "title": "User Manual" }
    }
         │
         ▼
Backend converts Markdown → Confluence Wiki Markup (or ADF)
         │
         ▼
Confluence API creates/updates the page with embedded screenshots (as Confluence attachments)
         │
         ▼
Response: { "page_url": "https://wiki.example.com/display/DOCS/User+Manual" }
         │
         ▼
Frontend shows success notification with link to published page
```

### 7.3 Security Considerations for Integration Credentials

Platform API tokens provided for publishing follow the **same zero-persistence credential policy** as staging credentials:

- Held in-memory only for the duration of the publish API call.
- Never stored in Redis state or persisted to disk.
- Excluded from all logging handlers.

---

## 8. v3.0 — Autonomous Documentation Monitoring

**Target Release:** Q4 2027 (concurrent with v2.2)  
**Focus:** Proactively detect when published documentation is outdated by monitoring staging environments for UI changes and alerting documentation owners.

### 8.1 Concept

DocuAgent AI v3.0 introduces a **background monitoring daemon** that periodically visits the staging application and compares current UI state against the original screenshots captured in a published manual.

```
Scheduled job (daily / on deploy hook):
         │
         ▼
Playwright re-visits all step URLs from a published job
         │
         ▼
Vision LLM compares new screenshot to original screenshot
    │
    ├── UI unchanged → "Documentation is current" status
    │
    └── UI changed (confidence > threshold)
                │
                ▼
        Notification sent to manual owner:
        "Step 3 may be outdated — the 'Add New User' button
         appears to have moved or been renamed. Review recommended."
                │
                ▼
        [Optional] Automated re-generation trigger
```

### 8.2 Trigger Options

| Trigger Method | Description                                       |
| -------------- | ------------------------------------------------- |
| **Scheduled**  | Cron-based re-check (daily, weekly)               |
| **Webhook**    | CI/CD pipeline calls DocuAgent at deployment time |
| **Manual**     | User clicks "Check for Updates" in the ExportBar  |

### 8.3 Benefits

| Benefit                       | Value                                                           |
| ----------------------------- | --------------------------------------------------------------- |
| Proactive staleness detection | Documentation team alerted before users find outdated manuals   |
| Automated re-generation       | Reduces revision workload to a single review-and-approve action |
| CI/CD integration             | Documentation health becomes part of the deployment pipeline    |

---

## 9. Backlog & Candidate Features

The following features are under consideration for future releases but are not yet scheduled:

| Feature                              | Description                                                                            | Est. Complexity |
| ------------------------------------ | -------------------------------------------------------------------------------------- | --------------- |
| **Multilingual parallel generation** | Generate the same manual in multiple languages simultaneously using parallel LLM calls | Medium          |
| **WCAG accessibility checks**        | Automatically flag UI elements that appear inaccessible based on screenshot analysis   | High            |
| **Manual versioning & diff view**    | Track document versions and display a diff when refinements are made                   | Medium          |
| **Template library**                 | Community-contributed and organization-specific document templates                     | Low             |
| **Browser extension**                | Record workflow directly in the browser without providing a staging URL                | High            |
| **Offline mode**                     | Run all LLM inference locally using smaller quantized models                           | High            |
| **Jira issue linking**               | Attach generated manuals to Jira tickets as documentation artifacts                    | Low             |
| **User analytics dashboard**         | Track which manuals are generated, exported, and published per team                    | Medium          |
| **Annotation tool**                  | Let users add manual callout arrows or text annotations to screenshots in-browser      | High            |
| **API-first scripting**              | Accept OpenAPI specs (Swagger) to automatically generate API documentation manuals     | High            |

---

## 10. Deprecation Plan

### 10.1 v1.0 Support Window

| Release | Feature Support | Security Patches | End of Support          |
| ------- | --------------- | ---------------- | ----------------------- |
| v1.0.x  | Until v2.0 GA   | Until v3.0 GA    | 12 months after v2.0 GA |
| v2.0.x  | Until v3.0 GA   | Until v4.0 GA    | 12 months after v3.0 GA |

### 10.2 Deprecation Notification Policy

- **90 days notice** before deprecating any public API endpoint or removing a feature.
- Deprecation notices communicated via API response headers (`Deprecation`, `Sunset`) and release notes.
- Migration guides published alongside all breaking changes.

### 10.3 API Version Lifecycle

| API Version | Status            | Sunset Date                                 |
| ----------- | ----------------- | ------------------------------------------- |
| `/api/v1`   | ✅ Active         | TBD (minimum 12 months post v2 API release) |
| `/api/v2`   | 🔲 Planned (v2.0) | —                                           |

---

_← Previous: [Non-Functional Requirements](./09_non_functional_requirements.md)_  
_→ Back to: [Documentation Index](./README.md)_

---

_Document ID: DOC-010 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite_
