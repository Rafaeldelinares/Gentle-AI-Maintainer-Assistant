# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-10-04

First tagged state. A deterministic triage engine for three repositories, a local Kanban board,
four mechanical analysis modules, and a gate that runs in CI on every push.

### Added

- **Deterministic triage engine** (`db/rules.py`) over a sanitized snapshot of 1,228 open issues
  from `gentle-ai`, `engram` and `gentle-shell`, with JSON Schema contracts for every artifact.
- **`decide()`**, the engine's decision as a first-class value: band, rule, evidence and an
  ordered trace, so nothing re-derives the cascade from the engine's private patterns.
- **Local Kanban board** (`board/`) on `127.0.0.1:8770`, one board per application, with an
  append-only event log and a rebuild check that proves the derived state is reconstructible.
- **Four mechanical modules** that need no human labels: completeness against each repository's
  real issue forms, probable duplicates, cross-repo links, and possibly obsolete references.
- **`tools/verify_all.py`**, the single gate: twelve checks that cover the invariants, the suites,
  the figures, and the determinism of every derived output.
- **`tools/figures_check.py`**, which compares the figures the documents claim against the figures
  reality produces, over a claim convention a machine can read.
- **`.github/workflows/gate.yml`**, the fast gate on every push over inputs pinned to the commits
  the published figures cite.
- **`maintainer_assistant.py`**, one entry point over the previously twenty-one scripts.
- Governance artifacts: `PROMISES.md`, `DECISIONS.md`, `STATUS.md`, `MODULES.md`, `BOARD.md`,
  `TAGS.md`, `GLOSSARY.md`, `DETERMINISM.md`, `OBSERVABILITY.md`, `AUDIT.md`, `EVALUATION.md`.

### Notes

- The read-only invariant is enforced by `tools/readonly_check.py`: outbound reads are allowed,
  writes to third-party repositories are not.
- No precision figure is published. The instrument exists and the human labels are zero; the
  project says "no disponible" rather than inventing a number.
- `--full` is not part of CI: the module reports walk the audited repositories' git history and
  need the complete checkouts. That difference is declared, not hidden.

[Unreleased]: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/releases/tag/v0.1.0
