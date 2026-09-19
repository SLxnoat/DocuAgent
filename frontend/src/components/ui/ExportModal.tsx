import * as React from "react";
import { useExport, type ExportFormat } from "@/hooks/useExport";
import { useManualStore } from "@/store/useManualStore";
import { Button } from "./button";
import {
  FileText,
  Code2,
  FileDown,
  X,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Download,
} from "lucide-react";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { documentTitle, markdownContent } = useManualStore();
  const { handleExport, exportingFormat, exportError } = useExport();

  if (!isOpen) return null;

  const formats: Array<{
    id: ExportFormat;
    title: string;
    description: string;
    badge: string;
    icon: React.ReactNode;
  }> = [
    {
      id: "pdf",
      title: "Print-Ready PDF Document",
      description:
        "WeasyPrint compiled A4 document with inline base64 graphics, headers, and footers.",
      badge: "Standard",
      icon: <FileDown className="h-6 w-6 text-red-500" />,
    },
    {
      id: "html",
      title: "Self-Contained HTML Manual",
      description:
        "Standalone HTML page with all stylesheet styles and screenshot images baked in.",
      badge: "Web Ready",
      icon: <Code2 className="h-6 w-6 text-blue-500" />,
    },
    {
      id: "markdown",
      title: "Raw Markdown Package",
      description:
        "GitHub-Flavored Markdown (GFM) formatted text with relative image references.",
      badge: "Developer",
      icon: <FileText className="h-6 w-6 text-emerald-500" />,
    },
  ];

  const wordCount = markdownContent.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="relative max-w-lg w-full bg-white dark:bg-gray-900 rounded-3xl overflow-hidden shadow-2xl border border-gray-200 dark:border-gray-800 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <Download className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-gray-900 dark:text-gray-100">
                Export User Documentation
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Select your preferred distribution packaging format.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Document Context Snapshot */}
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between text-xs">
          <span className="font-semibold text-gray-700 dark:text-gray-300 truncate max-w-[260px]">
            {documentTitle || "Generated User Manual"}
          </span>
          <span className="text-gray-400 text-[11px]">{wordCount} words</span>
        </div>

        {/* Format Selection List */}
        <div className="p-6 space-y-3">
          {exportError && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{exportError}</span>
            </div>
          )}

          {formats.map((fmt) => {
            const isExporting = exportingFormat === fmt.id;
            return (
              <div
                key={fmt.id}
                className="group p-4 rounded-2xl border border-gray-200 dark:border-gray-750 hover:border-blue-500 dark:hover:border-blue-500 bg-white dark:bg-gray-850 shadow-xs hover:shadow-md transition-all flex items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3.5">
                  <div className="mt-0.5 shrink-0">{fmt.icon}</div>
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
                        {fmt.title}
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                        {fmt.badge}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                      {fmt.description}
                    </p>
                  </div>
                </div>

                <Button
                  size="sm"
                  disabled={exportingFormat !== null}
                  onClick={async () => {
                    await handleExport(fmt.id);
                    if (!exportError) onClose();
                  }}
                  className="shrink-0 h-9 px-4 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white gap-1.5"
                >
                  {isExporting ? (
                    <>
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      <span>Building...</span>
                    </>
                  ) : (
                    <>
                      <Download className="h-3.5 w-3.5" />
                      <span>Export</span>
                    </>
                  )}
                </Button>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 dark:bg-gray-850 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between text-[11px] text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
            <span>High-resolution vector rendering</span>
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-7 text-xs"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
