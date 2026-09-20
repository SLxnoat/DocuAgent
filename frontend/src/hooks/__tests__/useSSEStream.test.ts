import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useSSEStream } from "../useSSEStream";
import { useManualStore } from "@/store/useManualStore";

describe("useSSEStream", () => {
  let mockEventSourceInstance: any;

  beforeEach(() => {
    useManualStore.getState().reset();

    mockEventSourceInstance = {
      close: vi.fn(),
      onmessage: null,
      onerror: null,
      readyState: 1,
    };

    (globalThis as any).EventSource = vi
      .fn()
      .mockImplementation(() => mockEventSourceInstance);
  });

  it("subscribes to stream URL and updates status on events", () => {
    renderHook(() => useSSEStream("job-999"));

    expect(globalThis.EventSource).toHaveBeenCalledWith(
      expect.stringContaining("/stream/job-999"),
    );

    // Simulate pipeline_started event
    mockEventSourceInstance.onmessage({
      data: JSON.stringify({ type: "pipeline_started", job_id: "job-999" }),
    });
    expect(useManualStore.getState().jobStatus).toBe("analyzing");

    // Simulate script_analyzed event
    mockEventSourceInstance.onmessage({
      data: JSON.stringify({ type: "script_analyzed", step_count: 4 }),
    });
    expect(useManualStore.getState().jobStatus).toBe("capturing");
    expect(useManualStore.getState().stepCount).toBe(4);

    // Simulate capture_progress event
    mockEventSourceInstance.onmessage({
      data: JSON.stringify({
        type: "capture_progress",
        step_index: 1,
        status: "captured",
      }),
    });
    expect(useManualStore.getState().stepStatuses).toHaveLength(1);
    expect(useManualStore.getState().stepStatuses[0].status).toBe("captured");

    // Simulate document_ready event
    mockEventSourceInstance.onmessage({
      data: JSON.stringify({
        type: "document_ready",
        markdown: "# Ready Manual",
      }),
    });
    expect(useManualStore.getState().jobStatus).toBe("awaiting_input");
    expect(useManualStore.getState().markdownContent).toBe("# Ready Manual");
  });

  it("closes EventSource on unmount", () => {
    const { unmount } = renderHook(() => useSSEStream("job-999"));
    unmount();
    expect(mockEventSourceInstance.close).toHaveBeenCalled();
  });
});
