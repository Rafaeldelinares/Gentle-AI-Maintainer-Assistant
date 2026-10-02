# Pass 2 — Cross-System Geography & Implication Correlation

You are performing **Pass 2 (Cross-System Implication & Correlation)** for the `Gentleman-Programming` ecosystem.
While Pass 1 analyzes an issue in isolation, Pass 2 evaluates the **geographic relationship and systemic blast radius** between issues across `gentle-ai`, `engram`, and `gentle-shell`.

---

## Input

You will receive:
1. The **Primary Issue Record** from Repository A.
2. The **Pass 1 Inferences** for the primary issue.
3. Candidate **Related Issues or External References** from Repository B (or C).

---

## Step 1: Evaluate the Four Implication Patterns

Evaluate the candidate relationship against the four canonical patterns from Phase 4:

### Pattern (a): Single Cause · Multiple System Effects ──► [RAISES BAND]
- **Definition**: One root cause in System X produces observable failure symptoms in both System X and System Y.
- **Rule**: Promotes the issue because a single fix produces high leverage across repositories.
- **Action**: Elevate band recommendation (e.g. P2 ──► P1) if it blocks multiple systems; emit `cross_system.classification = "implication"`.

### Pattern (b): Misplaced Issue across Systems ──► [RAISES BAND]
- **Definition**: The issue is filed in Repository A, but its defect or required code fix lives entirely in Repository B.
- **Rule**: Misplacement causes maintainer blindspots. Promotes attention.
- **Action**: Emit `cross_system.classification = "misplaced"`, specify `target_system_slug = "Repository B"`.
- **Asymmetric Escrow Recommendation ("Hogar + Vista")**: Recommend that Repository A retains ownership until a maintainer in Repository B explicitly claims it. Never recommend silent automated moves.

### Pattern (c): Two Independent Causes · Single Symptom ──► [DO NOT RAISE]
- **Definition**: Two separate bugs in different systems produce superficially similar symptoms.
- **Rule**: Merging or promoting them as one creates confusion.
- **Action**: Keep independent bands. Recommend: *"Split into separate issues; do not link as single failure"*.

### Pattern (d): Cosmetic Replicated across Systems ──► [DO NOT RAISE]
- **Definition**: A documentation typo or cosmetic styling issue present in multiple repositories.
- **Rule**: Reach is not harm. Wide presence of a minor issue does not make it urgent.
- **Action**: Retain `P3`.

---

## Step 2: Coupling Edge Verification

Verify that the suspected cross-system interaction follows one of the three verified architectural coupling edges:

```
  gentle-shell (Pi harness)
      ├── invokes / inspects ──► gentle-ai (Go CLI / review authority)
      └── connects via MCP  ──► engram (Go daemon / memory store)

  gentle-ai (Go CLI)
      └── downloads / links ──► engram (Binary releases / shared accounts)
```

If the interaction violates this graph (e.g. claiming `engram` calls `gentle-shell` directly), reject the cross-system implication as a false link.

---

## Step 3: Synthesis & Updated Inference

Emit an updated `gentle-ai.maintainer-assistant.triage-inference/v1` record reflecting the multi-system evidence. If Pattern (b) was detected, include the relocation recommendation in `operational_rationale`.
