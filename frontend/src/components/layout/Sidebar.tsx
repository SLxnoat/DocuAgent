import { NavLink } from "react-router-dom";
import {
  Sparkles,
  ListTodo,
  Settings,
  ChevronLeft,
  ChevronRight,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const navItems = [
    { to: "/", label: "Studio", icon: Sparkles },
    { to: "/jobs", label: "Jobs", icon: ListTodo },
    { to: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r bg-card transition-all duration-300 select-none z-20",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center px-4 justify-between border-b">
        {!collapsed && (
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-black font-bold">
              <BookOpen className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm leading-tight text-foreground truncate">
                DocuAgent AI
              </span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
                Autonomous Writer
              </span>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-black font-bold">
            <BookOpen className="h-5 w-5" />
          </div>
        )}

        <Button
          variant="ghost"
          size="icon"
          className={cn("h-7 w-7 text-muted-foreground", collapsed && "hidden")}
          onClick={onToggle}
          title="Collapse sidebar"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all",
                  isActive
                    ? "bg-brand/15 text-brand dark:bg-brand/20 dark:text-brand-light font-semibold"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  collapsed && "justify-center px-2",
                )
              }
              title={collapsed ? item.label : undefined}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer controls: theme toggle & collapse expander */}
      <div className="p-3 border-t flex flex-col gap-2">
        <div
          className={cn(
            "flex items-center justify-between",
            collapsed && "flex-col gap-2",
          )}
        >
          {!collapsed && (
            <span className="text-xs text-muted-foreground font-medium">
              Theme
            </span>
          )}
          <ThemeToggle />
        </div>
        {collapsed && (
          <>
            <Separator />
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 mx-auto text-muted-foreground"
              onClick={onToggle}
              title="Expand sidebar"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </>
        )}
      </div>
    </aside>
  );
}
