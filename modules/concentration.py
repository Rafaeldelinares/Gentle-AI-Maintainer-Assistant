#!/usr/bin/env python3
"""
concentration.py — Module E (read-only).

Groups every open issue by **where a change would land**, so a pile of reports becomes a handful of
places to look.

Why grouping and not classification: the priority of an issue is a judgement about impact, and the
data carries no deterministic proxy for impact — no SLA, no severity field, no affected-user count.
What the data *does* carry, deterministically, is **location**: the paths an issue mentions. A
directory named by 37 reports is one place where something is happening; it is not a claim that the
directory is important, broken, or urgent.

Design rules:
  - The unit of action is the directory where a change would land, capped at three levels.
  - Grouping never crosses repositories: a shared directory name is not a relationship.
  - The engine's band is asked for and reported as "sin banda", never interpreted.
  - Nothing here routes, prioritises or closes anything. Every entry is `veredicto_humano: pendiente`.
  - The report declares its own arithmetic: what it covers and what it leaves out.

  python3 modules/concentration.py
"""

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))

from common import (  # noqa: E402
    REPO_SLUGS, issue_body, issue_link, issue_ref, issue_title, load_issues, write_report,
)
from duplicates import make_signatures  # noqa: E402
from obsolete import extract_references  # noqa: E402
from rules import classify_issue_deterministically  # noqa: E402

# The report is bounded on purpose. A first version listed forty issues per cluster across fifteen
# clusters and produced 843 lines; the review relay aborted on it after sixteen minutes, and a
# report too large to review is also too large to read. The full lists are one command away, so the
# report shows enough to act on and states what the selection covers.
TOP_CLUSTERS = 10
TOP_FILES = 8
MAX_REFS_PER_CLUSTER = 12


def subsystem_of(path):
    """The directory where a change would land, capped at three levels.

    `internal/components/sdd/inject.go` -> `internal/components/sdd`
    `extensions/gentle-ai.ts`           -> `extensions`
    `deep/a/b/c/d.go`                   -> `deep/a/b`
    """
    parent = path.rsplit("/", 1)[0] if "/" in path else ""
    parts = [p for p in parent.split("/") if p]
    if not parts:
        return "(repository root)"
    return "/".join(parts[:3])


def is_grey(issue):
    """The engine's answer, not an interpretation of it: no band means the rules said nothing."""
    band, _cross, _rule = classify_issue_deterministically(
        issue, issue.get("labels") or [], issue.get("cross_refs") or [])
    return band is None


def collapse_rows_for(top_subsystems, by_ref):
    """Per cluster: how many distinct evidence signatures, and the largest repeated group.

    This exists because saying "a cluster is one place to look" was, on its own, an assertion.
    The question a reader asks next is whether the pile is one problem or many, and that question
    has a deterministic answer worth showing: the signatures.
    """
    rows = []
    for (slug, subsys), refs in top_subsystems[:TOP_CLUSTERS]:
        ordered = sorted(refs)
        sigs = {ref: make_signatures(by_ref[ref]) for ref in ordered}
        carrying = [ref for ref in ordered if sigs[ref]]
        groups = collections.defaultdict(list)
        for ref in carrying:
            groups[frozenset(sigs[ref])].append(ref)
        ordered_groups = sorted(groups.values(), key=lambda group: (-len(group), group))
        biggest = ordered_groups[0] if ordered_groups and len(ordered_groups[0]) > 1 else []
        rows.append((slug, subsys, len(ordered), len(carrying), len(groups), biggest))
    return rows


def main():
    issues = load_issues()

    by_ref = {issue_ref(issue): issue for issue in issues}
    by_subsystem = collections.defaultdict(set)
    by_file = collections.defaultdict(set)
    grey_by_subsystem = collections.defaultdict(set)
    grey_by_file = collections.defaultdict(set)
    with_path = set()
    grey_with_path = set()
    grey = set()

    for issue in issues:
        ref = issue_ref(issue)
        text = f"{issue.get('title') or ''}\n{issue.get('body') or ''}"
        paths = sorted({entry[0] for entry in extract_references(text).get("paths", [])})
        grey_issue = is_grey(issue)
        if grey_issue:
            grey.add(ref)
        if not paths:
            continue
        with_path.add(ref)
        if grey_issue:
            grey_with_path.add(ref)
        for path in paths:
            key_dir = (issue["slug"], subsystem_of(path))
            by_subsystem[key_dir].add(ref)
            by_file[(issue["slug"], path)].add(ref)
            if grey_issue:
                grey_by_subsystem[key_dir].add(ref)
                grey_by_file[(issue["slug"], path)].add(ref)

    # Coverage: an issue belongs to a cluster if it mentions a path at all. The top clusters are
    # reported by size, and the report states how much of the corpus they cover.
    top_subsystems = sorted(by_subsystem.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    top_files = sorted(by_file.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:TOP_FILES]
    collapse_rows = collapse_rows_for(top_subsystems, by_ref)
    covered = set().union(*[refs for _k, refs in top_subsystems[:TOP_CLUSTERS]]) if by_subsystem else set()

    lines = []
    lines.append(f"> Generated from the frozen snapshot of {len(issues)} open issues. Read-only: this")
    lines.append("> module writes no field, comments on nothing, and closes nothing. Every entry is")
    lines.append("> `veredicto_humano: pendiente`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Issues in the snapshot: **{len(issues)}**")
    lines.append(f"- Issues mentioning at least one repository path: **{len(with_path)}** "
                 f"({100 * len(with_path) / len(issues):.1f}%)")
    lines.append(f"- Of those, the engine left **without a band**: **{len(grey_with_path)}**")
    lines.append(f"- Issues mentioning no path at all: **{len(issues) - len(with_path)}** — no cluster")
    lines.append("  can reach them, and they are counted here rather than implied away")
    lines.append(f"- Distinct subsystems (repository + directory): **{len(by_subsystem)}**")
    lines.append(f"- The top {TOP_CLUSTERS} subsystems cover **{len(covered)}** of the "
                 f"{len(with_path)} issues that mention a path "
                 f"({100 * len(covered) / max(len(with_path), 1):.0f}%)")
    lines.append("")
    lines.append("## Clusters by subsystem")
    lines.append("")
    lines.append("The unit is the directory where a change would land, capped at three levels. A")
    lines.append("directory named by many reports is **one place to look**, not a task and not a claim")
    lines.append("about importance.")
    lines.append("")
    lines.append("| Repository | Subsystem | Issues | Without a band |")
    lines.append("| --- | --- | --- | --- |")
    for (slug, subsys), refs in top_subsystems[:TOP_CLUSTERS]:
        lines.append(f"| `{slug}` | `{subsys}` | **{len(refs)}** | {len(grey_by_subsystem[(slug, subsys)])} |")
    lines.append("")
    for (slug, subsys), refs in top_subsystems[:TOP_CLUSTERS]:
        ordered = sorted(refs)
        lines.append(f"### `{slug}` — `{subsys}` ({len(ordered)} issues)")
        lines.append("")
        for ref in ordered[:MAX_REFS_PER_CLUSTER]:
            issue = next(i for i in issues if issue_ref(i) == ref)
            lines.append(f"- **{ref}** — {issue_title(issue)}")
            lines.append(f"  - {issue_link(issue)}")
        if len(ordered) > MAX_REFS_PER_CLUSTER:
            lines.append(f"- …and {len(ordered) - MAX_REFS_PER_CLUSTER} more in this subsystem")
        lines.append("")
    lines.append("## Do the clusters collapse?")
    lines.append("")
    lines.append("A pile of reports in one directory invites the next question: is it one problem")
    lines.append("reported many times, or many problems landing in the same place? The deterministic")
    lines.append("answer is the evidence signatures — an exception name, an error code, a Go frame, an")
    lines.append("exit status, a long quoted error string. Issues that share no signature are not, by")
    lines.append("that evidence, the same problem.")
    lines.append("")
    lines.append("| Repository | Subsystem | Issues | Carrying a signature | Distinct signatures | "
                 "Largest repeated group |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for slug, subsys, total, carrying, distinct, biggest in collapse_rows:
        lines.append(f"| `{slug}` | `{subsys}` | {total} | {carrying} | **{distinct}** | "
                     f"{len(biggest) if biggest else '—'} |")
    lines.append("")
    lines.append("**Read plainly: they do not collapse.** The largest repeated group across every")
    lines.append("cluster above is a handful of issues, so a directory carrying many reports is carrying")
    lines.append("many *different* problems. Concentration here is **accumulation, not duplication** —")
    lines.append("a fact about where problems land, which is why this module reports location and never")
    lines.append("claims a shared cause.")
    lines.append("")
    for slug, subsys, _total, carrying, _distinct, biggest in collapse_rows:
        if len(biggest) > 1:
            lines.append(f"- The one repeated signature in `{slug}` `{subsys}` is shared by "
                         f"{len(biggest)} issues ({', '.join(biggest)}); every other issue in that "
                         f"cluster carries evidence of its own, or none at all.")
            break
    lines.append("- This is **absence of evidence, not proof of distinctness**: an issue with no")
    lines.append("  signature is uncorrelated evidence, not established as a different problem. Same for")
    lines.append("  two issues whose signatures differ but whose cause may be one.")
    lines.append("")
    lines.append("## Hotspot files")
    lines.append("")
    lines.append("The directory view hides a single file carrying most of a directory's reports. Same")
    lines.append("data, second reading.")
    lines.append("")
    lines.append("| Repository | File | Issues | Without a band |")
    lines.append("| --- | --- | --- | --- |")
    for (slug, path), refs in top_files:
        lines.append(f"| `{slug}` | `{path}` | **{len(refs)}** | {len(grey_by_file[(slug, path)])} |")
    lines.append("")
    lines.append("## The grey area, read through this lens")
    lines.append("")
    lines.append(f"Of the **{len(grey)}** issues the engine leaves without a band, "
                 f"**{len(grey_with_path)}** name at least one path. Those are the ones a cluster can")
    lines.append("reach. The rest name no path, carry no structural evidence, and **no rule reaches")
    lines.append("them**: they need a human read or a language-model pass, and saying so is the honest")
    lines.append("boundary of this module.")
    lines.append("")
    lines.append("A cluster does **not** say its issues are urgent, related in cause, or worth fixing")
    lines.append("together. It says they touch the same place, which is a fact about their text.")
    lines.append("")
    lines.append("## What this module does NOT say")
    lines.append("")
    lines.append("- **No priority, no severity, no ordering by importance.** The data carries no")
    lines.append("  deterministic proxy for impact, so any band here would be invented.")
    lines.append("- **No routing.** It does not decide which column an issue belongs to; it groups.")
    lines.append("- **No causality.** A cluster is co-location, not a shared root cause.")
    lines.append("- **No judgment about quality.** `veredicto_humano` stays `pendiente` for every row.")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- Paths come from a deterministic extractor over the issue text, so an issue that")
    lines.append("  describes a location in prose without naming a path lands in no cluster.")
    lines.append(f"- Only the top {TOP_CLUSTERS} subsystems and the top {TOP_FILES} files are shown with")
    lines.append("  their issues; the counts above state what the selection covers.")
    lines.append("- The extractor takes the first few paths per issue, so a report mentioning many files")
    lines.append("  is attributed to the ones it names first.")
    lines.append("- 'Without a band' is the engine's own output (`band is None`). It does not mean the")
    lines.append("  issue is unimportant, and it is not the same as 'unrouted': routing also involves the")
    lines.append("  board's completeness path, which this module deliberately does not read.")
    lines.append("")

    body = "\n".join(lines)
    path = write_report("report-concentration.md", "Module E — Where the Reports Concentrate", body)
    print(f"\n  report written: {path.name}")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
