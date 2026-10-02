#!/usr/bin/env python3
"""
privacy_check.py — Verifies the snapshot carries no personal data.

Checks issues.json for:
  - author/user/login/email fields (must not exist)
  - known maintainer handles (must not appear)
  - email-like strings, allowlisting example/placeholder and non-personal patterns

  python3 tools/privacy_check.py

Exit code 0 = clean. Exit code 1 = a violation was found.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "issues.json"

# Third-party maintainer handles that must never appear in the snapshot.
FORBIDDEN_HANDLES = ["Alan-TheGentleman"]

# Email-like strings that are placeholders or filenames, not personal data.
ALLOWED_EMAIL_PATTERNS = [
    re.compile(r"@example\.(com|invalid|org)$", re.IGNORECASE),
    re.compile(r"^go@go\d", re.IGNORECASE),
]

FORBIDDEN_KEYS = ["author", "user", "login", "email", "author_login"]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" PRIVACY CHECK (issues.json)")
    print("════════════════════════════════════════════════════════════════════")
    if not SNAPSHOT.exists():
        print("  ❌ issues.json not found")
        return 1
    with open(SNAPSHOT, "r", encoding="utf-8") as f:
        issues = json.load(f)
    print(f"  issues loaded: {len(issues)}")

    violations = []

    for it in issues:
        for key in FORBIDDEN_KEYS:
            if key in it and it[key]:
                violations.append(f"{it['slug']}#{it['number']} carries a '{key}' field")

    for it in issues:
        blob = f"{it.get('title') or ''}\n{it.get('body') or ''}"
        for handle in FORBIDDEN_HANDLES:
            if re.search(re.escape(handle), blob, re.IGNORECASE):
                violations.append(f"{it['slug']}#{it['number']} contains the maintainer handle '{handle}'")

    email_hits = []
    for it in issues:
        blob = f"{it.get('title') or ''}\n{it.get('body') or ''}"
        for m in EMAIL_RE.finditer(blob):
            value = m.group(0)
            if any(p.search(value) for p in ALLOWED_EMAIL_PATTERNS):
                continue
            email_hits.append(f"{it['slug']}#{it['number']} -> {value}")
    violations.extend(email_hits)

    if violations:
        print(f"  ❌ VIOLATIONS: {len(violations)}")
        for v in violations[:50]:
            print(f"    - {v}")
        print("════════════════════════════════════════════════════════════════════")
        return 1

    print("  ✔ no author/user fields")
    print(f"  ✔ no forbidden maintainer handles ({', '.join(FORBIDDEN_HANDLES)})")
    print("  ✔ no non-placeholder email addresses")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
