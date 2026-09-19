import * as React from "react";
import { useState } from "react";
import { useManualStore, type NavView } from "@/store/useManualStore";
import {
  LayoutDashboard,
  Sparkles,
  BookOpen,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Bot,
  ArrowUpRight,
} from "lucide-react";

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const { activeNavView, setActiveNavView, jobId, jobStatus, stepStatuses } =
    useManualStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems: Array<{
    id: NavView;
    label: string;
    icon: React.ReactNode;
    badge?: string;
  }> = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: <LayoutDashboard className="h-4 w-4 shrink-0" />,
    },
    {
      id: "input",
      label: "Workflow Studio",
      icon: <Sparkles className="h-4 w-4 shrink-0" />,
      badge: "New",
    },
    {
      id: "editor",
      label: "Manual Workspace",
      icon: <BookOpen className="h-4 w-4 shrink-0" />,
    },
    {
      id: "monitor",
      label: "Pipeline Monitor",
      icon: <Activity className="h-4 w-4 shrink-0" />,
      badge: jobId ? "Live" : undefined,
    },
    {
      id: "settings",
      label: "Preferences",
      icon: <Settings className="h-4 w-4 shrink-0" />,
    },
  ];

  return (
    <aside
      className={`flex flex-col border-r bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 transition-all duration-200 select-none shrink-0 ${
        isCollapsed ? "w-16" : "w-64"
      } ${className || ""}`}
    >
      {/* Sidebar Header */}
      <div className="p-3.5 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-2 pl-1.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              Workspace Navigation
            </span>
          </div>
        )}

        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 mx-auto transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Nav List */}
      <nav className="p-2 space-y-1 flex-1">
        {navItems.map((item) => {
          const isActive = activeNavView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveNavView(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                isActive
                  ? "bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-400 shadow-xs"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/60"
              }`}
              title={item.label}
            >
              <div className="flex items-center gap-3">
                <span
                  className={
                    isActive
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300"
                  }
                >
                  {item.icon}
                </span>
                {!isCollapsed && <span>{item.label}</span>}
              </div>

              {!isCollapsed && item.badge && (
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.2 rounded-md ${
                    item.badge === "Live"
                      ? "bg-blue-600 text-white animate-pulse"
                      : "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}

        {/* Live Active Job Mini-Card */}
        {jobId && !isCollapsed && (
          <div className="mt-6 mx-1 p-3.5 rounded-2xl bg-gradient-to-br from-blue-50/70 to-indigo-50/70 dark:from-gray-800/60 dark:to-gray-800/30 border border-blue-100 dark:border-gray-700/80 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-[11px] font-bold text-gray-700 dark:text-gray-300">
              <span className="flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-blue-500" />
                <span>Job Status</span>
              </span>
              <span
                className={`h-2 w-2 rounded-full ${
                  jobStatus === "completed"
                    ? "bg-emerald-500"
                    : jobStatus === "failed"
                      ? "bg-red-500"
                      : "bg-blue-500 animate-ping"
                }`}
              />
            </div>

            <div className="text-[11px] font-mono text-gray-500 dark:text-gray-400 truncate">
              {jobId.slice(0, 18)}...
            </div>

            <div className="flex items-center justify-between text-[11px] text-gray-600 dark:text-gray-400 pt-1">
              <span className="capitalize font-semibold text-blue-600 dark:text-blue-400">
                {jobStatus || "Ready"}
              </span>
              <span>{stepStatuses.length} steps</span>
            </div>

            <button
              onClick={() => setActiveNavView("monitor")}
              className="w-full text-center text-[10px] font-bold text-blue-600 dark:text-blue-400 hover:underline pt-1 flex items-center justify-center gap-1"
            >
              <span>Inspect Agents</span>
              <ArrowUpRight className="h-2.5 w-2.5" />
            </button>
          </div>
        )}
      </nav>

      {/* Sidebar Footer */}
      {!isCollapsed && (
        <div className="p-3 border-t border-gray-200 dark:border-gray-800 text-[11px] text-gray-400 flex items-center justify-between">
          <span className="flex items-center gap-1">
            <Bot className="h-3 w-3 text-blue-500" />
            <span>v1.0.0 Stable</span>
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="h-3 w-3 text-emerald-500" />
            <span>SSRF Safe</span>
          </span>
        </div>
      )}
    </aside>
  );
};
