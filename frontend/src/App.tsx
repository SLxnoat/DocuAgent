import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { StudioView } from "@/views/StudioView";

export function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<StudioView />} />
          {/* Fallback routes */}
          <Route
            path="/jobs"
            element={
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-muted-foreground text-sm">
                <h2 className="text-lg font-semibold text-foreground mb-1">
                  Job History
                </h2>
                <p>
                  View previous manual generation runs and exported documents.
                </p>
                <span className="text-xs text-brand mt-2 font-mono">
                  Status: Connected to Redis task backend
                </span>
              </div>
            }
          />
          <Route
            path="/settings"
            element={
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-muted-foreground text-sm">
                <h2 className="text-lg font-semibold text-foreground mb-1">
                  Settings & Integration
                </h2>
                <p>
                  Configure Ollama inference endpoints and Playwright capture
                  parameters.
                </p>
                <span className="text-xs text-brand mt-2 font-mono">
                  Backend: FastAPI 1.0.0
                </span>
              </div>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;
