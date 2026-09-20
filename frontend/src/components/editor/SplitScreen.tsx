import React, { useState, useRef, useCallback } from "react";

interface SplitScreenProps {
  leftPane: React.ReactNode;
  rightPane: React.ReactNode;
  defaultSplit?: number; // Percentage for left pane (0-100)
}

export function SplitScreen({
  leftPane,
  rightPane,
  defaultSplit = 50,
}: SplitScreenProps) {
  const [leftWidthPercent, setLeftWidthPercent] = useState<number>(() => {
    const saved = localStorage.getItem("docuagent-split-ratio");
    return saved ? Math.min(Math.max(parseFloat(saved), 20), 80) : defaultSplit;
  });

  const isDraggingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    isDraggingRef.current = true;
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDraggingRef.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const newLeftWidth = e.clientX - rect.left;
    const newPercent = (newLeftWidth / rect.width) * 100;
    const clampedPercent = Math.min(Math.max(newPercent, 20), 80);
    setLeftWidthPercent(clampedPercent);
    localStorage.setItem("docuagent-split-ratio", clampedPercent.toString());
  }, []);

  const handleMouseUp = useCallback(() => {
    isDraggingRef.current = false;
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, [handleMouseMove]);

  return (
    <div
      ref={containerRef}
      className="flex h-full w-full relative min-h-0 overflow-hidden"
    >
      {/* Left Pane (Editor) */}
      <div
        style={{ width: `${leftWidthPercent}%` }}
        className="h-full min-w-0 overflow-hidden"
      >
        {leftPane}
      </div>

      {/* Resize Handle */}
      <div
        onMouseDown={handleMouseDown}
        className="w-2.5 h-full flex items-center justify-center cursor-col-resize hover:bg-brand/20 transition-colors z-10 shrink-0 select-none group"
        title="Drag to resize split panes"
      >
        <div className="w-[2px] h-8 rounded-full bg-border group-hover:bg-brand transition-colors" />
      </div>

      {/* Right Pane (Preview) */}
      <div
        style={{ width: `${100 - leftWidthPercent}%` }}
        className="h-full min-w-0 overflow-hidden"
      >
        {rightPane}
      </div>
    </div>
  );
}
