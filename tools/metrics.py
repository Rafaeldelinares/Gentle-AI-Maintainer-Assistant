#!/usr/bin/env python3
"""
metrics.py — Recomputes every figure the project publishes.

Nothing here is hardcoded: run it and compare with README/EVALUATION.md.
  python3 tools/metrics.py

Data source: issues.json (sanitized snapshot of the open backlog) and db/exp.db
when present (calibration sample with judge votes).
"""

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "db"))

from rules import (  # noqa: E402
    classify_issue_deterministically,
    requires_human_review,
    P0_CANDIDATE_LABEL,
)


def load_issues():
    with open(ROOT / "issues.json", "r", encoding="utf-8") as f:
        return json.load(f)


def deterministic_split(issue):
    """Reproducible split: sha256(slug#number) mod 5; group 0 is the held-out set."""
    import hashlib
    key = f"{issue['slug']}#{issue['number']}"
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % 5


def classify_all(issues):
    rows = []
    for it in issues:
        band, cross, rule = classify_issue_deterministically(
            it, it.get("labels", []), it.get("cross_refs", [])
        )
        flag, reason = requires_human_review(it, it.get("labels", []), it.get("cross_refs", []))
        rows.append({
            "issue": it, "band": band, "cross": cross, "rule": rule,
            "review_flag": flag, "review_reason": reason,
            "split": deterministic_split(it),
        })
    return rows


def pct(n, d):
    return (100.0 * n / d) if d else 0.0


def main():
    issues = load_issues()
    rows = classify_all(issues)
    total = len(rows)

    print("════════════════════════════════════════════════════════════════════")
    print(" PUBLISHED FIGURES (recomputed; nothing hardcoded)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  total open issues: {total}")

    per_repo = collections.Counter(r["issue"]["slug"] for r in rows)
    print("  per repository: " + ", ".join(f"{k}={v}" for k, v in sorted(per_repo.items())))

    # ── label census ──
    with_priority = sum(1 for r in rows if any(l.startswith("priority:") for l in (r["issue"].get("labels") or [])))
    needs_review = sum(1 for r in rows if "status:needs-review" in (r["issue"].get("labels") or []))
    print(f"\n  issues with a priority:* label:   {with_priority} ({pct(with_priority, total):.1f}%)")
    print(f"  issues without any priority:*     {total - with_priority} ({pct(total - with_priority, total):.1f}%)")
    print(f"  issues under status:needs-review: {needs_review} ({pct(needs_review, total):.1f}%)")

    # ── deterministic coverage ──
    covered = [r for r in rows if r["band"] is not None]
    print(f"\n  classified by code (no LLM): {len(covered)} ({pct(len(covered), total):.1f}%)")
    print(f"  residual grey area:          {total - len(covered)} ({pct(total - len(covered), total):.1f}%)")
    print("\n  breakdown by deterministic rule:")
    for rule, cnt in collections.Counter(r["rule"] for r in covered).most_common():
        print(f"    - {rule:44s}: {cnt:4d} ({pct(cnt, total):.1f}%)")

    band_counts = collections.Counter(str(r["band"]) for r in rows)
    print("\n  bands:")
    for band, cnt in band_counts.most_common():
        print(f"    - {band:44s}: {cnt:4d} ({pct(cnt, total):.1f}%)")

    flagged = [r for r in rows if r["review_flag"]]
    print(f"\n  flagged for human review (hard signal under a low band): {len(flagged)}")
    for reason, cnt in collections.Counter(r["review_reason"] for r in flagged).most_common():
        print(f"    - {reason}: {cnt}")

    # ── deterministic split ──
    expl = [r for r in rows if r["split"] != 0]
    held = [r for r in rows if r["split"] == 0]
    for name, group in (("exploration (groups 1-4)", expl), ("held-out (group 0)", held)):
        c = sum(1 for r in group if r["band"] is not None)
        print(f"\n  {name}: {len(group)} issues, {c} classified ({pct(c, len(group)):.1f}%)")

    # ── cross-repo linking ──
    structured = [r for r in rows if r["issue"].get("cross_refs")]
    cross_dep = [r for r in rows if r["cross"] != "none"]
    print(f"\n  issues with structured cross_refs: {len(structured)}")
    print(f"  issues with cross != none:         {len(cross_dep)}")

    # ── lexical keyword precision (documented in EVALUATION.md) ──
    shell = [r for r in rows if r["issue"]["slug"] == "gentle-shell"]
    mentions = [r for r in shell if "gentle-ai" in f"{r['issue'].get('title') or ''}\n{r['issue'].get('body') or ''}".lower()]
    confirmed = [
        r for r in mentions
        if any(cr.get("target_system_id") != r["issue"].get("system_id") for cr in (r["issue"].get("cross_refs") or []))
    ]
    print(f"\n  gentle-shell issues mentioning 'gentle-ai': {len(mentions)}")
    print(f"  of those with a confirmed cross_ref:        {len(confirmed)}")
    if mentions:
        print(f"  lexical keyword precision:                  {pct(len(confirmed), len(mentions)):.1f}% ({len(confirmed)}/{len(mentions)})")

    # ── board: derived distribution per application (what the engine would suggest) ──
    try:
        sys.path.insert(0, str(ROOT / "board"))
        import core as board_core  # noqa: E402
        per_slug = collections.defaultdict(collections.Counter)
        for issue in issues:
            card = board_core.derive_card(issue)
            suggested = card["suggested_column"] or "entrada"
            per_slug[card["slug"]][suggested] += 1
        print("\n  board: derived column distribution per application (before any human move)")
        for slug in sorted(per_slug):
            total_cards = sum(per_slug[slug].values())
            detail = ", ".join(f"{col}={per_slug[slug].get(col, 0)}" for col in board_core.COLUMNS)
            print(f"    - {slug:14s} total={total_cards:4d} | {detail}")
    except Exception as exc:  # pragma: no cover
        print(f"\n  board: derived distribution unavailable ({exc})")

    # ── calibration sample from exp.db (optional) ──
    db = ROOT / "db" / "exp.db"
    if db.exists():
        import sqlite3
        conn = sqlite3.connect(db)
        try:
            cur = conn.execute("SELECT COUNT(*) FROM run_issues WHERE run_id = 1")
            n_sample = cur.fetchone()[0]
            print(f"\n  calibration sample (exp.db run 1): {n_sample} issues")
            print("  agreement figures are printed by 'python3 db/rules.py' section 2")
        finally:
            conn.close()
    else:
        print("\n  calibration sample: db/exp.db not present (figures unavailable)")

    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
