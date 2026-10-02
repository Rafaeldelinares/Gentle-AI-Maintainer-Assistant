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
