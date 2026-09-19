import * as React from "react";
import { useState, useRef } from "react";
import { useManualStore } from "@/store/useManualStore";
import { triggerRecapture, uploadReplacementScreenshot } from "@/api/client";
import { RefreshCw, Upload, Check, AlertCircle, Eye } from "lucide-react";

interface ScreenshotImageProps {
  src?: string;
  alt?: string;
  title?: string;
  className?: string;
}

export const ScreenshotImage: React.FC<ScreenshotImageProps> = ({
  src = "",
  alt = "",
  title = "",
  className,
}) => {
  const { jobId, updateStepStatus } = useManualStore();
  const [isRecapturing, setIsRecapturing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Extract step index from image src or alt text (e.g., "step_002.png" -> 2, "Step 3" -> 3)
  const extractStepIndex = (): number => {
    const srcMatch = src.match(/step_?(\d+)/i);
    if (srcMatch && srcMatch[1]) {
      return parseInt(srcMatch[1], 10);
    }
    const altMatch = alt.match(/step\s*(\d+)/i);
    if (altMatch && altMatch[1]) {
      return parseInt(altMatch[1], 10);
    }
    return 1;
  };

  const stepIndex = extractStepIndex();

  const handleRecapture = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!jobId) {
      setStatusMessage("No active job to recapture");
      setIsError(true);
      return;
    }

    setIsRecapturing(true);
    setStatusMessage("Triggering Playwright recapture...");
    setIsError(false);

    try {
      await triggerRecapture(jobId, stepIndex);
      setStatusMessage("Recapture queued!");
      updateStepStatus(stepIndex - 1, "pending");
      setTimeout(() => setStatusMessage(null), 3500);
    } catch (error: any) {
      console.error("Recapture error:", error);
      setStatusMessage(
        error?.response?.data?.error?.message || "Recapture failed",
      );
      setIsError(true);
      setTimeout(() => setStatusMessage(null), 4000);
    } finally {
      setIsRecapturing(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !jobId) return;

    setIsUploading(true);
    setStatusMessage("Uploading replacement...");
    setIsError(false);

    try {
      await uploadReplacementScreenshot(jobId, stepIndex, file);
      setStatusMessage("Screenshot replaced!");
      updateStepStatus(stepIndex - 1, "captured");
      setTimeout(() => setStatusMessage(null), 3000);
    } catch (error: any) {
      console.error("Upload screenshot error:", error);
      setStatusMessage(
        error?.response?.data?.error?.message || "Upload failed",
      );
      setIsError(true);
      setTimeout(() => setStatusMessage(null), 4000);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div
      className={`my-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/60 overflow-hidden shadow-xs transition-all group ${
        className || ""
      }`}
    >
      <div className="relative overflow-hidden bg-gray-900/5 dark:bg-gray-950/40">
        {src ? (
          <img
            src={src}
            alt={alt || `Step ${stepIndex} Screenshot`}
            title={title || alt}
            className="w-full max-h-[460px] object-contain mx-auto block cursor-pointer transition-transform duration-200 group-hover:scale-[1.01]"
            onClick={() => setShowPreviewModal(true)}
            loading="lazy"
          />
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
            <span>No screenshot available</span>
          </div>
        )}

        {/* Hover Action Overlay */}
        <div className="absolute top-2 right-2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-150 bg-black/70 backdrop-blur-sm p-1.5 rounded-lg">
          <button
            type="button"
            onClick={() => setShowPreviewModal(true)}
            className="p-1.5 text-white/90 hover:text-white rounded hover:bg-white/20 transition-colors"
            title="View Full Size"
          >
            <Eye className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={handleRecapture}
            disabled={isRecapturing}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white/90 hover:text-white rounded hover:bg-white/20 transition-colors disabled:opacity-50"
            title="Re-run browser automation for this step"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${isRecapturing ? "animate-spin" : ""}`}
            />
            <span>Recapture</span>
          </button>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white/90 hover:text-white rounded hover:bg-white/20 transition-colors disabled:opacity-50"
            title="Upload custom replacement screenshot"
          >
            <Upload
              className={`h-3.5 w-3.5 ${isUploading ? "animate-bounce" : ""}`}
            />
            <span>Replace</span>
          </button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* Footer info & status messages */}
      <div className="px-3.5 py-2 flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 bg-white/60 dark:bg-gray-850">
        <span className="font-medium truncate max-w-[60%]">
          {alt || `Step ${stepIndex} UI State`}
        </span>

        {statusMessage ? (
          <span
            className={`flex items-center gap-1 font-medium ${
              isError
                ? "text-red-600 dark:text-red-400"
                : "text-blue-600 dark:text-blue-400"
            }`}
          >
            {isError ? (
              <AlertCircle className="h-3.5 w-3.5" />
            ) : (
              <Check className="h-3.5 w-3.5" />
            )}
            <span>{statusMessage}</span>
          </span>
        ) : (
          <span className="text-gray-400 text-[11px]">
            Click image to inspect
          </span>
        )}
      </div>

      {/* Full-size preview modal */}
      {showPreviewModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer"
          onClick={() => setShowPreviewModal(false)}
        >
          <div
            className="relative max-w-5xl max-h-[90vh] bg-white dark:bg-gray-900 rounded-xl overflow-hidden shadow-2xl p-2"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center p-2 border-b border-gray-200 dark:border-gray-800">
              <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                {alt || `Step ${stepIndex} Screenshot`}
              </span>
              <button
                onClick={() => setShowPreviewModal(false)}
                className="text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 text-sm font-bold px-2 py-1"
              >
                ✕ Close
              </button>
            </div>
            <div className="p-2 overflow-auto max-h-[80vh]">
              <img
                src={src}
                alt={alt}
                className="w-full h-auto object-contain rounded"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
