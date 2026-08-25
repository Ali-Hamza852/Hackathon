import type { Confidence, Tier } from "../api/types";

export const TIER_LABELS: Record<Tier, string> = {
  green: "Green - Normal",
  amber: "Amber - Caution",
  red: "Red - High Risk",
};

export const DECISION_SUPPORT_DISCLAIMER =
  "Decision-support estimate - not a replacement for official Punjab EPA/health authority guidance.";

export const TIER_COLORS: Record<Tier, string> = {
  green: "#2E7D32",
  amber: "#F9A825",
  red: "#C62828",
};

export const TIER_BG_CLASS: Record<Tier, string> = {
  green: "bg-tier-green",
  amber: "bg-tier-amber",
  red: "bg-tier-red",
};

export const TIER_TEXT_CLASS: Record<Tier, string> = {
  green: "text-tier-green",
  amber: "text-tier-amber",
  red: "text-tier-red",
};

export const CONFIDENCE_LABELS: Record<Confidence, string> = {
  high: "High confidence",
  medium: "Estimated - medium confidence",
  low: "Estimated - low confidence",
};

export const isEstimatedConfidence = (confidence: Confidence): boolean =>
  confidence !== "high";
