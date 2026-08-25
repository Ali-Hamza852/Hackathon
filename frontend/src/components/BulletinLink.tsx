import { bulletinUrl } from "../api/client";
import { useBulletinAvailability } from "../hooks/useBulletinAvailability";
import { lahoreTodayISODate } from "../utils/formatting";

export function BulletinLink() {
  const today = lahoreTodayISODate();
  const available = useBulletinAvailability(today);

  if (available === null) {
    return <p className="text-xs text-slate-400">Checking today's bulletin...</p>;
  }

  if (!available) {
    return (
      <p className="text-xs text-slate-400">
        Today's PDF bulletin hasn't been generated yet - check back after the next scoring run.
      </p>
    );
  }

  return (
    <a
      href={bulletinUrl(today)}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 underline-offset-2 hover:underline"
    >
      📄 Download today's bulletin (PDF)
    </a>
  );
}
