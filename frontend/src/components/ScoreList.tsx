import type { Score } from "../api/types";
import { ScoreCard } from "./ScoreCard";

interface ScoreListProps {
  scores: Score[];
  onViewTrend: (score: Score) => void;
}

export function ScoreList({ scores, onViewTrend }: ScoreListProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {scores.map((score) => (
        <ScoreCard key={score.id} score={score} onViewTrend={onViewTrend} />
      ))}
    </div>
  );
}
