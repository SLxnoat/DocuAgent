import { describe, it, expect, beforeEach } from "vitest";
import { useManualStore } from "../useManualStore";

describe("useManualStore", () => {
  beforeEach(() => {
    useManualStore.getState().reset();
  });

  it("initializes with default values", () => {
    const state = useManualStore.getState();
    expect(state.jobId).toBeNull();
    expect(state.sessionId).toBeNull();
    expect(state.jobStatus).toBe("idle");
    expect(state.markdownContent).toBe("");
    expect(state.stepCount).toBe(0);
    expect(state.stepStatuses).toEqual([]);
    expect(state.chatHistory).toEqual([]);
    expect(state.isChatLoading).toBe(false);
    expect(state.isChatVisible).toBe(false);
  });

  it("sets job and session IDs", () => {
    useManualStore.getState().setJobId("job-1");
    useManualStore.getState().setSessionId("sess-1");

    const state = useManualStore.getState();
    expect(state.jobId).toBe("job-1");
    expect(state.sessionId).toBe("sess-1");
  });

  it("updates job status and markdown content", () => {
    useManualStore.getState().setJobStatus("compiling");
    useManualStore.getState().setMarkdownContent("# Header");

    const state = useManualStore.getState();
    expect(state.jobStatus).toBe("compiling");
    expect(state.markdownContent).toBe("# Header");
  });

  it("updates step statuses sorting by stepIndex", () => {
    useManualStore
      .getState()
      .updateStepStatus({ stepIndex: 2, status: "pending" });
    useManualStore
      .getState()
      .updateStepStatus({ stepIndex: 1, status: "captured" });
    useManualStore
      .getState()
      .updateStepStatus({ stepIndex: 2, status: "captured" });

    const state = useManualStore.getState();
    expect(state.stepStatuses).toHaveLength(2);
    expect(state.stepStatuses[0]).toEqual({ stepIndex: 1, status: "captured" });
    expect(state.stepStatuses[1]).toEqual({ stepIndex: 2, status: "captured" });
  });

  it("handles chat messages and updates last assistant message", () => {
    useManualStore.getState().addChatMessage({
      id: "1",
      role: "user",
      content: "Hello",
      timestamp: "2026-09-20T10:00:00Z",
    });
    useManualStore.getState().addChatMessage({
      id: "2",
      role: "assistant",
      content: "",
      timestamp: "2026-09-20T10:00:01Z",
      isLoading: true,
    });

    useManualStore.getState().updateLastAssistantMessage("Hi there!");

    const state = useManualStore.getState();
    expect(state.chatHistory).toHaveLength(2);
    expect(state.chatHistory[1].content).toBe("Hi there!");
    expect(state.chatHistory[1].isLoading).toBe(false);
  });

  it("toggles chat visibility and loading state", () => {
    useManualStore.getState().setChatVisible(true);
    useManualStore.getState().setChatLoading(true);

    expect(useManualStore.getState().isChatVisible).toBe(true);
    expect(useManualStore.getState().isChatLoading).toBe(true);
  });

  it("resets store to initial state", () => {
    useManualStore.getState().setJobId("job-999");
    useManualStore.getState().setJobStatus("completed");
    useManualStore.getState().reset();

    const state = useManualStore.getState();
    expect(state.jobId).toBeNull();
    expect(state.jobStatus).toBe("idle");
  });
});
