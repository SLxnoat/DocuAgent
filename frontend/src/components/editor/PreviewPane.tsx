import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { ScreenshotImage } from "./ScreenshotImage";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useManualStore } from "@/store/useManualStore";

export function PreviewPane() {
  const { markdownContent } = useManualStore();

  return (
    <div className="h-full w-full flex flex-col border rounded-lg overflow-hidden bg-card">
      <div className="flex items-center justify-between px-3 py-2 border-b bg-muted/40 text-xs font-mono text-muted-foreground select-none">
        <span className="font-semibold text-foreground">
          Live Document Preview
        </span>
        <span>HTML Render</span>
      </div>

      <ScrollArea className="flex-1 p-6">
        <article className="prose prose-slate dark:prose-invert max-w-none prose-headings:font-semibold prose-a:text-brand prose-img:rounded-md">
          {markdownContent ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                img: ({ src, alt }) => (
                  <ScreenshotImage src={src || ""} alt={alt || ""} />
                ),
              }}
            >
              {markdownContent}
            </ReactMarkdown>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground text-sm">
              <p>No document content generated yet.</p>
              <p className="text-xs mt-1">
                Start a generation job from the Studio.
              </p>
            </div>
          )}
        </article>
      </ScrollArea>
    </div>
  );
}
