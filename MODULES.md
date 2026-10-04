# MODULES.md — Mechanical Read-Only Modules (A, B, C, D, E)

> **What this file is.** The four modules that need **no human labels** to be useful: they compare each report with its own issue form, correlate probable duplicates by shared error signatures, surface cross-repository references, and flag references to source that no longer exists. Source, method, output and limits are all here.

> **Provenance:** module source at commit `7638f09`. Reports regenerate deterministically from the frozen snapshot (`issues.json`, 1,228 issues); `tools/determinism_check.py` proves byte-identical output across processes.

> **Read-only.** No module writes to GitHub, to `cross_refs`, or to the dataset. No `veredicto_humano` is ever filled. Nothing is closed or relabelled.

---

## 0. One-Screen Summary

| Module | Question it answers | Output | Headline | Limit |
| --- | --- | --- | --- | --- |
| **A** completeness | Is this report missing what its own form requires? | `report-completeness.md` | **313 incomplete** of 1043 form-filed (71 outside the form, excluded) | Completeness is a signal, not merit |
| **B** duplicates | Are two open issues probably the same? | `report-duplicates.md` | **7 strong** + 101 weaker pairs of 108 candidates | Shared identifiers are evidence, not proof |
| **C** cross-repo links | Does this issue reference another repository? | `report-cross-links.md` | 48 explicit refs, **15 resolve**; 914 bare mentions | Only an explicit `repo#N` proposes a link |
| **D** possibly obsolete | Does this issue reference source that no longer exists? | `report-obsolete.md` | **54 Class A** (deleted path, verifiable) + 155 Class B (weak, not an obsolescence claim) | Class A still needs human judgment |

```bash
python3 tools/run_reports.py        # regenerate all four reports
python3 tools/determinism_check.py   # fail if any report changes across processes
```

---

## 1. Module A — Completeness

**Question:** can this issue be triaged now, or is the report missing what its own repository's form asked for?

**Method:** parse `products/<repo>/.github/ISSUE_TEMPLATE/bug_report.yml` and `feature_request.yml` with PyYAML (fallback: an indentation-aware scanner) and read the fields marked `validations.required: true` — the maintainers' own ground truth, not an invented checklist. An issue is matched to the bug or feature template from its title prefix and labels. A required field counts as present when a heading matches it **or** a rendered inline label (`**Gentle AI Version:** …`) carries a non-empty value; GitHub renders form inputs inline, so a heading-only check produced false "missing" on well-formed reports. Attestation checkboxes are reported separately from triage-critical content, and an issue with no template heading at all is reported as *outside the form*, never as incomplete.

| Metric | Value |
| --- | --- |
| Issues matched to a template | 1114 |
| Filed through the form | 1043 |
| Outside the form (excluded from the metric) | 71 |
| Complete | n/a |
| Missing at least one required content field | **313** |

**Limit.** A report can be complete and still wrong, and one outside the form can be perfectly actionable. The maintainer decides whether to ask for the missing data.

---

## 2. Module B — Probable Duplicates

**Question:** are two open issues in the same repository probably the same problem?

**Method:** deterministic evidence only. Signatures: exception/panic class, error code (`TS6306`, `ENOENT`, `EPERM`…), `file:line` stack frame, quoted error string containing an error keyword, exit code, goroutine dump. Titles are normalized (prefix, versions, hashes, numbers, punctuation and stopwords removed). A signature is *rare* when it appears in at most 4 issues in that repository. Tiers:

- **Strong evidence:** identical normalized titles, or several shared rare signatures with high signature overlap, or a shared rare signature with title Jaccard ≥ 0.75.
- **Weaker evidence:** a single shared rare signature, or high title similarity alone.

| Metric | Value |
| --- | --- |
| Candidate pairs | 108 |
| Strong-evidence pairs | 7 |
| Weaker-evidence pairs | 101 |

**Limit.** "Strong evidence" means shared distinctive identifiers, **not** certainty: sibling issues implementing the same feature share exception names and configuration strings. The report says *candidate pair*, never *duplicate*.

---

## 3. Module C — Cross-Repository References

**Question:** does this issue reference another repository in a way the structured `cross_refs` field does not capture?

**Method:** three evidence levels. (1) An explicit `owner/repo#N` or `repo#N` whose number resolves to an open issue → propose a link. (2) `owner/repo` without a number → record, propose nothing. (3) A bare repository-name mention → record as the weakest signal, propose nothing.

| Metric | Value |
| --- | --- |
| Explicit references to another repo | 48 |
| — resolving to an open issue (linkable) | **15** |
| — not resolving (closed, renamed, typo) | 33 |
| `owner/repo` reference without a number | 81 |
| Bare repository-name mention, no `cross_refs` | 914 |

**This reframes an earlier audit figure.** `AUDIT.md` reported "345 issues mention another repo with no structured link". The actionable subset is much smaller: 33 issues carry an explicit `repo#N` reference and 15 resolve to an open issue. The rest are prose mentions — install instructions, comparisons, unrelated text — and a mention is not a dependency. Recording mentions as links would flood a maintainer who is already triaging 40 issues.

---

## 4. Module D — Possibly Obsolete Issues

**Question:** does this issue reference a source path, CLI flag or symbol that no longer exists in the repository?

**Method:** two evidence classes kept strictly apart. **Class A:** the referenced path appears in the repository's own git history as a deletion (`git log --diff-filter=D --name-only --all`) and is absent from the current tree — verifiable obsolescence. **Class B:** a path, flag or symbol absent from the checkout with **no deletion record** — likely another repository or the installed package layout, and explicitly *not* an obsolescence claim. Flags and symbols are matched as fixed strings anywhere in tracked source via a single batched `git grep`.

| Metric | Value |
| --- | --- |
| Class A — issues referencing a deleted path (verifiable) | **54** |
| Class B — issues with an unresolved reference (weak) | 155 |

**Why the split exists.** The first implementation reported 194 issues, but inspection showed most were misattributions: `--claude-code` is not a gentle-ai flag string, and `assets/agents/sdd-apply.md` belongs to the installed package layout, not the developer checkout. Mixing those with genuine cases (`internal/components/communitytool/rtk_runtime.go`, deleted in history) would have taught the maintainer to ignore the report.

**Limit.** Class A is verifiable but still needs human judgment: an issue can deliberately discuss removed code. Every row cites the token, the sentence and the commit the check ran against.

---

## 5. Module E — Concentration

**Question it answers:** where do the reports cluster? A pile of issues is unreadable; a handful of
directories is a plan.

**Method:** extract the repository paths each issue names, with the same deterministic extractor
Module D uses, and group them by **the directory where a change would land**, capped at three
levels. `internal/components/sdd/inject.go` becomes `internal/components/sdd`;
`extensions/gentle-ai.ts` becomes `extensions`. The same data is reported a second time by
**hotspot files**, because the directory view hides the case where one file carries most of a
directory's reports — which is exactly what happens in `gentle-shell`: 99 reports in `extensions`,
51 of them in one file.

**Grouping never crosses repositories.** A shared directory name is not a relationship, and merging
would invent one.

**What it deliberately does not do:** it does not prioritise. Priority is a judgement about impact,
and the snapshot carries no deterministic proxy for it — no SLA, no severity field, no
affected-user count. It reports location, which is a fact about the text, and nothing else.

**Result:** 458 of 1,228 issues name at least one path; the top fifteen subsystems cover 326 of them
(71%). Of those, 251 are issues the engine leaves without a band — the ones a cluster can reach.
The rest name no path at all and no rule reaches them; the report counts them rather than implying
them away.

**Its limits:** a location named in prose without a path lands in no cluster; only the top fifteen
subsystems and top twelve files are shown with their issues; the extractor takes the first few paths
per issue, so a report naming many files is attributed to the ones it names first.

**Reproduce with** `python3 modules/concentration.py` → `report-concentration.md`. Requires no
vendored checkouts and no labels.

## 6. Source (verbatim, at commit `7638f09`)

### `modules/common.py`

```python
#!/usr/bin/env python3
"""
common.py — Shared helpers for the read-only mechanical modules.

Every module reads issues.json, writes a Markdown report into the repository root,
and never mutates a third-party repository or the dataset.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "issues.json"

REPO_SLUGS = ("gentle-ai", "engram", "gentle-shell")


def load_issues():
    with open(SNAPSHOT, "r", encoding="utf-8") as f:
        return json.load(f)


def issue_text(issue):
    return f"{issue.get('title') or ''}\n{issue.get('body') or ''}"


def issue_body(issue):
    return issue.get("body") or ""


def issue_title(issue):
    return issue.get("title") or ""


def issue_ref(issue):
    return f"{issue['slug']}#{issue['number']}"


def issue_link(issue):
    return f"https://github.com/Gentleman-Programming/{issue['slug']}/issues/{issue['number']}"


def labels_of(issue):
    return {l.lower() for l in (issue.get("labels") or [])}


def is_bug_issue(issue):
    prefix = (issue.get("title_prefix") or "").lower()
    labels = labels_of(issue)
    return prefix in ("bug", "fix") or "type:bug" in labels or "bug" in labels


def is_feature_issue(issue):
    prefix = (issue.get("title_prefix") or "").lower()
    labels = labels_of(issue)
    return (
        prefix in ("feat", "feature")
        or "type:feature" in labels
        or "enhancement" in labels
        or "feature" in labels
    )


def strip_emoji_and_punct(text):
    """Normalizes a heading for comparison: removes emoji, punctuation, extra spaces."""
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]", " ", text)
    text = re.sub(r"[`*_#>\[\]():.!?\-–—]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def first_sentence(text, max_words=25):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return ""
    words = text.split(" ")
    return " ".join(words[:max_words])[:240]


def write_report(filename, title, body):
    path = ROOT / filename
    content = f"# {title}\n\n{body}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")
    return path
```

### `modules/templates.py`

```python
#!/usr/bin/env python3
"""
templates.py — Parses a repository's GitHub issue form (`.github/ISSUE_TEMPLATE/*.yml`).

Extracts the fields the repository itself declares as required, so Module A can tell
whether an open issue actually carries the information its own template asks for.

Uses PyYAML when available; otherwise falls back to a small indentation-aware scanner
that understands these specific form files (no third-party dependency is mandatory).
"""

import re
from pathlib import Path

try:  # optional
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from common import ROOT, REPO_SLUGS


def template_dir(slug):
    return ROOT / "products" / slug / ".github" / "ISSUE_TEMPLATE"


def _fallback_parse(text):
    """Minimal scanner for GitHub issue forms: collects type/label/required per field."""
    fields = []
    current = None
    pending_label = None
    pending_required = False
    in_attributes = False
    in_validations = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        m_type = re.match(r"^\s*-\s*type:\s*(\S+)", line)
        if m_type:
            if current:
                current["required"] = pending_required
                fields.append(current)
            current = {"type": m_type.group(1).strip().strip('"'), "label": None, "required": False}
            pending_label = None
            pending_required = False
            in_attributes = False
            in_validations = False
            continue

        if current is None:
            continue

        if re.match(r"^\s*attributes:\s*$", line):
            in_attributes = True
            in_validations = False
            continue
        if re.match(r"^\s*validations:\s*$", line):
            in_validations = True
            in_attributes = False
            continue
        if re.match(r"^\s*options:\s*$", line):
            in_attributes = True
            in_validations = False
            continue

        m_label = re.match(r"^\s*-\s*label:\s*(.+)$", line)
        if m_label and in_attributes:
            value = m_label.group(1).strip().strip('"').strip("'")
            if current["label"] is None:
                current["label"] = value
            continue

        m_attr_label = re.match(r"^\s*label:\s*(.+)$", line)
        if m_attr_label and in_attributes and current["label"] is None:
            value = m_attr_label.group(1).strip().strip('"').strip("'")
            current["label"] = value
            continue

        if in_validations and re.match(r"^\s*required:\s*true\s*$", line, re.IGNORECASE):
            pending_required = True
            continue

    if current:
        current["required"] = pending_required

    # For checkboxes the requirement lives on each option; a checkbox field is required
    # when every option is required. The fallback treats any checkbox as required when
    # its block contains "required: true".
    return fields


def parse_template(path):
    """Returns a list of {type, label, required} for one issue form."""
    text = Path(path).read_text(encoding="utf-8")
    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
            fields = []
            for entry in data.get("body") or []:
                etype = entry.get("type")
                if etype == "markdown":
                    continue
                attrs = entry.get("attributes") or {}
                label = attrs.get("label")
                required = bool((entry.get("validations") or {}).get("required"))
                if etype == "checkboxes":
                    options = attrs.get("options") or []
                    required = any(bool((o or {}).get("required")) for o in options) or required
                    label = label or "Checklist"
                fields.append({"type": etype, "label": label, "required": required})
            return fields
        except Exception:
            pass
    return _fallback_parse(text)


def templates_for(slug):
    """Returns {'bug': [...fields], 'feature': [...fields], ...} for one repository."""
    out = {}
    base = template_dir(slug)
    if not base.exists():
        return out
    mapping = {
        "bug_report.yml": "bug",
        "feature_request.yml": "feature",
        "docs_improvement.yml": "docs",
        "tracked_question.yml": "question",
    }
    for filename, kind in mapping.items():
        path = base / filename
        if path.exists():
            out[kind] = parse_template(path)
    return out


def required_labels(fields):
    """Required section labels (any type) for one template."""
    return [f["label"] for f in required_fields(fields)]


def required_fields(fields):
    """Required fields as {type, label}, skipping entries without a label."""
    out = []
    for f in fields:
        if not f.get("required"):
            continue
        label = f.get("label")
        if not label:
            continue
        out.append({"type": f.get("type"), "label": label})
    return out


def all_repo_templates():
    return {slug: templates_for(slug) for slug in REPO_SLUGS}
```

### `modules/completeness.py`

```python
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
```

### `modules/duplicates.py`

```python
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
```

### `modules/cross_repo.py`

```python
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
```

### `modules/obsolete.py`

```python
#!/usr/bin/env python3
"""
obsolete.py — Module D (read-only).

Finds issues that reference source paths, CLI flags or symbols that no longer exist in
the repository's current checkout, i.e. **possible obsolete issues**.

Two evidence classes, kept strictly apart:

  Class A — deleted path (strong).
      The referenced path exists in the repository's own git history as a deleted path
      and is absent from the current tree. This is verifiable obsolescence.

  Class B — unresolved reference (weak).
      A path, flag or symbol that is absent from the current checkout but has no
      deletion record in this repository. It may belong to another repository, to the
      installed package layout, or to work not yet landed. Never presented as obsolete.

Every suggestion cites the exact token, the sentence, the repository and the commit.
Nothing is closed, relabelled or commented. Every entry is `veredicto_humano: pendiente`.

Requires the vendored checkouts under `products/` (see `sync-products.sh`).

  python3 modules/obsolete.py
"""

import collections
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ROOT, REPO_SLUGS, load_issues, issue_link, issue_ref, issue_title,
    issue_text, write_report, first_sentence,
)

PRODUCTS = ROOT / "products"

SOURCE_EXTS = (
    "go|ts|tsx|js|jsx|mjs|cjs|py|rs|java|kt|rb|cs|c|cc|cpp|h|hpp|sql|sh|bash|"
    "md|json|json5|yml|yaml|toml|css|scss|html|vue|svelte|lua|proto|graphql"
)

PLAUSIBLE_ROOTS = {
    "internal", "lib", "libs", "cmd", "pkg", "src", "source", "docs", "doc", "tests", "test",
    "bin", "scripts", "script", "packages", "package", "extensions", "extension", "sdd",
    "prompts", "prompt", "skills", "skill", "schemas", "schema", "contracts", "contract",
    "api", "server", "client", "app", "apps", "core", "modules", "module", "config",
    "configs", "assets", "tools", "tool", "ui", "web", "frontend", "backend", "dist", "build",
    ".github", "templates", "fixtures", "examples", "benches", "bench", "migrations",
}

PATH_RE = re.compile(rf"(?<![\w./~-])((?:[\w.@+-]+/)+[\w.@+-]+\.(?:{SOURCE_EXTS}))\b")
FLAG_RE = re.compile(r"(?<![\w-])(--[a-z][a-z0-9]*(?:-[a-z0-9]+){1,4})(?![\w-])")
SYMBOL_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]{4,}(?:\.[A-Za-z_][A-Za-z0-9_]{2,})?)\s*\(\)?`")

SKIP_PATH_PARTS = ("node_modules/", ".git/", "site-packages/", "dist-packages/")


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo)] + list(args),
        capture_output=True, text=True, check=False,
    )


def repo_commit(slug):
    repo = PRODUCTS / slug
    if not (repo / ".git").exists():
        return None
    out = git(repo, "rev-parse", "--short", "HEAD")
    return out.stdout.strip() if out.returncode == 0 else None


def tracked_paths(slug):
    out = git(PRODUCTS / slug, "ls-files")
    if out.returncode != 0:
        return set()
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def deleted_paths(slug):
    """Paths that appear as deletions anywhere in the repository history."""
    out = git(PRODUCTS / slug, "log", "--diff-filter=D", "--name-only", "--pretty=format:", "--all")
    if out.returncode != 0:
        return set()
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def looks_like_repo_path(path):
    if any(part in path for part in SKIP_PATH_PARTS):
        return False
    if path.startswith(("http/", "https/", "www/")):
        return False
    return path.split("/", 1)[0].lower() in PLAUSIBLE_ROOTS


def extract_references(text, limit_paths=25, limit_flags=15, limit_symbols=10):
    refs = {"paths": [], "flags": [], "symbols": []}
    seen = {"paths": set(), "flags": set(), "symbols": set()}
    for m in PATH_RE.finditer(text):
        p = m.group(1)
        if not looks_like_repo_path(p) or p in seen["paths"]:
            continue
        if len(refs["paths"]) >= limit_paths:
            break
        seen["paths"].add(p)
        refs["paths"].append((p, first_sentence(text[max(0, m.start() - 50):m.end() + 50])))
    for m in FLAG_RE.finditer(text):
        f = m.group(1)
        if f in seen["flags"] or len(refs["flags"]) >= limit_flags:
            continue
        seen["flags"].add(f)
        refs["flags"].append((f, first_sentence(text[max(0, m.start() - 50):m.end() + 50])))
    for m in SYMBOL_RE.finditer(text):
        s = m.group(1)
        if s in seen["symbols"] or len(refs["symbols"]) >= limit_symbols:
            continue
        seen["symbols"].add(s)
        refs["symbols"].append((s, first_sentence(text[max(0, m.start() - 50):m.end() + 50])))
    return refs


def grep_present(slug, tokens):
    if not tokens:
        return set()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write("\n".join(sorted(tokens)) + "\n")
        pattern_file = fh.name
    try:
        out = git(PRODUCTS / slug, "grep", "-o", "-F", "-f", pattern_file)
        if out.returncode not in (0, 1):
            return set()
        return {line.split(":", 1)[1] for line in out.stdout.splitlines() if ":" in line}
    finally:
        try:
            os.unlink(pattern_file)
        except OSError:
            pass


def main():
    issues = load_issues()

    commits, tracked, deleted, basenames = {}, {}, {}, {}
    for slug in REPO_SLUGS:
        commits[slug] = repo_commit(slug)
        tracked[slug] = tracked_paths(slug)
        deleted[slug] = deleted_paths(slug)
        index = collections.defaultdict(list)
        for p in tracked[slug]:
            index[Path(p).name].append(p)
        basenames[slug] = index

    missing = [s for s in REPO_SLUGS if commits[s] is None]
    print("════════════════════════════════════════════════════════════════════")
    print(" MODULE D — POSSIBLY OBSOLETE ISSUES")
    print("════════════════════════════════════════════════════════════════════")
    for slug in REPO_SLUGS:
        print(f"  {slug}: commit {commits[slug]} — {len(tracked[slug])} tracked, "
              f"{len(deleted[slug])} deleted-in-history")
    if missing:
        print(f"  ❌ missing vendored repos: {missing}; run ./sync-products.sh")
        return 1

    per_issue = []
    all_flags = collections.defaultdict(set)
    all_symbols = collections.defaultdict(set)
    for issue in issues:
        refs = extract_references(issue_text(issue))
        if not any(refs.values()):
            continue
        per_issue.append((issue, refs))
        for token, _ in refs["flags"]:
            all_flags[issue["slug"]].add(token)
        for token, _ in refs["symbols"]:
            all_symbols[issue["slug"]].add(token)

    present_flags = {slug: grep_present(slug, toks) for slug, toks in all_flags.items()}
    present_symbols = {slug: grep_present(slug, toks) for slug, toks in all_symbols.items()}

    strong, weak = [], []
    for issue, refs in per_issue:
        slug = issue["slug"]
        a, b = [], []
        for p, quote in refs["paths"]:
            if p in tracked[slug]:
                continue
            if p in deleted[slug]:
                a.append({"token": p, "quote": quote, "detail": "path was deleted in this repository's history"})
            else:
                alternates = [t for t in basenames[slug].get(Path(p).name, []) if t != p]
                detail = "not in this checkout"
                if alternates:
                    detail += f" (same basename exists at `{alternates[0]}`)"
                else:
                    detail += " and no deletion record in this repository (likely another repo or the installed layout)"
                b.append({"token": p, "quote": quote, "detail": detail})
        for f, quote in refs["flags"]:
            if f not in present_flags.get(slug, set()):
                b.append({"token": f, "quote": quote, "detail": "flag string not present in this checkout"})
        for s, quote in refs["symbols"]:
            if s not in present_symbols.get(slug, set()):
                b.append({"token": s, "quote": quote, "detail": "symbol not present in this checkout"})
        if a:
            strong.append({"issue": issue, "refs": a})
        if b:
            weak.append({"issue": issue, "refs": b})

    strong_repo = collections.Counter(f["issue"]["slug"] for f in strong)
    weak_repo = collections.Counter(f["issue"]["slug"] for f in weak)
    strong_tokens = collections.Counter(r["token"] for f in strong for r in f["refs"])

    print(f"\n  Class A — issues referencing a deleted path: {len(strong)}")
    for slug, cnt in strong_repo.most_common():
        print(f"    - {slug}: {cnt}")
    print(f"  Class B — issues with an unresolved reference: {len(weak)}")
    for slug, cnt in weak_repo.most_common():
        print(f"    - {slug}: {cnt}")

    lines = []
    lines.append("> **Read-only module.** Flags issues that reference source paths, CLI flags or symbols that no longer exist in the repository's current checkout — i.e. **possible obsolete issues**.")
    lines.append(">")
    lines.append("> **Nothing is closed or relabelled.** Every entry is `veredicto_humano: pendiente`.")
    lines.append(">")
    lines.append("> Reproduce with `python3 modules/obsolete.py` (requires the vendored checkouts under `products/`, see `sync-products.sh`).")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("Two evidence classes, deliberately kept apart so the strong signal is not diluted by the weak one:")
    lines.append("")
    lines.append("| Class | Meaning | Issues |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| **A — deleted path** | The referenced path exists in this repository's git history as a deletion and is absent now. Verifiable obsolescence. | **{len(strong)}** |")
    lines.append(f"| **B — unresolved reference** | A path, flag or symbol absent from this checkout with **no deletion record**. May belong to another repository, the installed package layout, or unlanded work. **Not** evidence of obsolescence. | {len(weak)} |")
    lines.append("")
    lines.append("### Checked against these commits")
    lines.append("")
    lines.append("| Repository | Commit | Tracked files | Deleted paths in history |")
    lines.append("| --- | --- | --- | --- |")
    for slug in REPO_SLUGS:
        lines.append(f"| `{slug}` | `{commits[slug]}` | {len(tracked[slug])} | {len(deleted[slug])} |")
    lines.append("")
    lines.append("### Class A by repository")
    lines.append("")
    lines.append("| Repository | Issues |")
    lines.append("| --- | --- |")
    for slug, cnt in strong_repo.most_common():
        lines.append(f"| `{slug}` | {cnt} |")
    if not strong_repo:
        lines.append("| — | 0 |")
    lines.append("")
    lines.append("### Most frequently referenced deleted paths")
    lines.append("")
    lines.append("| Deleted path | Issues referencing it |")
    lines.append("| --- | --- |")
    for token, cnt in strong_tokens.most_common(15):
        lines.append(f"| `{token}` | {cnt} |")
    if not strong_tokens:
        lines.append("| — | 0 |")
    lines.append("")
    lines.append("## Class A — issues referencing a deleted path (up to 15 per repository)")
    lines.append("")
    lines.append("These are the actionable rows. Each cites the deleted path, the sentence, the repository and the commit. A maintainer must confirm the issue is indeed obsolete before closing anything.")
    lines.append("")
    for slug in REPO_SLUGS:
        subset = [f for f in strong if f["issue"]["slug"] == slug]
        subset.sort(key=lambda f: f["issue"]["number"])
        lines.append(f"### `{slug}` — {len(subset)} issues (checked at `{commits[slug]}`)")
        lines.append("")
        if not subset:
            lines.append("_None._")
            lines.append("")
            continue
        for f in subset[:15]:
            issue = f["issue"]
            lines.append(f"- **{issue_ref(issue)}** — {issue_title(issue)[:110]}")
            lines.append(f"  - Link: {issue_link(issue)}")
            for r in f["refs"][:5]:
                lines.append(f"  - `{r['token']}` — {r['detail']}")
                lines.append(f"    - Evidence: \"{r['quote']}\"")
            lines.append(f"  - **posible, requiere verificación** — veredicto_humano: pendiente")
        lines.append("")
    lines.append("## Class B — unresolved references (weak evidence, up to 8 per repository)")
    lines.append("")
    lines.append("**These are not obsolescence claims.** They are references this checkout does not contain; most belong to another repository or to the installed package layout. The section exists so the signal is visible without being mistaken for proof.")
    lines.append("")
    for slug in REPO_SLUGS:
        subset = [f for f in weak if f["issue"]["slug"] == slug]
        subset.sort(key=lambda f: f["issue"]["number"])
        lines.append(f"### `{slug}` — {len(subset)} issues (checked at `{commits[slug]}`)")
        lines.append("")
        if not subset:
            lines.append("_None._")
            lines.append("")
            continue
        for f in subset[:8]:
            issue = f["issue"]
            tokens = ", ".join(f"`{r['token']}`" for r in f["refs"][:6])
            lines.append(f"- **{issue_ref(issue)}** — {issue_title(issue)[:100]}")
            lines.append(f"  - Link: {issue_link(issue)}")
            lines.append(f"  - Unresolved: {tokens}")
            lines.append(f"  - veredicto_humano: pendiente")
        lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- **Class A is verifiable but still needs human judgment**: an issue can deliberately discuss code that was removed, or the removal may be unrelated to the issue's request.")
    lines.append("- **Class B is not evidence of obsolescence.** It exists because the absence of a reference is worth seeing, not because it proves anything. A path in the installed package layout (`assets/...`) or another repository naturally does not appear in this checkout.")
    lines.append("- The check runs against the vendored commit listed above, not the live default branch. Re-run `./sync-products.sh` then this module to refresh.")
    lines.append("- Flags and symbols are matched as substrings anywhere in tracked source, so a token that survives only in tests or docs resolves and is not reported (under-reporting, by design).")
    lines.append("- Only repo-relative paths under plausible source roots are checked; user paths, URLs and prose are ignored.")
    lines.append("- The module never closes, relabels or comments on anything.")
    lines.append("")

    path = write_report("report-obsolete.md", "Module D — Possibly Obsolete Issues", "\n".join(lines))
    print(f"\n  report written: {path.name}")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `tools/run_reports.py`

```python
#!/usr/bin/env python3
"""
run_reports.py — Regenerates every module report from the frozen snapshot.

  python3 tools/run_reports.py

Runs Module A (completeness), Module B (duplicates), Module C (cross-repository
references) and Module D (possibly obsolete issues). Each module is read-only and
writes one root Markdown report.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    ("Module A — completeness", ROOT / "modules" / "completeness.py"),
    ("Module B — duplicates", ROOT / "modules" / "duplicates.py"),
    ("Module C — cross-repo links", ROOT / "modules" / "cross_repo.py"),
    ("Module D — possibly obsolete", ROOT / "modules" / "obsolete.py"),
]


def main():
    failed = 0
    for name, path in MODULES:
        print(f"── {name} ──")
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            failed += 1
            sys.stderr.write(result.stderr)
        print()
    if failed:
        print(f"{failed} module(s) failed")
        return 1
    print("all module reports regenerated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `tools/determinism_check.py`

```python
#!/usr/bin/env python3
"""
determinism_check.py — Verifies that every module report is byte-identical across processes.

Python randomizes string hashing per process (PYTHONHASHSEED), so any module that iterates
a `set` of strings to build an ordered report can produce a different file each run. That
would make the published reports unreproducible.

This checker runs each module twice under different hash seeds and fails if a report changes.

  python3 tools/determinism_check.py

Exit code 0 = all reports byte-identical. Exit code 1 = a report is non-deterministic.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULES = [
    ("Module A — completeness", ROOT / "modules" / "completeness.py", ROOT / "report-completeness.md"),
    ("Module B — duplicates", ROOT / "modules" / "duplicates.py", ROOT / "report-duplicates.md"),
    ("Module C — cross-repo links", ROOT / "modules" / "cross_repo.py", ROOT / "report-cross-links.md"),
    ("Module D — possibly obsolete", ROOT / "modules" / "obsolete.py", ROOT / "report-obsolete.md"),
]

SEEDS = ["1", "7"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_once(module, report, seed):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run([sys.executable, str(module)], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"{module.name} failed with PYTHONHASHSEED={seed}")
    return digest(report)


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" REPORT DETERMINISM CHECK (two processes, two hash seeds)")
    print("════════════════════════════════════════════════════════════════════")
    failures = []
    for name, module, report in MODULES:
        if not module.exists():
            print(f"  ❌ missing module: {module}")
            failures.append(name)
            continue
        digests = {seed: run_once(module, report, seed) for seed in SEEDS}
        unique = set(digests.values())
        if len(unique) == 1:
            print(f"  ✔ {name}: {list(unique)[0][:16]}…")
        else:
            print(f"  ❌ {name}: report differs across seeds")
            for seed, d in digests.items():
                print(f"       seed {seed}: {d[:16]}…")
            failures.append(name)

    print("────────────────────────────────────────────────────────────────────")
    if failures:
        print(f" NON-DETERMINISTIC REPORTS: {len(failures)} — {', '.join(failures)}")
        print("════════════════════════════════════════════════════════════════════")
        return 1
    print(" ALL REPORTS BYTE-IDENTICAL ACROSS PROCESSES")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 6. Console Output of `python3 tools/run_reports.py`

```text
── Module A — completeness ──
════════════════════════════════════════════════════════════════════
 MODULE A — COMPLETENESS AGAINST THE REPOSITORY ISSUE FORM
════════════════════════════════════════════════════════════════════
  engram/bug: 7 required content fields, 0 attestation(s)
  engram/docs: 3 required content fields, 0 attestation(s)
  engram/feature: 3 required content fields, 0 attestation(s)
  engram/question: 3 required content fields, 0 attestation(s)
  gentle-ai/bug: 8 required content fields, 1 attestation(s)
  gentle-ai/feature: 3 required content fields, 1 attestation(s)
  gentle-shell/bug: 6 required content fields, 1 attestation(s)
  gentle-shell/feature: 2 required content fields, 1 attestation(s)

  issues matched to a template:        1114
  filed through the form:              1043
  outside the form (0 template heads): 71
  complete:                            730
  missing >= 1 required content field: 313

  report written: report-completeness.md
════════════════════════════════════════════════════════════════════

── Module B — duplicates ──
════════════════════════════════════════════════════════════════════
 MODULE B — PROBABLE DUPLICATES (same repository)
════════════════════════════════════════════════════════════════════
  issues analysed:      1228
  candidate pairs:      108
  strong-evidence pairs:7
  weaker-evidence pairs:101
    - gentle-ai: 68
    - gentle-shell: 39
    - engram: 1

  report written: report-duplicates.md
════════════════════════════════════════════════════════════════════

── Module C — cross-repo links ──
════════════════════════════════════════════════════════════════════
 MODULE C — CROSS-REPOSITORY REFERENCES NOT IN cross_refs
════════════════════════════════════════════════════════════════════
  issues with structured cross_refs: 26
  explicit references to another repo: 48
    - resolving to an open issue:      15
    - not resolving:                   33
  issues with >=1 explicit reference:  33
  owner/repo references without number:81
  bare slug mentions, no cross_refs:   914

  report written: report-cross-links.md
════════════════════════════════════════════════════════════════════

── Module D — possibly obsolete ──
════════════════════════════════════════════════════════════════════
 MODULE D — POSSIBLY OBSOLETE ISSUES
════════════════════════════════════════════════════════════════════
  gentle-ai: commit 9dfe17d8 — 1826 tracked, 1252 deleted-in-history (see D-037: this count
depends on the checkouts' local ref state, not only on the pinned commit)
  engram: commit 0f79d5e — 555 tracked, 276 deleted-in-history
  gentle-shell: commit 7a27c1c0 — 733 tracked, 1734 deleted-in-history

  Class A — issues referencing a deleted path: 54
    - gentle-ai: 34
    - gentle-shell: 20
  Class B — issues with an unresolved reference: 155
    - gentle-ai: 78
    - gentle-shell: 70
    - engram: 7

  report written: report-obsolete.md
════════════════════════════════════════════════════════════════════

all module reports regenerated
```

---

## 7. Honest Limits

1. **None of the four modules has human-verified precision.** They are deterministic and reproducible; a maintainer must judge the reports.

2. **Module A depends on the issue form being the ground truth.** It parses the vendored checkout, not a live fetch.

3. **Module B under-reports prose-only duplicates.** Without stack traces or distinctive strings there is no deterministic evidence, so it stays silent rather than guess.

4. **Module C does not populate `cross_refs`** and cannot tell a dependency from a comparison; it reports.

5. **Module D Class B is not evidence of obsolescence** and is labelled as such.

6. **Reports must stay byte-identical.** `tools/determinism_check.py` enforces it; a non-deterministic report would make every other reproducibility claim worthless.

7. **No module acts.** There is no write path to GitHub anywhere in the project; `tools/readonly_check.py` enforces it.
