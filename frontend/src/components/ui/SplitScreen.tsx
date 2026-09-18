import * as React from "react";
import { useState, useRef, useEffect } from "react";
import { MonacoEditor } from "./MonacoEditor";
import { PreviewPane } from "./PreviewPane";

interface SplitScreenProps {
  value: string;
  onChange: (value: string) => void;
}

export const SplitScreen: React.FC<SplitScreenProps> = ({
  value,
  onChange,
}) => {
  const [splitPosition, setSplitPosition] = useState<number>(50); // percentage
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const splitterRef = useRef<HTMLDivElement>(null);
  const startX = useRef<number>(0);
  const startPos = useRef<number>(0);

  const handleDragStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (containerRect) {
      startX.current = e.clientX;
      startPos.current = splitPosition;
    }
  };

  const handleDragMove = (e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();
    const deltaX = e.clientX - startX.current;
    const deltaPercent = (deltaX / containerRect.width) * 100;
    let newPos = startPos.current + deltaPercent;
    // Clamp between 20% and 80%
    newPos = Math.max(20, Math.min(80, newPos));
    setSplitPosition(newPos);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // We'll attach mouse move and up events to the window
  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleDragMove);
      window.addEventListener("mouseup", handleDragEnd);
      return () => {
        window.removeEventListener("mousemove", handleDragMove);
        window.removeEventListener("mouseup", handleDragEnd);
      };
    }
  }, [isDragging]);

  return (
    <div
      ref={containerRef}
      className="relative h-full w-full overflow-hidden bg-gray-50"
    >
      {/* Left pane: Editor */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-[${splitPosition}%] bg-white overflow-hidden`}
      >
        <MonacoEditor value={value} onChange={onChange} />
      </div>

      {/* Right pane: Preview */}
      <div
        className={`absolute right-0 top-0 bottom-0 w-[${
          100 - splitPosition
        }%] bg-white overflow-hidden`}
      >
        <PreviewPane value={value} />
      </div>

      {/* Splitter */}
      <div
        ref={splitterRef}
        className={`absolute left-[${splitPosition}%] top-0 bottom-0 w-2 cursor-col-resize bg-gray-200 hover:bg-gray-300 transition-colors z-10`}
        onMouseDown={handleDragStart}
      />
    </div>
  );
};
