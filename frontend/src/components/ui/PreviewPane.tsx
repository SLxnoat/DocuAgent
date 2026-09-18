import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ScreenshotImage } from "./ScreenshotImage";

interface PreviewPaneProps {
  value: string;
}

export const PreviewPane: React.FC<PreviewPaneProps> = ({ value }) => {
  return (
    <div className="h-full w-full p-4 overflow-y-auto">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // We can override the image component to use our ScreenshotImage
          image: ({ src, alt, title }) => {
            // Check if the image is a screenshot (maybe by a specific pattern in src or alt)
            // For now, we'll use ScreenshotImage for all images, but we might want to conditionally use it.
            // Alternatively, we can pass a prop to ScreenshotImage to indicate if it's editable.
            return <ScreenshotImage src={src} alt={alt} title={title} />;
          },
        }}
      >
        {value}
      </ReactMarkdown>
    </div>
  );
};
