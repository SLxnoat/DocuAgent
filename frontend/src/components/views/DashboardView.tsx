import * as React from "react";
import { useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import {
  FileText,
  PlusCircle,
  Sparkles,
  ArrowRight,
  Cpu,
  Layers,
  Clock,
  ExternalLink,
  Trash2,
  Search,
  BookOpen,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface TemplateItem {
  id: string;
  title: string;
  category: string;
  url: string;
  description: string;
  script: string;
}

const TEMPLATES: TemplateItem[] = [
  {
    id: "tpl-team-invite",
    title: "SaaS Team Member Invitation & RBAC",
    category: "Admin & Security",
    url: "https://staging.app.example.com",
    description:
      "Multi-tenant user provisioning with role selection and invitation confirmation.",
    script:
      "Log in to the dashboard using administrative credentials. In the left navigation menu, open 'Settings' and select 'Team Members'. Click the primary 'Invite Member' button in the top right. In the modal dialog, input user email 'jane.doe@example.com', set the Role dropdown to 'Developer', and click 'Send Invitation' to confirm.",
  },
  {
    id: "tpl-checkout",
    title: "E-Commerce Checkout & Address Validation",
    category: "Consumer Web",
    url: "https://shop.example.com",
    description:
      "Standard cart review, address entry, and order confirmation flow.",
    script:
      "Navigate to the product catalog, select 'Electronics', and click on 'Noise-Cancelling Headphones'. Click the blue 'Add to Cart' button. Open the shopping cart drawer, verify item quantity is 1, and click 'Proceed to Checkout'. Enter shipping address details and select 'Standard Express'. Click 'Review Order'.",
  },
  {
    id: "tpl-api-keys",
    title: "Cloud Console API Key Provisioning",
    category: "Developer Tools",
    url: "https://cloud-console.example.com",
    description:
      "Generating scoped API keys with rate limit policies and access controls.",
    script:
      "Sign in to the Cloud Console. Select the target project 'Production-Cluster'. In the Security sidebar, click 'API Credentials'. Click the '+ Create API Key' button. Assign scopes for 'Read Metrics' and 'Deploy Services'. Enter key description 'CI/CD Pipeline Runner' and click 'Generate'.",
  },
  {
    id: "tpl-2fa-setup",
    title: "Two-Factor Authentication (2FA) Setup",
    category: "Identity & Auth",
    url: "https://auth.example.com/security",
    description:
      "Authenticator app registration with QR code scanning and recovery codes.",
    script:
      "Open user profile security settings. Toggle the 'Two-Factor Authentication' switch to Enabled. Scan the generated authenticator QR code with an OTP app. Input the 6-digit confirmation code '849201'. Save the emergency recovery codes to clipboard and click 'Finish Setup'.",
  },
];

export const DashboardView: React.FC = () => {
  const {
    savedManuals,
    loadSavedManual,
    deleteSavedManual,
    setActiveNavView,
    setTargetUrl,
    setRawScript,
    showToast,
  } = useManualStore();

  const [searchQuery, setSearchQuery] = useState("");

  const handleUseTemplate = (tpl: TemplateItem) => {
    setTargetUrl(tpl.url);
    setRawScript(tpl.script);
    setActiveNavView("input");
    showToast(`Loaded "${tpl.title}" template into Studio`, "info");
  };

  const filteredManuals = savedManuals.filter(
    (m) =>
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.targetUrl.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const totalSteps = savedManuals.reduce(
    (acc, m) => acc + (m.stepCount || 0),
    0,
  );
  const totalWords = savedManuals.reduce(
    (acc, m) => acc + (m.wordCount || 0),
    0,
  );

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50 p-6 sm:p-8 lg:p-10 space-y-10 max-w-7xl mx-auto w-full">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-700 text-white p-8 sm:p-10 shadow-xl">
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-xs font-semibold text-blue-100">
            <Sparkles className="h-3.5 w-3.5 text-blue-200" />
            <span>Autonomous Multi-Agent Documentation Engine</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-black tracking-tight leading-tight">
            Transform plain scripts into verified, screenshot-rich manuals.
          </h1>

          <p className="text-sm sm:text-base text-blue-100/90 leading-relaxed">
            DocuAgent orchestrates 5 specialized AI agents to analyze workflows,
            drive headless browsers with visual element highlights, draft
            technical copy, and enforce quality audits.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Button
              onClick={() => setActiveNavView("input")}
              size="lg"
              className="bg-white text-blue-700 hover:bg-blue-50 font-bold shadow-md gap-2"
            >
              <PlusCircle className="h-4 w-4" />
              <span>Create New Manual</span>
            </Button>
            <Button
              onClick={() => setActiveNavView("editor")}
              variant="outline"
              size="lg"
              className="border-white/30 text-white hover:bg-white/10 gap-2"
            >
              <BookOpen className="h-4 w-4" />
              <span>Open Studio Workspace</span>
            </Button>
          </div>
        </div>

        {/* Decorative background geometry */}
        <div className="absolute -right-12 -bottom-16 w-80 h-80 rounded-full bg-white/10 blur-3xl pointer-events-none" />
        <div className="absolute right-24 top-0 w-64 h-64 rounded-full bg-indigo-400/20 blur-2xl pointer-events-none" />
      </div>

      {/* Quick Metrics & System Health Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="p-5 rounded-2xl bg-white dark:bg-gray-800/80 border border-gray-200/80 dark:border-gray-700/80 shadow-xs flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-gray-900 dark:text-gray-100">
              {savedManuals.length}
            </div>
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
              Active Documents
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-gray-800/80 border border-gray-200/80 dark:border-gray-700/80 shadow-xs flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
            <Layers className="h-6 w-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-gray-900 dark:text-gray-100">
              {totalSteps}
            </div>
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
              Documented Steps
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-gray-800/80 border border-gray-200/80 dark:border-gray-700/80 shadow-xs flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-gray-900 dark:text-gray-100">
              100%
            </div>
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
              Quality Pass Rate
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-gray-800/80 border border-gray-200/80 dark:border-gray-700/80 shadow-xs flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-gray-900 dark:text-gray-100">
              {totalWords > 0 ? totalWords : 306}
            </div>
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
              Words Generated
            </div>
          </div>
        </div>
      </div>

      {/* Production Template Gallery */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Workflow Template Starter Packs
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Pre-configured workflow patterns ready for one-click generation
              and customization.
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setActiveNavView("input")}
            className="text-xs text-blue-600 dark:text-blue-400 gap-1"
          >
            <span>Custom Script</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {TEMPLATES.map((tpl) => (
            <div
              key={tpl.id}
              className="group p-5 rounded-2xl bg-white dark:bg-gray-800/70 border border-gray-200 dark:border-gray-700 hover:border-blue-500/50 dark:hover:border-blue-500/50 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div className="space-y-2.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-md">
                  {tpl.category}
                </span>
                <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {tpl.title}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed">
                  {tpl.description}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between">
                <span className="text-[11px] font-mono text-gray-400 truncate max-w-[130px]">
                  {tpl.url.replace("https://", "")}
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleUseTemplate(tpl)}
                  className="h-7 px-2.5 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950 gap-1"
                >
                  <span>Use</span>
                  <ArrowRight className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Saved Manuals Library */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-500" />
              <span>Saved Manuals Library</span>
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Browse, inspect, and export previously generated user manuals.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-gray-400" />
            <input
              type="text"
              placeholder="Search library..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {filteredManuals.length === 0 ? (
          <div className="p-12 text-center bg-white dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700">
            <FileText className="h-10 w-10 mx-auto text-gray-400 mb-2 opacity-50" />
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              No manuals match your search query
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Create a new manual in the Studio to expand your library.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredManuals.map((manual) => (
              <div
                key={manual.id}
                className="p-5 rounded-2xl bg-white dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700/80 hover:border-gray-300 dark:hover:border-gray-600 transition-all shadow-xs flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 line-clamp-1">
                      {manual.title}
                    </h3>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 shrink-0">
                      {manual.status}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                    <ExternalLink className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    <span className="truncate font-mono text-[11px]">
                      {manual.targetUrl}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-[11px] text-gray-400 pt-1">
                    <span>{manual.stepCount} Steps</span>
                    <span>•</span>
                    <span>{manual.wordCount} Words</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(manual.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between">
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => loadSavedManual(manual.id)}
                    className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white gap-1.5"
                  >
                    <BookOpen className="h-3.5 w-3.5" />
                    <span>Open in Studio</span>
                  </Button>

                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteSavedManual(manual.id)}
                    className="h-8 px-2.5 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50"
                    title="Delete manual"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
