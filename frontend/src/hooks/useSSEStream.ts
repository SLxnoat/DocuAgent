import { useEffect, useRef } from "react";
import { useManualStore } from "@/store/useManualStore";
import type { SSEEvent } from "@/types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export function useSSEStream(jobId: string | null) {
  const store = useManualStore();
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!jobId) return;

    // Close any previous stream
    esRef.current?.close();

    const es = new EventSource(`${API_BASE}/stream/${jobId}`);
    esRef.current = es;

    es.onmessage = ({ data }: MessageEvent) => {
      let event: SSEEvent;
      try {
        event = JSON.parse(data);
      } catch {
        return;
      }

      switch (event.type) {
        case "pipeline_started":
          store.setJobStatus("analyzing");
          break;

        case "script_analyzed":
          store.setJobStatus("capturing");
          if (event.step_count) store.setStepCount(event.step_count);
          break;

        case "capture_progress":
          if (event.step_index != null) {
            store.updateStepStatus({
              stepIndex: event.step_index,
              status: event.status === "captured" ? "captured" : "fallback",
              error: event.error,
            });
          }
          break;

        case "capture_complete":
          break;

        case "draft_compiled":
          store.setJobStatus("compiling");
          break;

        case "quality_review_started":
          store.setJobStatus("reviewing");
          break;

        case "quality_approved":
          break;

        case "document_ready":
        case "document_updated":
          if (event.markdown) {
            store.setMarkdownContent(event.markdown);
          }
          store.setJobStatus("awaiting_input");
          break;

        case "job_failed":
          store.setJobStatus("failed");
          break;
      }
    };

    es.onerror = () => {
      if (es.readyState === EventSource.CLOSED) {
        store.setJobStatus("failed");
      }
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [jobId]);
}
