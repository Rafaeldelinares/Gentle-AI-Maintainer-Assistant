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

### gentle-ai#5058 <> gentle-ai#5059
- **A:** bug(review): negotiated OpenCode review.start fails with invalid consent question identity before consent envelope is sh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5058
- **B:** bug(review): negotiated OpenCode review.start fails with invalid consent question identity before consent envelope is sh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5059
- **Shared evidence:** title:identical
- **veredicto_humano:** pendiente

### gentle-ai#3560 <> gentle-ai#3562
- **A:** feat(pi): add bounded Unix model-routing transport
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3560
- **B:** feat(pi): define bounded process transport contract
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3562
- **Shared evidence:** exc:transporterror, quoted:unsupported-platform
- **veredicto_humano:** pendiente

### gentle-shell#1553 <> gentle-shell#946
- **A:** Windows: postinstall fails deterministically with EPERM renaming .gentle-ai staging bundle (blocks pi update --extension
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1553
- **B:** bug(installer): Windows EPERM renaming the staging bundle leaves .gentle-ai empty
  - https://github.com/Gentleman-Programming/gentle-shell/issues/946
- **Shared evidence:** code:EBUSY, code:EPERM
- **veredicto_humano:** pendiente

### gentle-shell#1164 <> gentle-shell#924
- **A:** bug(review): review.capture-validation fails deterministically in preflight — the validator transport produces no final 
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1164
- **B:** review.capture-validation rejects its own admitted evidence when the corrected finding is deterministic (no refuter batc
  - https://github.com/Gentleman-Programming/gentle-shell/issues/924
- **Shared evidence:** quoted:gentle-ai.review-integration.failure/v2, quoted:the negotiated review request is invalid.
- **veredicto_humano:** pendiente

### gentle-ai#4491 <> gentle-ai#4952
- **A:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **B:** fix(review): START rejects candidate accepted by inspect
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4952
- **Shared evidence:** quoted:candidate-view-invalid, quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#1291 <> gentle-ai#4263
- **A:** fix: EACCES on Android external storage during skill registry refresh
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1291
- **B:** bug(doctor): state:json remedy tells users to delete state.json on a permission error
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4263
- **Shared evidence:** code:EACCES, exc:patherror
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

### gentle-shell#446 <> gentle-shell#449
- **A:** feat(runtime): execute one prepared foreground Pi task through the authoritative registry
  - https://github.com/Gentleman-Programming/gentle-shell/issues/446
- **B:** feat(runtime): classify one direct Pi foreground run outcome
  - https://github.com/Gentleman-Programming/gentle-shell/issues/449
- **Shared evidence:** quoted:agent.state.errormessage, quoted:failed/prompt-failed
- **veredicto_humano:** pendiente

### gentle-shell#446 <> gentle-shell#448
- **A:** feat(runtime): execute one prepared foreground Pi task through the authoritative registry
  - https://github.com/Gentleman-Programming/gentle-shell/issues/446
- **B:** feat(runtime): atomically settle managed tasks with one closed final result
  - https://github.com/Gentleman-Programming/gentle-shell/issues/448
- **Shared evidence:** quoted:failed/cleanup-failed, quoted:failed/prompt-failed, quoted:failed/subscription-failed
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

### gentle-ai#4909 <> gentle-ai#5117
- **A:** [Automated provider defect] bug(opencode): possible regression of #3987 on 3.5.0 — reviewer Tasks rejected for a target 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4909
- **B:** [Automated provider defect] bug(opencode): reviewer Task refused as immutable_review_transport_unsupported on 3.7.0 stab
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5117
- **Shared evidence:** quoted:opencode_review_transport_binding_invalid
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

### gentle-ai#4509 <> gentle-ai#5066
- **A:** bug(installer): pipeline stalls with pending steps after a step fails, no auto-recovery/rollback
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4509
- **B:** bug(opencode-plugin): OpenCode V2 community-plugin refusal is classified as a failed apply step, so install runs end in 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5066
- **Shared evidence:** quoted:pipeline completed with errors
- **veredicto_humano:** pendiente

### gentle-ai#5061 <> gentle-ai#5062
- **A:** test(cli): install and sync tests inherit the host codex binary and fail when its version probe fails
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5061
- **B:** test(app): the documented-invocation sandbox is not hermetic — a concurrent Go toolchain write fails t.TempDir cleanup
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5062
- **Shared evidence:** frame:internal/app/documented_invocation_test.go:313
- **veredicto_humano:** pendiente

### gentle-ai#4795 <> gentle-ai#5042
- **A:** bug(opencode): engram plugin adapter still ships V1 shape — fails OpenCode 2.x loader (no default export)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4795
- **B:** engram.ts plugin rejected by opencode 2.0.18 (expects effect/setup, gets {id, server})
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5042
- **Shared evidence:** exc:loaderror
- **veredicto_humano:** pendiente

### gentle-ai#4337 <> gentle-ai#4842
- **A:** pi-host-relay: subprocess transport failure leaves reviewer slot pending without retry semantics
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4337
- **B:** bug(pi): pi-host-relay reviewer completion fails deterministically with JSON parse error on one lens while sibling lens 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4842
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4337 <> gentle-ai#4949
- **A:** pi-host-relay: subprocess transport failure leaves reviewer slot pending without retry semantics
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4337
- **B:** bug(pi): el relevo de revisores ignora el perfil de modelos fijado
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4949
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4337 <> gentle-ai#4997
- **A:** pi-host-relay: subprocess transport failure leaves reviewer slot pending without retry semantics
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4337
- **B:** bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4842 <> gentle-ai#4949
- **A:** bug(pi): pi-host-relay reviewer completion fails deterministically with JSON parse error on one lens while sibling lens 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4842
- **B:** bug(pi): el relevo de revisores ignora el perfil de modelos fijado
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4949
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4842 <> gentle-ai#4997
- **A:** bug(pi): pi-host-relay reviewer completion fails deterministically with JSON parse error on one lens while sibling lens 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4842
- **B:** bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4949 <> gentle-ai#4997
- **A:** bug(pi): el relevo de revisores ignora el perfil de modelos fijado
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4949
- **B:** bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **Shared evidence:** quoted:pi-host-relay-transport-failure
- **veredicto_humano:** pendiente

### gentle-ai#4664 <> gentle-ai#4748
- **A:** bug(review): claude-code capture-validation refuses the rctx2 context that bound STATUS keeps reissuing, so the prescrib
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4664
- **B:** [Automated provider defect] Claude Code: the four collect-returned capture-result slots refuse when launched concurrentl
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4748
- **Shared evidence:** quoted:invalid rctx2 repository context
- **veredicto_humano:** pendiente

### gentle-ai#4664 <> gentle-ai#4997
- **A:** bug(review): claude-code capture-validation refuses the rctx2 context that bound STATUS keeps reissuing, so the prescrib
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4664
- **B:** bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **Shared evidence:** quoted:invalid rctx2 repository context
- **veredicto_humano:** pendiente

### gentle-ai#4748 <> gentle-ai#4997
- **A:** [Automated provider defect] Claude Code: the four collect-returned capture-result slots refuse when launched concurrentl
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4748
- **B:** bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so 
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **Shared evidence:** quoted:invalid rctx2 repository context
- **veredicto_humano:** pendiente

### gentle-ai#4488 <> gentle-ai#4491
- **A:** bug(review): intended-untracked selection fails with schema-incompatible
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4488
- **B:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **Shared evidence:** quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#4488 <> gentle-ai#4902
- **A:** bug(review): intended-untracked selection fails with schema-incompatible
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4488
- **B:** bug(review): capture-validation reports no mutation after terminal validator escalation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4902
- **Shared evidence:** quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#4488 <> gentle-ai#4952
- **A:** bug(review): intended-untracked selection fails with schema-incompatible
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4488
- **B:** fix(review): START rejects candidate accepted by inspect
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4952
- **Shared evidence:** quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#4491 <> gentle-ai#4902
- **A:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **B:** bug(review): capture-validation reports no mutation after terminal validator escalation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4902
- **Shared evidence:** quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#4902 <> gentle-ai#4952
- **A:** bug(review): capture-validation reports no mutation after terminal validator escalation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4902
- **B:** fix(review): START rejects candidate accepted by inspect
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4952
- **Shared evidence:** quoted:resolve-native-operation-failure
- **veredicto_humano:** pendiente

### gentle-ai#2196 <> gentle-ai#4491
- **A:** bug(review): fresh candidate rejected before native START
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2196
- **B:** bug(review): lens captures reject as different session route after two admissions; START replay then fails candidate-vie
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4491
- **Shared evidence:** quoted:candidate-view-invalid
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

## Limits

- Only **same-repository** pairs. Cross-repository duplication is a linking question (Module C).
- A shared signature is evidence, not proof: the same error can come from different causes.
- Issues without stack traces or distinctive strings cannot be matched, so this module under-reports rather than over-reports on prose-only reports.
- No semantic similarity, no LLM: the module is deterministic and reproducible.
