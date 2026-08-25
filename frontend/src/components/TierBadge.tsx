import { TIER_BG_CLASS, TIER_LABELS } from "../constants/tiers";
import type { Tier } from "../api/types";

interface TierBadgeProps {
  tier: Tier;
  size?: "sm" | "md";
}

export function TierBadge({ tier, size = "md" }: TierBadgeProps) {
  const sizeClass = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  return (
    <span
      className={`inline-flex items-center rounded-full font-semibold text-white ${TIER_BG_CLASS[tier]} ${sizeClass}`}
    >
      {TIER_LABELS[tier]}
    </span>
  );
}
