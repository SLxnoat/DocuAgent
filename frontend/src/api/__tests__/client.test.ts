import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  apiClient,
  generateManual,
  sendChatMessage,
  triggerRecapture,
  getJobStatus,
  deleteJob,
  downloadExport,
  uploadReplacementScreenshot,
} from "../client";

vi.mock("axios", async () => {
  const actual = await vi.importActual("axios");
  const mockPost = vi.fn();
  const mockGet = vi.fn();
  const mockDelete = vi.fn();
  return {
    ...actual,
    default: {
      create: vi.fn(() => ({
        post: mockPost,
        get: mockGet,
        delete: mockDelete,
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: vi.fn(), eject: vi.fn() },
        },
      })),
    },
  };
});

describe("API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("generateManual calls POST /generate with expected body", async () => {
    const payload = {
      script: "Test workflow script longer than 10",
      target_url: "https://example.com",
    };
    const mockPost = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: { job_id: "job-123", session_id: "sess-456" },
    });

    const res = await generateManual(payload);
    expect(mockPost).toHaveBeenCalledWith("/generate", payload);
    expect(res.data.job_id).toBe("job-123");
  });

  it("sendChatMessage calls POST /chat/{sessionId} with message and context", async () => {
    const mockPost = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: {
        session_id: "sess-123",
        response_message: "Updated doc",
        updated_markdown: "# Updated",
        changes_summary: [],
        recapture_triggered: false,
        recapture_step_index: null,
        timestamp: "2026-09-20T12:00:00Z",
      },
    });

    const res = await sendChatMessage(
      "sess-123",
      "Make step 1 clear",
      "# Title",
    );
    expect(mockPost).toHaveBeenCalledWith("/chat/sess-123", {
      message: "Make step 1 clear",
      context: { current_markdown: "# Title" },
    });
    expect(res.data.response_message).toBe("Updated doc");
  });

  it("triggerRecapture calls POST /recapture/{jobId}/{stepIndex}", async () => {
    const mockPost = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: { job_id: "job-1", step_index: 2, status: "recapture_queued" },
    });

    const res = await triggerRecapture("job-1", 2, "#button-submit");
    expect(mockPost).toHaveBeenCalledWith("/recapture/job-1/2", {
      selector_override: "#button-submit",
    });
    expect(res.data.status).toBe("recapture_queued");
  });

  it("getJobStatus calls GET /jobs/{jobId}", async () => {
    const mockGet = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: { job_id: "job-1", status: "completed" },
    });

    const res = await getJobStatus("job-1");
    expect(mockGet).toHaveBeenCalledWith("/jobs/job-1");
    expect(res.data.status).toBe("completed");
  });

  it("deleteJob calls DELETE /jobs/{jobId}", async () => {
    const mockDelete = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({
      data: { message: "Job deleted" },
    });

    const res = await deleteJob("job-1");
    expect(mockDelete).toHaveBeenCalledWith("/jobs/job-1");
    expect(res.data.message).toBe("Job deleted");
  });

  it("downloadExport calls GET /export/{jobId}?format={fmt} with blob responseType", async () => {
    const mockGet = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: new Blob(["markdown"]),
    });

    await downloadExport("job-1", "pdf");
    expect(mockGet).toHaveBeenCalledWith("/export/job-1?format=pdf", {
      responseType: "blob",
    });
  });

  it("uploadReplacementScreenshot sends multipart/form-data", async () => {
    const mockPost = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: { message: "Uploaded" },
    });

    const file = new File(["image"], "step.png", { type: "image/png" });
    const res = await uploadReplacementScreenshot("job-1", 1, file);
    expect(mockPost).toHaveBeenCalledWith(
      "/jobs/job-1/assets/1",
      expect.any(FormData),
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    expect(res.data.message).toBe("Uploaded");
  });
});
