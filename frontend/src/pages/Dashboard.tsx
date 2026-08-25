import { useCallback, useMemo, useState } from "react";
import { useTodayScores } from "../hooks/useTodayScores";
import { Header } from "../components/Header";
import { SchoolSearch } from "../components/SchoolSearch";
import { ViewToggle, type DashboardView } from "../components/ViewToggle";
import { MapView } from "../components/MapView";
import { ScoreList } from "../components/ScoreList";
import { BulletinLink } from "../components/BulletinLink";
import { SchoolTrendModal } from "../components/SchoolTrendModal";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusMessage";
import type { School, Score } from "../api/types";

export default function Dashboard() {
  const { scores, status } = useTodayScores();
  const [view, setView] = useState<DashboardView>("map");
  const [matchingSchoolIds, setMatchingSchoolIds] = useState<Set<number> | null>(null);
  const [trendScore, setTrendScore] = useState<Score | null>(null);

  const handleSearchResults = useCallback((schools: School[] | null) => {
    setMatchingSchoolIds(schools === null ? null : new Set(schools.map((school) => school.id)));
  }, []);

  const visibleScores = useMemo(() => {
    if (!scores) return [];
    if (matchingSchoolIds === null) return scores;
    return scores.filter((score) => matchingSchoolIds.has(score.school_id));
  }, [scores, matchingSchoolIds]);

  const isFiltering = matchingSchoolIds !== null;

  return (
    <div className="min-h-screen bg-slate-50 font-body text-slate-900">
      <Header />
      <main className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="sm:max-w-md sm:flex-1">
            <SchoolSearch onResults={handleSearchResults} />
          </div>
          <ViewToggle view={view} onChange={setView} />
        </div>

        {status === "loading" && <LoadingState message="Loading today's smog scores..." />}

        {status === "error" && (
          <ErrorState
            message="Data temporarily unavailable."
            subtext="We couldn't reach the SAANS server. Please try again in a moment."
          />
        )}

        {status === "success" && scores && scores.length === 0 && (
          <EmptyState
            message="No smog scores are available yet for today."
            subtext="Scores are computed on a schedule - check back after the next run."
          />
        )}

        {status === "success" && scores && scores.length > 0 && isFiltering && visibleScores.length === 0 && (
          <EmptyState message="No schools match your search." />
        )}

        {status === "success" && visibleScores.length > 0 && (
          view === "map" ? (
            <MapView scores={visibleScores} />
          ) : (
            <ScoreList scores={visibleScores} onViewTrend={setTrendScore} />
          )
        )}

        <div className="border-t border-slate-200 pt-4">
          <BulletinLink />
        </div>
      </main>

      {trendScore && <SchoolTrendModal score={trendScore} onClose={() => setTrendScore(null)} />}
    </div>
  );
}
