import { CONFIDENCE_LABELS, isEstimatedConfidence } from "../constants/tiers";
import type { Confidence } from "../api/types";

interface ConfidenceBadgeProps {
  confidence: Confidence;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const estimated = isEstimatedConfidence(confidence);
  const styling = estimated
    ? "border-dashed border-slate-400 text-slate-600 bg-slate-50"
    : "border-solid border-emerald-600 text-emerald-700 bg-emerald-50";

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${styling}`}
      title={estimated ? "Based on a distant monitoring station - treat as an estimate" : undefined}
    >
      {estimated && <span aria-hidden="true">~</span>}
      {CONFIDENCE_LABELS[confidence]}
    </span>
  );
}
