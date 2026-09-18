import { AppShell } from "./components/AppShell";
import { useManualStore } from "./store/useManualStore";
import { useEffect } from "react";

function App() {
  const { darkMode } = useManualStore();

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
      {/* Main application content will go here */}
      <div className="space-y-6">
        <div className="p-4 bg-card rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4">Welcome to DocuAgent AI</h2>
          <p className="text-muted-foreground">
            This is the main workspace where document generation and editing
            will take place.
          </p>
        </div>

        {/* Placeholder for the main content areas like editor, preview, chat, etc. */}
        <div className="grid grid-cols-1 gap-4">
          <div className="p-4 bg-card rounded-lg shadow">
            <h3 className="font-semibold mb-2">Editor Panel</h3>
            <p className="text-sm text-muted-foreground">
              Monaco Editor for Markdown editing will be placed here
            </p>
          </div>
          <div className="p-4 bg-card rounded-lg shadow">
            <h3 className="font-semibold mb-2">Preview Panel</h3>
            <p className="text-sm text-muted-foreground">
              Live preview of the generated documentation will be placed here
            </p>
          </div>
          <div className="p-4 bg-card rounded-lg shadow">
            <h3 className="font-semibold mb-2">Chat Panel</h3>
            <p className="text-sm text-muted-foreground">
              Conversational interface with Agent 5 will be placed here
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default App;
