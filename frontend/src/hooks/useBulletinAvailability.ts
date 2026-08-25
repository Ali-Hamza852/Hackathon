import { useEffect, useState } from "react";
import { bulletinExists } from "../api/client";

export function useBulletinAvailability(dateStr: string): boolean | null {
  const [available, setAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    setAvailable(null);

    bulletinExists(dateStr).then((exists) => {
      if (!cancelled) setAvailable(exists);
    });

    return () => {
      cancelled = true;
    };
  }, [dateStr]);

  return available;
}
