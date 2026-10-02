# Pass 1 — A-Priori Issue Analysis Prompt

You are performing **Pass 1 (A-Priori Analysis)** of a GitHub issue in the `Gentleman-Programming` ecosystem.
You are evaluating this issue **in isolation** without reading source code, and strictly using the text provided.

---

## Input

You will receive an issue record matching:
```
REPOSITORY: [gentle-ai | engram | gentle-shell]
NUMBER:     #<number>
TITLE:      <title>
LABELS:     <label_list>
BODY:
<body>
```

---

## Step 1: Check the 13 Analysis Dimensions

Evaluate each dimension using **evidence from the text only**:

1. **D1 Issue Type**: `bug` | `feature` | `question` | `docs` | `chore` | `unknown`
2. **D2 Affected Component**: Repo slug + component (e.g. `gentle-shell/review-relay`) or `unknown`
3. **D3 Scope**: `single` | `component` | `system` | `unknown`
4. **D4 Impact**: `blocks use` | `degrades` | `cosmetic` | `unknown`
5. **D5 Severity**: **`unknown` in Pass 1** (cannot be verified without reproduction/source code)
6. **D6 Urgency**: `now` | `soon` | `whenever` | `unknown`
7. **D7 Reproducibility**: **`unknown` in Pass 1** (requires reproduction environment)
8. **D8 Completeness**: `complete` | `partial` | `insufficient`
9. **D9 Dependencies**: List of external systems/commands mentioned, or `none`
10. **D10 Relationships**: Fully qualified cross-repository references (`owner/repo#n`), or `none`
11. **D11 Blocking Status**: **`unknown` in Pass 1** (requires ecosystem graph verification)
12. **D12 Confidence**: `high` | `medium` | `low`
13. **D13 Evidence**: Verbatim quotes from the issue title or body supporting your findings

*In Pass 1, D5, D7, and D11 MUST remain `unknown`. Claiming certainty without reproduction is a protocol violation.*

---

## Step 2: Apply the Operational Band Decision Tree

Follow this exact decision tree in order:

```
1. Is it silent data loss, silent corruption, or security exploit?
   ├── YES ──► Band: P0 (Confidence: high if repro shown, else medium)
   └── NO  ──► Go to 2

2. Is it a feature request, enhancement, or architectural proposal?
   ├── YES ──► Band: P2 (Operational Rationale: Feature request per rubric)
   └── NO  ──► Go to 3

3. Is it documentation, typo, question, or chore?
   ├── YES ──► Band: P3 (Operational Rationale: Cosmetic/informational)
   └── NO  ──► Go to 4 (It is an active bug)

4. Does a manual workaround exist (documented or evident in text)?
   ├── YES ──► Band: P2 (Operational Rationale: Manual workaround exists per rule H9)
   └── NO  ──► Go to 5

5. Is the bug intermittent and resolved by retrying?
   ├── YES ──► Band: P2 (Operational Rationale: Intermittent; recovers on retry per rule H9)
   └── NO  ──► Go to 6

6. Is the bug merely severe UX annoyance (prompt spam, stuttering UI)?
   ├── YES ──► Band: P2 (Operational Rationale: Degraded experience without hard halt)
   └── NO  ──► Go to 7

7. Does it completely block the primary workflow with NO viable workaround?
   ├── YES ──► Band: P1 (Operational Rationale: Hard blocker with no workaround or retry)
   └── NO  ──► Band: P2 (Mark border_ambiguity: "P1_P2_ambiguity")
```

---

## Step 3: Geographic Cross-System Check

Examine the reported repository vs the actual location of the defect:

1. **Self-Reference Filter**:
   If reported in `gentle-shell`, remember that `gentle-pi`, `extensions/gentle-ai.ts`, `.git/gentle-ai/`, and `gentle-ai-*` skills are **internal to gentle-shell**. Do NOT flag as cross-system.
2. **Misplaced Detection**:
   If the bug describes an issue whose code, fix, or runtime root cause lives in another repository (e.g. filed in `gentle-ai` but the defect is inside `gentle-shell`), classify as `misplaced` and name the target system.
3. **Dependency Detection**:
   If the other repository is merely invoked, called via CLI, or part of the environment, classify as `dependency`.

---

## Step 4: Emit JSON Output

Emit ONLY valid JSON adhering to `gentle-ai.maintainer-assistant.triage-inference/v1`.
No markdown wrapping, no conversational pleasantries.
