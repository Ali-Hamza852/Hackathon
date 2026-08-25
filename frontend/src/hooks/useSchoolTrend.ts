import { useEffect, useState } from "react";
import { fetchSchoolTrend } from "../api/client";
import type { Score } from "../api/types";
import type { FetchStatus } from "./useTodayScores";

export function useSchoolTrend(schoolId: number, days = 7) {
  const [trend, setTrend] = useState<Score[] | null>(null);
  const [status, setStatus] = useState<FetchStatus>("loading");

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setTrend(null);

    fetchSchoolTrend(schoolId, days)
      .then((data) => {
        if (cancelled) return;
        setTrend(data);
        setStatus("success");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, [schoolId, days]);

  return { trend, status };
}
