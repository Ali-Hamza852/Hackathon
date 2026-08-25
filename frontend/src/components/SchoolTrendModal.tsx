import { TrendChart } from "./TrendChart";
import type { Score } from "../api/types";

interface SchoolTrendModalProps {
  score: Score;
  onClose: () => void;
}

export function SchoolTrendModal({ score, onClose }: SchoolTrendModalProps) {
  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/50 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-2xl bg-white p-5 shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 className="font-heading text-lg font-bold text-slate-900">{score.school_name}</h2>
            <p className="text-xs text-slate-500">7-day AQI trend</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close trend panel"
            className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            ✕
          </button>
        </div>
        <TrendChart schoolId={score.school_id} />
      </div>
    </div>
  );
}
