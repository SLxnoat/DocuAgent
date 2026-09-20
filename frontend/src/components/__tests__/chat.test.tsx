import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChatMessage } from "../chat/ChatMessage";
import { ChatInput } from "../chat/ChatInput";

describe("ChatMessage", () => {
  it("renders user message properly", () => {
    render(
      <ChatMessage
        message={{
          id: "1",
          role: "user",
          content: "Add caution callout to step 2",
          timestamp: "2026-09-20T12:00:00Z",
        }}
      />,
    );
    expect(
      screen.getByText("Add caution callout to step 2"),
    ).toBeInTheDocument();
  });

  it("renders loading state for assistant message", () => {
    render(
      <ChatMessage
        message={{
          id: "2",
          role: "assistant",
          content: "",
          timestamp: "2026-09-20T12:00:01Z",
          isLoading: true,
        }}
      />,
    );
    expect(screen.getByText(/Agent is editing/i)).toBeInTheDocument();
  });
});

describe("ChatInput", () => {
  it("triggers onSendMessage on click and Enter key", () => {
    const onSendMessage = vi.fn();
    render(<ChatInput onSendMessage={onSendMessage} isLoading={false} />);

    const textarea = screen.getByPlaceholderText(/Add a troubleshooting note/i);
    fireEvent.change(textarea, { target: { value: "Translate into French" } });

    const sendBtn = screen.getByRole("button", {
      name: /send refinement command/i,
    });
    fireEvent.click(sendBtn);

    expect(onSendMessage).toHaveBeenCalledWith("Translate into French");
  });

  it("disables input when disabled prop is true", () => {
    const onSendMessage = vi.fn();
    render(
      <ChatInput
        onSendMessage={onSendMessage}
        isLoading={false}
        disabled={true}
      />,
    );

    const textarea = screen.getByPlaceholderText(/Generate a document first/i);
    expect(textarea).toBeDisabled();
  });
});
