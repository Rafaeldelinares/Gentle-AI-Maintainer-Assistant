# Phase 2 — Problem Definition

> Status: **pre-approval design.** No production code, no API, no GitHub mutation.
> This document defines *what the assistant is for*. It implements Phase 2 of the
> Initial Development Protocol.
>
> Scope decisions recorded here were made by the maintainer. Everything else is
> derived from the Phase 1 inspection (`docs/phase-1-ecosystem-inspection.md`).

## Provenance

| Target | Repository |
| --- | --- |
| System 1 | `Gentleman-Programming/gentle-ai` — Go, ecosystem configurator |
| System 2 | `Gentleman-Programming/engram` — Go, persistent memory |
| System 3 | `Gentleman-Programming/gentle-shell` — TypeScript, Pi-native harness |

Backlog measured on 2026-10-01. The backlog moves; these are reference magnitudes.

| Repo | Open issues | Open PRs |
| --- | ---: | ---: |
| gentle-ai | 733 | 229 |
| gentle-shell | 422 | 104 |
| engram | 71 | 15 |
| **Total** | **1,226** | **348** |

---

## 1. The problem

The ecosystem has **1,226 open issues across three repositories** and no shared
criterion for deciding what deserves attention first.

**FACT** — Four specific gaps were verified in Phase 1:

| # | Gap | Evidence |
| --- | --- | --- |
| G1 | Triage knowledge exists only as **prose**, in three divergent skills, executed by hand | `gentle-ai/skills/systemic-issue-triage`, `gentle-ai/skills/issue-root-resolution`, `engram/skills/backlog-triage` |
| G2 | The three repos share **only one label**: the `status:needs-review` → `status:approved` gate. Type and priority vocabularies diverge | `.github/labels.yml` (engram), live label API (gentle-shell), templates (gentle-ai) |
| G3 | **Only `engram` has a full priority scale** (`priority:critical|high|medium|low`). `gentle-shell` has only `priority:high`. `gentle-ai` has none | verified label inventories |
| G4 | Cross-system issues are **structurally invisible**: each maintainer reads one repository, but the three systems are coupled in code | coupling graph, §10 |

**FACT** — The systems are genuinely coupled:

```
   gentle-ai     ──installs and wires──►  engram        (internal/components/engram/*)
   gentle-shell  ──installs binary─────►  gentle-ai     (scripts/gentle-ai-installer.mjs)
   gentle-shell  ──detects tools───────►  engram        (hasWritableEngramTool → mem_save)
```

**FACT** — Cross-repository references are abundant in open issues:

| Reported in | Open | mentions gentle-ai | mentions engram | mentions gentle-shell/-pi |
| --- | ---: | ---: | ---: | ---: |
| gentle-ai | 733 | — | 170 | 128 + 255 |
| gentle-shell | 422 | 251 | 37 | — |
| engram | 71 | 5 | — | 1 + 7 |

> **CAVEAT — mention ≠ implication.** These are text matches and therefore an
> **upper bound**. An issue that says "engram" may be about the engram
> *functionality inside gentle-ai*, not the engram *repository*. This is itself
> proof that the assistant cannot be a `grep`.

**Problem statement.** Maintainers of three coupled repositories cannot see which
incoming issues have implications beyond the repository they are reading, and have
no consistent, explainable way to order 1,226 open issues by importance.

---

## 2. What the assistant DOES

1. **Classifies every open issue** of the three systems into an explainable
   priority band, **derived from the implications visible a priori**.
2. **Detects cross-system implication** — whether an issue implies another system
   of the ecosystem — and says which one and with what citation.
3. **Detects misplaced issues** — reported in repository A but landing in system B.
4. **Orders the result** as a queue for the maintainer, never as a verdict.
5. **Separates** fact, evidence, inference and hypothesis in every output.

**Priority is the implication, not a score.** A band is only ever emitted together
with the reasons that produce it. See `docs/triage-model.md`.

The assistant works in **two speeds**:

| Pass | Cost | Input | Output |
| --- | --- | --- | --- |
| **1 — a priori** | low, runs on every issue | title, body, labels, template, references, coupling graph | provisional band, implication hypotheses, confidence |
| **2 — verification** | high, bounded | source code, comments, history, linked issues | confirms or corrects the band |

---

## 3. What the assistant does NOT do

| # | Not a goal | Why |
| --- | --- | --- |
| N1 | **No orchestration.** It does not dispatch tasks to other agents | maintainer decision |
| N2 | **No GitHub writes.** No comment, label, assignment, close, or PR | maintainer decision: read-only |
| N3 | **No maintainer decision.** It never converts a recommendation into a decision | Protocol Phase 5 |
| N4 | **No single score.** Priority is never a bare number | Protocol Phase 4 |
| N5 | **No internal blast radius.** Blocking graphs *within* one repo are out of v1 scope | maintainer decision, deferred to v2 |
| N6 | **No code modification.** It never fixes anything | out of mission |
| N7 | **No re-implementation** of existing ecosystem capabilities | Protocol Architectural Principle |
| N8 | **No autonomous workflow.** No daemon, webhook, or scheduled mutation | Protocol: "Never skip directly from the idea to autonomous GitHub actions" |

---

## 4. What information it requires

**Required (v1):**

- Issue surface: number, title, body, state, labels, author, timestamps, template used.
- Issue comments (needed for evidence — `issue-root-resolution` requires bodies **and** comments).
- Per-repo **label profile** (discovered, never assumed — `gentle-ai` declares no `labels.yml`).
- Per-repo **issue-template profile** (what the reporter was asked for).
- Per-repo **CI gate profile** (what "approved" means operationally).
- The **verified coupling graph** between systems.
- Cross-reference index: `owner/repo#n` references and system mentions.

**Explicitly NOT required in v1:** repository source code. Code is a Pass-2 input.

---

## 5. What information it produces

One structured record per issue:

```
   issue          : owner/repo#number
   band           : P0 | P1 | P2 | P3
   reasons        : >= 1 dimension-backed justification
   implication    : none | suspected | confirmed
                    + which system(s) + citation
   relocation     : none | suggested target repo
   confidence     : high | medium | low
   evidence       : >= 1 concrete citation
   pass           : a-priori | verified
```

Plus a **queue view**: issues ordered by band, with a count per band per repo.

Every field is labelled as FACT / EVIDENCE / INFERENCE / HYPOTHESIS. Nothing is
emitted without at least one reason and one citation.

---

## 6. Where human decisions remain necessary

**Always, and non-negotiably:**

| Decision | Owner |
| --- | --- |
| Accept, change, or reject a band | maintainer |
| Relocate an issue to another repository | maintainer |
| Apply any label, comment, or close | maintainer |
| Decide that two similar issues are one cause | maintainer |
| Any GitHub mutation whatsoever | maintainer |

**A maintainer override always wins and is recorded.** The record is a *maintainer
decision*, and per Protocol Phase 5 it is never silently produced by the assistant.
Without persisting the override, the assistant would re-propose the same band
indefinitely.

---

## 7. How it interacts with GitHub

**Read-only, through the established ecosystem mechanism.**

**FACT** — `gh` CLI is the acquisition convention in all three repositories; no Go
or TypeScript GitHub client exists anywhere in the ecosystem.

| Operation | Allowed in v1 |
| --- | --- |
| List issues, read bodies and comments | yes |
| Read labels and label definitions | yes |
| Read issue templates and CI workflow definitions | yes |
| Read cross-references and PR linkage | yes |
| Create / edit / comment / label / assign / close | **no** |

**Rate limits and authentication are an operational constraint, not a design
decision**, and remain unverified in this environment.

---

## 8. How it could interact with Engram

**STATUS: UNDECIDED — this is the largest open design question.**

**FACT** — Engram has **no issue entity**. `memory_relations` connects
observation↔observation only. There is no table, column or model for "issue #n of
repo X". Engram's addressable fields are `project`, `scope`, `type`, `title`,
`content`, `topic_key`.

**FACT** — Engram cannot be imported as a Go library (all core packages are
`internal/`). Integration is limited to **MCP stdio, local HTTP
(`127.0.0.1:7437`), or CLI subprocess**.

**What Engram would be used for if adopted:**

1. Persisting the **maintainer override** — the record that a human changed a band.
2. Persisting analysis history so a re-run does not re-propose the same thing.

**Candidate representations (no decision made):**

| Option | Shape | Risk |
| --- | --- | --- |
| E1 | `project` = repo, `topic_key` = `issue/<repo>-<n>` | `topic_key` space explodes; one topic per issue |
| E2 | one observation per analysis event; identity inside `title`/`content` | querying needs text parsing |
| E3 | dedicated store owned by the assistant; Engram only for decisions | duplicating storage, against the no-duplication principle |

**This decision blocks Phase 6 (data contracts).**

---

## 9. How it could eventually interact with gentle-ai

Three distinct relationships, which must not be confused:

1. **gentle-ai is a SUBJECT of analysis.** It is one of the three classified systems.
2. **gentle-ai is a reusable SOURCE of capability.** Its `skills/` already contain
   the triage prose (`systemic-issue-triage`, `issue-root-resolution`) that this
   design must reconcile with, not duplicate.
3. **gentle-ai is a candidate DELIVERY CHANNEL.** Its
   `internal/components/skills` and `internal/components/persona` pipelines inject
   skills and personas into the agent runtimes it configures. The assistant's
   prompts (Phase 7) could ship through that pipeline instead of a new mechanism.

**FACT** — `gentle-ai/contracts/` versions JSON Schemas with fixtures. Phase 6
should imitate that shape.

**No delivery decision is made here.**

---

## 10. How cross-repository analysis should work

**Scope decision (maintainer):** v1 covers **cross-repository implication only**.
Blocking graphs *within* a single repository are explicitly deferred to v2.

**v1 mechanism — bounded and cheap**, because the coupling graph is small and
already verified:

```
   STEP 1 · reference extraction      (a priori, deterministic)
     find owner/repo#n references and system name mentions
     in title, body, and comments

   STEP 2 · coupling test            (a priori, deterministic)
     does an edge exist in the verified coupling graph
     between the reported system and the referenced system?

   STEP 3 · geography test           (a priori, deterministic)
     does the issue look like its EFFECT lands in another
     system than the one it is reported in?

   STEP 4 · implication hypothesis   (a priori, INFERENCE)
     "suspected cross-system implication with <system>"
     + citation + confidence: low|medium
```

**Why the mechanism is small:** v1 needs only the **three edges** listed in §1,
not a reconstruction of each repository's internal dependency graph.

**Four implication patterns, and only two of them raise a band**
(full rules in `docs/triage-model.md`):

| Pattern | Raises? |
| --- | --- |
| (a) single cause, multiple system effects | **yes** |
| (b) misplaced report — reported in A, effect in B | **yes** |
| (c) two similar-looking independent causes | **no — must be split** |
| (d) cosmetic replicated across repos | **no** |

**The assistant's highest-value output is not the band. It is the sentence
"this issue is in the wrong repository"** — because that is information no single
maintainer can obtain by reading one repository.

---

## 11. Open questions carried forward

| # | Question | Blocks |
| --- | --- | --- |
| Q1 | How is an issue represented in Engram? (§8) | Phase 6 |
| Q2 | Product form: standalone binary, skill/prompt bundle, or both? | Phase 3 delivery, Phase 7 |
| Q3 | Execution model: interactive, or batch report? | Phase 3 |
| Q4 | Should the corrected Phase 1 document be committed? | housekeeping |
| Q5 | Which of the three `priority:*` vocabularies becomes the anchor? (proposal: engram's four bands) | Phase 4 — provisionally answered |
