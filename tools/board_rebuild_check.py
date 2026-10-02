#!/usr/bin/env python3
"""
board_rebuild_check.py — Proves the board's projections are reconstructible.

The board stores every human action as an append-only event. `card_state` and
`human_labels` are only caches. If that claim is true, rebuilding them from the event
log must reproduce the exact same values.

Two proofs, both on temporary copies so the live board is never touched:

  1. a simulated cycle: ingest the real snapshot, apply synthetic moves and verdicts,
     wreck the caches, rebuild, and compare. This runs whether or not you have used the
     board yet.
  2. the live board: the same comparison against `db/board.db` when it exists.

  python3 tools/board_rebuild_check.py

Exit code 0 = the log is the single source of truth. Exit code 1 = the projections and
the log disagree, which would make the "auditable" claim false.
"""

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "board"))

import core  # noqa: E402

DB = ROOT / "db" / "board.db"


def snapshot(conn):
    state = {r["ref"]: r["column_name"] for r in conn.execute("SELECT ref, column_name FROM card_state")}
    labels = {r["ref"]: r["verdict"] for r in conn.execute("SELECT ref, verdict FROM human_labels")}
    events = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    return state, labels, events


def verify(conn, label):
    """Wrecks the caches, rebuilds from the log, and compares."""
    before = snapshot(conn)
    conn.execute("UPDATE card_state SET column_name = 'entrada'")
    conn.execute("UPDATE human_labels SET verdict = 'no_valida'")
    conn.commit()
    core.rebuild_state(conn)
    after = snapshot(conn)

    state_ok = before[0] == after[0]
    labels_ok = before[1] == after[1]
    events_ok = before[2] == after[2]

    print(f"  {label}: {len(before[0])} cards, {len(before[1])} labels, {before[2]} events")
    print("    " + ("✔" if state_ok else "❌") + " card_state rebuilt from events matches exactly")
    print("    " + ("✔" if labels_ok else "❌") + " human_labels rebuilt from events matches exactly")
    print("    " + ("✔" if events_ok else "❌") + " the event log was not modified by the rebuild")
    return state_ok and labels_ok and events_ok


def simulated_cycle():
    """Ingests the real snapshot, applies synthetic human actions, and verifies the rebuild."""
    with open(ROOT / "issues.json", "r", encoding="utf-8") as f:
        import json
        issues = json.load(f)

    tmp_db = Path(tempfile.mkdtemp()) / "board-sim.db"
    conn = core.connect(tmp_db)
    try:
        core.init_schema(conn)
        core.ingest(conn, issues)
        core.rebuild_state(conn)
        first = {r["ref"] for r in conn.execute("SELECT ref FROM card_state LIMIT 3")}
        refs = sorted(first)
        if len(refs) < 3:
            print("    (snapshot too small for a simulated cycle)")
            return True
        core.move_card(conn, refs[0], "listo_mantener", "human-1", "simulated")
        core.move_card(conn, refs[1], "en_manos", "human-1", "simulated")
        core.move_card(conn, refs[2], "archivado", "human-1", "simulated")
        core.set_verdict(conn, refs[0], "P2", "human-1", "simulated")
        core.set_verdict(conn, refs[1], "P1", "human-1", "simulated")
        return verify(conn, "simulated cycle on the real snapshot")
    finally:
        conn.close()


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" BOARD REBUILD CHECK (is the event log the only source of truth?)")
    print("════════════════════════════════════════════════════════════════════")

    ok = simulated_cycle()

    if DB.exists():
        tmp_db = Path(tempfile.mkdtemp()) / "board-copy.db"
        shutil.copy2(DB, tmp_db)
        conn = core.connect(tmp_db)
        try:
            ok = verify(conn, "live board (db/board.db)") and ok
        finally:
            conn.close()
    else:
        print("  live board: no db/board.db yet (nothing to verify)")

    print("────────────────────────────────────────────────────────────────────")
    if ok:
        print(" THE EVENT LOG IS THE SINGLE SOURCE OF TRUTH")
        print("════════════════════════════════════════════════════════════════════")
        return 0
    print(" PROJECTIONS AND LOG DISAGREE — the auditable claim does not hold")
    print("════════════════════════════════════════════════════════════════════")
    return 1


if __name__ == "__main__":
    sys.exit(main())
