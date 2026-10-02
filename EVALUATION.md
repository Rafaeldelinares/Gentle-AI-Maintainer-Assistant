# EVALUATION.md — External Audit & Technical Verification Guide

> **Self-contained evaluation artifact for external technical auditors.**
> This document allows complete inspection and validation of the Gentle AI Maintainer Assistant proposal without requiring directory navigation or repository cloning.

---

## 1. Source Code: `db/rules.py`

Fuente: `db/rules.py @ 573c732`

```python
#!/usr/bin/env python3
"""
rules.py — Deterministic triage rule engine for the Gentle AI ecosystem

Applies code-based heuristics BEFORE invoking an LLM:
  1. Features / enhancements -> P2 (rule:feature_request)
  2. Docs / chores / questions -> P3 (rule:docs_chore_question)
  3. Silent data loss / corruption -> P0 (rule:silent_data_loss)
  4. Panic / SIGSEGV / hard crash without workaround -> P1 (rule:hard_crash)
  5. Crash WITH documented workaround / retry -> P2 (rule:crash_with_workaround_demoted_to_p2)
  6. Cross-repository links (cross_refs) -> cross classification

Usage:
  ./rules.py
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "exp.db"
SNAPSHOT_PATH = Path(__file__).parent.parent / "issues.json"

# Compiled regex patterns for deterministic text classification
# 1. P0: Silent data loss / corruption (non-capturing groups, bounded word characters)
RE_P0_SILENT = re.compile(
    r"(?:\bsilent(?:ly)?\s+(?:corrupt(?:s|ed|ing|ion)?|delet(?:es|ed|ing|ion)?|drop(?:s|ped|ping)?|overwrit(?:es|ing)?|overwrote|overwritten|los(?:es|t|ing)?|fail(?:s|ed|ing)?\s+to\s+save)\b|\bdata\s+loss\b)",
    re.IGNORECASE,
)

# Negation safeguards for P0 (e.g. 'prevents data loss', 'no data loss' must NOT trigger P0)
RE_P0_NEGATION = re.compile(
    r"\b(?:no|not|prevents?|preventing|avoid(?:s|ed|ing)?|without|protect(?:s|ed|ing)?\s+against|safeguard(?:s|ed|ing)?\s+against|zero)\s+(?:silent(?:ly)?\s+)?(?:data\s+loss|corruption|corrupting)\b",
    re.IGNORECASE,
)

# 2. P1: Hard crashes (without overfitted specific lineage/loop terms)
RE_P1_CRASH = re.compile(
    r"(?:\bpanic:\s*|\bSIGSEGV\b|\bfatal error:\s*runtime\b|\bsegmentation fault\b|\bNullPointerException\b|\buncaught exception\b|\bdeadlock(?:ed)?\b|\bstack overflow\b)",
    re.IGNORECASE,
)

# 3. Workaround & retry recovery detection (Codifies Rule H9)
RE_WORKAROUND_NEGATIVE = re.compile(
    r"\b(?:no(?:ne)?|without(?:\s+any)?|unaware\s+of\s+any)\s+(?:known\s+)?workaround\b|\bworkaround:\s*(?:none|n/?a|no)\b",
    re.IGNORECASE,
)

RE_WORKAROUND_POSITIVE = re.compile(
    r"\b(?:workaround|work-around|temporary fix|temp fix|mitigation|bypass|recovers?(?:\s+upon|\s+on)?\s+retry|retry succeeds|restart fixes)\b",
    re.IGNORECASE,
)

RE_P3_DOCS = re.compile(
    r"^(docs?|chore|typo|style|ci|refactor)(\(.*\))?:\s*",
    re.IGNORECASE,
)


def has_active_workaround(text: str) -> bool:
    """Returns True if text specifies a workaround or retry recovery without stating none exists."""
    if RE_WORKAROUND_NEGATIVE.search(text):
        return False
    return bool(RE_WORKAROUND_POSITIVE.search(text))


def classify_issue_deterministically(row, labels, cross_refs):
    """
    Returns (band, cross, rule_name) or (None, cross, None) if indeterminate.
    """
    row_dict = dict(row) if hasattr(row, "keys") else (row or {})
    title = row_dict.get("title") or ""
    body = row_dict.get("body") or ""
    prefix = (row_dict.get("title_prefix") or "").lower()
    full_text = f"{title}\n{body}"

    # ── 1. CROSS-SYSTEM (from cross_refs) ──
    cross = "none"
    if cross_refs:
        foreign_refs = [cr for cr in cross_refs if cr.get("target_system_id") != row_dict.get("system_id")]
        if foreign_refs:
            cross = "dependency"

    # ── 2. BAND DETERMINISM ──
    label_set = {l.lower() for l in labels}
    is_bug = prefix in ("bug", "fix") or "type:bug" in label_set or "bug" in label_set

    # Check P0: Silent data loss / corruption (only on bugs, excluding explicit negations)
    if is_bug and RE_P0_SILENT.search(full_text) and not RE_P0_NEGATION.search(full_text):
        return "P0", cross, "rule:silent_data_loss"

    # Check P1 vs P2 (Rule H9 & H10): Hard crash / fatal engine stall
    if is_bug and RE_P1_CRASH.search(full_text):
        if has_active_workaround(full_text):
            return "P2", cross, "rule:crash_with_workaround_demoted_to_p2"
        return "P1", cross, "rule:hard_crash"

    # Check P2: Feature / enhancement request
    if (
        prefix in ("feat", "feature")
        or "type:feature" in label_set
        or "enhancement" in label_set
        or "feature" in label_set
    ):
        return "P2", cross, "rule:feature_request"

    # Check P3: Documentation, questions, chores, typos
    if (
        prefix in ("docs", "doc", "chore", "typo")
        or "type:chore" in label_set
        or "documentation" in label_set
        or "question" in label_set
        or "discussion" in label_set
        or RE_P3_DOCS.search(title)
    ):
        return "P3", cross, "rule:docs_chore_question"

    # Indeterminate — must fall through to LLM / human triage
    return None, cross, None


def run_snapshot_evaluation(snapshot_data):
    """Evaluates classification over a loaded JSON snapshot dynamically without hardcoded figures."""
    total = len(snapshot_data)
    rule_counts = {}
    covered = 0

    for item in snapshot_data:
        band, cross, rule = classify_issue_deterministically(
            item, item.get("labels", []), item.get("cross_refs", [])
        )
        if band is not None:
            covered += 1
            rule_counts[rule] = rule_counts.get(rule, 0) + 1

    grey = total - covered
    pct_covered = (100.0 * covered / total) if total > 0 else 0.0
    pct_grey = (100.0 * grey / total) if total > 0 else 0.0

    print("════════════════════════════════════════════════════════════════════")
    print(f" DETERMINISTIC TRIAGE EVALUATION (from issues.json snapshot, {total} issues)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  Classified by code (without LLM): {covered} ({pct_covered:.1f}%)")
    print(f"  Residual grey-area (requires LLM): {grey} ({pct_grey:.1f}%)\n")
    print("  Breakdown by deterministic rule:")
    for rule, cnt in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (100.0 * cnt / total) if total > 0 else 0.0
        print(f"    - {rule:38s}: {cnt:4d} issues ({pct:.1f}%)")
    print("════════════════════════════════════════════════════════════════════")
    return 0


def run_demo():
    print("════════════════════════════════════════════════════════════════════")
    print(" DEMO: DETERMINISTIC CLASSIFICATION (exp.db not found)")
    print("════════════════════════════════════════════════════════════════════")

    # If issues.json exists, evaluate dynamically
    if SNAPSHOT_PATH.exists():
        with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)
        return run_snapshot_evaluation(snapshot_data)

    print(" Notice: Full dataset snapshot not found. Running synthetic validation suite:\n")
    test_cases = [
        {
            "slug": "engram", "number": 101, "title": "docs: update memory architecture guide",
            "body": "Fix typo in schema description", "title_prefix": "docs", "labels": ["documentation"], "cross_refs": []
        },
        {
            "slug": "gentle-ai", "number": 542, "title": "feat: add support for streaming responses",
            "body": "Please add streaming support to review CLI", "title_prefix": "feat", "labels": ["enhancement"], "cross_refs": []
        },
        {
            "slug": "gentle-shell", "number": 88, "title": "fatal error: runtime panic: nil pointer dereference in session_view",
            "body": "SIGSEGV when opening terminal with no config", "title_prefix": "bug", "labels": ["bug"], "cross_refs": []
        },
        {
            "slug": "engram", "number": 19, "title": "save operation silently drops rows when disk is full",
            "body": "Data loss: memory row is acknowledged but not persisted to SQLite", "title_prefix": "bug", "labels": ["bug"], "cross_refs": []
        },
        {
            "slug": "gentle-ai", "number": 712, "title": "review fails when path has trailing slash",
            "body": "Workaround: remove trailing slash from path argument", "title_prefix": "bug", "labels": ["bug"], "cross_refs": []
        },
    ]

    for tc in test_cases:
        row = {"id": tc["number"], "system_id": 1, "slug": tc["slug"], "number": tc["number"], "title": tc["title"], "body": tc["body"], "title_prefix": tc["title_prefix"]}
        band, cross, rule = classify_issue_deterministically(row, tc["labels"], tc["cross_refs"])
        status = f"──► [{band}] via {rule}" if band else "──► [GREY AREA] Requires LLM Pass 1"
        print(f" • {tc['slug']}#{tc['number']}: \"{tc['title'][:55]}\"")
        print(f"   {status}\n")

    print("════════════════════════════════════════════════════════════════════")
    return 0


def main():
    if not DB_PATH.exists():
        return run_demo()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Pre-fetch all labels grouped by issue_id
    cur = conn.cursor()
    cur.execute("SELECT issue_id, name FROM issue_labels il JOIN labels l ON l.id=il.label_id")
    labels_by_issue = {}
    for r in cur.fetchall():
        labels_by_issue.setdefault(r["issue_id"], []).append(r["name"])

    # Pre-fetch cross_refs grouped by issue_id
    cur.execute("SELECT issue_id, target_system_id, target_number, location, raw FROM cross_refs")
    xrefs_by_issue = {}
    for r in cur.fetchall():
        xrefs_by_issue.setdefault(r["issue_id"], []).append(dict(r))

    # Evaluate across all open issues
    cur.execute("""
        SELECT i.id, i.system_id, s.slug, i.number, i.title, i.body, i.title_prefix
        FROM issues i
        JOIN systems s ON s.id = i.system_id
        WHERE i.state = 'open'
    """)
    all_issues = cur.fetchall()

    results_all = {}
    rule_counts = {}
    for row in all_issues:
        iid = row["id"]
        band, cross, rule = classify_issue_deterministically(
            row, labels_by_issue.get(iid, []), xrefs_by_issue.get(iid, [])
        )
        results_all[iid] = (band, cross, rule)
        if rule:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1

    total_all = len(all_issues)
    covered_all = sum(1 for b, c, r in results_all.values() if b is not None)

    print("════════════════════════════════════════════════════════════════════")
    print(f" 1. DETERMINISTIC COVERAGE ACROSS BACKLOG ({total_all} open issues)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  Classified by code (without LLM): {covered_all} ({100.0 * covered_all / total_all:.1f}%)")
    print(f"  Residual grey-area (requires LLM): {total_all - covered_all} ({100.0 * (total_all - covered_all) / total_all:.1f}%)\n")
    print("  Breakdown by deterministic rule:")
    for rule, cnt in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {rule:38s}: {cnt:4d} issues ({100.0 * cnt / total_all:.1f}%)")

    # Evaluate against the 90-issue sample (Run #1) where we have Judge A and Judge B votes
    cur.execute("""
        SELECT i.id, i.system_id, ri.issue_id, s.slug, i.number, i.title, i.body, i.title_prefix
        FROM run_issues ri
        JOIN issues i ON i.id = ri.issue_id
        JOIN systems s ON s.id = i.system_id
        WHERE ri.run_id = 1
        ORDER BY ri.issue_id
    """)
    sample_issues = cur.fetchall()

    cur.execute("""
        SELECT issue_id, judge_id, band, cross
        FROM votes
        WHERE run_id = 1 AND attempt = 2
    """)
    judge_names = {r["id"]: r["name"] for r in conn.execute("SELECT id, name FROM judges").fetchall()}
    votes_by_issue = {}
    for r in cur.fetchall():
        votes_by_issue.setdefault(r["issue_id"], {})[judge_names[r["judge_id"]]] = r

    print("\n════════════════════════════════════════════════════════════════════")
    print(" 2. CALIBRATION SAMPLE EVALUATION (90 issues, Attempt 2)")
    print("════════════════════════════════════════════════════════════════════")
    sample_covered = 0
    match_a = 0
    match_b = 0
    both_match = 0

    evaluated = []
    for row in sample_issues:
        iid = row["id"]
        band, cross, rule = classify_issue_deterministically(
            row, labels_by_issue.get(iid, []), xrefs_by_issue.get(iid, [])
        )
        v_row_a = votes_by_issue.get(iid, {}).get("judge-a")
        v_row_b = votes_by_issue.get(iid, {}).get("judge-b")
        va = v_row_a["band"] if v_row_a else None
        vb = v_row_b["band"] if v_row_b else None

        if band is not None:
            sample_covered += 1
            ok_a = (band == va)
            ok_b = (band == vb)
            if ok_a: match_a += 1
            if ok_b: match_b += 1
            if ok_a and ok_b: both_match += 1
            evaluated.append((row["slug"], row["number"], band, rule, va, vb))

    print(f"  Total sample:                              90 issues")
    print(f"  Classified by deterministic rule:          {sample_covered} ({100.0 * sample_covered / 90:.1f}%)")
    print(f"  Residual grey-area left for LLM:           {90 - sample_covered} ({100.0 * (90 - sample_covered) / 90:.1f}%)\n")
    print(f"  Rule agreement with Judge A:               {match_a}/{sample_covered} ({100.0 * match_a / sample_covered:.1f}%)")
    print(f"  Rule agreement with Judge B:               {match_b}/{sample_covered} ({100.0 * match_b / sample_covered:.1f}%)")
    print(f"  Cases where BOTH judges agreed with rule:  {both_match}/{sample_covered} ({100.0 * both_match / sample_covered:.1f}%)")

    print("\n  Sample deterministic classification vs judges:")
    for slug, num, r_band, rule, va, vb in evaluated[:10]:
        status = "✔" if va == r_band and vb == r_band else "~"
        print(f"    [{status}] {slug:12s} #{num:<4d} -> {r_band} ({rule:35s}) | Judge A: {va} | Judge B: {vb}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 2. Test Suite: `test_rules.py` & Execution Output

Fuente: `test_rules.py @ 573c732`

```python
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
  9. Dynamic Dataset Snapshot verification (loads issues.json and verifies dynamic calculation)

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

    # 1. P0 POSITIVE CASES
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

    # 2. P0 NEGATIVE SAFEGUARDS
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

    # 3. P1 POSITIVE CRASH CASES
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

    # 4. RULE H9 vs H10 DEMOTION
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

    # 5. WORKAROUND NEGATION
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

    # 6. OVERFIT PATTERN ELIMINATION
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

    # 7. P2 FEATURES & P3 CHORES
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

    # 8. GREY-AREA FALL-THROUGH
    print("\n── 8. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──")
    grey_cases = [
        {"title": "button alignment is slightly off in Safari", "body": "Visual bug", "title_prefix": "bug", "labels": ["bug"]},
        {"title": "search results return in unexpected order", "body": "Sorting issue", "title_prefix": "bug", "labels": ["bug"]},
        {"title": "intermittent latency spike during peak load", "body": "Performance issue", "title_prefix": "bug", "labels": ["bug"]},
    ]
    for tc in grey_cases:
        band, _, rule = classify_issue_deterministically(tc, tc.get("labels", []), [])
        assert_test(band is None and rule is None, f"Grey area -> Indeterminate: '{tc['title'][:40]}'")

    # 9. DYNAMIC DATASET SNAPSHOT VERIFICATION
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
```

### Exact Test Runner Output:

```text
════════════════════════════════════════════════════════════════════
 RUNNING DETERMINISTIC RULES TEST SUITE (test_rules.py)
════════════════════════════════════════════════════════════════════

── 1. P0 POSITIVE CASES (Silent Data Loss & Corruption) ──
  ✔ [PASS] P0 positive: 'silently dropped rows during migration'
  ✔ [PASS] P0 positive: 'silently corrupted the db on shutdown'
  ✔ [PASS] P0 positive: 'silently lost data when buffer overflowed'
  ✔ [PASS] P0 positive: 'silently overwrites files without prompt'
  ✔ [PASS] P0 positive: 'panic: silently dropped rows'
  ✔ [PASS] P0 positive: 'unexpected data loss during table flush'
  ✔ [PASS] P0 positive: 'engine silently fails to save configuration'

── 2. P0 NEGATIVE SAFEGUARDS (Negations must NOT trigger P0) ──
  ✔ [PASS] P0 negative safe: 'this feature ensures no data loss during migr' -> None (not P0)
  ✔ [PASS] P0 negative safe: 'prevents data loss when disk is full' -> None (not P0)
  ✔ [PASS] P0 negative safe: 'avoid data loss by flushing WAL immediately' -> None (not P0)
  ✔ [PASS] P0 negative safe: 'system completes transaction without data los' -> None (not P0)
  ✔ [PASS] P0 negative safe: 'guarantees zero data loss replication' -> None (not P0)
  ✔ [PASS] P0 negative safe: 'safeguard against data loss on unexpected reb' -> None (not P0)

── 3. P1 POSITIVE CRASH CASES (Hard Crashes without Workaround) ──
  ✔ [PASS] P1 positive: 'panic: runtime error: index out of range'
  ✔ [PASS] P1 positive: 'fatal error: runtime: out of memory'
  ✔ [PASS] P1 positive: 'SIGSEGV in worker process on boot'
  ✔ [PASS] P1 positive: 'segmentation fault when dereferencing null po'
  ✔ [PASS] P1 positive: 'NullPointerException in MessageHandler'
  ✔ [PASS] P1 positive: 'uncaught exception terminated thread'
  ✔ [PASS] P1 positive: 'deadlock in transaction coordinator'
  ✔ [PASS] P1 positive: 'stack overflow during recursive traversal'

── 4. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──
  ✔ [PASS] Crash + Workaround demoted to P2: 'panic: runtime error: index out of ' + 'Workaround: run with --disable-cach'
  ✔ [PASS] Crash + Workaround demoted to P2: 'SIGSEGV on startup when config is m' + 'Temporary fix: touch config.json be'
  ✔ [PASS] Crash + Workaround demoted to P2: 'fatal error: runtime deadlock in po' + 'Recovers upon retry when worker poo'
  ✔ [PASS] Crash + Workaround demoted to P2: 'NullPointerException in sync loop' + 'Restart fixes the issue temporarily'

── 5. WORKAROUND NEGATION (Explicit 'No Workaround' -> Remains P1) ──
  ✔ [PASS] Crash + Negated Workaround remains P1: 'panic: runtime error: nil dereferen' + 'Workaround: none. The daemon immedi'
  ✔ [PASS] Crash + Negated Workaround remains P1: 'SIGSEGV on boot in initialization r' + 'No workaround available. Completely'
  ✔ [PASS] Crash + Negated Workaround remains P1: 'fatal error: runtime: out of memory' + 'Without any workaround; all attempt'
  ✔ [PASS] Crash + Negated Workaround remains P1: 'NullPointerException in parser' + 'Workaround: n/a. Issue is reproduci'

── 6. OVERFIT PATTERN ELIMINATION (Generalized / Removed) ──
  ✔ [PASS] Overfit pattern does not trigger P1: 'busy-loop on frozen review session' -> band=None
  ✔ [PASS] Overfit pattern does not trigger P1: 'dead-end encountered in review lineage' -> band=None

── 7. P2 FEATURES & P3 CHORES / DOCUMENTATION ──
  ✔ [PASS] Feature -> P2: 'feat(core): add streaming support'
  ✔ [PASS] Feature -> P2: 'add dark mode to user interface'
  ✔ [PASS] Feature -> P2: 'type:feature - support PostgreSQL'
  ✔ [PASS] Docs/Chore -> P3: 'docs: update getting started guide'
  ✔ [PASS] Docs/Chore -> P3: 'chore: bump dependencies to latest'
  ✔ [PASS] Docs/Chore -> P3: 'typo in configuration documentation'
  ✔ [PASS] Docs/Chore -> P3: 'question: how to configure custom port'

── 8. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──
  ✔ [PASS] Grey area -> Indeterminate: 'button alignment is slightly off in Safa'
  ✔ [PASS] Grey area -> Indeterminate: 'search results return in unexpected orde'
  ✔ [PASS] Grey area -> Indeterminate: 'intermittent latency spike during peak l'

── 9. DYNAMIC DATASET SNAPSHOT VERIFICATION (issues.json) ──
  ✔ [PASS] Snapshot file exists at /home/rafael/proyectos/Gentle-AI-Maintainer-Assistant/issues.json
  ✔ [PASS] Snapshot contains exactly 1,228 open issues (found 1228)
  ✔ [PASS] Dynamic calculation on snapshot yields exactly 491 resolved issues (40.0%)
  ✔ [PASS] rule:feature_request matches exactly 415 issues
  ✔ [PASS] rule:docs_chore_question matches exactly 52 issues
  ✔ [PASS] rule:silent_data_loss matches exactly 17 issues
  ✔ [PASS] rule:hard_crash matches exactly 7 issues

────────────────────────────────────────────────────────────────────
 FINAL TEST RESULT: 48/48 tests passed successfully.
════════════════════════════════════════════════════════════════════
```

---

## 3. Policy & Triage Model (`docs/triage-model.md` Literal Copy)

### The 13 Triage Dimensions

| # | Dimension | What it is | Pass | Values |
| --- | --- | --- | --- | --- |
| D1 | **issue type** | what kind of request this is | 1 | bug · feature · question · docs · chore · unknown |
| D2 | **affected component** | which part of which system | 1–2 | `owner/repo` + component, or `unknown` |
| D3 | **scope** | how wide the effect is inside its system | 1–2 | single · component · system · unknown |
| D4 | **impact** | what stops working, and for whom | 1–2 | blocks use · degrades · cosmetic · unknown |
| D5 | **severity** | how bad it is when it happens | 2 | high · medium · low · unknown |
| D6 | **urgency** | how soon it must be addressed | 1–2 | now · soon · whenever · unknown |
| D7 | **reproducibility** | can the reporter's case be reproduced | 2 | reproducible · partial · not-reproducible · unknown |
| D8 | **completeness** | does the report contain what the template asked for | 1 | complete · partial · insufficient |
| D9 | **dependencies** | what this needs, and what needs this | 1–2 | list of references, or `none` |
| D10 | **relationships** | links to other issues or other systems | 1 | list of `owner/repo#n`, or `none` |
| D11 | **blocking status** | whether it blocks other work | 2 | blocks · blocked-by · free · unknown |
| D12 | **confidence** | how sure the assistant is | 1–2 | high · medium · low |
| D13 | **evidence** | the citation that supports the claim | 1–2 | issue text · comment · file:line · label |

*Note on Pass 1 Honesty:* D5 (severity), D7 (reproducibility), and D11 (blocking status) are strictly unobservable a priori. In Pass 1 they are recorded as `unknown`.

### The 10 Hard Governance Rules (H1–H10)

| # | Rule | Literal Definition |
| --- | --- | --- |
| **H1** | Cross-System Implication | Cross-system implication alone never promotes a band. Only patterns (a) and (b) do. |
| **H2** | Mandatory Evidence | A band is never emitted without at least one reason and at least one citation. |
| **H3** | Inference Discipline | A band is always inference. Confidence is mandatory. Low confidence is a valid, expected outcome. |
| **H4** | Independent Causes | Pattern (c) must be split into separate issues, never promoted as one. |
| **H5** | Cosmetic Reach | Pattern (d) never promotes. Reach is not harm. |
| **H6** | Unknown Preservation | A missing dimension is `unknown`. It is never inferred silently to complete a band. |
| **H7** | Maintainer Authority | A maintainer override always wins and is recorded as a decision. |
| **H8** | Provisional Pass 1 | Pass-1 bands are provisional. Pass 2 may correct them, and the correction is recorded. |
| **H9** | Workaround & Retry (P1 vs P2) | If a documented or accessible manual workaround exists, or if the failure is intermittent and recovers upon retry, the issue **MUST** be classified as P2, never P1. P1 is strictly reserved for dead-ends with no viable escape hatch. |
| **H10** | Code > LLM Pre-Filter | Issues matching unambiguous structural patterns (`feat:` prefix -> P2, `docs:`/`chore:` -> P3, `panic:`/`SIGSEGV` -> P1, `silent corruption` -> P0) are classified deterministically by code without invoking an LLM. |

---

## 4. Architectural Analysis: Rule Conflict Resolution & Overfitting Audit

### A. Resolution of the Rule H9 vs Rule H10 Conflict
* **The Conflict:** Rule H10 previously stated that structural crash tokens (`panic:`, `SIGSEGV`) map directly to P1 via code. Rule H9 requires that any issue with an accessible manual workaround or retry recovery must be demoted to P2. Under naive regex matching, an issue with `panic: ... Workaround: run with --flag` would incorrectly be assigned P1 by Rule H10, violating Rule H9.
* **The Architectural Decision:** Rule H10 is subordinate to Rule H9's operational boundary. In `db/rules.py`:
  1. If an issue matches `RE_P1_CRASH`, the engine immediately inspects the issue text for workaround patterns (`RE_WORKAROUND_POSITIVE`) and retry recovery phrases.
  2. If an active workaround or retry recovery is present, the issue is deterministically assigned **P2** with rule `rule:crash_with_workaround_demoted_to_p2`.
  3. P1 (`rule:hard_crash`) is assigned **ONLY IF no workaround or retry recovery is detected**.
  4. Crucially, explicit declarations of the *absence* of a workaround (`workaround: none`, `no workaround available`, `without any workaround`) are recognized via `RE_WORKAROUND_NEGATIVE` to ensure they are **NOT** falsely treated as workarounds. They strictly remain **P1**.

### B. Elimination and Generalization of Overfitted Regex Patterns
During initial prototyping, two patterns were introduced that exhibited severe overfitting:
1. `dead-end.*lineage`: "Lineage" is an internal domain-specific concept of the `gentle-ai` review architecture. Matching "dead-end in lineage" was tailored to specific historical bug tickets in one repository. **Action:** Completely removed.
2. `busy-loop.*frozen`: An informal, colloquial phrase that matched a specific historical bug report but is neither a standard runtime signal nor a reliable architectural invariant. **Action:** Completely removed.
* **Replacement:** We generalized crash and stall detection to standard operating system signals, runtime panics, and concurrency deadlocks:
  `(?:\bpanic:\s*|\bSIGSEGV\b|\bfatal error:\s*runtime\b|\bsegmentation fault\b|\bNullPointerException\b|\buncaught exception\b|\bdeadlock(?:ed)?\b|\bstack overflow\b)`.

---

## 5. Metrics Methodology & Empirical Provenance

This section provides strict provenance for every metric cited in the project.

| Metric | Exact Value | Evaluated Scope | Ground Truth / Labeler | Evaluation vs Design Set Relationship |
| --- | --- | --- | --- | --- |
| **Backlog Deterministic Coverage** | **40.0%** (491 / 1,228) | All 1,228 open issues in `db/exp.db` and `issues.json` (`gentle-ai`: 733, `gentle-shell`: 424, `engram`: 71). | Calculated dynamically from issue titles, prefixes, labels, and bodies. | **Total population census.** Evaluated on all open issues across the three repositories. |
| **Deterministic Precision vs Judge A** | **94.1%** (32 / 34) | Stratified calibration sample of 90 issues (Run #1, hash `e049b162`), where 34 matched the calibrated rules. | Blind LLM Judge A (`minimax/MiniMax-M3`, Run #1 Attempt 2). | **Calibration sample.** Note: this 90-issue sample was used during heuristic calibration. Held-out test validation is planned for Phase 3. |
| **Deterministic Precision vs Judge B** | **85.3%** (29 / 34) | Same 34 matched issues from the 90-issue sample. | Blind LLM Judge B (`nan/deepseek-v4-flash`, Run #1 Attempt 2). | **Calibration sample.** Divergences stem from cosmetic features where Judge B preferred P3 while rules assigned P2 (`feat:`). |
| **Both Judges Match Deterministic Rule** | **85.3%** (29 / 34) | Same 34 matched issues from the 90-issue sample. | Both Judge A and Judge B independently concurred with the rule. | **Calibration sample.** In 0 of 34 cases did any judge assign P0 or P1 to a feature request. |
| **Feature Request P2 Precision** | **100.0%** vs P0/P1 (28 / 28) | 28 feature requests in the 90-issue sample matched by `rule:feature_request`. | Judge A: 28/28 (100% P2). Judge B: 24/28 P2, 4/28 P3. **0/28 (0%) assigned P0 or P1.** | **Calibration sample.** Confirms that feature requests never cause false high-priority alarms. |
| **Lexical Keyword Matching Precision** | **7.4%** (15 / 202) | In `gentle-shell`, 202 issues mention `"gentle-ai"` in text; only 15 have confirmed cross-system links in `cross_refs`. | SQL join of FTS text occurrences vs canonical foreign issue references. | **Total population census in `gentle-shell`.** Demonstrates why pure keyword search fails due to internal path collisions (`extensions/gentle-ai.ts`, `.git/gentle-ai/`). |

---

## 6. Empirical Verification: 20 Real Issues from `db/exp.db`

Below are 20 concrete issues drawn directly from SQLite (`db/exp.db`), showing the deterministic rule applied, the resulting priority band, and the independent verdicts of Judge A (`MiniMax-M3`) and Judge B (`DeepSeek-V4-Flash`):

| Issue Identifier | Issue Title | Rule Applied | Assigned Priority | Judge A Verdict | Judge B Verdict |
| --- | --- | --- | --- | --- | --- |
| `gentle-ai#5166` | `bug(review): a lens admitted a CRITICAL TS6306 "mi` | `rule:hard_crash` | **P1** | P1 | P1 |
| `gentle-ai#4823` | `feat(pi): support opt-in community plugin discover` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#3794` | `feat(review): add a candidate-bound cacheable deli` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#3580` | `feat(pi): apply validated model-routing drafts` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#3258` | `test(cli): cover the host-mediated refusal for rev` | `rule:docs_chore_question` | **P3** | P3 | P3 |
| `gentle-ai#3022` | `feat(workflow): stop stagnant non-SDD verification` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#2423` | `refactor(review): delete orphaned review authority` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#2123` | `feat(sync): preserve user customizations in manage` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#1973` | `feat(review): scope the RDD kill switch per worktr` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#1866` | `feat(ci): continuously verify and bind benchmark r` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#1308` | `feat(review): require candidate-bound evidence for` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#1286` | `feat(skills): add verifiable skill loading and com` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#1051` | `feat(context-pruning): integrate dynamic context p` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-ai#858` | `feat(tui): add compact OpenAI quota indicator` | `rule:feature_request` | **P2** | P2 | P2 |
| `engram#1501` | `feat(ci): recognize cross-repository issue referen` | `rule:feature_request` | **P2** | P2 | P2 |
| `engram#1461` | `Allow omitted or empty session directory metadata ` | `rule:feature_request` | **P2** | P2 | P2 |
| `engram#1372` | `feat(pi): honor mem_save capture_prompt associatio` | `rule:feature_request` | **P2** | P2 | P2 |
| `engram#1351` | `feat(store): make session closure replay-safe` | `rule:feature_request` | **P2** | P2 | P2 |
| `engram#904` | `feat(sync): define recovery semantics for incomple` | `rule:feature_request` | **P2** | P2 | P2 |
| `gentle-shell#1309`| `gentle-ai-worker edit surfaces resolve only agains`| `rule:feature_request` | **P2** | P2 | P2 |

---

## 7. Known Limitations & What is NOT Yet Validated

To maintain strict scientific and technical honesty, the following boundaries must be explicitly noted:

1. **Residual 60.0% Grey Area Backlog Evaluation:**
   * While the deterministic rules engine was evaluated across all 1,228 issues, the full two-pass LLM pipeline has only been run on the 90-issue sample (Run #1).
   * The remaining 737 open issues requiring LLM inference have not yet been evaluated end-to-end.
2. **No Autonomous GitHub Mutations:**
   * In strict accordance with the non-negotiable principles, the assistant has zero GitHub mutation authority. No labels, comments, transfers, or closures have been applied to live GitHub repositories.
3. **Longitudinal Maintainer Study:**
   * Human maintainer acceptance and override rates over extended operational periods (e.g. 30 days of active triaging) have not yet been measured.
4. **Generalization Beyond Conventional Commits:**
   * The deterministic engine achieves 40% coverage primarily because the Gentle-AI ecosystem widely adheres to Conventional Commits (`feat:`, `docs:`, `fix:`). In repositories without commit discipline, deterministic coverage would be lower and rely more heavily on LLM Pass 1.
5. **Cross-System Link Ground Truth:**
   * Only 55 explicit cross-repository references are currently indexed in `cross_refs`. While Asymmetric Escrow is modeled and schemas are validated, cross-repository routing precision in the wild remains to be verified upon live testing.
