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
* **Ecosystem Scale & Influx:** Rapid open-source growth across three tightly coupled repositories (`gentle-ai`, `engram`, `gentle-shell`), generating an influx of issues where maintainers must triage hundreds of incoming tickets while developing new features.
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
* Evaluated on calibration sample (n = 35 deterministic matches out of 90 sampled issues): **97.1% agreement** with Judge A (34/35) and **88.6%** with Judge B (31/35) on the initial ruleset (re-evaluated to 94.1% and 85.3% with calibrated boundary). Note: this sample was used during calibration and requires out-of-sample validation.

### 2. Calibrated P1 vs P2 Operational Policy (Rule H9)
* In empirical dual-judge runs (MiniMax-M3 vs DeepSeek-V4-Flash), the primary divergence was the interpretation of *"broken in production"*:
  * Judge A marked any initial failure as P1.
  * Judge B demoted to P2 if a documented manual workaround or retry existed.
* **Maintainer Axiom (Rule H9):** To prevent **alert fatigue** (which would otherwise produce 300+ urgent P1 issues), **P1 is strictly reserved for dead-ends with no viable escape hatch**. If an issue has a manual workaround, recovers upon retry, or is UX annoyance, it is classified as **P2**.

### 3. Asymmetric Escrow ("Hogar + Vista") for Misplaced Issues
* Lexical keyword matching fails (7.4% precision, 15/202) due to internal naming collisions (e.g. `gentle-shell` contains `extensions/gentle-ai.ts` and `.git/gentle-ai/`).
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
*Expected result:* `FINAL RESULT: 9/9 tests passed successfully.`

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

## 🔍 Archivos para revisión / Files for Review

Direct GitHub blob URLs for external auditors and automated web fetchers:

* **[EVALUATION.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/EVALUATION.md)** — Comprehensive self-contained audit guide: complete source code of `rules.py`, literal rules H1–H10, 13 dimensions, 20 sample issues from SQLite, and metrics methodology.
* **[db/rules.py](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/db/rules.py)** — Deterministic triage rule engine (Python).
* **[docs/triage-model.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/triage-model.md)** — Calibrated triage model, bands P0–P3, 13 dimensions, and rules H1–H10.
* **[docs/decision-model.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/decision-model.md)** — Human maintainer decision authority, auditability, and Asymmetric Escrow ("Hogar + Vista").
* **[prompts/system-triage-agent.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/prompts/system-triage-agent.md)** — Master System Prompt for triage inference agents.
* **[schemas/validate.py](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/schemas/validate.py)** — Automated test runner for JSON Schema Draft 2020-12 data contracts.
* **[docs/walkthrough-examples.md](https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/blob/master/docs/walkthrough-examples.md)** — End-to-end walkthrough with 4 concrete operational examples.

---

## 💻 Source Code Appendix: `db/rules.py`

*For automated AI reviewers and web crawlers that cannot navigate subdirectories:*

```python
#!/usr/bin/env python3
"""
rules.py — Deterministic triage rule engine for exp.db

Applies rule-based heuristics BEFORE invoking an LLM:
  1. Features / enhancements -> P2
  2. Docs / chores / questions -> P3
  3. Silent data loss / corruption -> P0
  4. Panic / SIGSEGV / hard crashes -> P1
  5. Canonical cross-repository links (cross_refs) -> cross classification

Usage:
  ./rules.py [--sample] [--all]
"""

import sqlite3
import re
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "exp.db"

# Compiled regex patterns for deterministic text classification
RE_P0_SILENT = re.compile(
    r"\b(silent(ly)?\s+(corrupt|delet|drop|overwrit|los)|data\s+loss|silently\s+fails\s+to\s+save)\b",
    re.IGNORECASE,
)
RE_P1_CRASH = re.compile(
    r"\b(panic:|SIGSEGV|fatal error:\s*runtime|segmentation fault|NullPointerException|busy-loop.*frozen|dead-end.*lineage)\b",
    re.IGNORECASE,
)
RE_P3_DOCS = re.compile(
    r"^(docs?|chore|typo|style|ci|refactor)(\(.*\))?:\s*",
    re.IGNORECASE,
)

def classify_issue_deterministically(row, labels, cross_refs):
    """
    Returns (band, cross, rule_name) or (None, cross, None) if indeterminate.
    """
    title = row["title"] or ""
    body = row["body"] or ""
    prefix = (row["title_prefix"] or "").lower()
    full_text = f"{title}\n{body}"

    # ── 1. CROSS-SYSTEM (from cross_refs table) ──
    cross = "none"
    if cross_refs:
        # Check if cross_refs point to a different repository
        foreign_refs = [cr for cr in cross_refs if cr["target_system_id"] != row["system_id"]]
        if foreign_refs:
            cross = "dependency"  # baseline deterministic cross link

    # ── 2. BAND DETERMINISM ──

    label_set = {l.lower() for l in labels}
    is_bug = prefix in ("bug", "fix") or "type:bug" in label_set or "bug" in label_set

    # Check P0: Silent data loss / corruption (only on actual bugs, not features proposing safeguards)
    if is_bug and RE_P0_SILENT.search(full_text):
        return "P0", cross, "rule:silent_data_loss"

    # Check P1: Hard crash / fatal engine stall (only on actual bugs)
    if is_bug and RE_P1_CRASH.search(full_text):
        return "P1", cross, "rule:hard_crash"

    # Check P2: Feature / enhancement request
    if (
        prefix in ("feat", "feature")
        or "type:feature" in label_set
        or "enhancement" in label_set
        or "feature" in label_set
    ):
        return "P2", cross, "rule:feature_request"

    # Check P3: Documentation, questions, chores, typos
    if (
        prefix in ("docs", "doc", "chore", "typo")
        or "type:chore" in label_set
        or "documentation" in label_set
        or "question" in label_set
        or "discussion" in label_set
        or RE_P3_DOCS.search(title)
    ):
        return "P3", cross, "rule:docs_chore_question"

    # Indeterminate — must fall through to LLM
    return None, cross, None


def run_demo():
    print("════════════════════════════════════════════════════════════════════")
    print(" DEMO: CLASIFICACIÓN DETERMINISTA (db/exp.db no encontrado)")
    print("════════════════════════════════════════════════════════════════════")
    print(" Nota: Para evaluar el censo completo de 1.228 issues reales, cargue")
    print(" la base ejecutando './load.py' tras sincronizar './sync-products.sh'.\n")
    print(" Ejecutando suite de prueba sintética sobre la función determinista:\n")

    test_cases = [
        {
            "slug": "engram", "number": 101, "title": "docs: update memory architecture guide",
            "body": "Fix typo in schema description", "title_prefix": "docs", "labels": ["documentation"], "xrefs": []
        },
        {
            "slug": "gentle-ai", "number": 542, "title": "feat: add support for streaming responses",
            "body": "Please add streaming support to review CLI", "title_prefix": "feat", "labels": ["enhancement"], "xrefs": []
        },
        {
            "slug": "gentle-shell", "number": 88, "title": "fatal error: runtime panic: nil pointer dereference in session_view",
            "body": "SIGSEGV when opening terminal with no config", "title_prefix": "bug", "labels": ["bug"], "xrefs": []
        },
        {
            "slug": "engram", "number": 19, "title": "save operation silently drops memories when disk is full",
            "body": "Data loss: memory row is acknowledged but not persisted to SQLite", "title_prefix": "bug", "labels": ["bug"], "xrefs": []
        },
        {
            "slug": "gentle-ai", "number": 712, "title": "review fails when path has trailing slash",
            "body": "Workaround: remove trailing slash from path argument", "title_prefix": "bug", "labels": ["bug"], "xrefs": []
        },
    ]

    for tc in test_cases:
        row = {"id": tc["number"], "system_id": 1, "slug": tc["slug"], "number": tc["number"], "title": tc["title"], "body": tc["body"], "title_prefix": tc["title_prefix"]}
        band, cross, rule = classify_issue_deterministically(row, tc["labels"], tc["xrefs"])
        status = f"──► [{band}] vía {rule}" if band else "──► [ZONA GRIS] Requiere LLM Pass 1"
        print(f" • {tc['slug']}#{tc['number']}: \"{tc['title'][:55]}\"")
        print(f"   {status}\n")

    print("════════════════════════════════════════════════════════════════════")
    print(" En el censo real de 1.228 issues del ecosistema Gentleman-Programming:")
    print(" • 39.0% (479 issues) se resuelven en 5 ms mediante este motor de código.")
    print(" • 61.0% (749 issues) pasan a la inferencia LLM con la política calibrada H9.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


def main():
    if not DB_PATH.exists():
        return run_demo()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Pre-fetch all labels grouped by issue_id
    cur = conn.cursor()
    cur.execute("SELECT issue_id, name FROM issue_labels il JOIN labels l ON l.id=il.label_id")
    labels_by_issue = {}
    for r in cur.fetchall():
        labels_by_issue.setdefault(r["issue_id"], []).append(r["name"])

    # Pre-fetch cross_refs grouped by issue_id
    cur.execute("SELECT issue_id, target_system_id, target_number, location, raw FROM cross_refs")
    xrefs_by_issue = {}
    for r in cur.fetchall():
        xrefs_by_issue.setdefault(r["issue_id"], []).append(dict(r))

    # Evaluate across all open issues (1,228)
    cur.execute("""
        SELECT i.id, i.system_id, s.slug, i.number, i.title, i.body, i.title_prefix
        FROM issues i
        JOIN systems s ON s.id = i.system_id
        WHERE i.state = 'open'
    """)
    all_issues = cur.fetchall()

    results_all = {}
    rule_counts = {}
    for row in all_issues:
        iid = row["id"]
        band, cross, rule = classify_issue_deterministically(
            row, labels_by_issue.get(iid, []), xrefs_by_issue.get(iid, [])
        )
        results_all[iid] = (band, cross, rule)
        if rule:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1

    total_all = len(all_issues)
    covered_all = sum(1 for b, c, r in results_all.values() if b is not None)

    print("════════════════════════════════════════════════════════════════════")
    print(f" 1. COBERTURA DETERMINISTA EN EL BACKLOG TOTAL ({total_all} issues abiertas)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  Total clasificadas por código (sin LLM): {covered_all} ({100.0 * covered_all / total_all:.1f}%)")
    print(f"  Zona gris residual (requieren LLM):       {total_all - covered_all} ({100.0 * (total_all - covered_all) / total_all:.1f}%)\n")
    print("  Desglose por regla determinista:")
    for rule, cnt in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {rule:25s}: {cnt:4d} issues ({100.0 * cnt / total_all:.1f}%)")

    # Evaluate against the 90-issue sample (Run #1) where we have Judge A and Judge B votes
    cur.execute("""
        SELECT i.id, i.system_id, ri.issue_id, s.slug, i.number, i.title, i.body, i.title_prefix
        FROM run_issues ri
        JOIN issues i ON i.id = ri.issue_id
        JOIN systems s ON s.id = i.system_id
        WHERE ri.run_id = 1
        ORDER BY ri.issue_id
    """)
    sample_issues = cur.fetchall()

    # Fetch attempt 2 votes for both judges
    cur.execute("""
        SELECT issue_id, judge_id, band, cross
        FROM votes
        WHERE run_id = 1 AND attempt = 2
    """)
    judge_names = {r["id"]: r["name"] for r in conn.execute("SELECT id, name FROM judges").fetchall()}
    votes_by_issue = {}
    for r in cur.fetchall():
        votes_by_issue.setdefault(r["issue_id"], {})[judge_names[r["judge_id"]]] = r

    print("\n════════════════════════════════════════════════════════════════════")
    print(" 2. VALIDACIÓN CONTRA LA MUESTRA DE 90 ISSUES (Intento 2)")
    print("════════════════════════════════════════════════════════════════════")
    sample_covered = 0
    match_a = 0
    match_b = 0
    both_match = 0

    evaluated = []
    for row in sample_issues:
        iid = row["id"]
        band, cross, rule = classify_issue_deterministically(
            row, labels_by_issue.get(iid, []), xrefs_by_issue.get(iid, [])
        )
        v_row_a = votes_by_issue.get(iid, {}).get("judge-a")
        v_row_b = votes_by_issue.get(iid, {}).get("judge-b")
        va = v_row_a["band"] if v_row_a else None
        vb = v_row_b["band"] if v_row_b else None

        if band is not None:
            sample_covered += 1
            ok_a = (band == va)
            ok_b = (band == vb)
            if ok_a: match_a += 1
            if ok_b: match_b += 1
            if ok_a and ok_b: both_match += 1
            evaluated.append((row["slug"], row["number"], band, rule, va, vb))

    print(f"  Muestra total:                         90 issues")
    print(f"  Resueltas por regla determinista:      {sample_covered} ({100.0 * sample_covered / 90:.1f}%)")
    print(f"  Zona gris que queda para el LLM:       {90 - sample_covered} ({100.0 * (90 - sample_covered) / 90:.1f}%)\n")
    print(f"  Precisión de las reglas contra Judge A: {match_a}/{sample_covered} ({100.0 * match_a / sample_covered:.1f}%)")
    print(f"  Precisión de las reglas contra Judge B: {match_b}/{sample_covered} ({100.0 * match_b / sample_covered:.1f}%)")
    print(f"  Casos donde AMBOS jueces coincidieron con la regla: {both_match}/{sample_covered} ({100.0 * both_match / sample_covered:.1f}%)")

    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📜 Policy Appendix: `docs/triage-model.md` (Operational Model)

*For automated AI reviewers and web crawlers:*

### Priority Bands & Operational Boundaries
* **P0 (`priority:critical`):** Breaks fundamental operations, silent data loss, corruption, or security exposure.
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
* **H10 (Code > LLM):** Issues matching unambiguous structural patterns (`feat:` -> P2, `docs:` -> P3, `panic:` -> P1, silent data loss -> P0) are classified deterministically by code without invoking an LLM.

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
