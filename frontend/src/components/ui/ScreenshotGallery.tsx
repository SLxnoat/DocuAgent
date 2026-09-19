import * as React from "react";
import { useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import { ScreenshotImage } from "./ScreenshotImage";
import {
  Camera,
  RefreshCw,
  ZoomIn,
  X,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { Button } from "./button";

export const ScreenshotGallery: React.FC = () => {
  const {
    jobId,
    stepStatuses,
    stepErrors,
    addChatMessage,
    setTyping,
    setChatLoading,
  } = useManualStore();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  if (!jobId || stepStatuses.length === 0) {
    return (
      <div className="p-12 text-center text-gray-400 dark:text-gray-500">
        <Camera className="h-10 w-10 mx-auto mb-3 opacity-40 text-blue-500" />
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          No Screenshot Assets Captured Yet
        </h3>
        <p className="text-xs mt-1 max-w-sm mx-auto">
          Screenshots captured by Agent 2 (Playwright Visual Capturer) will be
          rendered here with dynamic highlight effects.
        </p>
      </div>
    );
  }

  const handleRecapture = (stepIndex: number) => {
    const prompt = `Please re-capture the screenshot for step ${
      stepIndex + 1
    }.`;
    addChatMessage("user", prompt);
    setChatLoading(true);
    setTyping(true);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Camera className="h-4 w-4 text-blue-500" />
            <span>Visual Evidence & Screenshot Assets</span>
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {stepStatuses.length} interaction steps tracked for job{" "}
            <code className="text-[11px] font-mono">
              {jobId.slice(0, 16)}...
            </code>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {stepStatuses.map((status, index) => {
          const stepNum = index + 1;
          const formattedIndex = String(index).padStart(3, "0");
          const assetUrl = `/assets/${jobId}/step_${formattedIndex}.png`;
          const errorMsg = stepErrors[index];

          return (
            <div
              key={index}
              className="group rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xs hover:shadow-md transition-all flex flex-col"
            >
              {/* Header */}
              <div className="px-3.5 py-2.5 bg-gray-50 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between text-xs">
                <span className="font-bold text-gray-800 dark:text-gray-200">
                  Step {stepNum}
                </span>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                    status === "captured"
                      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300"
                      : status === "fallback"
                        ? "bg-amber-100 text-amber-800 dark:bg-amber-950/70 dark:text-amber-300"
                        : status === "error"
                          ? "bg-red-100 text-red-800 dark:bg-red-950/70 dark:text-red-300"
                          : "bg-blue-100 text-blue-800 dark:bg-blue-950/70 dark:text-blue-300"
                  }`}
                >
                  {status === "captured" && <CheckCircle className="h-3 w-3" />}
                  {status === "error" && <AlertCircle className="h-3 w-3" />}
                  <span>{status}</span>
                </span>
              </div>

              {/* Image Preview Container */}
              <div className="relative aspect-video bg-gray-100 dark:bg-gray-900 overflow-hidden flex items-center justify-center">
                <ScreenshotImage
                  src={assetUrl}
                  alt={`Step ${stepNum} screenshot`}
                  title={`Step ${stepNum}`}
                  className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-300"
                />

                {/* Hover overlay for zoom */}
                <div
                  onClick={() => setSelectedImage(assetUrl)}
                  className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
                >
                  <Button
                    size="sm"
                    variant="secondary"
                    className="h-8 gap-1.5 text-xs bg-white/90 text-gray-900 hover:bg-white dark:bg-gray-800/90 dark:text-white"
                  >
                    <ZoomIn className="h-3.5 w-3.5" />
                    <span>Enlarge</span>
                  </Button>
                </div>
              </div>

              {/* Footer action bar */}
              <div className="p-3 bg-white dark:bg-gray-850 mt-auto border-t border-gray-100 dark:border-gray-800 flex items-center justify-between gap-2">
                <span className="text-[11px] text-gray-400 font-mono truncate">
                  step_{formattedIndex}.png
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRecapture(index)}
                  className="h-7 px-2 text-[11px] text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/50 gap-1"
                  title="Ask Agent 5 to re-capture this step"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>Re-capture</span>
                </Button>
              </div>

              {errorMsg && (
                <div className="px-3 py-1.5 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-[10px] border-t border-red-100 dark:border-red-900/50 truncate">
                  {errorMsg}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Enlarge Zoom Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div
            className="relative max-w-5xl w-full bg-white dark:bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border border-gray-200 dark:border-gray-800"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-700 dark:text-gray-200">
                High-Resolution Asset Preview
              </span>
              <button
                onClick={() => setSelectedImage(null)}
                className="p-1 rounded-md text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-4 bg-gray-950 flex items-center justify-center max-h-[80vh] overflow-auto">
              <img
                src={selectedImage}
                alt="Enlarged screenshot"
                className="max-h-full max-w-full rounded-lg object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
