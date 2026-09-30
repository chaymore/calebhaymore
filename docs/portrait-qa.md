# Portrait Q&A deployment

The code is complete, but three services must be connected once: Cloudflare, OpenRouter, and a read-only Google service account. No secret belongs in the repository or the browser. If an API key was pasted into chat, revoke it and create a new one before deployment.

## 1. Create D1 and deploy the Worker

From `portrait-worker/`:

```sh
npm ci
npx wrangler login
npx wrangler d1 create portrait-context
```

Copy the returned database ID into `portrait-worker/wrangler.jsonc`, replacing `REPLACE_WITH_D1_DATABASE_ID`, then initialize and deploy:

```sh
npm run db:init:remote
npx wrangler secret put OPENROUTER_API_KEY
npx wrangler secret put SYNC_TOKEN
npx wrangler secret put RATE_LIMIT_SALT
npm run deploy
```

Use separate long random values for `SYNC_TOKEN` and `RATE_LIMIT_SALT`. Save the deployed `https://…workers.dev` URL.

The text model is `anthropic/claude-sonnet-4.5` (`OPENROUTER_MODEL` in `wrangler.jsonc`), with `openai/gpt-4o-mini` as an automatic fallback (`OPENROUTER_FALLBACK_MODEL`). Change either slug to any model listed on OpenRouter. Speech stays on `microsoft/mai-voice-2-flash` with `en-US-Harper:MAI-Voice-2` until a reference clip or Fish voice id is configured. Harper is synthetic, and the chat note says “AI-generated voice.” With a reference configured, `/speak` uses Fish Audio through OpenRouter (`fish-audio/s2.1-pro-free:free` by default; `fish-audio/s2.1-pro` when `FISH_TTS_MODEL` is set to that slug) and the note says “AI voice clone.” See [VOICE-CLONE.md](VOICE-CLONE.md) for the 20–45 second clip, the R2 object, and the `FISH_REFERENCE_ID` secret. `TTS_MODEL` and `TTS_VOICE` in `wrangler.jsonc` still select the Harper fallback.

## 2. Enable the homepage

In the GitHub repository, create an Actions variable:

| Variable | Value |
| --- | --- |
| `PUBLIC_PORTRAIT_API_URL` | Deployed Worker URL |

Re-run **Deploy to GitHub Pages**, or push a commit. The site build embeds only this public endpoint—not an API key.

## 3. Give the sync read-only Drive access

In Google Cloud:

1. In [Google Cloud Console](https://console.cloud.google.com/apis/library/drive.googleapis.com), select or create a project and enable the **Google Drive API**.
2. In **IAM & Admin → Service Accounts**, create a service account such as `portrait-context-reader`. You do not need to grant it project roles or enable domain-wide delegation.
3. Open the new service account, choose **Keys → Add key → Create new key → JSON**, and save the downloaded file securely. It cannot be downloaded again.
4. Share only the wiki's curated **Public Portrait Context** folder with the service account email as **Viewer** (deselect **Notify people**). Do **not** share the entire private Knowledge Wiki.

Add these GitHub Actions secrets:

| Secret | Value |
| --- | --- |
| `DRIVE_WIKI_FOLDER_ID` | `1jRZfC47H6li57fnxvu63_D2OLL_SruBx` (Public Portrait Context folder only) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Complete downloaded service-account JSON; store as a GitHub Actions secret, never paste it in chat |
| `PORTRAIT_SYNC_URL` | Deployed Worker URL |
| `PORTRAIT_SYNC_TOKEN` | Same value stored as the Worker `SYNC_TOKEN` |

Run **Sync portrait context** manually once. It also runs nightly at 08:17 UTC. Check `GET /health`; a positive `chunks` count confirms that searchable context exists.

## 4. Control which wiki content is shared

Everything in the shared Drive folder is synced **unless you exclude it**:

```yaml
---
portrait_access: private   # keep this page out of the chatbot
portrait_priority: 70      # optional: higher wins when nothing matches the question
---
```

- Pages under `people/` or `sources/` folders are skipped unless the page says `portrait_access: public`.
- Folders named `raw`, `.private`, and `.obsidian` are never read.
- Sections titled Related, Open questions, and Privacy notes are dropped.
- The sync divides pages by Markdown headings and removes Obsidian link syntax. A sync with zero shareable pages fails without deleting the live database.

Only the Drive folder you share with the service account is ever visible. Keep raw message exports, contact details, financial pages, and calendars out of that folder (or mark them `private`).

## 5. Always-on facts (`portrait-worker/src/persona.ts`)

Family, hobbies, favorite books and movies, and recent activity live in `persona.ts` and are included in **every** answer, so they don't depend on wiki search. Edit it, commit, and run `npm run deploy` in `portrait-worker/`. The repository is public, so only put things there you're happy for anyone to read. The personality and the rules for improvising live in `portrait-worker/src/prompt.ts`.

## 6. Review visitor questions

Every question and answer is saved to D1 (no IP address stored). After deploying, run `npm run db:init:remote` once to create the table, then open `https://<your-worker>.workers.dev/admin/inbox` and enter the `SYNC_TOKEN`. Amber tags mark likely gaps: **admitted a gap** (the answer sounded unsure) and **no wiki match** (the wiki search found nothing, which is normal for questions `persona.ts` already covers). Add what's missing to `persona.ts` or the wiki. The raw data is at `GET /admin/questions` with `Authorization: Bearer <SYNC_TOKEN>`.

## API behavior

- `POST /ask` accepts a question and up to four recent messages, retrieves up to twelve D1 chunks, and streams plain text.
- `POST /speak` converts the completed answer into MP3. Without a voice reference it uses the Harper fallback; with one, it uses the Fish clone and sets `x-portrait-voice`. See [VOICE-CLONE.md](VOICE-CLONE.md).
- Spoken questions are transcribed in the browser with the Web Speech API. The transcript is shown as the visitor message and then sent to the existing `/ask` and `/speak` routes. No speech-to-text secret or Worker route is required. Mouth animation is driven only by the reply MP3.
- `GET /admin/inbox` and `GET /admin/questions` show saved questions (token required for the data).
- `POST /admin/sync` replaces the D1 snapshot and requires the sync bearer token.
- `GET /health` reports the indexed chunk count but no private content.
- Requests are CORS-restricted to the configured site and locally hashed/rate-limited without retaining raw IP addresses.

## Local Worker development

Create `portrait-worker/.dev.vars` (gitignored):

```dotenv
OPENROUTER_API_KEY=...
SYNC_TOKEN=...
RATE_LIMIT_SALT=...
# Optional clone. See docs/VOICE-CLONE.md. A 20–45s clip belongs in R2, not here.
# FISH_REFERENCE_ID=
# FISH_REFERENCE_TRANSCRIPT=
# FISH_REFERENCE_AUDIO=
```

Replace the D1 ID in `wrangler.jsonc`, then:

```sh
npm run db:init:local
npm run dev
```

For local Astro, use `PUBLIC_PORTRAIT_API_URL=http://localhost:8787 npm run dev`.

## Speech input

The **mic** control sits in the existing Ask Caleb composer. Tap it to talk, or hold it and release to send. Browsers with `SpeechRecognition` or `webkitSpeechRecognition` (Chrome and Safari, including their mobile versions, on localhost or HTTPS) transcribe speech on the device’s speech service. Firefox and other browsers without that API keep typed questions working and show “Speech input isn’t available in this browser.” Denying the microphone shows “Microphone permission denied.” Silence shows “Didn’t catch that.”

Nothing in this path calls `getUserMedia` for the portrait. `window.calebPortrait.connectAudio` still receives only the reply audio element, which now drives mouth shapes from visemes instead of volume alone.

To try it against a live Worker, set `PUBLIC_PORTRAIT_API_URL` to the deployed Worker URL and open the site from an allowed origin (`https://calebhaymore.com`, `https://chaymore.github.io`, or local `http://localhost` / `http://127.0.0.1`). Allow the microphone, ask a short question, and confirm the transcript and the streamed answer both appear as text before the face speaks. Typed questions should behave as before when the mic is left unused.
