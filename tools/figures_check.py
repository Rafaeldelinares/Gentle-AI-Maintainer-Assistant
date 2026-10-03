#!/usr/bin/env python3
"""
figures_check.py — Compare the figures the documents CLAIM against the figures reality PRODUCES.

Why this exists
---------------
The project's rule is that no figure is published without the command that produces it
(DECISIONS.md D-029). Nothing re-ran those commands afterwards, so a published count went
stale twice: one document claimed 27 board tests against a real 76, and later 125/125 and
76/76 outlived the suites becoming 129 and 79 across five documents. Both times, fixing the
cited line was not enough, because the surviving occurrence was always in another file.

The gate already had a step *labelled* "published figures", whose command was only
tools/metrics.py: it recomputes the figures and never reads a document. This is the check
that actually reads them.

THE CLAIM CONVENTION
--------------------
A count claim is written so that a machine can read it:

    <subject marker> → N/N

for example ``python3 test_rules.py`` → 129/129, or ``--full`` → 11/11. The arrow is what
makes the claim unambiguous, and only claims in that form are checked.

How this design was reached, recorded because the dead ends matter
-----------------------------------------------------------------
* **First attempt** checked every `N/M` ratio it found. It cried wolf 44 times on legitimate
  ratios: `385/997` of audited issues, `32/34` judge agreement, `939/1228` loaded rows,
  `×8/8` of missing fields, `483/483` bands at audit time. A guard that fires on real prose
  gets switched off, which is worse than no guard.
* **Second attempt** attributed each ratio to the nearest subject marker. That is genuinely
  ambiguous in this prose: a label sometimes precedes the value (`--full` → 10/10) and
  sometimes follows it (12/12 contract tests), and `sin --full` *contains* `--full`, so
  distance alone picked the wrong marker. Every rule that tried to guess produced its own
  counterexample.
* **This version** stops guessing. It requires the claim to carry its own binding — the
  arrow — and skips anything else. A ratio that is not a claim about a subject simply is not
  a claim about a subject, and the guard says how many it skipped rather than inventing an
  attribution for it.

DECLARED GAPS — what this does NOT cover, and why
-------------------------------------------------
* Metric figures in prose (the total, the bands, the percentages, cited in 13 documents).
  They need the same treatment — a claim form a machine can read — which is a larger
  decision than this unit.
* The digest values published in STATUS.md and DETERMINISM.md: checking them means running
  the determinism check (~41 s) here, doubling the gate cost.
* Counts written in other shapes, such as a bare `(27)` next to a filename. The historical
  defect of that shape is why the convention exists; migrating old prose is a follow-up.

Usage
-----
    python3 tools/figures_check.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Subject markers, most specific first so that a nested marker never wins.
MARKERS = (
    ("sin `--full`", "gate fast"),
    ("sin --full", "gate fast"),
    ("without --full", "gate fast"),
    ("no --full", "gate fast"),
    ("con `--full`", "gate full"),
    ("con --full", "gate full"),
    ("with --full", "gate full"),
    ("`--full`", "gate full"),
    ("--full", "gate full"),
    ("test_rules", "rule suite"),
    ("rule suite", "rule suite"),
    ("rules suite", "rule suite"),
    ("test_board", "board suite"),
    ("board domain", "board suite"),
    ("schemas", "contracts"),
    ("contract tests", "contracts"),
    ("verify_all", "gate fast"),
)

# marker, then an arrow/equals/colon, then the count — nothing else in between.
CLAIM = re.compile(r"^[\s`*]*[→=:][\s`*]*(\d+)\s*/\s*(\d+)")


def run_capture(cmd):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)


def parse_ratio(text, marker):
    """Return N from the first 'MARKER: N/N' line, or None."""
    for line in text.splitlines():
        if marker in line:
            tail = line.split(marker, 1)[1].strip()
            head = tail.split()[0] if tail.split() else ""
            if "/" in head:
                left, _, right = head.partition("/")
                if left.isdigit() and right.isdigit() and left == right:
                    return int(left)
    return None


def gate_totals():
    """Compute the gate totals from verify_all's own lists, never hardcoded.

    main() appends the contracts step OUTSIDE those lists, and only when .venv exists, so
    the denominator is environment-dependent. Computing it here is the point: a hardcoded
    total would go stale exactly the way the documents did.
    """
    sys.path.insert(0, str(ROOT / "tools"))
    import verify_all  # noqa: E402  (path set above)

    contracts_step = 1 if (ROOT / ".venv" / "bin" / "python").exists() else 0
    fast = len(verify_all.FAST_CHECKS) + contracts_step
    full = len(verify_all.FAST_CHECKS) + len(verify_all.FULL_CHECKS) + contracts_step
    return fast, full


def establish_truth():
    """Run the real producers. A source that cannot be measured is a failure, not a pass."""
    truth = {}
    failures = []

    for label, script, marker in (
        ("rule suite", "test_rules.py", "FINAL TEST RESULT:"),
        ("board suite", "test_board.py", "FINAL TEST RESULT:"),
    ):
        result = run_capture([sys.executable, script])
        value = parse_ratio(result.stdout, marker) if result.returncode == 0 else None
        if value is None:
            failures.append(f"cannot establish the {label} total: {script} did not report it")
        else:
            truth[label] = value

    venv = ROOT / ".venv" / "bin" / "python"
    if venv.exists():
        result = run_capture([str(venv), "schemas/validate.py"])
        value = parse_ratio(result.stdout, "FINAL RESULT:") if result.returncode == 0 else None
        if value is None:
            failures.append("cannot establish the contracts total: schemas/validate.py did not report it")
        else:
            truth["contracts"] = value

    fast, full = gate_totals()
    truth["gate fast"] = fast
    truth["gate full"] = full
    return truth, failures


def tracked_documents():
    """Tracked Markdown only, minus generated reports.

    Untracked `odd/` holds planning notes with counts that are not product claims, and
    `report-*.md` are regenerated outputs, not claims. Scanning either would add noise.
    """
    result = run_capture(["git", "ls-files", "*.md"])
    if result.returncode != 0:
        return []
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and not Path(line.strip()).name.startswith("report-")
    ]


def claims_on_line(line):
    """Yield (subject, position, n, m) for every marker-bound claim on this line.

    A marker nested inside a longer marker is dropped, so the `--full` inside `sin --full`
    cannot compete for the claim that `sin --full` governs.
    """
    found = []
    for marker, subject in MARKERS:
        pos = 0
        while True:
            at = line.find(marker, pos)
            if at == -1:
                break
            pos = at + 1
            found.append((at, at + len(marker), subject))
    kept = [
        f
        for f in found
        if not any(o[0] <= f[0] and f[1] <= o[1] and (o[1] - o[0]) > (f[1] - f[0]) for o in found)
    ]
    for at, stop, subject in sorted(kept):
        match = CLAIM.match(line[stop:])
        if match:
            yield subject, at, int(match.group(1)), int(match.group(2))


def main():
    print("════════════════════════════════════════════════════════════════════")
    print(" PUBLISHED FIGURES CHECK (documents versus reality)")
    print("════════════════════════════════════════════════════════════════════")

    truth, truth_failures = establish_truth()
    if truth_failures:
        for message in truth_failures:
            print(f"   ❌ {message}")
        print("\n   A guard that cannot measure must not pass.")
        return 1

    print("   truth: " + " · ".join(f"{k} {v}/{v}" for k, v in sorted(truth.items())))

    documents = tracked_documents()
    if not documents:
        print("   ❌ no tracked Markdown found; cannot check any claim")
        return 1
    print(f"   scanned: {len(documents)} tracked documents (generated reports excluded)")

    checked = 0
    problems = []

    for name in documents:
        path = ROOT / name
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for subject, _at, n, m in claims_on_line(line):
                checked += 1
                if n != m:
                    problems.append((name, lineno, f"{subject} → {n}/{m}", f"is not a matched pair"))
                elif n != truth[subject]:
                    problems.append((name, lineno, f"{subject} → {n}/{m}", f"the real value is {truth[subject]}/{truth[subject]}"))

    print(f"   claims in the canonical form: {checked}")
    if not checked:
        print("   ⚠ no claim was found in the canonical form; the convention is `<marker> → N/N`")
        return 0

    if problems:
        print()
        for name, lineno, claim, why in sorted(problems):
            print(f"   ❌ {name}:{lineno}  claims {claim} — {why}")
        print(f"\n   {len(problems)} claim(s) do not match reality")
        print("════════════════════════════════════════════════════════════════════")
        return 1

    print(f"   ✔ every claim in the canonical form matches reality ({checked} checked)")
    print("   declared gaps: prose metric figures, the digest values, counts written in other shapes")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
