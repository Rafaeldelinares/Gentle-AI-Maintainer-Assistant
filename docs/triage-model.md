# Phase 4 — Triage Model

> Status: **pre-approval design.** No production code, no API, no GitHub mutation.
> Implements Phase 4 of the Initial Development Protocol.
>
> **The governing constraint is explicit in the protocol:**
>
> > *"Do NOT reduce triage to a single score.*
> > *Priority must remain contextual and explainable."*
>
> In this model **priority is not computed from the dimensions — priority IS the
> implication, expressed with the dimensions as its reasons.**

## 1. Priority, defined

**Maintainer's definition (authoritative):**

> Priority is the possible implication that can be seen **a priori**, and it is
> modifiable by maintainers.

Three consequences follow directly, and they shape everything below:

| # | Consequence |
| --- | --- |
| C1 | Priority is **derived from implication**, not from a weighted sum. The motor is implication detection, not scoring. |
| C2 | Priority is **a priori** — therefore it is **INFERENCE**, never FACT. It carries a confidence by construction. |
| C3 | Priority is **overridable**. A maintainer override always wins and must be recorded, or the model is not stable. |

**C3 is a hard requirement on the architecture:** without persisted overrides the
model re-proposes the same band forever. See `docs/architecture.md` §7.

---

## 2. The dimensions

Thirteen dimensions, as required by the protocol. For each: what it is, whether it
is observable in Pass 1 (a priori) or Pass 2 (verification), and its values.

| # | Dimension | What it is | Pass | Values |
| --- | --- | --- | --- | --- |
| D1 | **issue type** | what kind of request this is | 1 | bug · feature · question · docs · chore · unknown |
| D2 | **affected component** | which part of which system | 1–2 | `owner/repo` + component, or `unknown` |
| D3 | **scope** | how wide the effect is inside its system | 1–2 | single · component · system · unknown |
| D4 | **impact** | what stops working, and for whom | 1–2 | blocks use · degrades · cosmetic · unknown |
| D5 | **severity** | how bad it is when it happens | 2 | high · medium · low · unknown |
| D6 | **urgency** | how soon it must be addressed | 1–2 | now · soon · whenever · unknown |
| D7 | **reproducibility** | can the reporter's case be reproduced | 2 | reproducible · partial · not-reproducible · unknown |
| D8 | **completeness** | does the report contain what the template asked for | 1 | complete · partial · insufficient |
| D9 | **dependencies** | what this needs, and what needs this | 1–2 | list of references, or `none` |
| D10 | **relationships** | links to other issues or other systems | 1 | list of `owner/repo#n`, or `none` |
| D11 | **blocking status** | whether it blocks other work | 2 | blocks · blocked-by · free · unknown |
| D12 | **confidence** | how sure the assistant is | 1–2 | high · medium · low |
| D13 | **evidence** | the citation that supports the claim | 1–2 | issue text · comment · file:line · label |

**FACT — the Pass column is the honesty mechanism.** D5 (severity), D7
(reproducibility) and D11 (blocking status) are **not** obtainable a priori. In
Pass 1 they are `unknown`. Any model that guesses them is lying about its evidence.

---

## 3. The four implication patterns

Priority is driven by implication. But **implication alone does not raise a band.**

```
   ┌────────────────────────────────────────────────────────────────────┐
   │ (a) SINGLE CAUSE · MULTIPLE SYSTEM EFFECTS              ⬆ RAISES   │
   │     one defect in system X produces symptoms in X and in Y          │
   │     → one fix, several symptoms. high leverage                      │
   │     a-priori detectable? NO — (a) and (c) look identical in Pass 1  │
   ├────────────────────────────────────────────────────────────────────┤
   │ (b) MISPLACED REPORT                                    ⬆ RAISES   │
   │     reported in repository A, but the effect lands in system B      │
   │     → the owner of B is not looking at it                           │
   │     a-priori detectable? YES — it is purely geographic              │
   ├────────────────────────────────────────────────────────────────────┤
   │ (c) TWO INDEPENDENT CAUSES THAT LOOK ALIKE              ⬇ NO       │
   │     same symptom in two systems, unrelated causes                   │
   │     → these are TWO issues. SPLIT them. do not promote.             │
   ├────────────────────────────────────────────────────────────────────┤
   │ (d) COSMETIC REPLICATED ACROSS SYSTEMS                  ⬇ NO       │
   │     a documentation typo present in two repositories                │
   │     → reach is not harm                                             │
   └────────────────────────────────────────────────────────────────────┘
```

**FACT — why (b) is the centrepiece of v1.** It is the only pattern detectable a
priori with reasonable confidence, because it depends on *where the issue is
reported* versus *where its effect lands* — geography, not causality. It is also
the pattern whose information no single maintainer can obtain by reading one
repository. The assistant's most valuable output is therefore not a band but the
sentence:

> **"this issue is in the wrong repository."**

---

## 4. The bands

Four bands, anchored to the vocabulary that already exists in the ecosystem.
**`engram` defines all four** (`priority:critical|high|medium|low`);
`gentle-shell` defines only `priority:high`; `gentle-ai` defines none.

| Band | Anchor label | Meaning | Operational Boundary |
| --- | --- | --- | --- |
| **P0** | `priority:critical` | breaks something fundamental, silent data loss, corruption, or security exposure | Verified data loss/corruption or security breach. When the deterministic engine matches a silent-data-loss pattern, it emits strictly **`candidato P0, requiere revisión humana`** (candidate P0 requiring human review), never a final P0. |
| **P1** | `priority:high` | serious, hard blocker in production **with NO workaround and NO retry recovery** | Workflow is dead-ended. User cannot proceed by manual steps or retries. |
| **P2** | `priority:medium` | degrades functionality, **OR a workaround exists, OR intermittent recovery via retry, OR feature request** | Annoyance, UX spam, or manual config edit exists to unblock. All feature requests. |
| **P3** | `priority:low` | cosmetic, documentation, question, chore, minor discussion | Purely informational or non-actionable as reported. |

**The band is a recommendation about where the maintainer should look first.** It is
never applied as a label by the assistant.

---

## 5. Band derivation rules

A band is produced by the **first** rule that matches, top to bottom.

```
   P0 ─┬─ pattern (a) AND the crossed effect breaks an install/upgrade path
       ├─ data loss, corruption, or security exposure
       └─ regression with no workaround that blocks a release gate

   P1 ─┬─ pattern (b): reported in one repository, effect in another system
       ├─ pattern (a) with a non-destructive crossed effect
       ├─ D5 severity = high  AND  no workaround
       └─ D11 blocking status = blocks

   P2 ─┬─ D4 impact = degrades  AND  a workaround exists
       └─ D8 completeness = insufficient  (unactionable as reported)

   P3 ─┬─ D1 type = docs | question
       └─ no implication pattern, no blocking status
```

### Hard rules

| # | Rule |
| --- | --- |
| H1 | **Cross-system implication alone never promotes a band.** Only patterns (a) and (b) do. |
| H2 | A band is **never** emitted without at least one reason and at least one citation. |
| H3 | A band is **always** inference. Confidence is mandatory. Low confidence is a valid, expected outcome. |
| H4 | Pattern (c) must be **split into separate issues**, never promoted as one. |
| H5 | Pattern (d) never promotes. Reach is not harm. |
| H6 | A missing dimension is `unknown`. It is never inferred silently to complete a band. |
| H7 | A **maintainer override always wins** and is recorded as a decision. |
| H8 | Pass-1 bands are **provisional**. Pass 2 may correct them, and the correction is recorded. |
| H9 | **Workaround & Retry rule (P1 vs P2):** If a documented or accessible manual workaround exists, or if the failure is intermittent and recovers upon retry, the issue **MUST** be classified as P2, never P1. P1 is strictly reserved for dead-ends with no viable escape hatch. |
| H10 | **Deterministic Pre-Filter Rule (Code > LLM):** Issues matching unambiguous structural patterns (`feat:` prefix -> P2, `docs:`/`chore:` -> P3, `panic:`/`SIGSEGV` -> P1, silent corruption -> **`candidato P0, requiere revisión humana`**) are classified deterministically by code without invoking an LLM. A deterministic P0 is always a candidate requiring human review, never a final decision. Negations (`no/without/not ... data loss`, `is not a deadlock`) and fix descriptions never fire, and `deadlock` requires process/thread context. |

---

## 6. Why not a single score

Recorded because the protocol forbids it and the reason must survive future
revision.

```
   TWO REAL ISSUES, BOTH "P1" UNDER A SCORE:

     gentle-ai#A   installer breaks on Windows
                   severity high · urgency high · no workaround
     gentle-ai#B   a doc typo, duplicated in engram
                   severity low  · urgency low  · cosmetic

   WITH A SINGLE SCORE:            WITH A BAND + REASONS:
     8.4  →  P1                        A = P1  because it breaks the
     2.1  →  P3                                install path with no
                                               workaround
     The maintainer cannot             B = P3  because it is cosmetic,
     argue with 8.4.                           and reach is not harm

   Costs of the score:                The maintainer can argue with
     - unauditable (where is 8.4 from?) the reason — and the reason
     - unstable (change a weight,        survives review.
       the whole backbone reshuffles)
     - hides the causation the
       protocol requires be separated
```

---

## 7. Output record

Every classified issue is emitted as:

```
   issue       : owner/repo#number
   band        : P0 | P1 | P2 | P3
   reasons     : >= 1, each naming the dimension(s) that support it
   implication : none | suspected | confirmed
                 + target system(s)
                 + pattern: (a) | (b) | (c) | (d)
   relocation  : none | suggested target repository
   confidence  : high | medium | low
   evidence    : >= 1 concrete citation
   pass        : a-priori | verified
   unknown     : explicit list of dimensions that could not be determined
```

The `unknown` list is mandatory and non-empty in Pass 1 for D5, D7 and D11. It is
the model's declaration of what it does not know.

---

## 8. Override record

When a maintainer changes a band, the override is recorded as a **maintainer
decision** — never as an assistant output.

```
   issue        : owner/repo#number
   proposed     : band + reason + confidence   (the assistant's output)
   decided      : band                          (the maintainer's choice)
   actor        : who decided
   when         : timestamp
   why          : the maintainer's reason, free text
   kind         : MAINTAINER DECISION
```

Persistence of this record is blocked by the Engram representation decision
(`docs/problem-definition.md` §8). Without it the model cannot respect C3.

---

## 9. Open questions

| # | Question |
| --- | --- |
| Q1 | Is `engram`'s four-band `priority:*` vocabulary accepted as the common anchor? |
| Q2 | Should Pass 2 (verification) run on every issue, or only on P0/P1 and suspected relocations? |
| Q3 | How is pattern (c) — two independent causes — presented to the maintainer for splitting? |
| Q4 | Where are overrides persisted? (blocks C3) |
