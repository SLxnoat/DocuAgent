import { describe, it, expect } from "vitest";
import {
  extractScreenshotReferences,
  normalizeImagePaths,
} from "../markdownUtils";
import { formatTimestamp, formatFileSize, truncateText } from "../formatUtils";

describe("markdownUtils", () => {
  it("extracts screenshot references with step index", () => {
    const md = `
# Manual
Here is step 1:
![Step 1: Dashboard](/assets/job_abc/step_001.png)
And step 2:
![Step 2: Settings](/assets/job_abc/step_002.png)
And generic image:
![Logo](https://example.com/logo.png)
    `;

    const refs = extractScreenshotReferences(md);
    expect(refs).toHaveLength(3);
    expect(refs[0]).toEqual({
      alt: "Step 1: Dashboard",
      src: "/assets/job_abc/step_001.png",
      stepIndex: 1,
    });
    expect(refs[1]).toEqual({
      alt: "Step 2: Settings",
      src: "/assets/job_abc/step_002.png",
      stepIndex: 2,
    });
    expect(refs[2]).toEqual({
      alt: "Logo",
      src: "https://example.com/logo.png",
      stepIndex: null,
    });
  });

  it("normalizes relative /assets/ paths with API base", () => {
    const md = "![Step 1](/assets/job_1/step_001.png)";
    const normalized = normalizeImagePaths(md, "http://localhost:8000/api/v1");
    expect(normalized).toBe(
      "![Step 1](http://localhost:8000/assets/job_1/step_001.png)",
    );
  });
});

describe("formatUtils", () => {
  it("formats valid ISO timestamp", () => {
    const formatted = formatTimestamp("2026-09-20T10:30:00Z");
    expect(formatted).toBeTruthy();
    expect(typeof formatted).toBe("string");
  });

  it("handles invalid timestamp gracefully", () => {
    expect(formatTimestamp("invalid-date")).toBe("");
  });

  it("formats file sizes accurately", () => {
    expect(formatFileSize(500)).toBe("500 B");
    expect(formatFileSize(2048)).toBe("2.0 KB");
    expect(formatFileSize(1048576 * 2.5)).toBe("2.5 MB");
  });

  it("truncates text with ellipsis", () => {
    expect(truncateText("Short", 10)).toBe("Short");
    expect(truncateText("A very long text exceeding max limit", 10)).toBe(
      "A very lon…",
    );
  });
});
