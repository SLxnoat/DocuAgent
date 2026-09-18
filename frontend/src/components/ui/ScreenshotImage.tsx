import * as React from "react";
import { useManualStore } from "../store/useManualStore";
import { LucideIcons, Camera, Upload, X } from "lucide-react";

interface ScreenshotImageProps {
  src: string;
  alt?: string;
  title?: string;
}

export const ScreenshotImage: React.FC<ScreenshotImageProps> = ({
  src,
  alt = "",
  title = "",
}) => {
  const setMarkdownContent = useManualStore(
    (state) => state.setMarkdownContent,
  );
  const markdownContent = useManualStore((state) => state.markdownContent);

  const [previewSrc, setPreviewSrc] = useState<string>(src);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [webcamStream, setWebcamStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isRecapturing, setIsRecapturing] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  // Cleanup webcam stream on unmount or when stopping
  React.useEffect(() => {
    return () => {
      if (webcamStream) {
        webcamStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [webcamStream]);

  // Function to replace the image src in the markdown content
  const updateMarkdownImage = async (newSrc: string) => {
    // We replace the first occurrence of the original src with the new src
    // This is a simple replacement; note that if the same src appears multiple times, we only replace the first.
    // For a more robust solution, we might want to replace by the entire image markdown, but we don't have that here.
    const newContent = markdownContent.replace(src, newSrc);
    setMarkdownContent(newContent);
  };

  const handleRecapture = async () => {
    setIsRecapturing(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setWebcamStream(stream);
      videoRef.current?.play();
    } catch (err) {
      console.error("Error accessing webcam:", err);
      alert("Unable to access webcam. Please check your permissions.");
      setIsRecapturing(false);
    }
  };

  const handleCapture = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/png");
      setPreviewSrc(dataUrl);
      // Update the markdown content
      updateMarkdownImage(dataUrl);
    }
    // Stop the webcam stream
    if (webcamStream) {
      webcamStream.getTracks().forEach((track) => track.stop());
      setWebcamStream(null);
    }
    setIsRecapturing(false);
    setIsEditing(false);
  };

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    const reader = new FileReader();
    reader.onloadend = () => {
      if (reader.result && typeof reader.result === "string") {
        setPreviewSrc(reader.result);
        // Update the markdown content
        updateMarkdownImage(reader.result);
      }
      setIsUploading(false);
      setIsEditing(false);
      e.target.value = ""; // Reset the input
    };
    reader.readAsDataURL(file);
  };

  const handleClose = () => {
    // If we were recapturing, stop the webcam stream
    if (webcamStream) {
      webcamStream.getTracks().forEach((track) => track.stop());
      setWebcamStream(null);
    }
    setIsRecapturing(false);
    setIsUploading(false);
    setIsEditing(false);
    setPreviewSrc(src); // Reset preview to original src
  };

  return (
    <div className="relative inline-block">
      {/* The image */}
      <img
        src={previewSrc}
        alt={alt}
        title={title}
        className="cursor-pointer max-w-full hover:opacity-80 transition-opacity"
        onClick={() => setIsEditing(true)}
      />

      {/* Edit overlay */}
      {isEditing && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-80">
            <h2 className="text-lg font-semibold mb-4">Edit Image</h2>
            <div className="space-y-4">
              <button
                onClick={handleRecapture}
                disabled={isRecapturing}
                className="w-full flex items-center justify-between px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                <span>Recapture</span>
                {isRecapturing && <span className="ml-2">...</span>}
              </button>
              <button
                onClick={() => {
                  setIsUploading(true);
                  // Trigger the file input
                  const input = document.createElement("input");
                  input.type = "file";
                  input.accept = "image/*";
                  input.onchange = handleUpload;
                  input.click();
                }}
                disabled={isUploading}
                className="w-full flex items-center justify-between px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                <span>Upload</span>
                {isUploading && <span className="ml-2">...</span>}
              </button>
              <button
                onClick={handleClose}
                className="w-full flex items-center justify-between px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
                <X className="ml-2 h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Webcam preview when recapturing */}
      {isRecapturing && webcamStream && (
        <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center z-20">
          <div className="relative w-[640px] h-[480px]">
            <video
              ref={videoRef}
              autoPlay
              muted
              className="w-full h-full object-contain"
            />
            <button
              onClick={handleCapture}
              className="absolute bottom-4 right-4 bg-white rounded-full p-2 hover:bg-gray-200"
            >
              <Camera className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
