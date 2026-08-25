export function formatComputedAt(isoLike: string): string {
  const utcMoment = new Date(isoLike.endsWith("Z") ? isoLike : `${isoLike}Z`);
  if (Number.isNaN(utcMoment.getTime())) return isoLike;

  const formatted = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Karachi",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(utcMoment);
  return `${formatted} PKT`;
}

export function formatScoreDate(dateStr: string): string {
  const [year, month, day] = dateStr.split("-").map(Number);
  const localMoment = new Date(year, month - 1, day);
  return localMoment.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function lahoreTodayISODate(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Karachi" }).format(new Date());
}
