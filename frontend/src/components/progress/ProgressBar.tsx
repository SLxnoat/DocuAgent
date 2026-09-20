import { Progress } from "@/components/ui/progress";
import type { JobStatus } from "@/types";

interface ProgressBarProps {
  status: JobStatus;
  stepCount: number;
  capturedCount: number;
}

export function ProgressBar({
  status,
  stepCount,
  capturedCount,
}: ProgressBarProps) {
  const calculateProgress = (): number => {
    switch (status) {
      case "idle":
        return 0;
      case "queued":
        return 5;
      case "analyzing":
        return 15;
      case "capturing":
        if (stepCount > 0) {
          const captureShare = (capturedCount / stepCount) * 55;
          return Math.min(15 + captureShare, 70);
        }
        return 25;
      case "compiling":
        return 75;
      case "reviewing":
        return 90;
      case "awaiting_input":
      case "refining":
      case "completed":
        return 100;
      case "failed":
        return 100;
      default:
        return 0;
    }
  };

  const progressPercent = calculateProgress();

  return (
    <div className="w-full space-y-2">
      <Progress value={progressPercent} className="h-2.5 bg-muted" />
    </div>
  );
}
