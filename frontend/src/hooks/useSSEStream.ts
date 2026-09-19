import { useEffect, useRef } from "react";
import { useManualStore, type StepStatus } from "@/store/useManualStore";
import { API_BASE_URL } from "@/api/client";

export const useSSEStream = (jobId: string | null) => {
  const {
    setJobStatus,
    setMarkdownContent,
    updateStepStatus,
    addChatMessage,
    setTyping,
    addEventLog,
    setQualityAudit,
    saveCurrentManual,
  } = useManualStore();

  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let eventSource: EventSource | null = null;
    let isMounted = true;

    const connectSSE = () => {
      const streamUrl = `${API_BASE_URL}/stream/${jobId}`;
      eventSource = new EventSource(streamUrl);

      eventSource.onopen = () => {
        console.log(`[SSE] Connected to stream for job ${jobId}`);
      };

      eventSource.onmessage = (event) => {
        try {
          if (!event.data || event.data.trim() === "") return;
          const data = JSON.parse(event.data);
          const eventType = data.type || data.event_type || "event";
          addEventLog(eventType, data);

          switch (data.type) {
            case "pipeline_started":
              setJobStatus("analyzing");
              break;

            case "script_analyzed":
              setJobStatus("capturing");
              if (typeof data.step_count === "number" && data.step_count > 0) {
                for (let i = 0; i < data.step_count; i++) {
                  updateStepStatus(i, "pending");
                }
              }
              break;

            case "capture_progress": {
              const rawIndex =
                data.step_index !== undefined
                  ? data.step_index
                  : data.stepIndex;
              const stepIdx =
                typeof rawIndex === "number"
                  ? rawIndex > 0
                    ? rawIndex - 1 // 1-based to 0-based
                    : 0
                  : 0;

              const status: StepStatus =
                data.status === "fallback"
                  ? "fallback"
                  : data.status === "error"
                    ? "error"
                    : "captured";

              updateStepStatus(stepIdx, status, data.error);
              setJobStatus("capturing");
              break;
            }

            case "capture_complete":
              setJobStatus("compiling");
              break;

            case "draft_compiled":
              setJobStatus("reviewing");
              break;

            case "quality_approved":
              setJobStatus("awaiting_input");
              if (data.feedback) {
                setQualityAudit(data.feedback);
              }
              break;

            case "document_ready":
            case "document_updated": {
              const markdown = data.markdown || data.content || "";
              if (markdown) {
                setMarkdownContent(markdown);
              }
              setJobStatus("awaiting_input");
              setTyping(false);
              saveCurrentManual();
              break;
            }

            case "job_failed":
              setJobStatus("failed");
              setTyping(false);
              break;

            case "chat_message":
              if (data.role && data.content) {
                addChatMessage(data.role, data.content);
              }
              break;

            case "typing_start":
              setTyping(true);
              break;

            case "typing_stop":
              setTyping(false);
              break;

            case "heartbeat":
            case "ping":
              // keepalive
              break;

            default:
              console.debug("[SSE] Unhandled event type:", data.type, data);
          }
        } catch (error) {
          console.error("[SSE] Error parsing event data:", error, event.data);
        }
      };

      eventSource.onerror = (err) => {
        console.warn("[SSE] Connection interrupted, scheduling retry...", err);
        if (eventSource) {
          eventSource.close();
        }

        // Reconnect after 3s if still mounted and job is not complete/failed
        if (isMounted) {
          retryTimeoutRef.current = setTimeout(() => {
            if (isMounted) {
              connectSSE();
            }
          }, 3000);
        }
      };
    };

    connectSSE();

    return () => {
      isMounted = false;
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
      if (eventSource) {
        eventSource.close();
      }
      setTyping(false);
    };
  }, [
    jobId,
    setJobStatus,
    setMarkdownContent,
    updateStepStatus,
    addChatMessage,
    setTyping,
    addEventLog,
    setQualityAudit,
    saveCurrentManual,
  ]);
};
