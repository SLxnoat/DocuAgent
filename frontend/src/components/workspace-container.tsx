import * as React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

export function WorkspaceContainer(
  props: React.PropsWithChildren<{ className?: string }>,
) {
  return (
    <main className={`flex-1 flex flex-col min-h-0 ${props.className || ""}`}>
      <ScrollArea className="h-full w-full">{props.children}</ScrollArea>
    </main>
  );
}
