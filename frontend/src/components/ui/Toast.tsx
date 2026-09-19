import * as React from "react";
import { useManualStore } from "@/store/useManualStore";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export const Toast: React.FC = () => {
  const { toast, clearToast } = useManualStore();

  if (!toast) return null;

  const icons = {
    info: <Info className="h-4 w-4 text-blue-500 shrink-0" />,
    success: <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />,
    error: <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />,
  };

  const bgClasses = {
    info: "border-blue-200 dark:border-blue-900 bg-white dark:bg-gray-850",
    success:
      "border-emerald-200 dark:border-emerald-900 bg-white dark:bg-gray-850",
    error: "border-red-200 dark:border-red-900 bg-white dark:bg-gray-850",
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 animate-in fade-in slide-in-from-bottom-5 duration-200">
      <div
        className={`flex items-center gap-2.5 px-4 py-3 rounded-xl border shadow-xl text-xs font-medium text-gray-900 dark:text-gray-100 ${
          bgClasses[toast.type]
        }`}
      >
        {icons[toast.type]}
        <span>{toast.text}</span>
        <button
          onClick={clearToast}
          className="ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-0.5 rounded-md"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
};
