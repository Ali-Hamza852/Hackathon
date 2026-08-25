export function formatComputedAt(isoLike: string): string {
  const [datePart, timePart] = isoLike.split("T");
  if (!datePart || !timePart) return isoLike;

  const [year, month, day] = datePart.split("-").map(Number);
  const [hourStr, minuteStr] = timePart.split(":");
  const localMoment = new Date(year, month - 1, day, Number(hourStr), Number(minuteStr));

  const formatted = localMoment.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
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
