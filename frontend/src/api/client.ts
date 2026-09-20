import axios from "axios";
import type { GenerateRequest, GenerateResponse, ChatResponse } from "@/types";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${import.meta.env.VITE_API_TOKEN ?? ""}`,
  },
});

// Normalise error messages from backend error schema
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const backendMsg = err.response?.data?.error?.message;
    const errorCode = err.response?.data?.error?.code;
    const finalMsg = backendMsg ?? err.message;
    const error = new Error(finalMsg) as Error & {
      code?: string;
      status?: number;
    };
    error.code = errorCode;
    error.status = err.response?.status;
    return Promise.reject(error);
  },
);

// ── Typed API functions ───────────────────────────────────────────────────────

export const generateManual = (data: GenerateRequest) =>
  apiClient.post<GenerateResponse>("/generate", data);

export const sendChatMessage = (
  sessionId: string,
  message: string,
  currentMarkdown?: string,
) =>
  apiClient.post<ChatResponse>(`/chat/${sessionId}`, {
    message,
    context: currentMarkdown
      ? { current_markdown: currentMarkdown }
      : undefined,
  });

export const triggerRecapture = (
  jobId: string,
  stepIndex: number,
  selectorOverride?: string,
) =>
  apiClient.post(`/recapture/${jobId}/${stepIndex}`, {
    selector_override: selectorOverride ?? null,
  });

export const getJobStatus = (jobId: string) => apiClient.get(`/jobs/${jobId}`);

export const deleteJob = (jobId: string) => apiClient.delete(`/jobs/${jobId}`);

export const downloadExport = (
  jobId: string,
  format: "markdown" | "html" | "pdf",
) =>
  apiClient.get(`/export/${jobId}?format=${format}`, { responseType: "blob" });

export const uploadReplacementScreenshot = (
  jobId: string,
  stepIndex: number,
  file: File,
) => {
  const form = new FormData();
  form.append("file", file);
  return apiClient.post(`/jobs/${jobId}/assets/${stepIndex}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
