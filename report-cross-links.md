# Module C — Cross-Repository References

> **Read-only module.** Looks for cross-repository references that are **not** in the structured `cross_refs` field, so a maintainer can decide whether a link belongs there.
>
> **It proposes; it never links.** Nothing is written to `cross_refs`, and every entry is `veredicto_humano: pendiente`.
>
> Reproduce with `python3 modules/cross_repo.py`.

## Summary

| Metric | Value |
| --- | --- |
| Issues with a structured `cross_refs` entry | 26 |
| Explicit references to another repo (`repo#N`) | 48 |
| — resolving to an open issue in the snapshot | 15 |
| — not resolving (closed, renamed, or a typo) | 33 |
| Issues carrying at least one explicit reference | 33 |
| `owner/repo` reference without a number | 81 |
| Bare repository-name mention, no `cross_refs` | 914 |

### Explicit references by target repository

| Target repository | References |
| --- | --- |
| `gentle-ai` | 12 |
| `gentle-shell` | 2 |
| `engram` | 1 |

### Reference direction

| From -> To | References |
| --- | --- |
| `gentle-shell` -> `gentle-ai` | 10 |
| `gentle-ai` -> `gentle-shell` | 2 |
| `engram` -> `gentle-ai` | 2 |
| `gentle-ai` -> `engram` | 1 |

## Proposed links (explicit reference, target is open)

Each row cites the exact reference. The maintainer decides whether to record it in `cross_refs`.

- **gentle-ai#5156** -> **gentle-shell#1160**
  - Source: https://github.com/Gentleman-Programming/gentle-ai/issues/5156 — feat(odd): offer task close as an optional session boundary with a short printed brief
  - Target: https://github.com/Gentleman-Programming/gentle-shell/issues/1160 — feat(odd): derive a feature index so `odd/tasks/` never has to be read in full
  - Reference: team-reference — "udget shipped in #5147. This builds on Gentleman-Programming/gentle-shell#1160, which proposes a derived, deterministi"
  - veredicto_humano: pendiente

- **gentle-ai#5119** -> **gentle-shell#1540**
  - Source: https://github.com/Gentleman-Programming/gentle-ai/issues/5119 — bug(communitytool): shell-centric CodeGraph guidance injected into bash-less Pi agents causes retry 
  - Target: https://github.com/Gentleman-Programming/gentle-shell/issues/1540 — bug(agents): shell-centric CodeGraph guidance block injected into bash-less agents causes retry loop
  - Reference: team-reference — "l Context Cross-reference: Reported in Gentleman-Programming/gentle-shell#1540 by @matheo. A fully verified fix with r"
  - veredicto_humano: pendiente

- **gentle-ai#1734** -> **engram#327**
  - Source: https://github.com/Gentleman-Programming/gentle-ai/issues/1734 — feat(cli): add `gentle-ai account link` to connect a machine to an existing Engram Cloud account
  - Target: https://github.com/Gentleman-Programming/engram/issues/327 — Engram Cloud | Command to sync mutations
  - Reference: team-reference — "d to sync mutations", closed, moved to `Gentleman-Programming/engram#327`) confirms that manual `engram sync --c"
  - veredicto_humano: pendiente

- **engram#1501** -> **gentle-ai#1019**
  - Source: https://github.com/Gentleman-Programming/engram/issues/1501 — feat(ci): recognize cross-repository issue references in PR validation
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/1019 — bug(claude-code): Engram MCP connection gets SIGINT'd seconds after connecting and never reconnects
  - Reference: team-reference — "hat was already approved and claimed in Gentleman-Programming/gentle-ai#1019. The org already tracks twin issues acr"
  - veredicto_humano: pendiente

- **engram#1499** -> **gentle-ai#1019**
  - Source: https://github.com/Gentleman-Programming/engram/issues/1499 — feat(mcplogs): surviving-witness classifier for Claude Code MCP logs
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/1019 — bug(claude-code): Engram MCP connection gets SIGINT'd seconds after connecting and never reconnects
  - Reference: team-reference — "ever-reconnect failure class tracked in Gentleman-Programming/gentle-ai#1019 (Engram's MCP connection gets SIGINT'd"
  - veredicto_humano: pendiente

- **gentle-shell#1085** -> **gentle-ai#1863**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/1085 — bug(skills): packaged gentle-ai skill contradicts the injected orchestrator contract
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/1863 — feat(workflow): establish canonical workflow doctrine and exact embedded mirror
  - Reference: issue-reference — "llowing the integrity-mirror pattern of gentle-ai#1863. Related dedup direction: #259. ### St"
  - veredicto_humano: pendiente

- **gentle-shell#1084** -> **gentle-ai#1863**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/1084 — feat(skills): single-source the skills shipped by both gentle-ai and gentle-pi
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/1863 — feat(workflow): establish canonical workflow doctrine and exact embedded mirror
  - Reference: issue-reference — "plus integrity-test pattern accepted in gentle-ai#1863 across the repository boundary. ### Al"
  - veredicto_humano: pendiente

- **gentle-shell#998** -> **gentle-ai#4223**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/998 — bug(review): closure decoder rejects targeted validator evidence
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/4223 — fix(review): publish targeted validator evidence in last-event closure schema
  - Reference: team-reference — "Gentle Pi 2.6.2 / Gentle AI 2.8.2 pair. Gentleman-Programming/gentle-ai#4223 and Gentleman-Programming/gentle-ai#427"
  - veredicto_humano: pendiente

- **gentle-shell#741** -> **gentle-ai#4355**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/741 — bug(review): correction-plan captures always rejected — binding target (frozen authority) compared a
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/4355 — bug(review): provider refuses every capture including verbatim forecasts seconds after STATUS; two l
  - Reference: issue-reference — "nces: symptom family likely shared with gentle-ai#4355 (lineages stuck in `correction_required"
  - veredicto_humano: pendiente

- **gentle-shell#741** -> **gentle-ai#4370**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/741 — bug(review): correction-plan captures always rejected — binding target (frozen authority) compared a
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/4370 — bug(review): intended-untracked selection rejects exact binding as schema-incompatible
  - Reference: issue-reference — "hit the same day is already tracked as gentle-ai#4370. ### Steps to reproduce 1. Negotiated"
  - veredicto_humano: pendiente

- **gentle-shell#582** -> **gentle-ai#2029**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/582 — review: follow-up field report — 15-commit sliced series through the Pi host
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/2029 — fix(review): relay admission feedback and require canonical proof paths
  - Reference: issue-reference — "r session reports and route findings; - gentle-ai#2029, #3922, #4019, #4074, and #4082 — provi"
  - veredicto_humano: pendiente

- **gentle-shell#577** -> **gentle-ai#4031**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/577 — review: session report #3 to #551 — 7-batch committed-range walk via the direct CLI route: 7/7 appro
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/4031 — review and issues: negotiated v2 lifecycle on Pi — 3 escalation rounds, 12 sequential lens runs, opa
  - Reference: issue-reference — "hat worked (counter-evidence for #551 / gentle-ai#4031) - **7/7 lineages approved + acknowled"
  - veredicto_humano: pendiente

- **gentle-shell#551** -> **gentle-ai#4031**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/551 — review: full negotiated v2 session from Pi — 3 escalation rounds × 4 sequential lenses, ~40 min per 
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/4031 — review and issues: negotiated v2 lifecycle on Pi — 3 escalation rounds, 12 sequential lens runs, opa
  - Reference: team-reference — "gentle-ai-side defects are reported in Gentleman-Programming/gentle-ai#4031; this is the gentle-pi-side account of"
  - veredicto_humano: pendiente

- **gentle-shell#381** -> **gentle-ai#3522**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/381 — feat(models): expose a machine-readable routing contract
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/3522 — feat(tui): configure Pi agent models from gentle-ai
  - Reference: team-reference — "y semantics. This remains required by [Gentleman-Programming/gentle-ai#3522](https://github.com/Gentleman-Programmi"
  - veredicto_humano: pendiente

- **gentle-shell#373** -> **gentle-ai#1291**
  - Source: https://github.com/Gentleman-Programming/gentle-shell/issues/373 — fix(skill-registry): degrade truthfully when the project registry is unwritable
  - Target: https://github.com/Gentleman-Programming/gentle-ai/issues/1291 — fix: EACCES on Android external storage during skill registry refresh
  - Reference: team-reference — "implementation vehicle after rework. - Gentleman-Programming/gentle-ai#1291 tracks a separate provider-side Go skil"
  - veredicto_humano: pendiente

## Explicit references that do not resolve (first 20)

The target number is not an open issue in the snapshot: it may be closed, renamed, or a typo. Recorded but not proposed.

- **gentle-ai#4712** -> `engram#885` — https://github.com/Gentleman-Programming/gentle-ai/issues/4712
  - Reference: "or issues, none a conforming duplicate: Gentleman-Programming/engram#885 (gentle-ai RC/prerelease install suppor"
  - veredicto_humano: pendiente
- **gentle-ai#4712** -> `engram#498` — https://github.com/Gentleman-Programming/gentle-ai/issues/4712
  - Reference: "ntle-ai RC/prerelease install support), Gentleman-Programming/engram#498/#461/#143 (engram setup writing version"
  - veredicto_humano: pendiente
- **gentle-ai#4308** -> `engram#1039` — https://github.com/Gentleman-Programming/gentle-ai/issues/4308
  - Reference: "didate. Field evidence (real review on Gentleman-Programming/engram#1039, gentle-ai 2.6.0, reviewer lens `review"
  - veredicto_humano: pendiente
- **gentle-ai#1903** -> `engram#675` — https://github.com/Gentleman-Programming/gentle-ai/issues/1903
  - Reference: "dered - **Wait for `mem_list_projects` (engram#675)**: not needed — `mem_current_project`"
  - veredicto_humano: pendiente
- **engram#1533** -> `gentle-shell#1485` — https://github.com/Gentleman-Programming/engram/issues/1533
  - Reference: "ge. - **Proposed fix** (same pattern as gentle-shell#1485 / #1497): append the protocol idempoten"
  - veredicto_humano: pendiente
- **engram#1533** -> `gentle-shell#1528` — https://github.com/Gentleman-Programming/engram/issues/1533
  - Reference: "ated, same symptom from other layers:** Gentleman-Programming/gentle-shell#1528, elidickinson/pi-claude-bridge#144. Nei"
  - veredicto_humano: pendiente
- **engram#1501** -> `gentle-ai#1770` — https://github.com/Gentleman-Programming/engram/issues/1501
  - Reference: "ed. Prior art in the same check family: gentle-ai#1770 fixed a different parsing defect (HTML"
  - veredicto_humano: pendiente
- **gentle-shell#1564** -> `engram#853` — https://github.com/Gentleman-Programming/gentle-shell/issues/1564
  - Reference: "host. This is the same defect class as Gentleman-Programming/engram#853, which was fixed for `gentle-engram`'s"
  - veredicto_humano: pendiente
- **gentle-shell#1460** -> `gentle-ai#333` — https://github.com/Gentleman-Programming/gentle-shell/issues/1460
  - Reference: "- Relacionadas (otro repo, otro eje): `Gentleman-Programming/gentle-ai#333` (gobernanza de longitud de respuesta —"
  - veredicto_humano: pendiente
- **gentle-shell#1460** -> `gentle-ai#789` — https://github.com/Gentleman-Programming/gentle-shell/issues/1460
  - Reference: "espuesta — verbose ≠ incomprensible) y `Gentleman-Programming/gentle-ai#789` (paridad Gentleman/Neutral). Los outpu"
  - veredicto_humano: pendiente
- **gentle-shell#1456** -> `gentle-ai#4967` — https://github.com/Gentleman-Programming/gentle-shell/issues/1456
  - Reference: "context: the same retirement landed in Gentleman-Programming/gentle-ai#4967. The closure list below is limited to"
  - veredicto_humano: pendiente
- **gentle-shell#1399** -> `gentle-ai#4945` — https://github.com/Gentleman-Programming/gentle-shell/issues/1399
  - Reference: "inally filed in the wrong repository as Gentleman-Programming/gentle-ai#4945; that one will be closed in favour of t"
  - veredicto_humano: pendiente
- **gentle-shell#1325** -> `gentle-ai#4611` — https://github.com/Gentleman-Programming/gentle-shell/issues/1325
  - Reference: "reviewer (`lib/inprocess-reviewer.ts`, gentle-ai#4611 / gentle-pi#311) completes one frozen p"
  - veredicto_humano: pendiente
- **gentle-shell#1084** -> `gentle-ai#4520` — https://github.com/Gentleman-Programming/gentle-shell/issues/1084
  - Reference: "e same drift class has already produced gentle-ai#4520 and gentle-ai#4104. ### Proposed outco"
  - veredicto_humano: pendiente
- **gentle-shell#1084** -> `gentle-ai#4104` — https://github.com/Gentleman-Programming/gentle-shell/issues/1084
  - Reference: "has already produced gentle-ai#4520 and gentle-ai#4104. ### Proposed outcome - Declare `inte"
  - veredicto_humano: pendiente
- **gentle-shell#998** -> `gentle-ai#4272` — https://github.com/Gentleman-Programming/gentle-shell/issues/998
  - Reference: "closure. The coordinated schema fix in Gentleman-Programming/gentle-ai#4272 admits that provider-owned evidence, bu"
  - veredicto_humano: pendiente
- **gentle-shell#945** -> `gentle-ai#111` — https://github.com/Gentleman-Programming/gentle-shell/issues/945
  - Reference: "request is intentionally separate from Gentleman-Programming/gentle-ai#111, which concerns RTK as an optional Gent"
  - veredicto_humano: pendiente
- **gentle-shell#753** -> `engram#1090` — https://github.com/Gentleman-Programming/gentle-shell/issues/753
  - Reference: "guard. Related but distinct issues: - Gentleman-Programming/engram#1090 is the source report being transferred"
  - veredicto_humano: pendiente
- **gentle-shell#741** -> `gentle-ai#3483` — https://github.com/Gentleman-Programming/gentle-shell/issues/741
  - Reference: "ct that native already implements since gentle-ai#3483): 1. Input gate. `expectedInputTargetI"
  - veredicto_humano: pendiente
- **gentle-shell#593** -> `gentle-ai#602` — https://github.com/Gentleman-Programming/gentle-shell/issues/593
  - Reference: "84577d614` and follow-ups, tracked from Gentleman-Programming/gentle-ai#602), but the capability those names refere"
  - veredicto_humano: pendiente

## Repository mentions without a link (weakest signal)

914 issues mention another repository by name with no structured link. A name mention is **not** evidence of dependency: install instructions, comparisons and unrelated prose all mention repositories. No link is proposed for these.

- **gentle-ai#5176** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5176
  - veredicto_humano: pendiente
- **gentle-ai#5175** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5175
  - veredicto_humano: pendiente
- **gentle-ai#5169** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5169
  - veredicto_humano: pendiente
- **gentle-ai#5168** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5168
  - veredicto_humano: pendiente
- **gentle-ai#5166** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5166
  - veredicto_humano: pendiente
- **gentle-ai#5165** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5165
  - veredicto_humano: pendiente
- **gentle-ai#5160** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5160
  - veredicto_humano: pendiente
- **gentle-ai#5159** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5159
  - veredicto_humano: pendiente
- **gentle-ai#5157** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5157
  - veredicto_humano: pendiente
- **gentle-ai#5155** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5155
  - veredicto_humano: pendiente
- **gentle-ai#5152** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5152
  - veredicto_humano: pendiente
- **gentle-ai#5150** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5150
  - veredicto_humano: pendiente
- **gentle-ai#5149** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5149
  - veredicto_humano: pendiente
- **gentle-ai#5143** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5143
  - veredicto_humano: pendiente
- **gentle-ai#5142** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5142
  - veredicto_humano: pendiente
- **gentle-ai#5141** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5141
  - veredicto_humano: pendiente
- **gentle-ai#5140** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5140
  - veredicto_humano: pendiente
- **gentle-ai#5137** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5137
  - veredicto_humano: pendiente
- **gentle-ai#5136** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5136
  - veredicto_humano: pendiente
- **gentle-ai#5129** mentions `engram`, `gentle-shell` — https://github.com/Gentleman-Programming/gentle-ai/issues/5129
  - veredicto_humano: pendiente

## Limits

- A bare repository-name mention never produces a proposed link; only an explicit `repo#N` reference does.
- The module cannot tell a dependency from a comparison, so it reports; it does not classify.
- Numbers are resolved against the open-issue snapshot only; a closed target appears as non-resolving.
