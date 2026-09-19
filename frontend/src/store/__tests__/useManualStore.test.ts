import { describe, it, expect, beforeEach } from "vitest";
import { useManualStore } from "../useManualStore";

describe("useManualStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useManualStore.getState().reset();
  });

  it("should have correct default initial state", () => {
    const state = useManualStore.getState();
    expect(state.jobId).toBeNull();
    expect(state.sessionId).toBeNull();
    expect(state.jobStatus).toBeNull();
    expect(state.markdownContent).toBe("");
    expect(state.stepStatuses).toEqual([]);
    expect(state.stepErrors).toEqual({});
    expect(state.chatHistory).toEqual([]);
    expect(state.darkMode).toBe(false);
    expect(state.viewLayout).toBe("split");
  });

  it("should update jobId, sessionId, and jobStatus", () => {
    const store = useManualStore.getState();
    store.setJobId("job-abc-123");
    store.setSessionId("sess-xyz-789");
    store.setJobStatus("analyzing");

    const updated = useManualStore.getState();
    expect(updated.jobId).toBe("job-abc-123");
    expect(updated.sessionId).toBe("sess-xyz-789");
    expect(updated.jobStatus).toBe("analyzing");
  });

  it("should update markdownContent", () => {
    const store = useManualStore.getState();
    const content = "# Sample Guide\n\nStep 1: Open app.";
    store.setMarkdownContent(content);

    expect(useManualStore.getState().markdownContent).toBe(content);
  });

  it("should manage step statuses and step errors", () => {
    const store = useManualStore.getState();

    // Update step 0 to captured
    store.updateStepStatus(0, "captured");
    expect(useManualStore.getState().stepStatuses[0]).toBe("captured");

    // Update step 1 to error with error message
    store.updateStepStatus(1, "error", "Selector button#submit not found");
    const state = useManualStore.getState();
    expect(state.stepStatuses[1]).toBe("error");
    expect(state.stepErrors[1]).toBe("Selector button#submit not found");

    // Reset step statuses
    store.resetStepStatuses();
    const afterReset = useManualStore.getState();
    expect(afterReset.stepStatuses).toEqual([]);
    expect(afterReset.stepErrors).toEqual({});
  });

  it("should append chat messages to history", () => {
    const store = useManualStore.getState();
    store.addChatMessage("user", "Can you make step 2 clearer?");
    store.addChatMessage(
      "assistant",
      "Sure, I have updated step 2 with more detail.",
    );

    const history = useManualStore.getState().chatHistory;
    expect(history.length).toBe(2);
    expect(history[0].role).toBe("user");
    expect(history[0].content).toBe("Can you make step 2 clearer?");
    expect(history[1].role).toBe("assistant");
    expect(history[1].content).toBe(
      "Sure, I have updated step 2 with more detail.",
    );
    expect(history[0].timestamp).toBeDefined();
  });

  it("should toggle dark mode", () => {
    const store = useManualStore.getState();
    expect(store.darkMode).toBe(false);

    store.toggleDarkMode();
    expect(useManualStore.getState().darkMode).toBe(true);

    store.toggleDarkMode();
    expect(useManualStore.getState().darkMode).toBe(false);
  });

  it("should switch view layout", () => {
    const store = useManualStore.getState();
    store.setViewLayout("editor");
    expect(useManualStore.getState().viewLayout).toBe("editor");

    store.setViewLayout("preview");
    expect(useManualStore.getState().viewLayout).toBe("preview");

    store.setViewLayout("split");
    expect(useManualStore.getState().viewLayout).toBe("split");
  });

  it("should reset all fields to initial defaults", () => {
    const store = useManualStore.getState();
    store.setJobId("job-temp");
    store.setMarkdownContent("# Test");
    store.setJobStatus("completed");
    store.addChatMessage("user", "Hello");

    store.reset();

    const resetState = useManualStore.getState();
    expect(resetState.jobId).toBeNull();
    expect(resetState.markdownContent).toBe("");
    expect(resetState.jobStatus).toBeNull();
    expect(resetState.chatHistory).toEqual([]);
  });
});
