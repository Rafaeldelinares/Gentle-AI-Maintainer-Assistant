#!/usr/bin/env python3
"""
determinism_check.py — Verifies that everything *derived* is byte-identical across processes.

Covers three things that must be reproducible:
  1. the four module reports (files on disk);
  2. the board's derived projection (bands, rules, suggested columns, missing-info severity,
     tag counts and column counts), computed by ingesting the snapshot into a temporary
     database;
  3. the engine's structured decision contract (`decide(..., include_evidence=True)` covering
     band, rule, cross, review flag/reason, decided_by, rules_considered, and rich evidence)
     for the first 400 issues.

What is deliberately NOT checked here: the human decisions (card column, verdict). Those
must not be deterministic; what is verified about them is that they are reconstructible
from the append-only log, and that is tools/board_rebuild_check.py.


Python randomizes string hashing per process (PYTHONHASHSEED), so any module that iterates
a `set` of strings to build an ordered report can produce a different file each run. That
would make the published reports unreproducible.

This checker runs each module twice under different hash seeds and fails if a report changes.

  python3 tools/determinism_check.py

Exit code 0 = all reports byte-identical. Exit code 1 = a report is non-deterministic.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULES = [
    ("Module A — completeness", ROOT / "modules" / "completeness.py", ROOT / "report-completeness.md"),
    ("Module B — duplicates", ROOT / "modules" / "duplicates.py", ROOT / "report-duplicates.md"),
    ("Module C — cross-repo links", ROOT / "modules" / "cross_repo.py", ROOT / "report-cross-links.md"),
    ("Module D — possibly obsolete", ROOT / "modules" / "obsolete.py", ROOT / "report-obsolete.md"),
]

SEEDS = ["1", "7"]

BOARD_PROJECTION_SNIPPET = """
import hashlib, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(%r) / "board"))
import core
tmp = Path(tempfile.mkdtemp()) / "board-determinism.db"
conn = core.connect(tmp)
core.init_schema(conn)
with open(Path(%r) / "issues.json", encoding="utf-8") as fh:
    core.ingest(conn, json.load(fh))
core.rebuild_state(conn)
h = hashlib.sha256()
for row in conn.execute(
        "SELECT ref, band, rule, suggested_column, required_total, missing_severity, review_flag "
        "FROM cards ORDER BY ref"):
    h.update(("|".join(str(v) for v in row)).encode())
for slug in ("engram", "gentle-ai", "gentle-shell"):
    for tag in core.board_tags(conn, slug):
        h.update(f"{slug}:tag:{tag['key']}={tag['count']}".encode())
    for key, value in sorted(core.column_counts(conn, slug).items()):
        h.update(f"{slug}:col:{key}={value}".encode())
conn.close()
sys.stdout.write(h.hexdigest())
"""

ENGINE_DECISION_SNIPPET = """
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(%r) / "db"))
import rules
with open(Path(%r) / "issues.json", encoding="utf-8") as fh:
    issues = json.load(fh)
h = hashlib.sha256()
for row in issues[:400]:
    labels = row.get("labels") or []
    cross_refs = row.get("cross_refs") or []
    decision = rules.decide(row, labels, cross_refs, include_evidence=True)
    serialized = json.dumps(decision, sort_keys=True, ensure_ascii=False)
    h.update(serialized.encode("utf-8"))
sys.stdout.write(h.hexdigest())
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_once(module, report, seed):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run([sys.executable, str(module)], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"{module.name} failed with PYTHONHASHSEED={seed}")
    return digest(report)


def board_projection_digest(seed):
    """Digest of everything the board derives from the snapshot (no human decisions)."""
    env = dict(os.environ, PYTHONHASHSEED=seed)
    code = BOARD_PROJECTION_SNIPPET % (str(ROOT), str(ROOT))
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"board projection failed with PYTHONHASHSEED={seed}")
    return result.stdout.strip()


def engine_decision_digest(seed):
    """Digest of the engine structured decision contract (decide() with evidence for first 400 issues)."""
    timeout_seconds = 600  # this gate must never hang; the snippet itself runs in about 4 s
    env = dict(os.environ, PYTHONHASHSEED=seed)
    code = ENGINE_DECISION_SNIPPET % (str(ROOT), str(ROOT))
    try:
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                env=env, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        raise SystemExit(f"engine decision check timed out after {timeout_seconds}s "
                         f"with PYTHONHASHSEED={seed}")
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"engine decision check failed with PYTHONHASHSEED={seed}")
    return result.stdout.strip()


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" DERIVED-OUTPUT DETERMINISM CHECK (two processes, two hash seeds)")
    print("════════════════════════════════════════════════════════════════════")
    failures = []
    for name, module, report in MODULES:
        if not module.exists():
            print(f"  ❌ missing module: {module}")
            failures.append(name)
            continue
        digests = {seed: run_once(module, report, seed) for seed in SEEDS}
        unique = set(digests.values())
        if len(unique) == 1:
            print(f"  ✔ {name}: {list(unique)[0][:16]}…")
        else:
            print(f"  ❌ {name}: report differs across seeds")
            for seed, d in digests.items():
                print(f"       seed {seed}: {d[:16]}…")
            failures.append(name)

    # The board's derived projection: bands, rules, suggested columns, severity, tag counts.
    board_digests = {seed: board_projection_digest(seed) for seed in SEEDS}
    if len(set(board_digests.values())) == 1:
        print(f"  ✔ board derived projection: {list(board_digests.values())[0][:16]}…")
    else:
        print("  ❌ board derived projection differs across seeds")
        for seed, digest in board_digests.items():
            print(f"       seed {seed}: {digest[:16]}…")
        failures.append("board derived projection")

    # The engine's structured decision contract: band, rule, cross, review, decided_by, trace, evidence.
    engine_digests = {seed: engine_decision_digest(seed) for seed in SEEDS}
    if len(set(engine_digests.values())) == 1:
        print(f"  ✔ engine decision contract: {list(engine_digests.values())[0][:16]}…")
    else:
        print("  ❌ engine decision contract differs across seeds")
        for seed, digest in engine_digests.items():
            print(f"       seed {seed}: {digest[:16]}…")
        failures.append("engine decision contract")

    print("────────────────────────────────────────────────────────────────────")
    if failures:
        print(f" NON-DETERMINISTIC REPORTS: {len(failures)} — {', '.join(failures)}")
        print("════════════════════════════════════════════════════════════════════")
        return 1
    print(" ALL DERIVED OUTPUT IS BYTE-IDENTICAL ACROSS PROCESSES")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
