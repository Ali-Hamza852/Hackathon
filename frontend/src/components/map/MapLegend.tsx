import { TIER_LABELS } from "../../constants/tiers";
import type { Tier } from "../../api/types";
import { TIER_BG_CLASS } from "../../constants/tiers";

const TIERS: Tier[] = ["green", "amber", "red"];

export function MapLegend() {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600">
      {TIERS.map((tier) => (
        <span key={tier} className="flex items-center gap-1.5">
          <span className={`h-2.5 w-2.5 rounded-full ${TIER_BG_CLASS[tier]}`} />
          {TIER_LABELS[tier]}
        </span>
      ))}
      <span className="flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-full border-2 border-dashed border-slate-500" />
        Estimated (far from a station)
      </span>
    </div>
  );
}
