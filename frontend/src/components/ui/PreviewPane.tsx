import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ScreenshotImage } from "./ScreenshotImage";

interface PreviewPaneProps {
  value: string;
}

const isSafeUrl = (url?: string): boolean => {
  if (!url) return false;
  const trimmed = url.trim().toLowerCase();
  if (
    trimmed.startsWith("javascript:") ||
    trimmed.startsWith("vbscript:") ||
    (trimmed.startsWith("data:") && !trimmed.startsWith("data:image/"))
  ) {
    return false;
  }
  return true;
};

export const PreviewPane: React.FC<PreviewPaneProps> = ({ value }) => {
  if (!value || value.trim() === "") {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400 dark:text-gray-500 p-8 text-center">
        <p className="text-base font-medium">No document compiled yet</p>
        <p className="text-xs mt-1 max-w-sm">
          Submit a workflow script to start generating steps and screenshots
          with DocuAgent AI.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full w-full p-8 overflow-y-auto bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <article className="prose prose-slate dark:prose-invert max-w-3xl mx-auto">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            img: ({ src, alt, title }) => {
              return (
                <ScreenshotImage
                  src={typeof src === "string" ? src : ""}
                  alt={alt || ""}
                  title={title || ""}
                />
              );
            },
            a: ({ href, children }) => {
              const safeHref = isSafeUrl(href) ? href : "#";
              return (
                <a
                  href={safeHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  {children}
                </a>
              );
            },
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-blue-500 pl-4 py-1.5 my-3 bg-blue-50/50 dark:bg-blue-950/25 rounded-r text-sm">
                {children}
              </blockquote>
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto my-4 border rounded-lg border-gray-200 dark:border-gray-800">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-800 text-sm">
                  {children}
                </table>
              </div>
            ),
          }}
        >
          {value}
        </ReactMarkdown>
      </article>
    </div>
  );
};
