# AGENTS.md — Gentle-AI-Maintainer-Assistant

> **Project:** Gentle-AI-Maintainer-Assistant  
> **Status:** Phase 1.1 (rule hardening) and the read-only adversarial audit complete; deterministic engine, contracts, promise contract and decision log in place. Next: mechanical modules, shadow mode, labelling tool.  
> **Ecosystem:** [Gentleman-Programming](https://github.com/Gentleman-Programming) (`gentle-ai`, `engram`, `gentle-shell`)

This document establishes the authoritative governance protocol and architectural roadmap for the Gentle AI Maintainer Assistant.

---

## 🏛️ Core Principles & Invariants

1. **Human Authority Axiom:** The assistant is an advisor and router, never an autonomous decision-maker. It never applies labels, closes issues, or transfers issues on GitHub without explicit maintainer approval.
2. **Zero Issue Loss:** Triage functions as a router, not a silent filter ("sin perder de vista ningún issue"). Every issue remains visible and tracked.
3. **Explainable Priority Bands:** Priority is never reduced to a single black-box score. It is expressed as an explainable band (**P0–P3**) supported by textual citations and structured dimensions.
4. **Code > LLM:** Structural heuristics in code (`db/rules.py`) resolve predictable cases instantly without cost or non-deterministic noise. LLMs are reserved for grey-area reasoning.
5. **Calibrated Alert Discipline (Rule H9):** P1 is strictly reserved for production dead-ends with no workaround and no retry. Manual workarounds or retry recovery demote to P2 to prevent maintainer alert fatigue.

---

## 📋 The Eight-Phase Protocol

### Phase 0: Ground Rules & Constraints
* Read-only exploration. No mutations on GitHub.
* Local SQLite with FTS5 trigram indexing instead of heavy Docker containers.
* Empirical validation on real ecosystem data before code implementation.

### Phase 1: Ecosystem Inspection & Backlog Census
* **Census completed:** 1,228 open issues across `gentle-ai` (733), `gentle-shell` (424, formerly `gentle-pi`), and `engram` (71).
* **Triage bottleneck:** High issue-to-maintainer ratio across the three core repositories.
* **Triage debt:** Only 178 of 1,228 open issues (14.5%) carry an explicit `priority:*` label; 1,050 (85.5%) carry none, and 686 (55.9%) sit under `status:needs-review`.
* **Deterministic coverage:** `db/rules.py` resolves 510 of 1,228 open issues (41.5%) with pure code; 718 (58.5%) remain grey-area for the LLM pipeline.
* **Recomputed by:** `python3 tools/metrics.py` (no figure is hardcoded).
* Documented in `docs/phase-1-ecosystem-inspection.md`.

### Phase 1.1: Deterministic Rule Hardening
* Negation and context safeguards: patterns never fire on `no/without/not ... data loss`, on `is not a deadlock`, on fix descriptions such as *"from being silently dropped to being rejected"*, or on metaphorical deadlocks.
* Deterministic silent-data-loss matches are emitted strictly as **"candidato P0, requiere revisión humana"** (`rule:candidato_p0_requiere_revision_humana`), enforced bidirectionally by the schema, never as a final P0.
* Human-review gold set published as `gold-p0-p1.md` with `veredicto_humano: pendiente`.
* Rule suite `test_rules.py` uses concrete cases, not frozen totals, and validates snapshot self-consistency dynamically.

### Phase 1.2: Read-Only Adversarial Audit and Corrections
* `AUDIT.md` audited H1–H10 and the P0–P3 bands over 1,228 issues with a deterministic `sha256(slug#number) mod 5` split (group 0 held-out, groups 1–4 exploration).
* Confirmed findings, now fixed with named real-case tests:
  * Crash vocabulary widened (`crashes`, `uncaughtException`, `Go runtime panic`, `fails to start`, `out of memory`, `OOM killer`); generic `cannot start` deliberately excluded (blocked workflow, not a crash).
  * `title_prefix` recovered from the title when the ingested value is empty (leading backtick, `[Automated provider defect]`).
  * An explicit `docs:`/`chore:` prefix now wins over a conflicting `enhancement` label.
  * A hard signal under a `feat:`/`docs:` prefix is **not** auto-promoted; it is flagged by `requires_human_review()` while keeping its band.
  * Rule H9 workaround detection widened (`works if/after`, `retry works`, `restarting helps`); ambiguous `bypass`/`mitigation` removed.
* Every post-audit rule change is **pending human validation against a fresh labelled sample**; no precision improvement is claimed.
* Governed by `PROMISES.md` (claim → evidence → status → gap) and `DECISIONS.md` (decision → alternatives → consequence).

### Phase 2: Problem Definition & Operational Boundaries
* Characterized cross-system coupling edges and the 4 canonical implication patterns ((a)–(d)).
* Established boundaries: assistant generates inferences; maintainers make decisions.
* Documented in `docs/problem-definition.md`.

### Phase 3: Architectural Design
* Designed two-pass hybrid pipeline:
  * Fast-path deterministic pre-filter (`db/rules.py`).
  * Pass 1: A-priori isolated issue analysis with 13 dimensions.
  * Pass 2: Multi-system geographical correlation and escrow.
* Documented in `docs/architecture.md`.

### Phase 4: Calibrated Triage Model
* Defined P0–P3 operational boundaries and the 13 dimensions (enforcing honesty where D5, D7, D11 remain `unknown` a-priori).
* Codified Rules H1–H10, including Rule H9 (Workaround & Retry demotes to P2) calibrated with the maintainer.
* Documented in `docs/triage-model.md`.

### Phase 5: Decision Model & Asymmetric Escrow
* Modeled human maintainer decision lifecycle (`accept`, `override`, `relocate`, `defer`).
* Codified Asymmetric Escrow ("Hogar + Vista"): home repo retains custody until target repo claims it.
* Documented in `docs/decision-model.md`.

### Phase 6: JSON Schema Data Contracts
* Created JSON Schema Draft 2020-12 specifications matching `gentle-ai/contracts/`:
  * `schemas/issue-record.schema.json`
  * `schemas/triage-inference.schema.json`
  * `schemas/maintainer-decision.schema.json`
  * `schemas/triage-batch-report.schema.json`
* Automated validation test suite (`schemas/validate.py`) passing 12/12 positive and fail-closed negative tests, including bidirectional enforcement that a candidate P0 label requires the candidate rule and cannot be emitted as a final P0.
* Documented in `schemas/README.md`.

### Phase 7: Canonical Prompts Suite
* Authored production-ready prompts conforming to JSON schemas and calibrated rules:
  * `prompts/system-triage-agent.md` (Master System Prompt)
  * `prompts/pass-1-issue-analysis.md` (Pass 1 A-Priori)
  * `prompts/pass-2-cross-system-correlation.md` (Pass 2 Cross-System)
  * `prompts/maintainer-summary-view.md` (Interactive Maintainer Layout)
* Documented in `prompts/README.md`.

### Phase 8: Runtime Implementation (Pending Maintainer Approval)
* Packaging CLI tool and Pi subagent integration.
* Full backlog sweep across remaining 718 grey-area issues.
* Interactive TUI / dashboard for maintainer review.
