import { useRef, useEffect } from "react";
import Editor, { OnMount } from "@monaco-editor/react";
import type * as monaco from "monaco-editor";
import { useManualStore } from "@/store/useManualStore";
import { useThemeStore } from "@/store/useThemeStore";

export function EditorPane() {
  const { markdownContent, setMarkdownContent } = useManualStore();
  const { resolvedTheme } = useThemeStore();
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  const handleMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  // Diff-aware update to prevent cursor jumping on external changes (SSE/Chat)
  useEffect(() => {
    const editor = editorRef.current;
    if (editor && markdownContent !== editor.getValue()) {
      const position = editor.getPosition();
      editor.setValue(markdownContent);
      if (position) {
        editor.setPosition(position);
      }
    }
  }, [markdownContent]);

  return (
    <div className="h-full w-full flex flex-col border rounded-lg overflow-hidden bg-background">
      <div className="flex items-center justify-between px-3 py-2 border-b bg-muted/40 text-xs font-mono text-muted-foreground select-none">
        <span className="font-semibold text-foreground">
          Markdown Source Editor
        </span>
        <span>Monaco Editor</span>
      </div>

      <div className="flex-1 min-h-0">
        <Editor
          height="100%"
          defaultLanguage="markdown"
          value={markdownContent}
          theme={resolvedTheme === "dark" ? "vs-dark" : "vs-light"}
          onChange={(value) => setMarkdownContent(value ?? "")}
          onMount={handleMount}
          options={{
            wordWrap: "on",
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            automaticLayout: true,
            fontFamily: "JetBrains Mono, Fira Code, monospace",
            tabSize: 2,
          }}
        />
      </div>
    </div>
  );
}
