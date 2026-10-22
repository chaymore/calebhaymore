// Pure scheduling math for the /calendar booking page. No network calls, so tests can import it directly.

export interface Interval { start: number; end: number }

// One bookable window, in the owner's local time. day: 0 = Sunday … 6 = Saturday. Minutes since local midnight.
export interface HoursRule { day: number; from: number; to: number }

export interface SlotOptions {
  now: number;
  timeZone: string;
  hours: HoursRule[];
  busy: Interval[];
  durationMinutes: number;
  daysAhead: number;
  minNoticeMinutes: number;
  bufferMinutes: number;
}

const DAY_NAMES = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];

// Parses "Mon-Fri 09:00-17:00; Sat 10:00-12:00". Day lists may use ranges (Mon-Fri) or commas (Mon,Wed).
export function parseHours(spec: string): HoursRule[] {
  const rules: HoursRule[] = [];
  for (const part of spec.split(';').map(item => item.trim()).filter(Boolean)) {
    const match = part.match(/^([a-z,\-\s]+?)\s+(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$/i);
    if (!match) throw new Error(`Invalid BOOKING_HOURS entry: ${part}`);
    const from = Number(match[2]) * 60 + Number(match[3]);
    const to = Number(match[4]) * 60 + Number(match[5]);
    if (to <= from || to > 24 * 60) throw new Error(`Invalid BOOKING_HOURS time range: ${part}`);
    for (const day of parseDays(match[1])) rules.push({ day, from, to });
  }
  return rules;
}

function parseDays(spec: string): number[] {
  const days = new Set<number>();
  for (const token of spec.toLowerCase().split(',').map(item => item.trim()).filter(Boolean)) {
    const [first, last = first] = token.split('-').map(name => DAY_NAMES.indexOf(name.trim().slice(0, 3)));
    if (first < 0 || last < 0) throw new Error(`Invalid BOOKING_HOURS day: ${token}`);
    for (let day = first; ; day = (day + 1) % 7) {
      days.add(day);
      if (day === last) break;
    }
  }
  return [...days];
}

// Minutes the zone is ahead of UTC at this instant (America/Denver in winter = -420).
export function zoneOffsetMinutes(utcMs: number, timeZone: string): number {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric',
  }).formatToParts(new Date(utcMs));
  const get = (type: string) => Number(parts.find(part => part.type === type)?.value);
  const asUtc = Date.UTC(get('year'), get('month') - 1, get('day'), get('hour'), get('minute'), get('second'));
  return Math.round((asUtc - Math.floor(utcMs / 1000) * 1000) / 60000);
}

// The UTC instant of a local wall-clock time. Checks the offset twice so days that change to or from daylight time are right.
export function zonedTimeToUtc(year: number, month: number, day: number, minutes: number, timeZone: string): number {
  const wall = Date.UTC(year, month - 1, day, 0, minutes);
  const first = wall - zoneOffsetMinutes(wall, timeZone) * 60000;
  return wall - zoneOffsetMinutes(first, timeZone) * 60000;
}

function localDate(utcMs: number, timeZone: string) {
  const shifted = new Date(utcMs + zoneOffsetMinutes(utcMs, timeZone) * 60000);
  return { year: shifted.getUTCFullYear(), month: shifted.getUTCMonth() + 1, day: shifted.getUTCDate() };
}

// Start times (UTC ms) of every free slot. A slot is free when it sits inside a bookable window,
// starts after the notice period, and is at least bufferMinutes away from every busy interval.
export function computeSlots(options: SlotOptions): number[] {
  const { now, timeZone, hours, durationMinutes, daysAhead, minNoticeMinutes, bufferMinutes } = options;
  const length = durationMinutes * 60000;
  const buffer = bufferMinutes * 60000;
  const earliest = now + minNoticeMinutes * 60000;
  const busy = options.busy.map(item => ({ start: item.start - buffer, end: item.end + buffer })).sort((a, b) => a.start - b.start);
  const today = localDate(now, timeZone);
  const slots: number[] = [];

  for (let offset = 0; offset <= daysAhead; offset += 1) {
    const date = new Date(Date.UTC(today.year, today.month - 1, today.day + offset));
    const [year, month, day] = [date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate()];
    for (const rule of hours.filter(item => item.day === date.getUTCDay())) {
      // Slots start on multiples of the meeting length: 15-minute meetings every 15 minutes, 30-minute meetings on the hour and half hour.
      for (let minute = Math.ceil(rule.from / durationMinutes) * durationMinutes; minute + durationMinutes <= rule.to; minute += durationMinutes) {
        const start = zonedTimeToUtc(year, month, day, minute, timeZone);
        const end = start + length;
        if (start < earliest) continue;
        if (busy.some(item => item.start < end && item.end > start)) continue;
        slots.push(start);
      }
    }
  }
  return [...new Set(slots)].sort((a, b) => a - b);
}
