// Calendly-style booking for calebhaymore.com/calendar.
// Free/busy and new events go through the Google Calendar API with an OAuth refresh token for Caleb's account.
// Visitors only ever see open start times, never event titles or details. See docs/calendar-booking.md.
import { computeSlots, parseHours, type Interval } from './slots';

export interface BookingEnv {
  GOOGLE_CLIENT_ID?: string;
  GOOGLE_CLIENT_SECRET?: string;
  GOOGLE_REFRESH_TOKEN?: string;
  // Calendar that receives new bookings. Default: primary.
  BOOKING_CALENDAR_ID?: string;
  // Comma-separated calendars whose events block time. Default: the booking calendar.
  BOOKING_BUSY_CALENDARS?: string;
  BOOKING_TIMEZONE?: string;
  BOOKING_HOURS?: string;
  BOOKING_DAYS_AHEAD?: string;
  BOOKING_MIN_NOTICE_HOURS?: string;
  BOOKING_BUFFER_MINUTES?: string;
}

export const BOOKING_DURATIONS = [15, 30];

export interface BookingRequest {
  start: number;
  duration: number;
  name: string;
  email: string;
  topic: string;
  timeZone: string;
}

export class BookingError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

interface BookingConfig {
  calendarId: string;
  busyCalendars: string[];
  timeZone: string;
  hours: ReturnType<typeof parseHours>;
  daysAhead: number;
  minNoticeMinutes: number;
  bufferMinutes: number;
}

export function bookingConfigured(env: BookingEnv) {
  return Boolean(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET && env.GOOGLE_REFRESH_TOKEN);
}

function config(env: BookingEnv): BookingConfig {
  const number = (value: string | undefined, fallback: number, max: number) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? Math.min(parsed, max) : fallback;
  };
  const calendarId = env.BOOKING_CALENDAR_ID?.trim() || 'primary';
  const busyCalendars = (env.BOOKING_BUSY_CALENDARS || calendarId).split(',').map(id => id.trim()).filter(Boolean);
  return {
    calendarId,
    busyCalendars: busyCalendars.length ? busyCalendars : [calendarId],
    timeZone: env.BOOKING_TIMEZONE?.trim() || 'America/Denver',
    hours: parseHours(env.BOOKING_HOURS || 'Mon-Fri 09:00-17:00'),
    daysAhead: number(env.BOOKING_DAYS_AHEAD, 21, 60),
    minNoticeMinutes: number(env.BOOKING_MIN_NOTICE_HOURS, 12, 24 * 14) * 60,
    bufferMinutes: number(env.BOOKING_BUFFER_MINUTES, 5, 60),
  };
}

// Open slot start times (ISO strings) for each meeting length.
export async function availability(env: BookingEnv, now = Date.now()) {
  const settings = config(env);
  const busy = await freeBusy(env, settings, now);
  const slots: Record<string, string[]> = {};
  for (const duration of BOOKING_DURATIONS) {
    slots[duration] = computeSlots({ ...settings, now, busy, durationMinutes: duration }).map(start => new Date(start).toISOString());
  }
  return { timeZone: settings.timeZone, durations: BOOKING_DURATIONS, slots };
}

// Re-checks the calendar right before writing, so a slot taken since the page loaded is refused.
export async function book(env: BookingEnv, request: BookingRequest) {
  const settings = config(env);
  const now = Date.now();
  const busy = await freeBusy(env, settings, now);
  const open = computeSlots({ ...settings, now, busy, durationMinutes: request.duration });
  if (!open.includes(request.start)) throw new BookingError('That time was just taken. Please pick another one.', 409);

  const end = request.start + request.duration * 60000;
  const description = [
    `Booked from calebhaymore.com/calendar`,
    ``,
    `Name: ${request.name}`,
    `Email: ${request.email}`,
    `Their time zone: ${request.timeZone || 'unknown'}`,
    ``,
    `What they want to talk about:`,
    request.topic,
  ].join('\n');

  const response = await googleFetch(env, `/calendars/${encodeURIComponent(settings.calendarId)}/events?conferenceDataVersion=1&sendUpdates=all`, {
    method: 'POST',
    body: JSON.stringify({
      summary: `${request.name} <> Caleb Haymore (${request.duration} min)`,
      description,
      start: { dateTime: new Date(request.start).toISOString(), timeZone: settings.timeZone },
      end: { dateTime: new Date(end).toISOString(), timeZone: settings.timeZone },
      attendees: [{ email: request.email, displayName: request.name }],
      conferenceData: { createRequest: { requestId: crypto.randomUUID(), conferenceSolutionKey: { type: 'hangoutsMeet' } } },
      reminders: { useDefault: true },
      extendedProperties: { private: { bookedVia: 'calebhaymore.com/calendar' } },
    }),
  });
  const event = await response.json() as { hangoutLink?: string };
  return { start: new Date(request.start).toISOString(), end: new Date(end).toISOString(), meetLink: event.hangoutLink ?? '' };
}

// Checks and trims what the visitor sent. Throws BookingError with a message the page can show.
export function parseBookingRequest(body: Record<string, unknown>): BookingRequest {
  const text = (key: string, max: number) => typeof body[key] === 'string' ? (body[key] as string).trim().slice(0, max) : '';
  // Hidden "website" field: people never see it, form-filling bots usually do.
  if (text('website', 200)) throw new BookingError('Booking failed.', 400);
  const duration = Number(body.duration);
  if (!BOOKING_DURATIONS.includes(duration)) throw new BookingError('Pick a 15 or 30 minute meeting.', 400);
  const start = Date.parse(text('start', 40));
  if (!Number.isFinite(start)) throw new BookingError('Pick a time.', 400);
  const name = text('name', 80).replace(/[\r\n]+/g, ' ');
  if (name.length < 2) throw new BookingError('Please add your name.', 400);
  const email = text('email', 200).toLowerCase();
  if (!/^[^\s@<>(),;:"]+@[^\s@<>(),;:"]+\.[a-z]{2,}$/i.test(email)) throw new BookingError('Please add a valid email address.', 400);
  const topic = text('topic', 600);
  if (topic.length < 3) throw new BookingError('Add a short note about what you want to talk about.', 400);
  return { start, duration, name, email, topic, timeZone: text('timeZone', 64) };
}

async function freeBusy(env: BookingEnv, settings: BookingConfig, now: number): Promise<Interval[]> {
  const response = await googleFetch(env, '/freeBusy', {
    method: 'POST',
    body: JSON.stringify({
      timeMin: new Date(now).toISOString(),
      timeMax: new Date(now + (settings.daysAhead + 2) * 86400000).toISOString(),
      items: settings.busyCalendars.map(id => ({ id })),
    }),
  });
  const data = await response.json() as { calendars?: Record<string, { busy?: Array<{ start: string; end: string }>; errors?: unknown[] }> };
  const busy: Interval[] = [];
  for (const [id, calendar] of Object.entries(data.calendars ?? {})) {
    // A calendar we cannot read must not show as "free"; fail closed.
    if (calendar.errors?.length) throw new Error(`Free/busy unavailable for ${id}: ${JSON.stringify(calendar.errors)}`);
    for (const item of calendar.busy ?? []) busy.push({ start: Date.parse(item.start), end: Date.parse(item.end) });
  }
  return busy;
}

let cachedToken: { value: string; expires: number } | null = null;

async function accessToken(env: BookingEnv): Promise<string> {
  if (cachedToken && cachedToken.expires > Date.now() + 60000) return cachedToken.value;
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: env.GOOGLE_CLIENT_ID ?? '',
      client_secret: env.GOOGLE_CLIENT_SECRET ?? '',
      refresh_token: env.GOOGLE_REFRESH_TOKEN ?? '',
      grant_type: 'refresh_token',
    }),
  });
  if (!response.ok) throw new Error(`Google token refresh failed ${response.status}: ${await response.text()}`);
  const data = await response.json() as { access_token: string; expires_in: number };
  cachedToken = { value: data.access_token, expires: Date.now() + data.expires_in * 1000 };
  return data.access_token;
}

async function googleFetch(env: BookingEnv, path: string, init: RequestInit): Promise<Response> {
  const response = await fetch(`https://www.googleapis.com/calendar/v3${path}`, {
    ...init,
    headers: { authorization: `Bearer ${await accessToken(env)}`, 'content-type': 'application/json' },
  });
  if (!response.ok) throw new Error(`Google Calendar ${path} failed ${response.status}: ${await response.text()}`);
  return response;
}
