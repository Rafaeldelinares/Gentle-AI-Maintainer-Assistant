#!/usr/bin/env python3
"""
test_rules.py — Comprehensive test suite for deterministic triage rules (db/rules.py)

Validates, by concrete case rather than fixed totals:
  1. P0 candidate positives (silent data loss, corruption, silent drops/overwrites)
  2. P0 negation safeguards ('no/without/not ... data loss')
  3. Fix-description rejection ('from being silently dropped to being rejected')
  4. Real-issue regression cases: #5007, #4792, #4807, #2628 must NOT trigger high bands
  5. Hard crash positives ('panic:', 'SIGSEGV', 'NullPointerException', etc.)
  6. Deadlock requires process/thread context; 'not a deadlock' and 'two rules deadlock' rejected
  7. Rule H9 vs H10 demotion (crash WITH workaround or retry recovery demotes to P2)
  8. Workaround negation ('workaround: none' / 'no workaround' remains P1)
  9. Overfit pattern elimination ('busy-loop.*frozen', 'dead-end.*lineage')
  10. P2 feature requests and P3 documentation / chores
  11. Grey-area / indeterminate fall-through (requires LLM Pass 1)
  12. Snapshot self-consistency: dynamic run over issues.json with the exact issues the
      rules are expected to flag, never a frozen total.

Governance invariant: a deterministic silent-data-loss match is emitted strictly as
'candidato P0, requiere revisión humana' (candidate P0 requiring human review), never as a
final P0 decision.

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
    has_silent_data_loss,
    is_hard_crash,
    P0_CANDIDATE_LABEL,
    RULE_P0_CANDIDATE,
    RE_P0_SILENT_BASE,
    RE_P1_CRASH_CORE,
    RE_DEADLOCK_BASE,
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

    def classify(title, body="", prefix="bug", labels=None, cross_refs=None, slug="gentle-ai", number=1):
        row = {
            "id": number, "system_id": 1, "slug": slug, "number": number,
            "title": title, "body": body, "title_prefix": prefix,
        }
        return classify_issue_deterministically(row, labels if labels is not None else ["bug"], cross_refs or [])

    # ─────────────────────────────────────────────────────────────────
    # 1. P0 CANDIDATE POSITIVES
    # ─────────────────────────────────────────────────────────────────
    print("── 1. P0 CANDIDATE POSITIVES (Silent Data Loss & Corruption) ──")
    p0_positive_phrases = [
        "silently dropped rows during migration",
        "silently corrupted the db on shutdown",
        "silently lost data when buffer overflowed",
        "silently overwrites files without prompt",
        "panic: silently dropped rows",
        "unexpected data loss during table flush",
        "engine silently fails to save configuration",
        "A corrupt custom-agents.json silently drops the registry entry of a successful install",
    ]
    for phrase in p0_positive_phrases:
        band, _, rule = classify(phrase, "Observed in test")
        assert_test(
            band == P0_CANDIDATE_LABEL and rule == RULE_P0_CANDIDATE,
            f"candidate P0 via {RULE_P0_CANDIDATE}: '{phrase[:50]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 2. P0 NEGATION SAFEGUARDS
    # ─────────────────────────────────────────────────────────────────
    print("\n── 2. P0 NEGATION SAFEGUARDS (Negations must NOT trigger P0) ──")
    p0_negative_phrases = [
        "this feature ensures no data loss during migration",
        "prevents data loss when disk is full",
        "avoid data loss by flushing WAL immediately",
        "system completes transaction without data loss",
        "guarantees zero data loss replication",
        "safeguard against data loss on unexpected reboot",
        "no data loss on this path",
        "the run completes without data loss",
        "this is not data loss",
    ]
    for phrase in p0_negative_phrases:
        band, _, rule = classify(phrase, "Description of behavior")
        assert_test(band != P0_CANDIDATE_LABEL, f"negated data loss not flagged: '{phrase[:50]}' -> {band}")

    # ─────────────────────────────────────────────────────────────────
    # 3. FIX-DESCRIPTION REJECTION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 3. FIX-DESCRIPTION REJECTION (Describing a fix is not a defect) ──")
    fix_descriptions = [
        "changed unknown agents from being silently dropped to being rejected",
        "prevents records from being silently dropped",
    ]
    for phrase in fix_descriptions:
        assert_test(
            not has_silent_data_loss(phrase),
            f"fix description is not silent data loss: '{phrase[:50]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 4. REAL-ISSUE REGRESSION CASES
    # ─────────────────────────────────────────────────────────────────
    print("\n── 4. REAL-ISSUE REGRESSION CASES (#5007, #4792, #4807, #2628) ──")
    regression_cases = [
        (5007, "No workaround data loss: the local store is intact and the CLI",
         "state preserved after the rejected MCP writes"),
        (4792, "report. No observed runtime failure or data loss is claimed.",
         "documentation claim about burned authority"),
        (4807, "It is a fork bomb, not a deadlock. Measured on one machine: 504 python.exe",
         "launcher cycle created by ResolveTarget"),
        (2628, "heuristically changed unknown agents from being silently dropped to being rejected",
         "component modifiers report success when not scheduled"),
    ]
    for number, body, title in regression_cases:
        band, _, rule = classify(title, body, prefix="bug", number=number)
        assert_test(
            band not in (P0_CANDIDATE_LABEL, "P1"),
            f"issue #{number} is not flagged as candidate P0 / P1 -> band={band!r}",
        )

    # ─────────────────────────────────────────────────────────────────
    # 5. P1 HARD CRASH POSITIVES
    # ─────────────────────────────────────────────────────────────────
    print("\n── 5. P1 HARD CRASH POSITIVES (No workaround) ──")
    p1_positive_crashes = [
        "panic: runtime error: index out of range",
        "fatal error: runtime: out of memory",
        "SIGSEGV in worker process on boot",
        "segmentation fault when dereferencing null pointer",
        "NullPointerException in MessageHandler",
        "uncaught exception terminated thread",
        "stack overflow during recursive traversal",
        "fatal error: all goroutines are asleep - deadlock!",
        "worker thread enters deadlock when acquiring mutex",
        "process hangs due to deadlock in event loop",
    ]
    for phrase in p1_positive_crashes:
        band, _, rule = classify(phrase, "Call stack attached")
        assert_test(band == "P1" and rule == "rule:hard_crash", f"P1 positive: '{phrase[:50]}'")

    # ─────────────────────────────────────────────────────────────────
    # 6. DEADLOCK CONTEXT & NEGATION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 6. DEADLOCK REQUIRES PROCESS/THREAD CONTEXT (Metaphors rejected) ──")
    deadlock_rejects = [
        "It is a fork bomb, not a deadlock.",
        "This is not a deadlock situation",
        "The two rules deadlock each other.",
        "ordinary review denials deadlock the agent",
        "the review is deadlocked",
        "sdd-remediate run can deadlock before phase work",
    ]
    for phrase in deadlock_rejects:
        assert_test(
            not is_hard_crash(phrase),
            f"deadlock without concurrency context rejected: '{phrase[:50]}'",
        )
    deadlock_accepts = [
        "fatal error: all goroutines are asleep - deadlock!",
        "mutex deadlock detected in worker pool",
        "thread deadlock on channel receive",
    ]
    for phrase in deadlock_accepts:
        assert_test(is_hard_crash(phrase), f"real concurrency deadlock accepted: '{phrase[:50]}'")

    # ─────────────────────────────────────────────────────────────────
    # 7. RULE H9 vs H10 DEMOTION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 7. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──")
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
        band, _, rule = classify(title, body)
        assert_test(
            band == "P2" and rule == "rule:crash_with_workaround_demoted_to_p2",
            f"crash + workaround demoted to P2: '{title[:35]}' + '{body[:35]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 8. WORKAROUND NEGATION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 8. WORKAROUND NEGATION (Explicit 'No Workaround' -> Remains P1) ──")
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
        band, _, rule = classify(title, body)
        assert_test(
            band == "P1" and rule == "rule:hard_crash",
            f"crash + negated workaround remains P1: '{title[:35]}' + '{body[:35]}'",
        )

    # ─────────────────────────────────────────────────────────────────
    # 9. OVERFIT PATTERN ELIMINATION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 9. OVERFIT PATTERN ELIMINATION (Generalized / Removed) ──")
    overfit_phrases = [
        "busy-loop on frozen review session",
        "dead-end encountered in review lineage",
    ]
    for phrase in overfit_phrases:
        band, _, rule = classify(phrase, "Encountered in workflow")
        assert_test(band != "P1", f"overfit pattern does not trigger P1: '{phrase}' -> band={band}")

    # ─────────────────────────────────────────────────────────────────
    # 10. P2 FEATURES & P3 CHORES
    # ─────────────────────────────────────────────────────────────────
    print("\n── 10. P2 FEATURES & P3 CHORES / DOCUMENTATION ──")
    p2_cases = [
        {"title": "feat(core): add streaming support", "body": "Feature request", "prefix": "feat", "labels": []},
        {"title": "add dark mode to user interface", "body": "UI enhancement", "prefix": "", "labels": ["enhancement"]},
        {"title": "type:feature - support PostgreSQL", "body": "DB adapter", "prefix": "", "labels": ["type:feature"]},
    ]
    for tc in p2_cases:
        band, _, rule = classify(tc["title"], tc["body"], prefix=tc["prefix"], labels=tc["labels"])
        assert_test(band == "P2" and rule == "rule:feature_request", f"feature -> P2: '{tc['title'][:40]}'")

    p3_cases = [
        {"title": "docs: update getting started guide", "body": "Fix broken link", "prefix": "docs", "labels": []},
        {"title": "chore: bump dependencies to latest", "body": "Monthly updates", "prefix": "chore", "labels": []},
        {"title": "typo in configuration documentation", "body": "Correct spelling", "prefix": "typo", "labels": []},
        {"title": "question: how to configure custom port", "body": "User inquiry", "prefix": "", "labels": ["question"]},
    ]
    for tc in p3_cases:
        band, _, rule = classify(tc["title"], tc["body"], prefix=tc["prefix"], labels=tc["labels"])
        assert_test(band == "P3" and rule == "rule:docs_chore_question", f"docs/chore -> P3: '{tc['title'][:40]}'")

    # ─────────────────────────────────────────────────────────────────
    # 11. GREY-AREA FALL-THROUGH
    # ─────────────────────────────────────────────────────────────────
    print("\n── 11. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──")
    grey_cases = [
        {"title": "button alignment is slightly off in Safari", "body": "Visual bug"},
        {"title": "search results return in unexpected order", "body": "Sorting issue"},
        {"title": "intermittent latency spike during peak load", "body": "Performance issue"},
    ]
    for tc in grey_cases:
        band, _, rule = classify(tc["title"], tc["body"])
        assert_test(band is None and rule is None, f"grey area -> indeterminate: '{tc['title'][:40]}'")

    # ─────────────────────────────────────────────────────────────────
    # 12. SNAPSHOT SELF-CONSISTENCY (dynamic, no frozen totals)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 12. SNAPSHOT SELF-CONSISTENCY (issues.json, dynamic) ──")
    snapshot_file = Path(__file__).parent / "issues.json"
    assert_test(snapshot_file.exists(), "Snapshot file issues.json exists")
    with open(snapshot_file, "r", encoding="utf-8") as f:
        snapshot_issues = json.load(f)
    assert_test(len(snapshot_issues) > 0, f"Snapshot is non-empty (found {len(snapshot_issues)} issues)")

    index = {(it.get("slug"), it.get("number")): it for it in snapshot_issues}

    # #5007 / #4792 / #4807 / #2628 must stay out of candidate P0 and P1 in the real snapshot.
    for slug, number in [("gentle-ai", 5007), ("gentle-ai", 4792), ("gentle-ai", 4807), ("gentle-ai", 2628)]:
        item = index.get((slug, number))
        assert_test(item is not None, f"snapshot contains {slug}#{number}")
        band, _, rule = classify_issue_deterministically(item, item.get("labels", []), item.get("cross_refs", []))
        assert_test(
            band not in (P0_CANDIDATE_LABEL, "P1"),
            f"snapshot regression {slug}#{number} not candidate P0/P1 -> band={band!r}",
        )

    # The known genuinely-silent case must be flagged as a candidate (not a final P0).
    item_4917 = index.get(("gentle-ai", 4917))
    assert_test(item_4917 is not None, "snapshot contains gentle-ai#4917")
    band_4917, _, rule_4917 = classify_issue_deterministically(
        item_4917, item_4917.get("labels", []), item_4917.get("cross_refs", [])
    )
    assert_test(
        band_4917 == P0_CANDIDATE_LABEL and rule_4917 == RULE_P0_CANDIDATE,
        f"snapshot gentle-ai#4917 is a candidate P0, not a final decision (band={band_4917!r})",
    )

    # Dynamic recomputation must be reproducible: two passes over the snapshot agree.
    def snapshot_digest():
        digest = {}
        for item in snapshot_issues:
            band, _, rule = classify_issue_deterministically(item, item.get("labels", []), item.get("cross_refs", []))
            if band is not None:
                digest[rule] = digest.get(rule, 0) + 1
        return digest

    first_pass = snapshot_digest()
    second_pass = snapshot_digest()
    assert_test(first_pass == second_pass, "dynamic snapshot classification is reproducible across passes")

    covered = sum(first_pass.values())
    assert_test(covered > 0, f"deterministic engine covers at least one snapshot issue ({covered} covered)")
    assert_test(
        first_pass.get(RULE_P0_CANDIDATE, 0) > 0,
        f"candidate P0 rule is exercised on the snapshot ({first_pass.get(RULE_P0_CANDIDATE, 0)} candidates)",
    )

    print("\n  Dynamic rule histogram over issues.json (recomputed, not frozen):")
    for rule, cnt in sorted(first_pass.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {rule:44s}: {cnt:4d}")

    print("\n────────────────────────────────────────────────────────────────────")
    print(f" FINAL TEST RESULT: {passed}/{total} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
