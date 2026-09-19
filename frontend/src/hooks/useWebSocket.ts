import { useEffect, useRef, useCallback, useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import { API_BASE_URL } from "@/api/client";

export const useWebSocket = (sessionId: string | null) => {
  const { addChatMessage, setMarkdownContent, setChatLoading, setTyping } =
    useManualStore();
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let isMounted = true;

    const connectWebSocket = () => {
      try {
        // Derive WS endpoint from API_BASE_URL
        const wsBase = API_BASE_URL.replace(/^http/, "ws");
        const token =
          localStorage.getItem("api_token") ||
          import.meta.env.VITE_API_TOKEN ||
          "";
        const url = `${wsBase}/ws/chat/${sessionId}${
          token ? `?token=${encodeURIComponent(token)}` : ""
        }`;

        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          console.log(`[WebSocket] Connected for session ${sessionId}`);
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);

            switch (data.type) {
              case "agent_response":
                if (data.content) {
                  addChatMessage("assistant", data.content);
                }
                if (data.updated_markdown) {
                  setMarkdownContent(data.updated_markdown);
                }
                setChatLoading(false);
                setTyping(false);
                break;

              case "chat_message":
                if (data.role && data.content) {
                  addChatMessage(data.role, data.content);
                }
                setChatLoading(false);
                setTyping(false);
                break;

              case "typing_start":
                setTyping(true);
                break;

              case "typing_stop":
                setTyping(false);
                break;

              case "pong":
                // Heartbeat reply
                break;

              case "error":
                console.error("[WebSocket] Server error event:", data.message);
                setChatLoading(false);
                setTyping(false);
                break;

              default:
                console.debug("[WebSocket] Unhandled message:", data);
            }
          } catch (error) {
            console.error("[WebSocket] Parse error:", error, event.data);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setIsConnected(false);
          console.log(
            "[WebSocket] Disconnected, attempting reconnect in 3s...",
          );
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMounted) {
              connectWebSocket();
            }
          }, 3000);
        };

        ws.onerror = (error) => {
          console.warn("[WebSocket] Error occurred:", error);
          ws.close();
        };
      } catch (err) {
        console.error("[WebSocket] Failed to establish connection:", err);
      }
    };

    connectWebSocket();

    // Send keepalive ping every 25 seconds
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 25000);

    return () => {
      isMounted = false;
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
      setIsConnected(false);
    };
  }, [
    sessionId,
    addChatMessage,
    setMarkdownContent,
    setChatLoading,
    setTyping,
  ]);

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "user_message",
          content,
          timestamp: new Date().toISOString(),
        }),
      );
      return true;
    }
    return false;
  }, []);

  return { sendMessage, isConnected };
};
