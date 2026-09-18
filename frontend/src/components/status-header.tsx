import * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function StatusHeader(
  props: React.PropsWithChildren<{ className?: string }>,
) {
  return (
    <header className={props.className}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between w-full">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold">DocuAgent AI</h1>
          <div className="flex items-center space-x-2">
            <Badge variant="secondary">Online</Badge>
            <Badge variant="destructive" onclick={() => {}}>
              2 Jobs Running
            </Badge>
          </div>
        </div>

        <div className="flex items-center space-x-3 mt-3 sm:mt-0">
          <Button variant="outline" size="icon">
            Settings
          </Button>
          <Button variant="outline" size="icon">
            Help
          </Button>
          <Button>New Project</Button>
        </div>
      </div>
    </header>
  );
}
