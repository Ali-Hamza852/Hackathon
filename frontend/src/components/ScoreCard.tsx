import { DECISION_SUPPORT_DISCLAIMER, TIER_RECOMMENDATIONS } from "../constants/tiers";
import { formatComputedAt } from "../utils/formatting";
import type { Score } from "../api/types";
import { TierBadge } from "./TierBadge";
import { ConfidenceBadge } from "./ConfidenceBadge";

interface ScoreCardProps {
  score: Score;
  compact?: boolean;
  onViewTrend?: (score: Score) => void;
}

export function ScoreCard({ score, compact = false, onViewTrend }: ScoreCardProps) {
  const padding = compact ? "p-3" : "p-4";

  return (
    <article className={`flex flex-col gap-2.5 rounded-2xl border border-slate-200 bg-white ${padding} shadow-sm`}>
      <header className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-heading text-base font-bold leading-tight text-slate-900">
            {score.school_name}
          </h3>
          <p className="text-xs text-slate-500">{score.zone}</p>
        </div>
        <TierBadge tier={score.tier} size={compact ? "sm" : "md"} />
      </header>

      <p className="text-sm text-slate-700">{TIER_RECOMMENDATIONS[score.tier]}</p>

      <div className="flex flex-wrap items-center gap-2">
        <ConfidenceBadge confidence={score.confidence} />
        <span className="text-xs text-slate-400">AQI {Math.round(score.adjusted_aqi)}</span>
      </div>

      <p className="text-xs text-slate-400">{formatComputedAt(score.computed_at)}</p>

      {onViewTrend && (
        <button
          type="button"
          onClick={() => onViewTrend(score)}
          className="self-start text-xs font-semibold text-emerald-700 underline-offset-2 hover:underline"
        >
          View 7-day trend
        </button>
      )}

      <p className="border-t border-slate-100 pt-2 text-[11px] leading-snug text-slate-400">
        {DECISION_SUPPORT_DISCLAIMER}
      </p>
    </article>
  );
}
