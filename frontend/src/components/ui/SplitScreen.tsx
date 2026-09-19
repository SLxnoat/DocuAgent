import * as React from "react";
import { useState, useRef, useEffect } from "react";
import { MonacoEditor } from "./MonacoEditor";
import { PreviewPane } from "./PreviewPane";
import { useManualStore } from "@/store/useManualStore";
import { Code, Eye, Copy, Check, Clock } from "lucide-react";

interface SplitScreenProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export const SplitScreen: React.FC<SplitScreenProps> = ({
  value,
  onChange,
  className,
}) => {
  const { viewLayout, showToast } = useManualStore();
  const [splitPosition, setSplitPosition] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startX = useRef<number>(0);
  const startPos = useRef<number>(0);

  const handleDragStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    startX.current = e.clientX;
    startPos.current = splitPosition;
  };

  useEffect(() => {
    const handleDragMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;
      const containerRect = containerRef.current.getBoundingClientRect();
      const deltaX = e.clientX - startX.current;
      const deltaPercent = (deltaX / containerRect.width) * 100;
      const newPos = Math.max(
        20,
        Math.min(80, startPos.current + deltaPercent),
      );
      setSplitPosition(newPos);
    };

    const handleDragEnd = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener("mousemove", handleDragMove);
      window.addEventListener("mouseup", handleDragEnd);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }

    return () => {
      window.removeEventListener("mousemove", handleDragMove);
      window.removeEventListener("mouseup", handleDragEnd);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isDragging]);

  const handleCopyMarkdown = async () => {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      showToast("Markdown copied to clipboard!", "success");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showToast("Failed to copy to clipboard", "error");
    }
  };

  const lineCount = value ? value.split("\n").length : 0;
  const wordCount = value
    ? value.trim().split(/\s+/).filter(Boolean).length
    : 0;
  const readingTime = Math.max(1, Math.ceil(wordCount / 200));

  const showEditor = viewLayout === "split" || viewLayout === "editor";
  const showPreview = viewLayout === "split" || viewLayout === "preview";

  return (
    <div
      ref={containerRef}
      className={`relative flex h-full w-full overflow-hidden bg-gray-100 dark:bg-gray-900 select-none ${
        className || ""
      }`}
    >
      {/* Left pane: Monaco Editor */}
      {showEditor && (
        <div
          className={`flex flex-col h-full overflow-hidden border-r border-gray-200 dark:border-gray-800 select-text ${
            viewLayout === "editor" ? "w-full" : ""
          }`}
          style={
            viewLayout === "split" ? { width: `${splitPosition}%` } : undefined
          }
        >
          <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50/90 dark:bg-gray-800/90 border-gray-200 dark:border-gray-800 text-xs text-gray-600 dark:text-gray-300 shrink-0">
            <div className="flex items-center gap-2 font-semibold">
              <Code className="h-3.5 w-3.5 text-blue-500" />
              <span>Markdown Source</span>
              {lineCount > 0 && (
                <span className="text-[11px] text-gray-400 font-normal">
                  ({lineCount} lines)
                </span>
              )}
            </div>

            <button
              onClick={handleCopyMarkdown}
              disabled={!value}
              className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors disabled:opacity-40"
              title="Copy raw markdown to clipboard"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 text-emerald-500" />
                  <span className="text-emerald-600 dark:text-emerald-400">
                    Copied!
                  </span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>

          <div className="flex-1 min-h-0 bg-white dark:bg-gray-900">
            <MonacoEditor value={value} onChange={onChange} />
          </div>
        </div>
      )}

      {/* Splitter bar (only visible in split mode) */}
      {viewLayout === "split" && (
        <div
          className={`w-1.5 hover:w-2 cursor-col-resize bg-gray-200 dark:bg-gray-700 hover:bg-blue-500 transition-all z-20 flex items-center justify-center shrink-0 ${
            isDragging ? "bg-blue-600 w-2" : ""
          }`}
          onMouseDown={handleDragStart}
          title="Drag to resize panes"
        />
      )}

      {/* Right pane: Live Preview */}
      {showPreview && (
        <div
          className={`flex flex-col h-full overflow-hidden select-text flex-1 ${
            viewLayout === "preview" ? "w-full" : ""
          }`}
          style={
            viewLayout === "split"
              ? { width: `${100 - splitPosition}%` }
              : undefined
          }
        >
          <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50/90 dark:bg-gray-800/90 border-gray-200 dark:border-gray-800 text-xs text-gray-600 dark:text-gray-300 shrink-0">
            <div className="flex items-center gap-2 font-semibold">
              <Eye className="h-3.5 w-3.5 text-emerald-500" />
              <span>Live Document Preview</span>
            </div>

            {wordCount > 0 && (
              <div className="flex items-center gap-1 text-[11px] text-gray-400">
                <Clock className="h-3 w-3" />
                <span>~{readingTime} min read</span>
              </div>
            )}
          </div>

          <div className="flex-1 min-h-0 bg-white dark:bg-gray-900 overflow-y-auto">
            <PreviewPane value={value} />
          </div>
        </div>
      )}
    </div>
  );
};
