import { useState } from "react";
import { generateManual } from "@/api/client";
import { useManualStore } from "@/store/useManualStore";
import type { GenerateRequest } from "@/types";

export function useGenerate() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const store = useManualStore();

  const submit = async (data: GenerateRequest) => {
    setIsLoading(true);
    setError(null);
    store.reset();

    try {
      const { data: res } = await generateManual(data);
      store.setJobId(res.job_id);
      store.setSessionId(res.session_id);
      store.setJobStatus("queued");
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Failed to start generation";
      setError(msg);
      store.setJobStatus("failed");
    } finally {
      setIsLoading(false);
    }
  };

  return { submit, isLoading, error };
}
