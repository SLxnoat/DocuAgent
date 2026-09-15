# Frontend Developer Guide

**Document ID:** DOC-006  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Frontend Engineers

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Technology Stack](#3-technology-stack)
4. [Application State Management](#4-application-state-management)
5. [Core Components](#5-core-components)
6. [API Integration Layer](#6-api-integration-layer)
7. [SSE Stream Consumer](#7-sse-stream-consumer)
8. [WebSocket Chat Client](#8-websocket-chat-client)
9. [Monaco Editor Integration](#9-monaco-editor-integration)
10. [Export Flow](#10-export-flow)
11. [Environment Variables](#11-environment-variables)
12. [Development Setup](#12-development-setup)
13. [Component API Reference](#13-component-api-reference)

---

## 1. Overview

The DocuAgent AI frontend is a **React Single Page Application (SPA)** built with Vite. It provides:

- A workflow script input form with credential fields.
- A real-time split-screen Markdown editor (Monaco Editor on the left; live HTML preview on the right).
- An embedded chat panel for conversational document refinement.
- Real-time progress feedback via Server-Sent Events (SSE).
- One-click export in Markdown, HTML, and PDF formats.

---

## 2. Project Structure

```
docuagent-frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── api/
│   │   └── client.ts                # Axios REST client
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx         # Root layout: sidebar + main area
│   │   │   └── Sidebar.tsx          # Left sidebar navigation
│   │   ├── input/
│   │   │   ├── ScriptInputForm.tsx  # Script + URL + credential input form
│   │   │   └── OptionsPanel.tsx     # Generation options (format, language)
│   │   ├── editor/
│   │   │   ├── EditorPane.tsx       # Monaco Editor wrapper (left pane)
│   │   │   ├── PreviewPane.tsx      # Markdown → HTML live preview (right pane)
│   │   │   ├── SplitScreen.tsx      # Resizable split-pane container
│   │   │   └── ScreenshotImage.tsx  # Clickable screenshot with re-capture overlay
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx        # Chat container with message list
│   │   │   ├── ChatMessage.tsx      # Individual message bubble
│   │   │   └── ChatInput.tsx        # Message input field with send button
│   │   ├── progress/
│   │   │   ├── ProgressBar.tsx      # SSE-driven progress indicator
│   │   │   └── StepStatus.tsx       # Per-step capture status badge
│   │   └── export/
│   │       └── ExportBar.tsx        # Download buttons for MD / HTML / PDF
│   ├── hooks/
│   │   ├── useSSEStream.ts          # SSE consumer hook
│   │   ├── useWebSocket.ts          # WebSocket client hook
│   │   ├── useGenerate.ts           # Generation submit handler
│   │   └── useExport.ts             # Export download handler
│   ├── store/
│   │   └── useManualStore.ts        # Zustand global state store
│   ├── types/
│   │   └── index.ts                 # TypeScript type definitions
│   ├── utils/
│   │   ├── markdownUtils.ts         # Markdown parsing utilities
│   │   └── formatUtils.ts           # Date/size formatting helpers
│   ├── App.tsx                      # Root component
│   ├── main.tsx                     # Vite entry point
│   └── index.css                    # Tailwind CSS base import
├── .env.example                     # Environment variable template
├── vite.config.ts                   # Vite configuration
├── tailwind.config.ts               # Tailwind CSS configuration
└── tsconfig.json                    # TypeScript configuration
```

---

## 3. Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | 18+ | UI framework |
| `vite` | 5+ | Build tool and dev server |
| `typescript` | 5+ | Static typing |
| `tailwindcss` | 3+ | Utility-first CSS framework |
| `@shadcn/ui` | Latest | Accessible component primitives |
| `lucide-react` | Latest | Icon library |
| `zustand` | 4+ | Lightweight global state management |
| `@monaco-editor/react` | 4+ | Monaco code editor React wrapper |
| `@uiw/react-md-editor` | 3+ | Alternative Markdown preview renderer |
| `axios` | 1+ | HTTP client for REST API calls |
| `react-markdown` | 9+ | Markdown to JSX renderer |
| `remark-gfm` | 4+ | GitHub Flavored Markdown support |

**Install Dependencies:**

```bash
npm install react react-dom typescript vite
npm install tailwindcss @shadcn/ui lucide-react
npm install zustand @monaco-editor/react axios
npm install react-markdown remark-gfm @uiw/react-md-editor
npm install -D @types/react @types/react-dom
```

---

## 4. Application State Management

### 4.1 Zustand Store Schema

All shared application state is managed in a single Zustand store (`useManualStore`):

```typescript
// src/store/useManualStore.ts

import { create } from 'zustand';

export type JobStatus =
  | 'idle'
  | 'queued'
  | 'analyzing'
  | 'capturing'
  | 'compiling'
  | 'reviewing'
  | 'awaiting_input'
  | 'refining'
  | 'completed'
  | 'failed';

export interface StepCaptureStatus {
  stepIndex: number;
  status: 'pending' | 'captured' | 'fallback' | 'error';
  screenshotPath?: string;
  error?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ManualStore {
  // Job & Session State
  jobId: string | null;
  sessionId: string | null;
  jobStatus: JobStatus;
  
  // Document State
  markdownContent: string;
  
  // Progress State
  stepCount: number;
  stepStatuses: StepCaptureStatus[];
  
  // Chat State
  chatHistory: ChatMessage[];
  isChatLoading: boolean;
  
  // Export State
  exportFormats: ('markdown' | 'html' | 'pdf')[];
  
  // Actions
  setJobId: (id: string) => void;
  setSessionId: (id: string) => void;
  setJobStatus: (status: JobStatus) => void;
  setMarkdownContent: (content: string) => void;
  updateStepStatus: (status: StepCaptureStatus) => void;
  addChatMessage: (message: ChatMessage) => void;
  setChatLoading: (loading: boolean) => void;
  reset: () => void;
}

export const useManualStore = create<ManualStore>((set) => ({
  jobId: null,
  sessionId: null,
  jobStatus: 'idle',
  markdownContent: '',
  stepCount: 0,
  stepStatuses: [],
  chatHistory: [],
  isChatLoading: false,
  exportFormats: [],
  
  setJobId: (id) => set({ jobId: id }),
  setSessionId: (id) => set({ sessionId: id }),
  setJobStatus: (status) => set({ jobStatus: status }),
  setMarkdownContent: (content) => set({ markdownContent: content }),
  updateStepStatus: (status) => set((state) => ({
    stepStatuses: [...state.stepStatuses.filter(s => s.stepIndex !== status.stepIndex), status]
  })),
  addChatMessage: (message) => set((state) => ({
    chatHistory: [...state.chatHistory, message]
  })),
  setChatLoading: (loading) => set({ isChatLoading: loading }),
  reset: () => set({
    jobId: null, sessionId: null, jobStatus: 'idle',
    markdownContent: '', stepCount: 0, stepStatuses: [],
    chatHistory: [], isChatLoading: false,
  }),
}));
```

---

## 5. Core Components

### 5.1 ScriptInputForm

The entry point for the user workflow. Collects script text, target URL, and optional credentials.

```typescript
// src/components/input/ScriptInputForm.tsx

interface ScriptInputFormProps {
  onSubmit: (data: GenerateRequest) => void;
  isLoading: boolean;
}

interface GenerateRequest {
  script: string;
  targetUrl: string;
  credentials?: { username: string; password: string };
  options: {
    outputFormats: ('markdown' | 'html' | 'pdf')[];
    language: string;
  };
}
```

**Key Behaviors:**
- The credential fields use `type="password"` with no autocomplete.
- Submitting the form clears the credential fields from the React component state immediately after the API call is dispatched.
- The "Generate Manual" button is disabled while `isLoading` is true.

### 5.2 SplitScreen & EditorPane

The split-screen editor uses a resizable two-pane layout. The left pane hosts Monaco Editor; the right pane renders the live Markdown preview.

```typescript
// src/components/editor/SplitScreen.tsx

interface SplitScreenProps {
  leftPane: React.ReactNode;   // <EditorPane />
  rightPane: React.ReactNode;  // <PreviewPane />
  defaultSplit?: number;       // Percentage (0-100), default: 50
}
```

**EditorPane Configuration:**

```typescript
// src/components/editor/EditorPane.tsx
import Editor from '@monaco-editor/react';

const editorOptions = {
  language: 'markdown',
  theme: 'vs-dark',            // Dark theme — matches DocuAgent UI
  wordWrap: 'on',
  minimap: { enabled: false }, // Disable minimap for narrow pane
  fontSize: 14,
  lineNumbers: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,       // Auto-resize with pane resizing
};
```

### 5.3 ScreenshotImage

Each screenshot in the preview is wrapped in a `ScreenshotImage` component that enables click-to-replace and click-to-recapture interactions.

```typescript
// src/components/editor/ScreenshotImage.tsx

interface ScreenshotImageProps {
  src: string;
  alt: string;
  stepIndex: number;
  jobId: string;
  onRecapture: (stepIndex: number) => void;
  onReplace: (stepIndex: number, file: File) => void;
}
```

On click, the component renders an action overlay:
- **🔄 Re-Capture** — triggers `POST /api/v1/recapture/{job_id}/{step_index}`
- **📁 Upload Replacement** — opens a file picker for manual image upload

### 5.4 ChatPanel

```typescript
// src/components/chat/ChatPanel.tsx

interface ChatPanelProps {
  sessionId: string;
  isVisible: boolean;
}
```

**Panel States:**
- **Hidden** — collapsed to right sidebar when not in use.
- **Visible** — slides in as a side panel overlay on the preview pane.
- **Loading** — "Agent is thinking..." indicator with animated dots.

---

## 6. API Integration Layer

All REST calls are made through a centralized Axios client:

```typescript
// src/api/client.ts

import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${import.meta.env.VITE_API_TOKEN}`,
  },
});

// Typed API functions
export const generateManual = (data: GenerateRequest) =>
  apiClient.post<GenerateResponse>('/generate', data);

export const sendChatMessage = (sessionId: string, data: ChatRequest) =>
  apiClient.post<ChatResponse>(`/chat/${sessionId}`, data);

export const triggerRecapture = (jobId: string, stepIndex: number) =>
  apiClient.post(`/recapture/${jobId}/${stepIndex}`);

export const getJobStatus = (jobId: string) =>
  apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);

export const downloadExport = (jobId: string, format: string) =>
  apiClient.get(`/export/${jobId}?format=${format}`, { responseType: 'blob' });

export const uploadReplacementScreenshot = (jobId: string, stepIndex: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post(`/jobs/${jobId}/assets/${stepIndex}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
```

---

## 7. SSE Stream Consumer

```typescript
// src/hooks/useSSEStream.ts

import { useEffect } from 'react';
import { useManualStore } from '../store/useManualStore';

export function useSSEStream(jobId: string | null) {
  const { setJobStatus, setMarkdownContent, updateStepStatus } = useManualStore();
  
  useEffect(() => {
    if (!jobId) return;
    
    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_BASE_URL}/stream/${jobId}`,
      { withCredentials: true }
    );
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleSSEEvent(data);
    };
    
    eventSource.onerror = () => {
      eventSource.close();
      setJobStatus('failed');
    };
    
    function handleSSEEvent(event: SSEEvent) {
      switch (event.type) {
        case 'pipeline_started':
          setJobStatus('analyzing');
          break;
        case 'script_analyzed':
          setJobStatus('capturing');
          break;
        case 'capture_progress':
          updateStepStatus({
            stepIndex: event.step_index,
            status: event.status === 'captured' ? 'captured' : 'fallback',
            error: event.error,
          });
          break;
        case 'draft_compiled':
          setJobStatus('reviewing');
          break;
        case 'document_ready':
          setMarkdownContent(event.markdown);
          setJobStatus('awaiting_input');
          break;
        case 'document_updated':
          setMarkdownContent(event.markdown);
          setJobStatus('awaiting_input');
          break;
        case 'job_failed':
          setJobStatus('failed');
          break;
      }
    }
    
    return () => eventSource.close();
  }, [jobId]);
}
```

---

## 8. WebSocket Chat Client

```typescript
// src/hooks/useWebSocket.ts

import { useEffect, useRef, useCallback } from 'react';
import { useManualStore } from '../store/useManualStore';

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const { addChatMessage, setMarkdownContent, setChatLoading } = useManualStore();
  
  useEffect(() => {
    if (!sessionId) return;
    
    const ws = new WebSocket(
      `wss://${import.meta.env.VITE_API_HOST}/api/v1/ws/chat/${sessionId}?token=${import.meta.env.VITE_API_TOKEN}`
    );
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'agent_response') {
        addChatMessage({ role: 'assistant', content: data.content, ... });
        setMarkdownContent(data.updated_markdown);
        setChatLoading(false);
      }
    };
    
    // Heartbeat to keep connection alive
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
    
    return () => {
      clearInterval(heartbeat);
      ws.close();
    };
  }, [sessionId]);
  
  const sendMessage = useCallback((message: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    addChatMessage({ role: 'user', content: message, ... });
    setChatLoading(true);
    
    wsRef.current.send(JSON.stringify({
      type: 'user_message',
      content: message,
      timestamp: new Date().toISOString(),
    }));
  }, []);
  
  return { sendMessage };
}
```

---

## 9. Monaco Editor Integration

### 9.1 Two-Way Binding with Zustand

```typescript
// src/components/editor/EditorPane.tsx
import Editor from '@monaco-editor/react';
import { useManualStore } from '../../store/useManualStore';

export function EditorPane() {
  const { markdownContent, setMarkdownContent } = useManualStore();
  
  return (
    <Editor
      height="100%"
      defaultLanguage="markdown"
      value={markdownContent}
      onChange={(value) => setMarkdownContent(value ?? '')}
      options={editorOptions}
    />
  );
}
```

### 9.2 External Content Updates

When the SSE stream or chat agent updates `markdownContent` in the Zustand store, Monaco Editor reactively re-renders through the `value` prop. However, to avoid cursor jumping on external updates, use Monaco's `editor.setValue()` API only when the diff is substantial:

```typescript
// Diff-aware update to avoid cursor position disruption
useEffect(() => {
  if (editorRef.current && markdownContent !== editorRef.current.getValue()) {
    const position = editorRef.current.getPosition();
    editorRef.current.setValue(markdownContent);
    editorRef.current.setPosition(position); // Restore cursor position
  }
}, [markdownContent]);
```

---

## 10. Export Flow

```typescript
// src/hooks/useExport.ts

import { downloadExport } from '../api/client';
import { useManualStore } from '../store/useManualStore';

export function useExport() {
  const { jobId } = useManualStore();
  
  const handleExport = async (format: 'markdown' | 'html' | 'pdf') => {
    if (!jobId) return;
    
    const response = await downloadExport(jobId, format);
    const blob = new Blob([response.data]);
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `manual_${jobId}.${format === 'markdown' ? 'md' : format}`;
    link.click();
    
    URL.revokeObjectURL(url);
  };
  
  return { handleExport };
}
```

---

## 11. Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# .env.example

# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_HOST=localhost:8000
VITE_API_TOKEN=your_api_token_here

# Feature Flags
VITE_ENABLE_PDF_EXPORT=true
VITE_ENABLE_WEBSOCKET_CHAT=true
VITE_MAX_SCRIPT_LENGTH=10000

# UI Configuration
VITE_EDITOR_THEME=vs-dark
VITE_DEFAULT_LANGUAGE=en
```

> ⚠️ **Warning:** Never commit `.env` files containing real API tokens to version control. Use environment-specific CI/CD secrets management.

---

## 12. Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/docuagent-frontend.git
cd docuagent-frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env
# Edit .env with local API URL and token

# 4. Start development server (HMR enabled)
npm run dev
# Application available at http://localhost:5173

# 5. Run type checking
npm run type-check

# 6. Build for production
npm run build

# 7. Preview production build
npm run preview
```

**Vite Configuration:**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',   // Proxy API calls to FastAPI in dev
      '/assets': 'http://localhost:8000', // Proxy screenshot assets
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
});
```

---

## 13. Component API Reference

### ProgressBar

```typescript
interface ProgressBarProps {
  jobStatus: JobStatus;
  stepStatuses: StepCaptureStatus[];
  totalSteps: number;
}
```

### ExportBar

```typescript
interface ExportBarProps {
  jobId: string;
  availableFormats: ('markdown' | 'html' | 'pdf')[];
  isJobComplete: boolean;
}
```

### ChatMessage

```typescript
interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isLoading?: boolean;
}
```

### StepStatus Badge Colors

| Status | Color | Tailwind Class |
|--------|-------|---------------|
| `pending` | Gray | `bg-gray-400` |
| `captured` | Green | `bg-green-500` |
| `fallback` | Amber | `bg-amber-500` |
| `error` | Red | `bg-red-500` |

---

*← Previous: [Browser Automation Engine](./05_browser_automation_engine.md)*  
*→ Next: [Deployment & Operations Guide](./07_deployment_operations.md)*

---

*Document ID: DOC-006 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
