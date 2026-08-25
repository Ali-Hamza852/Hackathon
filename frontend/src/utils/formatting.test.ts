import { describe, expect, it } from "vitest";
import { formatComputedAt, formatScoreDate, lahoreTodayISODate } from "./formatting";

describe("formatComputedAt", () => {
  it("converts a naive-UTC backend timestamp to Lahore local time, not the raw wall-clock digits", () => {
    const result = formatComputedAt("2026-08-25T17:17:25.159698");
    expect(result).toBe("Aug 25, 10:17 PM PKT");
  });

  it("handles an already-Z-suffixed timestamp the same way", () => {
    const result = formatComputedAt("2026-08-25T17:17:25Z");
    expect(result).toBe("Aug 25, 10:17 PM PKT");
  });

  it("falls back to the raw string instead of throwing on unparseable input", () => {
    expect(formatComputedAt("not-a-date")).toBe("not-a-date");
  });
});

describe("formatScoreDate", () => {
  it("renders the same calendar date regardless of call, since it has no time component to shift", () => {
    expect(formatScoreDate("2026-08-25")).toBe("Aug 25");
    expect(formatScoreDate("2026-01-01")).toBe("Jan 1");
  });
});

describe("lahoreTodayISODate", () => {
  it("returns a YYYY-MM-DD string", () => {
    expect(lahoreTodayISODate()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
