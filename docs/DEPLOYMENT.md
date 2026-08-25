# Deploying SAANS

## Backend — Fly.io

Fly is chosen over Render/Railway because its free allowance includes a small persistent volume, which SQLite needs to survive restarts.

1. `fly auth login` (or export `FLY_API_TOKEN`).
2. From the repo root: `fly launch --no-deploy --copy-config --name <your-app-name>` if you want a different app name than the one already committed in `fly.toml`, otherwise skip straight to step 3 — `fly.toml` already exists.
3. `fly volumes create saans_data --region sin --size 1` (matches the `[mounts]` block in `fly.toml`; only needed once).
4. Set secrets — never put these in `fly.toml`, which is committed to git:
   ```
   fly secrets set \
     ADMIN_RECOMPUTE_SECRET=<random string> \
     WAQI_API_TOKEN=<your WAQI token> \
     OPENAQ_API_KEY=<your OpenAQ key> \
     WHATSAPP_CLOUD_API_TOKEN=<if ready> \
     WHATSAPP_PHONE_NUMBER_ID=<if ready> \
     WHATSAPP_VERIFY_TOKEN=<random string>
   ```
   WAQI and OpenAQ keys are both free and issued instantly by email/signup — grab them even if WhatsApp isn't ready yet, since the dashboard needs at least one of them to show real (non-empty) scores.
5. `fly deploy`.
6. Seed the schools once, against the deployed instance: `fly ssh console -C "python -c 'from app.seed import seed_schools; print(seed_schools())'"`.
7. Verify: `curl https://<your-app-name>.fly.dev/health` and `curl https://<your-app-name>.fly.dev/scores/today`.

## Frontend — Vercel

1. `vercel login` (or a Vercel token via `vercel --token`).
2. From `frontend/`: `vercel link`, then set the env var `VITE_BACKEND_BASE_URL=https://<your-app-name>.fly.dev` in the Vercel project settings (or `vercel env add`).
3. `vercel --prod`.
4. Update `fly.toml`'s `FRONTEND_BASE_URL` to the real Vercel URL and `fly deploy` again so the backend's CORS allowlist matches (the API otherwise rejects browser requests from the deployed frontend's origin).
5. Load the Vercel URL from a phone on mobile data — not just the venue Wi-Fi — to confirm it actually works off-network.

## WhatsApp Cloud API sandbox (manual, Meta account required)

1. Create a Meta developer app at developers.facebook.com, add the WhatsApp product, and grab the temporary access token + test phone number ID from the app dashboard.
2. Set the webhook callback URL to `https://<your-app-name>.fly.dev/whatsapp/webhook` and the verify token to whatever you set as `WHATSAPP_VERIFY_TOKEN` above — Meta will hit the `GET` handshake on save.
3. Subscribe the webhook to the `messages` field.
4. Send `SUBSCRIBE <school name>` from a test number to the sandbox number, confirm it shows up in `subscribers` (`GET /schools/{id}/scores` isn't the right check here — query the DB or add a temporary admin endpoint if you want to inspect it without SSH).

## What "not configured" looks like

Every external integration degrades gracefully rather than crashing when its credentials are missing:
- No WAQI/OpenAQ key → `/scores/today` returns `[]` (empty, not fake data) until at least one is set.
- No WhatsApp credentials → broadcasts write `BroadcastLog(status=skipped)` instead of attempting a send.

This is expected mid-build behavior, not a bug — the system is designed so dropping in a real key later requires no code change.
