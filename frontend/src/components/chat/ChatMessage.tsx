import { Bot, User } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { formatTimestamp } from "@/utils/formatUtils";
import type { ChatMessage as ChatMessageType } from "@/types";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-2.5 text-xs",
        isUser ? "flex-row-reverse" : "flex-row",
      )}
    >
      <Avatar className="h-7 w-7 shrink-0">
        <AvatarFallback
          className={cn(
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-brand/20 text-brand",
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          "flex flex-col max-w-[85%] rounded-lg px-3 py-2",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-none"
            : "bg-muted/70 text-foreground border rounded-tl-none",
        )}
      >
        {message.isLoading ? (
          <div className="flex items-center gap-1.5 py-1 px-1">
            <span className="text-[11px] text-muted-foreground mr-1">
              Agent is editing
            </span>
            <span className="h-1.5 w-1.5 rounded-full bg-brand typing-dot" />
            <span className="h-1.5 w-1.5 rounded-full bg-brand typing-dot" />
            <span className="h-1.5 w-1.5 rounded-full bg-brand typing-dot" />
          </div>
        ) : (
          <p className="whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
        )}

        {message.timestamp && !message.isLoading && (
          <span
            className={cn(
              "text-[9px] mt-1 self-end opacity-70 font-mono",
              isUser ? "text-primary-foreground" : "text-muted-foreground",
            )}
          >
            {formatTimestamp(message.timestamp)}
          </span>
        )}
      </div>
    </div>
  );
}
