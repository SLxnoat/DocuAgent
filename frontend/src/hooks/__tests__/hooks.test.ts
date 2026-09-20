import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useGenerate } from "../useGenerate";
import { useExport } from "../useExport";
import { useManualStore } from "@/store/useManualStore";
import * as apiClient from "@/api/client";

describe("useGenerate", () => {
  beforeEach(() => {
    useManualStore.getState().reset();
    vi.clearAllMocks();
  });

  it("submits generation request and updates store on success", async () => {
    vi.spyOn(apiClient, "generateManual").mockResolvedValueOnce({
      data: { job_id: "job-abc", session_id: "sess-xyz" },
    } as any);

    const { result } = renderHook(() => useGenerate());

    await act(async () => {
      await result.current.submit({
        script: "Test workflow script for manual",
        target_url: "https://staging.app",
      });
    });

    const state = useManualStore.getState();
    expect(state.jobId).toBe("job-abc");
    expect(state.sessionId).toBe("sess-xyz");
    expect(state.jobStatus).toBe("queued");
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles submission failure gracefully", async () => {
    vi.spyOn(apiClient, "generateManual").mockRejectedValueOnce(
      new Error("Validation failed"),
    );

    const { result } = renderHook(() => useGenerate());

    await act(async () => {
      await result.current.submit({
        script: "Short",
        target_url: "invalid",
      });
    });

    const state = useManualStore.getState();
    expect(state.jobStatus).toBe("failed");
    expect(result.current.error).toBe("Validation failed");
  });
});

describe("useExport", () => {
  beforeEach(() => {
    useManualStore.getState().reset();
    vi.clearAllMocks();
  });

  it("downloads export file when jobId is set", async () => {
    useManualStore.getState().setJobId("job-123");

    vi.spyOn(apiClient, "downloadExport").mockResolvedValueOnce({
      data: new Blob(["# Markdown Manual"]),
    } as any);

    // Mock URL.createObjectURL and URL.revokeObjectURL
    const createObjectURL = vi.fn().mockReturnValue("blob:test");
    const revokeObjectURL = vi.fn();
    window.URL.createObjectURL = createObjectURL;
    window.URL.revokeObjectURL = revokeObjectURL;

    const { result } = renderHook(() => useExport());

    await act(async () => {
      await result.current.handleExport("markdown");
    });

    expect(apiClient.downloadExport).toHaveBeenCalledWith(
      "job-123",
      "markdown",
    );
    expect(createObjectURL).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });
});
