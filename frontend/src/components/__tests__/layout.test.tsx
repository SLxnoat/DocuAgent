import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { Sidebar } from "../layout/Sidebar";
import { AppShell } from "../layout/AppShell";

describe("Sidebar", () => {
  it("renders brand and navigation links", () => {
    render(
      <BrowserRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </BrowserRouter>,
    );

    expect(screen.getByText("DocuAgent AI")).toBeInTheDocument();
    expect(screen.getByText("Studio")).toBeInTheDocument();
    expect(screen.getByText("Jobs")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });
});

describe("AppShell", () => {
  it("renders sidebar and children content", () => {
    render(
      <BrowserRouter>
        <AppShell>
          <div>Main Workspace Content</div>
        </AppShell>
      </BrowserRouter>,
    );

    expect(screen.getByText("Main Workspace Content")).toBeInTheDocument();
    expect(screen.getByText("DocuAgent AI")).toBeInTheDocument();
  });
});
