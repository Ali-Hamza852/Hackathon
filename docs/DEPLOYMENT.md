# Deploying SAANS

Backend: **Vercel** (Python serverless function). Frontend: **Vercel** (static Vite build). Database: **Neon** (free Postgres, no credit card, scales to zero when idle). Scheduled runs: a **GitHub Actions cron** hitting `/admin/recompute`, because a serverless function has no long-lived process for an in-process APScheduler to run in.

Render, Fly.io, and Railway were all tried first and ruled out — every one of them now requires a card on file even for its free/trial tier, as of August 2026. WeasyPrint was tried for PDF generation and ruled out too — its native C dependencies (Pango/Cairo/GDK-Pixbuf) aren't present in Vercel's Python runtime, so bulletin generation uses `fpdf2` instead, which is pure-Python-wheel and works there.

Backend and frontend are **two separate Vercel projects** (`saans-backend`, `saans-frontend`) sharing one git repo. That split, and how each project's Root Directory is configured, is the single most important thing to get right — see the pitfalls section below before touching project settings.

## 1. Database — Neon

1. Sign up at neon.com (no card).
2. Create a project. Copy the connection string — `postgresql://user:pass@ep-something.neon.tech/dbname?sslmode=require`. The backend normalizes `postgresql://`/`postgres://` to the driver it actually needs (`postgresql+psycopg://`) automatically in [session.py](../backend/app/db/session.py), no edits needed.

## 2. Backend — Vercel (`saans-backend` project)

The entrypoint is [api/index.py](../api/index.py) at the repo root: it puts `backend/` and the repo root on `sys.path`, then imports the real FastAPI `app` from `backend/app/main.py`. Root-level [vercel.json](../vercel.json) is what wires that entrypoint up:

```json
{
  "functions": { "api/index.py": { "maxDuration": 60 } },
  "rewrites": [{ "source": "/(.*)", "destination": "/api/index.py" }]
}
```

Steps:
1. `vercel project add saans-backend` (or create it from the dashboard, connected to `Ali-Hamza852/Hackathon`).
2. This project's **Root Directory must be the repo root** (`.` / unset) — it needs `api/index.py`, `backend/`, and the root `vercel.json` all visible in the same build.
3. Set project env vars (`vercel env add --project saans-backend <NAME> production`, or the dashboard):
   - `DATABASE_URL` — the Neon connection string.
   - `ADMIN_RECOMPUTE_SECRET` — any random string you choose; the GitHub Actions cron needs the same value.
   - `WAQI_API_TOKEN` / `OPENAQ_API_KEY` — free, instant signup (aqicn.org/data-platform/token/, explore.openaq.org). At least one is needed for `/scores/today` to return real data instead of an empty array.
   - `WHATSAPP_CLOUD_API_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` / `WHATSAPP_VERIFY_TOKEN` / `WHATSAPP_APP_SECRET` — from the Meta developer app (step 5 below); leave unset for now, broadcasts just log as `skipped` until they're added, no code change needed later.
   - `FRONTEND_BASE_URL` — the real `saans-frontend` production URL (step 3), so backend CORS accepts requests from it.
4. Deploy: `vercel --prod --project saans-backend --yes` from the repo root.
5. Seed the schools once — either run `PYTHONPATH=backend python -c "from app.seed import seed_schools; print(seed_schools())"` against the Neon `DATABASE_URL` locally, or add a temporary one-off admin route; there's no shell access on a serverless deploy.
6. Verify: `curl https://saans-backend.vercel.app/health` and `/scores/today`.

## 3. Frontend — Vercel (`saans-frontend` project)

The frontend is a plain Vite/React static build living in `frontend/`. It does **not** use the root `vercel.json` at all — it needs its own Root Directory setting.

Steps:
1. `vercel project add saans-frontend` (or create it from the dashboard, same repo).
2. This project's **Root Directory must be `frontend`** — set via the dashboard (Settings → General → Root Directory), or by deploying from inside the `frontend/` folder directly (`cd frontend && vercel --prod --project saans-frontend --yes`), which is the more reliable option — see pitfall below.
3. Set `VITE_BACKEND_BASE_URL=https://saans-backend.vercel.app` as a project env var (`vercel env add --project saans-frontend VITE_BACKEND_BASE_URL production --value "https://saans-backend.vercel.app"`). It's a Vite build-time var with no fallback in [client.ts](../frontend/src/api/client.ts), so a rebuild is required any time it changes.
4. Deploy: `cd frontend && vercel --prod --project saans-frontend --yes`.
5. Update `FRONTEND_BASE_URL` on the backend project (step 2.3 above) to this real URL and redeploy the backend, so CORS allows it.
6. Load the Vercel URL from a phone on mobile data, not just the deploy machine's network.

## Deployment pitfalls actually hit in production (read this before touching `vercel.json` or project settings)

These caused a real outage once and are easy to reintroduce silently, since nothing in CI catches them:

- **Never add a `services` key (or an object-shaped `rewrites[].destination`) to `vercel.json`.** It isn't a documented Vercel schema for defining functions. Worse, if it's ever deployed even once, Vercel **persists `"services"` as the project's Framework Preset** in that project's settings — so even reverting `vercel.json` back to the correct `functions`/rewrites shape isn't enough; the deploy will still fail with `Project framework is set to "services", but no services are declared` until the Framework Preset is explicitly reset (`PATCH /v9/projects/<id>` with `{"framework": null}` via the Vercel API, or the dashboard's Framework Preset dropdown).
- **`saans-frontend`'s Root Directory must point at `frontend/`, not the repo root.** If it's ever unset/root, the project builds and serves the *backend's* `vercel.json`/`api/index.py` instead of the Vite app — the live symptom is the frontend URL returning FastAPI's own `{"detail":"Not Found"}` JSON instead of the dashboard. The most reliable fix is deploying from inside `frontend/` (`cd frontend && vercel --prod --project saans-frontend`) rather than trusting a dashboard Root Directory setting to stick.
- **Always pass `--project <name>` explicitly on every `vercel` CLI command.** The ambient `.vercel/project.json` link file at the repo root can silently point at the wrong project (it's tracked which project you last ran `vercel link` against, not which one you mean right now), and running a bare `vercel` command from the wrong directory can clobber it or deploy to the wrong target.
- **`.vercelignore` at the repo root excludes `frontend/`** (it's written for the backend project's upload). That means you cannot deploy `saans-frontend` with Root Directory set to a `frontend` subdirectory while running the CLI from the repo root — the upload never contains that folder. Deploying from inside `frontend/` sidesteps this entirely.

## 4. Scheduled scoring runs — GitHub Actions

A serverless function has no persistent process, so the backend's in-process `APScheduler` never fires on its own in production — [main.py](../backend/app/main.py) gates it behind `RUNNING_ON_VERCEL` and skips starting it there. `.github/workflows/scheduled-recompute.yml` covers this instead: it hits `POST /admin/recompute` at 6:00 and 12:00 Asia/Karachi time (01:00 and 07:00 UTC), running the real scoring cycle end-to-end (including the PDF and WhatsApp hooks).

Repository secrets (Settings → Secrets and variables → Actions):
- `SAANS_BACKEND_URL` — `https://saans-backend.vercel.app`
- `SAANS_ADMIN_SECRET` — the same value as `ADMIN_RECOMPUTE_SECRET` on the backend

You can also trigger it manually anytime from the Actions tab (`workflow_dispatch`) instead of waiting for the schedule.

## 5. WhatsApp Cloud API sandbox (manual, Meta account required)

1. Create a Meta developer app at developers.facebook.com, add the WhatsApp product, and grab the temporary access token + test phone number ID from the app dashboard, plus the app's secret (Settings → Basic → App Secret) for `WHATSAPP_APP_SECRET`.
2. Set the webhook callback URL to `https://saans-backend.vercel.app/whatsapp/webhook` and the verify token to whatever you set as `WHATSAPP_VERIFY_TOKEN` — Meta hits the `GET` handshake on save.
3. Subscribe the webhook to the `messages` field.
4. Send `SUBSCRIBE <school name>` from a test number to the sandbox number to confirm the subscribe flow works.

## What "not configured" looks like

Every external integration degrades gracefully rather than crashing when its credentials are missing:
- No WAQI/OpenAQ key → `/scores/today` returns `[]` (empty, not fake data) until at least one is set.
- No WhatsApp credentials → broadcasts write `BroadcastLog(status=skipped)` instead of attempting a send, and it re-sends for real (not stuck) the moment credentials are added.

This is expected mid-build behavior, not a bug — dropping in a real key later requires no code change.

## Known limitations of the free-tier stack (worth knowing, not blockers)

- **Cold starts**: Neon's compute scales to zero after 5 minutes idle, so the first query after a quiet period adds roughly a second while it wakes. Vercel functions themselves cold-start in well under that.
- **Bulletin PDFs are rendered on demand, not stored**: [routes_bulletins.py](../backend/app/api/routes_bulletins.py) builds the PDF from the DB on every request rather than writing to disk, since a serverless function has no persistent disk between invocations. This means every `/bulletins/{date}.pdf` request re-renders — cheap (a few KB, sub-second), so this is a non-issue in practice, not a workaround to revisit.
