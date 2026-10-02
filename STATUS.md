# STATUS.md — Gentle AI Maintainer Assistant Project Status

> **Real-time implementation status tracking.**
> This file is updated on every phase commit to provide full visibility into completed tasks, current phase status, and pending milestones.

---

## Current Status: Phase 1.1 Complete (Waiting for Review & Approval)

* **Current Phase:** Phase 1.1 — Deterministic Rule Hardening (after Phase 1: Corregir la Base)
* **Status:** Complete (`77/77` rule tests passing, `12/12` schema tests passing)
* **Date:** 2026-10-02
* **Phase 1 Commit:** `854c38c` (`fase 1: fix regex boundaries, test suite, H9-H10 calibration, and reproducible snapshot`)
* **Phase 1.1 Commit:** the documentation-hash record commit for this phase follows the content commit; see the top-level repository log.

---

## Phase Breakdown

### ✅ Phase 1: Corregir la Base (Foundations & Deterministic Engine) — commit `854c38c`
* [x] **Word Boundary & Regex Group Fixes (`db/rules.py`):**
  * Converted regexes to non-capturing groups `(?:...)`.
  * Removed the trailing `\b` that broke punctuated tokens like `panic:`.
  * Detects silent-data-loss variants and fatal crash variants.
* [x] **Resolution of Rule H9 vs H10 Conflict:**
  * P1 is strictly assigned ONLY if no active workaround or retry recovery is detected.
  * Crashes with active workarounds or retry recovery demote to P2 (`rule:crash_with_workaround_demoted_to_p2`).
  * Explicit declarations of no workaround (`workaround: none`, `no workaround available`) remain P1.
* [x] **Elimination of Overfitted Patterns:**
  * Removed `busy-loop.*frozen` and `dead-end.*lineage` (overfitted to historical tickets).
* [x] **Reproducible Dataset Snapshot (`issues.json`):**
  * Published the 1,228 open issue snapshot stripped of personal data, logins, and emails.
  * `db/rules.py` dynamically calculates all counts and percentages without hardcoded strings.
* [x] **Governance & Cleanliness:**
  * Scrubbed all maintainer names and person-centric metrics across all files.
  * Confirmed MIT `LICENSE`. Corrected lexical precision to 7.4% (15/202) and clarified the calibration sample.
* [x] **Observability Infrastructure:**
  * Created `OBSERVABILITY.md` with direct raw URLs for all key files.
  * Updated `EVALUATION.md` to be self-contained with literal code and test output.

### ✅ Phase 1.1: Deterministic Rule Hardening (Negations, Deadlock Context, Candidate P0)

* [x] **Human-Review Gold Set (`gold-p0-p1.md`):**
  * Enumerates every issue currently flagged by the deterministic engine: 14 candidate P0 and 2 P1.
  * Each entry carries its issue link, trigger snippet, and `veredicto_humano: pendiente` (left unfilled on purpose).
  * A "Released False Positives" section records the 8 issues the corrected rules no longer flag, with the reason and the locking test.
* [x] **Negation & Fix-Description Safeguards:**
  * The data-loss rule no longer fires on `no/without/not ... data loss`.
  * The rule no longer fires on fix descriptions such as `from being silently dropped to being rejected`.
  * The deadlock rule no longer fires on `is not a deadlock`.
  * Concrete regression cases `gentle-ai#5007`, `#4792`, `#4807`, and `#2628` are locked by tests and are verified against the real snapshot.
* [x] **Deadlock Requires Process/Thread Context:**
  * `deadlock` now requires `goroutine`/`thread`/`mutex`/`lock`/`process`/`hang`/`worker` context within a bounded window.
  * Metaphorical deadlocks (`two rules deadlock each other`, `review denials deadlock the agent`) are rejected.
* [x] **Candidate P0 Governance Invariant:**
  * The deterministic band for silent data loss is now `candidato P0, requiere revisión humana` with rule `rule:candidato_p0_requiere_revision_humana`.
  * The JSON Schema enforces the invariant bidirectionally: a candidate label requires the candidate rule, and the candidate rule cannot emit a final `P0`.
  * A dedicated valid fixture (`triage-inference-p0-candidate.fixture.json`) and two fail-closed negative tests were added.
* [x] **Tests Use Concrete Cases, Not Frozen Totals:**
  * `test_rules.py` was rewritten to assert specific behaviors and named real issues instead of `"exactly 17/7"` counts.
  * Snapshot checks assert that the named issues are classified as expected and that the dynamic run is reproducible; no total is hardcoded.
  * Result: `77/77` tests passing.
* [x] **Documentation Alignment:**
  * `README.md`, `AGENTS.md`, and `EVALUATION.md` now report the current computed figures consistently: **39.3% deterministic (483 / 1,228)** and **60.7% grey area (745 / 1,228)**.
  * Removed the phrase "Empirically Validated" and all `/home/rafael` local paths.
  * Removed the stale embedded code block with hardcoded counts from `README.md`.

---

### ⏳ Phase 2: Mechanical Modules (Reorienting the Product) — Pending
* [ ] **Module A (Completeness):** Compare open bug reports against repository templates and flag missing fields.
* [ ] **Module B (Probable Duplicates):** Correlate matching stack traces, error strings, and normalized titles.
* [ ] **Module C (Cross-Repo Linking):** Canonical issue linking preserving Asymmetric Escrow ("Hogar + Vista").
* [ ] **Module D (Possibly Obsolete Issues):** Detect mentions of deleted files, functions, or CLI flags against repository source history.

### ⏳ Phase 3: Shadow Mode & Empirical Metrics — Pending
* [ ] Generate shadow priority inferences for all issues without mutating GitHub.
* [ ] Create a labeling template (`labeling.md`) with 100–150 stratified issues for human review (reserving a held-out test split).
* [ ] Measure false negatives on P0/P1 and precision per rule with sample sizes.

### ⏳ Phase 4: Maintainer Report (`REPORT.md`) — Pending
* [ ] Generate `REPORT.md` (max 15 items per section, with `verificado_por_humano: no`).
* [ ] Summary candidate table and total backlog metrics.
