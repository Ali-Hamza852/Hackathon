export type DashboardView = "map" | "list";

interface ViewToggleProps {
  view: DashboardView;
  onChange: (view: DashboardView) => void;
}

export function ViewToggle({ view, onChange }: ViewToggleProps) {
  const baseClass = "flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition-colors sm:flex-none";
  const activeClass = "bg-emerald-700 text-white";
  const inactiveClass = "bg-white text-slate-600 hover:bg-slate-100";

  return (
    <div className="flex gap-1 rounded-xl border border-slate-200 bg-white p-1">
      <button
        type="button"
        onClick={() => onChange("map")}
        className={`${baseClass} ${view === "map" ? activeClass : inactiveClass}`}
      >
        Map
      </button>
      <button
        type="button"
        onClick={() => onChange("list")}
        className={`${baseClass} ${view === "list" ? activeClass : inactiveClass}`}
      >
        List
      </button>
    </div>
  );
}
