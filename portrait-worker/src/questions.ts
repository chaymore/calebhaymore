// Saves every visitor question and the portrait's answer so Caleb can review them and fill gaps.
// No IP address or other visitor identifier is stored.

export interface QuestionLog {
  question: string;
  answer: string;
  sources: string[];
  matched: boolean;
  model: string;
  latencyMs: number;
}

// Phrases that suggest the portrait admitted it lacked information.
const ADMITTED_GAP = /\b(don'?t|do not|didn'?t|no)\b[^.!?]{0,40}\b(know|idea|context|details|info|information)\b|not sure|can'?t say|email (me|caleb)|calebhaymore@gmail\.com/i;

export async function saveQuestion(db: D1Database, log: QuestionLog) {
  const gap = ADMITTED_GAP.test(log.answer) ? 1 : 0;
  await db.prepare(`INSERT INTO questions (asked_at, question, answer, sources, matched, gap, model, latency_ms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
    .bind(new Date().toISOString(), log.question, log.answer.slice(0, 4000), log.sources.join(' | ').slice(0, 1000), log.matched ? 1 : 0, gap, log.model, log.latencyMs)
    .run();
}

export async function listQuestions(db: D1Database, url: URL) {
  const limit = Math.max(1, Math.min(200, Number(url.searchParams.get('limit')) || 100));
  const before = Number(url.searchParams.get('before')) || Number.MAX_SAFE_INTEGER;
  const onlyGaps = url.searchParams.get('gaps') === '1';
  const result = await db.prepare(`SELECT id, asked_at, question, answer, sources, matched, gap, model, latency_ms
    FROM questions WHERE id < ? AND (? = 0 OR gap = 1 OR matched = 0) ORDER BY id DESC LIMIT ?`)
    .bind(before, onlyGaps ? 1 : 0, limit).all();
  return result.results;
}

// A self-contained page. It holds no data: it asks for your sync token, then fetches
// /admin/questions with an Authorization header. All visitor text is inserted with textContent, never as HTML.
export const inboxPage = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Portrait questions</title>
<style>
  body{font:16px/1.5 system-ui,sans-serif;background:#0b0b0c;color:#e4e4e7;margin:0;padding:24px;max-width:860px;margin-inline:auto}
  h1{font-size:20px;margin:0 0 4px} .sub{color:#71717a;font-size:14px;margin-bottom:16px}
  .bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  button,input{font:inherit;padding:8px 12px;border-radius:8px;border:1px solid #3f3f46;background:#18181b;color:inherit}
  button{cursor:pointer} button[aria-pressed=true]{background:#e4e4e7;color:#0b0b0c}
  .card{border:1px solid #27272a;border-radius:12px;padding:14px 16px;margin-bottom:12px;background:#111113}
  .q{font-weight:600;white-space:pre-wrap} .a{margin-top:8px;color:#a1a1aa;white-space:pre-wrap}
  .meta{margin-top:10px;font-size:12px;color:#71717a;display:flex;gap:8px;flex-wrap:wrap}
  .tag{border:1px solid #52525b;border-radius:999px;padding:1px 8px} .warn{border-color:#f59e0b;color:#fbbf24}
  #err{color:#f87171}
</style></head><body>
<h1>Portrait questions</h1><div class="sub">Newest first. Amber tags mark likely gaps to fill in the persona or wiki.</div>
<div class="bar">
  <input id="token" type="password" placeholder="Sync token" autocomplete="off">
  <button id="load">Load</button>
  <button id="gaps" aria-pressed="false">Only possible gaps</button>
  <button id="more" hidden>Load older</button>
</div>
<div id="err"></div><div id="list"></div>
<script>
const $ = id => document.getElementById(id);
let last = null, gapsOnly = false;
$('token').value = sessionStorage.getItem('token') || '';
async function load(reset) {
  $('err').textContent = '';
  const token = $('token').value.trim();
  if (!token) { $('err').textContent = 'Enter the sync token.'; return; }
  const params = new URLSearchParams({ limit: '50' });
  if (gapsOnly) params.set('gaps', '1');
  if (!reset && last) params.set('before', String(last));
  const res = await fetch('/admin/questions?' + params, { headers: { authorization: 'Bearer ' + token } });
  if (!res.ok) { $('err').textContent = res.status === 401 ? 'Wrong token.' : 'Request failed (' + res.status + ').'; return; }
  sessionStorage.setItem('token', token);
  const { questions } = await res.json();
  if (reset) $('list').replaceChildren();
  for (const item of questions) $('list').append(card(item));
  if (questions.length) last = questions[questions.length - 1].id;
  $('more').hidden = questions.length < 50;
  if (reset && !questions.length) $('list').textContent = 'No questions yet.';
}
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
function card(item) {
  const c = el('div', 'card');
  c.append(el('div', 'q', item.question), el('div', 'a', item.answer));
  const meta = el('div', 'meta', new Date(item.asked_at).toLocaleString());
  if (item.gap) meta.append(el('span', 'tag warn', 'admitted a gap'));
  if (!item.matched) meta.append(el('span', 'tag warn', 'no wiki match'));
  if (item.sources) meta.append(el('span', 'tag', item.sources));
  c.append(meta);
  return c;
}
$('load').onclick = () => load(true);
$('more').onclick = () => load(false);
$('gaps').onclick = () => { gapsOnly = !gapsOnly; $('gaps').setAttribute('aria-pressed', String(gapsOnly)); load(true); };
if ($('token').value) load(true);
</script></body></html>`;
