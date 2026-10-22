import test from 'node:test';
import assert from 'node:assert/strict';
import { computeSlots, parseHours, zonedTimeToUtc } from '../portrait-worker/src/slots.ts';

const tz = 'America/Denver';
const base = { timeZone: tz, hours: parseHours('Mon-Fri 09:00-17:00'), busy: [], daysAhead: 0, minNoticeMinutes: 0, bufferMinutes: 0 };
// Monday 2026-10-19, 06:00 in Denver (MDT, UTC-6).
const mondayMorning = Date.parse('2026-10-19T12:00:00Z');

test('parseHours reads ranges, lists, and several windows', () => {
  assert.deepEqual(parseHours('Mon-Wed 09:00-10:30').map(rule => rule.day), [1, 2, 3]);
  assert.deepEqual(parseHours('Tue,Thu 13:00-14:00; Sat 10:00-11:00'), [
    { day: 2, from: 780, to: 840 }, { day: 4, from: 780, to: 840 }, { day: 6, from: 600, to: 660 },
  ]);
  assert.throws(() => parseHours('Mon 17:00-09:00'));
  assert.throws(() => parseHours('Someday 09:00-10:00'));
});

test('local wall time converts to UTC on both sides of daylight time', () => {
  assert.equal(new Date(zonedTimeToUtc(2026, 10, 19, 9 * 60, tz)).toISOString(), '2026-10-19T15:00:00.000Z');
  assert.equal(new Date(zonedTimeToUtc(2026, 11, 2, 9 * 60, tz)).toISOString(), '2026-11-02T16:00:00.000Z');
});

test('a full free day has 16 half-hour slots and 32 quarter-hour slots', () => {
  const thirty = computeSlots({ ...base, now: mondayMorning, durationMinutes: 30 });
  assert.equal(thirty.length, 16);
  assert.equal(new Date(thirty[0]).toISOString(), '2026-10-19T15:00:00.000Z');
  assert.equal(new Date(thirty.at(-1)).toISOString(), '2026-10-19T22:30:00.000Z');
  assert.equal(computeSlots({ ...base, now: mondayMorning, durationMinutes: 15 }).length, 32);
});

test('busy time and its buffer block overlapping slots', () => {
  const busy = [{ start: Date.parse('2026-10-19T16:00:00Z'), end: Date.parse('2026-10-19T17:00:00Z') }]; // 10–11 local
  const slots = computeSlots({ ...base, now: mondayMorning, busy, bufferMinutes: 5, durationMinutes: 30 })
    .map(start => new Date(start).toISOString().slice(11, 16));
  assert.ok(slots.includes('15:00'));
  assert.ok(!slots.includes('15:30'), '9:30 ends inside the 5 minute buffer before the meeting');
  assert.ok(!slots.includes('16:00') && !slots.includes('16:30'));
  assert.ok(!slots.includes('17:00'), '11:00 starts inside the buffer after the meeting');
  assert.ok(slots.includes('17:30'));
});

test('notice period and weekends remove slots', () => {
  const noon = Date.parse('2026-10-19T18:00:00Z');
  const slots = computeSlots({ ...base, now: noon, minNoticeMinutes: 120, durationMinutes: 30 });
  assert.equal(new Date(slots[0]).toISOString(), '2026-10-19T20:00:00.000Z');
  const saturday = Date.parse('2026-10-24T15:00:00Z');
  assert.equal(computeSlots({ ...base, now: saturday, daysAhead: 1, durationMinutes: 30 }).length, 0);
});
