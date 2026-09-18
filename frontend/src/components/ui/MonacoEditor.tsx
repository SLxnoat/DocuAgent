import * as React from "react";
import { Monaco } from "@monaco-editor/react";

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  onChange,
}) => {
  const [editor, setEditor] = useState<Monaco | null>(null);
  const [isSettingValue, setIsSettingValue] = useState<boolean>(false);
  const [hasSetValue, setHasSetValue] = useState<boolean>(false);

  // Use ref to store the previous selection to restore after setting value
  const prevSelectionRef = useReact.Monaco.Selection | (null > null);

  // When the editor instance is ready, set its value and handle changes
  React.useEffect(() => {
    if (!editor) return;

    // Set the editor's value if it's not already set (or if it's changed externally)
    if (!isSettingValue && editor.getValue() !== value) {
      // Save current selection
      const sel = editor.getSelection();
      prevSelectionRef.current = sel;

      setIsSettingValue(true);
      // We'll use the editor's executeEdits to change the value
      editor.executeEdits("", [
        {
          range: editor.getFullModelRange(),
          text: value,
          forceMoveMarkers: true,
        },
      ]);
      setIsSettingValue(false);
    }

    // If we haven't set the value at all (initial mount), set it now
    if (!hasSetValue) {
      setIsSettingValue(true);
      editor.setValue(value);
      setIsSettingValue(false);
      setHasSetValue(true);
    }
  }, [editor, value, isSettingValue, hasSetValue]);

  // Handle changes from the editor
  const handleEditorChange = (value: string) => {
    if (!isSettingValue) {
      onChange(value);
    }
  };

  // When the editor is loaded, we set up the editor
  const onMonacoLoad = (monaco: Monaco) => {
    setEditor(monaco);
  };

  return (
    <div className="h-full w-full">
      <Monaco
        height="100%"
        width="100%"
        language="markdown"
        theme="vs-dark"
        value={value}
        onChange={handleEditorChange}
        onLoad={onMonacoLoad}
        editorDidMount={editorDidMount}
        editorWillUnmount={editorWillUnmount}
        options={{
          wordWrap: "on",
          automaticLayout: true,
          readOnly: false,
          cursorBlinking: "solid",
        }}
      />
    </div>
  );

  function editorDidMount(editor: Monaco) {
    // We already have the editor in state, but we can also set it here if needed
    // We'll also set up a listener for external changes? Not needed.
  }

  function editorWillUnmount(editor: Monaco) {
    setEditor(null);
    setHasSetValue(false);
  }
};
