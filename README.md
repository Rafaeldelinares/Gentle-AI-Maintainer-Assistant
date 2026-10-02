# Gentle AI Maintainer Assistant

> **AI-assisted, explainable triage and cross-system classification engine for the [Gentleman-Programming](https://github.com/Gentleman-Programming) ecosystem.**
>
> **Status:** Proposal & Design Phase (Phases 1–7 completed and empirically validated).

<div align="center">

<a href="https://github.com/Gentleman-Programming/gentle-ai#built-with-gentle-ai">
  <img width="220" src="https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/docs/assets/brand/built-with-gentle-ai.png" alt="Built with Gentle-AI" />
</a>

<p><sub>Built with <strong><a href="https://github.com/Gentleman-Programming/gentle-ai#built-with-gentle-ai">Gentle-AI</a></strong> — Memory, Workflows & Evidence.</sub></p>

</div>

---

## 🎯 Executive Summary & Purpose

Managing multi-repository agent ecosystems creates unique maintenance bottlenecks:
* **The Backlog Scale:** 1,228 open issues across 3 core repositories (`gentle-ai`, `gentle-shell`, `engram`), with 76.5% completely untriaged.
* **Maintainer Concentration:** High commit concentration around a single principal maintainer (`Alan-TheGentleman` accounts for ~47% of ecosystem commits, bus factor of 1 in `gentle-shell`).
* **Cross-System Blindness:** Issues filed in one repository frequently stem from, depend on, or affect another repository without either maintainer having visibility.

**Gentle AI Maintainer Assistant** acts as an **intelligent, explainable router (not a filter)** to protect maintainer cognitive load without losing track of a single issue. It never autonomously closes or decides issues; it provides structured, citations-backed recommendations for human review.

---

## 🔬 Key Empirical Discoveries & Architecture

This proposal is backed by empirical research on the real 1,228 issue dataset:

### 1. Code > LLMs (The Deterministic Pipeline)
* Running full-text LLM prompts on every issue is slow, expensive, and subject to ~13% stochastic sampling noise.
* **Empirical finding:** **39.0% of the entire backlog (479 of 1,228 issues)** can be resolved **deterministically in 5 milliseconds** using pure code rules (`db/rules.py`):
  * Feature requests (`feat:` / `type:feature` / `enhancement`) ──► **P2** (100% precision vs P0/P1).
  * Chores, docs, questions (`docs:` / `type:chore`) ──► **P3**.
  * Hard crashes (`panic:`, `SIGSEGV`) ──► **P1**.
  * Verified silent data loss / corruption ──► **P0**.
* Tested against blind multi-judge runs: **97.1% accuracy** against Judge A and **88.6%** against Judge B.

### 2. Calibrated P1 vs P2 Operational Policy (Rule H9)
* In empirical dual-judge runs (MiniMax-M3 vs DeepSeek-V4-Flash), the primary divergence was the interpretation of *"broken in production"*:
  * Juez A marked any initial failure as P1.
  * Juez B demoted to P2 if a documented manual workaround or retry existed.
* **Maintainer Axiom (Rule H9):** To prevent **alert fatigue** (which would otherwise produce 300+ urgent P1 issues), **P1 is strictly reserved for dead-ends with no viable escape hatch**. If an issue has a manual workaround, recovers upon retry, or is UX annoyance, it is classified as **P2**.

### 3. Asymmetric Escrow ("Hogar + Vista") for Misplaced Issues
* Lexical keyword matching fails (6% precision) due to internal naming collisions (e.g. `gentle-shell` contains `extensions/gentle-ai.ts` and `.git/gentle-ai/`).
* Misplaced issues remain owned by the repository where they were reported (*Hogar*), and only generate notifications for the target system (*Vista*) until a human maintainer explicitly claims and transfers them. Zero issues are lost or silently deleted.

---

## 📖 End-to-End Walkthrough & Practical Examples

For a concrete, step-by-step demonstration of how the tool processes real issues:
👉 **[Read the Full Walkthrough with 4 Concrete Examples (`docs/walkthrough-examples.md`)](docs/walkthrough-examples.md)**

* **Example 1 (Deterministic Fast-Path):** A runtime panic in `gentle-ai#5166` categorized as **P1** in <5 ms with 0 tokens.
* **Example 2 (Residual Grey-Area with Workaround):** A CLI path failure in `gentle-ai#712` where Rule H9 detects a manual workaround and demotes it from P1 to **P2**.
* **Example 3 (Cross-System Asymmetric Escrow):** An issue reported in `gentle-shell#142` whose root cause is inside `engram`, routed via Asymmetric Escrow without closing or losing it.
* **Example 4 (Maintainer Dashboard & Human Decision):** The interactive view presented to maintainers and the resulting immutable decision contract.

---

## 📂 Project Structure

```
.
├── README.md               # You are here: proposal overview & evaluation guide
├── AGENTS.md               # Governance contract and development protocol (Phases 0-7)
├── docs/                   # Architectural & design specifications
│   ├── walkthrough-examples.md          # 4 concrete end-to-end operational examples
│   ├── phase-1-ecosystem-inspection.md  # Backlog census (1,228 issues, commit shares)
│   ├── problem-definition.md            # Problem framing & boundaries
│   ├── architecture.md                  # Two-pass pipeline architecture
│   ├── triage-model.md                  # P0–P3 bands, 13 dimensions, rules H1–H10
│   └── decision-model.md                # Human authority, judgment schemas, auditability
├── schemas/                # Formally typed data contracts (JSON Schema Draft 2020-12)
│   ├── issue-record.schema.json         # Canonical ingested issue representation
│   ├── triage-inference.schema.json     # Assistant recommendation output contract
│   ├── maintainer-decision.schema.json  # Authoritative human decision contract
│   ├── triage-batch-report.schema.json  # Batch export envelope
│   ├── validate.py                      # Automated validation test runner (9/9 pass)
│   └── fixtures/                        # Sample valid & invalid test payloads
├── prompts/                # Canonical agent prompts for LLM inference
│   ├── system-triage-agent.md           # Master System Prompt (invariants & traps)
│   ├── pass-1-issue-analysis.md         # Pass 1: A-priori isolated issue analysis
│   ├── pass-2-cross-system-correlation.md# Pass 2: Multi-system geographical correlation
│   └── maintainer-summary-view.md       # Interactive Markdown layout for human maintainer
└── db/                     # Data engine & deterministic heuristics
    ├── schema.sql                       # SQLite + FTS5 trigram schema (no Docker needed)
    ├── rules.py                         # Deterministic rule engine (resolves 39% of backlog)
    ├── load.py                          # Ingestion pipeline for ecosystem issues
    ├── sample.py                        # Stratified reproducible sampling tool
    └── ingest.py                        # Judge votes and task completion ingestor
```

---

## 🚀 How to Evaluate this Proposal

Anyone reviewing this repository can independently evaluate the contracts, rules, and designs:

### 1. Run the Contract Validation Test Suite
Verify that all schemas adhere to JSON Schema Draft 2020-12 and fail closed on violations:
```bash
python3 -m venv .venv
.venv/bin/pip install jsonschema
.venv/bin/python schemas/validate.py
```
*Expected result:* `RESULTADO FINAL: 9/9 pruebas pasaron exitosamente.`

### 2. Inspect the Deterministic Rules Engine
See how pure code classifies 39% of issues without calling an LLM:
```bash
python3 db/rules.py
```

### 3. Review the Triage & Decision Models
* Read [`docs/triage-model.md`](docs/triage-model.md) to inspect the 13 dimensions and rules H1–H10.
* Read [`docs/decision-model.md`](docs/decision-model.md) to inspect how human authority is structurally preserved.

### 4. Review the Agent Prompts
* Inspect [`prompts/system-triage-agent.md`](prompts/system-triage-agent.md) and [`prompts/pass-1-issue-analysis.md`](prompts/pass-1-issue-analysis.md).

---

## 🔗 Direct Links for Reviewers & AI Assistants

If you or your AI agent need direct, absolute links to inspect the core files:

* **End-to-End Walkthrough & Examples (`walkthrough-examples.md`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/walkthrough-examples.md
  * Raw Markdown: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/walkthrough-examples.md
* **Deterministic Rules Engine (`rules.py`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/db/rules.py
  * Raw Code: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/db/rules.py
* **Calibrated Triage Model (`triage-model.md`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/triage-model.md
  * Raw Markdown: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/triage-model.md
* **Two-Pass Architecture (`architecture.md`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/architecture.md
  * Raw Markdown: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/architecture.md
* **Human Authority & Decision Model (`decision-model.md`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/decision-model.md
  * Raw Markdown: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/docs/decision-model.md
* **Master System Prompt (`system-triage-agent.md`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/prompts/system-triage-agent.md
  * Raw Markdown: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/prompts/system-triage-agent.md
* **Triage Inference Schema (`triage-inference.schema.json`):**
  * GitHub UI: https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/schemas/triage-inference.schema.json
  * Raw JSON: https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/triage-inference.schema.json

---

## 💬 Feedback & Open Questions for Reviewers

We actively invite feedback from other maintainers and contributors:
1. **P1 vs P2 Operational Boundary:** Does the strict "no workaround, no retry" boundary match your daily maintenance workflow?
2. **Escrow Workflow:** Would you prefer automated issue transfer proposals on GitHub via PR, or an interactive TUI/CLI dashboard first?
3. **Delivery Mechanism:** Should the assistant ship as a standalone CLI tool, a Pi/Gentle-AI skill bundle, or both?

Feel free to open an issue or start a discussion to share your perspective!
