import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { StudioView } from "../StudioView";
import { useManualStore } from "@/store/useManualStore";

// Mock Monaco Editor wrapper so it doesn't try to load monaco in jsdom
vi.mock("@/components/editor/EditorPane", () => ({
  EditorPane: () => <div data-testid="mock-editor-pane">Mock Editor Pane</div>,
}));

vi.mock("@/components/editor/PreviewPane", () => ({
  PreviewPane: () => (
    <div data-testid="mock-preview-pane">Mock Preview Pane</div>
  ),
}));

describe("StudioView", () => {
  beforeEach(() => {
    useManualStore.getState().reset();
  });

  it("renders script input form initially when status is idle", () => {
    render(<StudioView />);
    expect(screen.getByText("Generate User Manual")).toBeInTheDocument();
  });

  it("renders progress panel when job is generating", () => {
    useManualStore.getState().setJobStatus("capturing");
    useManualStore.getState().setJobId("job-1234");
    render(<StudioView />);

    expect(screen.getByText(/Generating User Manual/i)).toBeInTheDocument();
  });

  it("renders editor and export bar when document is ready", () => {
    useManualStore.getState().setJobStatus("awaiting_input");
    useManualStore.getState().setSessionId("sess-1234");
    useManualStore.getState().setMarkdownContent("# My Manual");
    render(<StudioView />);

    expect(screen.getByTestId("mock-editor-pane")).toBeInTheDocument();
    expect(screen.getByTestId("mock-preview-pane")).toBeInTheDocument();
    expect(
      screen.getByText(/Interactive Studio Workspace/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/Export Publication Formats/i)).toBeInTheDocument();
  });

  it("allows resetting back to new manual form", () => {
    useManualStore.getState().setJobStatus("awaiting_input");
    render(<StudioView />);

    const newBtn = screen.getByRole("button", { name: /new manual/i });
    fireEvent.click(newBtn);

    expect(useManualStore.getState().jobStatus).toBe("idle");
    expect(screen.getByText("Generate User Manual")).toBeInTheDocument();
  });
});
