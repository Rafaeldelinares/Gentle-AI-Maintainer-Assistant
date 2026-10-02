#!/usr/bin/env python3
"""
sample.py — export a reproducible, stratified sample of issues as chunk files,
and record it as a run in the database.

The sample is deterministic: issues are ordered by a hash of (system, number),
then sliced proportionally to each system's open backlog. Re-running with the
same --n produces the same sample, and its hash is stored on the run row.

Usage:
    ./sample.py                    # 90 issues, 3 chunks, written to /tmp/gas/exp
    ./sample.py --n 180 --chunks 6
    ./sample.py --run 3            # re-export an existing run instead of creating one
    ./sample.py --list             # show existing runs
"""
from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "exp.db"
OUT_DIR = Path("/tmp/gas/exp")
LIMIT_BODY = 4000
RUBRIC_VERSION = "triage/v1"


def c(t: str, col: str) -> str:
    return f"\033[1;{col}m{t}\033[0m"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=90)
    ap.add_argument("--chunks", type=int, default=3)
    ap.add_argument("--run", type=int, help="re-export an existing run id")
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--tasks", action="store_true", help="create judge_tasks rows for the chunk set")
    ap.add_argument("--label", default=None)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")

    if args.list:
        for r in db.execute("""SELECT r.id, r.label, r.sample_size, r.started_at,
                                      count(ri.issue_id) AS exported
                               FROM runs r LEFT JOIN run_issues ri ON ri.run_id = r.id
                               GROUP BY r.id ORDER BY r.id"""):
            print(f"  #{r['id']}  {r['label']:28s} n={r['sample_size']:<4d} {r['started_at']}")
        return 0

    # ── existing run ────────────────────────────────────────────────────────
    if args.run:
        run_id = args.run
        rows = db.execute("""
            SELECT i.id, i.number, i.title, i.body, s.slug,
                   (SELECT group_concat(l.name, ', ')
                    FROM issue_labels il JOIN labels l ON l.id = il.label_id
                    WHERE il.issue_id = i.id) AS labels
            FROM run_issues ri
            JOIN issues i ON i.id = ri.issue_id
            JOIN systems s ON s.id = i.system_id
            WHERE ri.run_id = ?
            ORDER BY ri.ordinal""", (run_id,)).fetchall()
        if not rows:
            sys.exit(f"run {run_id} has no issues")
        print(f"  re-exporting run #{run_id} ({len(rows)} issues)")

    # ── new run: proportional stratified sample ─────────────────────────────
    else:
        backlog = db.execute("""
            SELECT s.id, s.slug, count(*) AS n
            FROM issues i JOIN systems s ON s.id = i.system_id
            WHERE i.state = 'open'
            GROUP BY s.id, s.slug ORDER BY s.slug""").fetchall()
        total_open = sum(b["n"] for b in backlog)

        picked: list[int] = []
        for b in backlog:
            k = max(1, round(args.n * b["n"] / total_open))
            ids = [r[0] for r in db.execute("""
                SELECT id FROM issues
                WHERE system_id = ? AND state = 'open'
                ORDER BY (number * 40503) % 10009
                LIMIT ?""", (b["id"], k))]
            picked.extend(ids)
            print(f"    {b['slug']:14s} {k:3d} of {b['n']}")

        picked.sort()
        sample_hash = hashlib.sha256(",".join(map(str, picked)).encode()).hexdigest()[:16]
        label = args.label or f"n{args.n}-{sample_hash[:8]}"
        cur = db.execute("""INSERT INTO runs (label, rubric_version, sample_hash, sample_size)
                            VALUES (?,?,?,?)""",
                         (label, RUBRIC_VERSION, sample_hash, len(picked)))
        run_id = cur.lastrowid
        for ordinal, iid in enumerate(picked):
            db.execute("INSERT INTO run_issues (run_id, issue_id, ordinal) VALUES (?,?,?)",
                       (run_id, iid, ordinal))
        db.commit()
        print(f"\n  {c('✔', '32')} run #{run_id} '{label}' hash={sample_hash} n={len(picked)}")

        rows = db.execute("""
            SELECT i.id, i.number, i.title, i.body, s.slug,
                   (SELECT group_concat(l.name, ', ')
                    FROM issue_labels il JOIN labels l ON l.id = il.label_id
                    WHERE il.issue_id = i.id) AS labels
            FROM run_issues ri
            JOIN issues i ON i.id = ri.issue_id
            JOIN systems s ON s.id = i.system_id
            WHERE ri.run_id = ?
            ORDER BY ri.ordinal""", (run_id,)).fetchall()

    # ── write chunks ────────────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("chunk-*.txt"):
        old.unlink()

    per = -(-len(rows) // args.chunks)          # ceil
    written = 0
    for ci in range(args.chunks):
        block = rows[ci * per:(ci + 1) * per]
        if not block:
            continue
        parts = []
        for r in block:
            body = (r["body"] or "")[:LIMIT_BODY]
            parts.append(
                f"───────── #{r['number']}  [{r['slug']}]\n"
                f"TITLE: {r['title']}\n"
                f"LABELS: {r['labels'] or '(none)'}\n"
                f"BODY:\n{body}\n"
            )
            written += 1
        (OUT_DIR / f"chunk-{ci + 1}.txt").write_text("\n".join(parts))

    files = sorted(OUT_DIR.glob("chunk-*.txt"))
    total_bytes = sum(f.stat().st_size for f in files)
    print(f"\n  {c('✔', '32')} {written} issues → {len(files)} chunks · {total_bytes/1024:.0f} KB in {OUT_DIR}")
    for f in files:
        print(f"      {f.name}  {f.stat().st_size/1024:6.1f} KB")

    if args.tasks:
        for jn in ("judge-a", "judge-b"):
            jid = db.execute("SELECT id FROM judges WHERE name=?", (jn,)).fetchone()["id"]
            for ci in range(1, len(files) + 1):
                db.execute("""INSERT OR IGNORE INTO judge_tasks
                                (run_id, judge_id, attempt, chunk, status, file)
                                VALUES (?,?,?,?, 'pending', ?)""",
                           (run_id, jid, args.attempt, ci,
                            str(OUT_DIR / f"votes-{jn}-c{ci}-a{args.attempt}.txt")))
        db.commit()
        print(f"\n  {c('✔', '32')} judge_tasks seeded:")
        for r in db.execute("""SELECT j.name, t.chunk, t.status
                               FROM judge_tasks t JOIN judges j ON j.id=t.judge_id
                               WHERE t.run_id=? AND t.attempt=?
                               ORDER BY j.name, t.chunk""", (run_id, args.attempt)):
            print(f"      {r['name']:9s} chunk {r['chunk']}  {r['status']}")

    print(f"\n  run_id = {run_id}   (use it to ingest votes)")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
