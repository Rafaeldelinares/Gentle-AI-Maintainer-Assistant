#!/usr/bin/env python3
"""
test_rules.py — Test suite for the deterministic triage rules (db/rules.py)

Validates by concrete, named real cases rather than fixed totals:
  1.  Candidate P0 positives (silent data loss, corruption, silent drops)
  2.  P0 negation safeguards ('no/without/not ... data loss')
  3.  Fix-description rejection ('from being silently dropped to being rejected')
  4.  Real-issue regression cases (#5007, #4792, #2628, #4807)
  5.  Hard-crash vocabulary, including the cases widened after AUDIT.md
      ('crashes', 'uncaughtException', 'Go runtime panic', 'fails to start',
       'out of memory', 'OOM killer')
  6.  Negation and idiom guards ('not a crash', 'has not been demonstrated',
      'crash-safe', 'crash-window', 'There is no system crash')
  7.  Deadlock requires process/thread context; metaphorical deadlocks rejected
  8.  Rule H9 vs H10 demotion (crash WITH workaround or retry -> P2)
  9.  Workaround negation ('workaround: none' remains P1)
  10. Overfit pattern elimination
  11. P2 features and P3 docs/chores, plus the AUDIT.md order fix
      (an explicit `docs:` prefix wins over an `enhancement` label)
  12. Grey-area fall-through (requires LLM Pass 1)
  13. title_prefix recovery (leading backtick, bracket prefix, no colon)
  14. requires_human_review (hard signal under a low band; band NOT changed)

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
    requires_human_review,
    has_active_workaround,
    has_silent_data_loss,
    is_hard_crash,
    derive_title_prefix,
    P0_CANDIDATE_LABEL,
    RULE_P0_CANDIDATE,
)

SNAPSHOT = Path(__file__).parent / "issues.json"


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
    # 1. CANDIDATE P0 POSITIVES
    # ─────────────────────────────────────────────────────────────────
    print("── 1. CANDIDATE P0 POSITIVES (Silent Data Loss & Corruption) ──")
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
    print("\n── 4. REAL-ISSUE REGRESSION CASES (#5007, #4792, #2628, #4807) ──")
    for number, body, title in [
        (5007, "No workaround data loss: the local store is intact and the CLI",
         "state preserved after the rejected MCP writes"),
        (4792, "report. No observed runtime failure or data loss is claimed.",
         "documentation claim about burned authority"),
        (2628, "heuristically changed unknown agents from being silently dropped to being rejected",
         "component modifiers report success when not scheduled"),
    ]:
        band, _, rule = classify(title, body, prefix="bug", number=number)
        assert_test(
            band not in (P0_CANDIDATE_LABEL, "P1"),
            f"issue #{number} is not flagged as candidate P0 / P1 -> band={band!r}",
        )
    # #4807 keeps its "not a deadlock" trap rejected, but the widened vocabulary now
    # correctly detects the real memory-exhaustion signal in the same issue.
    assert_test(
        not is_hard_crash("It is a fork bomb, not a deadlock."),
        "#4807 trap phrase 'not a deadlock' alone is not a crash",
    )
    band_4807, _, rule_4807 = classify(
        "bug(TUI) ResolveTarget can bake another tool's wrapper as the OpenCode target, creating a launcher cycle that fork-bombs",
        "The launcher spawns a new cmd.exe per lap until the machine runs out of memory.",
        prefix="", number=4807,
    )
    assert_test(
        band_4807 == "P1" and rule_4807 == "rule:hard_crash",
        f"#4807 is P1 from memory exhaustion, not from the deadlock metaphor (band={band_4807!r})",
    )

    # ─────────────────────────────────────────────────────────────────
    # 5. HARD-CRASH VOCABULARY WIDENED AFTER AUDIT.md
    # ─────────────────────────────────────────────────────────────────
    print("\n── 5. HARD-CRASH VOCABULARY (widened after AUDIT.md) ──")
    p1_positive_crashes = [
        "panic: runtime error: index out of range",
        "fatal error: runtime: out of memory",
        "SIGSEGV in worker process on boot",
        "segmentation fault when dereferencing null pointer",
        "NullPointerException in MessageHandler",
        "uncaught exception terminated thread",
        "stack overflow during recursive traversal",
        "recursive skill watcher crashes Pi with uncaughtException ENOENT",
        "bare `gentle-ai` invocation crashes with Go runtime panic",
        "the process can fail to start even though `pi --version` works",
        "the machine runs out of memory",
        "terminated by the OOM killer",
        "causing the parser to crash",
        "fatal error: all goroutines are asleep - deadlock!",
        "worker thread enters deadlock when acquiring mutex",
        "process hangs due to deadlock in event loop",
    ]
    for phrase in p1_positive_crashes:
        band, _, rule = classify(phrase, "Call stack attached")
        assert_test(band == "P1" and rule == "rule:hard_crash", f"P1 positive: '{phrase[:55]}'")

    # ─────────────────────────────────────────────────────────────────
    # 6. CRASH NEGATION AND IDIOM GUARDS
    # ─────────────────────────────────────────────────────────────────
    print("\n── 6. CRASH NEGATION AND IDIOM GUARDS (No false crash) ──")
    crash_rejects = [
        "It is a fork bomb, not a deadlock.",
        "This is not a deadlock situation",
        "The two rules deadlock each other.",
        "ordinary review denials deadlock the agent",
        "the review is deadlocked",
        "sdd-remediate run can deadlock before phase work",
        "There is no system crash, but the API usage log reflects retention",
        "the finding's premise (a live crash-on-render risk) does not apply",
        "Crash-window tests not parameterized for the new class",
        "a live crash-on-render risk does not apply",
        "the review cannot start for this candidate",
        "The native RDD assessment cannot start because a binary is missing",
        "a reload crash was already reported in another issue",
        "designed to be crash-safe by kernel release",
        "a general crash-recoverable quarantine engine",
        "prevent these filesystem errors from crashing Pi",
    ]
    for phrase in crash_rejects:
        assert_test(not is_hard_crash(phrase), f"no false crash: '{phrase[:55]}'")
    crash_accepts = [
        "fatal error: all goroutines are asleep - deadlock!",
        "mutex deadlock detected in worker pool",
        "thread deadlock on channel receive",
        "Pi crashes on startup",
        "it can corrupt or revert on crash",
        "the parser crashes when the payload is truncated",
    ]
    for phrase in crash_accepts:
        assert_test(is_hard_crash(phrase), f"real crash accepted: '{phrase[:55]}'")

    # ─────────────────────────────────────────────────────────────────
    # 7. RULE H9 vs H10 DEMOTION
    # ─────────────────────────────────────────────────────────────────
    print("\n── 7. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──")
    crash_with_workarounds = [
        ("panic: runtime error: index out of range",
         "Workaround: run with --disable-cache flag to avoid index error"),
        ("SIGSEGV on startup when config is missing",
         "Temporary fix: touch config.json before launching the binary"),
        ("fatal error: runtime deadlock in pool",
         "Recovers upon retry when worker pool reinitializes"),
        ("NullPointerException in sync loop",
         "Restart fixes the issue temporarily until next sync"),
        ("Pi fails to start after the overlay corrupts the file",
         "Workaround: repair the two lines back to a valid list by hand"),
        ("Pi crashes on reload",
         "The same command works after running git init"),
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
        ("panic: runtime error: nil dereference",
         "Workaround: none. The daemon immediately aborts."),
        ("SIGSEGV on boot in initialization routine",
         "No workaround available. Completely dead-end."),
        ("fatal error: runtime: out of memory",
         "Without any workaround; all attempts to launch fail."),
        ("NullPointerException in parser",
         "Workaround: n/a. Issue is reproducible 100% of the time."),
        ("Pi crashes when the session is loaded",
         "Note that no configuration can work around it: the headers are fixed."),
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

    # AUDIT.md order fix: an explicit `docs:` prefix wins over an `enhancement` label.
    band, _, rule = classify(
        "docs(sdd): remove retired SDD references from living docs",
        "Documentation cleanup.",
        prefix="docs", labels=["enhancement", "status:approved"], number=5168,
    )
    assert_test(
        band == "P3" and rule == "rule:docs_chore_question",
        f"#5168 explicit docs prefix wins over enhancement label -> {band!r} ({rule})",
    )

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
    # 12. TITLE PREFIX RECOVERY (AUDIT.md finding)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 12. TITLE PREFIX RECOVERY (leading backtick / bracket / no colon) ──")
    prefix_cases = [
        ("`bug(install): Pi commands fail through pi.cmd on Windows", "", "bug"),
        ("[Automated provider defect] bug(opencode): orchestrator calls unavailable tools", "", "bug"),
        ("bug(TUI) ResolveTarget can bake another tool's wrapper", "", "bug"),
        ("bug(2.3.0-rc.1) 6 Tests Results in Opencode", "", "bug"),
        ("fix(review) bloqueada por fallo de captura", "", "fix"),
        ("bug(harness) Agent left the current project directory", "", "bug"),
        ("Windows Terminal rendering is broken", "", ""),
        ("Error: something failed", "", ""),
    ]
    for title, provided, expected in prefix_cases:
        got = derive_title_prefix(title, provided)
        assert_test(got == expected, f"prefix '{title[:45]}' -> {got!r} (expected {expected!r})")

    # A recovered prefix changes the band: the crash report is no longer grey.
    band, _, rule = classify(
        "`bug(install): Pi commands fail through pi.cmd on Windows",
        "When `pi` resolves to that CMD launcher, the process can fail to start.",
        prefix="", number=4974,
    )
    assert_test(band == "P1" and rule == "rule:hard_crash",
                f"#4974 recovered prefix yields P1 (band={band!r})")

    # ─────────────────────────────────────────────────────────────────
    # 13. REQUIRES_HUMAN_REVIEW (band unchanged, flag raised)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 13. REQUIRES_HUMAN_REVIEW (hard signal under a low band) ──")
    row_feat = {"slug": "gentle-ai", "number": 1, "system_id": 1,
                "title": "feat(gemini): modularize GEMINI.md root",
                "body": "As a result, every fresh session silently drops the entire Engram protocol.",
                "title_prefix": "feat"}
    band, _, rule = classify_issue_deterministically(row_feat, ["enhancement"], [])
    flag, reason = requires_human_review(row_feat, ["enhancement"], [])
    assert_test(band == "P2" and rule == "rule:feature_request", f"feat with hard signal keeps band P2 (got {band!r})")
    assert_test(flag and "silent data loss" in (reason or ""), "feat with silent loss is flagged for human review")

    row_docs = {"slug": "gentle-ai", "number": 2, "system_id": 1,
                "title": "docs(x): update guide", "body": "Pi crashes on startup when the file is missing.",
                "title_prefix": "docs"}
    flag2, reason2 = requires_human_review(row_docs, ["documentation"], [])
    assert_test(flag2 and "crash" in (reason2 or ""), "docs with a crash is flagged for human review")

    row_clean = {"slug": "gentle-ai", "number": 3, "system_id": 1,
                 "title": "docs(x): add a section", "body": "Add a documentation section.", "title_prefix": "docs"}
    flag3, _ = requires_human_review(row_clean, ["documentation"], [])
    assert_test(not flag3, "clean docs issue is not flagged for human review")

    # ─────────────────────────────────────────────────────────────────
    # 14. SNAPSHOT SELF-CONSISTENCY (dynamic, no frozen totals)
    # ─────────────────────────────────────────────────────────────────
    print("\n── 14. SNAPSHOT SELF-CONSISTENCY (issues.json, dynamic) ──")
    assert_test(SNAPSHOT.exists(), "Snapshot file issues.json exists")
    with open(SNAPSHOT, "r", encoding="utf-8") as f:
        snapshot_issues = json.load(f)
    assert_test(len(snapshot_issues) > 0, f"Snapshot is non-empty (found {len(snapshot_issues)} issues)")

    index = {(it.get("slug"), it.get("number")): it for it in snapshot_issues}

    def snap_band(slug, number):
        it = index[(slug, number)]
        return classify_issue_deterministically(it, it.get("labels", []), it.get("cross_refs", []))

    # Named real cases: classification must match the corrected engine.
    expectations = [
        (("gentle-ai", 5007), None, "explicit 'no data loss' stays out of candidate P0/P1"),
        (("gentle-ai", 4792), None, "explicit 'no data loss claimed' stays out of candidate P0/P1"),
        (("gentle-ai", 2628), None, "fix description stays out of candidate P0/P1"),
        (("gentle-ai", 4807), "P1", "real memory exhaustion yields P1"),
        (("gentle-ai", 4917), P0_CANDIDATE_LABEL, "real silent loss is a candidate P0"),
        (("gentle-ai", 4677), "P1", "'crashes with Go runtime panic' is P1"),
        (("gentle-shell", 962), "P1", "'crashes Pi with uncaughtException' is P1"),
        (("gentle-ai", 4974), "P1", "recovered prefix + 'fail to start' is P1"),
        (("gentle-ai", 4809), "P2", "'fails to start' with a workaround is demoted to P2"),
        (("gentle-ai", 5168), "P3", "explicit docs prefix wins over enhancement label"),
    ]
    for (slug, number), expected, why in expectations:
        assert_test((slug, number) in index, f"snapshot contains {slug}#{number}")
        got, _, rule = snap_band(slug, number)
        assert_test(got == expected, f"{slug}#{number} -> {got!r} (expected {expected!r}): {why}")

    # Dynamic recomputation must be reproducible.
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
    assert_test(sum(first_pass.values()) > 0, f"engine covers at least one issue ({sum(first_pass.values())} covered)")
    assert_test(first_pass.get(RULE_P0_CANDIDATE, 0) > 0, "candidate P0 rule is exercised on the snapshot")
    assert_test(first_pass.get("rule:hard_crash", 0) > 0, "hard-crash rule is exercised on the snapshot")

    print("\n  Dynamic rule histogram over issues.json (recomputed, not frozen):")
    for rule, cnt in sorted(first_pass.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {rule:44s}: {cnt:4d}")

    print("\n────────────────────────────────────────────────────────────────────")
    print(f" FINAL TEST RESULT: {passed}/{total} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
