#!/usr/bin/env python3
"""
test_rules.py — Comprehensive test suite for deterministic triage rules (db/rules.py)

Validates:
  1. P0 Positive cases (silent data loss, corruption, silent drops/overwrites)
  2. P0 Negative safeguards (negated data loss phrases: 'prevents data loss', 'no data loss')
  3. P1 Positive crash cases ('panic: runtime error', 'SIGSEGV', 'NullPointerException', etc.)
  4. Rule H9 vs H10 Demotion (crash WITH workaround or retry recovery demotes to P2)
  5. Workaround Negation (explicit 'workaround: none' or 'no workaround' remains P1)
  6. Overfit Pattern Elimination ('busy-loop.*frozen' and 'dead-end.*lineage' do not trigger P1)
  7. P2 Feature requests and P3 Documentation / Chores
  8. Grey-area / Indeterminate fall-through (requires LLM Pass 1)
  9. Dataset Snapshot verification (loads issues.json and verifies dynamic calculation)

Usage:
  python3 test_rules.py
"""

import json
import sys
from pathlib import Path

# Add db/ to import path
sys.path.insert(0, str(Path(__file__).parent / "db"))
from rules import (
    classify_issue_deterministically,
    has_active_workaround,
    RE_P0_SILENT,
    RE_P0_NEGATION,
    RE_P1_CRASH,
    RE_WORKAROUND_POSITIVE,
    RE_WORKAROUND_NEGATIVE,
)


def run_tests():
    print("════════════════════════════════════════════════════════════════════")
    print(" RUNNING DETERMINISTIC RULES TEST SUITE (test_rules.py)")
    print("════════════════════════════════════════════════════════════════════\n")

    passed = 0
    total = 0

    def assert_test(condition, desc):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  ✔ [PASS] {desc}")
            passed += 1
        else:
            print(f"  ❌ [FAIL] {desc}", file=sys.stderr)
            sys.exit(1)

    # ─────────────────────────────────────────────────────────────────
    # 1. P0 POSITIVE CASES (Silent Data Loss & Corruption)
    # ─────────────────────────────────────────────────────────────────
    print("── 1. P0 POSITIVE CASES (Silent Data Loss & Corruption) ──")
    p0_positive_phrases = [
        "silently dropped rows during migration",
        "silently corrupted the db on shutdown",
        "silently lost data when buffer overflowed",
        "silently overwrites files without prompt",
        "panic: silently dropped rows",
        "unexpected data loss during table flush",
        "engine silently fails to save configuration",
    ]
    for phrase in p0_positive_phrases:
        row = {"title": phrase, "body": "Observed in test", "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(band == "P0" and rule == "rule:silent_data_loss", f"P0 positive: '{phrase[:45]}'")

    # ─────────────────────────────────────────────────────────────────
    # 2. P0 NEGATIVE SAFEGUARDS (Negated Data Loss must NOT trigger P0)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 2. P0 NEGATIVE SAFEGUARDS (Negations must NOT trigger P0) ──")
    p0_negative_phrases = [
        "this feature ensures no data loss during migration",
        "prevents data loss when disk is full",
        "avoid data loss by flushing WAL immediately",
        "system completes transaction without data loss",
        "guarantees zero data loss replication",
        "safeguard against data loss on unexpected reboot",
    ]
    for phrase in p0_negative_phrases:
        row = {"title": phrase, "body": "Description of behavior", "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(band != "P0", f"P0 negative safe: '{phrase[:45]}' -> {band} (not P0)")

    # ─────────────────────────────────────────────────────────────────
    # 3. P1 POSITIVE CRASH CASES (Hard Crashes)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 3. P1 POSITIVE CRASH CASES (Hard Crashes without Workaround) ──")
    p1_positive_crashes = [
        "panic: runtime error: index out of range",
        "fatal error: runtime: out of memory",
        "SIGSEGV in worker process on boot",
        "segmentation fault when dereferencing null pointer",
        "NullPointerException in MessageHandler",
        "uncaught exception terminated thread",
        "deadlock in transaction coordinator",
        "stack overflow during recursive traversal",
    ]
    for phrase in p1_positive_crashes:
        row = {"title": phrase, "body": "Call stack attached", "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(band == "P1" and rule == "rule:hard_crash", f"P1 positive: '{phrase[:45]}'")

    # ─────────────────────────────────────────────────────────────────
    # 4. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 4. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──")
    crash_with_workarounds = [
        (
            "panic: runtime error: index out of range",
            "Workaround: run with --disable-cache flag to avoid index error",
        ),
        (
            "SIGSEGV on startup when config is missing",
            "Temporary fix: touch config.json before launching the binary",
        ),
        (
            "fatal error: runtime deadlock in pool",
            "Recovers upon retry when worker pool reinitializes",
        ),
        (
            "NullPointerException in sync loop",
            "Restart fixes the issue temporarily until next sync",
        ),
    ]
    for title, body in crash_with_workarounds:
        row = {"title": title, "body": body, "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(
            band == "P2" and rule == "rule:crash_with_workaround_demoted_to_p2",
            f"Crash + Workaround demoted to P2: '{title[:35]}' + '{body[:35]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 5. WORKAROUND NEGATION (Explicitly NO Workaround -> Remains P1)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 5. WORKAROUND NEGATION (Explicit 'No Workaround' -> Remains P1) ──")
    crash_without_workarounds = [
        (
            "panic: runtime error: nil dereference",
            "Workaround: none. The daemon immediately aborts.",
        ),
        (
            "SIGSEGV on boot in initialization routine",
            "No workaround available. Completely dead-end.",
        ),
        (
            "fatal error: runtime: out of memory",
            "Without any workaround; all attempts to launch fail.",
        ),
        (
            "NullPointerException in parser",
            "Workaround: n/a. Issue is reproducible 100% of the time.",
        ),
    ]
    for title, body in crash_without_workarounds:
        row = {"title": title, "body": body, "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(
            band == "P1" and rule == "rule:hard_crash",
            f"Crash + Negated Workaround remains P1: '{title[:35]}' + '{body[:35]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 6. OVERFIT PATTERN ELIMINATION (Must NOT trigger P1)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 6. OVERFIT PATTERN ELIMINATION (Generalized / Removed) ──")
    overfit_phrases = [
        "busy-loop on frozen review session",
        "dead-end encountered in review lineage",
    ]
    for phrase in overfit_phrases:
        row = {"title": phrase, "body": "Encountered in workflow", "title_prefix": "bug"}
        band, _, rule = classify_issue_deterministically(row, ["bug"], [])
        assert_test(
            band != "P1",
            f"Overfit pattern does not trigger P1: '{phrase}' -> band={band}",
        )

    # ─────────────────────────────────────────────────────────────────
    # 7. P2 FEATURES & P3 DOCUMENTATION / CHORES
    # ─────────────────────────────────────────────────────────────────
    print("\n── 7. P2 FEATURES & P3 CHORES / DOCUMENTATION ──")
    p2_cases = [
        {"title": "feat(core): add streaming support", "body": "Feature request", "title_prefix": "feat", "labels": []},
        {"title": "add dark mode to user interface", "body": "UI enhancement", "title_prefix": "", "labels": ["enhancement"]},
        {"title": "type:feature - support PostgreSQL", "body": "DB adapter", "title_prefix": "", "labels": ["type:feature"]},
    ]
    for tc in p2_cases:
        band, _, rule = classify_issue_deterministically(tc, tc.get("labels", []), [])
        assert_test(band == "P2" and rule == "rule:feature_request", f"Feature -> P2: '{tc['title'][:40]}'")

    p3_cases = [
        {"title": "docs: update getting started guide", "body": "Fix broken link", "title_prefix": "docs", "labels": []},
        {"title": "chore: bump dependencies to latest", "body": "Monthly updates", "title_prefix": "chore", "labels": []},
        {"title": "typo in configuration documentation", "body": "Correct spelling", "title_prefix": "typo", "labels": []},
        {"title": "question: how to configure custom port", "body": "User inquiry", "title_prefix": "", "labels": ["question"]},
    ]
    for tc in p3_cases:
        band, _, rule = classify_issue_deterministically(tc, tc.get("labels", []), [])
        assert_test(band == "P3" and rule == "rule:docs_chore_question", f"Docs/Chore -> P3: '{tc['title'][:40]}'")

    # ─────────────────────────────────────────────────────────────────
    # 8. GREY-AREA / INDETERMINATE (Requires LLM Pass 1)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 8. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──")
    grey_cases = [
        {"title": "button alignment is slightly off in Safari", "body": "Visual bug", "title_prefix": "bug", "labels": ["bug"]},
        {"title": "search results return in unexpected order", "body": "Sorting issue", "title_prefix": "bug", "labels": ["bug"]},
        {"title": "intermittent latency spike during peak load", "body": "Performance issue", "title_prefix": "bug", "labels": ["bug"]},
    ]
    for tc in grey_cases:
        band, _, rule = classify_issue_deterministically(tc, tc.get("labels", []), [])
        assert_test(band is None and rule is None, f"Grey area -> Indeterminate: '{tc['title'][:40]}'")

    # ─────────────────────────────────────────────────────────────────
    # 9. DYNAMIC DATASET SNAPSHOT VERIFICATION (issues.json)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 9. DYNAMIC DATASET SNAPSHOT VERIFICATION (issues.json) ──")
    snapshot_file = Path(__file__).parent / "issues.json"
    assert_test(snapshot_file.exists(), f"Snapshot file exists at {snapshot_file}")
    with open(snapshot_file, "r", encoding="utf-8") as f:
        snapshot_issues = json.load(f)

    assert_test(len(snapshot_issues) == 1228, f"Snapshot contains exactly 1,228 open issues (found {len(snapshot_issues)})")

    classified_count = 0
    rule_histogram = {}
    for item in snapshot_issues:
        band, _, rule = classify_issue_deterministically(item, item.get("labels", []), item.get("cross_refs", []))
        if band is not None:
            classified_count += 1
            rule_histogram[rule] = rule_histogram.get(rule, 0) + 1

    pct_classified = 100.0 * classified_count / len(snapshot_issues)
    assert_test(
        classified_count == 491,
        f"Dynamic calculation on snapshot yields exactly 491 resolved issues ({pct_classified:.1f}%)"
    )
    assert_test(
        rule_histogram.get("rule:feature_request") == 415,
        f"rule:feature_request matches exactly 415 issues"
    )
    assert_test(
        rule_histogram.get("rule:docs_chore_question") == 52,
        f"rule:docs_chore_question matches exactly 52 issues"
    )
    assert_test(
        rule_histogram.get("rule:silent_data_loss") == 17,
        f"rule:silent_data_loss matches exactly 17 issues"
    )
    assert_test(
        rule_histogram.get("rule:hard_crash") == 7,
        f"rule:hard_crash matches exactly 7 issues"
    )

    print("\n────────────────────────────────────────────────────────────────────")
    print(f" FINAL TEST RESULT: {passed}/{total} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
