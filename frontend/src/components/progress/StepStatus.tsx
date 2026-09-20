import { CheckCircle2, Clock, AlertTriangle, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { CaptureStatus } from "@/types";

interface StepStatusProps {
  stepIndex: number;
  status: CaptureStatus;
  error?: string;
}

export function StepStatus({ stepIndex, status, error }: StepStatusProps) {
  const getBadgeConfig = () => {
    switch (status) {
      case "captured":
        return {
          variant: "success" as const,
          icon: CheckCircle2,
          label: "Captured",
        };
      case "fallback":
        return {
          variant: "warning" as const,
          icon: AlertTriangle,
          label: "Fallback",
        };
      case "error":
        return {
          variant: "destructive" as const,
          icon: XCircle,
          label: "Failed",
        };
      case "pending":
      default:
        return {
          variant: "secondary" as const,
          icon: Clock,
          label: "Pending",
        };
    }
  };

  const { variant, icon: Icon, label } = getBadgeConfig();

  const badgeElement = (
    <Badge variant={variant} className="gap-1.5 py-1 px-2.5 font-mono text-xs">
      <Icon className="h-3.5 w-3.5 shrink-0" />
      <span>
        Step {stepIndex}: {label}
      </span>
    </Badge>
  );

  if (error) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="cursor-help inline-block">{badgeElement}</div>
          </TooltipTrigger>
          <TooltipContent className="max-w-xs text-xs">
            <p className="font-semibold text-destructive-foreground">
              Warning / Error
            </p>
            <p>{error}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return badgeElement;
}
