#!/usr/bin/env python3
"""
readonly_check.py — Verifies the non-negotiable read-only invariant.

The assistant must never comment, label, close, transfer, or open anything on
Gentleman-Programming repositories. This checker scans the project's own source for
mutating GitHub or HTTP write operations and fails if any is found.

  python3 tools/readonly_check.py

Exit code 0 = read-only invariant holds. Exit code 1 = a mutating operation was found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Only the project's own executable code. `products/` holds third-party checkouts and
# markdown docs describe procedures rather than execute them.
SCAN_DIRS = ["db", "schemas", "tools"]
SCAN_FILES = ["test_rules.py"]
CODE_SUFFIXES = (".py", ".sh", ".bash", ".sql")
SELF = Path(__file__).resolve()

# Mutating GitHub / HTTP operations that would violate the invariant.
MUTATION_PATTERNS = [
    (re.compile(r"\bgh\s+issue\s+(comment|close|edit|delete|transfer|create|reopen|lock|unlock)\b"), "gh issue mutation"),
    (re.compile(r"\bgh\s+pr\s+(comment|close|edit|merge|create|review|reopen)\b"), "gh pr mutation"),
    (re.compile(r"\bgh\s+label\b"), "gh label mutation"),
    (re.compile(r"\bgh\s+api\b[^\n]*(-X|--method)\s*(POST|PATCH|PUT|DELETE)", re.IGNORECASE), "gh api write"),
    (re.compile(r"\brequests\.(post|put|patch|delete)\b", re.IGNORECASE), "HTTP write via requests"),
    (re.compile(r"\burlopen\s*\([^)]*data\s*="), "HTTP write via urlopen"),
    (re.compile(r"\bcurl\b[^\n]*\s(-X|--request)\s*(POST|PATCH|PUT|DELETE)", re.IGNORECASE), "HTTP write via curl"),
    (re.compile(r"\bgit\s+push\b"), "git push"),
]

# Documented exceptions: lines that describe the prohibition rather than perform it.
ALLOW_MARKERS = ("read-only", "readonly", "must never", "no mutation", "not allowed", "never ")


def iter_targets():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in CODE_SUFFIXES and p.resolve() != SELF:
                yield p
    for f in SCAN_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" READ-ONLY INVARIANT CHECK")
    print("════════════════════════════════════════════════════════════════════")
    violations = []
    scanned = 0
    for path in iter_targets():
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(marker in line.lower() for marker in ALLOW_MARKERS):
                continue
            # `gh issue list` / `gh pr list` / `gh label list` are read-only and allowed.
            if re.search(r"\bgh\s+(issue|pr|label)\s+list\b", line):
                continue
            for pattern, label in MUTATION_PATTERNS:
                if pattern.search(line):
                    violations.append((path.relative_to(ROOT), lineno, label, line.strip()[:120]))

    print(f"  files scanned: {scanned}")
    if violations:
        print(f"  ❌ VIOLATIONS: {len(violations)}")
        for rel, lineno, label, line in violations:
            print(f"    - {rel}:{lineno} [{label}] {line}")
        print("════════════════════════════════════════════════════════════════════")
        return 1

    print("  ✔ no mutating GitHub or HTTP write operation found in project source")
    print("  allowed: `gh issue list`, `gh pr list` (read-only) in ingestion scripts")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
