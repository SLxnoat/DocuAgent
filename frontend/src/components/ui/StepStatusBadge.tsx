import * as React from "react";
import { useManualStore, type StepStatus } from "@/store/useManualStore";
import { CheckCircle2, Clock, AlertTriangle, XCircle } from "lucide-react";

const stepStatusConfig: Record<
  StepStatus,
  { label: string; bg: string; text: string; icon: React.ReactNode }
> = {
  pending: {
    label: "Pending",
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-600 dark:text-gray-300",
    icon: <Clock className="h-3 w-3 animate-spin text-gray-500" />,
  },
  captured: {
    label: "Captured",
    bg: "bg-emerald-50 dark:bg-emerald-950/40",
    text: "text-emerald-700 dark:text-emerald-300",
    icon: (
      <CheckCircle2 className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
    ),
  },
  fallback: {
    label: "Fallback",
    bg: "bg-amber-50 dark:bg-amber-950/40",
    text: "text-amber-700 dark:text-amber-300",
    icon: (
      <AlertTriangle className="h-3 w-3 text-amber-600 dark:text-amber-400" />
    ),
  },
  error: {
    label: "Error",
    bg: "bg-red-50 dark:bg-red-950/40",
    text: "text-red-700 dark:text-red-300",
    icon: <XCircle className="h-3 w-3 text-red-600 dark:text-red-400" />,
  },
};

interface StepStatusBadgeProps {
  stepIndex: number;
}

export const StepStatusBadge: React.FC<StepStatusBadgeProps> = ({
  stepIndex,
}) => {
  const { stepStatuses, stepErrors } = useManualStore();
  const status: StepStatus = stepStatuses[stepIndex] || "pending";
  const config = stepStatusConfig[status] || stepStatusConfig.pending;
  const errorMsg = stepErrors[stepIndex];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border border-transparent shadow-xs transition-colors ${config.bg} ${config.text}`}
      title={errorMsg ? `Step ${stepIndex + 1}: ${errorMsg}` : undefined}
    >
      {config.icon}
      <span>
        Step {stepIndex + 1}: {config.label}
      </span>
    </span>
  );
};
