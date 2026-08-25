import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useSchoolTrend } from "../hooks/useSchoolTrend";
import { TIER_COLORS } from "../constants/tiers";
import { formatScoreDate } from "../utils/formatting";
import type { Score } from "../api/types";
import { LoadingState, ErrorState, EmptyState } from "./StatusMessage";

interface TrendChartProps {
  schoolId: number;
}

interface ChartRow {
  date: string;
  [segmentKey: string]: number | string | null;
}

function buildSegments(scores: Score[]) {
  const segmentCount = Math.max(scores.length - 1, 0);
  const rows: ChartRow[] = scores.map((score) => ({
    date: formatScoreDate(score.score_date),
  }));

  const colors: string[] = [];
  for (let segmentIndex = 0; segmentIndex < segmentCount; segmentIndex++) {
    const key = `seg${segmentIndex}`;
    colors.push(TIER_COLORS[scores[segmentIndex].tier]);
    rows.forEach((row, rowIndex) => {
      row[key] = rowIndex === segmentIndex || rowIndex === segmentIndex + 1
        ? scores[rowIndex].adjusted_aqi
        : null;
    });
  }

  return { rows, colors };
}

export function TrendChart({ schoolId }: TrendChartProps) {
  const { trend, status } = useSchoolTrend(schoolId, 7);

  if (status === "loading") {
    return <LoadingState message="Loading trend..." />;
  }

  if (status === "error") {
    return <ErrorState message="Trend data temporarily unavailable." />;
  }

  if (!trend || trend.length === 0) {
    return <EmptyState message="No score history yet for this school." />;
  }

  if (trend.length === 1) {
    return (
      <EmptyState
        message={`Today's AQI is ${Math.round(trend[0].adjusted_aqi)}.`}
        subtext="Check back tomorrow to see a trend line build up."
      />
    );
  }

  const { rows, colors } = buildSegments(trend);

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#64748b" }} />
        <YAxis tick={{ fontSize: 12, fill: "#64748b" }} width={40} />
        <ReferenceLine y={100} stroke={TIER_COLORS.amber} strokeDasharray="4 4" />
        <ReferenceLine y={200} stroke={TIER_COLORS.red} strokeDasharray="4 4" />
        <Tooltip
          formatter={(value) => [Math.round(Number(value)), "AQI"]}
          labelStyle={{ fontWeight: 600 }}
        />
        {colors.map((color, index) => (
          <Line
            key={index}
            type="monotone"
            dataKey={`seg${index}`}
            stroke={color}
            strokeWidth={3}
            dot={{ r: 4, fill: color, strokeWidth: 0 }}
            connectNulls={false}
            isAnimationActive={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
