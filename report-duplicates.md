# Module B — Probable Duplicates

> **Read-only module.** Finds probable duplicate open issues in the same repository using deterministic evidence: a shared rare error signature (exception class, error code, `file:line` frame, quoted error string, exit code) or near-identical normalized titles.
>
> **It never closes, merges or comments.** Every pair is a suggestion with its shared evidence, and every entry is `veredicto_humano: pendiente`.
>
> Reproduce with `python3 modules/duplicates.py`.

## Summary

| Metric | Value |
| --- | --- |
| Issues analysed | 1228 |
| Candidate duplicate pairs | 108 |
| Strong-evidence pairs | 7 |
| Weaker-evidence pairs | 101 |

### Candidate pairs by repository

| Repository | Candidate pairs |
| --- | --- |
| `gentle-ai` | 68 |
| `gentle-shell` | 39 |
| `engram` | 1 |

### Evidence types

| Evidence prefix | Meaning |
| --- | --- |
| `exc:` | exception or panic class (e.g. `NullPointerException`) |
| `code:` | error code (e.g. `TS6306`, `ENOENT`) |
| `frame:` | `file:line` from a stack trace |
| `quoted:` | quoted error string containing an error keyword |
| `exit:` | exit code |
| `dump:goroutine` | goroutine dump present |
| `title-*` | normalized-title similarity |

> **"Strong evidence" means the pair shares distinctive identifiers, not that it is certainly a duplicate.** Two sibling issues that implement the same feature often share exception names and configuration strings. The tier orders the maintainer's reading; it never decides.

## Strong-evidence pairs (up to 30)

### gentle-ai#3560 <> gentle-ai#3562
- **A:** feat(pi): add bounded Unix model-routing transport
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3560
- **B:** feat(pi): define bounded process transport contract
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3562
- **Shared evidence:** exc:transporterror, quoted:unsupported-platform
- **veredicto_humano:** pendiente

### gentle-ai#5058 <> gentle-ai#5059
- **A:** bug(review): negotiated OpenCode review.start fails with invalid consent question identity before consent envelope is sh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5058
- **B:** bug(review): negotiated OpenCode review.start fails with invalid consent question identity before consent envelope is sh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5059
- **Shared evidence:** title:identical
- **veredicto_humano:** pendiente

### gentle-shell#1164 <> gentle-shell#924
- **A:** bug(review): review.capture-validation fails deterministically in preflight — the validator transport produces no final 
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1164
- **B:** review.capture-validation rejects its own admitted evidence when the corrected finding is deterministic (no refuter batc
  - https://github.com/Gentleman-Programming/gentle-shell/issues/924
- **Shared evidence:** quoted:gentle-ai.review-integration.failure/v2, quoted:the negotiated review request is invalid.
- **veredicto_humano:** pendiente

### gentle-shell#1553 <> gentle-shell#946
- **A:** Windows: postinstall fails deterministically with EPERM renaming .gentle-ai staging bundle (blocks pi update --extension
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1553
- **B:** bug(installer): Windows EPERM renaming the staging bundle leaves .gentle-ai empty
  - https://github.com/Gentleman-Programming/gentle-shell/issues/946
- **Shared evidence:** code:EBUSY, code:EPERM
- **veredicto_humano:** pendiente

### gentle-ai#1291 <> gentle-ai#4263
- **A:** fix: EACCES on Android external storage during skill registry refresh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1291
- **B:** bug(doctor): state:json remedy tells users to delete state.json on a permission error
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4263
- **Shared evidence:** code:EACCES, exc:patherror
- **veredicto_humano:** pendiente

### gentle-ai#4491 <> gentle-ai#4952
- **A:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **B:** fix(review): START rejects candidate accepted by inspect
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4952
- **Shared evidence:** quoted:candidate-view-invalid, quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-shell#1187 <> gentle-shell#578
- **A:** bug(review): the prompt-size-derived reviewer relay timeout has ~0% margin, so lens runs are killed 16-18ms over the bou
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1187
- **B:** docs: document review relay configuration (relay contract env, dev-binary override, reviewer timeout)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/578
- **Shared evidence:** quoted:gentle_pi_review_relay_pi_timeout_ms, quoted:pi-host-relay-timeout
- **veredicto_humano:** pendiente

## Weaker-evidence pairs (up to 30)

### gentle-ai#2609 <> gentle-ai#3135
- **A:** bug(opencode): general worker completes with empty task result
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2609
- **B:** bug(opencode): general background worker completes with empty task result
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3135
- **Shared evidence:** title-jaccard:0.86
- **veredicto_humano:** pendiente

### gentle-ai#3581 <> gentle-ai#3608
- **A:** feat(pi): validate model-routing drafts
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3581
- **B:** feat(tui): edit and validate Pi model-routing drafts
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3608
- **Shared evidence:** title-jaccard:0.80
- **veredicto_humano:** pendiente

### gentle-ai#4940 <> gentle-ai#5066
- **A:** bug(installer): post-apply verification requires V2-skipped logo files (tui.json, gentle-logo.tsx), so install can never
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4940
- **B:** bug(opencode-plugin): OpenCode V2 community-plugin refusal is classified as a failed apply step, so install runs end in 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5066
- **Shared evidence:** exc:unsupportedlogoerror, quoted:unsupportedlogoerror
- **veredicto_humano:** pendiente

### gentle-shell#446 <> gentle-shell#448
- **A:** feat(runtime): execute one prepared foreground Pi task through the authoritative registry
  - https://github.com/Gentleman-Programming/gentle-shell/issues/446
- **B:** feat(runtime): atomically settle managed tasks with one closed final result
  - https://github.com/Gentleman-Programming/gentle-shell/issues/448
- **Shared evidence:** quoted:failed/cleanup-failed, quoted:failed/prompt-failed, quoted:failed/subscription-failed
- **veredicto_humano:** pendiente

### gentle-shell#446 <> gentle-shell#449
- **A:** feat(runtime): execute one prepared foreground Pi task through the authoritative registry
  - https://github.com/Gentleman-Programming/gentle-shell/issues/446
- **B:** feat(runtime): classify one direct Pi foreground run outcome
  - https://github.com/Gentleman-Programming/gentle-shell/issues/449
- **Shared evidence:** quoted:agent.state.errormessage, quoted:failed/prompt-failed
- **veredicto_humano:** pendiente

### engram#1454 <> engram#1462
- **A:** bug(codex/windows): Norton behavioral detection during hook execution; HTTP unavailable while MCP remains usable
  - https://github.com/Gentleman-Programming/engram/issues/1454
- **B:** feat(cli): run engram serve in the background as a daemon (--daemon, --status, --stop)
  - https://github.com/Gentleman-Programming/engram/issues/1462
- **Shared evidence:** exit:0
- **veredicto_humano:** pendiente

### gentle-ai#1291 <> gentle-ai#2143
- **A:** fix: EACCES on Android external storage during skill registry refresh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1291
- **B:** feat(system): Android/Termux first-class platform detection + external CodeGraph support
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2143
- **Shared evidence:** code:EACCES
- **veredicto_humano:** pendiente

### gentle-ai#2143 <> gentle-ai#4263
- **A:** feat(system): Android/Termux first-class platform detection + external CodeGraph support
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2143
- **B:** bug(doctor): state:json remedy tells users to delete state.json on a permission error
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4263
- **Shared evidence:** code:EACCES
- **veredicto_humano:** pendiente

### gentle-ai#2196 <> gentle-ai#4491
- **A:** bug(review): fresh candidate rejected before native START
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2196
- **B:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **Shared evidence:** quoted:candidate-view-invalid
- **veredicto_humano:** pendiente

### gentle-ai#2196 <> gentle-ai#4692
- **A:** bug(review): fresh candidate rejected before native START
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2196
- **B:** bug(review): Pi compact START returns schema-incompatible and never creates a lineage (empty workspace candidate)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4692
- **Shared evidence:** quoted:outcome: native-operation-failed
- **veredicto_humano:** pendiente

### gentle-ai#2196 <> gentle-ai#4857
- **A:** bug(review): fresh candidate rejected before native START
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2196
- **B:** bug(review): candidate-view materializes a full 5.2 GB worktree copy for a 16-path candidate, times out at a 10s git add
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4857
- **Shared evidence:** quoted:candidate-view-invalid
- **veredicto_humano:** pendiente

### gentle-ai#2196 <> gentle-ai#4952
- **A:** bug(review): fresh candidate rejected before native START
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2196
- **B:** fix(review): START rejects candidate accepted by inspect
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4952
- **Shared evidence:** quoted:candidate-view-invalid
- **veredicto_humano:** pendiente

### gentle-ai#2203 <> gentle-ai#4762
- **A:** fix(ci): make Claude network-none proof not applicable for legacy PR heads
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2203
- **B:** feat(installation): renew managed opencode.json format for OpenCode 2.x strict-schema conformance
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4762
- **Shared evidence:** code:ERROR
- **veredicto_humano:** pendiente

### gentle-ai#2356 <> gentle-ai#4509
- **A:** fix(installer): report state and offer recovery on step failure
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2356
- **B:** bug(installer): pipeline stalls with pending steps after a step fails, no auto-recovery/rollback
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4509
- **Shared evidence:** quoted:pipeline completed with errors
- **veredicto_humano:** pendiente

### gentle-ai#2356 <> gentle-ai#5066
- **A:** fix(installer): report state and offer recovery on step failure
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2356
- **B:** bug(opencode-plugin): OpenCode V2 community-plugin refusal is classified as a failed apply step, so install runs end in 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5066
- **Shared evidence:** quoted:pipeline completed with errors
- **veredicto_humano:** pendiente

### gentle-ai#2597 <> gentle-ai#4878
- **A:** .claude/CLAUDE.md mandates tools unavailable on Windows and prescribes brew
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2597
- **B:** [Automated provider defect] bug(sync): gentle-ai.exe missing from go/bin after 'sync' reports success (Windows)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4878
- **Shared evidence:** exit:127
- **veredicto_humano:** pendiente

### gentle-ai#3016 <> gentle-ai#4816
- **A:** fix(update): honor pnpm for OpenCode plugin upgrades
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3016
- **B:** [Automated provider defect] bug(opencode): orchestrator calls unavailable tools (question, task) — TypeError crashes ses
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4816
- **Shared evidence:** exc:typeerror
- **veredicto_humano:** pendiente

### gentle-ai#3370 <> gentle-ai#4588
- **A:** Canonical 4R missed a deterministic CRITICAL that a second 4R over the same code found
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3370
- **B:** gentle-pi postinstall masks recoverable Go module fetch failure as SumDB error
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4588
- **Shared evidence:** code:EPERM
- **veredicto_humano:** pendiente

### gentle-ai#3370 <> gentle-ai#4814
- **A:** Canonical 4R missed a deterministic CRITICAL that a second 4R over the same code found
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3370
- **B:** fix(install): gentle-pi postinstall always fails on Windows — lstat/fstat dev mismatch rejects every settings.json read
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4814
- **Shared evidence:** code:EPERM
- **veredicto_humano:** pendiente

### gentle-ai#3491 <> gentle-ai#3595
- **A:** feat(skills): a capability that decides whether a verified observation should change a future authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3491
- **B:** fix(cli): make the refusal-resolution ratchet enforce the runnable-command grammar the benchmark already classifies
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3595
- **Shared evidence:** quoted:internal/cli/refusal_resolution_ratchet_test.go
- **veredicto_humano:** pendiente

### gentle-ai#3558 <> gentle-ai#4667
- **A:** bug(tui): Reset Review Store is offered outside a Git repository and fails with a raw git rev-parse error (2.4.0, macOS)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3558
- **B:** bug(review): negotiated status regressed to git_command_failed on an unborn repository (2.9.1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4667
- **Shared evidence:** exit:128
- **veredicto_humano:** pendiente

### gentle-ai#3560 <> gentle-ai#3571
- **A:** feat(pi): add bounded Unix model-routing transport
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3560
- **B:** feat(pi): define safe Windows transport plans
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3571
- **Shared evidence:** quoted:unsupported-platform
- **veredicto_humano:** pendiente

### gentle-ai#3562 <> gentle-ai#3571
- **A:** feat(pi): define bounded process transport contract
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3562
- **B:** feat(pi): define safe Windows transport plans
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3571
- **Shared evidence:** quoted:unsupported-platform
- **veredicto_humano:** pendiente

### gentle-ai#3580 <> gentle-ai#3605
- **A:** feat(pi): apply validated model-routing drafts
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3580
- **B:** feat(pi): parse typed model-routing apply responses
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3605
- **Shared evidence:** exit:6
- **veredicto_humano:** pendiente

### gentle-ai#4030 <> gentle-ai#4909
- **A:** bug(opencode): single-worktree reliability reviewer wedged — lens-context succeeds but opencode-transport rejects same r
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4030
- **B:** [Automated provider defect] bug(opencode): possible regression of #3987 on 3.5.0 — reviewer Tasks rejected for a target 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4909
- **Shared evidence:** quoted:opencode_review_transport_binding_invalid
- **veredicto_humano:** pendiente

### gentle-ai#4030 <> gentle-ai#5117
- **A:** bug(opencode): single-worktree reliability reviewer wedged — lens-context succeeds but opencode-transport rejects same r
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4030
- **B:** [Automated provider defect] bug(opencode): reviewer Task refused as immutable_review_transport_unsupported on 3.7.0 stab
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5117
- **Shared evidence:** quoted:opencode_review_transport_binding_invalid
- **veredicto_humano:** pendiente

### gentle-ai#4046 <> gentle-ai#4147
- **A:** fix(review): finish root 18's representation sweep — opaque instruction handles, Git environment classes, degenerate-can
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
- **B:** refactor(review): decompose the review status god-function and contract validator
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4147
- **Shared evidence:** quoted:git_command_failed
- **veredicto_humano:** pendiente

### gentle-ai#4046 <> gentle-ai#4667
- **A:** fix(review): finish root 18's representation sweep — opaque instruction handles, Git environment classes, degenerate-can
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
- **B:** bug(review): negotiated status regressed to git_command_failed on an unborn repository (2.9.1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4667
- **Shared evidence:** quoted:git_command_failed
- **veredicto_humano:** pendiente

### gentle-ai#4046 <> gentle-ai#4670
- **A:** fix(review): finish root 18's representation sweep — opaque instruction handles, Git environment classes, degenerate-can
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
- **B:** bug(review): stop-hook and mode status fail on a Windows SMB share while RDD is off (2.9.1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4670
- **Shared evidence:** quoted:git_command_failed
- **veredicto_humano:** pendiente

### gentle-ai#4147 <> gentle-ai#4667
- **A:** refactor(review): decompose the review status god-function and contract validator
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4147
- **B:** bug(review): negotiated status regressed to git_command_failed on an unborn repository (2.9.1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4667
- **Shared evidence:** quoted:git_command_failed
- **veredicto_humano:** pendiente

## Limits

- Only **same-repository** pairs. Cross-repository duplication is a linking question (Module C).
- A shared signature is evidence, not proof: the same error can come from different causes.
- Issues without stack traces or distinctive strings cannot be matched, so this module under-reports rather than over-reports on prose-only reports.
- No semantic similarity, no LLM: the module is deterministic and reproducible.
