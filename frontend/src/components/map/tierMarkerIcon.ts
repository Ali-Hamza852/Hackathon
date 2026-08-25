import L from "leaflet";
import { TIER_COLORS, isEstimatedConfidence } from "../../constants/tiers";
import type { Confidence, Tier } from "../../api/types";

const iconCache = new Map<string, L.DivIcon>();

function createIcon(tier: Tier, estimated: boolean): L.DivIcon {
  const borderStyle = estimated ? "dashed" : "solid";
  const borderColor = estimated ? "#334155" : "#ffffff";

  const html = `<div style="
    width: 22px;
    height: 22px;
    border-radius: 9999px;
    background: ${TIER_COLORS[tier]};
    border: 3px ${borderStyle} ${borderColor};
    box-shadow: 0 1px 4px rgba(0,0,0,0.45);
  "></div>`;

  return L.divIcon({
    html,
    className: "",
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -14],
  });
}

export function buildTierMarkerIcon(tier: Tier, confidence: Confidence): L.DivIcon {
  const estimated = isEstimatedConfidence(confidence);
  const key = `${tier}_${estimated}`;

  let icon = iconCache.get(key);
  if (!icon) {
    icon = createIcon(tier, estimated);
    iconCache.set(key, icon);
  }
  return icon;
}
