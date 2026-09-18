import axios from "axios";

// Create axios instance with base URL from environment variable
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
});

// Add request interceptor to attach auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("api_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const generateManual = async (params: {
  script: string;
  target_url: string;
  credentials?: {
    username?: string;
    password?: string;
  };
}) => {
  const response = await apiClient.post("/generate", {
    script: params.script,
    target_url: params.target_url,
    credentials: params.credentials,
  });

  return response.data;
};

export default apiClient;
