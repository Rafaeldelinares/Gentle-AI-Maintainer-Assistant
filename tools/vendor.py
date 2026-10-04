#!/usr/bin/env python3
"""
vendor.py — Materialize the audited repositories' inputs, PINNED to the commits the published
figures cite.

Why pinning matters
-------------------
`sync-products.sh` used to clone and then `git pull` upstream/main. Re-running it moved the
inputs to whatever upstream was that day, while MODULES.md and the reports kept citing specific
commits. Every completeness and obsolescence figure therefore depended on input versions the
fetching script never fixed: re-running the documented setup and regenerating the reports would
have produced different numbers, silently, under the same citations.

A reproducibility claim that depends on whatever upstream is today is not a reproducibility
claim. This tool makes the pins the single source of truth and verifies what it materialized
against them.

Modes
-----
    python3 tools/vendor.py --templates-only    # the ten issue forms; no git, no clone
    python3 tools/vendor.py --full              # full checkouts at the pinned commits

`--templates-only` fetches each form from raw.githubusercontent at the exact pinned commit, so
it is deterministic and fast; it is what CI uses. `--full` is for Module D, which walks the
repositories' history.

Both modes fail loudly when a pinned commit is unavailable. That is the point: a fetch that
always "works" by silently taking something else is the defect this replaces.
"""

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "products"
OWNER = "Gentleman-Programming"
TIMEOUT_SECONDS = 180

# The single source of truth for the inputs' versions. Full commit hashes, because a short
# prefix is a citation and this is a pin. The template lists are pinned too: adding a form
# upstream must be a deliberate act here, not something that appears one morning.
PINS = {
    "gentle-ai": (
        "9dfe17d837dcd5c164c904164ae3888ff4f3ff54",
        ("bug_report.yml", "config.yml", "feature_request.yml"),
    ),
    "engram": (
        "0f79d5ea0bb842f65a0d2234ce3fef6353314846",
        ("bug_report.yml", "config.yml", "docs_improvement.yml", "feature_request.yml",
         "tracked_question.yml"),
    ),
    "gentle-shell": (
        "7a27c1c008b3922b851da5efb78e4ca4dae6e6b1",
        ("bug_report.yml", "feature_request.yml"),
    ),
}


def template_path(slug, name):
    return PRODUCTS / slug / ".github" / "ISSUE_TEMPLATE" / name


def raw_url(slug, commit, name):
    return f"https://raw.githubusercontent.com/{OWNER}/{slug}/{commit}/.github/ISSUE_TEMPLATE/{name}"


def fetch_templates():
    """Ten small files, by commit. Idempotent: an unchanged form is not rewritten."""
    written = unchanged = 0
    for slug, (commit, names) in sorted(PINS.items()):
        for name in names:
            path = template_path(slug, name)
            try:
                with urllib.request.urlopen(raw_url(slug, commit, name), timeout=TIMEOUT_SECONDS) as response:
                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status}")
                    content = response.read()
            except Exception as error:  # noqa: BLE001 - reported, never swallowed
                raise SystemExit(
                    f"cannot fetch {slug}/.github/ISSUE_TEMPLATE/{name} at {commit[:8]}: {error}\n"
                    f"  the pin is the point: if upstream removed this commit, fix the pin deliberately."
                )
            if path.exists() and path.read_bytes() == content:
                unchanged += 1
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            written += 1
    return written, unchanged


def run_git(*args):
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                              timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        raise SystemExit(f"git timed out after {TIMEOUT_SECONDS}s: git {' '.join(args)}")
    except OSError as error:
        raise SystemExit(f"cannot run git: {error}")


def fetch_full():
    """Clone or update each repository, then check out the pin and verify it landed."""
    for slug, (commit, _names) in sorted(PINS.items()):
        target = PRODUCTS / slug
        if not (target / ".git").exists():
            result = run_git("clone", f"https://github.com/{OWNER}/{slug}.git", str(target))
            if result.returncode != 0:
                raise SystemExit(f"cannot clone {slug}: {result.stderr.strip()}")
        else:
            run_git("-C", str(target), "fetch", "--quiet", "origin")
        checkout = run_git("-C", str(target), "checkout", "--quiet", commit)
        if checkout.returncode != 0:
            raise SystemExit(
                f"cannot check out {slug} at {commit[:8]}: {checkout.stderr.strip()}\n"
                f"  the pin is the point: if upstream removed this commit, fix the pin deliberately."
            )
        head = run_git("-C", str(target), "rev-parse", "HEAD").stdout.strip()
        if head != commit:
            raise SystemExit(f"{slug} is at {head[:8]} but the pin says {commit[:8]}")
        print(f"  ✔ {slug} at {commit[:8]} (pinned)")


def main():
    parser = argparse.ArgumentParser(description="Materialize the audited inputs at their pinned commits.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--templates-only", action="store_true", help="just the ten issue forms")
    group.add_argument("--full", action="store_true", help="full checkouts at the pins")
    args = parser.parse_args()

    print("════════════════════════════════════════════════════════════════════")
    print(" VENDOR — inputs pinned to the commits the figures cite")
    print("════════════════════════════════════════════════════════════════════")

    if args.templates_only:
        written, unchanged = fetch_templates()
        total = sum(len(names) for _commit, names in PINS.values())
        print(f"   issue forms: {written} written, {unchanged} already at the pin, {total} total")
        print(f"   pins: " + " · ".join(f"{slug}@{commit[:8]}" for slug, (commit, _n) in sorted(PINS.items())))
    else:
        fetch_full()

    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
