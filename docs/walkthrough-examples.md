# End-to-End Walkthrough & Practical Examples

> **How Gentle AI Maintainer Assistant operates on real-world issues.**
>
> This document provides concrete, end-to-end demonstrations of how incoming issues flow through the architecture: from deterministic code filtering to calibrated LLM reasoning, schema validation, and maintainer resolution.

---

## 🧭 The End-to-End Pipeline

```
           [ Incoming GitHub Issue ]
                      │
                      ▼
        ┌───────────────────────────┐
        │  db/rules.py (Pure Code)  │
        └─────────────┬─────────────┘
                      │
         ┌────────────┴────────────┐
         │ (39% of backlog)        │ (61% grey-area)
         ▼                         ▼
   [ Instant P0-P3 ]        ┌───────────────────────────────┐
   Zero cost / 5 ms         │ LLM Pass 1 (A-Priori Analysis)│
   Zero LLM noise           │   - Evaluates 13 dimensions   │
                            │   - Enforces Rule H9 (workaround)│
                            └──────────────┬────────────────┘
                                           │
                                           ▼
                            ┌───────────────────────────────┐
                            │ LLM Pass 2 (Cross-System)     │
                            │   - Implication patterns (a-d)│
                            │   - Asymmetric Escrow proposal│
                            └──────────────┬────────────────┘
                                           │
                                           ▼
                            ┌───────────────────────────────┐
                            │ Maintainer Interactive View   │
                            │   - Separates Facts & Inferences│
                            │   - Human 1-click decisions   │
                            └───────────────────────────────┘
```

---

## 📌 Example 1: Deterministic Fast-Path ("Código mata LLM")

### 1. Ingested Issue
* **Repository:** `gentle-ai`
* **Issue #:** `5166`
* **Title:** `fatal error: runtime panic: nil pointer dereference in session_view`
* **Body:**
  ```text
  When opening terminal session with an empty configuration file, the process crashes:
  panic: runtime error: invalid memory address or nil pointer dereference
  [signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0x12a4b]
  ```
* **Labels:** `["bug"]`

### 2. Processing via `db/rules.py`
The issue is evaluated by the deterministic pre-filter:
1. `prefix` is `bug` and label is `bug` ──► categorized as confirmed defect.
2. Evaluates `RE_P0_SILENT` ──► No silent data corruption text.
3. Evaluates `RE_P1_CRASH` ──► **MATCH**: `panic:` and `SIGSEGV` found.
4. Emits `P1` with rule `rule:hard_crash`.
5. **Execution time:** < 5 milliseconds. **LLM Cost:** $0.00. **Stochastic variance:** 0%.

### 3. Emitted Output Contract (`triage-inference/v1`)
```json
{
  "$schema": "https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/triage-inference.schema.json",
  "contract_version": "v1",
  "issue": {
    "repository": "gentle-ai",
    "issue_number": 5166
  },
  "priority": {
    "band": "P1",
    "confidence": "high",
    "method": "deterministic_rule",
    "rule_name": "rule:hard_crash"
  },
  "dimensions": {
    "issue_type": "bug",
    "affected_component": "session_view",
    "scope": "component",
    "impact": "blocks_use",
    "severity": "unknown",
    "urgency": "now",
    "reproducibility": "unknown",
    "completeness": "complete",
    "blocking_status": "unknown"
  },
  "cross_system": {
    "relation": "none"
  },
  "evidence": [
    {
      "source": "body",
      "citation": "panic: runtime error: invalid memory address or nil pointer dereference"
    }
  ],
  "reasoning": "Deterministic match: issue body contains fatal runtime crash signatures (panic / SIGSEGV)."
}
```

---

## 📌 Example 2: Grey-Area Residual Bug with Workaround (Rule H9)

### 1. Ingested Issue
* **Repository:** `gentle-ai`
* **Issue #:** `712`
* **Title:** `review command fails when target directory path has trailing slash`
* **Body:**
  ```text
  Running 'gentle-ai review inspect --path ./src/' exits with error:
  "Error: unresolvable worktree boundary './src/'"
  
  Note: Removing the trailing slash ('./src') works completely fine as a workaround.
  ```
* **Labels:** `["bug"]`

### 2. Processing via `db/rules.py`
* Not a feature (`feat:`), not a chore (`docs:`), not a hard crash (`panic:`), not silent data loss.
* **Deterministic result:** `None` (Indeterminate).
* **Action:** Routed to **LLM Pass 1** (`prompts/pass-1-issue-analysis.md`).

### 3. LLM Pass 1 Evaluation & Calibrated Rule H9
The LLM evaluates the 13 dimensions:
* `issue_type`: `bug`
* `impact`: `degrades` (fails when trailing slash is supplied).
* `severity`: `unknown` (Enforces Pass 1 honesty — severity is unverified).
* `workaround`: Detected in issue body (`"Removing the trailing slash works completely fine"`).

**Application of Calibrated Operational Rule H9:**
> *Without Rule H9:* A naive model flags this as P1 because a core CLI command failed.
> *With Rule H9:* Because a documented, accessible manual workaround exists, this issue is **strictly demoted to P2** to protect maintainers from alert fatigue.

### 4. Emitted Output Contract (`triage-inference/v1`)
```json
{
  "$schema": "https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/triage-inference.schema.json",
  "contract_version": "v1",
  "issue": {
    "repository": "gentle-ai",
    "issue_number": 712
  },
  "priority": {
    "band": "P2",
    "confidence": "high",
    "method": "llm_judge",
    "model_id": "minimax/MiniMax-M3"
  },
  "dimensions": {
    "issue_type": "bug",
    "affected_component": "cli/review",
    "scope": "component",
    "impact": "degrades",
    "severity": "unknown",
    "urgency": "soon",
    "reproducibility": "unknown",
    "completeness": "complete",
    "blocking_status": "unknown"
  },
  "cross_system": {
    "relation": "none"
  },
  "evidence": [
    {
      "source": "body",
      "citation": "Removing the trailing slash ('./src') works completely fine as a workaround."
    }
  ],
  "reasoning": "While the review inspect command fails when a trailing slash is passed, an immediate and reliable manual workaround exists (omitting the trailing slash). Calibrated Rule H9 requires demoting issues with accessible workarounds from P1 to P2."
}
```

---

## 📌 Example 3: Cross-System Implication & Asymmetric Escrow

### 1. Ingested Issue
* **Repository:** `gentle-shell` (formerly `gentle-pi`)
* **Issue #:** `142`
* **Title:** `agent memory retrieval fails with SQLite FTS5 syntax error`
* **Body:**
  ```text
  When the session triggers mem_search with special characters like 'foo/bar', 
  the memory provider returns:
  {"error": "fts5: syntax error near '/'"}
  This breaks conversation context hydration.
  ```

### 2. Processing via LLM Pass 2 (`prompts/pass-2-cross-system-correlation.md`)
1. **Coupling Edge Check:** `gentle-shell` invokes `engram` via IPC/MCP for persistent memory storage.
2. **Geographical Check:** The issue is reported in `gentle-shell`, but the failing component is `internal/store/fts.go` inside `engram`.
3. **Pattern Classification:** **Pattern (b) - Misplaced Report** (reported in repo A, root cause in repo B).
4. **Relocation & Escrow Recommendation:**
   * Do NOT close the issue in `gentle-shell` (Zero Issue Loss).
   * Put issue into **Asymmetric Escrow ("Hogar + Vista")**:
     * Home: `gentle-shell` (retains custody until claimed).
     * Target: `engram` (generates notification for engram maintainers).

### 3. Emitted Output Contract (`triage-inference/v1`)
```json
{
  "contract_version": "v1",
  "issue": {
    "repository": "gentle-shell",
    "issue_number": 142
  },
  "priority": {
    "band": "P1",
    "confidence": "high",
    "method": "llm_judge"
  },
  "cross_system": {
    "relation": "misplaced",
    "target_repository": "engram",
    "pattern": "pattern_b_misplaced",
    "escrow_recommended": true
  },
  "reasoning": "Pattern (b): The reporter experiences context failure in gentle-shell, but the underlying defect is SQLite FTS5 query token sanitization inside engram. Recommended for Asymmetric Escrow to notify engram maintainers without losing track of the issue in gentle-shell."
}
```

---

## 📌 Example 4: The Maintainer Dashboard Experience

When maintainers review triaged issues, they see a concise Markdown/TUI view separating verifiable facts from inferences:

```markdown
┌──────────────────────────────────────────────────────────────────────────┐
│ ISSUE: gentle-ai#712                                                     │
│ TITLE: review command fails when target directory path has trailing slash│
├──────────────────────────────────────────────────────────────────────────┤
│ 📋 HECHOS VERIFICABLES (Datos Objetivos)                                 │
│ • Autor: @contributor                                                    │
│ • Estado: open | Labels: [bug]                                           │
│ • Cita Textual: "Removing the trailing slash works completely fine"      │
├──────────────────────────────────────────────────────────────────────────┤
│ 🤖 INFERENCIA DEL ASISTENTE                                              │
│ • Banda Recomendada: [ P2 ] (Prioridad Media)                            │
│ • Confianza: ALTA (95%)                                                  │
│ • Justificación: Aplica Regla H9. Aunque la CLI falla al recibir '/',    │
│   existe un workaround manual inmediato y documentado.                   │
│ • Cross-System: Ninguno (confinado a gentle-ai)                          │
├──────────────────────────────────────────────────────────────────────────┤
│ ⚖️ ACCIÓN DEL MAINTAINER:                                                │
│   [A] Aceptar Recomendación (Registra inferencia como P2)                │
│   [O] Override Manual (Promover a P1 o P3 con motivo)                    │
│   [R] Reubicar / Iniciar Escrow                                          │
│   [D] Diferir / Solicitar más información                                │
└──────────────────────────────────────────────────────────────────────────┘
```

When the maintainer presses **`[A]` (Aceptar)**, an authoritative `maintainer-decision` record is created:
```json
{
  "$schema": "https://raw.githubusercontent.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant/master/schemas/maintainer-decision.schema.json",
  "contract_version": "v1",
  "issue": {
    "repository": "gentle-ai",
    "issue_number": 712
  },
  "action": "accept",
  "decided_band": "P2",
  "decided_cross": "none",
  "actor": "lead-maintainer",
  "timestamp": "2026-10-02T10:15:00Z",
  "notes": "Verified workaround. Scheduled for next CLI minor release."
}
```

---

## 💡 Summary of Value for Reviewers

1. **Deterministic efficiency:** 39% of all ecosystem issues never touch an LLM.
2. **Honesty by design:** The system never fabricates reproducibility or severity a-priori.
3. **No alert fatigue:** Rule H9 keeps P1 clean, meaningful, and actionable.
4. **Zero issue loss:** Misplaced issues are tracked through asymmetric escrow rather than disappearing between repositories.
