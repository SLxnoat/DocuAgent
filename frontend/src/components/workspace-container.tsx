import * as React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

export function WorkspaceContainer(
  props: React.PropsWithChildren<{ className?: string }>,
) {
  return (
    <main className={props.className}>
      <ScrollArea className="h-full w-full p-6">{props.children}</ScrollArea>
    </main>
  );
}
