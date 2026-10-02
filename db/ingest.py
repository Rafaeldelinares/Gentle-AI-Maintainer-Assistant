#!/usr/bin/env python3
"""
ingest.py — load a judge's raw output into the `votes` table.

Two accepted line formats:

  NEW (preferred, order-independent):
      <repo-slug> | <number> | <band> | <cross> | <reason>
      e.g.  gentle-shell | 1052 | P2 | misplaced | Kimi 400 from pi-ai serialization

  LEGACY (4 fields, mapped by ordinal within the run):
      <number> | <band> | <cross> | <reason>

Why the new format leads with the repo: a bare number is ambiguous across
systems. In this sample `1308` exists in both gentle-ai and gentle-shell, and so
does `1051`. `(system, number)` is the canonical key. Leading with the slug makes
the mapping unambiguous and independent of the order the judge chose to emit.

Usage:
    ./ingest.py --run 1 --judge judge-a --attempt 1 --file /tmp/gas/exp/votes-judge-a-c1-a1.txt
    ./ingest.py --run 1 --judge judge-a --attempt 1 --glob '/tmp/gas/exp/votes-judge-a-c*-a1.txt'
"""
from __future__ import annotations

import argparse
import glob as globmod
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "exp.db"

BANDS = {"P0", "P1", "P2", "P3", "UNKNOWN"}
CROSS = {"none", "dependency", "misplaced", "implication", "UNKNOWN"}
NEW = re.compile(r"^\s*([a-z0-9-]+)\s*\|\s*(\d+)\s*\|\s*([A-Za-z0-9]+)\s*\|\s*([A-Za-z]+)\s*\|\s*(.*)$", re.I)
OLD = re.compile(r"^\s*(\d+)\s*\|\s*([A-Za-z0-9]+)\s*\|\s*([A-Za-z]+)\s*\|\s*(.*)$")


def parse(lines: list[str]):
    out = []
    for ln in lines:
        if not ln.strip() or ln.lstrip().startswith(("#", "```", "EOF")):
            continue
        m = NEW.match(ln)
        if m:
            out.append(("new", m.group(1).lower(), int(m.group(2)),
                        m.group(3).upper(), m.group(4).lower(), m.group(5).strip(), ln.strip()))
            continue
        m = OLD.match(ln)
        if m:
            out.append(("old", None, int(m.group(1)),
                        m.group(2).upper(), m.group(3).lower(), m.group(4).strip(), ln.strip()))
            continue
        out.append(("bad", None, None, None, None, None, ln.strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--file")
    ap.add_argument("--glob")
    ap.add_argument("--chunk", type=int, help="mark this judge_tasks row done after ingesting")
    args = ap.parse_args()

    files = ([Path(args.file)] if args.file else
             [Path(p) for p in sorted(globmod.glob(args.glob or ""))])
    if not files:
        sys.exit("need --file or --glob")

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")

    j = db.execute("SELECT id, model FROM judges WHERE name=?", (args.judge,)).fetchone()
    if not j:
        sys.exit(f"unknown judge '{args.judge}'")
    sys_id = {r["slug"]: r["id"] for r in db.execute("SELECT slug, id FROM systems")}

    # the sample, for ordinal fallback
    sample = db.execute("""
        SELECT i.id, i.number, s.slug FROM run_issues ri
        JOIN issues i ON i.id=ri.issue_id JOIN systems s ON s.id=i.system_id
        WHERE ri.run_id=? ORDER BY ri.ordinal""", (args.run,)).fetchall()
    sample_key = {(r["slug"], r["number"]): r["id"] for r in sample}

    parsed, problems, cursor = [], [], 0
    for f in files:
        rows = parse(f.read_text().splitlines())
        for kind, slug, num, band, cross, reason, raw in rows:
            if kind == "bad":
                problems.append(f"{f.name}: unparsable -> {raw[:60]}")
                continue
            if kind == "old":
                if cursor >= len(sample):
                    problems.append(f"{f.name}: ordinal {cursor} out of range")
                    continue
                iid = sample[cursor]["id"]
                slug = sample[cursor]["slug"]
                cursor += 1
            else:
                iid = sample_key.get((slug, num))
                if iid is None:
                    problems.append(f"{f.name}: {slug}#{num} is not in run {args.run}")
                    continue
            if band not in BANDS:
                problems.append(f"{f.name}: bad band '{band}'")
                continue
            if cross not in CROSS:
                problems.append(f"{f.name}: bad cross '{cross}'")
                continue
            parsed.append((iid, band, cross, reason, raw))

    if problems:
        print("  ✗ refusing to ingest:")
        for p in problems[:12]:
            print(f"      {p}")
        sys.exit(1)

    db.execute("DELETE FROM votes WHERE run_id=? AND judge_id=? AND attempt=?",
               (args.run, j["id"], args.attempt))
    seen = set()
    for iid, band, cross, reason, raw in parsed:
        if iid in seen:
            continue
        seen.add(iid)
        db.execute("""INSERT INTO votes (run_id, judge_id, issue_id, attempt, band, cross, reason, raw_line)
                      VALUES (?,?,?,?,?,?,?,?)""",
                   (args.run, j["id"], iid, args.attempt, band, cross, reason, raw))

    if args.chunk is not None:
        db.execute("""UPDATE judge_tasks SET status='done', finished_at=datetime('now')
                      WHERE run_id=? AND judge_id=? AND attempt=? AND chunk=?""",
                   (args.run, j["id"], args.attempt, args.chunk))

    db.commit()
    print(f"  ✔ {len(seen)} votes · {args.judge} ({j['model']}) · run {args.run} · attempt {args.attempt} · {len(files)} file(s)")

    tal = db.execute("""SELECT band, count(*) n FROM votes
                        WHERE run_id=? AND judge_id=? AND attempt=? GROUP BY band ORDER BY band""",
                     (args.run, j["id"], args.attempt)).fetchall()
    print("      band:  " + "  ".join(f"{r['band']}={r['n']}" for r in tal))
    tcr = db.execute("""SELECT cross, count(*) n FROM votes
                        WHERE run_id=? AND judge_id=? AND attempt=? GROUP BY cross ORDER BY n DESC""",
                     (args.run, j["id"], args.attempt)).fetchall()
    print("      cross: " + "  ".join(f"{r['cross']}={r['n']}" for r in tcr))
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
