import * as React from "react";
import { useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import { MonacoEditor } from "@/components/ui/MonacoEditor";
import { PreviewPane } from "@/components/ui/PreviewPane";
import { ScreenshotGallery } from "@/components/ui/ScreenshotGallery";
import { QualityReportCard } from "@/components/ui/QualityReportCard";
import { ChatPanel } from "@/components/ui/ChatPanel";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { ExportModal } from "@/components/ui/ExportModal";
import {
  FileText,
  Eye,
  Camera,
  Award,
  Code2,
  Download,
  Save,
  Columns,
  Check,
  Copy,
  Clock,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export const EditorView: React.FC = () => {
  const {
    jobId,
    sessionId,
    jobStatus,
    documentTitle,
    setDocumentTitle,
    markdownContent,
    setMarkdownContent,
    targetUrl,
    viewLayout,
    setViewLayout,
    saveCurrentManual,
    showToast,
  } = useManualStore();

  const [activePreviewTab, setActivePreviewTab] = useState<
    "document" | "gallery" | "audit" | "raw"
  >("document");
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [copiedRaw, setCopiedRaw] = useState(false);

  const wordCount = markdownContent.trim().split(/\s+/).filter(Boolean).length;
  const readTimeMinutes = Math.max(1, Math.ceil(wordCount / 200));

  const handleCopyRaw = async () => {
    if (!markdownContent) return;
    try {
      await navigator.clipboard.writeText(markdownContent);
      setCopiedRaw(true);
      showToast("Markdown copied to clipboard!", "success");
      setTimeout(() => setCopiedRaw(false), 2000);
    } catch {
      showToast("Failed to copy markdown", "error");
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden bg-white dark:bg-gray-900">
      {/* Top Workspace Toolbar */}
      <div className="px-4 sm:px-6 py-2.5 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-850 flex flex-wrap items-center justify-between gap-3 shrink-0">
        {/* Title and Metadata */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="h-8 w-8 rounded-lg bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
            <FileText className="h-4 w-4" />
          </div>

          <div className="min-w-0">
            <input
              type="text"
              value={documentTitle}
              onChange={(e) => setDocumentTitle(e.target.value)}
              className="font-bold text-sm text-gray-900 dark:text-gray-100 bg-transparent border-b border-transparent hover:border-gray-300 dark:hover:border-gray-700 focus:border-blue-500 focus:outline-hidden px-0.5 max-w-[280px] sm:max-w-md truncate"
              placeholder="Untitled Manual"
            />
            <div className="flex items-center gap-2 text-[11px] text-gray-400">
              {targetUrl && (
                <span className="flex items-center gap-1 font-mono truncate max-w-[160px]">
                  <ExternalLink className="h-2.5 w-2.5" />
                  {targetUrl.replace(/^https?:\/\//, "")}
                </span>
              )}
              <span>•</span>
              <span>{wordCount} words</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="h-2.5 w-2.5" />
                {readTimeMinutes} min read
              </span>
            </div>
          </div>
        </div>

        {/* Workspace Controls */}
        <div className="flex items-center gap-2">
          {/* Layout Segmented Controls */}
          <div className="hidden sm:flex items-center bg-gray-100 dark:bg-gray-800 p-0.5 rounded-lg text-xs">
            <button
              onClick={() => setViewLayout("split")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                viewLayout === "split"
                  ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs"
                  : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
              }`}
              title="Split View (Editor + Live Preview)"
            >
              <Columns className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setViewLayout("editor")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                viewLayout === "editor"
                  ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs"
                  : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
              }`}
              title="Editor Only"
            >
              <Code2 className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setViewLayout("preview")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                viewLayout === "preview"
                  ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs"
                  : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
              }`}
              title="Preview Only"
            >
              <Eye className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="h-4 w-px bg-gray-200 dark:bg-gray-700 mx-1 hidden sm:block" />

          {/* Save to Library */}
          <Button
            size="sm"
            variant="outline"
            onClick={saveCurrentManual}
            disabled={!markdownContent}
            className="h-8 text-xs gap-1.5 border-gray-200 dark:border-gray-700"
            title="Save manual draft into local library"
          >
            <Save className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Save</span>
          </Button>

          {/* Export Dialog */}
          <Button
            size="sm"
            onClick={() => setIsExportModalOpen(true)}
            disabled={!markdownContent}
            className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white font-semibold gap-1.5 shadow-xs"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export</span>
          </Button>
        </div>
      </div>

      {/* Progress Bar Header (Visible while pipeline job is processing) */}
      {jobId && jobStatus !== null && jobStatus !== "completed" && (
        <div className="p-3 bg-gray-50 dark:bg-gray-900/60 border-b border-gray-200 dark:border-gray-800 shrink-0">
          <ProgressBar />
        </div>
      )}

      {/* Main Split / Unified Content Area */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        {/* Left: Monaco Editor */}
        {(viewLayout === "split" || viewLayout === "editor") && (
          <div
            className={`flex flex-col min-h-0 overflow-hidden border-r border-gray-200 dark:border-gray-800 ${
              viewLayout === "split" ? "w-1/2" : "w-full"
            }`}
          >
            <div className="px-4 py-2 bg-gray-50 dark:bg-gray-850 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 select-none">
              <span className="font-semibold uppercase tracking-wider text-[10px]">
                Markdown Source (Monaco)
              </span>
              <span className="font-mono text-[11px]">UTF-8 • GFM</span>
            </div>
            <div className="flex-1 min-h-0">
              <MonacoEditor
                value={markdownContent}
                onChange={setMarkdownContent}
                className="h-full w-full"
              />
            </div>
          </div>
        )}

        {/* Right: Multi-Tab Interactive Preview Pane */}
        {(viewLayout === "split" || viewLayout === "preview") && (
          <div
            className={`flex flex-col min-h-0 overflow-hidden bg-white dark:bg-gray-900 ${
              viewLayout === "split" ? "w-1/2" : "w-full"
            }`}
          >
            {/* Sub-Tabs Bar */}
            <div className="px-4 bg-gray-50 dark:bg-gray-850 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setActivePreviewTab("document")}
                  className={`px-3 py-2 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-all ${
                    activePreviewTab === "document"
                      ? "border-blue-600 text-blue-600 dark:text-blue-400"
                      : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Eye className="h-3.5 w-3.5" />
                  <span>Manual Preview</span>
                </button>

                <button
                  onClick={() => setActivePreviewTab("gallery")}
                  className={`px-3 py-2 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-all ${
                    activePreviewTab === "gallery"
                      ? "border-blue-600 text-blue-600 dark:text-blue-400"
                      : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Camera className="h-3.5 w-3.5" />
                  <span>Screenshot Assets</span>
                </button>

                <button
                  onClick={() => setActivePreviewTab("audit")}
                  className={`px-3 py-2 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-all ${
                    activePreviewTab === "audit"
                      ? "border-blue-600 text-blue-600 dark:text-blue-400"
                      : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Award className="h-3.5 w-3.5" />
                  <span>Quality Audit</span>
                </button>

                <button
                  onClick={() => setActivePreviewTab("raw")}
                  className={`px-3 py-2 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-all ${
                    activePreviewTab === "raw"
                      ? "border-blue-600 text-blue-600 dark:text-blue-400"
                      : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Code2 className="h-3.5 w-3.5" />
                  <span>Raw Markdown</span>
                </button>
              </div>

              {activePreviewTab === "raw" && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleCopyRaw}
                  className="h-7 text-xs gap-1 text-gray-500"
                >
                  {copiedRaw ? (
                    <Check className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                  <span>{copiedRaw ? "Copied" : "Copy"}</span>
                </Button>
              )}
            </div>

            {/* Tab Body */}
            <div className="flex-1 min-h-0 overflow-y-auto">
              {activePreviewTab === "document" && (
                <PreviewPane value={markdownContent} />
              )}
              {activePreviewTab === "gallery" && <ScreenshotGallery />}
              {activePreviewTab === "audit" && <QualityReportCard />}
              {activePreviewTab === "raw" && (
                <pre className="p-6 text-xs font-mono bg-gray-50 dark:bg-gray-950 text-gray-800 dark:text-gray-200 overflow-auto whitespace-pre-wrap leading-relaxed h-full">
                  {markdownContent || "No content available."}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Conversational Refiner (Agent 5 HITL Chat) */}
      {sessionId && (
        <div className="shrink-0">
          <ChatPanel sessionId={sessionId} />
        </div>
      )}

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />
    </div>
  );
};
