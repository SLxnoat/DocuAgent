import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ProgressBar } from "../progress/ProgressBar";
import { StepStatus } from "../progress/StepStatus";
import { ProgressPanel } from "../progress/ProgressPanel";
import { ThemeToggle } from "../ui/ThemeToggle";
import { OptionsPanel } from "../input/OptionsPanel";
import { ExportBar } from "../export/ExportBar";
import { ScriptInputForm } from "../input/ScriptInputForm";
import { useManualStore } from "@/store/useManualStore";

describe("ProgressBar", () => {
  it("renders progress bar with 0% when idle", () => {
    const { container } = render(
      <ProgressBar status="idle" stepCount={5} capturedCount={0} />,
    );
    const indicator = container.querySelector('[role="progressbar"]');
    expect(indicator).toBeInTheDocument();
  });

  it("calculates progress during capturing phase", () => {
    const { container } = render(
      <ProgressBar status="capturing" stepCount={10} capturedCount={5} />,
    );
    const indicator = container.querySelector('[role="progressbar"]');
    expect(indicator).toBeInTheDocument();
  });
});

describe("StepStatus", () => {
  it("renders pending status badge", () => {
    render(<StepStatus stepIndex={1} status="pending" />);
    expect(screen.getByText("Step 1: Pending")).toBeInTheDocument();
  });

  it("renders captured status badge", () => {
    render(<StepStatus stepIndex={2} status="captured" />);
    expect(screen.getByText("Step 2: Captured")).toBeInTheDocument();
  });

  it("renders fallback status badge with tooltip trigger when error exists", () => {
    render(
      <StepStatus stepIndex={3} status="fallback" error="Selector timeout" />,
    );
    expect(screen.getByText("Step 3: Fallback")).toBeInTheDocument();
  });
});

describe("ProgressPanel", () => {
  it("renders status message and step status elements", () => {
    useManualStore.getState().setJobStatus("capturing");
    useManualStore.getState().setStepCount(3);
    useManualStore
      .getState()
      .updateStepStatus({ stepIndex: 1, status: "captured" });

    render(<ProgressPanel />);
    expect(screen.getByText(/Agent 2/i)).toBeInTheDocument();
    expect(screen.getByText(/1 of 3 steps resolved/i)).toBeInTheDocument();
  });
});

describe("ThemeToggle", () => {
  it("renders theme toggle button", () => {
    render(<ThemeToggle />);
    const button = screen.getByRole("button", { name: /toggle theme/i });
    expect(button).toBeInTheDocument();
  });
});

describe("OptionsPanel", () => {
  it("renders options checkboxes and triggers change handler", () => {
    const onChangeFormats = vi.fn();
    const onChangeLanguage = vi.fn();
    const onChangeDomainHint = vi.fn();

    render(
      <OptionsPanel
        outputFormats={["markdown"]}
        onChangeFormats={onChangeFormats}
        language="en"
        onChangeLanguage={onChangeLanguage}
        domainHint=""
        onChangeDomainHint={onChangeDomainHint}
        selectedModel="llama3.3:70b"
        onChangeModel={vi.fn()}
      />,
    );

    expect(screen.getByText("Markdown")).toBeInTheDocument();
    expect(screen.getByText("HTML")).toBeInTheDocument();
    expect(screen.getByText("PDF")).toBeInTheDocument();
    expect(screen.getByText(/AI Model/i)).toBeInTheDocument();

    const htmlCheckbox = screen.getByRole("checkbox", { name: /html/i });
    fireEvent.click(htmlCheckbox);
    expect(onChangeFormats).toHaveBeenCalledWith(["markdown", "html"]);
  });
});

describe("ExportBar", () => {
  it("renders download buttons disabled when job is not ready", () => {
    useManualStore.getState().setJobStatus("capturing");
    render(<ExportBar />);

    const buttons = screen.getAllByRole("button");
    buttons.forEach((btn) => expect(btn).toBeDisabled());
  });

  it("enables download buttons when document is ready", () => {
    useManualStore.getState().setJobStatus("awaiting_input");
    render(<ExportBar />);

    const mdBtn = screen.getByRole("button", { name: /markdown/i });
    expect(mdBtn).not.toBeDisabled();
  });
});

describe("ScriptInputForm", () => {
  it("dispatches submission when form is filled and submitted", () => {
    const onSubmit = vi.fn();
    render(<ScriptInputForm onSubmit={onSubmit} isLoading={false} />);

    const scriptInput = screen.getByPlaceholderText(/1\. Go to Login/i);
    const urlInput = screen.getByPlaceholderText(/staging\.app/i);

    fireEvent.change(scriptInput, {
      target: {
        value: "Navigate to dashboard and test the user creation flow.",
      },
    });
    fireEvent.change(urlInput, {
      target: { value: "https://staging.app.example.com" },
    });

    const submitBtn = screen.getByRole("button", { name: /generate manual/i });
    fireEvent.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledWith({
      script: "Navigate to dashboard and test the user creation flow.",
      target_url: "https://staging.app.example.com",
      options: {
        output_formats: ["markdown", "pdf"],
        language: "en",
        domain_hint: undefined,
        model: "llama3.3:70b",
      },
    });
  });
});
