#!/usr/bin/env python3
"""
determinism_check.py — Verifies that every module report is byte-identical across processes.

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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_once(module, report, seed):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run([sys.executable, str(module)], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"{module.name} failed with PYTHONHASHSEED={seed}")
    return digest(report)


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" REPORT DETERMINISM CHECK (two processes, two hash seeds)")
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

    print("────────────────────────────────────────────────────────────────────")
    if failures:
        print(f" NON-DETERMINISTIC REPORTS: {len(failures)} — {', '.join(failures)}")
        print("════════════════════════════════════════════════════════════════════")
        return 1
    print(" ALL REPORTS BYTE-IDENTICAL ACROSS PROCESSES")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
