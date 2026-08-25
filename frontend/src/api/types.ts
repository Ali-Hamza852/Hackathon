export type Tier = "green" | "amber" | "red";

export type Confidence = "high" | "medium" | "low";

export type SchoolSource = "overpass" | "manual";

export interface School {
  id: number;
  name: string;
  zone: string;
  lat: number;
  lon: number;
  source: SchoolSource;
}

export interface Score {
  id: number;
  school_id: number;
  school_name: string;
  zone: string;
  lat: number;
  lon: number;
  score_date: string;
  computed_at: string;
  raw_aqi: number;
  adjusted_aqi: number;
  tier: Tier;
  recommendation: string;
  confidence: Confidence;
  distance_to_station_km: number;
}
