#!/usr/bin/env python3
"""
duplicates.py — Module B (read-only).

Finds probable duplicate open issues inside the same repository using deterministic
evidence: a shared rare error signature (exception class, error code, file:line frame,
quoted error string, exit code) or near-identical normalized titles.

Design decisions:
  - Only same-repository pairs. A cross-repository duplicate is a linking question,
    handled by Module C.
  - A signature is "rare" when it appears in few issues; common strings carry no signal.
  - Titles are normalized (prefix, versions, numbers, punctuation removed) so that
    "bug(cli): review fails with ENOENT" and "fix: ENOENT on review" converge.
  - Every pair is presented with its shared evidence and is marked
    `veredicto_humano: pendiente`. **Nothing is closed, merged or commented.**

  python3 modules/duplicates.py
"""

import collections
import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    load_issues, issue_body, issue_link, issue_ref, issue_title,
    strip_emoji_and_punct, write_report, first_sentence,
)

PREFIX_RE = re.compile(
    r"^\s*(?:[`'\"\[]+\s*|\[[^\]]*\]\s*)*(?:feat|feature|fix|bug|docs?|chore|typo|refactor|test|ci|perf|style|question|review|meta|security)\b[^:]*:\s*",
    re.IGNORECASE,
)
VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+){1,3}\b")
HEX_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+\b")

STOPWORDS = {
    "bug", "fix", "feat", "feature", "docs", "chore", "review", "issue", "issues",
    "please", "when", "with", "from", "that", "this", "have", "has", "does", "doesn",
    "isn", "not", "the", "and", "for", "are", "was", "were", "you", "your", "our",
    "can", "cannot", "will", "would", "should", "into", "after", "before", "using",
    "use", "used", "gets", "get", "run", "running", "error", "errors",
}

EXCEPTION_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:Error|Exception|Panic))\b")
ERROR_CODE_RE = re.compile(r"\b(TS\d{4}|E[A-Z]{3,}|ERR_[A-Z0-9_]+|ENOENT|EACCES|EMFILE|EPERM|EEXIST|EINVAL)\b")
FRAME_RE = re.compile(r"\b([\w./-]+\.(?:go|ts|tsx|js|jsx|py|rs|java|kt|rb|c|cpp|h))(?:[\"']?[,:]|\", line )(\d+)\b")
GOROUTINE_RE = re.compile(r"\bgoroutine \d+ \[" )
QUOTED_RE = re.compile(r"[\"'`]([^\"'`\n]{18,90})[\"'`]")
EXIT_RE = re.compile(r"\b(?:exit(?:ed)?(?: with)?(?: code)?|status)\s*(\d{1,3})\b", re.IGNORECASE)
ERRORISH = re.compile(r"error|fail|denied|refus|timeout|invalid|missing|unable|cannot|unsupported|panic|corrupt", re.IGNORECASE)


def normalize_title(title):
    text = PREFIX_RE.sub("", title or "")
    text = text.lower()
    text = VERSION_RE.sub(" ", text)
    text = HEX_RE.sub(" ", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = NUMBER_RE.sub(" ", text)
    tokens = [t for t in text.split() if len(t) >= 3 and t not in STOPWORDS]
    return tokens


def make_signatures(issue):
    """Returns a set of deterministic evidence strings."""
    body = issue_body(issue)
    sigs = set()
    for m in EXCEPTION_RE.finditer(body):
        sigs.add(f"exc:{m.group(1).lower()}")
    for m in ERROR_CODE_RE.finditer(body):
        sigs.add(f"code:{m.group(1).upper()}")
    for m in FRAME_RE.finditer(body):
        sigs.add(f"frame:{m.group(1).lower()}:{m.group(2)}")
    if GOROUTINE_RE.search(body):
        sigs.add("dump:goroutine")
    for m in QUOTED_RE.finditer(body):
        value = m.group(1).strip()
        if ERRORISH.search(value) and len(value) >= 18:
            sigs.add("quoted:" + re.sub(r"\s+", " ", value.lower())[:70])
    for m in EXIT_RE.finditer(body):
        sigs.add(f"exit:{m.group(1)}")
    return sigs


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    issues = load_issues()

    titles = {}
    signatures = {}
    for issue in issues:
        key = issue_ref(issue)
        titles[key] = normalize_title(issue_title(issue))
        signatures[key] = make_signatures(issue)

    # Signature rarity inside each repository.
    df = collections.Counter()
    for issue in issues:
        for sig in signatures[issue_ref(issue)]:
            df[(issue["slug"], sig)] += 1
    RARE_MAX = 4

    by_key = {issue_ref(i): i for i in issues}

    pairs = {}

    def add_pair(a, b, score, tier, evidence):
        if a == b:
            return
        x, y = sorted((a, b))
        current = pairs.get((x, y))
        if current is None or score > current["score"]:
            pairs[(x, y)] = {"score": score, "tier": tier, "evidence": sorted(set(evidence))}

    # Candidate pairs from shared rare signatures.
    sig_index = collections.defaultdict(list)
    for issue in issues:
        for sig in signatures[issue_ref(issue)]:
            if df[(issue["slug"], sig)] <= RARE_MAX:
                sig_index[(issue["slug"], sig)].append(issue_ref(issue))

    for (slug, sig) in sorted(sig_index):
        members = sig_index[(slug, sig)]
        if len(members) < 2:
            continue
        for a, b in itertools.combinations(sorted(members), 2):
            shared = {s for s in signatures[a] & signatures[b] if df[(slug, s)] <= RARE_MAX}
            ja = jaccard(titles[a], titles[b])
            title_equal = titles[a] == titles[b] and len(titles[a]) >= 3
            sig_overlap = 0.0
            if shared:
                smallest = min(len(signatures[a]), len(signatures[b]))
                sig_overlap = len(shared) / smallest if smallest else 0.0
            if title_equal:
                add_pair(a, b, 95, "high", ["title:identical"])
            elif len(shared) >= 2 and sig_overlap >= 0.6:
                add_pair(a, b, 85 + int(sig_overlap * 10), "high", shared)
            elif len(shared) >= 1 and ja >= 0.75:
                add_pair(a, b, 84, "high", shared)
            elif len(shared) >= 2:
                add_pair(a, b, 58, "medium", shared)
            elif len(shared) == 1:
                add_pair(a, b, 50, "medium", shared)

    # Candidate pairs from near-identical titles (token index to avoid O(n^2)).
    token_index = collections.defaultdict(list)
    for issue in issues:
        for token in sorted(set(titles[issue_ref(issue)])):
            token_index[(issue["slug"], token)].append(issue_ref(issue))

    for (slug, token) in sorted(token_index):
        members = token_index[(slug, token)]
        if len(members) < 2 or len(members) > 40:
            continue
        for a, b in itertools.combinations(sorted(members), 2):
            ja = jaccard(titles[a], titles[b])
            if ja >= 0.8 and len(titles[a]) >= 3 and len(titles[b]) >= 3:
                shared = [f"title-jaccard:{ja:.2f}"]
                add_pair(a, b, 60 + int(ja * 30), "medium", shared)

    order = {"high": 0, "medium": 1}
    # A total ordering: score, tier, then the pair keys, so the report is byte-identical
    # across processes regardless of PYTHONHASHSEED-driven set iteration order.
    ranked = sorted(pairs.items(), key=lambda kv: (-kv[1]["score"], order.get(kv[1]["tier"], 2), kv[0][0], kv[0][1]))

    high = [kv for kv in ranked if kv[1]["tier"] == "high"]
    medium = [kv for kv in ranked if kv[1]["tier"] == "medium"]
    by_repo = collections.Counter(by_key[a]["slug"] for (a, _b) in [kv[0] for kv in ranked])

    print("════════════════════════════════════════════════════════════════════")
    print(" MODULE B — PROBABLE DUPLICATES (same repository)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  issues analysed:      {len(issues)}")
    print(f"  candidate pairs:      {len(ranked)}")
    print(f"  strong-evidence pairs:{len(high)}")
    print(f"  weaker-evidence pairs:{len(medium)}")
    for slug, cnt in by_repo.most_common():
        print(f"    - {slug}: {cnt}")

    lines = []
    lines.append("> **Read-only module.** Finds probable duplicate open issues in the same repository using deterministic evidence: a shared rare error signature (exception class, error code, `file:line` frame, quoted error string, exit code) or near-identical normalized titles.")
    lines.append(">")
    lines.append("> **It never closes, merges or comments.** Every pair is a suggestion with its shared evidence, and every entry is `veredicto_humano: pendiente`.")
    lines.append(">")
    lines.append("> Reproduce with `python3 modules/duplicates.py`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Issues analysed | {len(issues)} |")
    lines.append(f"| Candidate duplicate pairs | {len(ranked)} |")
    lines.append(f"| Strong-evidence pairs | {len(high)} |")
    lines.append(f"| Weaker-evidence pairs | {len(medium)} |")
    lines.append("")
    lines.append("### Candidate pairs by repository")
    lines.append("")
    lines.append("| Repository | Candidate pairs |")
    lines.append("| --- | --- |")
    for slug, cnt in by_repo.most_common():
        lines.append(f"| `{slug}` | {cnt} |")
    lines.append("")
    lines.append("### Evidence types")
    lines.append("")
    lines.append("| Evidence prefix | Meaning |")
    lines.append("| --- | --- |")
    lines.append("| `exc:` | exception or panic class (e.g. `NullPointerException`) |")
    lines.append("| `code:` | error code (e.g. `TS6306`, `ENOENT`) |")
    lines.append("| `frame:` | `file:line` from a stack trace |")
    lines.append("| `quoted:` | quoted error string containing an error keyword |")
    lines.append("| `exit:` | exit code |")
    lines.append("| `dump:goroutine` | goroutine dump present |")
    lines.append("| `title-*` | normalized-title similarity |")
    lines.append("")
    lines.append("> **\"Strong evidence\" means the pair shares distinctive identifiers, not that it is certainly a duplicate.** Two sibling issues that implement the same feature often share exception names and configuration strings. The tier orders the maintainer's reading; it never decides.")
    lines.append("")

    for tier, subset in (("Strong-evidence", high), ("Weaker-evidence", medium)):
        lines.append(f"## {tier} pairs (up to 30)")
        lines.append("")
        if not subset:
            lines.append("_None._")
            lines.append("")
            continue
        for (a, b), meta in subset[:30]:
            ia, ib = by_key[a], by_key[b]
            lines.append(f"### {a} <> {b}")
            lines.append(f"- **A:** {issue_title(ia)[:120]}")
            lines.append(f"  - {issue_link(ia)}")
            lines.append(f"- **B:** {issue_title(ib)[:120]}")
            lines.append(f"  - {issue_link(ib)}")
            lines.append(f"- **Shared evidence:** {', '.join(meta['evidence'])}")
            lines.append(f"- **veredicto_humano:** pendiente")
            lines.append("")

    lines.append("## Limits")
    lines.append("")
    lines.append("- Only **same-repository** pairs. Cross-repository duplication is a linking question (Module C).")
    lines.append("- A shared signature is evidence, not proof: the same error can come from different causes.")
    lines.append("- Issues without stack traces or distinctive strings cannot be matched, so this module under-reports rather than over-reports on prose-only reports.")
    lines.append("- No semantic similarity, no LLM: the module is deterministic and reproducible.")
    lines.append("")

    body = "\n".join(lines)
    path = write_report("report-duplicates.md", "Module B — Probable Duplicates", body)
    print(f"\n  report written: {path.name}")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
