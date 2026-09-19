import * as React from "react";
import { useManualStore } from "@/store/useManualStore";
import { Settings, Moon, Sun, Globe, Trash2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";

export const SettingsView: React.FC = () => {
  const {
    darkMode,
    toggleDarkMode,
    defaultLanguage,
    setDefaultLanguage,
    preferredOutputFormat,
    setPreferredOutputFormat,
    reset,
    showToast,
  } = useManualStore();

  const handleClearAll = () => {
    if (
      window.confirm(
        "Are you sure you want to reset all current workspace session data?",
      )
    ) {
      reset();
      showToast("Workspace state reset to factory defaults.", "info");
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50 p-6 sm:p-8 lg:p-10 space-y-8 max-w-4xl mx-auto w-full">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 pb-5">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800">
          <Settings className="h-3 w-3" />
          <span>Application Settings</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 mt-1">
          Preferences & Environment
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Configure appearance, default document export behavior, and persistent
          local storage.
        </p>
      </div>

      <div className="space-y-6">
        {/* Appearance Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 shadow-xs space-y-4">
          <h2 className="text-sm font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            {darkMode ? (
              <Moon className="h-4 w-4 text-blue-400" />
            ) : (
              <Sun className="h-4 w-4 text-amber-500" />
            )}
            <span>Appearance & Theme</span>
          </h2>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                Dark Mode
              </p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400">
                Switch between high-contrast dark theme and crisp daytime light
                theme.
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={toggleDarkMode}
              className="text-xs gap-2 border-gray-200 dark:border-gray-700"
            >
              {darkMode ? (
                <Sun className="h-3.5 w-3.5 text-amber-400" />
              ) : (
                <Moon className="h-3.5 w-3.5" />
              )}
              <span>{darkMode ? "Light Theme" : "Dark Theme"}</span>
            </Button>
          </div>
        </div>

        {/* Generation Defaults Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 shadow-xs space-y-4">
          <h2 className="text-sm font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Globe className="h-4 w-4 text-indigo-500" />
            <span>Generation & Language Defaults</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                Default Documentation Language
              </label>
              <select
                value={defaultLanguage}
                onChange={(e) => {
                  setDefaultLanguage(e.target.value);
                  showToast(
                    `Default language set to ${e.target.value}`,
                    "info",
                  );
                }}
                className="w-full px-3.5 py-2 text-xs bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
              >
                <option value="en">English (United States)</option>
                <option value="es">Spanish (Español)</option>
                <option value="fr">French (Français)</option>
                <option value="de">German (Deutsch)</option>
                <option value="ja">Japanese (日本語)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                Preferred Export Format
              </label>
              <select
                value={preferredOutputFormat}
                onChange={(e) => {
                  setPreferredOutputFormat(e.target.value);
                  showToast(
                    `Preferred export set to ${e.target.value.toUpperCase()}`,
                    "info",
                  );
                }}
                className="w-full px-3.5 py-2 text-xs bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
              >
                <option value="pdf">Print-Ready PDF (.pdf)</option>
                <option value="html">Standalone HTML (.html)</option>
                <option value="markdown">GitHub-Flavored Markdown (.md)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Local Storage & Session State Management */}
        <div className="p-6 rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 shadow-xs space-y-4">
          <h2 className="text-sm font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Trash2 className="h-4 w-4 text-red-500" />
            <span>Workspace Storage & Reset</span>
          </h2>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                Reset Active Session State
              </p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400">
                Clears current job ID, active markdown editor content, and chat
                history.
              </p>
            </div>

            <Button
              variant="destructive"
              size="sm"
              onClick={handleClearAll}
              className="text-xs gap-1.5 shrink-0"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Reset Workspace</span>
            </Button>
          </div>
        </div>

        {/* About & System Runtime Spec */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50/50 to-indigo-50/50 dark:from-gray-850 dark:to-gray-850 border border-blue-100 dark:border-gray-800 space-y-3 text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2 font-bold text-gray-900 dark:text-gray-200 text-sm">
            <Info className="h-4 w-4 text-blue-500" />
            <span>DocuAgent AI v1.0.0 Production Build</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-[11px]">
            <div>FastAPI: 0.115+</div>
            <div>LangGraph: 0.2.28</div>
            <div>Playwright: 1.47</div>
            <div>React: 19.2 (Vite 8)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
