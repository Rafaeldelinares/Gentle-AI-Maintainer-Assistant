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
