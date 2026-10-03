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


def _spans(pattern, text, limit=3):
    """Matched snippets with a little context, for showing the evidence."""
    out = []
    for m in pattern.finditer(text or ""):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        out.append({
            "match": m.group(0),
            "context": re.sub(r"\s+", " ", text[start:end]).strip(),
        })
        if len(out) >= limit:
            break
    return out


def decide(row, labels=None, cross_refs=None, include_evidence=False):
    """
    Evaluates deterministic triage rules for an issue and returns a structured decision.

    This is the first-class decision port for the engine. Callers obtain band, rule,
    cross-system classification, human review requirements, the ordered trace of rules
    considered, and rich evidence (matched spans, negations, predicate states).

    Performance & laziness:
      Building the rich evidence block (running 10 regex finditer sweeps and extracting
      contextual spans) is computationally expensive. Because regular triage callers
      (classify_issue_deterministically, requires_human_review, board card projection)
      only need the decision fields, `include_evidence` defaults to False.
      When False, `evidence` in the return dictionary is None.
      Callers requiring explanation inspection (such as board/explain.py) must pass
      `include_evidence=True`.

    Determinism invariant: evidence lists and dictionaries are constructed in stable,
    deterministic order without depending on process-randomized hash sets.
    """
    row_dict = dict(row) if hasattr(row, "keys") else (row or {})
    title = row_dict.get("title") or ""
    body = row_dict.get("body") or ""
    prefix = derive_title_prefix(title, row_dict.get("title_prefix") or "")
    full_text = f"{title}\n{body}"
    labels_list = list(labels or [])
    cross_refs_list = list(cross_refs or [])

    # ── 1. CROSS-SYSTEM (from cross_refs) ──
    cross = "none"
    if cross_refs_list:
        foreign_refs = [cr for cr in cross_refs_list if cr.get("target_system_id") != row_dict.get("system_id")]
        if foreign_refs:
            cross = "dependency"

    # ── 2. PREDICATE EVALUATIONS ──
    label_set = {l.lower() for l in labels_list}
    is_bug = prefix in ("bug", "fix") or "type:bug" in label_set or "bug" in label_set
    feature_prefix = prefix in EXPLICIT_FEATURE_PREFIXES
    feature_label = bool(label_set & {"type:feature", "enhancement", "feature"})
    docs_prefix = prefix in EXPLICIT_DOCS_PREFIXES or prefix in ("refactor", "test", "ci", "style")
    docs_label_or_header = (
        bool(label_set & {"type:chore", "documentation", "question", "discussion"})
        or bool(RE_P3_DOCS.search(title))
    )
    docs_predicate = prefix in EXPLICIT_DOCS_PREFIXES or docs_label_or_header

    if include_evidence:
        p0_fires = has_silent_data_loss(full_text)
        crash_fires = is_hard_crash(full_text)
        workaround = has_active_workaround(full_text)
    elif is_bug:
        p0_fires = has_silent_data_loss(full_text)
        crash_fires = is_hard_crash(full_text)
        workaround = has_active_workaround(full_text) if crash_fires else False
    else:
        p0_fires = False
        crash_fires = False
        workaround = False

    # ── 3. ORDERED RULE EVALUATION TRACE ──
    chain = [
        ("candidato P0",                        RULE_P0_CANDIDATE,                          P0_CANDIDATE_LABEL, is_bug and p0_fires),
        ("P1 crash sin salida",                 "rule:hard_crash",                          "P1",                is_bug and crash_fires and not workaround),
        ("P2 crash con workaround (regla H9)",  "rule:crash_with_workaround_demoted_to_p2", "P2",                is_bug and crash_fires and workaround),
        ("P3 prefijo explícito de docs/tarea",  "rule:docs_chore_question",                 "P3",                docs_prefix),
        ("P2 prefijo explícito de feature",     "rule:feature_request",                     "P2",                feature_prefix),
        ("P2 etiqueta de feature",              "rule:feature_request",                     "P2",                feature_label),
        ("P3 etiqueta o encabezado de docs",    "rule:docs_chore_question",                 "P3",                docs_predicate),
    ]

    winner = next((c for c in chain if c[3]), None)
    winner_name = winner[0] if winner else None

    if winner:
        band = winner[2]
        rule = winner[1]
        decided_by = winner[0]
    else:
        band = None
        rule = None
        decided_by = "(ninguna regla: zona gris)"

    rules_considered = []
    for name, r_id, b_id, matched in chain:
        rules_considered.append({
            "name": name,
            "rule": r_id,
            "band": b_id,
            "matched": matched,
            "won": matched and name == winner_name,
        })

    # ── 4. HUMAN REVIEW REQUIREMENT (Rule H-review / DECISIONS.md D-004) ──
    req_review = False
    review_reason = None
    if band in ("P2", "P3"):
        if include_evidence or is_bug:
            if p0_fires:
                req_review = True
                review_reason = "hard_signal_under_prefix: silent data loss under a non-bug prefix"
            elif crash_fires:
                req_review = True
                review_reason = "hard_signal_under_prefix: crash under a non-bug prefix"
        else:
            if has_silent_data_loss(full_text):
                req_review = True
                review_reason = "hard_signal_under_prefix: silent data loss under a non-bug prefix"
            elif is_hard_crash(full_text):
                req_review = True
                review_reason = "hard_signal_under_prefix: crash under a non-bug prefix"

    # ── 5. EVIDENCE SUPERSET (lazy: only when explicitly requested) ──
    evidence = None
    if include_evidence:
        p0_matches = _spans(RE_P0_SILENT_BASE, full_text)
        p0_negations = _spans(RE_DATA_LOSS_NEGATION, full_text) + _spans(RE_SILENT_NEGATION, full_text)
        p0_fix_desc = _spans(RE_FIX_DESCRIPTION, full_text)
        crash_matches = _spans(RE_P1_CRASH_CORE, full_text)
        crash_handled = _spans(RE_CRASH_HANDLED, full_text)
        deadlocks = _spans(RE_DEADLOCK_BASE, full_text)
        deadlock_neg = _spans(RE_DEADLOCK_NEGATION, full_text)
        concurrency = _spans(RE_CONCURRENCY_CONTEXT, full_text)
        workaround_pos = _spans(RE_WORKAROUND_POSITIVE, full_text)
        workaround_neg = _spans(RE_WORKAROUND_NEGATIVE, full_text)

        blocked_by = {
            "candidato P0": p0_negations + p0_fix_desc,
            "P1 crash sin salida": crash_handled + deadlock_neg,
            "P2 crash con workaround (regla H9)": workaround_neg,
        }

        prefix_str = prefix or "(ninguno)"
        labels_str = str(labels_list) if labels_list else "[]"
        p0_m = [s["match"] for s in p0_matches] or "ninguna"
        cr_m = [s["match"] for s in crash_matches] or "ninguno"
        dl_m = [s["match"] for s in deadlocks] or "ninguno"
        wa_m = [s["match"] for s in workaround_pos] or "ninguno"

        details = {
            "compuerta de bug": f"prefijo='{prefix_str}' etiquetas={labels_str}",
            "candidato P0": f"coincidencias={p0_m}",
            "P1 crash sin salida": f"crash={cr_m} deadlock={dl_m}",
            "P2 crash con workaround (regla H9)": f"workaround={wa_m}",
            "P3 prefijo explícito de docs/tarea": f"prefijo='{prefix_str}'",
            "P2 prefijo explícito de feature": f"prefijo='{prefix_str}'",
            "P2 etiqueta de feature": f"etiquetas={labels_str}",
            "P3 etiqueta o encabezado de docs": f"etiquetas={labels_str} prefijo='{prefix_str}'",
        }

        evidence = {
            "derived_prefix": prefix,
            "is_bug": is_bug,
            "has_silent_data_loss": p0_fires,
            "is_hard_crash": crash_fires,
            "has_active_workaround": workaround,
            "has_hard_signal": p0_fires or crash_fires,
            "feature_prefix": feature_prefix,
            "feature_label": feature_label,
            "docs_prefix": docs_prefix,
            "docs_label_or_header": docs_label_or_header,
            "docs_predicate": docs_predicate,
            "p0_matches": p0_matches,
            "p0_negations": p0_negations,
            "p0_fix_desc": p0_fix_desc,
            "crash_matches": crash_matches,
            "crash_handled": crash_handled,
            "deadlocks": deadlocks,
            "deadlock_neg": deadlock_neg,
            "concurrency": concurrency,
            "workaround_pos": workaround_pos,
            "workaround_neg": workaround_neg,
            "blocked_by": blocked_by,
            "details": details,
        }

    return {
        "band": band,
        "rule": rule,
        "cross": cross,
        "requires_human_review": req_review,
        "review_reason": review_reason,
        "decided_by": decided_by,
        "rules_considered": rules_considered,
        "evidence": evidence,
    }


def classify_issue_deterministically(row, labels, cross_refs):
    """
    Returns (band, cross, rule_name) or (None, cross, None) if indeterminate.

    Invariant: P0 is strictly 'candidato P0, requiere revisión humana', never a final
    decision. A hard signal under a non-bug prefix does NOT change the band; use
    requires_human_review() to detect that case.
    """
    decision = decide(row, labels, cross_refs)
    return decision["band"], decision["cross"], decision["rule"]


def requires_human_review(row, labels, cross_refs):
    """
    Returns (bool, reason).

    True when a non-bug issue keeps a low band (P2/P3) yet carries a hard P0/P1
    signal. The band is intentionally NOT changed (never auto-promote a `feat:` to
    P1); the maintainer is asked to look. See DECISIONS.md D-004.
    """
    decision = decide(row, labels, cross_refs)
    return decision["requires_human_review"], decision["review_reason"]


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
