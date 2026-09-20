import { Loader2, CheckCircle2, AlertOctagon } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ProgressBar } from "./ProgressBar";
import { StepStatus } from "./StepStatus";
import { useManualStore } from "@/store/useManualStore";

export function ProgressPanel() {
  const { jobStatus, stepCount, stepStatuses, jobId } = useManualStore();

  const getStatusDescription = () => {
    switch (jobStatus) {
      case "queued":
        return "Job queued in background task queue...";
      case "analyzing":
        return "Agent 1 (Script Analyzer) parsing workflow steps & target selectors...";
      case "capturing":
        return "Agent 2 (Playwright) navigating staging UI and capturing highlighted elements...";
      case "compiling":
        return "Agent 3 (Technical Writer) drafting formatted markdown & layout...";
      case "reviewing":
        return "Agent 4 (Quality Verification) reviewing accuracy and layout coherence...";
      case "awaiting_input":
      case "completed":
        return "Document ready! You can now refine or export.";
      case "failed":
        return "Pipeline encountered a fatal error. Please review the script or target URL.";
      default:
        return "Preparing execution pipeline...";
    }
  };

  const capturedCount = stepStatuses.filter(
    (s) => s.status === "captured" || s.status === "fallback",
  ).length;

  const isCompleted =
    jobStatus === "awaiting_input" || jobStatus === "completed";
  const isFailed = jobStatus === "failed";

  return (
    <Card className="w-full max-w-4xl mx-auto border-border shadow-sm">
      <CardHeader className="py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isFailed ? (
              <div className="p-2 rounded-full bg-destructive/15 text-destructive">
                <AlertOctagon className="h-5 w-5" />
              </div>
            ) : isCompleted ? (
              <div className="p-2 rounded-full bg-emerald-500/15 text-emerald-500">
                <CheckCircle2 className="h-5 w-5" />
              </div>
            ) : (
              <div className="p-2 rounded-full bg-brand/15 text-brand">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            )}

            <div>
              <CardTitle className="text-base font-semibold">
                {isFailed
                  ? "Generation Failed"
                  : isCompleted
                    ? "Manual Compilation Complete"
                    : "Generating User Manual..."}
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">
                {getStatusDescription()}
              </p>
            </div>
          </div>

          {jobId && (
            <span className="font-mono text-[11px] text-muted-foreground px-2 py-1 bg-muted rounded">
              Job: {jobId.slice(0, 8)}...
            </span>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pt-0">
        <ProgressBar
          status={jobStatus}
          stepCount={stepCount}
          capturedCount={capturedCount}
        />

        {/* Step Status Badges Grid */}
        {stepCount > 0 && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span className="font-semibold uppercase tracking-wider">
                Step-by-Step UI Capture Progress
              </span>
              <span>
                {capturedCount} of {stepCount} steps resolved
              </span>
            </div>

            <div className="flex flex-wrap gap-2 pt-1 max-h-36 overflow-y-auto scrollbar-thin">
              {Array.from({ length: stepCount }, (_, i) => {
                const stepIdx = i + 1;
                const statusObj = stepStatuses.find(
                  (s) => s.stepIndex === stepIdx,
                );
                return (
                  <StepStatus
                    key={stepIdx}
                    stepIndex={stepIdx}
                    status={statusObj ? statusObj.status : "pending"}
                    error={statusObj?.error}
                  />
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
