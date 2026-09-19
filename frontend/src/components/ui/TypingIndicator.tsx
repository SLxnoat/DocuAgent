import * as React from "react";

interface TypingIndicatorProps {
  isTyping: boolean;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  isTyping,
}) => {
  if (!isTyping) return null;

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] px-4 py-2 rounded-lg bg-gray-200 text-gray-800">
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce"></div>
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce animate-bounce-delay-2"></div>
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce animate-bounce-delay-4"></div>
          <span>DocuAgent is refining the document...</span>
        </div>
      </div>
    </div>
  );
};
