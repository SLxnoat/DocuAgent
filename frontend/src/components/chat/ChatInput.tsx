import { useState, useRef } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({
  onSendMessage,
  isLoading,
  disabled,
}: ChatInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!content.trim() || isLoading || disabled) return;
    onSendMessage(content.trim());
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 p-3 border-t bg-card">
      <Textarea
        ref={textareaRef}
        rows={1}
        placeholder={
          disabled
            ? "Generate a document first to enable refinement..."
            : "e.g. 'Add a troubleshooting note to step 2' or 'Translate to Spanish'"
        }
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled || isLoading}
        className="min-h-[38px] max-h-32 text-xs resize-none py-2 px-3 bg-muted/30"
      />

      <Button
        size="icon"
        className="h-9 w-9 shrink-0 bg-brand text-black hover:bg-brand/90"
        onClick={handleSend}
        disabled={!content.trim() || isLoading || disabled}
        title="Send refinement command"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
