import * as React from "react";
import { useExport, type ExportFormat } from "@/hooks/useExport";
import { useManualStore } from "@/store/useManualStore";
import { Button } from "@/components/ui/button";
import {
  FileText,
  Code2,
  FileDown,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

interface ExportBarProps {
  className?: string;
}

export const ExportBar: React.FC<ExportBarProps> = ({ className }) => {
  const { jobId, jobStatus, markdownContent } = useManualStore();
  const { handleExport, exportingFormat, exportError, clearExportError } =
    useExport();

  const isReadyToExport =
    Boolean(jobId) &&
    Boolean(markdownContent) &&
    (jobStatus === "completed" ||
      jobStatus === "awaiting_input" ||
      jobStatus === "refining");

  const formats: Array<{
    id: ExportFormat;
    label: string;
    extension: string;
    icon: React.ReactNode;
  }> = [
    {
      id: "markdown",
      label: "Markdown",
      extension: ".md",
      icon: <FileText className="h-3.5 w-3.5" />,
    },
    {
      id: "html",
      label: "Standalone HTML",
      extension: ".html",
      icon: <Code2 className="h-3.5 w-3.5" />,
    },
    {
      id: "pdf",
      label: "Print PDF",
      extension: ".pdf",
      icon: <FileDown className="h-3.5 w-3.5" />,
    },
  ];

  return (
    <div
      className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-white dark:bg-gray-850 border-b border-gray-200 dark:border-gray-800 transition-colors ${
        className || ""
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Export Document:
        </span>
        {exportError && (
          <span className="inline-flex items-center gap-1 text-xs text-red-600 dark:text-red-400 font-medium">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>{exportError}</span>
            <button
              onClick={clearExportError}
              className="ml-1 underline cursor-pointer text-[11px]"
            >
              dismiss
            </button>
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {formats.map((fmt) => {
          const isCurrentExporting = exportingFormat === fmt.id;

          return (
            <Button
              key={fmt.id}
              variant="outline"
              size="sm"
              disabled={!isReadyToExport || exportingFormat !== null}
              onClick={() => handleExport(fmt.id)}
              className="h-8 text-xs flex items-center gap-1.5 border-gray-200 dark:border-gray-750 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-40"
              title={`Download as ${fmt.label} (${fmt.extension})`}
            >
              {isCurrentExporting ? (
                <RefreshCw className="h-3.5 w-3.5 animate-spin text-blue-600 dark:text-blue-400" />
              ) : (
                fmt.icon
              )}
              <span>
                {isCurrentExporting
                  ? `Building ${fmt.extension}...`
                  : fmt.label}
              </span>
            </Button>
          );
        })}
      </div>
    </div>
  );
};
