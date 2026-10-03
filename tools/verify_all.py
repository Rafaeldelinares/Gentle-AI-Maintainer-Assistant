#!/usr/bin/env python3
"""
verify_all.py — One gate for every invariant and test in the project.

    python3 tools/verify_all.py           # fast gate (~10s)
    python3 tools/verify_all.py --full    # adds report regeneration + determinism (~4min)

Nothing that matters should be checked by memory. If a rule can be broken silently, it
belongs in this list.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FAST_CHECKS = [
    ("rule test suite", [sys.executable, "test_rules.py"]),
    ("board domain tests", [sys.executable, "test_board.py"]),
    ("read-only invariant", [sys.executable, "tools/readonly_check.py"]),
    ("privacy invariant", [sys.executable, "tools/privacy_check.py"]),
    ("board log reconstructibility", [sys.executable, "tools/board_rebuild_check.py"]),
    ("figure recomputation", [sys.executable, "tools/metrics.py"]),
    ("published figures match the documents", [sys.executable, "tools/figures_check.py"]),
    ("figures check unit tests", [sys.executable, "test_figures_check.py"]),
    ("precision report runs (0 labels -> not available)", [sys.executable, "tools/precision_report.py"]),
]

FULL_CHECKS = [
    ("module reports regenerate", [sys.executable, "tools/run_reports.py"]),
    ("report determinism", [sys.executable, "tools/determinism_check.py"]),
]


def run(label, cmd):
    print(f"\n── {label} ──")
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    tail = [l for l in result.stdout.strip().splitlines() if l.strip()][-3:]
    for line in tail:
        print("   " + line)
    if result.returncode != 0:
        print(f"   ❌ {label} FAILED (exit {result.returncode})")
        for line in result.stderr.strip().splitlines()[-12:]:
            print("   " + line)
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="also regenerate reports and check determinism")
    args = parser.parse_args()

    print("════════════════════════════════════════════════════════════════════")
    print(" VERIFY ALL" + (" (full)" if args.full else ""))
    print("════════════════════════════════════════════════════════════════════")

    checks = list(FAST_CHECKS)
    if args.full:
        checks += FULL_CHECKS

    results = []
    for label, cmd in checks:
        results.append((label, run(label, cmd)))

    # The board suite and the module reports read the issue forms from products/,
    # which is deliberately outside git. Say so where it fails, so the failure is
    # legible instead of a cryptic test error.
    if not (ROOT / "products").exists():
        print("\n── prerequisite ──")
        print("   ⚠ products/ is missing: the board suite and the module reports read")
        print("     the issue templates from it. Run ./sync-products.sh, then retry.")

    # Contract tests need jsonschema, which lives in .venv.
    venv = ROOT / ".venv" / "bin" / "python"
    if venv.exists():
        results.append(("data contracts", run("data contracts", [str(venv), "schemas/validate.py"])))
    else:
        print("\n── data contracts ──\n   ⚠ .venv not found; run: python3 -m venv .venv && .venv/bin/pip install jsonschema")

    failed = [label for label, ok in results if not ok]
    print("\n════════════════════════════════════════════════════════════════════")
    print(f" {len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        print(" FAILED: " + ", ".join(failed))
        print("════════════════════════════════════════════════════════════════════")
        return 1
    print(" ALL CHECKS PASSED")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
