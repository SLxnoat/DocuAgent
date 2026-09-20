import { useState } from "react";
import { downloadExport } from "@/api/client";
import { useManualStore } from "@/store/useManualStore";
import type { ExportFormat } from "@/types";

export function useExport() {
  const { jobId } = useManualStore();
  const [isExporting, setIsExporting] = useState<ExportFormat | null>(null);

  const handleExport = async (format: ExportFormat) => {
    if (!jobId) return;
    setIsExporting(format);
    try {
      const response = await downloadExport(jobId, format);
      const ext = format === "markdown" ? "md" : format;
      const filename = `manual_${jobId}.${ext}`;
      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export download failed:", err);
    } finally {
      setIsExporting(null);
    }
  };

  return { handleExport, isExporting };
}
