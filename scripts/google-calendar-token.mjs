// One-time helper: signs in to Google and prints a refresh token for the booking Worker.
// Usage: GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... node scripts/google-calendar-token.mjs
// Needs a "Desktop app" OAuth client. See docs/calendar-booking.md.
import { createServer } from 'node:http';
import { exec } from 'node:child_process';

const clientId = process.env.GOOGLE_CLIENT_ID;
const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
if (!clientId || !clientSecret) {
  console.error('Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET first.');
  process.exit(1);
}

const port = 8765;
const redirectUri = `http://127.0.0.1:${port}`;
// freebusy: read busy times only (no event details). events: create the booked meetings.
const scopes = ['https://www.googleapis.com/auth/calendar.freebusy', 'https://www.googleapis.com/auth/calendar.events'];
const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
  client_id: clientId,
  redirect_uri: redirectUri,
  response_type: 'code',
  scope: scopes.join(' '),
  access_type: 'offline',
  prompt: 'consent',
})}`;

const server = createServer(async (request, response) => {
  const code = new URL(request.url ?? '/', redirectUri).searchParams.get('code');
  if (!code) { response.end('Waiting for Google sign-in…'); return; }
  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ code, client_id: clientId, client_secret: clientSecret, redirect_uri: redirectUri, grant_type: 'authorization_code' }),
  });
  const tokens = await tokenResponse.json();
  if (!tokens.refresh_token) {
    response.end('No refresh token returned. Check the terminal.');
    console.error(tokens);
  } else {
    response.end('Done. You can close this tab and go back to the terminal.');
    console.log('\nGOOGLE_REFRESH_TOKEN (store it as a Worker secret, never commit it):\n');
    console.log(tokens.refresh_token);
  }
  server.close();
});

server.listen(port, '127.0.0.1', () => {
  console.log(`Open this URL and sign in as the calendar owner:\n\n${authUrl}\n`);
  const opener = process.platform === 'darwin' ? 'open' : process.platform === 'win32' ? 'start ""' : 'xdg-open';
  exec(`${opener} "${authUrl}"`, () => {});
});
