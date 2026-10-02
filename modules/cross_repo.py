#!/usr/bin/env python3
"""
cross_repo.py — Module C (read-only).

Finds cross-repository references that are **not** captured by the structured
`cross_refs` field, so the maintainer can decide whether a link belongs there.

Three evidence levels, strongest first:
  1. `owner/repo#N` or `repo#N` where N resolves to an open issue in the snapshot.
  2. `owner/repo` reference without a number (a repository mention, no link proposed).
  3. bare repository-name mention in prose (recorded as the weakest signal).

Design rules:
  - Only explicit references produce a proposed link. A bare slug mention never does.
  - The module never writes `cross_refs`, never comments, never labels.
  - Every entry is `veredicto_humano: pendiente`.

  python3 modules/cross_repo.py
"""

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    load_issues, issue_body, issue_link, issue_ref, issue_title, issue_text,
    REPO_SLUGS, write_report, first_sentence,
)

OWNER_PATTERN = r"(?:Gentleman-Programming|gentleman-programming)"

# owner/repo#N or repo#N
REF_WITH_NUMBER = re.compile(
    rf"(?:(?P<owner>{OWNER_PATTERN})/)?(?P<repo>gentle-ai|engram|gentle-shell)#(?P<num>\d+)",
    re.IGNORECASE,
)
# owner/repo without a number
REF_NO_NUMBER = re.compile(
    rf"{OWNER_PATTERN}/(?P<repo>gentle-ai|engram|gentle-shell)\b",
    re.IGNORECASE,
)
# bare repository-name mention
BARE_MENTION = re.compile(r"\b(gentle-ai|engram|gentle-shell)\b", re.IGNORECASE)


def main():
    issues = load_issues()
    index = {(i["slug"], i["number"]): i for i in issues}
    print("════════════════════════════════════════════════════════════════════")
    print(" MODULE C — CROSS-REPOSITORY REFERENCES NOT IN cross_refs")
    print("════════════════════════════════════════════════════════════════════")

    already = [i for i in issues if i.get("cross_refs")]
    print(f"  issues with structured cross_refs: {len(already)}")

    proposals = []          # explicit repo#N resolving to an open issue
    repo_refs_no_number = []  # owner/repo without a number
    mentions_only = []      # bare slug mention

    for issue in issues:
        text = issue_text(issue)
        seen = set()

        for m in REF_WITH_NUMBER.finditer(text):
            target_repo = m.group("repo").lower()
            target_num = int(m.group("num"))
            if target_repo == issue["slug"]:
                continue
            key = (target_repo, target_num)
            if key in seen:
                continue
            seen.add(key)
            resolves = key in index
            proposals.append({
                "issue": issue,
                "target_repo": target_repo,
                "target_num": target_num,
                "resolves": resolves,
                "quote": first_sentence(text[max(0, m.start() - 40):m.end() + 40]),
                "kind": "team-reference" if m.group("owner") else "issue-reference",
            })

        for m in REF_NO_NUMBER.finditer(text):
            target_repo = m.group("repo").lower()
            if target_repo == issue["slug"]:
                continue
            repo_refs_no_number.append({
                "issue": issue,
                "target_repo": target_repo,
                "quote": first_sentence(text[max(0, m.start() - 40):m.end() + 40]),
            })

        if not issue.get("cross_refs"):
            others = {s for s in REPO_SLUGS if s != issue["slug"] and BARE_MENTION.search(text)}
            if others:
                mentions_only.append({"issue": issue, "others": sorted(others)})

    resolving = [p for p in proposals if p["resolves"]]
    non_resolving = [p for p in proposals if not p["resolves"]]
    issues_with_proposal = {issue_ref(p["issue"]) for p in proposals}

    print(f"  explicit references to another repo: {len(proposals)}")
    print(f"    - resolving to an open issue:      {len(resolving)}")
    print(f"    - not resolving:                   {len(non_resolving)}")
    print(f"  issues with >=1 explicit reference:  {len(issues_with_proposal)}")
    print(f"  owner/repo references without number:{len(repo_refs_no_number)}")
    print(f"  bare slug mentions, no cross_refs:   {len(mentions_only)}")

    by_target = collections.Counter(p["target_repo"] for p in resolving)
    by_pair = collections.Counter((p["issue"]["slug"], p["target_repo"]) for p in resolving)

    lines = []
    lines.append("> **Read-only module.** Looks for cross-repository references that are **not** in the structured `cross_refs` field, so a maintainer can decide whether a link belongs there.")
    lines.append(">")
    lines.append("> **It proposes; it never links.** Nothing is written to `cross_refs`, and every entry is `veredicto_humano: pendiente`.")
    lines.append(">")
    lines.append("> Reproduce with `python3 modules/cross_repo.py`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Issues with a structured `cross_refs` entry | {len(already)} |")
    lines.append(f"| Explicit references to another repo (`repo#N`) | {len(proposals)} |")
    lines.append(f"| — resolving to an open issue in the snapshot | {len(resolving)} |")
    lines.append(f"| — not resolving (closed, renamed, or a typo) | {len(non_resolving)} |")
    lines.append(f"| Issues carrying at least one explicit reference | {len(issues_with_proposal)} |")
    lines.append(f"| `owner/repo` reference without a number | {len(repo_refs_no_number)} |")
    lines.append(f"| Bare repository-name mention, no `cross_refs` | {len(mentions_only)} |")
    lines.append("")
    lines.append("### Explicit references by target repository")
    lines.append("")
    lines.append("| Target repository | References |")
    lines.append("| --- | --- |")
    for slug, cnt in by_target.most_common():
        lines.append(f"| `{slug}` | {cnt} |")
    lines.append("")
    lines.append("### Reference direction")
    lines.append("")
    lines.append("| From -> To | References |")
    lines.append("| --- | --- |")
    for (src, dst), cnt in by_pair.most_common():
        lines.append(f"| `{src}` -> `{dst}` | {cnt} |")
    lines.append("")
    lines.append("## Proposed links (explicit reference, target is open)")
    lines.append("")
    lines.append("Each row cites the exact reference. The maintainer decides whether to record it in `cross_refs`.")
    lines.append("")
    for p in resolving[:60]:
        issue = p["issue"]
        target = index[(p["target_repo"], p["target_num"])]
        lines.append(f"- **{issue_ref(issue)}** -> **{p['target_repo']}#{p['target_num']}**")
        lines.append(f"  - Source: {issue_link(issue)} — {issue_title(issue)[:100]}")
        lines.append(f"  - Target: {issue_link(target)} — {issue_title(target)[:100]}")
        lines.append(f"  - Reference: {p['kind']} — \"{p['quote']}\"")
        lines.append(f"  - veredicto_humano: pendiente")
        lines.append("")
    if not resolving:
        lines.append("_None._")
        lines.append("")
    lines.append("## Explicit references that do not resolve (first 20)")
    lines.append("")
    lines.append("The target number is not an open issue in the snapshot: it may be closed, renamed, or a typo. Recorded but not proposed.")
    lines.append("")
    for p in non_resolving[:20]:
        issue = p["issue"]
        lines.append(f"- **{issue_ref(issue)}** -> `{p['target_repo']}#{p['target_num']}` — {issue_link(issue)}")
        lines.append(f"  - Reference: \"{p['quote']}\"")
        lines.append(f"  - veredicto_humano: pendiente")
    if not non_resolving:
        lines.append("_None._")
    lines.append("")
    lines.append("## Repository mentions without a link (weakest signal)")
    lines.append("")
    lines.append(f"{len(mentions_only)} issues mention another repository by name with no structured link. A name mention is **not** evidence of dependency: install instructions, comparisons and unrelated prose all mention repositories. No link is proposed for these.")
    lines.append("")
    for m in mentions_only[:20]:
        issue = m["issue"]
        lines.append(f"- **{issue_ref(issue)}** mentions {', '.join('`'+o+'`' for o in m['others'])} — {issue_link(issue)}")
        lines.append(f"  - veredicto_humano: pendiente")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- A bare repository-name mention never produces a proposed link; only an explicit `repo#N` reference does.")
    lines.append("- The module cannot tell a dependency from a comparison, so it reports; it does not classify.")
    lines.append("- Numbers are resolved against the open-issue snapshot only; a closed target appears as non-resolving.")
    lines.append("")

    body = "\n".join(lines)
    path = write_report("report-cross-links.md", "Module C — Cross-Repository References", body)
    print(f"\n  report written: {path.name}")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
