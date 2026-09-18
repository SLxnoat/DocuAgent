import * as React from "react";
import { Nav } from "@/components/ui/nav";

export function Sidebar(
  props: React.PropsWithChildren<{ className?: string }>,
) {
  return (
    <aside className={props.className}>
      <Nav className="space-y-1 p-4">
        <Nav.Link
          href="/"
          className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-primary/10"
        >
          Dashboard
        </Nav.Link>
        <Nav.Link
          href="/projects"
          className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-primary/10"
        >
          Projects
        </Nav.Link>
        <Nav.Link
          href="/settings"
          className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-primary/10"
        >
          Settings
        </Nav.Link>
      </Nav>

      {/* Additional sidebar content can go here */}
      <div className="mt-auto p-4 border-t">
        <p className="text-sm text-muted-foreground">DocuAgent AI v1.0.0</p>
      </div>
    </aside>
  );
}
