import { useState, useCallback } from "react";
import { downloadExport } from "@/api/client";
import { useManualStore } from "@/store/useManualStore";

export type ExportFormat = "markdown" | "html" | "pdf";

export const useExport = () => {
  const { jobId, showToast } = useManualStore();
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(
    null,
  );
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExport = useCallback(
    async (format: ExportFormat) => {
      if (!jobId) {
        setExportError("No active job available to export.");
        return;
      }

      setExportingFormat(format);
      setExportError(null);
      showToast(`Preparing ${format.toUpperCase()} export…`, "info");

      try {
        const blob = await downloadExport(jobId, format);
        const url = window.URL.createObjectURL(blob);

        const extension = format === "markdown" ? "md" : format;
        const filename = `manual_${jobId.slice(0, 8)}.${extension}`;

        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        window.URL.revokeObjectURL(url);
        showToast(
          `${format.toUpperCase()} downloaded successfully!`,
          "success",
        );
      } catch (err: any) {
        console.error(`Export failed for format ${format}:`, err);
        const message =
          err?.response?.data?.error?.message ||
          `Failed to export as ${format.toUpperCase()}. Please ensure the manual generation is complete.`;
        setExportError(message);
        showToast(message, "error");
      } finally {
        setExportingFormat(null);
      }
    },
    [jobId, showToast],
  );

  return {
    handleExport,
    isExporting: exportingFormat !== null,
    exportingFormat,
    exportError,
    clearExportError: () => setExportError(null),
  };
};
