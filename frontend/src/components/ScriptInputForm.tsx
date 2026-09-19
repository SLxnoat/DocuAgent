import * as React from "react";
import { useManualStore } from "@/store/useManualStore";
import { generateManual } from "@/api/client";
import {
  Sparkles,
  Globe,
  KeyRound,
  User,
  RotateCcw,
  AlertTriangle,
  FileText,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface ScriptInputFormProps {
  onSuccess?: () => void;
}

interface WorkflowTemplate {
  title: string;
  url: string;
  script: string;
}

const SAMPLE_TEMPLATES: WorkflowTemplate[] = [
  {
    title: "Team Invite (SaaS Admin)",
    url: "https://staging.app.example.com",
    script:
      "Log in to the dashboard using administrative credentials. In the left navigation menu, open 'Settings' and select 'Team Members'. Click the primary 'Invite Member' button in the top right. In the modal dialog, input user email 'jane.doe@example.com', set the Role dropdown to 'Developer', and click 'Send Invitation' to confirm.",
  },
  {
    title: "E-Commerce Checkout",
    url: "https://shop.example.com",
    script:
      "Navigate to the product catalog, select 'Electronics', and click on 'Noise-Cancelling Headphones'. Click the blue 'Add to Cart' button. Open the shopping cart drawer, verify item quantity is 1, and click 'Proceed to Checkout'. Enter shipping address details and select 'Standard Express'. Click 'Review Order'.",
  },
  {
    title: "API Key Generation",
    url: "https://cloud-console.example.com",
    script:
      "Sign in to the Cloud Console. Select the target project 'Production-Cluster'. In the Security sidebar, click 'API Credentials'. Click the '+ Create API Key' button. Assign scopes for 'Read Metrics' and 'Deploy Services'. Enter key description 'CI/CD Pipeline Runner' and click 'Generate'.",
  },
];

export function ScriptInputForm({ onSuccess }: ScriptInputFormProps) {
  const {
    setJobId,
    setSessionId,
    setJobStatus,
    reset,
    resetStepStatuses,
    setDefaultLanguage,
    setPreferredOutputFormat,
    defaultLanguage,
    preferredOutputFormat,
    exportFormats,
    showToast,
  } = useManualStore();

  const [script, setScript] = React.useState("");
  const [url, setUrl] = React.useState("");
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [formErrors, setFormErrors] = React.useState<{
    script?: string;
    url?: string;
    username?: string;
    password?: string;
    general?: string;
  }>({});

  const applyTemplate = (template: WorkflowTemplate) => {
    setScript(template.script);
    setUrl(template.url);
    setFormErrors({});
    showToast(`Applied sample template: "${template.title}"`, "info");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors({});

    let isValid = true;
    const errors: typeof formErrors = {};

    if (!script || script.trim().length < 10) {
      errors.script = "Script must be at least 10 characters long.";
      isValid = false;
    }

    if (!url) {
      errors.url = "Staging application URL is required.";
      isValid = false;
    } else {
      try {
        const parsed = new URL(url);
        if (!parsed.protocol.startsWith("http")) {
          throw new Error("Protocol must be http or https");
        }
      } catch {
        errors.url = "Please enter a valid HTTP/HTTPS URL.";
        isValid = false;
      }
    }

    if (!isValid) {
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);
    setJobStatus("queued");
    resetStepStatuses();

    try {
      const response = await generateManual({
        script: script.trim(),
        target_url: url.trim(),
        credentials:
          username || password
            ? {
                username: username || undefined,
                password: password || undefined,
              }
            : undefined,
        options: {
          language: defaultLanguage,
          output_formats: [preferredOutputFormat as any],
        },
      });

      // Immediate zero-retention credential wiping
      setUsername("");
      setPassword("");

      setJobId(response.job_id);
      setSessionId(response.session_id);
      setJobStatus("analyzing");

      showToast("Manual generation started successfully!", "success");

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error("Failed to start generation job:", error);
      const msg =
        error?.response?.data?.error?.message ||
        error?.message ||
        "Failed to submit generation job. Please verify your backend connection.";
      setFormErrors({ general: msg });
      setJobStatus("failed");
      showToast(msg, "error");
    } finally {
      setIsSubmitting(false);
      setUsername("");
      setPassword("");
    }
  };

  const charCount = script.trim().length;

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white dark:bg-gray-850 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm my-6">
      {/* Header */}
      <div className="mb-6 border-b border-gray-100 dark:border-gray-800 pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-gray-900 dark:text-gray-100">
                New User Manual Generator
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Multi-agent pipeline: parses workflow, automates browser, and
                synthesizes documentation.
              </p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 text-[11px] font-medium">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Zero-Retention Auth</span>
          </div>
        </div>

        {/* 1-Click Sample Workflow Chips */}
        <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800/80">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 mb-2 font-medium">
            <Zap className="h-3.5 w-3.5 text-amber-500" />
            <span>Try a quick sample workflow:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_TEMPLATES.map((tmpl, i) => (
              <button
                key={i}
                type="button"
                onClick={() => applyTemplate(tmpl)}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-blue-50 hover:text-blue-700 dark:hover:bg-blue-950/50 dark:hover:text-blue-300 border border-transparent hover:border-blue-200 dark:hover:border-blue-800 transition-all flex items-center gap-1"
              >
                <FileText className="h-3 w-3" />
                <span>{tmpl.title}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {formErrors.general && (
          <div className="rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 p-3.5 flex items-center gap-2 text-xs text-red-700 dark:text-red-300">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{formErrors.general}</span>
          </div>
        )}

        {/* Workflow Script */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              Workflow Script / Steps <span className="text-red-500">*</span>
            </label>
            <span
              className={`text-[11px] font-mono ${
                charCount >= 10
                  ? "text-emerald-600 dark:text-emerald-400"
                  : "text-gray-400"
              }`}
            >
              {charCount} chars {charCount < 10 && "(min 10)"}
            </span>
          </div>

          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Describe the workflow steps you want to document in plain language..."
            rows={7}
            className={`block w-full rounded-xl border bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
              formErrors.script
                ? "border-red-500 focus:ring-red-500"
                : "border-gray-300 dark:border-gray-700"
            }`}
          />
          {formErrors.script && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {formErrors.script}
            </p>
          )}
        </div>

        {/* Staging URL */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
            Target Application URL <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <Globe className="h-4 w-4" />
            </div>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://staging.app.example.com"
              className={`block w-full pl-9 pr-3 py-2.5 rounded-xl border bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
                formErrors.url
                  ? "border-red-500 focus:ring-red-500"
                  : "border-gray-300 dark:border-gray-700"
              }`}
            />
          </div>
          {formErrors.url && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {formErrors.url}
            </p>
          )}
        </div>

        {/* Credentials (Optional & Ephemeral) */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-750 p-4 bg-gray-50/60 dark:bg-gray-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
              <KeyRound className="h-3.5 w-3.5 text-blue-500" />
              <span>Staging Credentials (Optional)</span>
            </span>
            <span className="text-[11px] text-gray-500 dark:text-gray-400">
              Wiped from memory upon login
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <User className="h-4 w-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Username / Email"
                  autoComplete="off"
                  className="block w-full pl-9 pr-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <KeyRound className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  autoComplete="new-password"
                  className="block w-full pl-9 pr-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Options: Language & Export Format */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Target Language
            </label>
            <select
              value={defaultLanguage}
              onChange={(e) => setDefaultLanguage(e.target.value)}
              className="block w-full px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English (en)</option>
              <option value="es">Spanish (es)</option>
              <option value="fr">French (fr)</option>
              <option value="de">German (de)</option>
              <option value="ja">Japanese (ja)</option>
              <option value="zh">Chinese (zh)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">
              Preferred Export Format
            </label>
            <select
              value={preferredOutputFormat}
              onChange={(e) => setPreferredOutputFormat(e.target.value)}
              className="block w-full px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {exportFormats.map((format) => (
                <option key={format} value={format}>
                  {format.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-800 gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setScript("");
              setUrl("");
              setUsername("");
              setPassword("");
              setFormErrors({});
              reset();
            }}
            className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-300"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </Button>

          <Button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 max-w-xs font-semibold h-10 bg-blue-600 hover:bg-blue-700 text-white shadow-xs"
          >
            {isSubmitting
              ? "Dispatching 5-Agent Pipeline..."
              : "Generate User Manual"}
          </Button>
        </div>
      </form>
    </div>
  );
}
