import * as React from "react";
import { useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import { generateManual } from "@/api/client";
import {
  Sparkles,
  Globe,
  KeyRound,
  User,
  ShieldCheck,
  Zap,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  HelpCircle,
  Play,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export const StudioView: React.FC = () => {
  const {
    targetUrl,
    setTargetUrl,
    rawScript,
    setRawScript,
    setJobId,
    setSessionId,
    setJobStatus,
    setActiveNavView,
    resetStepStatuses,
    showToast,
  } = useManualStore();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showAuthDrawer, setShowAuthDrawer] = useState(false);
  const [showAdvancedDrawer, setShowAdvancedDrawer] = useState(false);
  const [viewportPreset, setViewportPreset] = useState("desktop");
  const [language, setLanguage] = useState("en");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{
    url?: string;
    script?: string;
    general?: string;
  }>({});

  const validateUrl = (val: string): boolean => {
    try {
      const parsed = new URL(val);
      return parsed.protocol === "http:" || parsed.protocol === "https:";
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const newErrors: typeof errors = {};
    if (!targetUrl || !validateUrl(targetUrl)) {
      newErrors.url = "Please enter a valid HTTP or HTTPS staging URL.";
    }
    if (!rawScript || rawScript.trim().length < 10) {
      newErrors.script =
        "Workflow script must describe at least 1-2 steps (10+ characters).";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      showToast("Please correct the highlighted form errors.", "error");
      return;
    }

    setIsSubmitting(true);
    resetStepStatuses();

    try {
      const credentials =
        username && password ? { username, password } : undefined;

      const response = await generateManual({
        target_url: targetUrl,
        script: rawScript,
        credentials,
      });

      setJobId(response.job_id);
      setSessionId(response.session_id);
      setJobStatus("analyzing");

      showToast(
        "Multi-Agent pipeline dispatched! Navigating to Workspace...",
        "success",
      );
      setActiveNavView("editor");
    } catch (err: unknown) {
      console.error("Failed to generate manual:", err);
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to connect to backend service.";
      setErrors({ general: msg });
      showToast(msg, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50 p-6 sm:p-8 lg:p-10 max-w-4xl mx-auto w-full space-y-8">
      {/* Title Section */}
      <div className="space-y-1.5 border-b border-gray-200 dark:border-gray-800 pb-5">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950">
          <Zap className="h-3 w-3" />
          <span>Workflow Studio</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100">
          Script-to-Manual Generator
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
          Provide your target application address and step descriptions in
          natural English. Agent 1 will decompose interactions, Agent 2 will
          execute browser captures, Agent 3 will author the guide, and Agent 4
          will audit accuracy.
        </p>
      </div>

      {errors.general && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errors.general}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Target URL Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Globe className="h-4 w-4 text-blue-500" />
              <span>Target Application URL</span>
            </label>
            <span className="text-[11px] text-gray-400">
              Staging / Test Environment
            </span>
          </div>

          <div className="relative">
            <input
              type="text"
              value={targetUrl}
              onChange={(e) => {
                setTargetUrl(e.target.value);
                if (errors.url)
                  setErrors((prev) => ({ ...prev, url: undefined }));
              }}
              placeholder="https://staging.app.example.com"
              className={`w-full px-4 py-3 text-sm bg-gray-50/50 dark:bg-gray-900/60 border rounded-xl font-mono focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all ${
                errors.url
                  ? "border-red-400 dark:border-red-600 bg-red-50/20"
                  : "border-gray-200 dark:border-gray-700"
              }`}
            />
          </div>

          {errors.url ? (
            <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
              {errors.url}
            </p>
          ) : (
            <p className="text-[11px] text-gray-400">
              Target domain must resolve publicly. Internal loopback (127.0.0.1,
              RFC 1918) addresses are blocked by SSRF guardrails.
            </p>
          )}
        </div>

        {/* Step 2: Natural Language Script Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-500" />
              <span>Plain-English Workflow Script</span>
            </label>
            <span className="text-[11px] text-gray-400 font-mono">
              {rawScript.length} characters
            </span>
          </div>

          <textarea
            rows={7}
            value={rawScript}
            onChange={(e) => {
              setRawScript(e.target.value);
              if (errors.script)
                setErrors((prev) => ({ ...prev, script: undefined }));
            }}
            placeholder={`Example:
1. Log in with user credentials
2. Click Settings in the sidebar and choose Team Members
3. Click the Invite Member button
4. Enter email 'jane@example.com' and select Developer role
5. Click Send Invitation`}
            className={`w-full p-4 text-sm bg-gray-50/50 dark:bg-gray-900/60 border rounded-xl font-sans leading-relaxed focus:outline-hidden focus:ring-2 focus:ring-blue-500 transition-all ${
              errors.script
                ? "border-red-400 dark:border-red-600 bg-red-50/20"
                : "border-gray-200 dark:border-gray-700"
            }`}
          />

          {errors.script && (
            <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
              {errors.script}
            </p>
          )}

          <div className="p-3 rounded-xl bg-blue-50/50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/40 text-[11px] text-blue-700 dark:text-blue-300 flex items-start gap-2.5">
            <HelpCircle className="h-4 w-4 shrink-0 mt-0.5 text-blue-500" />
            <span>
              <strong>Writing Tip:</strong> Specify key button names, input
              labels, or tabs in quotes (e.g. &apos;Settings&apos;, &apos;Save
              Changes&apos;) so Agent 1 can generate resilient multi-strategy
              CSS and XPath selectors.
            </span>
          </div>
        </div>

        {/* Optional Authentication Drawer */}
        <div className="rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xs">
          <button
            type="button"
            onClick={() => setShowAuthDrawer(!showAuthDrawer)}
            className="w-full px-6 py-4 flex items-center justify-between text-xs font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <KeyRound className="h-4 w-4 text-emerald-500" />
              <span>Authentication Credentials (Optional)</span>
              <span className="text-[10px] bg-emerald-50 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded-full font-medium">
                Zero-Retention
              </span>
            </div>
            {showAuthDrawer ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>

          {showAuthDrawer && (
            <div className="p-6 border-t border-gray-100 dark:border-gray-800 space-y-4 bg-gray-50/30 dark:bg-gray-900/30">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 flex items-center gap-1.5">
                    <User className="h-3.5 w-3.5" />
                    <span>Username / Email</span>
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="admin@example.com"
                    className="w-full px-3.5 py-2.5 text-xs bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 flex items-center gap-1.5">
                    <KeyRound className="h-3.5 w-3.5" />
                    <span>Password</span>
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full px-3.5 py-2.5 text-xs bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 text-[11px] text-emerald-700 dark:text-emerald-300 font-medium">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span>
                  Security Policy: Passwords are wiped from memory immediately
                  following browser login before screenshots are taken.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Optional Advanced Settings Drawer */}
        <div className="rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xs">
          <button
            type="button"
            onClick={() => setShowAdvancedDrawer(!showAdvancedDrawer)}
            className="w-full px-6 py-4 flex items-center justify-between text-xs font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-purple-500" />
              <span>Advanced Pipeline Parameters</span>
            </div>
            {showAdvancedDrawer ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>

          {showAdvancedDrawer && (
            <div className="p-6 border-t border-gray-100 dark:border-gray-800 grid grid-cols-1 sm:grid-cols-2 gap-4 bg-gray-50/30 dark:bg-gray-900/30">
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5">
                  Browser Viewport Profile
                </label>
                <select
                  value={viewportPreset}
                  onChange={(e) => setViewportPreset(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
                >
                  <option value="desktop">Desktop HD (1920 × 1080)</option>
                  <option value="laptop">Standard Laptop (1440 × 900)</option>
                  <option value="tablet">Tablet / iPad (1024 × 768)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5">
                  Target Documentation Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl"
                >
                  <option value="en">English (US)</option>
                  <option value="es">Spanish (Español)</option>
                  <option value="fr">French (Français)</option>
                  <option value="de">German (Deutsch)</option>
                  <option value="ja">Japanese (日本語)</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="pt-2 flex items-center justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={() => {
              setTargetUrl("");
              setRawScript("");
              setUsername("");
              setPassword("");
            }}
            className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 gap-1.5"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Clear Form</span>
          </Button>

          <Button
            type="submit"
            size="lg"
            disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 shadow-md gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Launching Agents...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-white" />
                <span>Generate User Manual</span>
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};
