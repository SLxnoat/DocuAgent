import { create } from "zustand";
import { persist } from "zustand/middleware";

export type JobStatus =
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

export interface ManualStoreState {
  jobId: string | null;
  sessionId: string | null;
  jobStatus: JobStatus | null;
  markdownContent: string;
  stepStatuses: StepStatus[];
  chatHistory: Array<{
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
  }>;
  isChatLoading: boolean;
  exportFormats: string[]; // e.g., ['markdown', 'html', 'pdf']
  darkMode: boolean; // true for dark mode, false for light mode
  preferredOutputFormat: string; // e.g., 'markdown', 'html', 'pdf'
  defaultLanguage: string; // e.g., 'en', 'es', 'fr'

  // Action creators
  setJobId: (jobId: string) => void;
  setSessionId: (sessionId: string) => void;
  setJobStatus: (status: JobStatus) => void;
  setMarkdownContent: (content: string) => void;
  updateStepStatus: (stepIndex: number, status: StepStatus) => void;
  addChatMessage: (role: "user" | "assistant", content: string) => void;
  setChatLoading: (isLoading: boolean) => void;
  setExportFormats: (formats: string[]) => void;
  setDarkMode: (darkMode: boolean) => void;
  toggleDarkMode: () => void;
  setPreferredOutputFormat: (format: string) => void;
  setDefaultLanguage: (language: string) => void;
  reset: () => void;
}

export const useManualStore = create<ManualStoreState>()(
  persist(
    (set) => ({
      // Initial state
      jobId: null,
      sessionId: null,
      jobStatus: null,
      markdownContent: "",
      stepStatuses: [],
      chatHistory: [],
      isChatLoading: false,
      exportFormats: [],
      darkMode: false, // Start with light mode
      preferredOutputFormat: "markdown", // Default format
      defaultLanguage: "en", // Default language

      // Action creators
      setJobId: (jobId: string) => set({ jobId }),
      setSessionId: (sessionId: string) => set({ sessionId }),
      setJobStatus: (status: JobStatus) => set({ jobStatus: status }),
      setMarkdownContent: (content: string) =>
        set({ markdownContent: content }),
      updateStepStatus: (stepIndex: number, status: StepStatus) =>
        set((state) => {
          const newStepStatuses = [...state.stepStatuses];
          while (newStepStatuses.length <= stepIndex) {
            newStepStatuses.push("pending");
          }
          newStepStatuses[stepIndex] = status;
          return { stepStatuses: newStepStatuses };
        }),
      addChatMessage: (role: "user" | "assistant", content: string) =>
        set((state) => ({
          chatHistory: [
            ...state.chatHistory,
            { role, content, timestamp: new Date() },
          ],
        })),
      setChatLoading: (isLoading: boolean) => set({ isChatLoading: isLoading }),
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
      reset: () =>
        set({
          jobId: null,
          sessionId: null,
          jobStatus: null,
          markdownContent: "",
          stepStatuses: [],
          chatHistory: [],
          isChatLoading: false,
          exportFormats: [],
          darkMode: false,
          preferredOutputFormat: "markdown",
          defaultLanguage: "en",
        }),
    }),
    {
      name: "docuagent-settings", // name of the item in localStorage
      getStorage: () => localStorage, // (optional) by default, 'localStorage' is used
      // Optional: specify which parts of the state to persist
      // We'll persist the settings but not the session-specific data
      partialize: (state) => ({
        darkMode: state.darkMode,
        preferredOutputFormat: state.preferredOutputFormat,
        defaultLanguage: state.defaultLanguage,
      }),
    },
  ),
);
