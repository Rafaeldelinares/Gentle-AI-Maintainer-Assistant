#!/usr/bin/env python3
"""
completeness.py — Module A (read-only).

Compares every open bug/feature report against the required fields of its own
repository's GitHub issue form and lists what is missing.

Rationale: a maintainer triaging 40 issues spends most of the time asking for the
information the template already requested. This module answers, per issue, "can this
be triaged now, or is it missing required fields?" — without contacting anyone.

Honesty rules built in:
  - An issue that contains none of the template headings is reported as "outside the
    form" (filed before the template existed, or an automated provider report) and is
    NOT counted in the missing-fields metric.
  - Attestation checkboxes (pre-flight / before-submitting) are reported separately
    from triage-critical content, because a missing checkbox is not missing information.
  - Nothing is applied; the maintainer decides.

  python3 modules/completeness.py
"""

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    load_issues, issue_body, issue_link, issue_ref, issue_title,
    is_bug_issue, is_feature_issue, strip_emoji_and_punct, write_report,
)
from templates import all_repo_templates, required_fields  # noqa: E402

HEADING_ANY = re.compile(r"^#{2,4}\s+(.*)$", re.MULTILINE)
HEADING_FORM = re.compile(r"^###\s+(.*)$", re.MULTILINE)
PLACEHOLDER_LINE = re.compile(r"^\s*(?:-?\s*\[[ xX]\]|\d+\.|```\s*$|```[a-z]*\s*$)\s*$")

TEMPLATE_FILENAMES = {"bug": "bug_report", "feature": "feature_request"}


def split_sections(body, form_only=True):
    """
    Returns {normalized_heading: raw_content}.

    form_only=True uses `###` headings, which is exactly what a GitHub issue form renders;
    it is the signal for "this issue was filed through the form". form_only=False also
    accepts `##`/`####`, used as a fallback when checking whether a field is present.
    """
    sections = {}
    pattern = HEADING_FORM if form_only else HEADING_ANY
    matches = list(pattern.finditer(body))
    for i, m in enumerate(matches):
        name = strip_emoji_and_punct(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        if name and name not in sections:
            sections[name] = body[start:end]
    return sections


def content_is_empty(content):
    if content is None:
        return True
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if PLACEHOLDER_LINE.match(line):
            continue
        return False
    return True


def _core_label(label):
    """Label without emoji/punctuation, for inline matching ('**Gentle AI Version:** x')."""
    return strip_emoji_and_punct(label)


def _inline_value(body, label):
    """
    Returns the inline value for a bold/plain label, or None when absent.

    GitHub renders an input field as `**Label:** value` inside a section, not as a `###`
    heading; both renderings must count as present.
    """
    core = _core_label(label)
    if not core:
        return None
    words = [re.escape(w) for w in core.split(" ") if w]
    if not words:
        return None
    pattern = r"\*{0,2}\s*" + r"\s+".join(words) + r"\s*\*{0,2}\s*:?"
    m = re.search(pattern, body, re.IGNORECASE)
    if not m:
        return None
    return body[m.end():m.end() + 160]


def label_status(body, sections, required_label, any_sections=None):
    """Returns 'present', 'empty' or 'missing' for a required template label."""
    target = _core_label(required_label)
    if not target:
        return "missing"
    pools = [sections] if any_sections is None else [sections, any_sections]
    found = []
    for pool in pools:
        for heading, content in pool.items():
            if heading == target or target in heading or heading in target:
                found.append(content)
    if found:
        return "present" if any(not content_is_empty(c) for c in found) else "empty"
    inline = _inline_value(body, required_label)
    if inline is not None:
        cleaned = re.sub(r"[*\s:]", "", inline.splitlines()[0] if inline.splitlines() else "")
        return "present" if len(cleaned) >= 2 else "empty"
    return "missing"


def kind_of(issue):
    if is_bug_issue(issue):
        return "bug"
    if is_feature_issue(issue):
        return "feature"
    return None


def main():
    issues = load_issues()
    templates = all_repo_templates()

    print("════════════════════════════════════════════════════════════════════")
    print(" MODULE A — COMPLETENESS AGAINST THE REPOSITORY ISSUE FORM")
    print("════════════════════════════════════════════════════════════════════")

    template_fields = {}
    for slug, kinds in sorted(templates.items()):
        for kind, fields in sorted(kinds.items()):
            req = required_fields(fields)
            template_fields[(slug, kind)] = req
            content = [f for f in req if f["type"] != "checkboxes"]
            attest = [f for f in req if f["type"] == "checkboxes"]
            print(f"  {slug}/{kind}: {len(content)} required content fields, {len(attest)} attestation(s)")

    in_form, outside_form = [], []
    for issue in issues:
        kind = kind_of(issue)
        if kind is None:
            continue
        req = template_fields.get((issue["slug"], kind))
        if not req:
            continue
        form_sections = split_sections(issue_body(issue), form_only=True)
        any_sections = split_sections(issue_body(issue), form_only=False)
        body = issue_body(issue)
        content_fields = [f for f in req if f["type"] != "checkboxes"]
        attest_fields = [f for f in req if f["type"] == "checkboxes"]

        matched_headings = sum(
            1 for f in req if f.get("label") and label_status(body, form_sections, f["label"], any_sections) != "missing"
        )
        content_missing = [
            (f["label"], label_status(body, form_sections, f["label"], any_sections)) for f in content_fields
            if label_status(body, form_sections, f["label"], any_sections) != "present"
        ]
        attested = [
            (f["label"], label_status(body, form_sections, f["label"], any_sections)) for f in attest_fields
        ]
        row = {
            "issue": issue, "kind": kind,
            "content_required": len(content_fields),
            "content_missing": content_missing,
            "attestations": attested,
            "matched_headings": matched_headings,
        }
        if matched_headings == 0:
            outside_form.append(row)
        else:
            in_form.append(row)

    incomplete = [r for r in in_form if r["content_missing"]]
    complete = [r for r in in_form if not r["content_missing"]]

    print(f"\n  issues matched to a template:        {len(in_form) + len(outside_form)}")
    print(f"  filed through the form:              {len(in_form)}")
    print(f"  outside the form (0 template heads): {len(outside_form)}")
    print(f"  complete:                            {len(complete)}")
    print(f"  missing >= 1 required content field: {len(incomplete)}")

    by_repo = collections.Counter(r["issue"]["slug"] for r in incomplete)
    by_kind = collections.Counter(r["kind"] for r in incomplete)
    field_counter = collections.Counter(label for r in incomplete for label, _ in r["content_missing"])

    lines = []
    lines.append("> **Read-only module.** Compares each open report against the required fields of its own repository's issue form. It is a **completeness signal**, not an accusation.")
    lines.append(">")
    lines.append("> **Nothing is applied.** The maintainer decides whether to ask for the missing data. `veredicto_humano: pendiente` is stated for every entry; the tool never fills it.")
    lines.append(">")
    lines.append("> Reproduce with `python3 modules/completeness.py`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Issues matched to a template (bug/feature) | {len(in_form) + len(outside_form)} |")
    lines.append(f"| Filed through the form (>=1 template heading present) | {len(in_form)} |")
    lines.append(f"| Outside the form (no template heading; pre-template or automated) | {len(outside_form)} |")
    lines.append(f"| Complete: every required content field present and non-empty | {len(complete)} |")
    lines.append(f"| **Incomplete: missing >= 1 required content field** | **{len(incomplete)}** |")
    lines.append("")
    lines.append("_Only issues filed through the form are counted in the incomplete metric. Attestation checkboxes are reported separately because a missing checkbox is not missing information._")
    lines.append("")
    lines.append("### Incomplete issues by repository")
    lines.append("")
    lines.append("| Repository | Incomplete | Share of its form-filed issues |")
    lines.append("| --- | --- | --- |")
    for slug in sorted({r["issue"]["slug"] for r in in_form}):
        total = sum(1 for r in in_form if r["issue"]["slug"] == slug)
        cnt = by_repo.get(slug, 0)
        share = f"{100.0 * cnt / total:.1f}%" if total else "n/a"
        lines.append(f"| `{slug}` | {cnt} | {share} |")
    lines.append("")
    lines.append("### Most frequently missing required content fields")
    lines.append("")
    lines.append("| Required field | Issues missing or empty |")
    lines.append("| --- | --- |")
    for label, cnt in field_counter.most_common(15):
        lines.append(f"| {label} | {cnt} |")
    lines.append("")
    lines.append("### Template fields parsed (ground truth)")
    lines.append("")
    for (slug, kind), req in sorted(template_fields.items()):
        content = [f["label"] for f in req if f["type"] != "checkboxes"]
        attest = [f["label"] for f in req if f["type"] == "checkboxes"]
        if not req:
            continue
        lines.append(f"- `{slug}/{TEMPLATE_FILENAMES.get(kind, kind)}.yml`")
        lines.append(f"  - required content: {', '.join(content) if content else '—'}")
        lines.append(f"  - attestations: {', '.join(attest) if attest else '—'}")
    lines.append("")
    lines.append("## Incomplete issues (up to 15 per repository)")
    lines.append("")
    for slug in sorted({r["issue"]["slug"] for r in in_form}):
        subset = [r for r in incomplete if r["issue"]["slug"] == slug]
        subset.sort(key=lambda r: (-len(r["content_missing"]), r["issue"]["number"]))
        lines.append(f"### `{slug}` — {len(subset)} incomplete")
        lines.append("")
        for r in subset[:15]:
            issue = r["issue"]
            missing_txt = "; ".join(f"{label} ({why})" for label, why in r["content_missing"])
            lines.append(f"- **{issue_ref(issue)}** — {issue_title(issue)[:110]}")
            lines.append(f"  - Link: {issue_link(issue)}")
            lines.append(f"  - Missing: {missing_txt}")
            lines.append(f"  - veredicto_humano: pendiente")
        lines.append("")

    body = "\n".join(lines)
    path = write_report("report-completeness.md", "Module A — Report Completeness", body)
    print(f"\n  report written: {path.name}")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
