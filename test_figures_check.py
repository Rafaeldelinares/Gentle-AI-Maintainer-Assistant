#!/usr/bin/env python3
"""
test_figures_check.py — Unit tests for the claim parser and the counting arithmetic.

Why this file exists: the guard that checks published figures shipped with 269 lines and no
tests of its own, while the rules and the board have 129 and 79. A check nobody tests is a
check nobody can trust. These tests cover only the pure logic, so they need no subprocess and
no filesystem and run in milliseconds.

Usage:
  python3 test_figures_check.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "tools"))
from figures_check import claims_on_line, gate_totals_from, parse_ratio  # noqa: E402


def run_tests():
    print("════════════════════════════════════════════════════════════════════")
    print(" RUNNING FIGURES CHECK UNIT SUITE (test_figures_check.py)")
    print("════════════════════════════════════════════════════════════════════\n")

    passed = 0
    total = 0

    def check(condition, desc):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  ✔ [PASS] {desc}")
            passed += 1
        else:
            print(f"  ❌ [FAIL] {desc}", file=sys.stderr)
            sys.exit(1)

    def claims(line):
        return [(subject, n, m) for subject, _at, n, m in claims_on_line(line)]

    # ── reading the real total out of a suite banner
    check(parse_ratio(" FINAL TEST RESULT: 129/129 tests passed successfully.", "FINAL TEST RESULT:") == 129,
          "parse_ratio reads the total from a suite banner")
    check(parse_ratio(" FINAL TEST RESULT: 125/129 tests passed.", "FINAL TEST RESULT:") is None,
          "parse_ratio refuses an unmatched pair")
    check(parse_ratio("nothing to see here", "FINAL TEST RESULT:") is None,
          "parse_ratio returns None when the marker is absent")
    check(parse_ratio("FINAL RESULT: 12/12 tests passed successfully.", "FINAL RESULT:") == 12,
          "parse_ratio reads the contract validator's banner too")

    # ── the claim convention: a marker bound to a count by an arrow or a parenthesis
    check(claims("`python3 test_rules.py` → **129/129**") == [("rule suite", 129, 129)],
          "a marker inside a path is attributed to the rule suite")
    check(claims("`python3 test_board.py` (**79/79**)") == [("board suite", 79, 79)],
          "a parenthesis binds a claim just as an arrow does")
    check(claims("`--full` → **11/11**") == [("gate full", 11, 11)],
          "the full-gate marker is attributed to the full total")
    check(claims("sin `--full` → **9/9**") == [("gate fast", 9, 9)],
          "the `--full` nested inside 'sin --full' does not steal the claim")
    check(claims("`schemas/validate.py` → **12/12**") == [("contracts", 12, 12)],
          "the contract validator is attributed to the contracts total")

    # ── two bindings on one line keep their own subjects
    check(claims("`--full` → **11/11**, sin `--full` → **9/9**") == [("gate full", 11, 11), ("gate fast", 9, 9)],
          "two bindings on one line are attributed separately")

    # ── what must NOT be read as a claim, which is why this guard does not cry wolf
    check(claims("exploration 385/997 (38.6%), held-out 98/231 (42.4%)") == [],
          "a ratio with no marker is not a claim")
    check(claims("total 1,228/1,228 identical suggestions") == [],
          "a comma-grouped ratio is not a claim")
    check(claims("[falta info ×8/8]") == [],
          "eight of eight missing fields is not a gate claim")
    check(claims("34 deterministic matches out of 90 sampled issues: 32/34") == [],
          "judge agreement is not a claim about a subject")

    # ── the counting arithmetic, including its dependence on the environment
    check(gate_totals_from(7, 2, 1) == (8, 10),
          "with the contracts step: 7+1 fast, 7+2+1 full")
    check(gate_totals_from(8, 2, 1) == (9, 11),
          "one more fast check moves both totals")
    check(gate_totals_from(8, 2, 0) == (8, 10),
          "without .venv the denominator drops by one, because the contracts step is skipped")

    print("\n════════════════════════════════════════════════════════════════════")
    print(f" FINAL TEST RESULT: {passed}/{total} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
