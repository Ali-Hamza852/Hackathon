# Deploying SAANS

Backend: **Render** (free web service, no credit card). Database: **Neon** (free Postgres, no credit card, permanent free tier — this is what makes Render's lack of a persistent disk a non-issue). Frontend: **Vercel** (free). Scheduled runs: a **GitHub Actions cron** hitting `/admin/recompute`, because Render's free web service sleeps after 15 minutes of inactivity and the in-process APScheduler can't fire while asleep.

Fly.io and Railway were considered and ruled out — both now require a card on file even for their free/trial tiers, as of August 2026.

## 1. Database — Neon

1. Sign up at neon.com (no card).
2. Create a project. Copy the connection string it gives you — it looks like `postgresql://user:pass@ep-something.neon.tech/dbname?sslmode=require`. Hand it to me as-is; the backend normalizes the `postgresql://`/`postgres://` scheme to the driver it needs (`postgresql+psycopg://`) automatically, no edits needed.

## 2. Backend — Render

1. Sign up at render.com (no card), connect your GitHub account, grant it access to `Ali-Hamza852/Hackathon`.
2. New → Web Service → pick this repo. Render will detect `render.yaml` at the repo root and offer to use it as a Blueprint — accept that; it's already configured for the Docker build (`Dockerfile` builds `backend/` + `distribution/` together) and the free plan.
3. When prompted for the env vars marked `sync: false` in `render.yaml`, fill in:
   - `DATABASE_URL` — the Neon connection string from step 1.
   - `ADMIN_RECOMPUTE_SECRET` — any random string you choose.
   - `WAQI_API_TOKEN` / `OPENAQ_API_KEY` — free, instant signup (aqicn.org/data-platform/token/, explore.openaq.org). Grab at least one so `/scores/today` shows real data instead of an empty array.
   - `WHATSAPP_CLOUD_API_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` / `WHATSAPP_VERIFY_TOKEN` / `WHATSAPP_APP_SECRET` — from the Meta developer app (step 4 below); leave blank for now if not ready, the app runs fine without them (broadcasts just log as `skipped`).
   - `FRONTEND_BASE_URL` — the Vercel URL from step 3, once you have it (comes after the frontend deploy — update and redeploy this var once you know it, otherwise the browser's CORS requests from the deployed frontend will be rejected).
4. Deploy. Once live, seed the schools once — Render's dashboard has a Shell tab for the running service:
   ```
   PYTHONPATH=/app/backend python -c "from app.seed import seed_schools; print(seed_schools())"
   ```
5. Verify: `curl https://<your-service>.onrender.com/health`.

## 3. Frontend — Vercel

1. `vercel link` (or use a Vercel token non-interactively).
2. Set `VITE_BACKEND_BASE_URL=https://<your-service>.onrender.com` as a Vercel project env var.
3. `vercel --prod`.
4. Go back to Render and set `FRONTEND_BASE_URL` to the real Vercel URL, then redeploy the backend so CORS allows it.
5. Load the Vercel URL from a phone on mobile data, not just the deploy machine's network.

## 4. Scheduled scoring runs — GitHub Actions

Render's free web service sleeps after 15 minutes idle, so the backend's own 6am/midday `APScheduler` cron can't be relied on to fire — it only runs while the process happens to be awake. `.github/workflows/scheduled-recompute.yml` covers this: it hits `POST /admin/recompute` at 6:00 and 12:00 Asia/Karachi time (01:00 and 07:00 UTC), which both wakes the sleeping service and runs the real scoring cycle end-to-end (including the PDF and WhatsApp hooks).

Add two repository secrets (Settings → Secrets and variables → Actions):
- `SAANS_BACKEND_URL` — `https://<your-service>.onrender.com`
- `SAANS_ADMIN_SECRET` — the same value as `ADMIN_RECOMPUTE_SECRET` on Render

You can also trigger it manually anytime from the Actions tab (`workflow_dispatch`) instead of waiting for the schedule — useful for a live demo.

## 5. WhatsApp Cloud API sandbox (manual, Meta account required)

1. Create a Meta developer app at developers.facebook.com, add the WhatsApp product, and grab the temporary access token + test phone number ID from the app dashboard, plus the app's secret (Settings → Basic → App Secret) for `WHATSAPP_APP_SECRET`.
2. Set the webhook callback URL to `https://<your-service>.onrender.com/whatsapp/webhook` and the verify token to whatever you set as `WHATSAPP_VERIFY_TOKEN` — Meta hits the `GET` handshake on save.
3. Subscribe the webhook to the `messages` field.
4. Send `SUBSCRIBE <school name>` from a test number to the sandbox number to confirm the subscribe flow works.

## What "not configured" looks like

Every external integration degrades gracefully rather than crashing when its credentials are missing:
- No WAQI/OpenAQ key → `/scores/today` returns `[]` (empty, not fake data) until at least one is set.
- No WhatsApp credentials → broadcasts write `BroadcastLog(status=skipped)` instead of attempting a send, and it re-sends for real (not stuck) the moment credentials are added.

This is expected mid-build behavior, not a bug — dropping in a real key later requires no code change.

## Known limitations of the free-tier stack (worth knowing, not blockers)

- **Cold starts**: the first request after 15 minutes idle takes roughly a minute while Render wakes the service. The scheduled workflow above absorbs this with a 90s timeout and retries; a live demo click on `/admin/recompute` right after a quiet period will feel slow once, then be fast.
- **Bulletin PDFs don't persist across restarts**: Render's free tier has no persistent disk, so generated PDFs live only until the next sleep/restart cycle (the DB is unaffected — that's on Neon). A fresh PDF regenerates on the next scoring cycle regardless, so this only matters if someone expects yesterday's PDF to still be downloadable.
