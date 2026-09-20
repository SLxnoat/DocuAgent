import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Theme } from "@/types";

interface ThemeStore {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (t: Theme) => void;
}

function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function applyTheme(resolved: "light" | "dark") {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.classList.toggle("dark", resolved === "dark");
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: "system" as Theme,
      resolvedTheme: getSystemTheme(),

      setTheme: (t) => {
        const resolved = t === "system" ? getSystemTheme() : t;
        applyTheme(resolved);
        set({ theme: t, resolvedTheme: resolved });
      },
    }),
    { name: "docuagent-theme" },
  ),
);

// Listen for OS theme changes when in 'system' mode
if (typeof window !== "undefined") {
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const { theme, setTheme } = useThemeStore.getState();
      if (theme === "system") setTheme("system");
    });

  // Apply theme on initial load
  const { theme, setTheme } = useThemeStore.getState();
  setTheme(theme);
}
