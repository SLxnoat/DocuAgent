import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SplitScreen } from "../editor/SplitScreen";
import { ScreenshotImage } from "../editor/ScreenshotImage";

describe("SplitScreen", () => {
  it("renders left and right pane content", () => {
    render(
      <SplitScreen
        leftPane={<div>Left Editor</div>}
        rightPane={<div>Right Preview</div>}
        defaultSplit={50}
      />,
    );

    expect(screen.getByText("Left Editor")).toBeInTheDocument();
    expect(screen.getByText("Right Preview")).toBeInTheDocument();
  });
});

describe("ScreenshotImage", () => {
  it("renders image with alt text and src", () => {
    render(
      <ScreenshotImage
        src="/assets/job-1/step_001.png"
        alt="Step 1 Screenshot"
        stepIndex={1}
      />,
    );

    const img = screen.getByAltText("Step 1 Screenshot");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "/assets/job-1/step_001.png");
  });
});
