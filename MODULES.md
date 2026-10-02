# MODULES.md — Mechanical Read-Only Modules (A, B, C)

> **What this file is.** The three modules that need **no human labels** to be useful: they compare each report with its own issue form, correlate probable duplicates by shared error signatures, and surface cross-repository references. Source, method, output and limits are all here.

> **Provenance:** module source at commit `8081020`. Reports regenerate deterministically from the frozen snapshot (`issues.json`, 1,228 issues).

> **Read-only.** No module writes to GitHub, to `cross_refs`, or to the dataset. No `veredicto_humano` is ever filled.

---

## 0. One-Screen Summary

| Module | Question it answers | Output | Evidence | Limit |
| --- | --- | --- | --- | --- |
| **A** completeness | Is this report missing the fields its own form requires? | `report-completeness.md` | 1114 issues matched to a template; 1043 form-filed; **313 incomplete**; 71 outside the form | Signals completeness, not merit; pre-template reports excluded |
| **B** duplicates | Are two open issues probably the same? | `report-duplicates.md` | **7 strong** and 101 weaker pairs out of 108 candidates | Shared identifiers are evidence, not proof; never closes or merges |
| **C** cross-repo links | Does this issue reference another repository? | `report-cross-links.md` | 48 explicit references; **15 resolve** to an open issue; 81 unnumbered repo refs; 914 bare mentions | Only an explicit `repo#N` proposes a link; a mention never does |

```bash
python3 tools/run_reports.py     # regenerates all three reports
```

---

## 1. Module A — Completeness

**Question:** can this issue be triaged now, or is the report missing what its own repository's form asked for?

**Method:** parse `products/<repo>/.github/ISSUE_TEMPLATE/bug_report.yml` and `feature_request.yml` with PyYAML (fallback: an indentation-aware scanner) and read the fields marked `validations.required: true` — the maintainers' own ground truth, not an invented checklist. An issue is matched to the bug or feature template from its title prefix and labels. A required field counts as present when a `###`/`##` heading matches it **or** a rendered inline label (`**Gentle AI Version:** …`) carries a non-empty value. Attestation checkboxes are reported separately from triage-critical content, and an issue with no template heading at all is reported as *outside the form*, not as incomplete.

**Findings:**

| Metric | Value |
| --- | --- |
| Issues matched to a template | 1114 |
| Filed through the form | 1043 |
| Outside the form (excluded from the metric) | 71 |
| Complete | n/a |
| Missing at least one required content field | **313** |

**Limit.** This is a completeness signal, not an accusation: a report can be complete and still wrong, and a report outside the form may be perfectly actionable. The maintainer decides whether to ask for the missing data.

---

## 2. Module B — Probable Duplicates

**Question:** are two open issues in the same repository probably the same problem?

**Method:** deterministic evidence only. Signatures: exception/panic class, error code (`TS6306`, `ENOENT`, `EPERM`…), `file:line` stack frame, quoted error string containing an error keyword, exit code, goroutine dump. Titles are normalized (conventional prefix, versions, hashes, numbers, punctuation and stopwords removed). A signature is *rare* when it appears in at most 4 issues in that repository. Tiers:

- **Strong evidence:** identical normalized titles, or several shared rare signatures with high signature overlap, or a shared rare signature with title Jaccard ≥ 0.75.
- **Weaker evidence:** a single shared rare signature, or high title similarity alone.

**Findings:**

| Metric | Value |
| --- | --- |
| Candidate pairs | 108 |
| Strong-evidence pairs | 7 |
| Weaker-evidence pairs | 101 |

**Limit.** "Strong evidence" means shared distinctive identifiers, **not** certainty: sibling issues that implement the same feature often share exception names and configuration strings. The report says *candidate pair*, never *duplicate*, and every entry is `veredicto_humano: pendiente`. The module never closes or merges anything.

---

## 3. Module C — Cross-Repository References

**Question:** does this issue reference another repository in a way the structured `cross_refs` field does not capture?

**Method:** three evidence levels. (1) An explicit `owner/repo#N` or `repo#N` whose number resolves to an open issue → propose a link. (2) `owner/repo` without a number → record, propose nothing. (3) A bare repository-name mention → record as the weakest signal, propose nothing.

**Findings:**

| Metric | Value |
| --- | --- |
| Issues with a structured `cross_refs` entry | 26 |
| Explicit references to another repo | 48 |
| — resolving to an open issue (linkable) | **15** |
| — not resolving (closed, renamed, typo) | 33 |
| `owner/repo` reference without a number | 81 |
| Bare repository-name mention, no `cross_refs` | 914 |

**This reframes an earlier audit figure.** `AUDIT.md` reported "345 issues mention another repo with no structured link". Module C shows the actionable subset is much smaller: only 33 issues carry an explicit `repo#N` reference, and 15 resolve to an open issue. The rest are prose mentions — install instructions, comparisons, unrelated text — and a mention is not a dependency. Recording mentions as links would flood a maintainer who is already triaging 40 issues.

**Limit.** The module cannot tell a dependency from a comparison, so it reports and does not classify. It never writes `cross_refs`.

---

## 4. Source (verbatim, at commit `8081020`)

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

    for (slug, sig), members in sig_index.items():
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
        for token in set(titles[issue_ref(issue)]):
            token_index[(issue["slug"], token)].append(issue_ref(issue))

    for (slug, token), members in token_index.items():
        if len(members) < 2 or len(members) > 40:
            continue
        for a, b in itertools.combinations(sorted(members), 2):
            ja = jaccard(titles[a], titles[b])
            if ja >= 0.8 and len(titles[a]) >= 3 and len(titles[b]) >= 3:
                shared = [f"title-jaccard:{ja:.2f}"]
                add_pair(a, b, 60 + int(ja * 30), "medium", shared)

    order = {"high": 0, "medium": 1}
    ranked = sorted(pairs.items(), key=lambda kv: (-kv[1]["score"], order.get(kv[1]["tier"], 2)))

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

### `tools/run_reports.py`

```python
#!/usr/bin/env python3
"""
run_reports.py — Regenerates every module report from the frozen snapshot.

  python3 tools/run_reports.py

Runs Module A (completeness), Module B (duplicates) and Module C (cross-repository
references). Each module is read-only and writes one root Markdown report.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    ("Module A — completeness", ROOT / "modules" / "completeness.py"),
    ("Module B — duplicates", ROOT / "modules" / "duplicates.py"),
    ("Module C — cross-repo links", ROOT / "modules" / "cross_repo.py"),
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

---

## 5. Console Output of `python3 tools/run_reports.py`

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

all module reports regenerated
```

---

## 6. Honest Limits

1. **None of the three modules has human-verified precision yet.** They are deterministic and reproducible, but their usefulness must be judged by a maintainer reading the reports.

2. **Module A depends on the issue form being the ground truth.** If a repository changes its template, the parse follows the template in `products/`, which is a vendored checkout, not a live fetch.

3. **Module B under-reports prose-only duplicates.** Without stack traces or distinctive strings there is no deterministic evidence, so it stays silent rather than guess.

4. **Module C does not populate `cross_refs`.** The structured field is maintainer-owned.

5. **No module acts.** There is no write path to GitHub anywhere in the project; `tools/readonly_check.py` enforces it.
