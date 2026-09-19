import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor to attach auth token
apiClient.interceptors.request.use((config) => {
  const token =
    localStorage.getItem("api_token") || import.meta.env.VITE_API_TOKEN;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface GenerateRequest {
  script: string;
  target_url: string;
  credentials?: {
    username?: string;
    password?: string;
  };
  options?: {
    output_formats?: ("markdown" | "html" | "pdf")[];
    domain_hint?: string;
    language?: string;
  };
}

export interface GenerateResponse {
  job_id: string;
  session_id: string;
  status: string;
  estimated_duration_seconds?: number;
  stream_url?: string;
  created_at?: string;
}

export interface ChatResponse {
  session_id: string;
  response_message: string;
  updated_markdown: string;
  changes_summary?: Array<{
    section: string;
    change_type: string;
    description: string;
  }>;
  recapture_triggered?: boolean;
  recapture_step_index?: number | null;
  timestamp?: string;
}

export interface JobStatusResponse {
  job_id: string;
  session_id: string;
  status: string;
  step_count?: number;
  screenshots_captured?: number;
  screenshots_fallback?: number;
  quality_approved?: boolean;
  export_formats_available?: string[];
  created_at?: string;
  completed_at?: string;
  duration_seconds?: number;
}

export const generateManual = async (
  params: GenerateRequest,
): Promise<GenerateResponse> => {
  const response = await apiClient.post<GenerateResponse>("/generate", params);
  return response.data;
};

export const sendChatMessage = async (
  sessionId: string,
  params: {
    message: string;
    context?: { current_markdown?: string };
  },
): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>(
    `/chat/${sessionId}`,
    params,
  );
  return response.data;
};

export const triggerRecapture = async (
  jobId: string,
  stepIndex: number,
  options?: {
    selector_override?: string;
    custom_screenshot_path?: string;
  },
) => {
  const response = await apiClient.post(
    `/recapture/${jobId}/${stepIndex}`,
    options || {},
  );
  return response.data;
};

export const uploadReplacementScreenshot = async (
  jobId: string,
  stepIndex: number,
  file: File,
) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post(
    `/jobs/${jobId}/assets/${stepIndex}`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return response.data;
};

export const getJobStatus = async (
  jobId: string,
): Promise<JobStatusResponse> => {
  const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);
  return response.data;
};

export const downloadExport = async (
  jobId: string,
  format: "markdown" | "html" | "pdf",
): Promise<Blob> => {
  const response = await apiClient.get(`/export/${jobId}`, {
    params: { format },
    responseType: "blob",
  });
  return response.data;
};

export default apiClient;
