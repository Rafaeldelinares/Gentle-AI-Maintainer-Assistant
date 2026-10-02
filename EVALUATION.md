# EVALUATION.md — External Audit & Technical Verification Guide

> **Self-contained evaluation artifact for external technical auditors.**
> This document allows complete inspection and validation of the Gentle AI Maintainer Assistant proposal without requiring directory navigation or repository cloning.
>
> **Governance invariant:** a deterministic silent-data-loss match is emitted strictly as **`candidato P0, requiere revisión humana`** (candidate P0 requiring human review), never as a final P0 decision.

---

## 1. Source Code: `db/rules.py`

Fuente: `db/rules.py`

```python
#!/usr/bin/env python3
"""
rules.py — Deterministic triage rule engine for the Gentle AI ecosystem

Applies code-based heuristics BEFORE invoking an LLM:
  1. Features / enhancements -> P2 (rule:feature_request)
  2. Docs / chores / questions -> P3 (rule:docs_chore_question)
  3. Silent data loss / corruption -> candidato P0, requiere revisión humana (rule:candidato_p0_requiere_revision_humana)
  4. Panic / SIGSEGV / hard crash without workaround -> P1 (rule:hard_crash)
  5. Crash WITH documented workaround / retry -> P2 (rule:crash_with_workaround_demoted_to_p2)
  6. Cross-repository links (cross_refs) -> cross classification

Governance Invariants:
  - Deterministic P0 is strictly a candidate ("candidato P0, requiere revisión humana"), never an autonomous final decision.
  - Negations ("no data loss", "without data loss", "is not a deadlock") and fix descriptions ("from being silently dropped to being rejected") never trigger high-priority rules.
  - Deadlocks require process or thread context (goroutine, thread, mutex, process, hang); metaphorical deadlocks ("two rules deadlock") are ignored.

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

# Label constants
P0_CANDIDATE_LABEL = "candidato P0, requiere revisión humana"
RULE_P0_CANDIDATE = "rule:candidato_p0_requiere_revision_humana"

# 1. P0: Silent data loss & corruption base pattern
RE_P0_SILENT_BASE = re.compile(
    r"(?:\bsilent(?:ly)?\s+(?:corrupt(?:s|ed|ing|ion)?|delet(?:es|ed|ing|ion)?|drop(?:s|ped|ping)?|overwrit(?:es|ing)?|overwrote|overwritten|los(?:es|t|ing)?|fail(?:s|ed|ing)?\s+to\s+save)\b|\bdata\s+loss\b)",
    re.IGNORECASE,
)

# Negation safeguards for data loss (e.g. 'no data loss', 'without data loss', 'not data loss', 'zero data loss')
RE_DATA_LOSS_NEGATION = re.compile(
    r"\b(?:no|not|without|zero|neither|nor|prevent(?:s|ed|ing)?|avoid(?:s|ed|ing)?|protect(?:s|ed|ing)?\s+against|safeguard(?:s|ed|ing)?\s+against)\b[^.\n;]{0,60}?\bdata\s+loss\b|"
    r"\bdata\s+loss\b[^.\n;]{0,50}?\b(?:is\s+(?:claimed|none)|avoided|prevented|not\s+observed|not\s+found)\b",
    re.IGNORECASE,
)

# Descriptions of fixes or transitions (e.g. 'from being silently dropped to being rejected')
RE_FIX_DESCRIPTION = re.compile(
    r"\bfrom\s+being\s+silent(?:ly)?\s+(?:corrupt|delet|drop|overwrit|los)\w*\s+to\s+being\b|"
    r"\b(?:prevent(?:s|ed|ing)?|fixed|stops?|stopped|protected)\s+(?:\w+\s+){0,5}from\s+being\s+silent",
    re.IGNORECASE,
)

# General silent negation
RE_SILENT_NEGATION = re.compile(
    r"\b(?:no|not|without|zero)\s+(?:silent(?:ly)?\s+)?(?:data\s+loss|corruption)\b",
    re.IGNORECASE,
)

# 2. P1: Hard crashes core runtime errors
RE_P1_CRASH_CORE = re.compile(
    r"(?:\bpanic:\s*|\bSIGSEGV\b|\bfatal error:\s*runtime\b|\bsegmentation fault\b|\bNullPointerException\b|\buncaught exception\b|\bstack overflow\b)",
    re.IGNORECASE,
)

# Deadlock base pattern
RE_DEADLOCK_BASE = re.compile(r"\bdeadlock(?:ed|s)?\b", re.IGNORECASE)

# Negation for deadlock (e.g. 'is not a deadlock', 'not a deadlock')
RE_DEADLOCK_NEGATION = re.compile(
    r"\b(?:not|never|is\s+not|hardly)\s+(?:a\s+)?deadlock\b",
    re.IGNORECASE,
)

# Process or thread concurrency context required for deadlock to be a real crash
RE_CONCURRENCY_CONTEXT = re.compile(
    r"\b(?:goroutines?|threads?|mutex(?:es)?|locks?|process(?:es)?|hangs?|hanging|workers?)\b",
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


def has_silent_data_loss(text: str) -> bool:
    """
    Returns True if text reports an unnegated silent data loss or corruption event.
    Rejects negations ('no data loss', 'without data loss') and fix descriptions.
    """
    for m in RE_P0_SILENT_BASE.finditer(text):
        matched = m.group(0).lower()
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 80)
        window = text[start:end]

        # Reject fix descriptions ('from being silently dropped to being rejected')
        if RE_FIX_DESCRIPTION.search(window):
            continue

        # Reject data loss negations
        if "data loss" in matched:
            if RE_DATA_LOSS_NEGATION.search(window):
                continue

        # Reject general silent negations
        if RE_SILENT_NEGATION.search(window):
            continue

        return True
    return False


def is_hard_crash(text: str) -> bool:
    """
    Returns True if text reports a hard runtime crash (SIGSEGV, panic, stack overflow)
    or a concurrency deadlock with explicit thread/process/mutex/hang context.
    Rejects 'not a deadlock' and metaphorical deadlocks ('two rules deadlock each other').
    """
    if RE_P1_CRASH_CORE.search(text):
        return True

    for m in RE_DEADLOCK_BASE.finditer(text):
        start = max(0, m.start() - 60)
        end = min(len(text), m.end() + 60)
        window = text[start:end]

        if RE_DEADLOCK_NEGATION.search(window):
            continue
        if RE_CONCURRENCY_CONTEXT.search(window):
            return True

    return False


def classify_issue_deterministically(row, labels, cross_refs):
    """
    Returns (band, cross, rule_name) or (None, cross, None) if indeterminate.
    
    Invariant: P0 is strictly 'candidato P0, requiere revisión humana', never a final decision.
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

    # Check P0: Silent data loss / corruption -> Candidate P0, requires human review
    if is_bug and has_silent_data_loss(full_text):
        return P0_CANDIDATE_LABEL, cross, RULE_P0_CANDIDATE

    # Check P1 vs P2 (Rule H9 & H10): Hard crash / fatal engine stall
    if is_bug and is_hard_crash(full_text):
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
        print(f"    - {rule:42s}: {cnt:4d} issues ({pct:.1f}%)")
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
        print(f"    - {rule:42s}: {cnt:4d} issues ({100.0 * cnt / total_all:.1f}%)")

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
            eval_band = "P0" if "P0" in band else band
            ok_a = (eval_band == va)
            ok_b = (eval_band == vb)
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
        display_band = "P0 (candidato)" if "P0" in r_band else r_band
        eval_band = "P0" if "P0" in r_band else r_band
        status = "✔" if va == eval_band and vb == eval_band else "~"
        print(f"    [{status}] {slug:12s} #{num:<4d} -> {display_band:16s} ({rule:40s}) | Judge A: {va} | Judge B: {vb}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 2. Test Suite: `test_rules.py` & Execution Output

Fuente: `test_rules.py`

```python
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
```

### Exact Test Runner Output

```text
════════════════════════════════════════════════════════════════════
 RUNNING DETERMINISTIC RULES TEST SUITE (test_rules.py)
════════════════════════════════════════════════════════════════════

── 1. P0 CANDIDATE POSITIVES (Silent Data Loss & Corruption) ──
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'silently dropped rows during migration'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'silently corrupted the db on shutdown'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'silently lost data when buffer overflowed'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'silently overwrites files without prompt'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'panic: silently dropped rows'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'unexpected data loss during table flush'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'engine silently fails to save configuration'
  ✔ [PASS] candidate P0 via rule:candidato_p0_requiere_revision_humana: 'A corrupt custom-agents.json silently drops the re'

── 2. P0 NEGATION SAFEGUARDS (Negations must NOT trigger P0) ──
  ✔ [PASS] negated data loss not flagged: 'this feature ensures no data loss during migration' -> None
  ✔ [PASS] negated data loss not flagged: 'prevents data loss when disk is full' -> None
  ✔ [PASS] negated data loss not flagged: 'avoid data loss by flushing WAL immediately' -> None
  ✔ [PASS] negated data loss not flagged: 'system completes transaction without data loss' -> None
  ✔ [PASS] negated data loss not flagged: 'guarantees zero data loss replication' -> None
  ✔ [PASS] negated data loss not flagged: 'safeguard against data loss on unexpected reboot' -> None
  ✔ [PASS] negated data loss not flagged: 'no data loss on this path' -> None
  ✔ [PASS] negated data loss not flagged: 'the run completes without data loss' -> None
  ✔ [PASS] negated data loss not flagged: 'this is not data loss' -> None

── 3. FIX-DESCRIPTION REJECTION (Describing a fix is not a defect) ──
  ✔ [PASS] fix description is not silent data loss: 'changed unknown agents from being silently dropped'
  ✔ [PASS] fix description is not silent data loss: 'prevents records from being silently dropped'

── 4. REAL-ISSUE REGRESSION CASES (#5007, #4792, #4807, #2628) ──
  ✔ [PASS] issue #5007 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] issue #4792 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] issue #4807 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] issue #2628 is not flagged as candidate P0 / P1 -> band=None

── 5. P1 HARD CRASH POSITIVES (No workaround) ──
  ✔ [PASS] P1 positive: 'panic: runtime error: index out of range'
  ✔ [PASS] P1 positive: 'fatal error: runtime: out of memory'
  ✔ [PASS] P1 positive: 'SIGSEGV in worker process on boot'
  ✔ [PASS] P1 positive: 'segmentation fault when dereferencing null pointer'
  ✔ [PASS] P1 positive: 'NullPointerException in MessageHandler'
  ✔ [PASS] P1 positive: 'uncaught exception terminated thread'
  ✔ [PASS] P1 positive: 'stack overflow during recursive traversal'
  ✔ [PASS] P1 positive: 'fatal error: all goroutines are asleep - deadlock!'
  ✔ [PASS] P1 positive: 'worker thread enters deadlock when acquiring mutex'
  ✔ [PASS] P1 positive: 'process hangs due to deadlock in event loop'

── 6. DEADLOCK REQUIRES PROCESS/THREAD CONTEXT (Metaphors rejected) ──
  ✔ [PASS] deadlock without concurrency context rejected: 'It is a fork bomb, not a deadlock.'
  ✔ [PASS] deadlock without concurrency context rejected: 'This is not a deadlock situation'
  ✔ [PASS] deadlock without concurrency context rejected: 'The two rules deadlock each other.'
  ✔ [PASS] deadlock without concurrency context rejected: 'ordinary review denials deadlock the agent'
  ✔ [PASS] deadlock without concurrency context rejected: 'the review is deadlocked'
  ✔ [PASS] deadlock without concurrency context rejected: 'sdd-remediate run can deadlock before phase work'
  ✔ [PASS] real concurrency deadlock accepted: 'fatal error: all goroutines are asleep - deadlock!'
  ✔ [PASS] real concurrency deadlock accepted: 'mutex deadlock detected in worker pool'
  ✔ [PASS] real concurrency deadlock accepted: 'thread deadlock on channel receive'

── 7. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──
  ✔ [PASS] crash + workaround demoted to P2: 'panic: runtime error: index out of ' + 'Workaround: run with --disable-cach'
  ✔ [PASS] crash + workaround demoted to P2: 'SIGSEGV on startup when config is m' + 'Temporary fix: touch config.json be'
  ✔ [PASS] crash + workaround demoted to P2: 'fatal error: runtime deadlock in po' + 'Recovers upon retry when worker poo'
  ✔ [PASS] crash + workaround demoted to P2: 'NullPointerException in sync loop' + 'Restart fixes the issue temporarily'

── 8. WORKAROUND NEGATION (Explicit 'No Workaround' -> Remains P1) ──
  ✔ [PASS] crash + negated workaround remains P1: 'panic: runtime error: nil dereferen' + 'Workaround: none. The daemon immedi'
  ✔ [PASS] crash + negated workaround remains P1: 'SIGSEGV on boot in initialization r' + 'No workaround available. Completely'
  ✔ [PASS] crash + negated workaround remains P1: 'fatal error: runtime: out of memory' + 'Without any workaround; all attempt'
  ✔ [PASS] crash + negated workaround remains P1: 'NullPointerException in parser' + 'Workaround: n/a. Issue is reproduci'

── 9. OVERFIT PATTERN ELIMINATION (Generalized / Removed) ──
  ✔ [PASS] overfit pattern does not trigger P1: 'busy-loop on frozen review session' -> band=None
  ✔ [PASS] overfit pattern does not trigger P1: 'dead-end encountered in review lineage' -> band=None

── 10. P2 FEATURES & P3 CHORES / DOCUMENTATION ──
  ✔ [PASS] feature -> P2: 'feat(core): add streaming support'
  ✔ [PASS] feature -> P2: 'add dark mode to user interface'
  ✔ [PASS] feature -> P2: 'type:feature - support PostgreSQL'
  ✔ [PASS] docs/chore -> P3: 'docs: update getting started guide'
  ✔ [PASS] docs/chore -> P3: 'chore: bump dependencies to latest'
  ✔ [PASS] docs/chore -> P3: 'typo in configuration documentation'
  ✔ [PASS] docs/chore -> P3: 'question: how to configure custom port'

── 11. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──
  ✔ [PASS] grey area -> indeterminate: 'button alignment is slightly off in Safa'
  ✔ [PASS] grey area -> indeterminate: 'search results return in unexpected orde'
  ✔ [PASS] grey area -> indeterminate: 'intermittent latency spike during peak l'

── 12. SNAPSHOT SELF-CONSISTENCY (issues.json, dynamic) ──
  ✔ [PASS] Snapshot file issues.json exists
  ✔ [PASS] Snapshot is non-empty (found 1228 issues)
  ✔ [PASS] snapshot contains gentle-ai#5007
  ✔ [PASS] snapshot regression gentle-ai#5007 not candidate P0/P1 -> band=None
  ✔ [PASS] snapshot contains gentle-ai#4792
  ✔ [PASS] snapshot regression gentle-ai#4792 not candidate P0/P1 -> band=None
  ✔ [PASS] snapshot contains gentle-ai#4807
  ✔ [PASS] snapshot regression gentle-ai#4807 not candidate P0/P1 -> band=None
  ✔ [PASS] snapshot contains gentle-ai#2628
  ✔ [PASS] snapshot regression gentle-ai#2628 not candidate P0/P1 -> band=None
  ✔ [PASS] snapshot contains gentle-ai#4917
  ✔ [PASS] snapshot gentle-ai#4917 is a candidate P0, not a final decision (band='candidato P0, requiere revisión humana')
  ✔ [PASS] dynamic snapshot classification is reproducible across passes
  ✔ [PASS] deterministic engine covers at least one snapshot issue (483 covered)
  ✔ [PASS] candidate P0 rule is exercised on the snapshot (14 candidates)

  Dynamic rule histogram over issues.json (recomputed, not frozen):
    - rule:feature_request                        :  415
    - rule:docs_chore_question                    :   52
    - rule:candidato_p0_requiere_revision_humana  :   14
    - rule:hard_crash                             :    2

────────────────────────────────────────────────────────────────────
 FINAL TEST RESULT: 77/77 tests passed successfully.
════════════════════════════════════════════════════════════════════
```

---

## 3. Contract Validation: `schemas/validate.py` Output

Fuente: `schemas/validate.py`

```text
════════════════════════════════════════════════════════════════════
 VALIDATING SCHEMAS & FIXTURES (Draft 2020-12)
════════════════════════════════════════════════════════════════════

✔ Schema syntax OK: issue-record.schema.json
    ✔ Valid fixture: issue-record.fixture.json
✔ Schema syntax OK: triage-inference.schema.json
    ✔ Valid fixture: triage-inference-deterministic.fixture.json
    ✔ Valid fixture: triage-inference-llm.fixture.json
    ✔ Valid fixture: triage-inference-p0-candidate.fixture.json
✔ Schema syntax OK: maintainer-decision.schema.json
    ✔ Valid fixture: maintainer-decision-accept.fixture.json
    ✔ Valid fixture: maintainer-decision-override.fixture.json
✔ Schema syntax OK: triage-batch-report.schema.json
    ✔ Valid fixture: triage-batch-report.fixture.json

════════════════════════════════════════════════════════════════════
 NEGATIVE TESTS (Verifying fail-closed behavior)
════════════════════════════════════════════════════════════════════

✔ Neg test 1 OK: deterministic_rule without rule_name is rejected as expected
✔ Neg test 2 OK: decision without human actor is rejected as expected
✔ Neg test 3 OK: invented band P4 is rejected as expected
✔ Neg test 4 OK: candidate P0 label requires rule:candidato_p0_requiere_revision_humana
✔ Neg test 5 OK: deterministic candidate rule cannot emit a final P0 band

────────────────────────────────────────────────────────────────────
 FINAL RESULT: 12/12 tests passed successfully.
════════════════════════════════════════════════════════════════════
```

The schema enforces the governance invariant **bidirectionally**: `band == "candidato P0, requiere revisión humana"` requires `source == "deterministic_rule"` and `rule_name == "rule:candidato_p0_requiere_revision_humana"`; and that rule name requires the candidate band. A deterministic candidate rule cannot be published as a final `P0` band, and a candidate P0 label cannot be attached to a non-candidate rule.

---

## 4. Triage Model: 13 Dimensions & Rules H1–H10

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
| **H10** | Code > LLM Pre-Filter | Issues matching unambiguous structural patterns (`feat:` -> P2, `docs:`/`chore:` -> P3, `panic:`/`SIGSEGV` -> P1, silent corruption -> **candidate P0 requiring human review**) are classified deterministically by code without invoking an LLM. |

---

## 5. Architectural Analysis: Negation Hardening, Deadlock Context & Overfitting Audit

### A. Resolution of the Rule H9 vs Rule H10 Conflict

* **The Conflict:** Rule H10 previously stated that structural crash tokens (`panic:`, `SIGSEGV`) map directly to P1 via code. Rule H9 requires that any issue with an accessible manual workaround or retry recovery must be demoted to P2. Under naive regex matching, an issue with `panic: ... Workaround: run with --flag` would incorrectly be assigned P1 by Rule H10, violating Rule H9.
* **The Architectural Decision:** Rule H10 is subordinate to Rule H9's operational boundary. In `db/rules.py`:
  1. If an issue matches `RE_P1_CRASH_CORE` or a genuine concurrency deadlock, the engine immediately inspects the issue text for workaround patterns (`RE_WORKAROUND_POSITIVE`) and retry recovery phrases.
  2. If an active workaround or retry recovery is present, the issue is deterministically assigned **P2** with rule `rule:crash_with_workaround_demoted_to_p2`.
  3. P1 (`rule:hard_crash`) is assigned **ONLY IF no workaround or retry recovery is detected**.
  4. Explicit declarations of the *absence* of a workaround (`workaround: none`, `no workaround available`, `without any workaround`) are recognized via `RE_WORKAROUND_NEGATIVE` and are **NOT** treated as workarounds. They strictly remain **P1**.

### B. Negation Hardening for Silent Data Loss (P0 candidate)

Naive matching produced false high-priority flags on issues that explicitly state the *absence* of loss, or that *describe a fix*. Four real issues exposed this:

| Issue | Trap text | Why it must not fire | Safeguard applied |
| --- | --- | --- | --- |
| `gentle-ai#5007` | `No workaround data loss: the local store is intact` | Explicitly states the state is preserved | `RE_DATA_LOSS_NEGATION` (`no ... data loss`) |
| `gentle-ai#4792` | `No observed runtime failure or data loss is claimed.` | Explicitly claims no data loss occurred | `RE_DATA_LOSS_NEGATION` (`no observed ... data loss`) |
| `gentle-ai#2628` | `from being silently dropped to being rejected` | Describes a fix (transition to a better behavior) | `RE_FIX_DESCRIPTION` (`from being silently ... to being`) |
| `gentle-ai#4807` | `It is a fork bomb, not a deadlock.` | Negated deadlock | `RE_DEADLOCK_NEGATION` (`not a deadlock`) |

### C. Deadlock Requires Process/Thread Context

The bare token `deadlock` matched metaphorical usages such as *"The two rules deadlock each other"* and *"ordinary review denials deadlock the agent"* — a logical impasse, not a runtime crash. The rule now requires explicit concurrency context (`goroutine`, `thread`, `mutex`, `lock`, `process`, `hang`, `worker`) within a bounded window of the token, and rejects explicit negation. Metaphorical deadlocks (`gentle-ai#4286`, `#2366`, `#5094`; `gentle-shell#1087`) no longer trigger P1.

### D. Elimination and Generalization of Overfitted Regex Patterns

During initial prototyping, two patterns were introduced that exhibited severe overfitting:

1. `dead-end.*lineage`: "lineage" is an internal domain-specific concept of the `gentle-ai` review architecture. Matching "dead-end in lineage" was tailored to specific historical bug tickets in one repository. **Action:** Completely removed.
2. `busy-loop.*frozen`: An informal, colloquial phrase that matched a specific historical bug report but is neither a standard runtime signal nor a reliable architectural invariant. **Action:** Completely removed.

* **Replacement:** crash and stall detection was generalized to standard operating-system signals, runtime panics, and concurrency deadlocks: `panic:`, `SIGSEGV`, `fatal error: runtime`, `segmentation fault`, `NullPointerException`, `uncaught exception`, `stack overflow`, plus context-bound `deadlock`.

### E. Candidate-P0 Governance Invariant

The deterministic engine never declares a final P0. A silent-data-loss match is emitted as `candidato P0, requiere revisión humana` with rule `rule:candidato_p0_requiere_revision_humana`. The schema enforces this in both directions (Section 3), and the human-review gold set lives in `gold-p0-p1.md` with `veredicto_humano: pendiente`.

---

## 6. Metrics Methodology & Empirical Provenance

Every figure below is computed dynamically by `db/rules.py` and `test_rules.py`; no figure is hardcoded in the engine.

| Metric | Exact Value | Evaluated Scope | Ground Truth / Labeler | Evaluation vs Design Set Relationship |
| --- | --- | --- | --- | --- |
| **Backlog Deterministic Coverage** | **39.3%** (483 / 1,228) | All 1,228 open issues (`gentle-ai`: 733, `gentle-shell`: 424, `engram`: 71). | Calculated dynamically from titles, prefixes, labels, and bodies by `db/rules.py`. | **Total population census.** |
| **Residual Grey Area** | **60.7%** (745 / 1,228) | Same census. | Issues not matched by any deterministic rule; routed to LLM Pass 1. | **Total population census.** |
| **Candidate P0 (silent data loss)** | **14 issues** | Same census. | `rule:candidato_p0_requiere_revision_humana`. | **Candidates only.** Enumerated in `gold-p0-p1.md` with `veredicto_humano: pendiente`. |
| **P1 (hard crash, no workaround)** | **2 issues** | Same census. | `rule:hard_crash`. | **Candidates only.** Enumerated in `gold-p0-p1.md`. |
| **P2 (feature request)** | **415 issues** | Same census. | `rule:feature_request`. | **Total population census.** |
| **P3 (docs/chore/question)** | **52 issues** | Same census. | `rule:docs_chore_question`. | **Total population census.** |
| **Deterministic Precision vs Judge A** | **94.1%** (32 / 34) | Stratified calibration sample of 90 issues (Run #1), where 34 matched the calibrated rules. | Blind LLM Judge A (`minimax/MiniMax-M3`, Run #1 Attempt 2). | **Calibration sample.** This sample was used during heuristic calibration; out-of-sample validation is planned for Phase 3. |
| **Deterministic Precision vs Judge B** | **85.3%** (29 / 34) | Same 34 matched issues. | Blind LLM Judge B (`nan/deepseek-v4-flash`, Run #1 Attempt 2). | **Calibration sample.** Divergences stem from cosmetic features where Judge B preferred P3 while rules assigned P2 (`feat:`). |
| **Both Judges Match Deterministic Rule** | **85.3%** (29 / 34) | Same 34 matched issues. | Both judges independently concurred with the rule. | **Calibration sample.** In 0 of 34 cases did any judge assign P0 or P1 to a feature request. |
| **Lexical Keyword Matching Precision** | **7.4%** (15 / 202) | In `gentle-shell`, 202 issues mention `"gentle-ai"` in text; only 15 have confirmed cross-system links in `cross_refs`. | SQL join of FTS text occurrences vs canonical foreign issue references. | **Total population census in `gentle-shell`.** Demonstrates why pure keyword search fails due to internal path collisions (`extensions/gentle-ai.ts`, `.git/gentle-ai/`). |
| **Open issues without `priority:*` label** | **85.5%** (1,050 / 1,228) | Same census. | Label census over the sanitized snapshot. | **Total population census.** |
| **Open issues under `status:needs-review`** | **55.9%** (686 / 1,228) | Same census. | Label census over the sanitized snapshot. | **Total population census.** |

### Coverage Delta from Rule Hardening

Earlier, pre-fix rule versions reported 40.0% deterministic coverage (491 / 1,228) and 60.0% grey area (737 / 1,228). Applying the negation and deadlock-context safeguards removed **8 false positives** — 3 from the silent-data-loss class (`gentle-ai#5007`, `#4792`, `#2628`) and 5 from the deadlock class (`gentle-ai#5094`, `#4286`, `#2366`; `gentle-shell#1087`, and `gentle-ai#4807`) — producing the current, corrected figures of **39.3% (483) / 60.7% (745)**.

---

## 7. Empirical Verification: 20 Real Issues from the Sanitized Snapshot

Below are 20 concrete issues drawn directly from `issues.json` (identical to `db/exp.db`), showing the deterministic rule applied and the resulting recommendation:

| Issue Identifier | Issue Title (truncated) | Rule Applied | Recommendation | Human Review |
| --- | --- | --- | --- | --- |
| `gentle-ai#4917` | A corrupt custom-agents.json silently drops the registry entry of a successful install | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#4795` | bug(opencode): engram plugin adapter still ships V1 shape | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#4701` | bug(repo): contributor-filed issues never receive the form-declared status:needs-review label | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#4474` | bug(review): approved closure lists advisory findings without their claim text | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#4282` | bug(doctor): engram:reachable names only two persisted configs | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#4031` | review and issues: negotiated v2 lifecycle on Pi | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#3774` | bug(install/sync): transient atomic-rename denial on Windows | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#1829` | fix(theme): theme injection would overwrite TOML/YAML settings files with JSON | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#787` | fix(opencode): orchestrator agent permission override bypasses top-level denies | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-shell#1044` | Engram tools are never detected when the MCP adapter prefixes tool names | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-shell#923` | bug(gentle-shell): framePromptLines consumes the last autocomplete row | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-shell#883` | bug(pi-pretty): FFF native backend is unreachable on Android/Termux | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-shell#748` | bug(review): host consent prompt outlives its binding TTL | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-shell#715` | Shell bar drops extension statuses on narrow terminals | `rule:candidato_p0_requiere_revision_humana` | candidato P0, requiere revisión humana | required |
| `gentle-ai#3190` | bug(review): review start aborts on Windows when Go runtime cannot allocate memory | `rule:hard_crash` | P1 | recommended |
| `gentle-shell#1606` | bug(skill-registry): unhandled async EMFILE from directory watcher crashes pi on startup | `rule:hard_crash` | P1 | recommended |
| `gentle-ai#4823` | feat(pi): support opt-in community plugin discovery and installation | `rule:feature_request` | P2 | recommended |
| `gentle-ai#3794` | feat(review): add a candidate-bound cacheable delivery | `rule:feature_request` | P2 | recommended |
| `gentle-ai#3258` | test(cli): cover the host-mediated refusal for review | `rule:docs_chore_question` | P3 | recommended |
| `gentle-ai#2628` | fix(cli): component modifiers report success when their component is not scheduled | (none) | grey area -> LLM Pass 1 | yes |

Issue `gentle-ai#2628` is intentionally included as the concrete regression case that the corrected engine **no longer** flags as candidate P0: the matched span is a fix description, not a silent loss.

---

## 8. Known Limitations & What Is NOT Yet Validated

To maintain strict scientific and technical honesty, the following boundaries are explicitly noted:

1. **Residual 60.7% Grey-Area Backlog Evaluation:**
   * The deterministic rules engine was evaluated across all 1,228 issues, but the full two-pass LLM pipeline has only been run on the 90-issue sample (Run #1).
   * The remaining 745 open issues requiring LLM inference have not yet been evaluated end-to-end.
2. **Calibration Sample Reuse:**
   * The 90-issue sample informed heuristic calibration. Out-of-sample (held-out) validation is planned for Phase 3.
3. **No Autonomous GitHub Mutations:**
   * In strict accordance with the non-negotiable principles, the assistant has zero GitHub mutation authority. No labels, comments, transfers, or closures have been applied to live GitHub repositories.
4. **Candidate P0 Requires Human Adjudication:**
   * The 14 candidate P0 issues are pending `veredicto_humano` in `gold-p0-p1.md`; none has been confirmed by a maintainer.
5. **Longitudinal Maintainer Study:**
   * Human maintainer acceptance and override rates over extended operational periods (e.g. 30 days of active triaging) have not yet been measured.
6. **Generalization Beyond Conventional Commits:**
   * The deterministic engine achieves 39.3% coverage primarily because the Gentle-AI ecosystem widely adheres to Conventional Commits (`feat:`, `docs:`, `fix:`). In repositories without commit discipline, deterministic coverage would be lower and rely more heavily on LLM Pass 1.
7. **Cross-System Link Ground Truth:**
   * Only a small set of explicit cross-repository references is currently indexed in `cross_refs`. While Asymmetric Escrow is modeled and schemas are validated, cross-repository routing precision in the wild remains to be verified upon live testing.
