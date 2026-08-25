# SAANS Backend API Contract

Base URL: `BACKEND_BASE_URL` (local dev: `http://localhost:8000`). Full interactive schema is always live at `/docs` (Swagger) and `/openapi.json`.

Every score object below carries `tier`, `recommendation`, `confidence`, and `distance_to_station_km` — never a partial object. Every tier's `recommendation` text and the disclaimer come straight from `app/scoring/tiers.py`, the single source of truth; the frontend, PDF, and WhatsApp bot must not re-type this copy.

## `GET /health`
Liveness check. `200 { "status": "ok" }`.

## `GET /schools`
Query params, both optional: `q` (substring match against **either** name or zone — the general free-text search box), `zone` (substring match against zone only — narrows further, ANDed with `q` if both are given).
Returns: `SchoolOut[]` — `{ id, name, zone, lat, lon, source }`, `source` is `"overpass" | "manual"`.

## `GET /schools/{id}`
Returns one `SchoolOut`. `404` if the id doesn't exist.

## `GET /scores/today`
Returns `ScoreOut[]` for every school with a score computed for the current Lahore-local date. Empty array is valid (no crash) when no provider has usable data yet — the frontend must render an empty/loading state, not assume this is always populated.

`ScoreOut`:
```json
{
  "id": 1,
  "school_id": 11,
  "school_name": "Aitchison College",
  "zone": "Gulberg",
  "lat": 31.5395,
  "lon": 74.332,
  "score_date": "2026-08-25",
  "computed_at": "2026-08-25T06:00:03.221000",
  "raw_aqi": 168.0,
  "adjusted_aqi": 176.4,
  "tier": "amber",
  "recommendation": "Move recess and sports indoors; sensitive students should avoid outdoor exposure.",
  "confidence": "medium",
  "distance_to_station_km": 2.31
}
```
`tier` is `"green" | "amber" | "red"`. `confidence` is `"high" | "medium" | "low"` (`<=1km` / `<=5km` / `>5km` from the nearest usable station).

## `GET /schools/{id}/scores?days=7`
Trailing score history for one school, `ScoreOut[]` ordered oldest to newest. `days` defaults to 7. `404` if the school doesn't exist.

## `POST /subscribers`
Body:
```json
{ "school_id": 11, "channel": "whatsapp", "contact": "+923001234567" }
```
`school_id` is nullable (null = neighbourhood-level, not tied to one school). `channel` is `"whatsapp" | "sms"`. Returns `201` + `SubscriberOut`, or `404` if `school_id` doesn't exist, or `422` if `contact` doesn't look like a phone number.

## `POST /admin/recompute`
Header required: `X-Admin-Secret: <ADMIN_RECOMPUTE_SECRET>`. Runs the full scoring cycle immediately (same job the 6 AM / midday scheduler runs), including the PDF and WhatsApp post-scoring hooks once those are wired in. Returns the freshly computed `ScoreOut[]`. `403` on a wrong/missing secret.

## Disclaimer text (verbatim, use everywhere)
> Decision-support estimate - not a replacement for official Punjab EPA/health authority guidance.

## Not-configured behavior
If `WAQI_API_TOKEN` / `OPENAQ_API_KEY` aren't set, ingestion clients skip cleanly instead of throwing — `/scores/today` will legitimately return `[]` until at least one is configured. This is expected, not a bug.
