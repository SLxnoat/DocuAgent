import { AppShell } from "./components/AppShell";
import { useManualStore } from "./store/useManualStore";
import { SplitScreen } from "./components/ui/SplitScreen";
import { useEffect } from "react";

function App() {
  const { darkMode, markdownContent, setMarkdownContent } = useManualStore();

  // Effect to handle dark mode class on html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <AppShell className="min-h-screen">
      <div className="flex flex-col h-full">
        {/* SplitScreen for Editor and Preview */}
        <SplitScreen
          value={markdownContent}
          onChange={setMarkdownContent}
          className="flex-1"
        />
        {/* Chat Panel */}
        <div className="border-t p-4">
          <h3 className="font-semibold mb-2">Chat Panel</h3>
          <p className="text-sm text-muted-foreground">
            Conversational interface with Agent 5 will be placed here
          </p>
        </div>
      </div>
    </AppShell>
  );
}

export default App;
