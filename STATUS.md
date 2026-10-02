# STATUS.md — Gentle AI Maintainer Assistant, Project Status

> **Current state, what is done, what is missing, and what the owner must decide.**
> Updated on every delivery. The hash cited below is a real commit.

---

## Current Status: Delivery 2 — Mechanical read-only modules (A, B, C)

* **Delivery 1 commits:** `ad7b6b1` (engine corrections, promise contract, decision log), `fc34e85` (privacy redaction + checker).
* **Delivery 2 content commits:** `b07b282` (modules A/B/C, reports, docs), `8081020` (tier naming consistency).
* **This STATUS revision:** a documentation-only commit that follows `8081020`.
* **Date:** 2026-10-02
* **Tests:** `125/125` rule tests, `12/12` contract tests, read-only check green, privacy check green.
* **Figures:** recomputed by `python3 tools/metrics.py` and `python3 tools/run_reports.py`; nothing hardcoded.

---

## Delivery 2 — Mechanical modules (this delivery)

Three read-only modules that need **no human labels** to be useful. Full method, embedded source and limits: `MODULES.md`. Reports: `report-completeness.md`, `report-duplicates.md`, `report-cross-links.md`. Regenerate with `python3 tools/run_reports.py`.

* **Module A — completeness.** Parses each repository's real `.github/ISSUE_TEMPLATE/*.yml` and checks whether an open report carries the required fields. Result: 1,114 issues matched to a template, 1,043 filed through the form, **313 missing at least one required content field**; 71 issues outside the form are excluded and reported separately. Attestation checkboxes are reported apart from triage-critical content.
* **Module B — probable duplicates.** Deterministic evidence only: exception/panic class, error code, `file:line` frame, quoted error string, exit code, normalized titles. Result: **108 candidate pairs, 7 with strong evidence**, 101 weaker. Tiers are named "strong/weaker evidence", never "duplicate"; the report never closes or merges.
* **Module C — cross-repo links.** A proposed link requires an explicit `repo#N` that resolves to an open issue. Result: 48 explicit references, **15 resolving**, 33 not resolving, 81 unnumbered `owner/repo` references, 914 bare mentions. It reframes `AUDIT.md`'s "345 mentions": the actionable subset is small, and a mention is not a dependency.
* **Guard:** `tools/readonly_check.py` now also scans `modules/`. No module writes to `cross_refs`, to the dataset, or to GitHub.
* **Not validated:** none of the three modules has human-verified precision yet. They are deterministic and useful for triage reading, but a maintainer must judge the reports.

---

## Delivery 1 — Post-audit corrections, promise contract and decision log

* **Delivery commit:** `ad7b6b1` — `feat(triage): widen crash vocabulary, recover title_prefix, fix rule order, flag hard signals`
* **Privacy correction commit:** `fc34e85` — `fix(privacy): redact maintainer handle from snapshot, add privacy check`
* **Tests:** `125/125` rule tests, `12/12` contract tests, read-only check green.
* **Figures:** recomputed by `python3 tools/metrics.py`; nothing hardcoded.

---

## What is done

### Phase 1 — Foundations
* Deterministic engine `db/rules.py`, sanitized snapshot `issues.json` (1,228 issues, no personal data), JSON Schema contracts, MIT license.

### Phase 1.1 — Rule hardening
* Negation and context safeguards; candidate-P0 governance invariant enforced by the schema.
* Human-review gold set `gold-p0-p1.md` with `veredicto_humano: pendiente`.

### Phase 1.2 — Read-only adversarial audit
* `AUDIT.md` audited H1–H10 and the P0–P3 bands over the full corpus with a deterministic `sha256(slug#number) mod 5` split (held-out group 0 = 231 issues, exploration = 997).
* H1, H2 and H5: 0 violations. H3, H4, H6, H7, H8: **not auditable with this dataset**. H9 and H10: detailed findings.

### Delivery 1 — Corrections and governance (this delivery)
* **Crash vocabulary widened:** `crashes`, `uncaughtException`, `Go runtime panic`, `fails to start`, `out of memory`, `OOM killer`. Generic `cannot start` deliberately excluded (blocked workflow, not a crash). P1 went from 2 to 17 issues.
* **`title_prefix` recovered** from the title when the ingested value is empty (leading backtick, `[Automated provider defect]`).
* **Rule order fixed:** an explicit `docs:`/`chore:` prefix now wins over a conflicting `enhancement` label (`gentle-ai#5168` is P3).
* **No auto-promotion:** a hard signal under `feat:`/`docs:` keeps its band and is flagged by `requires_human_review()` — 26 issues (17 loss, 9 crash).
* **H9 now fires:** workaround detection widened; `bypass`/`mitigation` removed. 4 real demotions.
* **New governance artifacts:** `PROMISES.md` (claim → evidence → status → gap), `DECISIONS.md` (12 decisions with alternatives), `tools/metrics.py` (recomputes every figure), `tools/readonly_check.py` (read-only invariant).
* **Docs aligned:** `README.md`, `AGENTS.md`, `EVALUATION.md`, `OBSERVABILITY.md` all carry the recomputed figures and point to the promise contract.

### Delivery 1.1 — Privacy correction
* The snapshot was re-audited for personal data. One maintainer handle inside an issue body (`gentle-ai#3312`) was found and redacted to `@[maintainer]`.
* The band/rule digest before and after the redaction is identical, so no rule depends on the handle.
* `tools/privacy_check.py` now verifies: no `author`/`user`/`login`/`email` field, no forbidden maintainer handle, no non-placeholder email address.

---

## Current figures (recomputed, not written by hand)

| Metric | Value |
| --- | --- |
| Open issues | 1,228 (`gentle-ai` 733, `gentle-shell` 424, `engram` 71) |
| Resolved deterministically | **510 (41.5%)** |
| Residual grey area | **718 (58.5%)** |
| Candidate P0 | 14 |
| P1 | 17 |
| P2 | 399 |
| P3 | 80 |
| Flagged for human review | 26 |

> Coverage is a census, not a correctness measure. **Precision of the post-audit rules is pending human validation.**

---

## What is NOT validated

* **No precision figure for the post-audit rules.** The crash vocabulary and rule order changed after the audit; both are pending a fresh human-labelled sample. The README states this explicitly and claims no improvement.
* **Grey area not run end-to-end.** The two-pass LLM pipeline was run only on the 90-issue calibration sample.
* **Cross-repo linking incomplete.** 345 issues mention another repository with no structured link.
* **Mechanical modules, shadow mode and the labelling tool are not implemented.** Tracked in `PROMISES.md` §4.

---

## What is missing (next, in planned order)

1. **Module D — possibly obsolete issues** (plan item b, remaining): detect mentions of deleted files, functions or CLI flags; every suggestion must cite the source path and commit and be marked "posible, requiere verificación".
2. **Labelling tool for Rafael** (plan item d): stratified sample of 100–150 issues including P0/P1, a template to label, and a script that computes false negatives of P0/P1 and precision per rule with its `n` from human labels only. This unblocks every "pending human validation" claim.
3. **Shadow mode** (plan item c): compute suggested priority without showing or applying it.
4. **`REPORT.md` for maintainers** (plan item e): max 15 items per section, every item `verificado_por_humano: no` until reviewed.

Modules A, B and C are done and delivered. The planned order can be reordered only with a recorded decision in `DECISIONS.md`. Rationale for the current order: Module D completes the mechanical set with the same read-only guarantee; the labelling tool then converts "pending validation" into measured facts; shadow mode and the maintainer report come after, because they should be built on validated signals.

---

## What Rafael must decide

| # | Decision | Options | Blocks |
| --- | --- | --- | --- |
| 1 | Reorder the plan (labelling tool first, then modules)? | keep the proposed order / move shadow mode first / other | nothing today; the default is the proposed order |
| 2 | License | MIT is in place; confirm or change | nothing today |
| 3 | External contact / publishing | not requested; the tool stays internal until Rafael approves | any contact with maintainers |
| 4 | Fresh labelled sample | Rafael labels ~100–150 issues | every precision claim |

No question above blocks continued development; work proceeds on the proposed order until Rafael says otherwise.

---

## Constraints in force

* Read-only on third-party repositories; verified by `tools/readonly_check.py`.
* No maintainer names or person-level metrics.
* No `veredicto_humano` filled by the tool; every entry stays `pendiente`.
* No hardcoded figures in code or docs; everything is recomputed or cited.
* No irreversible operation without asking: no data deletion, no history rewrite, no force-push.
