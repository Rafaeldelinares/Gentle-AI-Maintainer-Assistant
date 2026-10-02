# Phase 5 — Decision Model

> Status: **pre-approval design.** No production code, no API, no GitHub mutation.
> Implements Phase 5 of the Initial Development Protocol.
>
> **The governing constraint is explicit in the protocol:**
>
> > *"The assistant must never silently convert a recommendation into a maintainer decision."*
>
> Everything below exists to make that sentence enforceable rather than aspirational.

## 1. The six kinds

| Kind | What it is | Produced by | May change state? |
| --- | --- | --- | --- |
| **Evidence** | a citation to a primary artifact | acquisition | no |
| **Fact** | a claim entailed by cited evidence, reproducible by a third party | analysis | no |
| **Inference** | a conclusion derived from facts by reasoning that could be wrong | analysis, relationship detection | no |
| **Hypothesis** | a testable proposition not yet supported by evidence | relationship detection | no |
| **Recommendation** | a proposal for action, addressed to the maintainer | decision support | no |
| **Maintainer decision** | the human's choice | **the maintainer only** | **yes — only this** |

---

## 2. Evidence vs. fact — the distinction everything rests on

They are not the same thing, and collapsing them is the most common way a system like
this becomes untrustworthy.

- **Evidence is the artifact.** The issue text, a comment, a `file:line`, a label, a CI
  run. Raw, citable, third-party checkable. It asserts nothing on its own.
- **Fact is the claim bound to that evidence.** It requires at least one citation, and a
  third party must be able to follow the citation and reach the same conclusion.

```
   EVIDENCE   "gentle-ai/internal/components/engram/inject.go:42 escribe
               el comando engram mcp en la config del agente"
                        │
                        │  entailed by
                        ▼
   FACT       "gentle-ai configura el MCP de engram"
                        │
                        │  reasoning (could be wrong)
                        ▼
   INFERENCE  "un issue que reporta que la memoria no aparece en
               Windows probablemente tenga su causa en gentle-ai,
               no en engram"
```

**Rule E1.** Evidence without a claim is not a fact. A fact without evidence is not a fact.

---

## 3. The trust ladder

```
   ┌────────────────────────────────────────────────────────────────────┐
   │ EVIDENCE          the artifact                                     │
   │                   raw · citable · third-party checkable            │
   ├────────────────────────────────────────────────────────────────────┤
   │ FACT              claim entailed by the cited evidence             │
   │                   a third party verifies and gets the same answer  │
   ├────────────────────────────────────────────────────────────────────┤
   │ INFERENCE         conclusion derived from facts by reasoning       │
   │                   the reasoning is stated, and may be wrong        │
   ├────────────────────────────────────────────────────────────────────┤
   │ HYPOTHESIS        testable proposition, not yet evidenced          │
   │                   must state how it would be falsified             │
   ├────────────────────────────────────────────────────────────────────┤
   │ RECOMMENDATION    action proposal for the maintainer               │
   │                   never changes state                             │
   ├────────────────────────────────────────────────────────────────────┤
   │ MAINTAINER        the human's choice                               │
   │ DECISION          ██ the only thing that can change state ██       │
   └────────────────────────────────────────────────────────────────────┘
```

**Downward is free. Upward requires evidence.**

---

## 4. Transition rules

| From | To | Who may do it | Condition |
| --- | --- | --- | --- |
| evidence | fact | the system | a claim is entailed by the citation and reproducible |
| fact | inference | the system | the reasoning is stated explicitly |
| inference | fact | the system | **only** when new evidence entails it |
| hypothesis | inference or fact | the system | after the stated test has been run |
| recommendation | decision | **the maintainer only** | explicit, attributed, recorded |
| decision | decision | **the maintainer only** | a new decision supersedes; the system never revises one |

**Rule T1 — repetition is not promotion.** Repeating an inference does not make it a fact.
Confidence rises with evidence, never with insistence.

**Rule T2 — the system never reaches upward on its own.** Every step toward fact requires
an artifact that did not exist before.

---

## 5. The prohibition: what "silent conversion" means

The protocol forbids *silently* converting a recommendation into a maintainer decision.
That is only enforceable if "silently" is defined. It means any of the following:

| # | Silent conversion | Why it is a violation |
| --- | --- | --- |
| S1 | An inference written in the grammar of a fact | the maintainer cannot calibrate trust |
| S2 | An assistant output stored in the same field or store as a decision | the provenance is destroyed |
| S3 | A recommendation treated as settled because nobody objected | silence is not consent |
| S4 | An `unknown` dimension quietly filled by inference | hides the model's ignorance |
| S5 | A decision record without actor, time, or reason | stops being auditable |

**Rule P1 — every state-changing record must carry:** `kind: MAINTAINER DECISION`,
`actor`, `when`, `why`. A record lacking any of these is not a decision and may not be
acted upon.

**Rule P2 — no component may write a decision.** Per `docs/architecture.md` §7, the memory
component stores decisions; it never manufactures them.

---

## 6. Wording contract

Each kind must be grammatically identifiable, so a reader can tell them apart without
reading this document.

| Kind | Required shape |
| --- | --- |
| Fact | *"X is Y"* + citation |
| Inference | *"X appears to be Y because …"* + confidence |
| Hypothesis | *"if … then …"* + how it would be falsified |
| Recommendation | *"consider …"* + explicitly no state change |
| Decision | *"the maintainer decided …"* + actor + when + why |

**Rule W1.** A sentence that fails its required shape is not emitted. In particular, no
inference is ever emitted as a bare assertion.

---

## 7. Where each kind appears

| Architecture section | Emits | Never emits |
| --- | --- | --- |
| §1 Data acquisition | Evidence | anything interpreted |
| §2 Repository analysis | Fact (label profiles, gate profiles) | evaluative claims |
| §4 Issue analysis | Fact, Inference, `unknown` | decisions |
| §5 Relationship detection | Hypothesis, Inference | Fact without evidence |
| §8 Decision support | Recommendation | decisions |
| §9 Maintainer interaction | all kinds, visibly separated | a decision it did not receive |
| §7 Memory | stores Decision only | a band stored as fact |

---

## 8. Which kind is the priority band?

This is the question Phase 5 exists to answer for this project.

```
   THE PRIORITY BAND IS AN INFERENCE. ALWAYS.

     Pass 1 (a priori) : inference with low/medium confidence
     Pass 2 (verified) : inference BOUND to facts — still an inference
     Accepted by the   : the band stays an inference;
     maintainer          the ENDORSEMENT is the decision

   It never becomes a fact, because "important" is an evaluative
   claim about what the maintainer should do first — not an
   observation about the world.

   It never becomes a decision, because only a maintainer decides.
```

**FACT — this is consistent by construction with `docs/triage-model.md`:** consequence C2
states that a band is a priori and therefore always an inference; hard rule H3 makes
confidence mandatory; hard rule H7 gives the maintainer the override.

**Consequence:** an accepted band and a corrected band are both *maintainer decisions*, and
both must be recorded identically (see `docs/triage-model.md` §8). The difference between
"accepted" and "changed" is a field value, not a different kind of record.

---

## 9. Failure modes to watch

| Failure | What it looks like | Damage |
| --- | --- | --- |
| **Inflation** | a hypothesis presented as fact | the maintainer over-trusts a guess |
| **Laundering** | an inference repeated until it reads like fact | repetition is not evidence |
| **Silent promotion** | a recommendation becomes a decision with no human | violates the protocol's core rule |
| **Unknown-filling** | an `unknown` dimension quietly inferred | hides what the model does not know |
| **Decision drift** | the override loses its actor or reason | the record stops being auditable |
| **Attribution loss** | analysis history and decisions share one field | nobody can tell who decided what |

---

## 10. Open questions

| # | Question | Blocks |
| --- | --- | --- |
| Q1 | Where is the decision record persisted? (Engram has no issue entity) | Phase 6 |
| Q2 | Does *accepting* a band without change count as a decision? (proposal: yes, recorded identically) | Phase 6 |
| Q3 | How is a superseded decision represented — new record, or a revision field? | Phase 6 |
| Q4 | Should Pass-1 inferences be persisted at all, or only decisions? (proposal: only decisions, to keep the inference space from becoming a second source of truth) | Phase 3 §7 |
