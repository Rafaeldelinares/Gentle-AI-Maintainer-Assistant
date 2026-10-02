# STATUS.md — Gentle AI Maintainer Assistant Project Status

> **Real-time implementation status tracking.**
> This file is updated on every phase commit to provide full visibility into completed tasks, current phase status, and pending milestones.

---

## Current Status: Phase 1 Complete (Waiting for Review & Approval)

* **Current Phase:** Phase 1: Corregir la Base (Fixing Foundations)
* **Status:** Complete (48/48 unit tests passing, 9/9 schema tests passing)
* **Date:** 2026-10-02
* **Phase 1 Commit:** `573c732`

---

## Phase Breakdown

### ✅ Phase 1: Corregir la Base (Foundations & Deterministic Engine)
* [x] **Word Boundary & Regex Group Fixes (`db/rules.py`):**
  * Converted regexes to non-capturing groups `(?:...)`.
  * Removed trailing `\b` breaking punctated tokens like `panic:`.
  * Fully detects silent data loss variants (`silently dropped rows`, `silently corrupted the db`, `silently lost data`, `silently overwrites files`).
  * Fully detects fatal crash variants (`panic: runtime error: index out of range`, `SIGSEGV`, `NullPointerException`, `deadlock`, `fatal error: runtime`).
* [x] **Comprehensive Test Suite (`test_rules.py`):**
  * 48 positive and negative test cases.
  * Negative safeguards for P0 (e.g., `prevents data loss`, `no data loss`, `without data loss` do NOT trigger P0).
  * 48/48 tests passing.
* [x] **Resolution of Rule H9 vs H10 Conflict:**
  * P1 is strictly assigned ONLY if no active workaround or retry recovery is detected.
  * Crashes with active workarounds or retry recovery demote to P2 (`rule:crash_with_workaround_demoted_to_p2`).
  * Explicit statements of no workaround (`workaround: none`, `no workaround available`) are protected from false-positive demotion and remain P1.
* [x] **Elimination of Overfitted Patterns:**
  * Removed `busy-loop.*frozen` and `dead-end.*lineage` (overfitted to historical tickets).
  * Replaced with general crash and concurrency deadlock patterns.
* [x] **Reproducible Dataset Snapshot (`issues.json`):**
  * Published full 1,228 open issue snapshot (5.3 MB) stripped of all personal data, logins, and emails.
  * `db/rules.py` dynamically calculates all counts and percentages from data without hardcoded strings.
* [x] **Governance & Cleanliness (`AGENTS.md`, `README.md`):**
  * `AGENTS.md` updated with full Phase 0–8 protocol without local paths (`/home/rafael/...`).
  * Scrubbed all maintainer names and person-centric metrics ("bus factor", commit percentages per person) across all files.
  * Confirmed MIT `LICENSE`. Corrected lexical precision to 7.4% (15/202) and sample size (n=35 calibration sample).
* [x] **Observability Infrastructure:**
  * Created `OBSERVABILITY.md` with direct raw URLs for all key files.
  * Updated `EVALUATION.md` to be completely self-contained with literal code, test runner output, and empirical metrics.

---

### ⏳ Phase 2: Mechanical Modules (Reorienting the Product) — Pending
* [ ] **Module A (Completeness):** Compare open bug reports against repository templates and flag missing fields.
* [ ] **Module B (Probable Duplicates):** Correlate matching stack traces, error strings, and normalized titles.
* [ ] **Module C (Cross-Repo Linking):** Canonical issue linking preserving Asymmetric Escrow ("Hogar + Vista").
* [ ] **Module D (Possibly Obsolete Issues):** Detect mentions of deleted files, functions, or CLI flags against repository source history.

### ⏳ Phase 3: Shadow Mode & Empirical Metrics — Pending
* [ ] Generate shadow priority inferences for all issues without mutating GitHub.
* [ ] Create labeling template (`labeling.md`) with 100–150 stratified issues for human review (reserving held-out test split).
* [ ] Measure false negatives on P0/P1 and precision per rule with sample sizes.

### ⏳ Phase 4: Maintainer Report (`REPORT.md`) — Pending
* [ ] Generate `REPORT.md` (max 15 items per section, with `verificado_por_humano: no`).
* [ ] Summary candidate table and total backlog metrics.
