#!/usr/bin/env python3
"""
maintainer_assistant.py — the project's single entry point.

Before this there were twenty-one `__main__` scripts and a README that listed which to run for
what. That is fine for the author and hostile to everyone else: a reader has to find the right
file, remember the arguments, and know which of them need the vendored inputs.

    maintainer-assistant check              the gate
    maintainer-assistant check --full       the gate plus the module reports and determinism
    maintainer-assistant vendor             fetch the audited inputs at their pinned commits
    maintainer-assistant board              the local Kanban board, on 127.0.0.1:8770
    maintainer-assistant reports            regenerate the four module reports
    maintainer-assistant figures            the published-figures guard on its own
    maintainer-assistant version            the version, read from pyproject.toml

Two properties are deliberate. It prints the file it is about to run, because a friendly name that
hides which script executes is a new indirection to debug. And every child gets a ceiling, because
the whole of the two units before this one were about a gate that could hang.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIMEOUT_SECONDS = 1800  # the full gate regenerates the module reports, so it is generous

# name -> the script it runs, and whether the extra arguments are forwarded.
SCRIPTS = {
    "check": ("tools/verify_all.py", True),
    "vendor": ("tools/vendor.py", True),
    "board": ("board/server.py", True),
    "reports": ("tools/run_reports.py", False),
    "figures": ("tools/figures_check.py", False),
}


def project_version():
    """One source of truth: the version lives in pyproject.toml, so the CLI cannot disagree."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib  # Python 3.11+
        return tomllib.loads(text)["project"]["version"]
    except ModuleNotFoundError:  # pragma: no cover - 3.10
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
        if not match:
            raise SystemExit("cannot read the version from pyproject.toml")
        return match.group(1)


def run(relative, extra):
    script = ROOT / relative
    if not script.exists():
        raise SystemExit(f"missing {relative}: the repository is incomplete")
    command = [sys.executable, str(script), *extra]
    print(f"── {relative} {' '.join(extra)}".rstrip())
    try:
        return subprocess.run(command, cwd=str(ROOT), timeout=TIMEOUT_SECONDS).returncode
    except subprocess.TimeoutExpired:
        raise SystemExit(f"{relative} timed out after {TIMEOUT_SECONDS}s")
    except OSError as error:
        raise SystemExit(f"cannot run {relative}: {error}")


def main(argv=None):
    names = list(SCRIPTS) + ["version"]
    parser = argparse.ArgumentParser(
        prog="maintainer-assistant",
        description="Read-only triage and maintainer assistance. The gate is `check`.",
        epilog="`check` is the one that matters: it is what CI runs and what a reviewer should run.",
    )
    parser.add_argument("command", choices=names, help="what to run")
    parser.add_argument("extra", nargs=argparse.REMAINDER,
                        help="arguments forwarded to the underlying script")
    args = parser.parse_args(argv)

    if args.command == "version":
        print(f"gentle-ai-maintainer-assistant {project_version()}")
        return 0

    relative, forwards = SCRIPTS[args.command]
    return run(relative, args.extra if forwards else [])


if __name__ == "__main__":
    sys.exit(main())
