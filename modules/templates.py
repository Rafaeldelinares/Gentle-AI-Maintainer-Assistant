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


def templates_present(slug):
    """Whether this repository's issue-form directory exists at all.

    Absent means the vendored checkouts are missing. That is a different fact from a
    repository whose forms simply do not require a field: the first is unknown, the second
    is known. Callers that report completeness must distinguish them, because reporting
    "nothing missing" when nothing could be read is a silent lie.
    """
    return template_dir(slug).exists()


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
