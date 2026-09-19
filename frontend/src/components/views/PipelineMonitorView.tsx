import * as React from "react";
import { useState } from "react";
import { useManualStore } from "@/store/useManualStore";
import {
  Activity,
  Bot,
  Camera,
  FileCode,
  ShieldCheck,
  MessageSquare,
  Terminal,
  Trash2,
  Copy,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export const PipelineMonitorView: React.FC = () => {
  const {
    jobId,
    sessionId,
    jobStatus,
    stepStatuses,
    stepErrors,
    eventsLog,
    clearEventLogs,
    showToast,
  } = useManualStore();

  const [filterType, setFilterType] = useState<string>("all");
  const [copiedState, setCopiedState] = useState(false);

  const agents = [
    {
      id: 1,
      name: "Agent 1: Script Analyzer",
      role: "Workflow Decomposition & DOM Selector Inference",
      status:
        jobStatus === "analyzing"
          ? "active"
          : jobStatus && jobStatus !== "idle"
            ? "completed"
            : "pending",
      icon: <Bot className="h-5 w-5" />,
    },
    {
      id: 2,
      name: "Agent 2: Playwright Capturer",
      role: "Headless Browser Navigation & Dynamic Visual Highlighting",
      status:
        jobStatus === "capturing"
          ? "active"
          : ["compiling", "reviewing", "awaiting_input", "completed"].includes(
                jobStatus || "",
              )
            ? "completed"
            : "pending",
      icon: <Camera className="h-5 w-5" />,
    },
    {
      id: 3,
      name: "Agent 3: Technical Writer",
      role: "Markdown Compilation, Steps & Troubleshooting Sections",
      status:
        jobStatus === "compiling"
          ? "active"
          : ["reviewing", "awaiting_input", "completed"].includes(
                jobStatus || "",
              )
            ? "completed"
            : "pending",
      icon: <FileCode className="h-5 w-5" />,
    },
    {
      id: 4,
      name: "Agent 4: Quality Reviewer",
      role: "Multi-Criteria Rubric Audit & Cyclic Revision Edge",
      status:
        jobStatus === "reviewing"
          ? "active"
          : ["awaiting_input", "completed"].includes(jobStatus || "")
            ? "completed"
            : "pending",
      icon: <ShieldCheck className="h-5 w-5" />,
    },
    {
      id: 5,
      name: "Agent 5: Interactive Refiner",
      role: "Human-in-the-Loop Conversational Chat & Targeted Diffs",
      status:
        jobStatus === "awaiting_input" || jobStatus === "refining"
          ? "active"
          : jobStatus === "completed"
            ? "completed"
            : "pending",
      icon: <MessageSquare className="h-5 w-5" />,
    },
  ];

  const filteredEvents = eventsLog.filter((evt) => {
    if (filterType === "all") return true;
    if (filterType === "capture")
      return evt.type.includes("capture") || evt.type.includes("screenshot");
    if (filterType === "quality") return evt.type.includes("quality");
    if (filterType === "error")
      return evt.type.includes("fail") || evt.type.includes("error");
    return true;
  });

  const handleCopyState = async () => {
    const stateSnapshot = {
      jobId,
      sessionId,
      jobStatus,
      stepCount: stepStatuses.length,
      stepStatuses,
      stepErrors,
    };
    try {
      await navigator.clipboard.writeText(
        JSON.stringify(stateSnapshot, null, 2),
      );
      setCopiedState(true);
      showToast("State snapshot copied to clipboard!", "success");
      setTimeout(() => setCopiedState(false), 2000);
    } catch {
      showToast("Failed to copy state snapshot", "error");
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50 p-6 sm:p-8 lg:p-10 space-y-8 max-w-6xl mx-auto w-full">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950">
            <Activity className="h-3 w-3" />
            <span>Agent Orchestration Monitor</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 mt-1">
            LangGraph Multi-Agent Pipeline
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            Real-time inspection of active job execution, agent transition
            states, and Redis SSE event emissions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyState}
            className="text-xs gap-1.5 border-gray-200 dark:border-gray-700"
          >
            {copiedState ? (
              <Check className="h-3.5 w-3.5 text-emerald-500" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
            <span>Copy State Snapshot</span>
          </Button>
        </div>
      </div>

      {/* Active Pipeline Nodes Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300">
          Agent State Machine Topology
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {agents.map((agent, i) => {
            const isActive = agent.status === "active";
            const isDone = agent.status === "completed";

            return (
              <div
                key={agent.id}
                className={`p-4 rounded-2xl border transition-all flex flex-col justify-between space-y-3 ${
                  isActive
                    ? "bg-blue-50/80 dark:bg-blue-950/40 border-blue-500 shadow-md ring-2 ring-blue-500/20"
                    : isDone
                      ? "bg-white dark:bg-gray-850 border-emerald-300/80 dark:border-emerald-900/60 shadow-xs"
                      : "bg-white/60 dark:bg-gray-850/40 border-gray-200 dark:border-gray-800 opacity-60"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div
                      className={`h-9 w-9 rounded-xl flex items-center justify-center ${
                        isActive
                          ? "bg-blue-600 text-white animate-pulse"
                          : isDone
                            ? "bg-emerald-600 text-white"
                            : "bg-gray-100 dark:bg-gray-800 text-gray-400"
                      }`}
                    >
                      {agent.icon}
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        isActive
                          ? "bg-blue-200 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
                          : isDone
                            ? "bg-emerald-100 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100"
                            : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                      }`}
                    >
                      {agent.status}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-xs font-bold text-gray-900 dark:text-gray-100">
                      {agent.name}
                    </h3>
                    <p className="text-[11px] text-gray-500 dark:text-gray-400 leading-snug mt-1 line-clamp-3">
                      {agent.role}
                    </p>
                  </div>
                </div>

                <div className="text-[10px] font-mono text-gray-400 pt-2 border-t border-gray-100 dark:border-gray-800">
                  Node #{i + 1}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Event Log Stream */}
      <div className="rounded-2xl bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xs space-y-0">
        {/* Terminal Header Bar */}
        <div className="px-5 py-3.5 bg-gray-50 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-800 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-gray-600 dark:text-gray-300" />
            <span className="text-xs font-bold text-gray-800 dark:text-gray-200">
              Live Redis Pub/Sub Event Stream
            </span>
            <span className="text-[11px] font-mono text-gray-400">
              ({eventsLog.length} events logged)
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Filter Pills */}
            <div className="flex items-center bg-gray-100 dark:bg-gray-700/80 p-0.5 rounded-lg text-[11px]">
              {["all", "capture", "quality", "error"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilterType(f)}
                  className={`px-2 py-0.5 rounded-md capitalize font-semibold transition-all ${
                    filterType === f
                      ? "bg-white dark:bg-gray-850 text-gray-900 dark:text-gray-100 shadow-xs"
                      : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>

            <Button
              size="sm"
              variant="ghost"
              onClick={clearEventLogs}
              className="h-7 text-xs text-gray-500 hover:text-red-600 gap-1"
            >
              <Trash2 className="h-3 w-3" />
              <span>Clear</span>
            </Button>
          </div>
        </div>

        {/* Terminal Event Body */}
        <div className="p-4 max-h-96 overflow-y-auto space-y-2 font-mono text-xs bg-gray-950 text-gray-200">
          {filteredEvents.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              No SSE stream events received yet for current session.
            </div>
          ) : (
            filteredEvents.map((evt) => (
              <div
                key={evt.id}
                className="p-2.5 rounded-lg bg-gray-900/90 border border-gray-800 hover:border-gray-700 transition-colors flex items-start justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 text-[10px]">
                      {evt.timestamp}
                    </span>
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-950 text-blue-400 border border-blue-800">
                      {evt.type}
                    </span>
                  </div>
                  <pre className="text-[11px] text-gray-300 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(evt.payload, null, 2)}
                  </pre>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
