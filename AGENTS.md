# AGENTS.md — Gentle-AI-Maintainer-Assistant

> **Project:** Gentle-AI-Maintainer-Assistant  
> **Status:** Proposal & Design Phase (Phases 0–7 Complete & Empirically Validated)  
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
* **Triage debt:** 76.5% of open issues are completely untriaged.
* Documented in `docs/phase-1-ecosystem-inspection.md`.

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
* Automated validation test suite (`schemas/validate.py`) passing 9/9 positive and fail-closed negative tests.
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
* Full backlog sweep across remaining 749 grey-area issues.
* Interactive TUI / dashboard for maintainer review.
