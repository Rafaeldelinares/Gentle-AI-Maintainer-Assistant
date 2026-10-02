-- ════════════════════════════════════════════════════════════════════════════
--  Gentle-AI Maintainer Assistant — issue store  (SQLite)
--  Experiment harness. Read-only against GitHub; this file is the only state.
--
--  WHY SQLITE, NOT POSTGRES
--    · Engram — the ecosystem's own memory system — is SQLite + FTS5 with
--      tokenize='trigram'. Same problem, same answer, already made.
--    · Engram's own architecture splits local (SQLite) from cloud (Postgres).
--      This store is local.
--    · 20 MB, one writer. A server buys nothing and costs a container,
--      a volume, a port, and the three bugs that came with them.
--
--  WHY ONE issues TABLE, NOT THREE
--    Cross-system analysis is the entire point. Three tables would turn every
--    cross query into a UNION and break a single FK for labels.
--
--  WHY votes AND judgments ARE SEPARATE TABLES
--    This is the Phase 5 decision model encoded structurally. `votes` has no
--    column that could express a decision; `judgments` refuses machine actors.
--
--  This file is idempotent: drop it, re-run it.   sqlite3 exp.db < schema.sql
-- ════════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Systems ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS systems (
  id             INTEGER PRIMARY KEY,
  slug           TEXT    NOT NULL UNIQUE,
  full_name      TEXT    NOT NULL UNIQUE,
  language       TEXT    NOT NULL,
  default_branch TEXT    NOT NULL DEFAULT 'main',
  repo_id        INTEGER,
  notes          TEXT
);

-- ── Issues ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS issues (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  system_id      INTEGER NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
  number         INTEGER NOT NULL,
  title          TEXT    NOT NULL DEFAULT '',
  body           TEXT    NOT NULL DEFAULT '',
  state          TEXT    NOT NULL CHECK (state IN ('open','closed')),
  author         TEXT,
  created_at     TEXT    NOT NULL,
  updated_at     TEXT,
  closed_at      TEXT,
  comments_count INTEGER NOT NULL DEFAULT 0,
  title_prefix   TEXT,                     -- conventional-commit type
  title_scope    TEXT,                     -- the (scope) token
  fetched_at     TEXT    NOT NULL DEFAULT (datetime('now')),
  body_bytes     INTEGER GENERATED ALWAYS AS (length(body)) VIRTUAL,
  UNIQUE (system_id, number)
);
-- Canonical identity is (system_id, number). A bare "#123" is ambiguous
-- across systems and must never be used alone.

CREATE INDEX IF NOT EXISTS issues_system_state_idx ON issues (system_id, state);
CREATE INDEX IF NOT EXISTS issues_created_idx      ON issues (created_at DESC);
CREATE INDEX IF NOT EXISTS issues_title_idx        ON issues (title);

-- ── Full-text search: the same pattern Engram uses ──────────────────────────
-- trigram chosen deliberately: it matches substrings and short texts, which is
-- exactly what cross-system title comparison needs.
CREATE VIRTUAL TABLE IF NOT EXISTS issues_fts USING fts5(
  title,
  body,
  content='issues',
  content_rowid='id',
  tokenize='trigram'
);

CREATE TRIGGER IF NOT EXISTS issues_ai AFTER INSERT ON issues BEGIN
  INSERT INTO issues_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
CREATE TRIGGER IF NOT EXISTS issues_ad AFTER DELETE ON issues BEGIN
  INSERT INTO issues_fts(issues_fts, rowid, title, body) VALUES ('delete', old.id, old.title, old.body);
END;
CREATE TRIGGER IF NOT EXISTS issues_au AFTER UPDATE ON issues BEGIN
  INSERT INTO issues_fts(issues_fts, rowid, title, body) VALUES ('delete', old.id, old.title, old.body);
  INSERT INTO issues_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

-- ── Labels (per system: the vocabularies diverge) ───────────────────────────
CREATE TABLE IF NOT EXISTS labels (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  system_id   INTEGER NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
  name        TEXT    NOT NULL,
  color       TEXT,
  description TEXT,
  UNIQUE (system_id, name)
);

CREATE TABLE IF NOT EXISTS issue_labels (
  issue_id INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  label_id INTEGER NOT NULL REFERENCES labels(id) ON DELETE CASCADE,
  PRIMARY KEY (issue_id, label_id)
);
CREATE INDEX IF NOT EXISTS issue_labels_label_idx ON issue_labels (label_id);

-- ── Comments (optional) ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id   INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  gh_id      INTEGER NOT NULL UNIQUE,
  author     TEXT,
  body       TEXT    NOT NULL DEFAULT '',
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS comments_issue_idx ON comments (issue_id);

-- ── Qualified cross-references: the only high-confidence cross signal ───────
CREATE TABLE IF NOT EXISTS cross_refs (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id         INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  target_system_id INTEGER NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
  target_number    INTEGER NOT NULL,
  location         TEXT    NOT NULL CHECK (location IN ('title','body','comment')),
  raw              TEXT    NOT NULL,
  UNIQUE (issue_id, target_system_id, target_number, location)
);

-- ── Judges: the inference engine is data, not an assumption ─────────────────
CREATE TABLE IF NOT EXISTS judges (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  name     TEXT NOT NULL UNIQUE,
  agent    TEXT,
  model    TEXT NOT NULL,
  provider TEXT NOT NULL,
  effort   TEXT,
  kind     TEXT NOT NULL DEFAULT 'llm' CHECK (kind IN ('llm','human'))
);

INSERT OR IGNORE INTO judges (name, agent, model, provider, effort) VALUES
  ('judge-a', 'jd-judge-a', 'minimax/MiniMax-M3',     'minimax', 'high'),
  ('judge-b', 'jd-judge-b', 'nan/deepseek-v4-flash',  'nan',     'high');

-- ── Experiment runs ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS runs (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  label          TEXT    NOT NULL,
  rubric_version TEXT    NOT NULL,
  sample_hash    TEXT,
  sample_size    INTEGER NOT NULL,
  started_at     TEXT    NOT NULL DEFAULT (datetime('now')),
  finished_at    TEXT,
  notes          TEXT
);

CREATE TABLE IF NOT EXISTS run_issues (
  run_id   INTEGER NOT NULL REFERENCES runs(id)   ON DELETE CASCADE,
  issue_id INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  ordinal  INTEGER NOT NULL,
  PRIMARY KEY (run_id, issue_id)
);

-- ── Judge work units: a cut costs ONE chunk, not the whole run ────────────
-- A subagent in `task` mode is cancelled when the turn is interrupted (the
-- runner does this explicitly: "a human interrupting the turn, a timeout").
-- Splitting a judge's work into chunks, and having each chunk write its own
-- file, means an interruption is survivable and resumable.
CREATE TABLE IF NOT EXISTS judge_tasks (
  run_id      INTEGER NOT NULL REFERENCES runs(id)   ON DELETE CASCADE,
  judge_id    INTEGER NOT NULL REFERENCES judges(id) ON DELETE CASCADE,
  attempt     INTEGER NOT NULL DEFAULT 1,
  chunk       INTEGER NOT NULL,
  status      TEXT    NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','running','done','failed')),
  file        TEXT,
  started_at  TEXT,
  finished_at TEXT,
  note        TEXT,
  PRIMARY KEY (run_id, judge_id, attempt, chunk)
);

-- ── VOTES — pure inference. Notice what is NOT here: no "approved". ─────────
-- `attempt` lets the SAME judge classify the SAME sample twice, which makes
-- test-retest stability measurable — a different question from agreement
-- between two different engines.
CREATE TABLE IF NOT EXISTS votes (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id     INTEGER NOT NULL REFERENCES runs(id)   ON DELETE CASCADE,
  judge_id   INTEGER NOT NULL REFERENCES judges(id) ON DELETE CASCADE,
  issue_id   INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  attempt    INTEGER NOT NULL DEFAULT 1,
  band       TEXT    NOT NULL CHECK (band  IN ('P0','P1','P2','P3','UNKNOWN')),
  cross      TEXT    NOT NULL CHECK (cross IN ('none','dependency','misplaced','implication','UNKNOWN')),
  confidence TEXT             CHECK (confidence IN ('high','medium','low')),
  reason     TEXT,
  raw_line   TEXT,
  created_at TEXT    NOT NULL DEFAULT (datetime('now')),
  UNIQUE (run_id, judge_id, attempt, issue_id)
);

-- ── JUDGMENTS — maintainer decision only. Authoritative. ────────────────────
CREATE TABLE IF NOT EXISTS judgments (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id      INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  kind          TEXT    NOT NULL CHECK (kind IN ('accepted','overridden','deferred')),
  band          TEXT             CHECK (band  IN ('P0','P1','P2','P3')),
  cross         TEXT             CHECK (cross IN ('none','dependency','misplaced','implication')),
  actor         TEXT    NOT NULL,
  decided_at    TEXT    NOT NULL DEFAULT (datetime('now')),
  reason        TEXT    NOT NULL,
  superseded_by INTEGER REFERENCES judgments(id) ON DELETE SET NULL,
  -- Phase 5 rule P1 made structural: a machine identity cannot be the decider.
  CHECK (lower(actor) NOT GLOB 'judge*'  AND lower(actor) NOT GLOB 'jd-*'
         AND lower(actor) NOT GLOB 'gama*'   AND lower(actor) NOT GLOB 'assistant*'
         AND lower(actor) NOT GLOB 'system*' AND lower(actor) NOT GLOB 'bot*'
         AND lower(actor) NOT GLOB 'llm*'    AND lower(actor) NOT GLOB 'model*'),
  CHECK (length(trim(reason)) > 0)
);

-- ════════════════════════════════════════════════════════════════════════════
--  Views
-- ════════════════════════════════════════════════════════════════════════════

DROP VIEW IF EXISTS v_triage_debt;
-- Headline metric: how much of the backlog never passed the first gate.
CREATE VIEW v_triage_debt AS
WITH per_issue AS (
  SELECT i.id, s.slug,
    EXISTS (SELECT 1 FROM issue_labels il JOIN labels l ON l.id = il.label_id
            WHERE il.issue_id = i.id AND l.name = 'status:needs-review') AS needs_review,
    EXISTS (SELECT 1 FROM issue_labels il JOIN labels l ON l.id = il.label_id
            WHERE il.issue_id = i.id AND l.name LIKE 'status:%')          AS has_status
  FROM issues i JOIN systems s ON s.id = i.system_id
  WHERE i.state = 'open'
)
SELECT slug,
       count(*)                                               AS open_total,
       sum(needs_review)                                      AS needs_review,
       sum(NOT has_status)                                    AS no_status_label,
       sum(needs_review OR NOT has_status)                    AS untriaged,
       round(100.0 * sum(needs_review OR NOT has_status) / count(*), 1) AS untriaged_pct
FROM per_issue GROUP BY slug ORDER BY untriaged DESC;

DROP VIEW IF EXISTS v_cross_system;
-- Issues carrying a qualified reference to a DIFFERENT system.
CREATE VIEW v_cross_system AS
SELECT i.id           AS issue_id,
       s.slug         AS filed_in,
       i.number,
       i.title,
       s2.slug        AS refs_system,
       group_concat(DISTINCT cr.target_number) AS target_numbers,
       group_concat(DISTINCT cr.location)      AS locations
FROM cross_refs cr
JOIN issues  i  ON i.id  = cr.issue_id
JOIN systems s  ON s.id  = i.system_id
JOIN systems s2 ON s2.id = cr.target_system_id
WHERE s2.id <> i.system_id
GROUP BY i.id, s.slug, i.number, i.title, s2.slug;

DROP VIEW IF EXISTS v_label_vocabulary;
-- The three vocabularies diverged; making that visible is a finding.
CREATE VIEW v_label_vocabulary AS
SELECT s.slug, l.name, count(il.issue_id) AS issues_using_it
FROM labels l
JOIN systems s ON s.id = l.system_id
LEFT JOIN issue_labels il ON il.label_id = l.id
GROUP BY s.slug, l.name
ORDER BY s.slug, issues_using_it DESC, l.name;

DROP VIEW IF EXISTS v_title_prefix;
-- Conventional-commit prefix distribution: the strongest a-priori signal.
CREATE VIEW v_title_prefix AS
SELECT s.slug,
       coalesce(i.title_prefix, '(sin prefijo)') AS prefix,
       count(*) AS n
FROM issues i JOIN systems s ON s.id = i.system_id
WHERE i.state = 'open'
GROUP BY s.slug, prefix ORDER BY s.slug, n DESC;

DROP VIEW IF EXISTS v_judge_agreement;
-- Per issue and attempt: what each judge said, and whether they agreed.
CREATE VIEW v_judge_agreement AS
SELECT v.run_id, v.attempt, s.slug, i.number, i.title,
  max(CASE WHEN j.name = 'judge-a' THEN v.band  END) AS band_a,
  max(CASE WHEN j.name = 'judge-b' THEN v.band  END) AS band_b,
  max(CASE WHEN j.name = 'judge-a' THEN v.cross END) AS cross_a,
  max(CASE WHEN j.name = 'judge-b' THEN v.cross END) AS cross_b,
  (max(CASE WHEN j.name='judge-a' THEN v.band END)
     IS max(CASE WHEN j.name='judge-b' THEN v.band END))  AS band_agree,
  (max(CASE WHEN j.name='judge-a' THEN v.cross END)
     IS max(CASE WHEN j.name='judge-b' THEN v.cross END)) AS cross_agree
FROM issues i
JOIN systems s ON s.id = i.system_id
JOIN votes v   ON v.issue_id = i.id
JOIN judges j  ON j.id = v.judge_id
GROUP BY v.run_id, v.attempt, s.slug, i.number, i.title
HAVING count(DISTINCT j.id) >= 2;

DROP VIEW IF EXISTS v_judge_stability;
-- Test-retest: the SAME judge, SAME sample, two independent runs.
-- Answers "is this engine consistent with itself?", which agreement between two
-- engines cannot answer.
CREATE VIEW v_judge_stability AS
SELECT j.name AS judge, v.run_id, s.slug, i.number, i.title,
  max(CASE WHEN v.attempt = 1 THEN v.band  END) AS band_t1,
  max(CASE WHEN v.attempt = 2 THEN v.band  END) AS band_t2,
  max(CASE WHEN v.attempt = 1 THEN v.cross END) AS cross_t1,
  max(CASE WHEN v.attempt = 2 THEN v.cross END) AS cross_t2,
  (max(CASE WHEN v.attempt=1 THEN v.band END)
     IS max(CASE WHEN v.attempt=2 THEN v.band END))  AS band_stable,
  (max(CASE WHEN v.attempt=1 THEN v.cross END)
     IS max(CASE WHEN v.attempt=2 THEN v.cross END)) AS cross_stable
FROM votes v
JOIN issues i ON i.id = v.issue_id
JOIN systems s ON s.id = i.system_id
JOIN judges j ON j.id = v.judge_id
GROUP BY j.name, v.run_id, s.slug, i.number, i.title
HAVING count(DISTINCT v.attempt) >= 2;
