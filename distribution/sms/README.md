# SMS Fallback — Roadmap, Not Implemented

SMS via Twilio is explicitly scoped as **roadmap** for this build, not shipped code. This matches
the original phase spec's own priority ordering (PDF first as highest-feasibility/lowest-risk,
WhatsApp second, SMS as a Low–medium feasibility stretch goal that should not block the demo) and
the project owner's explicit decision to ship "PDF + WhatsApp, full" and document SMS rather than
land a half-working channel that could fail live during a demo.

No `twilio_sender.py` exists in this repo. Nothing under `distribution/sms/` is wired into
`distribution_wiring.py` or the scoring cycle hooks.

## What it would take to add later

- **Subscriber source**: reuse the existing `subscribers` table, filtered to `channel = sms`
  (same `Subscriber` / `SubscriberChannel.sms` model already defined in `app/db/models.py` —
  no schema change needed).
- **Sender**: a `distribution/sms/twilio_sender.py` module using the Twilio REST client
  (`twilio_account_sid`, `twilio_auth_token`, `twilio_from_number` from `app.config.Settings`,
  already present as env vars but currently unused).
- **Message copy**: a short, plain-text version of the bulletin message — tier + one-line
  recommendation, kept under ~160 characters per school to fit a single SMS segment, sourced
  from the same `Score` row (never hand-typed) the same way `distribution/whatsapp/message_templates.py`
  does.
- **Reliability pattern**: identical shape to `distribution/whatsapp/bot.py`'s
  `send_whatsapp_message` — 5s timeout, retry-once, catch and log rather than raise, return a
  plain `bool` so the broadcast loop can keep going on a single failure.
- **Logging**: write one `BroadcastLog` row per attempted subscriber with `status`
  `sent`/`failed`/`skipped` (skipped when Twilio credentials aren't configured), exactly like the
  WhatsApp hook's `on_scores_computed`.
- **Wiring**: register an `on_scores_computed(db, scores, settings)` hook in
  `distribution_wiring.py`-equivalent fashion (that file lives under `backend/app/` and is
  frozen — adding the SMS hook there is a backend-owner change, not a `distribution/` change).
