#!/usr/bin/env python3
"""
api.py — HTTP surface for the board. Translates HTTP to `core` calls and back.

There is no business logic here: every rule (valid columns, valid verdicts, who may
write what) lives in `core.py`. There is also no outbound network call of any kind —
the board is a read-only projection of GitHub plus a local, append-only decision log.
"""

import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402
import explain as explain_mod  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_ACTOR = os.environ.get("BOARD_ACTOR", "human-1")  # never a person's name

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}

REF_RE = re.compile(r"^[a-z0-9-]+#\d+$")

# An actor is a local label, never an identity and never a person's name.
# Reserved prefixes keep the engine's own writes distinguishable from human ones.
ACTOR_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,31}$")
RESERVED_ACTOR_PREFIXES = ("engine", "system")


def _validated_actor(raw):
    """Returns a safe actor label, or None when the caller sent something reserved or malformed."""
    actor = (raw or DEFAULT_ACTOR).strip().lower()
    if not ACTOR_RE.match(actor) or actor.startswith(RESERVED_ACTOR_PREFIXES):
        return None
    return actor


def _int_param(query, name, default, minimum, maximum):
    """Parses a bounded integer query parameter, rejecting invalid client input with 400."""
    raw = (query.get(name) or [str(default)])[0]
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {name}: {raw!r}")
    return max(minimum, min(value, maximum))


class Handler(BaseHTTPRequestHandler):
    server_version = "GentleBoard/0.1"
    protocol_version = "HTTP/1.1"

    # ------------------------------------------------------------------ helpers
    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not path.exists() or not path.is_file():
            self._json(404, {"error": "not found"})
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > 1_000_000:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def log_message(self, fmt, *args):  # quieter, structured
        sys.stderr.write("[board] %s %s\n" % (self.address_string(), fmt % args))

    # --------------------------------------------------------------------- GET
    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if route in ("/", "/index.html"):
            return self._file(STATIC_DIR / "index.html")
        if route.startswith("/static/"):
            # Serve only regular files that resolve *inside* the static directory.
            # A substring check for '..' is not containment: an absolute remainder
            # (for example "//etc/passwd") makes pathlib return the right-hand path.
            relative = unquote(route[len("/static/"):]).lstrip("/")
            candidate = (STATIC_DIR / relative).resolve()
            if not candidate.is_relative_to(STATIC_DIR.resolve()) or candidate.suffix not in CONTENT_TYPES:
                return self._json(400, {"error": "invalid path"})
            return self._file(candidate)

        conn = core.connect()
        try:
            if route == "/api/health":
                return self._json(200, {"ok": True, "snapshot": core.snapshot_meta(),
                                        "columns": core.COLUMNS, "archive": core.ARCHIVE_COLUMN,
                                        "human_activity": core.human_activity(conn)})

            if route == "/api/boards":
                return self._json(200, {"boards": core.boards(conn), "actor": DEFAULT_ACTOR})

            m = re.match(r"^/api/boards/([a-z0-9-]+)/cards$", route)
            if m:
                slug = m.group(1)
                column = (query.get("column") or [None])[0]
                q = (query.get("q") or [None])[0]
                try:
                    limit = _int_param(query, "limit", 60, 1, 200)
                    offset = _int_param(query, "offset", 0, 0, 1_000_000)
                except ValueError as exc:
                    return self._json(400, {"error": str(exc)})
                hide = core.clean_tags((query.get("hide") or [""])[0].split(","))
                cards = core.list_cards(conn, slug, column=column, query=q, limit=limit,
                                        offset=offset, hide_tags=hide)
                return self._json(200, {"slug": slug, "column": column, "cards": cards,
                                        "counts": core.column_counts(conn, slug, hide_tags=hide),
                                        "tags": core.board_tags(conn, slug),
                                        "hidden_tags": hide})

            if route == "/api/card":
                ref = (query.get("ref") or [""])[0]
                if not REF_RE.match(ref):
                    return self._json(400, {"error": "invalid ref"})
                card = core.get_card(conn, ref)
                if card is None:
                    return self._json(404, {"error": "unknown card"})
                return self._json(200, {"card": card})
        finally:
            conn.close()

        return self._json(404, {"error": "not found"})

    # -------------------------------------------------------------------- POST
    def do_POST(self):
        parsed = urlparse(self.path)
        route = parsed.path
        body = self._read_body()

        if route == "/api/simulate":
            # Solo calcula: no crea eventos, no toca tarjetas, no escribe nada.
            title = (body.get("title") or "").strip()
            if not title:
                return self._json(400, {"error": "title is required"})
            slug = body.get("slug") or "gentle-ai"
            if slug not in ("gentle-ai", "engram", "gentle-shell"):
                return self._json(400, {"error": "unknown slug"})
            labels = [l.strip() for l in (body.get("labels") or "").split(",") if l.strip()]
            return self._json(200, {"explanation": explain_mod.explain(
                title, body.get("body") or "", body.get("title_prefix") or "", labels, slug)})

        if route not in ("/api/move", "/api/verdict", "/api/ingest"):
            return self._json(404, {"error": "not found"})

        ref = body.get("ref", "")
        note = (body.get("note") or "").strip() or None
        actor = _validated_actor(body.get("actor"))
        if actor is None:
            return self._json(400, {"error": "invalid actor: reserved or malformed"})

        if route in ("/api/move", "/api/verdict") and not REF_RE.match(ref):
            return self._json(400, {"error": "invalid ref"})

        conn = core.connect()
        try:
            if route == "/api/move":
                column = body.get("column", "")
                try:
                    result = core.move_card(conn, ref, column, actor, note)
                except ValueError as exc:
                    return self._json(400, {"error": str(exc)})
                return self._json(200, {"moved": result,
                                        "counts": core.column_counts(conn, ref.split("#")[0])})

            if route == "/api/verdict":
                verdict = body.get("verdict", "")
                try:
                    result = core.set_verdict(conn, ref, verdict, actor, note)
                except ValueError as exc:
                    return self._json(400, {"error": str(exc)})
                return self._json(200, {"verdict": result})

            if route == "/api/ingest":
                stats = core.ingest(conn)
                return self._json(200, {"ingested": stats})
        finally:
            conn.close()


def build_server(host="127.0.0.1", port=8770):
    return ThreadingHTTPServer((host, port), Handler)
