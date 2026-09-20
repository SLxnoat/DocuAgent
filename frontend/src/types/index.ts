// ── Job Lifecycle ─────────────────────────────────────────────────────────────
export type JobStatus =
  | "idle" // Client-only: before first submission
  | "queued" // Celery task queued
  | "analyzing" // Agent 1: script parsing
  | "capturing" // Agent 2: Playwright browser automation
  | "compiling" // Agent 3: Markdown generation
  | "reviewing" // Agent 4: quality check
  | "awaiting_input" // HITL interrupt — document ready for user
  | "refining" // Agent 5: processing a chat request
  | "completed" // All pipeline phases done
  | "failed"; // Fatal error

export type CaptureStatus = "pending" | "captured" | "fallback" | "error";

export interface StepCaptureStatus {
  stepIndex: number;
  status: CaptureStatus;
  screenshotPath?: string;
  error?: string;
}

// ── Chat ──────────────────────────────────────────────────────────────────────
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isLoading?: boolean; // true while awaiting agent_response
}

// ── API Request / Response ────────────────────────────────────────────────────
export interface GenerateRequest {
  script: string;
  target_url: string;
  credentials?: { username: string; password: string };
  options?: {
    output_formats?: ("markdown" | "html" | "pdf")[];
    domain_hint?: string;
    language?: string;
  };
}

export interface GenerateResponse {
  job_id: string;
  session_id: string;
}

export interface ChangeSummaryItem {
  section: string;
  change_type: string;
  description: string;
}

export interface ChatResponse {
  session_id: string;
  response_message: string;
  updated_markdown: string;
  changes_summary: ChangeSummaryItem[];
  recapture_triggered: boolean;
  recapture_step_index: number | null;
  timestamp: string;
}

// ── SSE Events ────────────────────────────────────────────────────────────────
export type SSEEventType =
  | "pipeline_started"
  | "script_analyzed"
  | "capture_progress"
  | "capture_complete"
  | "draft_compiled"
  | "quality_review_started"
  | "quality_loop"
  | "quality_approved"
  | "document_ready"
  | "document_updated"
  | "export_ready"
  | "job_failed"
  | "heartbeat";

export interface SSEEvent {
  type: SSEEventType;
  job_id?: string;
  step_index?: number;
  total_steps?: number;
  status?: string;
  markdown?: string;
  error?: string;
  step_count?: number;
  domain?: string;
  changes_summary?: ChangeSummaryItem[];
  timestamp?: string;
}

// ── WebSocket Messages ────────────────────────────────────────────────────────
export interface WSClientMessage {
  type: "user_message" | "ping";
  content?: string;
  timestamp: string;
}

export interface WSServerMessage {
  type: "agent_response" | "typing_start" | "typing_stop" | "pong" | "error";
  content?: string;
  updated_markdown?: string;
  changes_summary?: ChangeSummaryItem[];
  recapture_triggered?: boolean;
  recapture_step_index?: number | null;
  message?: string; // error message
  timestamp?: string;
}

// ── Theme ─────────────────────────────────────────────────────────────────────
export type Theme = "light" | "dark" | "system";

export type ExportFormat = "markdown" | "html" | "pdf";
