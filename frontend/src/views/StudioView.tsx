import { useEffect } from "react";
import { PlusCircle, RotateCcw, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScriptInputForm } from "@/components/input/ScriptInputForm";
import { ProgressPanel } from "@/components/progress/ProgressPanel";
import { SplitScreen } from "@/components/editor/SplitScreen";
import { EditorPane } from "@/components/editor/EditorPane";
import { PreviewPane } from "@/components/editor/PreviewPane";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ExportBar } from "@/components/export/ExportBar";
import { useGenerate } from "@/hooks/useGenerate";
import { useSSEStream } from "@/hooks/useSSEStream";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useManualStore } from "@/store/useManualStore";
import { getAvailableModels } from "@/api/client";

export function StudioView() {
  const {
    jobId,
    sessionId,
    jobStatus,
    reset,
    selectedModel,
    setSelectedModel,
    setAvailableModels,
  } = useManualStore();
  const { submit, isLoading, error } = useGenerate();

  useEffect(() => {
    getAvailableModels()
      .then((res) => {
        if (res.data?.models?.length) {
          setAvailableModels(res.data.models);
          if (res.data.default_primary && selectedModel === "llama3.3:70b") {
            setSelectedModel(res.data.default_primary);
          }
        }
      })
      .catch(() => {
        // Fall back gracefully to preset models
      });
  }, [setAvailableModels, setSelectedModel, selectedModel]);

  // Active SSE stream for real-time pipeline events
  useSSEStream(jobId);

  // Active WebSocket/REST refinement connection
  const { sendMessage, isConnected } = useWebSocket(sessionId);

  const isFormVisible = jobStatus === "idle";
  const isProgressActive = [
    "queued",
    "analyzing",
    "capturing",
    "compiling",
    "reviewing",
    "failed",
  ].includes(jobStatus);
  const isEditorVisible = ["awaiting_input", "refining", "completed"].includes(
    jobStatus,
  );

  return (
    <div className="flex-1 flex flex-col h-full min-h-0 p-4 gap-3 overflow-hidden">
      {/* Top action bar when a document is in view */}
      {isEditorVisible && (
        <div className="flex items-center justify-between py-1 px-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm">
              Interactive Studio Workspace
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-500 font-medium">
              Human-in-the-Loop Active
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-brand/15 text-brand font-mono font-medium flex items-center gap-1">
              <Cpu className="h-3 w-3" /> {selectedModel}
            </span>
          </div>

          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
            onClick={reset}
          >
            <PlusCircle className="h-3.5 w-3.5" />
            New Manual
          </Button>
        </div>
      )}

      {/* 1. Workflow Input Form (Initial Screen) */}
      {isFormVisible && (
        <div className="flex-1 flex items-center justify-center overflow-y-auto p-4 scrollbar-thin">
          <ScriptInputForm
            onSubmit={submit}
            isLoading={isLoading}
            error={error}
          />
        </div>
      )}

      {/* 2. Generation Progress Stream */}
      {isProgressActive && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <ProgressPanel />
          {jobStatus === "failed" && (
            <Button variant="outline" className="mt-4 gap-2" onClick={reset}>
              <RotateCcw className="h-4 w-4" /> Start Over
            </Button>
          )}
        </div>
      )}

      {/* 3. Split-Screen Editor & Live HTML Preview */}
      {isEditorVisible && (
        <div className="flex-1 flex gap-3 min-h-0 overflow-hidden">
          <SplitScreen
            leftPane={<EditorPane />}
            rightPane={<PreviewPane />}
            defaultSplit={50}
          />
          <ChatPanel
            sessionId={sessionId}
            sendMessage={sendMessage}
            isConnected={isConnected}
          />
        </div>
      )}

      {/* 4. Bottom Export Bar */}
      {isEditorVisible && <ExportBar />}
    </div>
  );
}
