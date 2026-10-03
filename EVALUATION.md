# EVALUATION.md — External Audit & Technical Verification Guide

> **Self-contained evaluation artifact.** It lets an external auditor verify the tool without cloning the repository or navigating directories: the engine source, the test suite, the exact outputs, the metrics and the limitations are all in this file.
>
> **Governance invariant:** a deterministic silent-data-loss match is emitted strictly as **`candidato P0, requiere revisión humana`** (candidate P0 requiring human review), never as a final P0 decision.

---

## 0. One-Screen Summary

| Question | Answer | Where to verify |
| --- | --- | --- |
| What is the backlog? | 1,228 open issues: `gentle-ai` 733, `gentle-shell` 424, `engram` 71 | `python3 tools/metrics.py` |
| How much does code resolve without an LLM? | **510 issues (41.5%)**; 718 (58.5%) remain grey area | `python3 tools/metrics.py` |
| What are the bands? | candidate P0 14, P1 17, P2 399, P3 80, grey 718 | `python3 tools/metrics.py` |
| Is anything auto-promoted against the reporter? | No. A hard signal under `feat:`/`docs:` keeps its band and is flagged for human review (26 issues) | `test_rules.py` §13 |
| Does the tool act on GitHub? | No. It is read-only; a checker fails if any mutating call appears | `python3 tools/readonly_check.py` |
| Are the figures trustworthy? | Every figure is recomputed; none is hardcoded. Precision of the post-audit rules is **pending human validation** | `PROMISES.md` |
| What is not done? | Module D (obsolete issues), shadow mode, labelling tool | `PROMISES.md` §4 |
| Do the mechanical modules exist? | Yes: completeness (A), duplicates (B), cross-repo links (C), possibly-obsolete (D). Read-only, no labels needed | `MODULES.md`, `python3 tools/run_reports.py` |
| Are the reports reproducible? | Yes, byte-identical across processes | `python3 tools/determinism_check.py` |
| Is there a board? | Yes: a local Kanban console with one board per application, in testing | `python3 board/server.py --ingest` → 127.0.0.1:8770 |
| One gate for everything? | 10/10 checks in one command (`--full`) | `python3 tools/verify_all.py --full` |
| Tests | `129/129` rule tests, `12/12` contract tests | this file §2 and §3 |

> **Honesty note.** Coverage is a census, not a correctness measure. The crash vocabulary and the rule order were changed after the adversarial audit; **no precision improvement is claimed** until a maintainer labels a fresh sample.

---

## 1. Source: `db/rules.py`

Fuente: `db/rules.py @ ad7b6b1`

```python
#!/usr/bin/env python3
"""
rules.py — Deterministic triage rule engine for the Gentle AI ecosystem

Applies code-based heuristics BEFORE invoking an LLM:
  1. Features / enhancements -> P2 (rule:feature_request)
  2. Docs / chores / questions -> P3 (rule:docs_chore_question)
  3. Silent data loss / corruption -> candidato P0, requiere revisión humana
     (rule:candidato_p0_requiere_revision_humana)
  4. Panic / SIGSEGV / hard crash without workaround -> P1 (rule:hard_crash)
  5. Crash WITH documented workaround / retry -> P2 (rule:crash_with_workaround_demoted_to_p2)
  6. Cross-repository links (cross_refs) -> cross classification

Governance Invariants:
  - Deterministic P0 is strictly a candidate ("candidato P0, requiere revisión humana"),
    never an autonomous final decision.
  - Negations ("no data loss", "without data loss", "is not a deadlock") and fix
    descriptions ("from being silently dropped to being rejected") never trigger
    high-priority rules.
  - Deadlocks require process or thread context (goroutine, thread, mutex, process,
    hang); metaphorical deadlocks ("two rules deadlock") are ignored.
  - A feature/docs issue that nonetheless carries a hard P0/P1 signal is NOT promoted
    to P0/P1 automatically. It keeps its band and is flagged for human review.
  - No figure is hardcoded. All counts are computed dynamically.

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

# Conventional title prefixes recognized by the ecosystem.
KNOWN_PREFIXES = (
    "feat", "feature", "fix", "bug", "docs", "doc", "chore", "typo",
    "refactor", "test", "ci", "perf", "style", "question", "review",
    "meta", "security",
)

# Title prefix extraction tolerates leading backticks, quotes and bracketed
# prefixes such as "[Automated provider defect] bug(opencode): ...".
_PREFIX_LEAD = re.compile(
    r"^\s*(?:[`'\"\[]+\s*|\[[^\]]*\]\s*)*"
    r"(?P<tok>feat|feature|fix|bug|docs?|chore|typo|refactor|test|ci|perf|style|question|review|meta|security)\b",
    re.IGNORECASE,
)


# 1. P0: Silent data loss & corruption base pattern
RE_P0_SILENT_BASE = re.compile(
    r"(?:\bsilent(?:ly)?\s+(?:corrupt(?:s|ed|ing|ion)?|delet(?:es|ed|ing|ion)?|drop(?:s|ped|ping)?|overwrit(?:es|ing)?|overwrote|overwritten|los(?:es|t|ing)?|fail(?:s|ed|ing)?\s+to\s+save)\b|\bdata\s+loss\b)",
    re.IGNORECASE,
)

# Negation safeguards for data loss (e.g. 'no data loss', 'without data loss', 'not data loss')
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

# 2. P1: Hard crashes. Vocabulary widened after the adversarial audit (AUDIT.md):
# verb forms of "crash", "uncaughtException" (camelCase), "runtime panic" without a
# colon, "fails to start", "out of memory". Generic "cannot start" is deliberately NOT
# matched because "review cannot start" is a blocked workflow, not a process crash.
RE_P1_CRASH_CORE = re.compile(
    r"(?:"
    r"\bpanic:\s*"
    r"|\bruntime\s+panic\b"
    r"|\bSIGSEGV\b"
    r"|\bfatal\s+error:\s*runtime\b"
    r"|\bsegmentation\s+fault\b"
    r"|\bNullPointerException\b"
    r"|\buncaught\s*exception\b"
    r"|\bunhandled\s*(?:exception|rejection)\b"
    r"|\bstack\s+overflow\b"
    r"|\bout\s+of\s+memory\b"
    r"|\bOOM[- ]?kill\w*\b"
    r"|\bfail(?:s|ed|ing)?\s+to\s+start\b"
    r"|\b(?:refuses?|refused|unable)\s+to\s+start\b"
    r"|\b(?:pi|process|binary|app|service|server|daemon|cli|command|launcher|pi-pretty|the\s+tool)\b[^.\n]{0,12}?\b(?:cannot|can'?t|will\s+not|won'?t)\s+(?:even\s+)?start\b"
    r"|\bcrash(?:es|ed|ing)\b"
    r"|\b(?:a|an|the|hard|fatal|silent|app|pi|process|binary|it|to|on|after|during)\s+crash\b"
    r"|\bcrash[- ](?:loop|on|when|after|during|escalat\w*)\b"
    r"|\bbricked\b"
    r")",
    re.IGNORECASE,
)

# Idioms where "crash" is a design property or a dismissed hypothesis, not an event.
RE_CRASH_HANDLED = re.compile(
    r"(?:\bcrash[-\s]?(?:safe|safety|recover\w*|consistent\w*|only|proof|free|on-)\w*\b"
    r"|\b(?:avoid|avoids|avoided|avoiding|prevent|prevents|prevented|preventing|stop|stops|stopped|protect|protects|protected)\b"
    r"[^.\n;]{0,40}?\b(?:from\s+)?crash\w*\b"
    r"|\b(?:incorrectly|mistakenly|falsely|wrongly)\s+(?:conclude|concludes|concluded|assume|assumes|assumed|report|reports|reported|claim|claims|claimed)\b[^.\n]{0,80}?\b(?:start|crash|fail)\w*\b)",
    re.IGNORECASE,
)

# Deadlock base pattern
RE_DEADLOCK_BASE = re.compile(r"\bdeadlock(?:ed|s)?\b", re.IGNORECASE)

# Negation for deadlock (e.g. 'is not a deadlock')
RE_DEADLOCK_NEGATION = re.compile(
    r"\b(?:not|never|is\s+not|hardly)\s+(?:a\s+)?deadlock\b",
    re.IGNORECASE,
)

# Process or thread concurrency context required for deadlock to be a real crash
RE_CONCURRENCY_CONTEXT = re.compile(
    r"\b(?:goroutines?|threads?|mutex(?:es)?|locks?|process(?:es)?|hangs?|hanging|workers?)\b",
    re.IGNORECASE,
)

# Trailing negation ("... has not been demonstrated / observed / does not apply")
RE_NEG_AFTER = re.compile(
    r"\b(?:has|have|had|was|were|is|are|does|do|did)?\s*not\s+(?:been\s+)?"
    r"(?:demonstrated|observed|reproduced|confirmed|reported|shown|present|found|apply)\b",
    re.IGNORECASE,
)

# Leading negation immediately before a signal ("not a crash", "no crash", "no system crash")
RE_NEG_BEFORE = re.compile(
    r"(?:\bnothing\b[^.\n;]{0,20}?|\b(?:no|not|never|without|hardly|nor|neither)\b(?:\s+\w+){0,3}\s*)\s*$",
    re.IGNORECASE,
)

# 3. Workaround & retry recovery detection (Codifies Rule H9)
RE_WORKAROUND_NEGATIVE = re.compile(
    r"\b(?:no(?:ne)?|without(?:\s+any)?|unaware\s+of\s+any)\s+(?:known\s+)?workaround\b"
    r"|\bworkaround:\s*(?:none|n/?a|no)\b"
    r"|\b(?:no|not|never|without)\b[^.\n;]{0,30}?\b(?:work\s*around|workaround)\b",
    re.IGNORECASE,
)

RE_WORKAROUND_POSITIVE = re.compile(
    r"\b(?:workaround|work-around|work\s+around|temporary fix|temp fix"
    r"|recovers?(?:\s+upon|\s+on)?\s+retry|retry succeeds|retrys?\s+(?:works|helps)"
    r"|restart(?:ing)?\s+(?:fixes|helps|works)|restart fixes"
    r"|works?\s+(?:if|after)|re-?run\w*\s+(?:works|fixes))\b",
    re.IGNORECASE,
)

RE_P3_DOCS = re.compile(
    r"^(docs?|chore|typo|style|ci|refactor)(\(.*\))?:\s*",
    re.IGNORECASE,
)

EXPLICIT_DOCS_PREFIXES = ("docs", "doc", "chore", "typo")
EXPLICIT_FEATURE_PREFIXES = ("feat", "feature")


def derive_title_prefix(title: str, provided: str) -> str:
    """
    Returns a normalized conventional prefix.

    The ingested `title_prefix` is sometimes empty even though the title starts with
    a conventional token, because of a leading backtick or a bracketed prefix such as
    "[Automated provider defect]". This function recovers the token from the title.
    """
    m = _PREFIX_LEAD.match(title or "")
    if m:
        return m.group("tok").lower()
    return (provided or "").strip().lower()


def _is_negated(text: str, start: int, end: int) -> bool:
    """True when the signal at [start, end) is negated right before or right after."""
    before = text[max(0, start - 40):start]
    if RE_NEG_BEFORE.search(before):
        return True
    after = text[end:end + 60]
    if RE_NEG_AFTER.search(after):
        return True
    return False


def has_active_workaround(text: str) -> bool:
    """True when the text specifies a workaround or retry recovery without stating none exists."""
    if RE_WORKAROUND_NEGATIVE.search(text):
        return False
    return bool(RE_WORKAROUND_POSITIVE.search(text))


def has_silent_data_loss(text: str) -> bool:
    """
    True when the text reports an unnegated silent data loss or corruption event.
    Rejects negations ('no data loss', 'without data loss') and fix descriptions.
    """
    for m in RE_P0_SILENT_BASE.finditer(text):
        matched = m.group(0).lower()
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 80)
        window = text[start:end]

        if RE_FIX_DESCRIPTION.search(window):
            continue
        if "data loss" in matched and RE_DATA_LOSS_NEGATION.search(window):
            continue
        if RE_SILENT_NEGATION.search(window):
            continue
        if _is_negated(text, m.start(), m.end()):
            continue
        return True
    return False


def is_hard_crash(text: str) -> bool:
    """
    True when the text reports a hard runtime crash (panic, SIGSEGV, crash, fatal
    error, out of memory, fails to start, stack overflow) or a concurrency deadlock
    with explicit thread/process/mutex/hang context.

    Rejects negation ('not a crash', 'has not been demonstrated') and compound
    adjectives ('crash-safe'); metaphorical deadlocks are rejected separately.
    """
    for m in RE_P1_CRASH_CORE.finditer(text):
        window_start = max(0, m.start() - 120)
        window_end = min(len(text), m.end() + 120)
        window = text[window_start:window_end]
        # 'crash-safe', 'crash-recoverable', 'avoid the crash' describe design, not an event.
        if RE_CRASH_HANDLED.search(window):
            continue
        if _is_negated(text, m.start(), m.end()):
            continue
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


def has_hard_signal(text: str) -> bool:
    """True when the text carries any unnegated hard P0/P1 signal."""
    return has_silent_data_loss(text) or is_hard_crash(text)


def classify_issue_deterministically(row, labels, cross_refs):
    """
    Returns (band, cross, rule_name) or (None, cross, None) if indeterminate.

    Invariant: P0 is strictly 'candidato P0, requiere revisión humana', never a final
    decision. A hard signal under a non-bug prefix does NOT change the band; use
    requires_human_review() to detect that case.
    """
    row_dict = dict(row) if hasattr(row, "keys") else (row or {})
    title = row_dict.get("title") or ""
    body = row_dict.get("body") or ""
    prefix = derive_title_prefix(title, row_dict.get("title_prefix") or "")
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

    # Check candidate P0: silent data loss / corruption
    if is_bug and has_silent_data_loss(full_text):
        return P0_CANDIDATE_LABEL, cross, RULE_P0_CANDIDATE

    # Check P1 vs P2 (Rule H9 & H10): hard crash, demoted when a workaround exists
    if is_bug and is_hard_crash(full_text):
        if has_active_workaround(full_text):
            return "P2", cross, "rule:crash_with_workaround_demoted_to_p2"
        return "P1", cross, "rule:hard_crash"

    # Explicit conventional prefix wins over a conflicting type label.
    # (Fixes the audit finding: a `docs:` issue with an `enhancement` label was P2.)
    if prefix in EXPLICIT_DOCS_PREFIXES or prefix in ("refactor", "test", "ci", "style"):
        return "P3", cross, "rule:docs_chore_question"

    if prefix in EXPLICIT_FEATURE_PREFIXES:
        return "P2", cross, "rule:feature_request"

    # Label-only fallbacks
    if "type:feature" in label_set or "enhancement" in label_set or "feature" in label_set:
        return "P2", cross, "rule:feature_request"

    if (
        "type:chore" in label_set
        or "documentation" in label_set
        or "question" in label_set
        or "discussion" in label_set
        or RE_P3_DOCS.search(title)
    ):
        return "P3", cross, "rule:docs_chore_question"

    # Indeterminate — must fall through to LLM / human triage
    return None, cross, None


def requires_human_review(row, labels, cross_refs):
    """
    Returns (bool, reason).

    True when a non-bug issue keeps a low band (P2/P3) yet carries a hard P0/P1
    signal. The band is intentionally NOT changed (never auto-promote a `feat:` to
    P1); the maintainer is asked to look. See DECISIONS.md D-004.
    """
    row_dict = dict(row) if hasattr(row, "keys") else (row or {})
    band, cross, rule = classify_issue_deterministically(row_dict, labels, cross_refs)
    if band not in ("P2", "P3"):
        return False, None
    text = f"{row_dict.get('title') or ''}\n{row_dict.get('body') or ''}"
    if has_silent_data_loss(text):
        return True, "hard_signal_under_prefix: silent data loss under a non-bug prefix"
    if is_hard_crash(text):
        return True, "hard_signal_under_prefix: crash under a non-bug prefix"
    return False, None


def run_snapshot_evaluation(snapshot_data):
    """Evaluates classification over a loaded JSON snapshot dynamically without hardcoded figures."""
    total = len(snapshot_data)
    rule_counts = {}
    covered = 0
    review_flagged = 0

    for item in snapshot_data:
        band, cross, rule = classify_issue_deterministically(
            item, item.get("labels", []), item.get("cross_refs", [])
        )
        if band is not None:
            covered += 1
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
        flag, reason = requires_human_review(item, item.get("labels", []), item.get("cross_refs", []))
        if flag:
            review_flagged += 1

    grey = total - covered
    pct_covered = (100.0 * covered / total) if total > 0 else 0.0
    pct_grey = (100.0 * grey / total) if total > 0 else 0.0

    print("════════════════════════════════════════════════════════════════════")
    print(f" DETERMINISTIC TRIAGE EVALUATION (from issues.json snapshot, {total} issues)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  Classified by code (without LLM): {covered} ({pct_covered:.1f}%)")
    print(f"  Residual grey-area (requires LLM): {grey} ({pct_grey:.1f}%)")
    print(f"  Flagged for human review (hard signal under low band): {review_flagged}\n")
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
        flag, reason = requires_human_review(row, tc["labels"], tc["cross_refs"])
        status = f"──► [{band}] via {rule}" if band else "──► [GREY AREA] Requires LLM Pass 1"
        if flag:
            status += "  ⚠ REQUIRES HUMAN REVIEW"
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

    # Evaluate against the calibration sample where we have Judge A and Judge B votes
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

## 2. Test Suite: `test_rules.py` and its exact output

Fuente: `test_rules.py @ ad7b6b1`

```python
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
```

### Exact output (`python3 test_rules.py`)

```text
════════════════════════════════════════════════════════════════════
 RUNNING DETERMINISTIC RULES TEST SUITE (test_rules.py)
════════════════════════════════════════════════════════════════════

── 1. CANDIDATE P0 POSITIVES (Silent Data Loss & Corruption) ──
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

── 4. REAL-ISSUE REGRESSION CASES (#5007, #4792, #2628, #4807) ──
  ✔ [PASS] issue #5007 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] issue #4792 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] issue #2628 is not flagged as candidate P0 / P1 -> band=None
  ✔ [PASS] #4807 trap phrase 'not a deadlock' alone is not a crash
  ✔ [PASS] #4807 is P1 from memory exhaustion, not from the deadlock metaphor (band='P1')

── 5. HARD-CRASH VOCABULARY (widened after AUDIT.md) ──
  ✔ [PASS] P1 positive: 'panic: runtime error: index out of range'
  ✔ [PASS] P1 positive: 'fatal error: runtime: out of memory'
  ✔ [PASS] P1 positive: 'SIGSEGV in worker process on boot'
  ✔ [PASS] P1 positive: 'segmentation fault when dereferencing null pointer'
  ✔ [PASS] P1 positive: 'NullPointerException in MessageHandler'
  ✔ [PASS] P1 positive: 'uncaught exception terminated thread'
  ✔ [PASS] P1 positive: 'stack overflow during recursive traversal'
  ✔ [PASS] P1 positive: 'recursive skill watcher crashes Pi with uncaughtExcepti'
  ✔ [PASS] P1 positive: 'bare `gentle-ai` invocation crashes with Go runtime pan'
  ✔ [PASS] P1 positive: 'the process can fail to start even though `pi --version'
  ✔ [PASS] P1 positive: 'the machine runs out of memory'
  ✔ [PASS] P1 positive: 'terminated by the OOM killer'
  ✔ [PASS] P1 positive: 'causing the parser to crash'
  ✔ [PASS] P1 positive: 'fatal error: all goroutines are asleep - deadlock!'
  ✔ [PASS] P1 positive: 'worker thread enters deadlock when acquiring mutex'
  ✔ [PASS] P1 positive: 'process hangs due to deadlock in event loop'

── 6. CRASH NEGATION AND IDIOM GUARDS (No false crash) ──
  ✔ [PASS] no false crash: 'It is a fork bomb, not a deadlock.'
  ✔ [PASS] no false crash: 'This is not a deadlock situation'
  ✔ [PASS] no false crash: 'The two rules deadlock each other.'
  ✔ [PASS] no false crash: 'ordinary review denials deadlock the agent'
  ✔ [PASS] no false crash: 'the review is deadlocked'
  ✔ [PASS] no false crash: 'sdd-remediate run can deadlock before phase work'
  ✔ [PASS] no false crash: 'There is no system crash, but the API usage log reflect'
  ✔ [PASS] no false crash: 'the finding's premise (a live crash-on-render risk) doe'
  ✔ [PASS] no false crash: 'Crash-window tests not parameterized for the new class'
  ✔ [PASS] no false crash: 'a live crash-on-render risk does not apply'
  ✔ [PASS] no false crash: 'the review cannot start for this candidate'
  ✔ [PASS] no false crash: 'The native RDD assessment cannot start because a binary'
  ✔ [PASS] no false crash: 'a reload crash was already reported in another issue'
  ✔ [PASS] no false crash: 'designed to be crash-safe by kernel release'
  ✔ [PASS] no false crash: 'a general crash-recoverable quarantine engine'
  ✔ [PASS] no false crash: 'prevent these filesystem errors from crashing Pi'
  ✔ [PASS] real crash accepted: 'fatal error: all goroutines are asleep - deadlock!'
  ✔ [PASS] real crash accepted: 'mutex deadlock detected in worker pool'
  ✔ [PASS] real crash accepted: 'thread deadlock on channel receive'
  ✔ [PASS] real crash accepted: 'Pi crashes on startup'
  ✔ [PASS] real crash accepted: 'it can corrupt or revert on crash'
  ✔ [PASS] real crash accepted: 'the parser crashes when the payload is truncated'

── 7. RULE H9 vs H10 DEMOTION (Crash WITH Workaround -> P2) ──
  ✔ [PASS] crash + workaround demoted to P2: 'panic: runtime error: index out of ' + 'Workaround: run with --disable-cach'
  ✔ [PASS] crash + workaround demoted to P2: 'SIGSEGV on startup when config is m' + 'Temporary fix: touch config.json be'
  ✔ [PASS] crash + workaround demoted to P2: 'fatal error: runtime deadlock in po' + 'Recovers upon retry when worker poo'
  ✔ [PASS] crash + workaround demoted to P2: 'NullPointerException in sync loop' + 'Restart fixes the issue temporarily'
  ✔ [PASS] crash + workaround demoted to P2: 'Pi fails to start after the overlay' + 'Workaround: repair the two lines ba'
  ✔ [PASS] crash + workaround demoted to P2: 'Pi crashes on reload' + 'The same command works after runnin'

── 8. WORKAROUND NEGATION (Explicit 'No Workaround' -> Remains P1) ──
  ✔ [PASS] crash + negated workaround remains P1: 'panic: runtime error: nil dereferen' + 'Workaround: none. The daemon immedi'
  ✔ [PASS] crash + negated workaround remains P1: 'SIGSEGV on boot in initialization r' + 'No workaround available. Completely'
  ✔ [PASS] crash + negated workaround remains P1: 'fatal error: runtime: out of memory' + 'Without any workaround; all attempt'
  ✔ [PASS] crash + negated workaround remains P1: 'NullPointerException in parser' + 'Workaround: n/a. Issue is reproduci'
  ✔ [PASS] crash + negated workaround remains P1: 'Pi crashes when the session is load' + 'Note that no configuration can work'

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
  ✔ [PASS] #5168 explicit docs prefix wins over enhancement label -> 'P3' (rule:docs_chore_question)

── 11. GREY-AREA FALL-THROUGH (Requires LLM Pass 1) ──
  ✔ [PASS] grey area -> indeterminate: 'button alignment is slightly off in Safa'
  ✔ [PASS] grey area -> indeterminate: 'search results return in unexpected orde'
  ✔ [PASS] grey area -> indeterminate: 'intermittent latency spike during peak l'

── 12. TITLE PREFIX RECOVERY (leading backtick / bracket / no colon) ──
  ✔ [PASS] prefix '`bug(install): Pi commands fail through pi.cm' -> 'bug' (expected 'bug')
  ✔ [PASS] prefix '[Automated provider defect] bug(opencode): or' -> 'bug' (expected 'bug')
  ✔ [PASS] prefix 'bug(TUI) ResolveTarget can bake another tool'' -> 'bug' (expected 'bug')
  ✔ [PASS] prefix 'bug(2.3.0-rc.1) 6 Tests Results in Opencode' -> 'bug' (expected 'bug')
  ✔ [PASS] prefix 'fix(review) bloqueada por fallo de captura' -> 'fix' (expected 'fix')
  ✔ [PASS] prefix 'bug(harness) Agent left the current project d' -> 'bug' (expected 'bug')
  ✔ [PASS] prefix 'Windows Terminal rendering is broken' -> '' (expected '')
  ✔ [PASS] prefix 'Error: something failed' -> '' (expected '')
  ✔ [PASS] #4974 recovered prefix yields P1 (band='P1')

── 13. REQUIRES_HUMAN_REVIEW (hard signal under a low band) ──
  ✔ [PASS] feat with hard signal keeps band P2 (got 'P2')
  ✔ [PASS] feat with silent loss is flagged for human review
  ✔ [PASS] docs with a crash is flagged for human review
  ✔ [PASS] clean docs issue is not flagged for human review

── 14. SNAPSHOT SELF-CONSISTENCY (issues.json, dynamic) ──
  ✔ [PASS] Snapshot file issues.json exists
  ✔ [PASS] Snapshot is non-empty (found 1228 issues)
  ✔ [PASS] snapshot contains gentle-ai#5007
  ✔ [PASS] gentle-ai#5007 -> None (expected None): explicit 'no data loss' stays out of candidate P0/P1
  ✔ [PASS] snapshot contains gentle-ai#4792
  ✔ [PASS] gentle-ai#4792 -> None (expected None): explicit 'no data loss claimed' stays out of candidate P0/P1
  ✔ [PASS] snapshot contains gentle-ai#2628
  ✔ [PASS] gentle-ai#2628 -> None (expected None): fix description stays out of candidate P0/P1
  ✔ [PASS] snapshot contains gentle-ai#4807
  ✔ [PASS] gentle-ai#4807 -> 'P1' (expected 'P1'): real memory exhaustion yields P1
  ✔ [PASS] snapshot contains gentle-ai#4917
  ✔ [PASS] gentle-ai#4917 -> 'candidato P0, requiere revisión humana' (expected 'candidato P0, requiere revisión humana'): real silent loss is a candidate P0
  ✔ [PASS] snapshot contains gentle-ai#4677
  ✔ [PASS] gentle-ai#4677 -> 'P1' (expected 'P1'): 'crashes with Go runtime panic' is P1
  ✔ [PASS] snapshot contains gentle-shell#962
  ✔ [PASS] gentle-shell#962 -> 'P1' (expected 'P1'): 'crashes Pi with uncaughtException' is P1
  ✔ [PASS] snapshot contains gentle-ai#4974
  ✔ [PASS] gentle-ai#4974 -> 'P1' (expected 'P1'): recovered prefix + 'fail to start' is P1
  ✔ [PASS] snapshot contains gentle-ai#4809
  ✔ [PASS] gentle-ai#4809 -> 'P2' (expected 'P2'): 'fails to start' with a workaround is demoted to P2
  ✔ [PASS] snapshot contains gentle-ai#5168
  ✔ [PASS] gentle-ai#5168 -> 'P3' (expected 'P3'): explicit docs prefix wins over enhancement label
  ✔ [PASS] dynamic snapshot classification is reproducible across passes
  ✔ [PASS] engine covers at least one issue (510 covered)
  ✔ [PASS] candidate P0 rule is exercised on the snapshot
  ✔ [PASS] hard-crash rule is exercised on the snapshot

  Dynamic rule histogram over issues.json (recomputed, not frozen):
    - rule:feature_request                        :  395
    - rule:docs_chore_question                    :   80
    - rule:hard_crash                             :   17
    - rule:candidato_p0_requiere_revision_humana  :   14
    - rule:crash_with_workaround_demoted_to_p2    :    4

────────────────────────────────────────────────────────────────────
 FINAL TEST RESULT: 129/129 tests passed successfully.
════════════════════════════════════════════════════════════════════
```

---

## 3. Contract Validation: `schemas/validate.py`

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

The schema enforces the governance invariant **bidirectionally**: `band == "candidato P0, requiere revisión humana"` requires `source == "deterministic_rule"` and `rule_name == "rule:candidato_p0_requiere_revision_humana"`, and that rule name requires the candidate band. Negative tests 4 and 5 prove a final `P0` cannot be emitted by the candidate rule, and that the candidate label cannot be attached to a non-candidate rule.

---

## 4. Recomputed Figures: `tools/metrics.py`

```text
════════════════════════════════════════════════════════════════════
 PUBLISHED FIGURES (recomputed; nothing hardcoded)
════════════════════════════════════════════════════════════════════
  total open issues: 1228
  per repository: engram=71, gentle-ai=733, gentle-shell=424

  issues with a priority:* label:   178 (14.5%)
  issues without any priority:*     1050 (85.5%)
  issues under status:needs-review: 686 (55.9%)

  classified by code (no LLM): 510 (41.5%)
  residual grey area:          718 (58.5%)

  breakdown by deterministic rule:
    - rule:feature_request                        :  395 (32.2%)
    - rule:docs_chore_question                    :   80 (6.5%)
    - rule:hard_crash                             :   17 (1.4%)
    - rule:candidato_p0_requiere_revision_humana  :   14 (1.1%)
    - rule:crash_with_workaround_demoted_to_p2    :    4 (0.3%)

  bands:
    - None                                        :  718 (58.5%)
    - P2                                          :  399 (32.5%)
    - P3                                          :   80 (6.5%)
    - P1                                          :   17 (1.4%)
    - candidato P0, requiere revisión humana      :   14 (1.1%)

  flagged for human review (hard signal under a low band): 26
    - hard_signal_under_prefix: silent data loss under a non-bug prefix: 17
    - hard_signal_under_prefix: crash under a non-bug prefix: 9

  exploration (groups 1-4): 997 issues, 409 classified (41.0%)

  held-out (group 0): 231 issues, 101 classified (43.7%)

  issues with structured cross_refs: 26
  issues with cross != none:         25

  gentle-shell issues mentioning 'gentle-ai': 202
  of those with a confirmed cross_ref:        16
  lexical keyword precision:                  7.9% (16/202)

  calibration sample (exp.db run 1): 90 issues
  agreement figures are printed by 'python3 db/rules.py' section 2
════════════════════════════════════════════════════════════════════
```

---

## 5. Read-Only Invariant and Privacy Checks

### `tools/readonly_check.py`

```text
════════════════════════════════════════════════════════════════════
 READ-ONLY INVARIANT CHECK
════════════════════════════════════════════════════════════════════
  files scanned: 9
  ✔ no mutating GitHub or HTTP write operation found in project source
  allowed: `gh issue list`, `gh pr list` (read-only) in ingestion scripts
════════════════════════════════════════════════════════════════════
```

### `tools/privacy_check.py`

```text
════════════════════════════════════════════════════════════════════
 PRIVACY CHECK (issues.json)
════════════════════════════════════════════════════════════════════
  issues loaded: 1228
  ✔ no author/user fields
  ✔ no forbidden maintainer handles (Alan-TheGentleman)
  ✔ no non-placeholder email addresses
════════════════════════════════════════════════════════════════════
```

One maintainer handle was found inside an issue body and redacted to `@[maintainer]`. The band/rule digest before and after the redaction is identical, proving no rule depends on the handle.

---

## 6. Triage Model: 13 Dimensions and Rules H1–H10

### The 13 dimensions

| # | Dimension | Pass | Values |
| --- | --- | --- | --- |
| D1 | issue type | 1 | bug · feature · question · docs · chore · unknown |
| D2 | affected component | 1–2 | `owner/repo` + component, or `unknown` |
| D3 | scope | 1–2 | single · component · system · unknown |
| D4 | impact | 1–2 | blocks use · degrades · cosmetic · unknown |
| D5 | severity | 2 | high · medium · low · unknown |
| D6 | urgency | 1–2 | now · soon · whenever · unknown |
| D7 | reproducibility | 2 | reproducible · partial · not-reproducible · unknown |
| D8 | completeness | 1 | complete · partial · insufficient |
| D9 | dependencies | 1–2 | list of references, or `none` |
| D10 | relationships | 1 | list of `owner/repo#n`, or `none` |
| D11 | blocking status | 2 | blocks · blocked-by · free · unknown |
| D12 | confidence | 1–2 | high · medium · low |
| D13 | evidence | 1–2 | issue text · comment · file:line · label |

D5, D7 and D11 are strictly unobservable a priori; in Pass 1 they are recorded as `unknown`.

### The 10 hard governance rules

| # | Rule | Literal definition |
| --- | --- | --- |
| **H1** | Cross-System Implication | Cross-system implication alone never promotes a band. |
| **H2** | Mandatory Evidence | A band is never emitted without at least one reason and at least one citation. |
| **H3** | Inference Discipline | A band is always inference; confidence is mandatory. |
| **H4** | Independent Causes | Pattern (c) must be split into separate issues, never promoted as one. |
| **H5** | Cosmetic Reach | Pattern (d) never promotes. Reach is not harm. |
| **H6** | Unknown Preservation | A missing dimension is `unknown`; it is never inferred silently. |
| **H7** | Maintainer Authority | A maintainer override always wins and is recorded as a decision. |
| **H8** | Provisional Pass 1 | Pass-1 bands are provisional; Pass 2 may correct them. |
| **H9** | Workaround & Retry | A documented workaround or a retry recovery demotes to P2, never P1. |
| **H10** | Code > LLM Pre-Filter | Unambiguous structural patterns are classified by code without an LLM. |

`AUDIT.md` §8 measured H1, H2 and H5 with 0 violations across the corpus and marked H3, H4, H6, H7 and H8 as **not auditable with this dataset** (process rules or dimensions the dataset does not carry).

---

## 7. Corrections Applied After the Adversarial Audit

| Finding (`AUDIT.md`) | Correction in the engine | Test | Validation |
| --- | --- | --- | --- |
| Crash vocabulary too narrow (`crashes`, `uncaughtException`, `fails to start`, `out of memory`) | `RE_P1_CRASH_CORE` widened; generic `cannot start` deliberately excluded | `test_rules.py` §5, §6; `gentle-shell#962`, `gentle-ai#4677` | pending human validation |
| Empty `title_prefix` (leading backtick, bracket prefix) | `derive_title_prefix()` recovers the token | `test_rules.py` §12; `gentle-ai#4974` | pending human validation |
| `feature` evaluated before `docs` (`gentle-ai#5168`) | explicit `docs:`/`chore:` prefix wins over a conflicting label | `test_rules.py` §10; `gentle-ai#5168` now P3 | pending human validation |
| `is_bug` blocks `feat:` with hard signals | `requires_human_review()` flags 26 issues; the band is **not** changed | `test_rules.py` §13 | pending human validation |
| H9 never fired on real data | workaround vocabulary widened; `bypass`/`mitigation` removed | `test_rules.py` §7–§8; 4 real demotions | pending human validation |
| Cross-repo coverage (345 unindexed mentions) | **not implemented** | — | not started |

Each decision, its alternatives and its consequences are recorded in `DECISIONS.md`.

---

## 8. Metrics Methodology and Provenance

| Metric | Value | Scope | How it is computed |
| --- | --- | --- | --- |
| Backlog size | 1,228 | all open issues | `tools/metrics.py` over `issues.json` |
| Deterministic coverage | 510 (41.5%) | all open issues | `classify_issue_deterministically` |
| Residual grey area | 718 (58.5%) | all open issues | same |
| Candidate P0 | 14 | all open issues | `rule:candidato_p0_requiere_revision_humana` |
| P1 | 17 | all open issues | `rule:hard_crash` |
| P2 | 399 | all open issues | feature requests + H9 demotions |
| P3 | 80 | all open issues | docs/chores/questions |
| Human-review flags | 26 | all open issues | `requires_human_review()` |
| Exploration coverage | 409/997 (41.0%) | groups 1–4 | `sha256(slug#number) mod 5` |
| Held-out coverage | 101/231 (43.7%) | group 0 | same |
| Lexical keyword precision | 7.9% (16/202) | gentle-shell issues mentioning `gentle-ai` | `tools/metrics.py` |
| Judge agreement | 94.1% / 85.3% | 34 deterministic matches in the 90-issue calibration sample | `python3 db/rules.py` section 2 |

**Calibration vs validation.** The 90-issue sample was used to author the heuristics, so it cannot validate them. The deterministic split exists for a fresh, reproducible validation; the maintainer must label it before any precision figure is published.

---

## 9. Known Limitations

1. **Precision is unvalidated.** All post-audit rule changes are pending human labelling. Only coverage is published as fact.
2. **Grey area untested end-to-end.** 718 issues require LLM inference, which has not been run over the full backlog.
3. **No autonomous GitHub mutation.** By design and by check (`tools/readonly_check.py`); no candidate has been labelled, commented or closed.
4. **Candidate P0 unconfirmed.** The 14 candidates in `gold-p0-p1.md` have `veredicto_humano: pendiente`.
5. **Cross-repo linking incomplete.** 345 issues mention another repository with no structured link; the linking module is not implemented.
6. **Module D Class B is not obsolescence evidence.** Only Class A (a path deleted in the repository's own history) is; Class B is reported separately and labelled weaker. No module has human-verified precision yet.
7. **Conventional-commit bias.** 41.5% coverage depends on the ecosystem using `feat:`/`docs:`/`bug:` prefixes; repositories without that discipline would rely more on the LLM pass.
8. **Process rules unverified.** H3, H4, H6, H7 and H8 cannot be checked with this dataset.

---

## 10. See Also

* `PROMISES.md` — every README claim mapped to evidence, status and gap.
* `DECISIONS.md` — design decisions with alternatives considered.
* `AUDIT.md` — the read-only adversarial audit that found the gaps above.
* `MODULES.md` — the mechanical read-only modules (completeness, duplicates, cross-repo links, possibly obsolete) with embedded source and limits.
* `BOARD.md` — the local Kanban console: columns, derived-vs-decided split, append-only log and limits.
* `STATUS.md` — current state, commit hashes, and what the owner must decide.

---

## 12. Local Kanban Board (in testing)

A local console on `http://127.0.0.1:8770/` with **one board per application** (`gentle-ai`, `engram`, `gentle-shell`), never mixed. Five working columns plus an archive.

| Aspect | Decision |
| --- | --- |
| State location | Local SQLite (`db/board.db`, gitignored). GitHub stays the source of truth for *what exists*; the board is the source of truth for *what a human decided* |
| Engine suggestions | Only **blocking** columns: `falta_info` (Module A) and `revision_humana` (candidate P0 or a hard signal under a non-bug prefix). Never `listo_mantener` |
| Human actions | Moving a card and setting the human verdict; both append to an immutable event log |
| Auditability | `tools/board_rebuild_check.py` wrecks the caches, rebuilds them from events and compares — on a temporary copy and on the live DB |
| Outbound network | None. `tools/readonly_check.py` now fails on `http.client`, `urllib.request` or `requests` anywhere in the project |
| Exposure | `127.0.0.1` only; the server refuses any other interface. Port 8770, distinct from the CRM cockpit on 8000 |
| UI language | Spanish (internal console). Repository artifacts remain English |

`test_board.py` covers 76 assertions, including that no card is auto-promoted to a positive column, that repositories are never mixed, and that the projections are reconstructible from the log.

**Not yet integrated per card:** Module B (duplicates), Module C (cross-repo links) and Module D (possibly obsolete) signals remain report-level; only band, rule, human-review flag and Module A missing fields show as card badges today.

---

## 11. Mechanical Modules (A, B, C)

Three read-only modules run over the frozen snapshot and write root reports. None needs human labels, none writes to GitHub, and every suggestion carries `veredicto_humano: pendiente`. Full method and embedded source live in [`MODULES.md`](MODULES.md).

| Module | Report | Headline figure |
| --- | --- | --- |
| A completeness | `report-completeness.md` | 313 of 1,043 form-filed issues miss a required content field |
| B duplicates | `report-duplicates.md` | 108 candidate pairs, 7 with strong evidence |
| C cross-repo links | `report-cross-links.md` | 48 explicit references, 15 resolving to an open issue |
| D possibly obsolete | `report-obsolete.md` | 54 issues reference a path deleted in the repository's own history (Class A); 155 more have an unresolved reference with no deletion record (Class B, weaker) |

Regenerate with `python3 tools/run_reports.py`; verify byte-identical output with `python3 tools/determinism_check.py`. Module C reframes an `AUDIT.md` figure: the audit reported "345 issues mention another repo with no structured link"; the actionable subset is 33 issues with an explicit `repo#N` reference, of which 15 resolve. The rest are prose mentions, which are not links. Module D keeps verifiable obsolescence (Class A) apart from a merely unresolved reference (Class B) so the weak signal does not dilute the strong one.
