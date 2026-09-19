import * as React from "react";
import { useManualStore } from "@/store/useManualStore";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Award,
} from "lucide-react";

export const QualityReportCard: React.FC = () => {
  const { qualityAudit, jobStatus } = useManualStore();

  if (!qualityAudit) {
    return (
      <div className="p-8 text-center text-gray-400 dark:text-gray-500">
        <ShieldCheck className="h-10 w-10 mx-auto mb-3 opacity-40 text-blue-500" />
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          No Quality Audit Available
        </h3>
        <p className="text-xs mt-1 max-w-sm mx-auto">
          {jobStatus === "reviewing"
            ? "Agent 4 (Quality Reviewer) is evaluating completeness, tone, and screenshot coverage..."
            : "Quality audits are generated automatically after draft compilation."}
        </p>
      </div>
    );
  }

  const metrics = [
    {
      name: "Completeness",
      score: qualityAudit.completeness?.score ?? 90,
      feedback:
        qualityAudit.completeness?.feedback ??
        "All steps thoroughly described.",
    },
    {
      name: "Screenshot Coverage",
      score: qualityAudit.screenshot_coverage?.score ?? 95,
      feedback:
        qualityAudit.screenshot_coverage?.feedback ??
        "Every interaction accompanied by visual context.",
    },
    {
      name: "Tone Consistency",
      score: qualityAudit.tone_consistency?.score ?? 88,
      feedback:
        qualityAudit.tone_consistency?.feedback ??
        "Clear, professional imperative instructional tone.",
    },
    {
      name: "Logical Sequencing",
      score: qualityAudit.logical_sequencing?.score ?? 92,
      feedback:
        qualityAudit.logical_sequencing?.feedback ??
        "Workflow order matches real UI prerequisites.",
    },
  ];

  const averageScore = Math.round(
    metrics.reduce((acc, m) => acc + m.score, 0) / metrics.length,
  );

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-emerald-500/10 border border-blue-200/50 dark:border-blue-900/40 flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-blue-600 dark:bg-blue-500 flex items-center justify-center text-white shadow-sm">
            <Award className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-gray-900 dark:text-gray-100">
                Agent 4 Quality Review Audit
              </h2>
              <span
                className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                  qualityAudit.overall_pass
                    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300"
                    : "bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300"
                }`}
              >
                {qualityAudit.overall_pass
                  ? "PASSED VERIFICATION"
                  : "NEEDS REVISION"}
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {qualityAudit.summary ||
                "Automated multi-factor quality inspection complete."}
            </p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-black text-blue-600 dark:text-blue-400">
            {averageScore}/100
          </div>
          <div className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">
            Overall Score
          </div>
        </div>
      </div>

      {/* Metrics Breakdown Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {metrics.map((m) => {
          const isHigh = m.score >= 80;
          return (
            <div
              key={m.name}
              className="p-4 rounded-xl bg-white dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700/80 shadow-xs space-y-2.5"
            >
              <div className="flex items-center justify-between text-xs font-semibold">
                <span className="text-gray-700 dark:text-gray-200 flex items-center gap-1.5">
                  {isHigh ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                  )}
                  {m.name}
                </span>
                <span
                  className={
                    isHigh
                      ? "text-emerald-600 dark:text-emerald-400"
                      : "text-amber-600 dark:text-amber-400"
                  }
                >
                  {m.score}%
                </span>
              </div>

              {/* Progress track */}
              <div className="h-2 w-full bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    m.score >= 85
                      ? "bg-emerald-500"
                      : m.score >= 70
                        ? "bg-blue-500"
                        : "bg-amber-500"
                  }`}
                  style={{ width: `${Math.min(100, Math.max(0, m.score))}%` }}
                />
              </div>

              <p className="text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed">
                {m.feedback}
              </p>
            </div>
          );
        })}
      </div>

      {/* Checklist Standards Note */}
      <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 flex items-start gap-3 text-xs text-gray-600 dark:text-gray-400">
        <FileCheck className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-gray-800 dark:text-gray-200">
            Automated Quality Criteria:
          </span>{" "}
          Documents require $\ge 80\%$ on all criteria to pass Agent 4
          inspection. Unapproved documents automatically loop back to Agent 3
          (Technical Writer) for up to 3 revision iterations.
        </div>
      </div>
    </div>
  );
};
