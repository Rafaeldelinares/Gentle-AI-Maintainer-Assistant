# Phase 3 — Architecture

> Status: **pre-approval design.** No production code, no API, no GitHub mutation.
> Implements Phase 3 of the Initial Development Protocol, on top of
> `docs/problem-definition.md` (Phase 2).
>
> The protocol requires that this document **explicitly separate** ten concerns.
> Each is a section below, with its boundary, its inputs and outputs, and its v1
> scope. Separation is a contract: a concern never reaches into another's data.

## Architectural invariants

| # | Invariant |
| --- | --- |
| A1 | **Read-only outward.** Nothing in this architecture mutates GitHub. |
| A2 | **No decision production.** The system emits recommendations with evidence; only a maintainer produces decisions. |
| A3 | **No bare scores.** Every band carries its reasons and citations. |
| A4 | **A priori is inference.** Pass-1 output is never presented as fact. |
| A5 | **Deterministic before semantic.** Everything obtainable without a model is computed without a model. |
| A6 | **Bounded blast radius.** v1 crosses repositories only; it never reconstructs a repository's internal graph. |

---

## 1. Data acquisition

**Boundary.** The only component allowed to touch the network or invoke `gh`.

**Reads.** Issue number, title, body, state, labels, author, timestamps, template
used, comments, cross-references, PR linkage; repository label inventories; issue
templates; CI workflow definitions.

**Writes.** None. Enforced by construction: the adapter exposes no mutating call.

**Mechanism.** `gh` CLI, matching the ecosystem convention verified in Phase 1.
No Go or TypeScript GitHub client exists anywhere in the ecosystem, and none is
introduced.

**Output.** Raw, unclassified records. No interpretation happens here.

**v1 scope.** Full. This is the foundation.

---

## 2. Repository analysis

**Boundary.** Answers "what does this repository consider normal?" — never "is this
issue important?"

**Produces, per repository:**

- **Label profile** — the repository's real labels and their families.
  Needed because `gentle-ai` declares no `labels.yml` and must be discovered live.
- **Template profile** — what the reporter was asked for; drives the *completeness* dimension.
- **Gate profile** — what "approved" means operationally in this repository's CI.
- **Vocabulary map** — how this repository's labels map onto the common vocabulary.

**FACT — why this is a real component, not a formality.** The three repositories
share only the `status:needs-review` → `status:approved` gate. Their type and
priority vocabularies diverge:

| | gentle-ai | engram | gentle-shell |
| --- | --- | --- | --- |
| central label declaration | none | `labels.yml` | live API |
| type labels | `bug`, `enhancement` | `type:*` | `type:*` **and** defaults |
| priority labels | none | 4 bands | `priority:high` only |
| duplicate labels | none | `possible-duplicate` + `resolution:duplicate` | `duplicate` (GitHub default) |

**v1 scope.** Metadata-level only (labels, templates, gates, coupling). **Source
code analysis is a Pass-2 concern and is out of v1.**

---

## 3. Context construction

**Boundary.** Assembles the per-issue context object. Owns no classification logic.

**Inputs.** Raw record (§1) + repository profile (§2) + coupling graph.

**Output.** A single self-contained context record per issue, sufficient for §4–§6
to run without further acquisition. This is the seam that keeps acquisition out of
analysis.

**v1 scope.** Full, and deliberately cheap — scope is bounded by the 1,226 open
issues measured in Phase 1.

---

## 4. Issue analysis

**Boundary.** Characterises one issue in isolation. **Does not look at other issues.**

**Produces the dimensions** defined in `docs/triage-model.md`: issue type, affected
component, scope, impact, severity, urgency, reproducibility, completeness,
dependencies.

**Constraint.** Each dimension is emitted with a value, a confidence, and the
evidence that supports it. A dimension with no evidence is emitted as `unknown` —
never guessed.

**v1 scope.** A-priori dimensions only. Nothing here reads source code.

---

## 5. Relationship detection

**Boundary.** Compares an issue against **other systems** — not against other issues.

**This is the component that produces priority**, because priority is defined as
the implication visible a priori.

**Mechanism** (four deterministic steps plus one inference, from Phase 2 §10):
reference extraction → coupling test → geography test → implication hypothesis.

**Emits** the four patterns of Phase 2 §10, of which only (a) and (b) raise a band.

**v1 scope.** Cross-repository only. **Internal blast radius is deferred to v2** by
maintainer decision. Consequence: v1 needs only the three verified coupling edges,
not a graph reconstruction.

---

## 6. Issue clustering

**Boundary.** Compares issues against **each other**, grouping by root class.

**Status: defined but deferred.** The protocol requires this concern to be
separated; it does not require it in v1.

**Reconciliation obligation.** Three divergent vocabularies already exist in the
ecosystem and must not be joined by a fourth:

| Source | Vocabulary |
| --- | --- |
| `gentle-ai/skills/systemic-issue-triage` | root classes A–E |
| `gentle-ai/skills/issue-root-resolution` | mechanism map + evidence-gated closures |
| `engram/skills/backlog-triage` | 6 dispositions (MERGE / REQUEST CHANGES / CLOSE / NEEDS DESIGN / APPROVE ISSUE / REJECT ISSUE) |

**v1 scope.** Out. Included here so the boundary exists and clustering cannot leak
into §4 or §5.

---

## 7. Memory

**Boundary.** The only component that may persist anything.

**Permitted to store.** Maintainer overrides (a human decision), and optionally
analysis history.

**Must never store.** A band as if it were a fact; anything that would let the
assistant reconstruct a maintainer decision it did not receive.

**STATUS: UNDECIDED.** Engram has no issue entity (`memory_relations` is
observation↔observation only) and cannot be imported as a Go library — integration
is limited to MCP stdio, local HTTP, or CLI. Three candidate representations are
recorded in `docs/problem-definition.md` §8. **This decision blocks Phase 6.**

**v1 scope.** Blocked pending decision. The architecture is designed so that memory
is optional: Pass 1 and Pass 2 produce a complete result without it. What is lost
without memory is override persistence.

---

## 8. Decision support

**Boundary.** Turns dimensions and relations into a **band with reasons**. Produces
no decision.

**Output per issue.** Band, reasons, implication, relocation suggestion, confidence,
evidence, pass marker — the record defined in `docs/problem-definition.md` §5.

**Hard rules.** Cross-system implication alone never promotes a band. A band is
never emitted without at least one reason and one citation. Two similar-looking
independent causes are split, not promoted. Full rules in `docs/triage-model.md`.

---

## 9. Maintainer interaction

**Boundary.** The only surface a human reads. Read-only in v1.

**Must present,** for every issue: the band, the reasons, the evidence, the
confidence, and — visibly separated — what is a-priori inference versus what was
verified.

**Must never present:** a bare number, a decision, or an inference formatted to look
like a fact.

**v1 scope.** Undecided between an interactive surface and a batch Markdown report
(open question Q3). Both are compatible with this boundary.

---

## 10. External integrations

**Boundary.** The complete list of things outside the system the architecture may
touch. Anything not listed is out of bounds.

| Integration | Direction | Mechanism | Constraint |
| --- | --- | --- | --- |
| GitHub | read | `gh` CLI | read-only; no mutation ever |
| Engram | read/write | MCP stdio, local HTTP, or CLI | **never** a library import |
| gentle-ai | read | reuse `skills/` prose as source material | do not duplicate |
| gentle-ai | write-once, later | skill/persona injection pipeline | delivery decision not made |

---

## Data flow

```
   ┌──────────────────────────────────────────────────────────────┐
   │  §1 DATA ACQUISITION                                [read]   │
   │     gh CLI → raw records, labels, templates, workflows       │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  §2 REPOSITORY ANALYSIS                                      │
   │     label profile · template profile · gate profile          │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  §3 CONTEXT CONSTRUCTION                                     │
   │     one self-contained context record per issue              │
   └───────────┬──────────────────────────────────┬───────────────┘
               ▼                                  ▼
   ┌───────────────────────┐        ┌──────────────────────────────┐
   │ §4 ISSUE ANALYSIS     │        │ §5 RELATIONSHIP DETECTION    │
   │  one issue, in        │        │  cross-repo only (v1)        │
   │  isolation            │        │  ← this produces PRIORITY    │
   └───────────┬───────────┘        └───────────────┬──────────────┘
               │                                    │
               └──────────────┬─────────────────────┘
                              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  §8 DECISION SUPPORT                                         │
   │     band + reasons + implication + confidence + evidence     │
   └───────────┬──────────────────────────────────┬───────────────┘
               ▼                                  ▼
   ┌───────────────────────┐        ┌──────────────────────────────┐
   │ §9 MAINTAINER         │        │ §7 MEMORY  (optional, blocked)│
   │    INTERACTION        │        │  overrides + history          │
   └───────────┬───────────┘        └──────────────────────────────┘
               ▼
        MAINTAINER
     accepts · changes · rejects
     ██ only writer in the system ██

   ┌──────────────────────────────────────────────────────────────┐
   │  §6 ISSUE CLUSTERING          — defined, DEFERRED (v1 out)   │
   └──────────────────────────────────────────────────────────────┘
```

---

## Component dependency rules

| Rule | Statement |
| --- | --- |
| R1 | §4 and §5 never call each other. They meet only in §8. |
| R2 | §1 is the only component with network access. |
| R3 | §7 receives only maintainer decisions and may never feed back into §8 as if it were evidence. |
| R4 | §9 may not reformat an inference as a fact. |
| R5 | Removing §7 must not break §1–§6 or §8–§9. |
| R6 | §6, when implemented, may not reuse §5's pattern vocabulary. |

## Open questions carried forward

| # | Question | Blocks |
| --- | --- | --- |
| Q1 | Engram representation of an issue (§7) | Phase 6 |
| Q2 | Product form: binary, skill bundle, or both? | §9, Phase 7 |
| Q3 | Interactive surface or batch report? | §9 |
| Q4 | Which `priority:*` vocabulary is the anchor? (proposal: engram's) | Phase 4 |
