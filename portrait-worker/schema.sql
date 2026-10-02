CREATE TABLE IF NOT EXISTS context_chunks (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  source_title TEXT NOT NULL,
  source_path TEXT NOT NULL,
  section TEXT NOT NULL,
  content TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS context_fts USING fts5(
  id UNINDEXED,
  source_title,
  section,
  content,
  tokenize = 'porter unicode61'
);

CREATE TABLE IF NOT EXISTS request_limits (
  key TEXT NOT NULL,
  minute INTEGER NOT NULL,
  count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (key, minute)
);

-- Every visitor question and the portrait's answer, for the private inbox at /admin/inbox.
-- matched = the wiki search found something; gap = the answer sounded like it lacked information.
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asked_at TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL DEFAULT '',
  sources TEXT NOT NULL DEFAULT '',
  matched INTEGER NOT NULL DEFAULT 0,
  gap INTEGER NOT NULL DEFAULT 0,
  model TEXT NOT NULL DEFAULT '',
  latency_ms INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS context_source_idx ON context_chunks(source_id);
CREATE INDEX IF NOT EXISTS context_priority_idx ON context_chunks(priority DESC);
