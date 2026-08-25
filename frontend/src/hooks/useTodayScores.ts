import { useEffect, useState } from "react";
import { fetchTodayScores } from "../api/client";
import type { Score } from "../api/types";

export type FetchStatus = "loading" | "success" | "error";

export function useTodayScores() {
  const [scores, setScores] = useState<Score[] | null>(null);
  const [status, setStatus] = useState<FetchStatus>("loading");

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");

    fetchTodayScores()
      .then((data) => {
        if (cancelled) return;
        setScores(data);
        setStatus("success");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { scores, status };
}
