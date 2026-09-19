import { useEffect } from "react";
import { useManualStore } from "./store/useManualStore";
import { Sidebar } from "./components/sidebar";
import { StatusHeader } from "./components/status-header";
import { DashboardView } from "./components/views/DashboardView";
import { StudioView } from "./components/views/StudioView";
import { EditorView } from "./components/views/EditorView";
import { PipelineMonitorView } from "./components/views/PipelineMonitorView";
import { SettingsView } from "./components/views/SettingsView";
import { Toast } from "./components/ui/Toast";
import { useSSEStream } from "./hooks/useSSEStream";

export function App() {
  const { darkMode, activeNavView, setActiveNavView, jobId } = useManualStore();

  // Synchronize dark mode class on <html> document element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  // Connect SSE progress stream when jobId is active
  useSSEStream(jobId);

  // Global keyboard shortcuts (Ctrl/Cmd+K for Studio, Ctrl/Cmd+D for Dashboard)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setActiveNavView("input");
      } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "d") {
        e.preventDefault();
        setActiveNavView("dashboard");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setActiveNavView]);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100 antialiased font-sans">
      {/* Top Navigation & Status Context Header */}
      <StatusHeader />

      {/* Main App Layout: Collapsible Sidebar + Dynamic View Container */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        <Sidebar className="hidden md:flex" />

        <main className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden bg-white dark:bg-gray-900">
          {activeNavView === "dashboard" && <DashboardView />}
          {activeNavView === "input" && <StudioView />}
          {activeNavView === "editor" && <EditorView />}
          {activeNavView === "monitor" && <PipelineMonitorView />}
          {activeNavView === "settings" && <SettingsView />}
        </main>
      </div>

      {/* Global Interactive Toast Notification System */}
      <Toast />
    </div>
  );
}

export default App;
