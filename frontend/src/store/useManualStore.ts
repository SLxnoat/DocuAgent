import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type JobStatus =
  | "idle"
  | "queued"
  | "analyzing"
  | "capturing"
  | "compiling"
  | "reviewing"
  | "awaiting_input"
  | "refining"
  | "completed"
  | "failed"
  | "cancelled";

export type StepStatus = "pending" | "captured" | "fallback" | "error";

export type ViewLayout = "split" | "editor" | "preview";

export type NavView = "dashboard" | "input" | "editor" | "monitor" | "settings";

export interface ChatMessageItem {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date | string;
}

export interface ToastNotification {
  id: string;
  text: string;
  type: "info" | "success" | "error";
}

export interface SSEEventLogItem {
  id: string;
  timestamp: string;
  type: string;
  payload: Record<string, unknown>;
}

export interface SavedManual {
  id: string;
  title: string;
  jobId: string;
  targetUrl: string;
  markdownContent: string;
  stepCount: number;
  wordCount: number;
  createdAt: string;
  updatedAt: string;
  status: JobStatus;
}

export interface QualityAuditReport {
  overall_pass: boolean;
  summary: string;
  completeness: { score: number; feedback: string };
  screenshot_coverage: { score: number; feedback: string };
  tone_consistency: { score: number; feedback: string };
  logical_sequencing: { score: number; feedback: string };
}

export interface ManualStoreState {
  // Navigation & Primary App State
  activeNavView: NavView;
  jobId: string | null;
  sessionId: string | null;
  jobStatus: JobStatus | null;
  markdownContent: string;
  targetUrl: string;
  rawScript: string;
  documentTitle: string;

  // Multi-Agent Pipeline & Capture State
  stepStatuses: StepStatus[];
  stepErrors: Record<number, string>;
  eventsLog: SSEEventLogItem[];
  qualityAudit: QualityAuditReport | null;

  // Interactive HITL Chat
  chatHistory: ChatMessageItem[];
  isChatLoading: boolean;
  isTyping: boolean;

  // Configuration & Preferences
  exportFormats: string[];
  darkMode: boolean;
  preferredOutputFormat: string;
  defaultLanguage: string;
  viewLayout: ViewLayout;
  toast: ToastNotification | null;

  // Saved Manuals Library
  savedManuals: SavedManual[];

  // Actions
  setActiveNavView: (view: NavView) => void;
  setJobId: (jobId: string | null) => void;
  setSessionId: (sessionId: string | null) => void;
  setJobStatus: (status: JobStatus | null) => void;
  setMarkdownContent: (content: string) => void;
  setTargetUrl: (url: string) => void;
  setRawScript: (script: string) => void;
  setDocumentTitle: (title: string) => void;
  updateStepStatus: (
    stepIndex: number,
    status: StepStatus,
    errorMessage?: string,
  ) => void;
  resetStepStatuses: () => void;
  addEventLog: (type: string, payload: Record<string, unknown>) => void;
  clearEventLogs: () => void;
  setQualityAudit: (audit: QualityAuditReport | null) => void;
  addChatMessage: (role: "user" | "assistant", content: string) => void;
  setChatLoading: (isLoading: boolean) => void;
  setTyping: (isTyping: boolean) => void;
  setExportFormats: (formats: string[]) => void;
  setDarkMode: (darkMode: boolean) => void;
  toggleDarkMode: () => void;
  setPreferredOutputFormat: (format: string) => void;
  setDefaultLanguage: (language: string) => void;
  setViewLayout: (layout: ViewLayout) => void;
  showToast: (text: string, type?: "info" | "success" | "error") => void;
  clearToast: () => void;
  saveCurrentManual: () => void;
  loadSavedManual: (manualId: string) => void;
  deleteSavedManual: (manualId: string) => void;
  reset: () => void;
}

let toastTimer: ReturnType<typeof setTimeout> | null = null;

const INITIAL_SAMPLE_MANUALS: SavedManual[] = [
  {
    id: "sample-manual-001",
    title: "SaaS Team Member Invitation & RBAC Guide",
    jobId: "demo-job-team-invite-01",
    targetUrl: "https://staging.app.example.com",
    markdownContent: `# SaaS Team Member Invitation & RBAC Guide

## Prerequisites
- Administrative user credentials with \`admin:write\` scopes.
- Active Internet connection and modern Chromium-based web browser.
- Valid email address for the invited team member.

## System Overview
This guide documents the enterprise workflow for provisioning new user accounts into an organization workspace with role-based access control (RBAC).

## Step-by-Step Walkthrough

### Step 1: Open Organization Settings
Navigate to the left-hand navigation sidebar and click on **Settings**, then choose **Team & Permissions**.

![Organization Settings](assets/demo-job-team-invite-01/step_000.png)

### Step 2: Click Invite Team Member
Click the primary blue button labeled **Invite Member** located in the top-right corner of the user roster table.

![Invite Button](assets/demo-job-team-invite-01/step_001.png)

### Step 3: Configure Role & Email
In the invitation modal, enter the user's corporate email \`jane.doe@example.com\`, select the **Developer** role, and click **Send Invitation**.

![Invite Modal](assets/demo-job-team-invite-01/step_002.png)

## Troubleshooting
- **Email Delivery Delay**: Confirmation emails are dispatched asynchronously via transactional worker queues. If not received within 5 minutes, verify spam folders or click *Resend Invitation*.
- **Role Permission Conflicts**: Verify your account has \`admin:write\` privileges.
`,
    stepCount: 3,
    wordCount: 194,
    createdAt: "2026-09-18T10:30:00Z",
    updatedAt: "2026-09-18T10:30:00Z",
    status: "completed",
  },
  {
    id: "sample-manual-002",
    title: "E-Commerce Express Checkout & Address Verification",
    jobId: "demo-job-checkout-02",
    targetUrl: "https://shop.example.com",
    markdownContent: `# E-Commerce Express Checkout & Address Verification

## Prerequisites
- Valid customer session with at least 1 item in the cart.
- Verified shipping address.

## System Overview
Standard user manual for finalizing a customer cart transaction using 1-Click express checkout.

## Step-by-Step Walkthrough

### Step 1: Review Shopping Bag
Click the shopping cart icon in the navigation bar to open the sliding drawer. Verify item quantities and order subtotal.

### Step 2: Proceed to Checkout
Click the primary **Proceed to Checkout** button to navigate to payment gateway.

### Step 3: Confirm Shipping & Place Order
Select saved shipping address, choose delivery speed, and click **Place Order**.

## Troubleshooting
- If payment fails, ensure 3D Secure verification window is permitted in browser pop-ups.
`,
    stepCount: 3,
    wordCount: 112,
    createdAt: "2026-09-19T14:15:00Z",
    updatedAt: "2026-09-19T14:15:00Z",
    status: "completed",
  },
];

export const useManualStore = create<ManualStoreState>()(
  persist(
    (set, get) => ({
      // Initial state
      activeNavView: "dashboard",
      jobId: null,
      sessionId: null,
      jobStatus: null,
      markdownContent: "",
      targetUrl: "",
      rawScript: "",
      documentTitle: "Untitled Manual",
      stepStatuses: [],
      stepErrors: {},
      eventsLog: [],
      qualityAudit: null,
      chatHistory: [],
      isChatLoading: false,
      isTyping: false,
      exportFormats: ["markdown", "html", "pdf"],
      darkMode: false,
      preferredOutputFormat: "markdown",
      defaultLanguage: "en",
      viewLayout: "split",
      toast: null,
      savedManuals: INITIAL_SAMPLE_MANUALS,

      // Navigation & Primary Actions
      setActiveNavView: (view: NavView) => set({ activeNavView: view }),
      setJobId: (jobId: string | null) => set({ jobId }),
      setSessionId: (sessionId: string | null) => set({ sessionId }),
      setJobStatus: (status: JobStatus | null) => set({ jobStatus: status }),
      setMarkdownContent: (content: string) => {
        // Automatically derive title from first markdown heading if available
        let title = get().documentTitle;
        const match = content.match(/^#\s+(.+)$/m);
        if (match && match[1]) {
          title = match[1].trim();
        }
        set({ markdownContent: content, documentTitle: title });
      },
      setTargetUrl: (url: string) => set({ targetUrl: url }),
      setRawScript: (script: string) => set({ rawScript: script }),
      setDocumentTitle: (title: string) => set({ documentTitle: title }),

      // Step & Event Actions
      updateStepStatus: (
        stepIndex: number,
        status: StepStatus,
        errorMessage?: string,
      ) =>
        set((state) => {
          if (stepIndex < 0) {
            return { stepStatuses: [], stepErrors: {} };
          }
          const newStepStatuses = [...state.stepStatuses];
          while (newStepStatuses.length <= stepIndex) {
            newStepStatuses.push("pending");
          }
          newStepStatuses[stepIndex] = status;

          const newStepErrors = { ...state.stepErrors };
          if (errorMessage) {
            newStepErrors[stepIndex] = errorMessage;
          } else {
            delete newStepErrors[stepIndex];
          }

          return {
            stepStatuses: newStepStatuses,
            stepErrors: newStepErrors,
          };
        }),
      resetStepStatuses: () => set({ stepStatuses: [], stepErrors: {} }),

      addEventLog: (type: string, payload: Record<string, unknown>) =>
        set((state) => ({
          eventsLog: [
            ...state.eventsLog.slice(-99), // Keep latest 100 events
            {
              id: `evt-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
              timestamp: new Date().toLocaleTimeString(),
              type,
              payload,
            },
          ],
        })),
      clearEventLogs: () => set({ eventsLog: [] }),

      setQualityAudit: (audit: QualityAuditReport | null) =>
        set({ qualityAudit: audit }),

      // Chat Actions
      addChatMessage: (role: "user" | "assistant", content: string) =>
        set((state) => ({
          chatHistory: [
            ...state.chatHistory,
            {
              id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
              role,
              content,
              timestamp: new Date(),
            },
          ],
        })),
      setChatLoading: (isLoading: boolean) => set({ isChatLoading: isLoading }),
      setTyping: (isTyping: boolean) => set({ isTyping }),

      // Preferences Actions
      setExportFormats: (formats: string[]) => set({ exportFormats: formats }),
      setDarkMode: (darkMode: boolean) => set({ darkMode }),
      toggleDarkMode: () =>
        set((state) => ({
          darkMode: !state.darkMode,
        })),
      setPreferredOutputFormat: (format: string) =>
        set({ preferredOutputFormat: format }),
      setDefaultLanguage: (language: string) =>
        set({ defaultLanguage: language }),
      setViewLayout: (layout: ViewLayout) => set({ viewLayout: layout }),

      // Toast Notification Actions
      showToast: (
        text: string,
        type: "info" | "success" | "error" = "info",
      ) => {
        if (toastTimer) clearTimeout(toastTimer);
        const toast = { id: `toast-${Date.now()}`, text, type };
        set({ toast });
        toastTimer = setTimeout(() => {
          set({ toast: null });
        }, 3500);
      },
      clearToast: () => {
        if (toastTimer) clearTimeout(toastTimer);
        set({ toast: null });
      },

      // Saved Manuals Actions
      saveCurrentManual: () => {
        const state = get();
        if (!state.markdownContent || !state.jobId) return;

        const words = state.markdownContent
          .trim()
          .split(/\s+/)
          .filter(Boolean).length;
        const manual: SavedManual = {
          id: `manual-${state.jobId}`,
          title: state.documentTitle || "Generated Manual",
          jobId: state.jobId,
          targetUrl: state.targetUrl,
          markdownContent: state.markdownContent,
          stepCount: state.stepStatuses.length || 1,
          wordCount: words,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          status: state.jobStatus || "completed",
        };

        const existingIndex = state.savedManuals.findIndex(
          (m) => m.id === manual.id || m.jobId === manual.jobId,
        );
        let updatedList: SavedManual[];
        if (existingIndex >= 0) {
          updatedList = [...state.savedManuals];
          updatedList[existingIndex] = manual;
        } else {
          updatedList = [manual, ...state.savedManuals];
        }

        set({ savedManuals: updatedList });
        state.showToast(
          "Manual successfully saved to your library!",
          "success",
        );
      },

      loadSavedManual: (manualId: string) => {
        const state = get();
        const manual = state.savedManuals.find((m) => m.id === manualId);
        if (!manual) return;

        set({
          jobId: manual.jobId,
          documentTitle: manual.title,
          markdownContent: manual.markdownContent,
          targetUrl: manual.targetUrl,
          jobStatus: manual.status,
          stepStatuses: Array(manual.stepCount).fill("captured"),
          activeNavView: "editor",
        });
        state.showToast(`Loaded "${manual.title}" into Editor`, "info");
      },

      deleteSavedManual: (manualId: string) => {
        set((state) => ({
          savedManuals: state.savedManuals.filter((m) => m.id !== manualId),
        }));
        get().showToast("Manual removed from library", "info");
      },

      // Global Reset
      reset: () =>
        set({
          jobId: null,
          sessionId: null,
          jobStatus: null,
          markdownContent: "",
          targetUrl: "",
          rawScript: "",
          documentTitle: "Untitled Manual",
          stepStatuses: [],
          stepErrors: {},
          eventsLog: [],
          qualityAudit: null,
          chatHistory: [],
          isChatLoading: false,
          isTyping: false,
          exportFormats: ["markdown", "html", "pdf"],
          viewLayout: "split",
          toast: null,
        }),
    }),
    {
      name: "docuagent-storage-v2",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        darkMode: state.darkMode,
        preferredOutputFormat: state.preferredOutputFormat,
        defaultLanguage: state.defaultLanguage,
        viewLayout: state.viewLayout,
        savedManuals: state.savedManuals,
      }),
    },
  ),
);
