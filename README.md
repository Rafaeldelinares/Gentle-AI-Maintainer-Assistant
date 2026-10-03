# Gentle AI Maintainer Assistant

> **AI-assisted, explainable triage and cross-system classification engine for the [Gentleman-Programming](https://github.com/Gentleman-Programming) ecosystem.**
>
> **Status:** Proposal & Design Phase (Phases 1–7 in progress; Phase 1 complete and under review).

<div align="center">

<a href="https://github.com/Gentleman-Programming/gentle-ai#built-with-gentle-ai">
  <img width="220" src="https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/docs/assets/brand/built-with-gentle-ai.png" alt="Built with Gentle-AI" />
</a>

<p><sub>Built with <strong><a href="https://github.com/Gentleman-Programming/gentle-ai#built-with-gentle-ai">Gentle-AI</a></strong> — Memory, Workflows & Evidence.</sub></p>

</div>

---

## 🎯 Executive Summary & Purpose

Managing multi-repository agent ecosystems creates unique maintenance bottlenecks:

* **The Backlog Scale:** 1,228 open issues across 3 core repositories (`gentle-ai`, `gentle-shell`, `engram`).
* **Untriaged Triage State:** Only 178 of 1,228 open issues (14.5%) carry an explicit `priority:*` label; 1,050 (85.5%) carry none, and 686 (55.9%) sit under `status:needs-review`.
* **Ecosystem Influx:** Rapid open-source growth across three tightly coupled repositories (`gentle-ai`, `engram`, `gentle-shell`), generating an influx of issues while maintainers must triage hundreds of incoming tickets and develop new features.
* **Cross-System Blindness:** Issues filed in one repository frequently stem from, depend on, or affect another repository without either maintainer having visibility.

**Gentle AI Maintainer Assistant** acts as an **intelligent, explainable router (not a filter)** to protect maintainer cognitive load without losing track of a single issue. It never autonomously closes or decides issues; it provides structured, citation-backed recommendations for human review.

> **All figures in this document are recomputed by `tools/metrics.py` from `issues.json` (1,228 open issues, sanitized snapshot) and re-verified by `test_rules.py`. No figure is hardcoded.** Reproduce them with `python3 tools/metrics.py`, `python3 db/rules.py` and `python3 test_rules.py`.

---

## 🔬 Key Empirical Discoveries & Architecture

This proposal is backed by empirical research on the real 1,228-issue dataset.

### 1. Code > LLMs (The Deterministic Pipeline)

* Running full-text LLM prompts on every issue is slow, expensive, and subject to stochastic sampling noise.
* **Empirical finding:** **510 of 1,228 open issues (41.5%)** can be resolved **deterministically in milliseconds** using pure code rules (`db/rules.py`), with no LLM call:
  * Feature requests (`feat:` / `type:feature` / `enhancement`) ──► **P2** (395 issues).
  * Chores, docs, questions (`docs:` / `type:chore`) ──► **P3** (80 issues).
  * Hard crashes without workaround (`panic:`, `SIGSEGV`, `crashes`, `uncaughtException`, `fails to start`, `out of memory`) ──► **P1** (17 issues).
  * Crash with a documented workaround or retry recovery ──► **P2** (4 issues, Rule H9).
  * **Silent data loss / corruption ──► "candidato P0, requiere revisión humana"** (14 issues): a *candidate P0 that requires human review*, never an autonomous final P0 decision.
* The remaining **718 open issues (58.5%)** fall through to the calibrated two-pass LLM pipeline.
* Additionally, **26 issues (17 with a loss signal, 9 with a crash signal)** keep their low band but are flagged **"requires human review"** because a hard signal sits under a non-bug prefix (`feat:`/`docs:`). The band is never auto-promoted.
* On the calibration sample (34 deterministic matches out of 90 sampled issues): **94.1% agreement** with Judge A (`MiniMax-M3`, 32/34) and **85.3%** with Judge B (`DeepSeek-V4-Flash`, 29/34). This sample was used during calibration; **out-of-sample validation is pending a fresh human-labeled sample** (see `PROMISES.md`).

### 2. Calibrated P1 vs P2 Operational Policy (Rule H9)

* In dual-judge runs (`MiniMax-M3` vs `DeepSeek-V4-Flash`), the primary divergence was the interpretation of *"broken in production"*:
  * Judge A marked any initial failure as P1.
  * Judge B demoted to P2 if a documented manual workaround or retry existed.
* **Maintainer Axiom (Rule H9):** To prevent **alert fatigue** (which would otherwise inflate urgent P1 counts), **P1 is strictly reserved for dead-ends with no viable escape hatch**. If an issue has a manual workaround, recovers upon retry, or is a UX annoyance, it is classified as **P2**.

### 3. Asymmetric Escrow ("Hogar + Vista") for Misplaced Issues

* Lexical keyword matching fails (**7.9% precision, 16/202**: gentle-shell issues mentioning `gentle-ai` that carry a confirmed cross-system link) due to internal naming collisions (e.g. `gentle-shell` contains `extensions/gentle-ai.ts` and `.git/gentle-ai/`).
* Misplaced issues remain owned by the repository where they were reported (*Hogar*), and only generate notifications for the target system (*Vista*) until a human maintainer explicitly claims and transfers them. Zero issues are lost or silently deleted.

---

## 📖 End-to-End Walkthrough & Practical Examples

For a concrete, step-by-step demonstration of the pipeline:
👉 **[Read the Full Walkthrough (`docs/walkthrough-examples.md`)](docs/walkthrough-examples.md)**

The walkthrough uses illustrative, clearly synthetic issue numbers so that no invented scenario is attributed to a real ticket; the verified real-issue examples live in [`EVALUATION.md`](EVALUATION.md) §7 and [`gold-p0-p1.md`](gold-p0-p1.md).

* **Example 1 (Deterministic Fast-Path):** The silent data loss reported in `gentle-ai#4917` is flagged in milliseconds with 0 tokens as **candidato P0, requiere revisión humana** — a candidate for human review, not a final decision.
* **Example 2 (Hard Crash P1):** `gentle-shell#1606`, an unhandled async `EMFILE` that crashes `pi` on startup, is flagged as **P1** via `rule:hard_crash` (no workaround present).
* **Example 3 (Grey-Area Fall-Through):** `gentle-ai#5166` mentions a "dead-end" that is not a runtime crash and offers no process/thread context; the corrected engine routes it to LLM Pass 1 instead of falsely flagging P1.
* **Example 4 (Maintainer Dashboard & Human Decision):** The interactive view presented to maintainers and the resulting immutable decision contract.

---

## 📂 Project Structure

```
.
├── README.md               # You are here: proposal overview & evaluation guide
├── AGENTS.md               # Governance contract and development protocol
├── PROMISES.md             # Promise contract: every README claim vs its evidence
├── DECISIONS.md            # Design decisions with alternatives considered
├── AUDIT.md                # Read-only adversarial audit of the rules
├── STATUS.md               # Phase status, commit hashes and stop-and-wait gate
├── OBSERVABILITY.md        # Canonical raw GitHub URLs for every reviewable artifact
├── EVALUATION.md           # Self-contained external audit guide (code, tests, metrics)
├── gold-p0-p1.md           # Human-review gold set for candidate P0 and P1 rule matches
├── issues.json             # Sanitized snapshot of 1,228 open issues (no personal data)
├── test_rules.py           # Deterministic rule test suite (concrete cases, no frozen totals)
├── MODULES.md               # Mechanical read-only modules: method, code, outputs, limits
├── BOARD.md                 # Local Kanban console: columns, rules, limits (in testing)
├── GLOSSARY.md              # What P0-P3, the badges and the sidebar mean
├── TAGS.md                  # Detailed reference for every tag
├── DETERMINISM.md           # What is deterministic, what is not, what is pending
├── label-sample.md          # The stratified sample to label by hand (measurement input)
├── board/                   # Local board: domain, HTTP, static UI
├── report-completeness.md   # Module A output: reports missing their form's required fields
├── report-duplicates.md     # Module B output: probable duplicate pairs with shared evidence
├── report-cross-links.md    # Module C output: cross-repo references not in cross_refs
├── report-obsolete.md       # Module D output: references to deleted source paths
├── modules/
│   ├── common.py            # Shared helpers (snapshot, links, report writer)
│   ├── templates.py         # Parses each repository's GitHub issue form
│   ├── completeness.py      # Module A
│   ├── duplicates.py        # Module B
│   ├── cross_repo.py        # Module C
│   └── obsolete.py          # Module D
├── tools/
│   ├── metrics.py                       # Recomputes every published figure
│   ├── precision_report.py              # Precision from human labels (nothing invented)
│   ├── label_sample.py                  # Stratified, deterministic labelling sample
│   ├── run_reports.py                   # Regenerates all module reports
│   ├── determinism_check.py             # Fails if a report changes across processes
│   ├── readonly_check.py                # Fails if any source performs a GitHub mutation
│   └── privacy_check.py                 # Fails if the snapshot carries personal data
├── docs/                   # Architectural & design specifications
│   ├── walkthrough-examples.md          # 4 concrete end-to-end operational examples
│   ├── phase-1-ecosystem-inspection.md  # Backlog census (1,228 issues)
│   ├── problem-definition.md            # Problem framing & boundaries
│   ├── architecture.md                  # Two-pass pipeline architecture
│   ├── triage-model.md                  # P0–P3 bands, 13 dimensions, rules H1–H10
│   └── decision-model.md                # Human authority, judgment schemas, auditability
├── schemas/                # Formally typed data contracts (JSON Schema Draft 2020-12)
│   ├── issue-record.schema.json         # Canonical ingested issue representation
│   ├── triage-inference.schema.json     # Assistant recommendation output contract
│   ├── maintainer-decision.schema.json  # Authoritative human decision contract
│   ├── triage-batch-report.schema.json  # Batch export envelope
│   ├── validate.py                      # Automated validation test runner (12/12 pass)
│   └── fixtures/                        # Sample valid & invalid test payloads
├── prompts/                # Canonical agent prompts for LLM inference
│   ├── system-triage-agent.md           # Master System Prompt (invariants & traps)
│   ├── pass-1-issue-analysis.md         # Pass 1: A-priori isolated issue analysis
│   ├── pass-2-cross-system-correlation.md# Pass 2: Multi-system geographical correlation
│   └── maintainer-summary-view.md       # Interactive Markdown layout for human maintainer
└── db/                     # Data engine & deterministic heuristics
    ├── schema.sql                       # SQLite + FTS5 trigram schema (no Docker needed)
    ├── rules.py                         # Deterministic rule engine (resolves 41.5% of backlog)
    ├── load.py                          # Ingestion pipeline for ecosystem issues
    ├── sample.py                        # Stratified reproducible sampling tool
    └── ingest.py                        # Judge votes and task completion ingestor
```

---

## 🚀 How to Evaluate this Proposal

Anyone reviewing this repository can independently evaluate the contracts, rules, and designs.

### 0. Fetch the vendored checkouts (required for two checks)

```bash
./sync-products.sh
```

The board suite and the Module A/B/C/D reports read the audited repositories' real issue
forms and source from `products/`, which is **deliberately outside git**. Without it the
board cannot tell whether a report is missing information, so it reports completeness as
*unavailable* rather than guessing, and `tools/verify_all.py` says which checks need the step.
Everything else runs without it.

### 1. Run the Contract Validation Test Suite

Verify that all schemas adhere to JSON Schema Draft 2020-12 and fail closed on violations:

```bash
python3 -m venv .venv
.venv/bin/pip install jsonschema
.venv/bin/python schemas/validate.py
```

*Expected result:* `FINAL RESULT: 12/12 tests passed successfully.`

### 2. Recompute Every Published Figure

`tools/metrics.py` recomputes the backlog census, the deterministic coverage, the rule histogram and the human-review flags. Nothing is hardcoded:

```bash
python3 tools/metrics.py
```

### 3. Inspect the Deterministic Rules Engine

See how pure code classifies 41.5% of open issues without calling an LLM, and run the rule regression suite:

```bash
python3 db/rules.py
python3 test_rules.py
```

*Expected result:* `FINAL TEST RESULT: 129/129 tests passed successfully.`

### 4. Review the Promise Contract

* [`PROMISES.md`](PROMISES.md) maps every claim in this README to its evidence, status and gap.
* [`DECISIONS.md`](DECISIONS.md) records each design decision with the alternatives considered.

### 5. Review the Triage & Decision Models

* Read [`docs/triage-model.md`](docs/triage-model.md) to inspect the 13 dimensions and rules H1–H10.
* Read [`docs/decision-model.md`](docs/decision-model.md) to inspect how human authority is structurally preserved.

### 6. Review the Human-Review Gold Set

* Read [`gold-p0-p1.md`](gold-p0-p1.md): every issue currently flagged by the deterministic engine, its trigger snippet, and its `veredicto_humano: pendiente` field awaiting maintainer judgment.

### 7. Review the Mechanical Modules

The modules do not need labels to be useful: they compare each report with its own issue form, correlate duplicates by shared error signatures, and surface cross-repository references.

* [`MODULES.md`](MODULES.md) — method, embedded source and limits.
* [`report-completeness.md`](report-completeness.md) — reports missing required fields.
* [`report-duplicates.md`](report-duplicates.md) — probable duplicate pairs with shared evidence.
* [`report-cross-links.md`](report-cross-links.md) — cross-repo references not in `cross_refs`.
* [`report-obsolete.md`](report-obsolete.md) — references to deleted source paths, with the commit each check ran against.

```bash
python3 tools/run_reports.py
python3 tools/determinism_check.py   # reports must be byte-identical across processes
```

### 8. Review the Board (in testing)

A local Kanban console with one board per application. Read-only toward GitHub; human decisions live in a local append-only log.

```bash
python3 board/server.py --ingest     # http://127.0.0.1:8770/
```

* [`BOARD.md`](BOARD.md) — how to run it, the columns, the derived-vs-decided split and the limits.
* [`GLOSSARY.md`](GLOSSARY.md) — what P0–P3, the card badges, `zona gris` and the sidebar mean.
* [`TAGS.md`](TAGS.md) — the detailed reference for every tag: how it is decided, real examples, what it does *not* mean, and its limits.
* [`DETERMINISM.md`](DETERMINISM.md) — what is deterministic and how it is verified, what is not and why, whether the system learns from your movements, and what is still pending.

> The port is **8770**, deliberately distinct from the ByBusiness CRM cockpit already serving on `http://localhost:8000/`.

### 9. Review the Agent Prompts

* Inspect [`prompts/system-triage-agent.md`](prompts/system-triage-agent.md) and [`prompts/pass-1-issue-analysis.md`](prompts/pass-1-issue-analysis.md).

---

## 🔍 Archivos para revisión / Files for Review

Direct GitHub blob URLs for external auditors and automated web fetchers:

* **[EVALUATION.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/EVALUATION.md)** — Comprehensive self-contained audit guide: complete source code of `rules.py` and `test_rules.py`, literal rules H1–H10, 13 dimensions, 20 sample issues, and metrics methodology with provenance.
* **[gold-p0-p1.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/gold-p0-p1.md)** — Human-review gold set for candidate P0 and P1 rule matches.
* **[STATUS.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/STATUS.md)** — Phase status and commit hashes.
* **[OBSERVABILITY.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/OBSERVABILITY.md)** — Canonical raw URLs for every artifact.
* **[db/rules.py](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/db/rules.py)** — Deterministic triage rule engine (Python).
* **[test_rules.py](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/test_rules.py)** — Deterministic rule regression suite.
* **[docs/triage-model.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/triage-model.md)** — Calibrated triage model, bands P0–P3, 13 dimensions, and rules H1–H10.
* **[docs/decision-model.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/decision-model.md)** — Human maintainer decision authority, auditability, and Asymmetric Escrow ("Hogar + Vista").
* **[prompts/system-triage-agent.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/prompts/system-triage-agent.md)** — Master System Prompt for triage inference agents.
* **[schemas/validate.py](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/schemas/validate.py)** — Automated test runner for JSON Schema Draft 2020-12 data contracts.
* **[docs/walkthrough-examples.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/walkthrough-examples.md)** — End-to-end walkthrough with 4 concrete operational examples.

---

## 📜 Policy Appendix: Triage Model (Operational Summary)

*The canonical, unabridged model lives in [`docs/triage-model.md`](docs/triage-model.md). The deterministic engine itself lives in [`db/rules.py`](db/rules.py) and is exercised by [`test_rules.py`](test_rules.py).*

### Priority Bands & Operational Boundaries

* **Candidate P0 (`candidato P0, requiere revisión humana`):** Pattern-matched silent data loss, corruption, or security exposure. **Emitted only as a candidate requiring human review, never as a final decision.**
* **P1 (`priority:high`):** Serious hard blocker in production **with NO workaround and NO retry recovery**. Workflow is dead-ended.
* **P2 (`priority:medium`):** Degrades functionality, **OR an accessible manual workaround exists, OR intermittent recovery upon retry, OR feature request**.
* **P3 (`priority:low`):** Cosmetic, documentation, question, chore, minor discussion.

### The 10 Hard Governance Rules

* **H1:** Cross-system implication alone never promotes a band. Only patterns (a) and (b) do.
* **H2:** A band is never emitted without at least one reason and at least one citation.
* **H3:** A band is always inference. Confidence is mandatory.
* **H4:** Pattern (c) (two independent causes) must be split into separate issues, never promoted as one.
* **H5:** Pattern (d) (cosmetic across systems) never promotes. Reach is not harm.
* **H6:** A missing dimension is `unknown`. It is never inferred silently.
* **H7:** A maintainer override always wins and is recorded as a decision.
* **H8:** Pass-1 bands are provisional. Pass 2 may correct them.
* **H9 (Workaround & Retry):** If a documented or accessible manual workaround exists, or if failure is intermittent and recovers upon retry, the issue **MUST** be classified as P2, never P1.
* **H10 (Code > LLM):** Issues matching unambiguous structural patterns (`feat:` -> P2, `docs:` -> P3, `panic:`/`crashes` -> P1, silent data loss -> **candidate P0 requiring human review**) are classified deterministically by code without invoking an LLM. An explicit `docs:`/`chore:` prefix wins over a conflicting `enhancement` label.

Negation and context safeguards are mandatory: a pattern never fires on `no/without/not ... data loss`, on `is not a deadlock`, on fix descriptions such as *"from being silently dropped to being rejected"*, or on metaphorical deadlocks such as *"two rules deadlock each other"*.

---

## 💬 Feedback & Open Questions for Reviewers

We actively invite feedback from other maintainers and contributors:

1. **P1 vs P2 Operational Boundary:** Does the strict "no workaround, no retry" boundary match your daily maintenance workflow?
2. **Escrow Workflow:** Would you prefer automated issue transfer proposals on GitHub via PR, or an interactive TUI/CLI dashboard first?
3. **Delivery Mechanism:** Should the assistant ship as a standalone CLI tool, a Pi/Gentle-AI skill bundle, or both?

Feel free to open an issue or start a discussion to share your perspective!

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
