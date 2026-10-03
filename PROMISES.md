# PROMISES.md — Promise Contract

> **What this file is.** Every claim the README makes about what the tool does, mapped to the evidence that supports it, its current status, and what is still missing.
> **How to read it.** `cumplida` = verifiable today with the cited command. `parcial` = true but bounded (calibration sample, missing held-out, or partial coverage). `sin evidencia` = no evidence yet; if a promise cannot be sustained, it is removed from the README.
> **Rule.** Nothing below is asserted without a path, a command, or a test. Figures are recomputed by `tools/metrics.py`; no figure is hardcoded.

Last verified against commit `HEAD` (`git rev-parse --short HEAD`) by running every command in the *Evidence* column.

---

## 1. Data & scale promises

| # | Promise (README) | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-01 | "1,228 open issues across 3 core repositories" | `issues.json` (1,228 records); `python3 tools/metrics.py` prints `total open issues: 1228` and per-repo counts | **cumplida** | Snapshot is a point-in-time copy, not a live feed |
| P-02 | "Only 178 of 1,228 (14.5%) carry an explicit `priority:*` label; 1,050 (85.5%) carry none; 686 (55.9%) under `status:needs-review`" | `python3 tools/metrics.py` (label census section) | **cumplida** | None |
| P-03 | "Snapshot is sanitized: no personal data, logins or emails" | `python3 tools/privacy_check.py` → no `author`/`user`/`login`/`email` field, no forbidden maintainer handle, no non-placeholder email; `issues.json` stores only `slug`, `number`, `title`, `body`, `labels`, `cross_refs`, `system_id` | **cumplida** | One maintainer handle found in an issue body was redacted (see §6); example placeholders (`p@example.invalid`, `reproduction@example.com`) and a Go telemetry filename are allow-listed, not personal data |

## 2. Deterministic engine promises

| # | Promise (README) | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-10 | "510 of 1,228 open issues (41.5%) resolved deterministically with no LLM call" | `python3 tools/metrics.py` → `classified by code (no LLM): 510 (41.5%)` | **cumplida** | Coverage is a census, not a correctness measure |
| P-11 | "718 open issues (58.5%) remain grey area" | same command | **cumplida** | Grey-area correctness depends on the LLM passes, which are not run over the full backlog |
| P-12 | "Feature requests → P2 (395 issues)" | `python3 tools/metrics.py` rule histogram | **cumplida** | Precision of this rule is only measured on the calibration sample (P-30) |
| P-13 | "Docs/chores → P3 (80 issues)" | same | **cumplida** | Same caveat |
| P-14 | "Hard crashes without workaround → P1 (17 issues)" | same | **cumplida** | Precision **not validated by humans**; the crash vocabulary was widened after `AUDIT.md` and needs a fresh labelled sample |
| P-15 | "Crash with workaround/retry → P2, Rule H9 (4 issues)" | same; `test_rules.py` §7 | **parcial** | H9 fired 0 times before the audit; it now fires 4 times, all with an explicit workaround section. Still a small n |
| P-16 | "Silent data loss → `candidato P0, requiere revisión humana` (14 issues), never a final P0" | `python3 tools/metrics.py`; `schemas/validate.py` negative tests 4 and 5 enforce it bidirectionally | **cumplida** | The 14 are **candidates**; a maintainer has confirmed none of them |
| P-17 | "A hard signal under a non-bug prefix is never auto-promoted; it is flagged for human review (26 issues)" | `python3 tools/metrics.py` → `flagged for human review: 26`; `test_rules.py` §13 | **cumplida** | Flag precision not validated by humans |
| P-18 | "No figure is hardcoded" | every README figure is recomputed by `tools/metrics.py` and `db/rules.py`; `test_rules.py` §14 asserts reproducibility across two passes | **cumplida** | None |

## 3. Authority & safety promises

| # | Promise (README / AGENTS) | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-20 | "Strictly read-only on third-party repositories: no comment, label, close, PR or issue" | `python3 tools/readonly_check.py` → exit 0, "no mutating GitHub or HTTP write operation found" | **cumplida** | Static check only; it cannot prove absence of a future manual action |
| P-21 | "The assistant never assigns final priority; the human decides" | `schemas/maintainer-decision.schema.json` requires a human `actor`; negative test 2 in `schemas/validate.py` rejects a decision without it; the engine's P0 output is a *candidate* label | **cumplida** | None |
| P-22 | "A band is never emitted without a reason and a citation (H2)" | `AUDIT.md` §8: 483/483 bands (at audit time) had an evidence anchor, 0 violations; `db/rules.py` returns `(band, cross, rule_name)` and every rule has a matched span | **parcial** | The audit measured this over the corpus once; it is not yet an automated assertion in `test_rules.py` |
| P-23 | "`veredicto_humano` is never filled by the tool" | `gold-p0-p1.md`: every entry says `veredicto_humano: pendiente`; no code writes that field | **cumplida** | None |
| P-24 | "No maintainer names or person-level metrics" | `python3 tools/privacy_check.py` → no forbidden maintainer handle in the snapshot; no person-level metric exists in any project file | **cumplida** | The handle list in the checker is explicit and must be extended when a new handle is learned |
| P-25 | "Nothing irreversible without asking: no data deletion, no history rewrite, no force-push" | `AGENTS.md` limits; no such command exists in project tooling (`tools/readonly_check.py` would flag `git push`) | **parcial** | Policy-level; not machine-enforced beyond the push check |

## 4. Quality & validation promises

| # | Promise (README) | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-30 | "94.1% agreement with Judge A and 85.3% with Judge B on 34 deterministic matches out of a 90-issue sample" | `python3 db/rules.py` section 2 | **parcial** | This is the **calibration** sample, not held-out validation. The README says so explicitly |
| P-31 | "7.9% lexical-keyword precision (16/202) in gentle-shell" | `python3 tools/metrics.py` (lexical section); definition: gentle-shell issues mentioning `gentle-ai` that carry a cross-system `cross_ref` | **cumplida** | The metric is a lower bound by construction (only indexed links count) |
| P-32 | "The rule suite passes and is reproducible" | `python3 test_rules.py` → `FINAL TEST RESULT: 129/129 tests passed successfully.` | **cumplida** | Test count will change as cases are added; the file states no frozen total |
| P-33 | "The data contracts are valid and fail closed" | `python3 schemas/validate.py` → `FINAL RESULT: 12/12 tests passed successfully.` | **cumplida** | None |
| P-34 | Module D (obsolete issues) exists | `python3 modules/obsolete.py`; report `report-obsolete.md`; checks the vendored checkouts at the commits it cites | **cumplida** | Class A (deleted path) is verifiable but still needs human judgment; Class B is not obsolescence evidence |
| P-40 | "Module A: completeness — flags open reports missing the fields their own issue form requires" | `python3 modules/completeness.py`; report `report-completeness.md`; templates parsed from `products/<repo>/.github/ISSUE_TEMPLATE/*.yml` | **cumplida** | The signal is deterministic but its precision is not human-verified; issues outside the form are excluded and reported separately |
| P-41 | "Module B: probable duplicates — correlates shared error signatures and normalized titles" | `python3 modules/duplicates.py`; report `report-duplicates.md`; evidence tiers and per-pair citations | **cumplida** | A shared signature is evidence, not proof; siblings can share identifiers. Never closes or merges |
| P-42 | "Module C: cross-repository references not captured by `cross_refs`" | `python3 modules/cross_repo.py`; report `report-cross-links.md` | **cumplida** | Only an explicit `repo#N` reference produces a proposed link; bare mentions never do |
| P-43 | "Reports regenerate deterministically from the frozen snapshot" | `python3 tools/run_reports.py`; `python3 tools/determinism_check.py` runs each module under two `PYTHONHASHSEED` values and fails if a report changes | **cumplida** | Module D needs the vendored checkouts under `products/` (`./sync-products.sh`) |
| P-44 | "Module D: possibly obsolete issues — references to deleted source paths, checked against the repository history" | `python3 modules/obsolete.py`; report `report-obsolete.md`; per-issue commit citation | **cumplida** | Two classes kept apart: Class A (deleted path) is verifiable, Class B (unresolved reference) is weak and explicitly not an obsolescence claim |

## 4b. Board (local Kanban console)

| # | Promise | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-50 | "Local Kanban board, one per application, never mixed" | `python3 board/server.py --ingest` → `http://127.0.0.1:8770/`; `test_board.py` asserts each board contains only its repository's cards | **cumplida** | In testing; no real-usage validation yet |
| P-51 | "The board never writes to GitHub" | The board has no outbound HTTP client at all; `tools/readonly_check.py` now fails on `http.client`, `urllib.request` or `requests` anywhere in the project | **cumplida** | Static check; it cannot prove absence of a future manual action |
| P-52 | "The engine only suggests blocking columns; promoting to a maintainer is human" | `board/core.py` `SUGGESTIBLE_COLUMNS`; `test_board.py` asserts no card is auto-promoted to `listo_mantener` or `en_manos` | **cumplida** | None |
| P-53 | "Every human action is append-only and the state is reconstructible from the log" | `python3 tools/board_rebuild_check.py` wrecks the caches, rebuilds from events and compares, on a temporary copy and on the live DB | **cumplida** | None |
| P-54 | "The board never fills `veredicto_humano`" | The engine writes no verdict event; `test_board.py` asserts no label was written by an `engine%` actor | **cumplida** | The UI still lets a human choose it, by design |
| P-55 | "Local only: no LAN exposure, no auth needed" | `board/server.py` refuses any host other than `127.0.0.1`/`localhost`/`::1`; default port 8770, distinct from the CRM cockpit on 8000 | **cumplida** | None |
| P-58 | "The derived layer is deterministic: the same snapshot yields the same result byte for byte" | `python3 tools/determinism_check.py` → engine digest stable across `PYTHONHASHSEED` 1/7/99, four module reports byte-identical, board derived projection byte-identical | **cumplida** | Deterministic *within* a snapshot; when the snapshot changes the figures change, which is why its hash is always shown |
| P-59 | "The system does not learn from human movements" | `test_board.py` asserts 1,228/1,228 identical suggestions with and without 40 human decisions on the same snapshot | **cumplida** | Deliberate: learning would break P-58 (see `DECISIONS.md` D-025) |
| P-61 | "The board can explain why any phrase was classified the way it was" | Button «Probar una regla»; `POST /api/simulate`; `board/explain.py` | **cumplida** | The simulated band is what the engine *would* decide, not a truth |
| P-62 | "The simulator writes nothing" | `test_board.py` and a live check: human activity is identical before and after simulating | **cumplida** | None |
| P-63 | "The explainer cannot drift from the engine" | `test_board.py` compares `explain()` against the real classification for 400 snapshot issues | **cumplida** | Covers 400 of 1,228 (a sample, for test speed) |
| P-64 | "Rules are not editable from the UI" | No write path exists; `DECISIONS.md` D-026 | **cumplida** | Deliberate: UI-edited local rules would break P-58 and make the rules invisible to the external reviewer |
| P-66 | "Precision is measured from human labels only" | `python3 tools/precision_report.py` — reads `human_labels` + the event log, computes P0/P1 false negatives, per-rule precision with its `n`, and a Wilson 95% interval | **cumplida (el instrumento)** | The instrument exists and is tested against a synthetic scenario. With **0 human labels** it reports «no disponible» rather than inventing a number. The figure itself is **pending labels** |
| P-67 | "The labelling sample is stratified, deterministic and uncontaminated" | `python3 tools/label_sample.py --write` → `label-sample.md`; ordering from `sha256('label:'+ref)`; excludes the calibration sample and the held-out group the audit inspected | **cumplida** | 120 issues selected (12 P0, 13 P1, 30 P2, 8 P3, 57 grey) out of 928 eligible; 90 excluded for contamination |
| P-65 | "Human counter-verdicts become rule proposals" | — | **sin evidencia** | **Not implemented.** Listed as pending in `DETERMINISM.md` |
| P-60 | "The board shows what is still missing, in the app" | Button «Determinismo y límites» in the board; `DETERMINISM.md` in the root | **cumplida** | The list is maintained by hand; it is not generated |
| P-56 | "Module B/C/D signals appear as per-card badges" | — | **sin evidencia** | **Not implemented.** Only band, rule, human-review flag and Module A missing fields are per-card today; B/C/D remain report-level |
| P-57 | "Two views: cards and a system view aggregated by root class" | — | **sin evidencia** | **Not implemented** (planned as E4) |
| P-35 | "Shadow mode: suggested priority computed without showing or applying it" | — | **sin evidencia** | **Not implemented.** Not claimed in the README today |
| P-36 | "A labelling tool computes false negatives of P0/P1 and precision per rule from human labels" | — | **sin evidencia** | **Not implemented.** Not claimed in the README today |

## 5. Findings from the external audit: state of each correction

| Audit finding | Fix status | Evidence | Validation status |
| --- | --- | --- | --- |
| Narrow crash vocabulary (`crashes`, `uncaughtException`, "Go runtime panic", `fails to start`, `out of memory`) | **fixed** | `db/rules.py` `RE_P1_CRASH_CORE`; `test_rules.py` §5; named cases `gentle-shell#962`, `gentle-ai#4677` | **Pending human validation** |
| Empty `title_prefix` (leading backtick, bracket prefix) | **fixed** | `derive_title_prefix`; `test_rules.py` §12; named case `gentle-ai#4974` | **Pending human validation** |
| `feature` rule evaluated before `docs` (`gentle-ai#5168`) | **fixed** | `db/rules.py` explicit-prefix precedence; `test_rules.py` §10; named case `#5168` | **Pending human validation** |
| `is_bug` blocks `feat:` with hard signals from reaching P0/P1 | **mitigated, not promoted** | `requires_human_review()`; `test_rules.py` §13; 26 issues flagged; band intentionally unchanged | **Pending human validation** |
| H9 never fires on real data | **investigated + widened** | `RE_WORKAROUND_POSITIVE` widened; now 4 real demotions (`gentle-ai#4809`, `#3016`, `gentle-shell#745`, `#1052`); `test_rules.py` §7–8 | **Pending human validation** |
| Cross-repo coverage: 345 issues mention another repo without a structured link | **quantified by Module C** | `modules/cross_repo.py`: only **33** issues carry an explicit `repo#N` reference; **15** resolve to an open issue; the rest are prose mentions, which are not links | `report-cross-links.md` |
| Snapshot privacy: maintainer handle inside an issue body | **fixed** | `tools/privacy_check.py` → clean; the handle was redacted, reclassification verified identical before/after | **cumplida** |
| Module B report changed across processes | **fixed** | `tools/determinism_check.py` → all reports byte-identical; ordering is now total (`-score, tier, pair`), and set iteration is sorted | **cumplida** |

---

| P-68 | "Every unit of this delivery passed native review" | `STATUS.md` states the exact state per unit | **sin evidencia (parcial)** | **Not true and not claimed.** C1a's review is open with 4 lenses pending; one unit's 4 lenses ran and produced a CRITICAL that was corrected, but its **targeted validation is pending** (D-028, facade defect); the remaining units are committed and not yet reviewed |
| P-69 | "No unit closed a review it did not close" | `DECISIONS.md` D-028; no figure or claim in this repo asserts a completed validation | **cumplida** | The word used everywhere is **pendiente** |

## 6. Honest summary

- **Sustained today:** scale and label census (P-01…P-03), deterministic coverage and its distribution (P-10…P-14, P-16…P-18), read-only invariant (P-20), human authority (P-21, P-23), and the two test suites (P-32, P-33).
- **Partially sustained:** H9 (P-15, small n), the calibration agreement (P-30, calibration not held-out), H2 as an automated assertion (P-22), the privacy check (P-24), the irreversible-actions check (P-25).
- **Not sustained / not implemented:** the remaining board work (P-56, P-57), shadow mode (P-35) and the labelling-and-metrics tool (P-36). The mechanical modules (P-34, P-40…P-44) and the board core (P-50…P-55) are implemented. None of the remaining items is claimed in the README today.
- **Never claimed and never to be claimed until measured:** precision improvements. Every rule change made after `AUDIT.md` is **pending human validation against a fresh labelled sample**.
