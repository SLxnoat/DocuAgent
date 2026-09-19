import * as React from "react";
import Editor, { type OnMount } from "@monaco-editor/react";
import { useManualStore } from "@/store/useManualStore";

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

type EditorInstance = Parameters<OnMount>[0];

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  onChange,
  className,
}) => {
  const { darkMode } = useManualStore();
  const editorRef = React.useRef<EditorInstance | null>(null);

  const handleEditorDidMount: OnMount = (editorInstance) => {
    editorRef.current = editorInstance;
  };

  // Synchronize external value changes while preserving cursor position
  React.useEffect(() => {
    if (editorRef.current) {
      const currentValue = editorRef.current.getValue();
      if (value !== currentValue) {
        const position = editorRef.current.getPosition();
        editorRef.current.setValue(value);
        if (position) {
          editorRef.current.setPosition(position);
        }
      }
    }
  }, [value]);

  return (
    <div className={`h-full w-full overflow-hidden ${className || ""}`}>
      <Editor
        height="100%"
        width="100%"
        defaultLanguage="markdown"
        theme={darkMode ? "vs-dark" : "light"}
        value={value}
        onChange={(val) => onChange(val ?? "")}
        onMount={handleEditorDidMount}
        options={{
          wordWrap: "on",
          automaticLayout: true,
          minimap: { enabled: false },
          fontSize: 13,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          cursorBlinking: "smooth",
          tabSize: 2,
          renderWhitespace: "selection",
        }}
      />
    </div>
  );
};
