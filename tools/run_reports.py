#!/usr/bin/env python3
"""
run_reports.py — Regenerates every module report from the frozen snapshot.

  python3 tools/run_reports.py

Runs Module A (completeness), Module B (duplicates) and Module C (cross-repository
references). Each module is read-only and writes one root Markdown report.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    ("Module A — completeness", ROOT / "modules" / "completeness.py"),
    ("Module B — duplicates", ROOT / "modules" / "duplicates.py"),
    ("Module C — cross-repo links", ROOT / "modules" / "cross_repo.py"),
]


def main():
    failed = 0
    for name, path in MODULES:
        print(f"── {name} ──")
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            failed += 1
            sys.stderr.write(result.stderr)
        print()
    if failed:
        print(f"{failed} module(s) failed")
        return 1
    print("all module reports regenerated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
