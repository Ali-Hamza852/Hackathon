# SAANS — Smog Advisory & School Closure Decision System

## Project Identity

- **Name:** SAANS ("breath" in Urdu)
- **Goal:** Give individual Lahore schools a daily, location-specific smog risk score (Green/Amber/Red) and a concrete recommended action, distributed via web, WhatsApp, and printable PDF — replacing blanket province-wide closure orders with targeted, timely, explainable guidance.

## System Architecture

```
External data sources (WAQI, OpenAQ, Open-Meteo, OSM Overpass)
                    |
              Scoring engine (in-process cron: 6 AM + midday)
        nearest-station lookup -> interpolation fallback ->
        wind/time-of-day adjustment -> tier + confidence
                    |
              Database (SQLite, Postgres-compatible schema)
        schools | aqi_readings | scores | subscribers | broadcast_log
                    |
        -----------------------------------------------
        |                    |                        |
   Backend API          PDF bulletin job          WhatsApp bot
   (FastAPI)            (Jinja2 + Playwright)      (Cloud API)
        |                    |                        |
   Web dashboard        Printable PDF            Parent/school
   (React + Leaflet)    at the school gate        WhatsApp groups
```

Every distribution channel reads from the backend's already-computed `scores` table through the same REST API/DB session — none of them call an AQI provider directly. This keeps a single source of truth for tier, recommendation, and confidence.

## Components

| # | Component | Location | Owner role |
|---|---|---|---|
| 1 | Data ingestion, scoring engine, DB schema | `backend/app/{ingestion,scoring,db,schools}` | Backend |
| 2 | Web dashboard | `frontend/` | Frontend |
| 3 | WhatsApp bot, PDF bulletin generator, SMS (roadmap) | `distribution/` | Integrations |
| 4 | Docs, demo script | `docs/` | Product |

## Technology Stack

| Layer | Choice |
|---|---|
| Backend API | Python + FastAPI |
| Database | SQLite (file, Postgres-compatible schema) |
| ORM | SQLAlchemy 2.0 |
| Scheduler | APScheduler (in-process cron) |
| Frontend | React + Vite + TypeScript, Leaflet, TailwindCSS, Recharts |
| PDF generation | Jinja2 template rendered to PDF via Playwright (headless Chromium) |
| WhatsApp | WhatsApp Business Platform Cloud API |
| SMS | Twilio (roadmap, not built — see `distribution/sms/README.md`) |
| Hosting | Fly.io (backend, persistent volume for SQLite), Vercel (frontend) |

## Data Model

See `backend/app/db/models.py` for the authoritative SQLAlchemy definitions — `School`, `AQIReading`, `Score`, `Subscriber`, `BroadcastLog`, matching this schema exactly.

## Tier Logic

| Tier | AQI Range | Action |
|---|---|---|
| Green — Normal | 0–100 | Outdoor activity, sports, recess proceed as normal |
| Amber — Caution | 101–200 | Move recess/sports indoors; sensitive students avoid outdoor exposure |
| Red — High Risk | 201+ | Recommend remote learning or indoor-only day; flag to admin for closure decision |

Thresholds live as named constants in `backend/app/scoring/tiers.py` — never hardcoded elsewhere.

## Non-Negotiable Constraints

1. Every AQI/weather/distribution API call has a timeout, retry-once, and graceful fallback — never crashes the job.
2. The system never presents an interpolated score as a direct sensor reading — `confidence` is mandatory on every score object.
3. No distribution channel blocks the core deliverable (the dashboard with real scores).
4. All official/health-authority language stays hedged: SAANS is a **decision-support aid**, not a replacement for Punjab EPA/health authority guidance — in UI copy, WhatsApp templates, and the PDF footer alike.

## Environment Variables

See `.env.example` at the repo root and per-service (`backend/.env.example`, `frontend/.env.example`).
