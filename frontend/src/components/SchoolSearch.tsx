import { useEffect, useState } from "react";
import { searchSchools } from "../api/client";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type { School } from "../api/types";

interface SchoolSearchProps {
  onResults: (schools: School[] | null) => void;
}

export function SchoolSearch({ onResults }: SchoolSearchProps) {
  const [inputValue, setInputValue] = useState("");
  const debouncedValue = useDebouncedValue(inputValue, 300);

  useEffect(() => {
    const term = debouncedValue.trim();
    if (term === "") {
      onResults(null);
      return;
    }

    let cancelled = false;
    searchSchools(term)
      .then((schools) => {
        if (!cancelled) onResults(schools);
      })
      .catch(() => {
        if (!cancelled) onResults([]);
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedValue, onResults]);

  return (
    <input
      type="search"
      value={inputValue}
      onChange={(event) => setInputValue(event.target.value)}
      placeholder="Search by school name or zone..."
      aria-label="Search schools by name or zone"
      className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-100"
    />
  );
}
