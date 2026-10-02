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
