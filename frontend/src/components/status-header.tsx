import * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useManualStore } from "@/store/useManualStore";
import { PlusCircle, RefreshCw, Sun, Moon, ChevronRight } from "lucide-react";

interface StatusHeaderProps {
  className?: string;
}

export const StatusHeader: React.FC<StatusHeaderProps> = ({ className }) => {
  const {
    jobStatus,
    jobId,
    darkMode,
    toggleDarkMode,
    activeNavView,
    setActiveNavView,
    reset,
  } = useManualStore();

  const handleNewManual = () => {
    reset();
    setActiveNavView("input");
  };

  const getStatusBadge = () => {
    if (!jobId) {
      return (
        <Badge
          variant="secondary"
          className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 font-medium"
        >
          Ready
        </Badge>
      );
    }
    switch (jobStatus) {
      case "completed":
        return (
          <Badge variant="success" className="text-xs font-semibold">
            Completed
          </Badge>
        );
      case "failed":
        return (
          <Badge variant="destructive" className="text-xs font-semibold">
            Failed
          </Badge>
        );
      case "awaiting_input":
        return (
          <Badge variant="warning" className="text-xs font-semibold">
            HITL Ready
          </Badge>
        );
      default:
        return (
          <Badge
            variant="default"
            className="flex items-center gap-1.5 text-xs font-semibold bg-blue-600 text-white"
          >
            <RefreshCw className="h-3 w-3 animate-spin" />
            <span className="capitalize">{jobStatus || "Processing"}</span>
          </Badge>
        );
    }
  };

  const viewTitles: Record<string, string> = {
    dashboard: "Dashboard",
    input: "Workflow Studio",
    editor: "Manual Workspace",
    monitor: "Pipeline Monitor",
    settings: "Preferences",
  };

  return (
    <header
      className={`border-b bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 px-4 sm:px-6 py-2.5 transition-colors shrink-0 select-none ${
        className || ""
      }`}
    >
      <div className="flex items-center justify-between gap-3 w-full">
        {/* Left: Logo & Breadcrumbs */}
        <div className="flex items-center space-x-3">
          <div
            onClick={() => setActiveNavView("dashboard")}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="h-7 w-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-black text-xs shadow-xs group-hover:scale-105 transition-transform">
              D
            </div>
            <span className="text-sm font-black tracking-tight text-gray-900 dark:text-gray-100 hidden sm:inline">
              DocuAgent{" "}
              <span className="text-blue-600 dark:text-blue-400 font-medium">
                AI
              </span>
            </span>
          </div>

          <div className="h-4 w-px bg-gray-200 dark:bg-gray-700 hidden sm:block" />

          {/* Breadcrumb Context */}
          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 font-medium">
            <ChevronRight className="h-3.5 w-3.5 text-gray-400" />
            <span className="text-gray-800 dark:text-gray-200 font-semibold">
              {viewTitles[activeNavView] || "Workspace"}
            </span>
          </div>
        </div>

        {/* Center/Right: Job status badge & action buttons */}
        <div className="flex items-center space-x-2.5">
          {/* Active Status Badge */}
          {getStatusBadge()}

          {/* New Manual Button */}
          <Button
            size="sm"
            onClick={handleNewManual}
            className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white font-semibold gap-1.5 shadow-xs"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            <span className="hidden md:inline">New Manual</span>
          </Button>

          {/* Theme Toggle Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleDarkMode}
            className="h-8 w-8 p-0 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
            title={darkMode ? "Switch to Light theme" : "Switch to Dark theme"}
          >
            {darkMode ? (
              <Sun className="h-4 w-4 text-amber-400" />
            ) : (
              <Moon className="h-4 w-4 text-gray-600" />
            )}
          </Button>
        </div>
      </div>
    </header>
  );
};
