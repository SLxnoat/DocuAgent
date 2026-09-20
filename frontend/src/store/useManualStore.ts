import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { JobStatus, StepCaptureStatus, ChatMessage } from "@/types";

interface ManualStore {
  // ── Session ────────────────────────────────────────────────────────────────
  jobId: string | null;
  sessionId: string | null;
  jobStatus: JobStatus;

  // ── Document ───────────────────────────────────────────────────────────────
  markdownContent: string;

  // ── Progress ───────────────────────────────────────────────────────────────
  stepCount: number;
  stepStatuses: StepCaptureStatus[];

  // ── Chat ───────────────────────────────────────────────────────────────────
  chatHistory: ChatMessage[];
  isChatLoading: boolean;
  isChatVisible: boolean;

  // ── Actions ────────────────────────────────────────────────────────────────
  setJobId: (id: string) => void;
  setSessionId: (id: string) => void;
  setJobStatus: (status: JobStatus) => void;
  setMarkdownContent: (content: string) => void;
  setStepCount: (count: number) => void;
  updateStepStatus: (status: StepCaptureStatus) => void;
  addChatMessage: (message: ChatMessage) => void;
  updateLastAssistantMessage: (content: string) => void;
  setChatLoading: (loading: boolean) => void;
  setChatVisible: (visible: boolean) => void;
  reset: () => void;
}

const initialState = {
  jobId: null,
  sessionId: null,
  jobStatus: "idle" as JobStatus,
  markdownContent: "",
  stepCount: 0,
  stepStatuses: [] as StepCaptureStatus[],
  chatHistory: [] as ChatMessage[],
  isChatLoading: false,
  isChatVisible: false,
};

export const useManualStore = create<ManualStore>()(
  devtools(
    (set) => ({
      ...initialState,

      setJobId: (id) => set({ jobId: id }, false, "setJobId"),
      setSessionId: (id) => set({ sessionId: id }, false, "setSessionId"),
      setJobStatus: (status) =>
        set({ jobStatus: status }, false, "setJobStatus"),
      setMarkdownContent: (content) =>
        set({ markdownContent: content }, false, "setMarkdownContent"),
      setStepCount: (count) => set({ stepCount: count }, false, "setStepCount"),

      updateStepStatus: (status) =>
        set(
          (state) => ({
            stepStatuses: [
              ...state.stepStatuses.filter(
                (s) => s.stepIndex !== status.stepIndex,
              ),
              status,
            ].sort((a, b) => a.stepIndex - b.stepIndex),
          }),
          false,
          "updateStepStatus",
        ),

      addChatMessage: (message) =>
        set(
          (state) => ({ chatHistory: [...state.chatHistory, message] }),
          false,
          "addChatMessage",
        ),

      updateLastAssistantMessage: (content) =>
        set(
          (state) => {
            const history = [...state.chatHistory];
            const lastIdx = history.map((m) => m.role).lastIndexOf("assistant");
            if (lastIdx >= 0) {
              history[lastIdx] = {
                ...history[lastIdx],
                content,
                isLoading: false,
              };
            }
            return { chatHistory: history };
          },
          false,
          "updateLastAssistantMessage",
        ),

      setChatLoading: (loading) =>
        set({ isChatLoading: loading }, false, "setChatLoading"),
      setChatVisible: (visible) =>
        set({ isChatVisible: visible }, false, "setChatVisible"),

      reset: () => set(initialState, false, "reset"),
    }),
    { name: "ManualStore" },
  ),
);
