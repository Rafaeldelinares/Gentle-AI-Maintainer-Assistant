#!/usr/bin/env python3
"""
core.py — Board domain: local state, append-only event log, deterministic ingest.

Design rules (see DECISIONS.md D-018..D-023):

  - **Read-only toward GitHub.** The board never comments, labels, closes or transfers
    anything. It has no write path to any network service. `tools/readonly_check.py`
    enforces it.
  - **Derived vs. decided.** The engine derives a *suggested* column and a suggested
    band. Only a human writes `card_state` and `human_labels`.
  - **The engine can only suggest blocking columns.** It may suggest `falta_info`
    (a required form field is missing) or `revision_humana` (a hard signal sits under a
    non-bug prefix, or the issue is a candidate P0). It never suggests `listo_mantener`:
    promoting work to a maintainer is a human judgement.
  - **Append-only.** Every move and every verdict is an event. `card_state` and
    `human_labels` are projections that can be rebuilt from the log, which
    `tools/board_rebuild_check.py` verifies.
  - **One board per application.** Cards are never mixed across repositories.

No HTTP lives here. No business logic lives in the UI.
"""

import hashlib
import json
import sqlite3
import sys
import threading
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "modules"))

from rules import classify_issue_deterministically, requires_human_review  # noqa: E402

try:  # module A helpers are optional: without them the board still works
    from completeness import split_sections, label_status, kind_of  # noqa: E402
    from templates import all_repo_templates, required_fields, templates_present  # noqa: E402
    _COMPLETENESS_AVAILABLE = True
except Exception:  # pragma: no cover
    _COMPLETENESS_AVAILABLE = False

# The issue forms are parsed once per (slug, kind); parsing them per issue was O(n) YAML.
_REQUIRED_CONTENT_CACHE = {}
_SNAPSHOT_META_CACHE = {}

COLUMNS = ["entrada", "falta_info", "revision_humana", "listo_mantener", "en_manos"]
ARCHIVE_COLUMN = "archivado"
ALL_COLUMNS = COLUMNS + [ARCHIVE_COLUMN]

COLUMN_LABELS = {
    "entrada": "Entrada",
    "falta_info": "Falta información",
    "revision_humana": "Revisión humana",
    "listo_mantener": "Listo para el mantenedor",
    "en_manos": "En manos del mantenedor",
    "archivado": "Archivado",
}

# Only blocking columns may be suggested by the engine.
SUGGESTIBLE_COLUMNS = ("falta_info", "revision_humana")

VERDICTS = ("P0", "P1", "P2", "P3", "no_valida")

# Severidad de la información faltante: proporción de campos obligatorios ausentes.
# La escala es relativa, no absoluta: faltar 1 de 2 campos es peor que faltar 1 de 8.
# La regla vive acá y no en el JavaScript (DECISIONS.md D-023).
MISSING_SEVERITY_THRESHOLDS = (
    (0.80, "critical"),   # rojo
    (0.60, "high"),       # naranja
    (0.34, "medium"),     # amarillo
    (0.00, "low"),        # blanco
)
MISSING_SEVERITY_ORDER = ("none", "low", "medium", "high", "critical")

# Etiquetas visibles del tablero. La barra superior las prende y apaga: una tarjeta
# desaparece del Kanban cuando lleva una etiqueta apagada. Las condiciones se evaluan
# en SQL y viven aca, no en el JavaScript (DECISIONS.md D-023).
# Cada condición tiene que ser NULL-safe: con `band IS NULL` (zona gris), un
# `NOT (band = 'P1')` evalua a NULL y SQL descarta la fila, así que apagar una banda
# se llevaba por delante TODA la zona gris. COALESCE evita ese NULL silencioso.
TAGS = (
    ("p0",      "candidato P0",     "COALESCE(c.band,'') LIKE 'candidato P0%'"),
    ("p1",      "P1",               "COALESCE(c.band,'') = 'P1'"),
    ("p2",      "P2",               "COALESCE(c.band,'') = 'P2'"),
    ("p3",      "P3",               "COALESCE(c.band,'') = 'P3'"),
    ("grey",    "zona gris",        "COALESCE(c.band,'') = ''"),
    ("missing", "falta info",       "COALESCE(json_array_length(c.missing_fields),0) > 0"),
    ("review",  "mirada humana",    "COALESCE(c.review_flag,0) = 1"),
)
TAG_KEYS = tuple(t[0] for t in TAGS)
TAG_LABELS = {t[0]: t[1] for t in TAGS}
TAG_CONDITIONS = {t[0]: t[2] for t in TAGS}


def clean_tags(tags):
    """Keeps only known tag keys, order-stable and deduplicated."""
    seen, out = set(), []
    for tag in tags or []:
        if tag in TAG_CONDITIONS and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def _tag_where(hide_tags, alias="c"):
    sql, params = "", []
    for tag in clean_tags(hide_tags):
        sql += f" AND NOT ({TAG_CONDITIONS[tag].replace('c.', alias + '.')})"
    return sql, params


def board_tags(conn, slug):
    """Count of open cards carrying each tag on one board."""
    _ensure_state(conn)
    out = []
    for key, label, cond in TAGS:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM cards c JOIN card_state s ON s.ref = c.ref "
            f"WHERE c.slug = ? AND s.column_name != ? AND ({cond})",
            (slug, ARCHIVE_COLUMN)).fetchone()["c"]
        out.append({"key": key, "label": label, "count": count})
    return out


def missing_severity(missing_count, required_total):
    """Severidad proporcional de la información faltante, de 'none' a 'critical'.

    'unavailable' no es una severidad más alta: es la ausencia de la medición. Se distingue
    de 'none' a propósito, porque 'none' afirma que no falta nada y eso, cuando no se pudieron
    leer los formularios, es una afirmación falsa.
    """
    if missing_count is None or required_total is None:
        return "unavailable"
    if not required_total or missing_count <= 0:
        return "none"
    ratio = missing_count / required_total
    for threshold, label in MISSING_SEVERITY_THRESHOLDS:
        if ratio > threshold or (threshold == 0.0 and ratio > 0):
            return label
    return "low"

DB_PATH = ROOT / "db" / "board.db"

# The HTTP layer is threaded: read-then-write actions must be serialized, otherwise two
# concurrent moves on the same card both observe the same origin column, both append an
# event, and the projection keeps only the last one.
_WRITE_LOCK = threading.Lock()


def serialized(func):
    """Serializes one state-changing operation so the event log and the projection agree."""
    def wrapper(*args, **kwargs):
        with _WRITE_LOCK:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


SNAPSHOT = ROOT / "issues.json"


def _now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def connect(path=None):
    conn = sqlite3.connect(str(path or DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cards (
            ref              TEXT PRIMARY KEY,
            slug             TEXT NOT NULL,
            number           INTEGER NOT NULL,
            title            TEXT NOT NULL,
            state            TEXT,
            labels           TEXT NOT NULL,
            band             TEXT,
            rule             TEXT,
            review_flag      INTEGER NOT NULL DEFAULT 0,
            review_reason    TEXT,
            suggested_column TEXT,
            missing_fields   TEXT NOT NULL DEFAULT '[]',
            required_total   INTEGER NOT NULL DEFAULT 0,
            missing_severity TEXT NOT NULL DEFAULT 'none',
            ingested_at      TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cards_slug ON cards(slug);

        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT NOT NULL,
            ref         TEXT NOT NULL,
            kind        TEXT NOT NULL,
            from_column TEXT,
            to_column   TEXT,
            actor       TEXT NOT NULL,
            note        TEXT,
            payload     TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_events_ref ON events(ref);

        CREATE TABLE IF NOT EXISTS card_state (
            ref         TEXT PRIMARY KEY,
            column_name TEXT NOT NULL,
            since      TEXT NOT NULL,
            updated_by  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS human_labels (
            ref     TEXT PRIMARY KEY,
            verdict TEXT NOT NULL,
            note    TEXT,
            actor   TEXT NOT NULL,
            ts      TEXT NOT NULL
        );
        """
    )
    conn.commit()


def snapshot_meta():
    stat = SNAPSHOT.stat()
    key = (stat.st_mtime_ns, stat.st_size)
    if _SNAPSHOT_META_CACHE.get("key") == key:
        return _SNAPSHOT_META_CACHE["value"]
    data = SNAPSHOT.read_bytes()
    value = {
        "path": SNAPSHOT.name,
        "sha256": hashlib.sha256(data).hexdigest()[:16],
        "issues": len(json.loads(data)),
        "mtime": datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc).replace(microsecond=0).isoformat(),
    }
    _SNAPSHOT_META_CACHE["key"] = key
    _SNAPSHOT_META_CACHE["value"] = value
    return value


def _required_content(slug, kind):
    """Required content fields for one repository's form kind, parsed once."""
    key = (slug, kind)
    if key not in _REQUIRED_CONTENT_CACHE:
        fields = (all_repo_templates().get(slug) or {}).get(kind) or []
        _REQUIRED_CONTENT_CACHE[key] = [f for f in required_fields(fields) if f["type"] != "checkboxes"]
    return _REQUIRED_CONTENT_CACHE[key]


# --------------------------------------------------------------------------- ingest

def _missing_fields(issue):
    """Returns (missing_labels, required_total), or (None, None) when it cannot be known.

    "Cannot be known" is not "nothing is missing". The first means this repository's forms
    were not available to read -- the vendored checkouts are absent -- and the second means
    they were read and ask for nothing. Only the second is a claim about the issue, and
    collapsing them is what let the board report every card as complete without ever
    reading a form.
    """
    kind = kind_of(issue)
    if kind is None:
        return [], 0
    if not _COMPLETENESS_AVAILABLE or not templates_present(issue["slug"]):
        return None, None
    content = _required_content(issue["slug"], kind)
    if not content:
        return [], 0
    body = issue.get("body") or ""
    form_sections = split_sections(body, form_only=True)
    any_sections = split_sections(body, form_only=False)
    missing = []
    for f in content:
        if label_status(body, form_sections, f["label"], any_sections) != "present":
            missing.append(f["label"])
    return missing, len(content)


def derive_card(issue):
    """Derived (recomputed) card projection for one issue."""
    labels = issue.get("labels") or []
    cross_refs = issue.get("cross_refs") or []
    band, cross, rule = classify_issue_deterministically(issue, labels, cross_refs)
    flag, reason = requires_human_review(issue, labels, cross_refs)
    missing, required_total = _missing_fields(issue)
    severity = missing_severity(None if missing is None else len(missing), required_total)

    suggested = None
    if missing:
        suggested = "falta_info"
    elif flag:
        suggested = "revision_humana"

    return {
        "ref": f"{issue['slug']}#{issue['number']}",
        "slug": issue["slug"],
        "number": issue["number"],
        "title": issue.get("title") or "",
        "state": issue.get("state") or "open",
        "labels": labels,
        "band": band,
        "rule": rule,
        "review_flag": 1 if flag else 0,
        "review_reason": reason,
        "suggested_column": suggested,
        "missing_fields": missing or [],
        "required_total": required_total or 0,
        "missing_severity": severity,
    }


def ingest(conn, issues=None):
    """Rebuilds the derived projection. Never touches the event log or human decisions."""
    if issues is None:
        with open(SNAPSHOT, "r", encoding="utf-8") as f:
            issues = json.load(f)
    init_schema(conn)
    now = _now()
    rows = [derive_card(i) for i in issues]
    conn.execute("DELETE FROM cards")
    conn.executemany(
        """INSERT INTO cards (ref, slug, number, title, state, labels, band, rule,
                              review_flag, review_reason, suggested_column, missing_fields,
                              required_total, missing_severity, ingested_at)
           VALUES (:ref, :slug, :number, :title, :state, :labels, :band, :rule,
                   :review_flag, :review_reason, :suggested_column, :missing_fields,
                   :required_total, :missing_severity, :ingested_at)""",
        [{**r, "labels": json.dumps(r["labels"]), "missing_fields": json.dumps(r["missing_fields"]),
          "ingested_at": now} for r in rows],
    )
    meta = snapshot_meta()
    conn.execute("INSERT INTO meta(key, value) VALUES('snapshot', ?) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                 (json.dumps({**meta, "ingested_at": now}),))
    conn.commit()
    return {"cards": len(rows), "meta": meta}


# ----------------------------------------------------------------------- projections

def rebuild_state(conn):
    """
    Recomputes `card_state` and `human_labels` from the append-only event log.

    Cards with no move event fall back to the derived suggestion, and then to `entrada`.
    Returns (cards_rewritten, labels_rewritten).
    """
    moves = {}
    for row in conn.execute("SELECT * FROM events WHERE kind = 'move' ORDER BY id ASC"):
        moves[row["ref"]] = row

    suggestions = {r["ref"]: r["suggested_column"] for r in conn.execute("SELECT ref, suggested_column FROM cards")}

    conn.execute("DELETE FROM card_state")
    for ref, ev in moves.items():
        conn.execute("INSERT INTO card_state(ref, column_name, since, updated_by) VALUES (?,?,?,?)",
                     (ref, ev["to_column"], ev["ts"], ev["actor"]))
    for ref, suggestion in suggestions.items():
        if ref in moves:
            continue
        column = suggestion if suggestion in SUGGESTIBLE_COLUMNS else "entrada"
        conn.execute("INSERT INTO card_state(ref, column_name, since, updated_by) VALUES (?,?,?,?)",
                     (ref, column, _now(), "engine:derived"))

    labels = {}
    for row in conn.execute("SELECT * FROM events WHERE kind = 'verdict' ORDER BY id ASC"):
        labels[row["ref"]] = row
    conn.execute("DELETE FROM human_labels")
    for ref, ev in labels.items():
        payload = json.loads(ev["payload"] or "{}")
        conn.execute("INSERT INTO human_labels(ref, verdict, note, actor, ts) VALUES (?,?,?,?,?)",
                     (ref, payload.get("verdict", "no_valida"), ev["note"], ev["actor"], ev["ts"]))
    conn.commit()
    return len(moves) + (len(suggestions) - len(moves)), len(labels)


def _ensure_state(conn):
    """Builds the projections when the store is new or after an ingest."""
    if conn.execute("SELECT COUNT(*) AS c FROM card_state").fetchone()["c"] == 0:
        rebuild_state(conn)


# ---------------------------------------------------------------------------- actions

@serialized
def move_card(conn, ref, column, actor, note=None):
    """Human action: move one card. Rejects unknown columns and no-op moves."""
    if column not in ALL_COLUMNS:
        raise ValueError(f"unknown column: {column}")
    current = get_card(conn, ref)
    if current is None:
        raise ValueError(f"unknown card: {ref}")
    from_column = current["column_name"]
    if from_column == column:
        raise ValueError(f"card {ref} is already in {column}")
    ts = _now()
    conn.execute(
        "INSERT INTO events(ts, ref, kind, from_column, to_column, actor, note) VALUES (?,?,?,?,?,?,?)",
        (ts, ref, "move", from_column, column, actor, note),
    )
    conn.execute("INSERT INTO card_state(ref, column_name, since, updated_by) VALUES (?,?,?,?) "
                 "ON CONFLICT(ref) DO UPDATE SET column_name=excluded.column_name, since=excluded.since, updated_by=excluded.updated_by",
                 (ref, column, ts, actor))
    conn.commit()
    return {"ref": ref, "from": from_column, "to": column, "ts": ts}


@serialized
def set_verdict(conn, ref, verdict, actor, note=None):
    """Human action: record a human verdict. The tool never writes this by itself."""
    if verdict not in VERDICTS:
        raise ValueError(f"unknown verdict: {verdict}")
    if get_card(conn, ref) is None:
        raise ValueError(f"unknown card: {ref}")
    ts = _now()
    conn.execute(
        "INSERT INTO events(ts, ref, kind, from_column, to_column, actor, note, payload) VALUES (?,?,?,?,?,?,?,?)",
        (ts, ref, "verdict", None, None, actor, note, json.dumps({"verdict": verdict})),
    )
    conn.execute("INSERT INTO human_labels(ref, verdict, note, actor, ts) VALUES (?,?,?,?,?) "
                 "ON CONFLICT(ref) DO UPDATE SET verdict=excluded.verdict, note=excluded.note, actor=excluded.actor, ts=excluded.ts",
                 (ref, verdict, note, actor, ts))
    conn.commit()
    return {"ref": ref, "verdict": verdict, "ts": ts}


# ----------------------------------------------------------------------------- reads

def boards(conn):
    _ensure_state(conn)
    meta = snapshot_meta()
    out = []
    for row in conn.execute("SELECT DISTINCT slug FROM cards ORDER BY slug"):
        out.append({"slug": row["slug"], "total": _board_total(conn, row["slug"]),
                    "columns": _column_counts(conn, row["slug"]),
                    "tags": board_tags(conn, row["slug"]), "snapshot": meta})
    return out


def _board_total(conn, slug):
    return conn.execute(
        "SELECT COUNT(*) AS c FROM cards c JOIN card_state s ON s.ref = c.ref WHERE c.slug = ? AND s.column_name != ?",
        (slug, ARCHIVE_COLUMN)).fetchone()["c"]


def _column_counts(conn, slug):
    counts = {c: 0 for c in ALL_COLUMNS}
    for row in conn.execute(
        "SELECT s.column_name AS col, COUNT(*) AS c FROM cards c JOIN card_state s ON s.ref = c.ref "
        "WHERE c.slug = ? GROUP BY s.column_name", (slug,)):
        counts[row["col"]] = row["c"]
    return [{"key": c, "label": COLUMN_LABELS[c], "count": counts.get(c, 0)} for c in ALL_COLUMNS]


CARD_SELECT = """
    SELECT c.*, s.column_name AS column_name, s.since AS since, s.updated_by AS updated_by,
           h.verdict AS human_verdict, h.note AS human_note, h.ts AS human_ts
    FROM cards c
    JOIN card_state s ON s.ref = c.ref
    LEFT JOIN human_labels h ON h.ref = c.ref
"""


def _row_to_card(row):
    card = dict(row)
    card["labels"] = json.loads(card["labels"] or "[]")
    card["missing_fields"] = json.loads(card["missing_fields"] or "[]")
    card["review_flag"] = bool(card["review_flag"])
    return card


def list_cards(conn, slug, column=None, query=None, limit=60, offset=0, hide_tags=None):
    _ensure_state(conn)
    sql = CARD_SELECT + " WHERE c.slug = ?"
    params = [slug]
    hidden_sql, hidden_params = _tag_where(hide_tags)
    sql += hidden_sql
    params.extend(hidden_params)
    if column:
        if column not in ALL_COLUMNS:
            raise ValueError(f"unknown column: {column}")
        if column != ARCHIVE_COLUMN:
            sql += " AND s.column_name = ?"
            params.append(column)
        else:
            sql += " AND s.column_name = ?"
            params.append(ARCHIVE_COLUMN)
    if query:
        sql += " AND (c.title LIKE ? OR c.ref LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    sql += " ORDER BY CASE WHEN c.band LIKE 'candidato P0%' THEN 0 WHEN c.band = 'P1' THEN 1 ELSE 2 END, c.number DESC"
    sql += " LIMIT ? OFFSET ?"
    params.extend([int(limit), int(offset)])
    return [_row_to_card(r) for r in conn.execute(sql, params)]


def get_card(conn, ref):
    _ensure_state(conn)
    row = conn.execute(CARD_SELECT + " WHERE c.ref = ?", (ref,)).fetchone()
    if row is None:
        return None
    card = _row_to_card(row)
    card["events"] = [dict(r) for r in conn.execute(
        "SELECT ts, kind, from_column, to_column, actor, note, payload FROM events WHERE ref = ? ORDER BY id ASC",
        (ref,))]
    return card


def column_counts(conn, slug, hide_tags=None, include_archive=True):
    """Per-column counts for one board, honouring the active tag filter."""
    _ensure_state(conn)
    hidden_sql, hidden_params = _tag_where(hide_tags)
    counts = {c: 0 for c in ALL_COLUMNS}
    for row in conn.execute(
            "SELECT s.column_name AS col, COUNT(*) AS c FROM cards c "
            "JOIN card_state s ON s.ref = c.ref WHERE c.slug = ?" + hidden_sql +
            " GROUP BY s.column_name", [slug] + hidden_params):
        counts[row["col"]] = row["c"]
    if not include_archive:
        counts.pop(ARCHIVE_COLUMN, None)
    return counts


def human_activity(conn):
    """
    Cuántas decisiones humanas hay registradas.

    Se usan para MOSTRAR y para medir; nunca para recalcular una banda ni una sugerencia.
    El sistema acumula etiquetas humanas, no aprende de ellas. Ver DECISIONS.md D-025.
    """
    _ensure_state(conn)
    row = conn.execute(
        "SELECT (SELECT COUNT(*) FROM events) AS events,"
        "       (SELECT COUNT(*) FROM events WHERE kind='move') AS moves,"
        "       (SELECT COUNT(*) FROM events WHERE kind='verdict') AS verdicts,"
        "       (SELECT COUNT(*) FROM human_labels) AS labels").fetchone()
    return {key: row[key] for key in row.keys()}


def counts_by_slug(conn):
    _ensure_state(conn)
    out = {}
    for row in conn.execute(
            "SELECT c.slug AS slug, s.column_name AS col, COUNT(*) AS c FROM cards c "
            "JOIN card_state s ON s.ref = c.ref GROUP BY c.slug, s.column_name"):
        out.setdefault(row["slug"], {})[row["col"]] = row["c"]
    return out
