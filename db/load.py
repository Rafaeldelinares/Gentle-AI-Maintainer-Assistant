#!/usr/bin/env python3
"""
load.py — pull the three systems' issues from GitHub into the SQLite store.

Source of truth for acquisition is the HOST's authenticated `gh`.
The database is a single file: no server, no container, no volume.

Usage:
    ./load.py                     # fetch fresh, all three systems, all states
    ./load.py --state open        # open issues only
    ./load.py --cached            # reuse /tmp/gas/*-full.json, no network
    ./load.py --no-comments       # skip comment fetching
    ./load.py --reset             # delete the .db file first
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "exp.db"
SCHEMA = HERE / "schema.sql"
CACHE_DIR = Path("/tmp/gas")

# slug, full_name, language
SYSTEMS = [
    ("gentle-ai",    "Gentleman-Programming/gentle-ai",    "Go"),
    ("engram",       "Gentleman-Programming/engram",       "Go"),
    ("gentle-shell", "Gentleman-Programming/gentle-shell", "TypeScript"),
]

# Only these repos count as a cross-system reference. Everything else that
# merely *looks* like a name (extensions/gentle-ai.ts, gentle-ai-* skills,
# .git/gentle-ai/) is deliberately NOT matched.
XREF = re.compile(r"Gentleman-Programming/([A-Za-z0-9_.-]+)#(\d+)", re.I)
TITLE_PREFIX = re.compile(r"^([A-Za-z]+)\s*(?:\(([^)]*)\))?:")

JSON_FIELDS = "number,title,body,state,author,createdAt,updatedAt,closedAt,labels,comments"


def c(txt: str, colour: str) -> str:
    return f"\033[1;{colour}m{txt}\033[0m"


def step(msg: str) -> None:
    print(f"\n{c('▸', '36')} {msg}")


def ok(msg: str) -> None:
    print(f"  {c('✔', '32')} {msg}")


def gh_json(args: list[str]) -> object:
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def fetch_repo(full: str, state: str, limit: int) -> list[dict]:
    return gh_json([
        "issue", "list", "-R", full,
        "--state", state, "--limit", str(limit),
        "--json", JSON_FIELDS,
    ])


def cached_repo(slug: str) -> list[dict]:
    f = CACHE_DIR / f"{slug}-full.json"
    if not f.exists():
        sys.exit(f"no cache at {f} — run without --cached first")
    return json.loads(f.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="all", choices=["open", "closed", "all"])
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--cached", action="store_true")
    ap.add_argument("--no-comments", action="store_true")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()

    if args.reset:
        for suffix in ("", "-wal", "-shm"):
            Path(str(DB_PATH) + suffix).unlink(missing_ok=True)
        step("reset: removed the database file")

    step("opening database")
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA.read_text())
    db.execute("PRAGMA foreign_keys = ON")
    ok(f"{DB_PATH}  ({DB_PATH.stat().st_size} bytes, schema applied)")

    # ── systems ─────────────────────────────────────────────────────────────
    step("systems")
    for slug, full, lang in SYSTEMS:
        info = gh_json(["api", f"repos/{full}"])
        repo_id, branch = info["id"], info["default_branch"]
        db.execute("""
            INSERT INTO systems (slug, full_name, language, default_branch, repo_id)
            VALUES (?,?,?,?,?)
            ON CONFLICT (slug) DO UPDATE SET
              full_name = excluded.full_name, repo_id = excluded.repo_id,
              default_branch = excluded.default_branch
        """, (slug, full, lang, branch, int(repo_id)))
        print(f"    {slug:14s} {full}")

    # ── labels ──────────────────────────────────────────────────────────────
    step("labels")
    total_labels = 0
    for slug, full, _lang in SYSTEMS:
        rows = gh_json(["label", "list", "-R", full, "--limit", "200",
                        "--json", "name,color,description"])
        sid = db.execute("SELECT id FROM systems WHERE slug=?", (slug,)).fetchone()[0]
        for r in rows:
            db.execute("""
                INSERT INTO labels (system_id, name, color, description)
                VALUES (?,?,?,?)
                ON CONFLICT (system_id, name) DO UPDATE SET
                  color = excluded.color, description = excluded.description
            """, (sid, r["name"], r.get("color") or "", (r.get("description") or "")))
        total_labels += len(rows)
    ok(f"{total_labels} labels")

    # ── issues ──────────────────────────────────────────────────────────────
    for slug, full, _lang in SYSTEMS:
        step(f"issues: {slug}  (state={args.state} limit={args.limit})")
        data = cached_repo(slug) if args.cached else fetch_repo(full, args.state, args.limit)
        sid = db.execute("SELECT id FROM systems WHERE slug=?", (slug,)).fetchone()[0]

        for it in data:
            state = (it.get("state") or "open").lower()
            db.execute("""
                INSERT INTO issues (system_id, number, title, body, state, author,
                                    created_at, updated_at, closed_at, comments_count)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT (system_id, number) DO UPDATE SET
                  title = excluded.title, body = excluded.body, state = excluded.state,
                  closed_at = excluded.closed_at, comments_count = excluded.comments_count,
                  fetched_at = datetime('now')
            """, (
                sid, it["number"], it.get("title") or "", it.get("body") or "",
                state, (it.get("author") or {}).get("login"),
                it.get("createdAt") or datetime.now(timezone.utc).isoformat(),
                it.get("updatedAt"), it.get("closedAt"),
                len(it.get("comments") or []),
            ))
            iid = db.execute("SELECT id FROM issues WHERE system_id=? AND number=?",
                             (sid, it["number"])).fetchone()[0]

            for lb in (it.get("labels") or []):
                db.execute("""
                    INSERT INTO issue_labels (issue_id, label_id)
                    SELECT ?, id FROM labels WHERE system_id=? AND name=?
                    ON CONFLICT DO NOTHING
                """, (iid, sid, lb["name"]))

            if not args.no_comments:
                for cm in (it.get("comments") or []):
                    if not cm.get("id"):
                        continue
                    db.execute("""
                        INSERT INTO comments (issue_id, gh_id, author, body, created_at)
                        VALUES (?,?,?,?,?)
                        ON CONFLICT (gh_id) DO NOTHING
                    """, (iid, cm["id"], (cm.get("author") or {}).get("login"),
                          cm.get("body") or "", cm.get("createdAt")))

        db.commit()
        n = db.execute("SELECT count(*) FROM issues WHERE system_id=?", (sid,)).fetchone()[0]
        lk = db.execute("""SELECT count(*) FROM issue_labels il
                           JOIN issues i ON i.id=il.issue_id WHERE i.system_id=?""", (sid,)).fetchone()[0]
        cm = db.execute("""SELECT count(*) FROM comments c
                           JOIN issues i ON i.id=c.issue_id WHERE i.system_id=?""", (sid,)).fetchone()[0]
        ok(f"{len(data)} fetched · {n} in db · {lk} label links · {cm} comments")

    # ── derived columns + cross references ──────────────────────────────────
    # SQLite has no built-in regexp, so this lives here rather than in a
    # SQL function. Still deterministic, still re-runnable: no refetch.
    step("derived columns and cross_refs")
    slug_by_repo = {full.split("/")[1]: slug for slug, full, _ in SYSTEMS}
    sys_id = {s: i for s, i in db.execute("SELECT slug, id FROM systems").fetchall()}

    db.execute("DELETE FROM cross_refs")
    issues = db.execute("SELECT id, system_id, title, body FROM issues").fetchall()
    prefixes = 0
    refs = 0
    for iid, sid_sys, title, body in issues:
        m = TITLE_PREFIX.match(title or "")
        prefix = m.group(1) if m else None
        scope = (m.group(2) if m and m.group(2) else None)
        if prefix:
            prefixes += 1
        db.execute("UPDATE issues SET title_prefix=?, title_scope=? WHERE id=?",
                   (prefix, scope, iid))

        for loc, text in (("title", title or ""), ("body", body or "")):
            for repo, num in XREF.findall(text):
                target = slug_by_repo.get(repo)
                if target is None:
                    continue          # a name that merely looks like a repo
                db.execute("""
                    INSERT OR IGNORE INTO cross_refs
                      (issue_id, target_system_id, target_number, location, raw)
                    VALUES (?,?,?,?,?)
                """, (iid, sys_id[target], int(num), loc,
                      f"Gentleman-Programming/{repo}#{num}"))
                if sys_id[target] != sid_sys:
                    refs += 1
    db.commit()
    ok(f"{prefixes} titles with a conventional-commit prefix")
    ok(f"{refs} qualified cross-system references")

    # ── summary ─────────────────────────────────────────────────────────────
    step("summary")
    print(f"    {'slug':14s} {'issues':>7s} {'open':>7s} {'text':>10s}")
    for slug, n, o, b in db.execute("""
            SELECT s.slug, count(*), sum(i.state='open'), sum(i.body_bytes)
            FROM issues i JOIN systems s ON s.id=i.system_id
            GROUP BY s.slug ORDER BY s.slug"""):
        print(f"    {slug:14s} {n:7d} {o:7d} {b/1024:9.0f}K")
    print()
    print("    v_triage_debt:")
    for row in db.execute("SELECT slug, open_total, untriaged, untriaged_pct FROM v_triage_debt"):
        print(f"      {row[0]:14s} {row[2]:4d}/{row[1]:<4d}  {row[3]}%")
    xr = db.execute("SELECT count(*) FROM v_cross_system").fetchone()[0]
    print(f"\n    cross-system issues (qualified refs): {xr}")

    db.close()
    print(f"\n{c('✔', '32')} done — query it with:  sqlite3 -header -column {DB_PATH} 'SELECT * FROM v_triage_debt'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
