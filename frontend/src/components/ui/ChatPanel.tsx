import * as React from "react";
import { useState, useRef, useEffect } from "react";
import { useManualStore } from "@/store/useManualStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { sendChatMessage } from "@/api/client";
import { TypingIndicator } from "./TypingIndicator";
import {
  Send,
  Bot,
  User,
  Sparkles,
  MessageSquare,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface ChatPanelProps {
  sessionId: string | null;
  className?: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  sessionId,
  className,
}) => {
  const {
    chatHistory,
    isChatLoading,
    isTyping,
    addChatMessage,
    setChatLoading,
    setTyping,
    markdownContent,
    setMarkdownContent,
  } = useManualStore();

  const { sendMessage, isConnected } = useWebSocket(sessionId);
  const [inputValue, setInputValue] = useState("");
  const [isCollapsed, setIsCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll when chat messages or typing state changes
  useEffect(() => {
    if (!isCollapsed) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory, isTyping, isCollapsed]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = inputValue.trim();
    if (!text || !sessionId || isChatLoading) return;

    // Add user message to history
    addChatMessage("user", text);
    setInputValue("");
    setChatLoading(true);
    setTyping(true);

    // Try sending over WebSocket first
    const sentViaWs = sendMessage(text);

    if (!sentViaWs) {
      // Fallback to HTTP REST
      try {
        const response = await sendChatMessage(sessionId, {
          message: text,
          context: {
            current_markdown: markdownContent,
          },
        });

        if (response.response_message) {
          addChatMessage("assistant", response.response_message);
        }
        if (response.updated_markdown) {
          setMarkdownContent(response.updated_markdown);
        }
      } catch (err) {
        console.error("Failed to send chat message:", err);
        addChatMessage(
          "assistant",
          "Sorry, I encountered an issue updating the document. Please verify network connectivity and retry.",
        );
      } finally {
        setChatLoading(false);
        setTyping(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className={`border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex flex-col shadow-lg transition-all ${
        isCollapsed ? "h-12" : "h-72 sm:h-80"
      } ${className || ""}`}
    >
      {/* Header bar */}
      <div
        className="flex items-center justify-between px-4 py-2.5 bg-gray-50 dark:bg-gray-800/90 border-b border-gray-200 dark:border-gray-800 cursor-pointer select-none"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
            Agent 5: Conversational Refiner (HITL)
          </span>
          <span
            className={`inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full ${
              isConnected
                ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                : "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isConnected ? "bg-emerald-500" : "bg-amber-500 animate-pulse"
              }`}
            />
            <span>{isConnected ? "Live WS" : "REST Fallback"}</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-gray-500 dark:text-gray-400 hidden sm:inline">
            {isCollapsed ? "Click to expand" : "Shift + Enter for new line"}
          </span>
          <button
            type="button"
            className="p-1 rounded text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
          >
            {isCollapsed ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Messages area */}
      {!isCollapsed && (
        <>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 bg-gray-50/50 dark:bg-gray-900/50">
            {chatHistory.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-gray-400 text-xs py-6">
                <MessageSquare className="h-8 w-8 text-gray-300 dark:text-gray-600 mb-2" />
                <p className="font-medium text-gray-600 dark:text-gray-300">
                  Ask DocuAgent to refine your manual
                </p>
                <p className="max-w-md mt-1">
                  E.g., &quot;Add a warning note in Step 2 about required
                  permissions&quot; or &quot;Translate the manual to
                  Spanish&quot;.
                </p>
              </div>
            ) : (
              chatHistory.map((msg, index) => (
                <div
                  key={msg.id || index}
                  className={`flex gap-2.5 ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.role === "assistant" && (
                    <div className="h-7 w-7 rounded-full bg-blue-600 dark:bg-blue-500 flex items-center justify-center text-white shrink-0">
                      <Bot className="h-4 w-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-xs ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-xs"
                        : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-bl-xs"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <span
                      className={`block text-[10px] mt-1 text-right ${
                        msg.role === "user"
                          ? "text-blue-100"
                          : "text-gray-400 dark:text-gray-500"
                      }`}
                    >
                      {typeof msg.timestamp === "string"
                        ? new Date(msg.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : msg.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                    </span>
                  </div>

                  {msg.role === "user" && (
                    <div className="h-7 w-7 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-700 dark:text-gray-200 shrink-0">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))
            )}

            {/* Typing Indicator */}
            <TypingIndicator isTyping={isTyping} />

            <div ref={messagesEndRef} />
          </div>

          {/* Message composer */}
          <form
            onSubmit={handleSend}
            className="p-2.5 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-end gap-2"
          >
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask DocuAgent to adjust, add notes, or rephrase steps..."
              rows={1}
              className="flex-1 max-h-24 min-h-[38px] p-2 text-xs border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isChatLoading}
              className="h-[38px] px-3.5 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              title="Send message (Enter)"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </>
      )}
    </div>
  );
};
