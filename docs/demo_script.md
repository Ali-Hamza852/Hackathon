# SAANS Demo Script (~2:30–3:00)

1. **Hook (15s).** Province-wide reactive school closures during Lahore's smog season respond to a crisis after it's already citywide — most schools that get closed were never actually at high risk that day, and schools that were at risk stayed open elsewhere. SAANS gives each school its own daily number instead of one blanket order.

2. **Show the map (45s).** Open the live dashboard, zoom to Lahore. Point out a Red-tier school and a Green-tier school on the same day, same city, a few kilometers apart — this is the core "aha": targeted guidance beats a province-wide switch.

3. **Show a low-confidence estimate (20s).** Click a school far from any sensor, point at its "estimated" badge and confidence indicator. The system says plainly when it's interpolating instead of measuring directly — that honesty is deliberate, not a gap we're hiding.

4. **Show the WhatsApp message (30s).** A phone receiving the real 7 AM bulletin: tier, plain-language recommendation, disclaimer.

5. **Show the PDF at the gate (20s).** The printable bulletin, black-and-white legible, no data connection required at the school. Emphasize equity and reach for schools without reliable app/data access.

6. **Close (20s).** Roadmap: partnership with the School Education Department Punjab for the full school registry, citywide WhatsApp scale-up, SMS fallback via Twilio (deferred from this build — the WhatsApp Cloud API sandbox and PDF bulletin covered the two highest-feasibility channels; SMS is the next channel to add, reusing the same `subscribers`/`broadcast_log` tables), and extension to construction sites, elderly care, and transit stops.

## Known, deliberate deferrals (say these out loud if asked, don't dodge)

- **SMS/Twilio:** not built in this pass. Reasoning is in `03_PHASE3_DISTRIBUTION_WHATSAPP_PDF_SMS.md` §1 — PDF and WhatsApp were the higher-feasibility channels per the original proposal, and shipping a half-working SMS path risked a live failure during the demo. `distribution/sms/README.md` documents exactly what's needed to add it.
- **Overpass school data:** the manual 25-school seed list is what the demo runs on; Overpass augments it when reachable but isn't required — Overpass mirrors can be flaky/rate-limited from some networks, and the manual list alone already covers the target 20–30 schools across all five zones.
- **AQI provider keys:** the dashboard shows real, non-mocked scores the moment a WAQI or OpenAQ key is configured — both are free and issued within minutes. Without one, `/scores/today` returns an honest empty state rather than fake numbers.
