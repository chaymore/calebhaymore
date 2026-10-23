import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveView, asciiCell, ASCII_RAMP } from '../src/scripts/portrait-view.ts';

test('a ?view= link wins over the stored choice', () => {
  assert.equal(resolveView('?view=ascii', 'dots'), 'ascii');
  assert.equal(resolveView('?view=dots', 'ascii'), 'dots');
});

test('without a link the stored choice holds, and dots is the default', () => {
  assert.equal(resolveView('', 'ascii'), 'ascii');
  assert.equal(resolveView('', null), 'dots');
  assert.equal(resolveView('?view=braille', 'nonsense'), 'dots');
});

test('ASCII cells stay readable on small and large stages', () => {
  assert.deepEqual(asciiCell(400, 1), { width: 4, height: 7 });
  assert.deepEqual(asciiCell(850, 2), { width: 12, height: 20 });
  assert.deepEqual(asciiCell(2000, 1), { width: 7, height: 12 });
  assert.equal(ASCII_RAMP[0], ' ');
});
