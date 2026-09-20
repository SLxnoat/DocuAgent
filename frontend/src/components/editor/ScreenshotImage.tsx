import { useState, useRef } from "react";
import { Camera, Upload, Loader2, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { triggerRecapture, uploadReplacementScreenshot } from "@/api/client";
import { useManualStore } from "@/store/useManualStore";

interface ScreenshotImageProps {
  src: string;
  alt: string;
  stepIndex?: number;
}

export function ScreenshotImage({ src, alt, stepIndex }: ScreenshotImageProps) {
  const { jobId } = useManualStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isHovered, setIsHovered] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isRecapturing, setIsRecapturing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Derive stepIndex from src if not provided (e.g. /assets/job/step_002.png -> 2)
  let resolvedStep = stepIndex;
  if (resolvedStep === undefined) {
    const match = src.match(/step_(\d+)\.png/i);
    if (match) resolvedStep = parseInt(match[1], 10);
  }

  const handleRecapture = async () => {
    if (!jobId || resolvedStep === undefined) return;
    setIsRecapturing(true);
    setActionMessage(null);
    try {
      await triggerRecapture(jobId, resolvedStep);
      setActionMessage(
        "Re-capture task queued! Playwright will update this screenshot.",
      );
    } catch (err) {
      setActionMessage("Failed to trigger re-capture.");
    } finally {
      setIsRecapturing(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !jobId || resolvedStep === undefined) return;

    setIsUploading(true);
    setActionMessage(null);
    try {
      await uploadReplacementScreenshot(jobId, resolvedStep, file);
      setActionMessage("Screenshot uploaded successfully!");
    } catch (err) {
      setActionMessage("Failed to upload replacement screenshot.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      className="relative my-4 inline-block group rounded-lg overflow-hidden border shadow-sm max-w-full"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <img
        src={src}
        alt={alt}
        className="max-h-[480px] w-auto object-contain bg-muted/20 cursor-pointer"
        onClick={() => setIsDialogOpen(true)}
        loading="lazy"
      />

      {/* Floating Action Overlay on Hover */}
      {isHovered && resolvedStep !== undefined && (
        <div className="absolute top-2 right-2 flex items-center gap-1.5 p-1 bg-background/90 backdrop-blur-sm border rounded-md shadow-md">
          <Button
            size="sm"
            variant="secondary"
            className="h-7 px-2 text-xs gap-1"
            onClick={handleRecapture}
            disabled={isRecapturing}
          >
            {isRecapturing ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Camera className="h-3.5 w-3.5 text-brand" />
            )}
            Re-Capture
          </Button>

          <Button
            size="sm"
            variant="secondary"
            className="h-7 px-2 text-xs gap-1"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Upload className="h-3.5 w-3.5 text-brand" />
            )}
            Replace
          </Button>

          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>
      )}

      {/* Lightbox / Action Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-4xl w-[95vw]">
          <DialogHeader>
            <DialogTitle className="text-sm font-mono flex items-center gap-2">
              <ImageIcon className="h-4 w-4 text-brand" />
              {alt || `Screenshot (Step ${resolvedStep ?? "Unknown"})`}
            </DialogTitle>
            <DialogDescription>
              Inspect high-resolution capture or manage this asset.
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col items-center justify-center p-2 bg-muted/20 rounded-md overflow-hidden">
            <img
              src={src}
              alt={alt}
              className="max-h-[65vh] w-auto object-contain rounded"
            />
          </div>

          {actionMessage && (
            <div className="p-2 text-xs rounded bg-muted text-center font-medium">
              {actionMessage}
            </div>
          )}

          {resolvedStep !== undefined && (
            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={handleRecapture}
                disabled={isRecapturing}
              >
                {isRecapturing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Camera className="h-4 w-4 text-brand" />
                )}
                Re-take Screenshot with Playwright
              </Button>

              <Button
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4 text-brand" />
                )}
                Upload Custom Image
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
