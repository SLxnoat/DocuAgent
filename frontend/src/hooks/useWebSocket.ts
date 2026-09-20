import { useCallback, useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { sendChatMessage } from "@/api/client";
import { useManualStore } from "@/store/useManualStore";
import type { WSServerMessage } from "@/types";

const API_HOST = import.meta.env.VITE_API_HOST ?? "localhost:8000";
const WS_ENABLED = import.meta.env.VITE_ENABLE_WEBSOCKET_CHAT !== "false";

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const heartRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const store = useManualStore();

  useEffect(() => {
    if (!sessionId || !WS_ENABLED) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = API_HOST.includes(":")
      ? API_HOST
      : `${window.location.hostname}:8000`;
    const url = `${protocol}//${host}/api/v1/ws/chat/${sessionId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      heartRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(
            JSON.stringify({
              type: "ping",
              timestamp: new Date().toISOString(),
            }),
          );
        }
      }, 20_000);
    };

    ws.onclose = () => {
      setIsConnected(false);
      if (heartRef.current) {
        clearInterval(heartRef.current);
        heartRef.current = null;
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onmessage = ({ data }: MessageEvent) => {
      let msg: WSServerMessage;
      try {
        msg = JSON.parse(data);
      } catch {
        return;
      }

      switch (msg.type) {
        case "typing_start":
          store.setChatLoading(true);
          break;

        case "typing_stop":
          store.setChatLoading(false);
          break;

        case "agent_response":
          if (msg.updated_markdown) {
            store.setMarkdownContent(msg.updated_markdown);
          }
          if (msg.content) {
            store.updateLastAssistantMessage(msg.content);
          }
          store.setChatLoading(false);
          break;

        case "error":
          store.setChatLoading(false);
          if (msg.message) {
            store.updateLastAssistantMessage(`⚠️ Error: ${msg.message}`);
          }
          break;
      }
    };

    return () => {
      ws.close();
      if (heartRef.current) {
        clearInterval(heartRef.current);
        heartRef.current = null;
      }
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim()) return;

      // Add user message to chat
      store.addChatMessage({
        id: uuidv4(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      });

      // Add loading placeholder for assistant response
      store.addChatMessage({
        id: uuidv4(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        isLoading: true,
      });

      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            type: "user_message",
            content,
            timestamp: new Date().toISOString(),
          }),
        );
      } else {
        // Fallback: REST endpoint
        store.setChatLoading(true);
        try {
          const { data } = await sendChatMessage(
            sessionId,
            content,
            store.markdownContent,
          );
          if (data.updated_markdown) {
            store.setMarkdownContent(data.updated_markdown);
          }
          store.updateLastAssistantMessage(data.response_message);
        } catch (err) {
          const msg =
            err instanceof Error ? err.message : "Chat request failed";
          store.updateLastAssistantMessage(`⚠️ Error: ${msg}`);
        } finally {
          store.setChatLoading(false);
        }
      }
    },
    [sessionId, store],
  );

  return { sendMessage, isConnected };
}
