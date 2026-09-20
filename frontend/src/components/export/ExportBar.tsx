import { Download, FileText, Code2, FileCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useExport } from "@/hooks/useExport";
import { useManualStore } from "@/store/useManualStore";

export function ExportBar() {
  const { jobStatus } = useManualStore();
  const { handleExport, isExporting } = useExport();

  const isExportReady = ["awaiting_input", "refining", "completed"].includes(
    jobStatus,
  );

  return (
    <div className="flex items-center justify-between px-4 py-2.5 border rounded-lg bg-card shadow-sm select-none">
      <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
        <Download className="h-4 w-4 text-brand" />
        <span className="uppercase tracking-wider">
          Export Publication Formats:
        </span>
      </div>

      <div className="flex items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1.5 text-xs font-medium"
          onClick={() => handleExport("markdown")}
          disabled={!isExportReady || isExporting !== null}
        >
          {isExporting === "markdown" ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <FileText className="h-3.5 w-3.5 text-blue-500" />
          )}
          Markdown (.md)
        </Button>

        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1.5 text-xs font-medium"
          onClick={() => handleExport("html")}
          disabled={!isExportReady || isExporting !== null}
        >
          {isExporting === "html" ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Code2 className="h-3.5 w-3.5 text-orange-500" />
          )}
          HTML (.html)
        </Button>

        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1.5 text-xs font-medium"
          onClick={() => handleExport("pdf")}
          disabled={!isExportReady || isExporting !== null}
        >
          {isExporting === "pdf" ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <FileCheck className="h-3.5 w-3.5 text-emerald-500" />
          )}
          Print-Ready PDF (.pdf)
        </Button>
      </div>
    </div>
  );
}
