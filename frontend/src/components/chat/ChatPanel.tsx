import { useRef, useEffect } from "react";
import { Bot, Sparkles, X, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { useManualStore } from "@/store/useManualStore";

interface ChatPanelProps {
  sessionId: string | null;
  sendMessage: (message: string) => void;
  isConnected: boolean;
}

export function ChatPanel({
  sessionId,
  sendMessage,
  isConnected,
}: ChatPanelProps) {
  const {
    chatHistory,
    isChatLoading,
    isChatVisible,
    setChatVisible,
    jobStatus,
  } = useManualStore();
  const scrollEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages or loading updates
  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isChatLoading]);

  const isEnabled =
    sessionId !== null &&
    ["awaiting_input", "refining", "completed"].includes(jobStatus);

  if (!isChatVisible) {
    return (
      <Button
        variant="outline"
        size="sm"
        className="fixed bottom-6 right-6 shadow-lg z-30 gap-2 border-brand bg-card hover:bg-brand/10 text-foreground"
        onClick={() => setChatVisible(true)}
      >
        <Sparkles className="h-4 w-4 text-brand" />
        <span>Refinement Chat</span>
        {chatHistory.length > 0 && (
          <span className="ml-1 px-1.5 py-0.2 text-[10px] rounded-full bg-brand text-black font-bold">
            {chatHistory.length}
          </span>
        )}
      </Button>
    );
  }

  return (
    <aside className="w-80 md:w-96 flex flex-col h-full border rounded-lg bg-card shadow-lg shrink-0 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2.5 border-b bg-muted/40">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-brand/10 text-brand">
            <Bot className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold leading-tight text-foreground">
              Document Refiner (Agent 5)
            </span>
            <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
              {isConnected ? (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>WebSocket Connected</span>
                </>
              ) : (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                  <span>REST Fallback Mode</span>
                </>
              )}
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-muted-foreground hover:text-foreground"
          onClick={() => setChatVisible(false)}
          title="Close chat panel"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Message List */}
      <ScrollArea className="flex-1 p-3">
        {chatHistory.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center text-muted-foreground text-xs p-4">
            <MessageSquare className="h-8 w-8 mb-2 opacity-30 text-brand" />
            <p className="font-semibold text-foreground">
              Interactive Human-in-the-Loop
            </p>
            <p className="mt-1 leading-relaxed">
              Ask Agent 5 to add notes, expand steps, translate language, or
              re-take specific screenshots without re-generating from scratch.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {chatHistory.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={scrollEndRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <ChatInput
        onSendMessage={sendMessage}
        isLoading={isChatLoading}
        disabled={!isEnabled}
      />
    </aside>
  );
}
