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
| P-03 | "Snapshot is sanitized: no personal data, logins or emails" | `issues.json` stores `slug`, `number`, `title`, `body`, `labels`, `cross_refs`, `system_id` only; no `author`/`user` field. `git grep -i "@"` on the snapshot finds no email addresses | **cumplida** | Reviewer can re-run the check with the command above |

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
| P-24 | "No maintainer names or person-level metrics" | `git grep` for maintainer logins and person-level percentages returns nothing in the project's own files | **parcial** | No automated check is committed; a `tools/privacy_check.py` is pending |
| P-25 | "Nothing irreversible without asking: no data deletion, no history rewrite, no force-push" | `AGENTS.md` limits; no such command exists in project tooling (`tools/readonly_check.py` would flag `git push`) | **parcial** | Policy-level; not machine-enforced beyond the push check |

## 4. Quality & validation promises

| # | Promise (README) | Evidence | Status | What is missing |
| --- | --- | --- | --- | --- |
| P-30 | "94.1% agreement with Judge A and 85.3% with Judge B on 34 deterministic matches out of a 90-issue sample" | `python3 db/rules.py` section 2 | **parcial** | This is the **calibration** sample, not held-out validation. The README says so explicitly |
| P-31 | "7.9% lexical-keyword precision (16/202) in gentle-shell" | `python3 tools/metrics.py` (lexical section); definition: gentle-shell issues mentioning `gentle-ai` that carry a cross-system `cross_ref` | **cumplida** | The metric is a lower bound by construction (only indexed links count) |
| P-32 | "The rule suite passes and is reproducible" | `python3 test_rules.py` → `FINAL TEST RESULT: 125/125 tests passed successfully.` | **cumplida** | Test count will change as cases are added; the file states no frozen total |
| P-33 | "The data contracts are valid and fail closed" | `python3 schemas/validate.py` → `FINAL RESULT: 12/12 tests passed successfully.` | **cumplida** | None |
| P-34 | "The three core modules (completeness, duplicates, cross-repo links, obsolete issues) exist" | — | **sin evidencia** | **Not implemented.** The README does not claim them today; when implemented, this row becomes the evidence row |
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
| Cross-repo coverage: 345 issues mention another repo without a structured link | **pending** | `AUDIT.md` §10; `tools/metrics.py` cross-repo section | Not started |

---

## 6. Honest summary

- **Sustained today:** scale and label census (P-01…P-03), deterministic coverage and its distribution (P-10…P-14, P-16…P-18), read-only invariant (P-20), human authority (P-21, P-23), and the two test suites (P-32, P-33).
- **Partially sustained:** H9 (P-15, small n), the calibration agreement (P-30, calibration not held-out), H2 as an automated assertion (P-22), the privacy check (P-24), the irreversible-actions check (P-25).
- **Not sustained / not implemented:** the mechanical modules (P-34), shadow mode (P-35), and the labelling-and-metrics tool (P-36). None of them is claimed in the README today.
- **Never claimed and never to be claimed until measured:** precision improvements. Every rule change made after `AUDIT.md` is **pending human validation against a fresh labelled sample**.
