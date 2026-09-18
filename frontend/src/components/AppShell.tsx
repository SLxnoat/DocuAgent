import * as React from "react";
import { Sidebar } from "./sidebar";
import { StatusHeader } from "./status-header";
import { WorkspaceContainer } from "./workspace-container";

export function AppShell(
  props: React.PropsWithChildren<{ className?: string }>,
) {
  return (
    <div className="flex flex-col h-[100vh] bg-background">
      <StatusHeader className="mb-4" />
      <div className="flex flex-1">
        <Sidebar className="w-64 bg-muted border-r" />
        <WorkspaceContainer className="flex-1 overflow-hidden" {...props} />
      </div>
    </div>
  );
}
