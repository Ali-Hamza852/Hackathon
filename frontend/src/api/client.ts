import axios from "axios";
import type { School, Score } from "./types";

export const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

const httpClient = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 10000,
});

export async function fetchTodayScores(): Promise<Score[]> {
  const response = await httpClient.get<Score[]>("/scores/today");
  return response.data;
}

export async function fetchSchoolTrend(schoolId: number, days = 7): Promise<Score[]> {
  const response = await httpClient.get<Score[]>(`/schools/${schoolId}/scores`, {
    params: { days },
  });
  return response.data;
}

export async function searchSchools(term: string): Promise<School[]> {
  const [byName, byZone] = await Promise.all([
    httpClient.get<School[]>("/schools", { params: { q: term } }),
    httpClient.get<School[]>("/schools", { params: { zone: term } }),
  ]);

  const merged = new Map<number, School>();
  for (const school of [...byName.data, ...byZone.data]) {
    merged.set(school.id, school);
  }
  return Array.from(merged.values());
}

export function bulletinUrl(dateStr: string): string {
  return `${BACKEND_BASE_URL}/bulletins/${dateStr}.pdf`;
}

export async function bulletinExists(dateStr: string): Promise<boolean> {
  try {
    await httpClient.head(`/bulletins/${dateStr}.pdf`);
    return true;
  } catch {
    return false;
  }
}
