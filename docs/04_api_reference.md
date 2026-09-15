# API Reference

**Document ID:** DOC-004  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Frontend Engineers, Backend Engineers, Integration Developers

---

## Table of Contents

1. [Base URL & Versioning](#1-base-url--versioning)
2. [Authentication](#2-authentication)
3. [Common Headers](#3-common-headers)
4. [Error Response Format](#4-error-response-format)
5. [Generation Endpoints](#5-generation-endpoints)
6. [Streaming Endpoints](#6-streaming-endpoints)
7. [Chat & Refinement Endpoints](#7-chat--refinement-endpoints)
8. [Export Endpoints](#8-export-endpoints)
9. [Recapture Endpoints](#9-recapture-endpoints)
10. [Job Management Endpoints](#10-job-management-endpoints)
11. [WebSocket Protocol](#11-websocket-protocol)
12. [SSE Event Reference](#12-sse-event-reference)
13. [HTTP Status Code Reference](#13-http-status-code-reference)
14. [Schema Definitions](#14-schema-definitions)

---

## 1. Base URL & Versioning

All API endpoints are prefixed with the base URL and API version:

```
Base URL: https://{host}:{port}
API Prefix: /api/v1
Full Base: https://{host}:{port}/api/v1
```

**API Versioning Policy:** The current stable version is `v1`. Breaking changes will be introduced under `v2`. Non-breaking additions are applied to the existing version.

**Health Check:**

```http
GET /health

Response 200:
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-09-15T14:31:30+05:30"
}
```

---

## 2. Authentication

> 🔒 **Security:** API authentication uses Bearer tokens for client-server communication. Staging application credentials submitted in generation requests are handled separately and are never exposed in response bodies or logs.

```http
Authorization: Bearer {api_token}
```

Tokens are issued during system provisioning and managed by the system administrator. Contact your DevOps team for token issuance.

---

## 3. Common Headers

| Header          | Required          | Description                                                 |
| --------------- | ----------------- | ----------------------------------------------------------- |
| `Authorization` | ✅ Yes            | Bearer authentication token                                 |
| `Content-Type`  | ✅ Yes (POST/PUT) | Must be `application/json`                                  |
| `Accept`        | Optional          | `application/json` (default) or `text/event-stream` for SSE |
| `X-Request-ID`  | Optional          | Client-provided UUID for request tracing                    |

---

## 4. Error Response Format

All error responses follow a consistent JSON schema:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error description",
    "details": {
      "field": "target_url",
      "issue": "Must be a valid HTTP/HTTPS URL"
    },
    "request_id": "req_abc123",
    "timestamp": "2026-09-15T14:31:30+05:30"
  }
}
```

### Error Codes

| Code                        | HTTP Status | Description                                          |
| --------------------------- | ----------- | ---------------------------------------------------- |
| `VALIDATION_ERROR`          | 422         | Request body failed schema validation                |
| `AUTHENTICATION_FAILED`     | 401         | Invalid or missing API token                         |
| `JOB_NOT_FOUND`             | 404         | Specified job_id does not exist                      |
| `SESSION_NOT_FOUND`         | 404         | Specified session_id does not exist                  |
| `JOB_ALREADY_RUNNING`       | 409         | A generation job is already active for this session  |
| `EXPORT_FORMAT_UNSUPPORTED` | 400         | Requested export format is not supported             |
| `INTERNAL_SERVER_ERROR`     | 500         | Unhandled server-side error                          |
| `LLM_INFERENCE_TIMEOUT`     | 504         | Ollama Cloud API did not respond within timeout      |
| `BROWSER_AUTOMATION_FAILED` | 500         | Playwright engine encountered an unrecoverable error |

---

## 5. Generation Endpoints

### POST `/api/v1/generate`

Submits a new manual generation job. Returns a `job_id` and `session_id` for subsequent streaming and chat operations.

**Request Body:**

```json
{
  "script": "string",
  "target_url": "string (valid URL)",
  "credentials": {
    "username": "string",
    "password": "string"
  },
  "options": {
    "output_formats": ["markdown", "html", "pdf"],
    "domain_hint": "string (optional)",
    "language": "en"
  }
}
```

| Field                    | Type   | Required | Description                                  |
| ------------------------ | ------ | -------- | -------------------------------------------- |
| `script`                 | string | ✅       | Unstructured workflow text to process        |
| `target_url`             | string | ✅       | Base URL of the staging application          |
| `credentials.username`   | string | Optional | Username for application authentication      |
| `credentials.password`   | string | Optional | Password for application authentication      |
| `options.output_formats` | array  | Optional | Formats to generate. Default: `["markdown"]` |
| `options.domain_hint`    | string | Optional | Override domain detection (e.g., `"CRM"`)    |
| `options.language`       | string | Optional | Output language code. Default: `"en"`        |

**Response `202 Accepted`:**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "session_id": "sess_x9y8z7w6v5u4",
  "status": "queued",
  "estimated_duration_seconds": 120,
  "stream_url": "/api/v1/stream/job_a1b2c3d4e5f6",
  "created_at": "2026-09-15T14:31:30+05:30"
}
```

**Example Request:**

```bash
curl -X POST https://docuagent.example.com/api/v1/generate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Log in to the dashboard, navigate to Users, add a new admin user.",
    "target_url": "https://staging.app.example.com",
    "credentials": {
      "username": "admin@example.com",
      "password": "staging_password_123"
    },
    "options": {
      "output_formats": ["markdown", "pdf"]
    }
  }'
```

---

## 6. Streaming Endpoints

### GET `/api/v1/stream/{job_id}`

Opens a Server-Sent Events (SSE) channel for real-time pipeline progress updates.

**Path Parameters:**

| Parameter | Type   | Description                            |
| --------- | ------ | -------------------------------------- |
| `job_id`  | string | Job identifier returned by `/generate` |

**Headers:**

```http
Accept: text/event-stream
Cache-Control: no-cache
```

**SSE Event Stream Example:**

```
data: {"type": "pipeline_started", "job_id": "job_a1b2c3d4e5f6", "timestamp": "2026-09-15T14:31:30Z"}

data: {"type": "script_analyzed", "step_count": 5, "domain": "Admin Portal", "timestamp": "2026-09-15T14:31:32Z"}

data: {"type": "capture_progress", "step_index": 1, "total_steps": 5, "status": "captured", "timestamp": "2026-09-15T14:31:35Z"}

data: {"type": "capture_progress", "step_index": 2, "total_steps": 5, "status": "captured", "timestamp": "2026-09-15T14:31:38Z"}

data: {"type": "capture_progress", "step_index": 3, "total_steps": 5, "status": "fallback", "error": "Selector not found", "timestamp": "2026-09-15T14:31:40Z"}

data: {"type": "capture_complete", "total_captured": 5, "total_fallbacks": 1, "timestamp": "2026-09-15T14:31:42Z"}

data: {"type": "draft_compiled", "timestamp": "2026-09-15T14:31:55Z"}

data: {"type": "quality_approved", "timestamp": "2026-09-15T14:32:00Z"}

data: {"type": "document_ready", "markdown": "# User Manual\n...", "timestamp": "2026-09-15T14:32:01Z"}
```

> 📌 **Note:** The `document_ready` event includes the full Markdown content. The frontend should parse and render this event to populate the editor.

**Full SSE Event Reference:** See [Section 12](#12-sse-event-reference).

---

## 7. Chat & Refinement Endpoints

### POST `/api/v1/chat/{session_id}`

Sends a natural language refinement request to the Conversational Refiner Agent.

**Path Parameters:**

| Parameter    | Type   | Description                                |
| ------------ | ------ | ------------------------------------------ |
| `session_id` | string | Session identifier returned by `/generate` |

**Request Body:**

```json
{
  "message": "string",
  "context": {
    "current_markdown": "string (optional — current editor content if modified by user)"
  }
}
```

| Field                      | Type   | Required | Description                                                |
| -------------------------- | ------ | -------- | ---------------------------------------------------------- |
| `message`                  | string | ✅       | Natural language refinement request                        |
| `context.current_markdown` | string | Optional | If user manually edited the document, pass current content |

**Response `200 OK`:**

```json
{
  "session_id": "sess_x9y8z7w6v5u4",
  "response_message": "I've added a warning callout to Step 3 regarding data loss. Please review the updated document.",
  "updated_markdown": "# User Manual\n...[updated content]...",
  "changes_summary": [
    {
      "section": "Step 3",
      "change_type": "text_edit",
      "description": "Added ⚠️ Warning callout box"
    }
  ],
  "recapture_triggered": false,
  "recapture_step_index": null,
  "timestamp": "2026-09-15T14:35:10+05:30"
}
```

| Response Field         | Type     | Description                                     |
| ---------------------- | -------- | ----------------------------------------------- |
| `response_message`     | string   | Agent's conversational reply to the user        |
| `updated_markdown`     | string   | Full updated Markdown document                  |
| `changes_summary`      | array    | Machine-readable summary of applied changes     |
| `recapture_triggered`  | boolean  | True if agent initiated a screenshot re-capture |
| `recapture_step_index` | int/null | Step index being recaptured (if applicable)     |

**Example Request:**

```bash
curl -X POST https://docuagent.example.com/api/v1/chat/sess_x9y8z7w6v5u4 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a troubleshooting note to step 3 about what to do if the button is greyed out."
  }'
```

---

## 8. Export Endpoints

### GET `/api/v1/export/{job_id}?format={format}`

Generates and downloads the final document in the specified format.

**Path Parameters:**

| Parameter | Type   | Description    |
| --------- | ------ | -------------- |
| `job_id`  | string | Job identifier |

**Query Parameters:**

| Parameter | Type   | Required | Description                       |
| --------- | ------ | -------- | --------------------------------- |
| `format`  | string | ✅       | One of: `markdown`, `html`, `pdf` |

**Response `200 OK`:**

Returns the file as a binary stream with appropriate Content-Type and Content-Disposition headers.

| Format     | Content-Type      | Filename               |
| ---------- | ----------------- | ---------------------- |
| `markdown` | `text/markdown`   | `manual_{job_id}.md`   |
| `html`     | `text/html`       | `manual_{job_id}.html` |
| `pdf`      | `application/pdf` | `manual_{job_id}.pdf`  |

**Example Request:**

```bash
# Download PDF
curl -X GET "https://docuagent.example.com/api/v1/export/job_a1b2c3d4e5f6?format=pdf" \
  -H "Authorization: Bearer {token}" \
  --output manual.pdf
```

**Error Cases:**

| Scenario                 | HTTP Status | Error Code                  |
| ------------------------ | ----------- | --------------------------- |
| Job not found            | 404         | `JOB_NOT_FOUND`             |
| Export not yet available | 409         | `JOB_STILL_PROCESSING`      |
| Unsupported format       | 400         | `EXPORT_FORMAT_UNSUPPORTED` |

---

## 9. Recapture Endpoints

### POST `/api/v1/recapture/{job_id}/{step_index}`

Triggers a Playwright re-capture for a single step. Used when the user clicks the re-capture button on an individual screenshot in the editor.

**Path Parameters:**

| Parameter    | Type    | Description                      |
| ------------ | ------- | -------------------------------- |
| `job_id`     | string  | Job identifier                   |
| `step_index` | integer | 1-based step index to re-capture |

**Request Body (optional):**

```json
{
  "selector_override": "string (CSS selector to use instead of original)",
  "custom_screenshot_path": "string (if user provides a manual upload path)"
}
```

**Response `202 Accepted`:**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "step_index": 3,
  "status": "recapture_queued",
  "stream_url": "/api/v1/stream/job_a1b2c3d4e5f6"
}
```

The SSE stream will emit a `capture_progress` event for the specific step when recapture completes.

---

## 10. Job Management Endpoints

### GET `/api/v1/jobs/{job_id}`

Retrieves the current status and metadata of a generation job.

**Response `200 OK`:**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "session_id": "sess_x9y8z7w6v5u4",
  "status": "completed",
  "step_count": 5,
  "screenshots_captured": 4,
  "screenshots_fallback": 1,
  "quality_approved": true,
  "export_formats_available": ["markdown", "html", "pdf"],
  "created_at": "2026-09-15T14:31:30+05:30",
  "completed_at": "2026-09-15T14:32:01+05:30",
  "duration_seconds": 91
}
```

**Job Status Values:**

| Status           | Description                                      |
| ---------------- | ------------------------------------------------ |
| `queued`         | Job is in the Celery task queue, not yet started |
| `analyzing`      | Agent 1 is parsing the script                    |
| `capturing`      | Agent 2 is running browser automation            |
| `compiling`      | Agent 3 is generating Markdown                   |
| `reviewing`      | Agent 4 is performing quality review             |
| `awaiting_input` | HITL interrupt — document presented to user      |
| `refining`       | Agent 5 is processing a chat request             |
| `completed`      | Pipeline finished, document ready                |
| `failed`         | Job failed after all retries                     |

### DELETE `/api/v1/jobs/{job_id}`

Cancels a running job and cleans up associated assets.

**Response `200 OK`:**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "cancelled",
  "timestamp": "2026-09-15T14:40:00+05:30"
}
```

---

## 11. WebSocket Protocol

The chat interface can also operate over a persistent WebSocket connection for lower-latency bidirectional communication.

**Connection URL:**

```
wss://{host}/api/v1/ws/chat/{session_id}?token={api_token}
```

**Client → Server Message Format:**

```json
{
  "type": "user_message",
  "content": "Add a note about browser compatibility in the prerequisites section.",
  "timestamp": "2026-09-15T14:35:00+05:30"
}
```

**Server → Client Message Format:**

```json
{
  "type": "agent_response",
  "content": "I've added a browser compatibility note to the Prerequisites section.",
  "updated_markdown": "# User Manual\n...",
  "changes_summary": [...],
  "timestamp": "2026-09-15T14:35:08+05:30"
}
```

**WebSocket Message Types:**

| Type                 | Direction       | Description                       |
| -------------------- | --------------- | --------------------------------- |
| `user_message`       | Client → Server | User refinement request           |
| `agent_response`     | Server → Client | Agent reply with updated document |
| `recapture_started`  | Server → Client | Playwright recapture initiated    |
| `recapture_complete` | Server → Client | New screenshot available          |
| `error`              | Server → Client | Error notification                |
| `ping`               | Client → Server | Keep-alive heartbeat              |
| `pong`               | Server → Client | Keep-alive response               |

---

## 12. SSE Event Reference

All SSE events are JSON objects emitted as `data:` fields.

| Event Type               | Payload Fields                                  | Description                        |
| ------------------------ | ----------------------------------------------- | ---------------------------------- |
| `pipeline_started`       | `job_id`, `timestamp`                           | Job execution has begun            |
| `script_analyzed`        | `step_count`, `domain`, `timestamp`             | Script parsing complete            |
| `capture_progress`       | `step_index`, `total_steps`, `status`, `error?` | Per-step capture update            |
| `capture_complete`       | `total_captured`, `total_fallbacks`             | All captures finished              |
| `draft_compiled`         | `timestamp`                                     | Markdown draft generated           |
| `quality_review_started` | `timestamp`                                     | Quality agent reviewing            |
| `quality_loop`           | `retry_count`, `feedback`                       | Quality review failed; retrying    |
| `quality_approved`       | `timestamp`                                     | Quality review passed              |
| `document_ready`         | `markdown`                                      | Full document content ready for UI |
| `document_updated`       | `markdown`, `changes_summary`                   | Chat-triggered update applied      |
| `export_ready`           | `format`, `download_url`                        | Export file ready                  |
| `job_failed`             | `error`, `step`, `timestamp`                    | Job encountered fatal error        |

---

## 13. HTTP Status Code Reference

| Status                      | Meaning                               | Common Causes                          |
| --------------------------- | ------------------------------------- | -------------------------------------- |
| `200 OK`                    | Request succeeded                     | Successful GET, synchronous operations |
| `202 Accepted`              | Request accepted for async processing | Job submission, recapture trigger      |
| `400 Bad Request`           | Invalid request parameters            | Unsupported format, malformed body     |
| `401 Unauthorized`          | Authentication failed                 | Missing/invalid Bearer token           |
| `404 Not Found`             | Resource not found                    | Unknown job_id or session_id           |
| `409 Conflict`              | State conflict                        | Job already running, export not ready  |
| `422 Unprocessable Entity`  | Schema validation failure             | Missing required fields                |
| `500 Internal Server Error` | Server-side failure                   | LLM or browser automation error        |
| `504 Gateway Timeout`       | Upstream timeout                      | Ollama Cloud API timeout               |

---

## 14. Schema Definitions

### GenerateRequest

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["script", "target_url"],
  "properties": {
    "script": { "type": "string", "minLength": 10 },
    "target_url": { "type": "string", "format": "uri" },
    "credentials": {
      "type": "object",
      "properties": {
        "username": { "type": "string" },
        "password": { "type": "string" }
      }
    },
    "options": {
      "type": "object",
      "properties": {
        "output_formats": {
          "type": "array",
          "items": { "enum": ["markdown", "html", "pdf"] },
          "default": ["markdown"]
        },
        "domain_hint": { "type": "string" },
        "language": { "type": "string", "default": "en" }
      }
    }
  }
}
```

### ChatRequest

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["message"],
  "properties": {
    "message": { "type": "string", "minLength": 1 },
    "context": {
      "type": "object",
      "properties": {
        "current_markdown": { "type": "string" }
      }
    }
  }
}
```

---

_← Previous: [Multi-Agent Design Specification](./03_multi_agent_specification.md)_  
_→ Next: [Browser Automation Engine](./05_browser_automation_engine.md)_

---

_Document ID: DOC-004 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite_
