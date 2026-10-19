# Calendar booking (/calendar)

`calebhaymore.com/calendar` is a Calendly-style page. Visitors pick a 15 or 30 minute slot, add their name, email, and a short note, and the meeting goes straight onto Google Calendar with a Google Meet link and an invite to the visitor.

## How it works

- `src/pages/calendar.astro` is the static page. It calls the same Worker as Ask Caleb (`PUBLIC_PORTRAIT_API_URL`).
- `GET /calendar/availability` asks Google for **free/busy only** on the calendars in `BOOKING_BUSY_CALENDARS`, then returns open start times. Event titles and details never leave Google.
- `POST /calendar/book` checks free/busy again (so two people cannot take the same slot), then creates the event on `BOOKING_CALENDAR_ID` with `sendUpdates=all`. Google emails the visitor the invite.
- If a busy calendar cannot be read, the Worker shows no times instead of showing false free time.
- Bookings are limited to 3 per minute per visitor, and a hidden form field catches simple bots.
- `?demo` on the page shows sample times without calling the Worker, for previewing design changes.

## Settings (`portrait-worker/wrangler.jsonc`)

| Variable | Default | Meaning |
| --- | --- | --- |
| `BOOKING_CALENDAR_ID` | `primary` | Calendar that receives bookings |
| `BOOKING_BUSY_CALENDARS` | `primary,caleb.haymore@joinleland.com` | Calendars whose events block time |
| `BOOKING_TIMEZONE` | `America/Denver` | Time zone of the hours below |
| `BOOKING_HOURS` | `Mon-Fri 09:00-17:00` | Bookable windows, for example `Mon-Thu 10:00-12:00; Fri 13:00-16:00` |
| `BOOKING_DAYS_AHEAD` | `21` | How far ahead people can book |
| `BOOKING_MIN_NOTICE_HOURS` | `12` | Earliest booking from now |
| `BOOKING_BUFFER_MINUTES` | `5` | Free gap kept before and after other events |

Changes deploy with the **Deploy portrait worker** Action when they reach `main`.

## One-time Google setup

The Worker acts as `calebhaymore@gmail.com` through an OAuth refresh token. A service account cannot send invites from a personal Gmail calendar, so OAuth is required.

1. In [Google Cloud Console](https://console.cloud.google.com/), use the same project as the Drive sync. Enable the **Google Calendar API**.
2. Open **Google Auth Platform → Branding** (OAuth consent screen). Set user type **External** and fill in the required app name and email.
3. Open **Audience** and select **Publish app** (status **In production**).
   Caution: in **Testing** status, Google expires the refresh token after 7 days and booking stops. You do not need Google verification; you only see an "unverified app" warning when you sign in yourself.
4. Open **Clients → Create client → Desktop app**. Copy the client ID and client secret.
5. On your computer, from the repository root, run:
   ```sh
   GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... node scripts/google-calendar-token.mjs
   ```
   Sign in as `calebhaymore@gmail.com` and allow both permissions (see free/busy, and edit events). The terminal prints the refresh token.
6. Store the three values as Worker secrets (from `portrait-worker/`):
   ```sh
   npx wrangler secret put GOOGLE_CLIENT_ID
   npx wrangler secret put GOOGLE_CLIENT_SECRET
   npx wrangler secret put GOOGLE_REFRESH_TOKEN
   ```
   Or add them in the Cloudflare dashboard: Workers & Pages → `caleb-portrait-api` → Settings → Variables and Secrets (type **Secret**).
7. Check `GET <worker>/health`. `"booking": true` means the secrets are present. Then open `/calendar`.

Never paste these values in chat or commit them.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| Page says "scheduler is offline" | Secrets missing, `PUBLIC_PORTRAIT_API_URL` not set, or a Google error. Check Worker logs in Cloudflare (Observability). |
| Log says `Free/busy unavailable for caleb.haymore@joinleland.com` | The Gmail account cannot see that calendar's free/busy. Share it with `calebhaymore@gmail.com` ("See only free/busy"), or remove it from `BOOKING_BUSY_CALENDARS`. |
| Log says `invalid_grant` | The refresh token expired or was revoked. Confirm the app is **In production**, then repeat step 5–6. |
