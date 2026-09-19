import * as React from "react";
import { useManualStore, type JobStatus } from "@/store/useManualStore";
import { StepStatusBadge } from "./StepStatusBadge";
import { RefreshCw, CheckCircle2, AlertCircle } from "lucide-react";

const jobStatusDescriptions: Record<
  JobStatus,
  { title: string; desc: string }
> = {
  idle: { title: "Ready", desc: "Awaiting new manual generation request." },
  queued: { title: "Job Queued", desc: "Dispatched to Celery task queue..." },
  analyzing: {
    title: "Analyzing Script (Agent 1)",
    desc: "Parsing workflow text into structured JSON interaction steps...",
  },
  capturing: {
    title: "Capturing Screenshots (Agent 2)",
    desc: "Playwright is executing actions & injecting DOM highlights...",
  },
  compiling: {
    title: "Compiling Markdown (Agent 3)",
    desc: "Writing technical documentation with embedded screenshots...",
  },
  reviewing: {
    title: "Quality Review (Agent 4)",
    desc: "Auditing completeness, layout consistency, and image validity...",
  },
  awaiting_input: {
    title: "Human-in-the-Loop Ready",
    desc: "Document draft ready. You can refine it via chat or manual edits.",
  },
  refining: {
    title: "Refining Manual (Agent 5)",
    desc: "Applying your conversational instructions to the document...",
  },
  completed: {
    title: "Completed",
    desc: "Documentation generation finished successfully.",
  },
  failed: {
    title: "Generation Failed",
    desc: "Pipeline encountered an error. Check logs or retry.",
  },
  cancelled: {
    title: "Job Cancelled",
    desc: "Execution was stopped by user.",
  },
};

const progressMap: Record<JobStatus, number> = {
  idle: 0,
  queued: 8,
  analyzing: 22,
  capturing: 50,
  compiling: 72,
  reviewing: 85,
  awaiting_input: 100,
  refining: 92,
  completed: 100,
  failed: 100,
  cancelled: 100,
};

export const ProgressBar: React.FC = () => {
  const { jobStatus, stepStatuses } = useManualStore();

  const currentStatus = jobStatus || "idle";
  const progress = progressMap[currentStatus] ?? 0;
  const statusInfo = jobStatusDescriptions[currentStatus] || {
    title: "Processing",
    desc: "Working on your manual...",
  };

  const capturedCount = stepStatuses.filter(
    (s) => s === "captured" || s === "fallback",
  ).length;
  const totalCount = stepStatuses.length;

  const isFinished =
    currentStatus === "completed" || currentStatus === "awaiting_input";
  const isFailed = currentStatus === "failed";

  return (
    <div className="bg-white dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-xs space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          {isFinished ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
          ) : isFailed ? (
            <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
          ) : (
            <RefreshCw className="h-5 w-5 text-blue-500 animate-spin shrink-0" />
          )}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {statusInfo.title}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {statusInfo.desc}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 self-end sm:self-auto">
          {totalCount > 0 && (
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
              Screenshots: {capturedCount} / {totalCount}
            </span>
          )}
          <span className="text-sm font-bold text-gray-700 dark:text-gray-200">
            {progress}%
          </span>
        </div>
      </div>

      {/* Progress track */}
      <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${
            isFailed
              ? "bg-red-500"
              : isFinished
                ? "bg-emerald-500"
                : "bg-gradient-to-r from-blue-500 to-indigo-600 animate-pulse"
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Per-step Badges */}
      {stepStatuses.length > 0 && (
        <div className="pt-2 border-t border-gray-100 dark:border-gray-700/60">
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
            Execution Steps:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {stepStatuses.map((_, idx) => (
              <StepStatusBadge key={idx} stepIndex={idx} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
