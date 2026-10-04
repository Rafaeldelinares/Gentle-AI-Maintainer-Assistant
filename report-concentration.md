# Module E — Where the Reports Concentrate

> Generated from the frozen snapshot of 1228 open issues. Read-only: this
> module writes no field, comments on nothing, and closes nothing. Every entry is
> `veredicto_humano: pendiente`.

## Summary

- Issues in the snapshot: **1228**
- Issues mentioning at least one repository path: **458** (37.3%)
- Of those, the engine left **without a band**: **251**
- Issues mentioning no path at all: **770** — no cluster
  can reach them, and they are counted here rather than implied away
- Distinct subsystems (repository + directory): **164**
- The top 15 subsystems cover **326** of the 458 issues that mention a path (71%)

## Clusters by subsystem

The unit is the directory where a change would land, capped at three levels. A
directory named by many reports is **one place to look**, not a task and not a claim
about importance.

| Repository | Subsystem | Issues | Without a band |
| --- | --- | --- | --- |
| `gentle-shell` | `extensions` | **99** | 62 |
| `gentle-shell` | `lib` | **98** | 63 |
| `gentle-ai` | `internal/cli` | **55** | 32 |
| `gentle-shell` | `tests` | **39** | 23 |
| `gentle-ai` | `docs` | **35** | 11 |
| `gentle-ai` | `internal/reviewtransaction` | **25** | 16 |
| `gentle-shell` | `docs` | **19** | 13 |
| `gentle-ai` | `internal/assets/skills` | **16** | 6 |
| `gentle-ai` | `internal/tui` | **16** | 7 |
| `gentle-ai` | `internal/components/sdd` | **15** | 6 |
| `gentle-shell` | `assets` | **15** | 7 |
| `gentle-ai` | `internal/components/communitytool` | **14** | 9 |
| `gentle-ai` | `internal/tui/screens` | **14** | 3 |
| `gentle-ai` | `internal/components/engram` | **13** | 6 |
| `gentle-ai` | `internal/assets/opencode` | **12** | 5 |

### `gentle-shell` — `extensions` (99 issues)

- **gentle-shell#1023** — Windows: trusted helper path resolution fails before native review START
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1023
- **gentle-shell#1025** — feat(agents): support launch-local routing classes without mutating global profiles
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1025
- **gentle-shell#1029** — bug(agents): volatile RDD/SDD status embedded in the rebuilt system prompt defeats prompt caching
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1029
- **gentle-shell#1031** — Review subagent dispatch rejects the run tool's own fields (label, workspace_root, …): SUBAGENT_RUN_KEYS out of sync
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1031
- **gentle-shell#1033** — bug(sdd): fresh OpenSpec research locator rejected outside exact scope
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1033
- **gentle-shell#1042** — feat(skills): native selected-only skill resolution and loading
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1042
- **gentle-shell#1044** — Engram tools are never detected when the MCP adapter prefixes tool names (hybrid preflight unreachable + SDD agents silently lose memory)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1044
- **gentle-shell#1046** — sdd-research cannot persist on a first run: the scope guard requires pre-existing carried artifact locators
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1046
- **gentle-shell#1051** — feat(sdd): coordinate classical workflow parity across Pi runtime and assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1051
- **gentle-shell#1092** — bug(agents): unread background completion becomes transcript-only during a long parent tool call
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1092
- **gentle-shell#1093** — bug(changes): the capture-limit warning repeats on every later write/edit
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1093
- **gentle-shell#1115** — bug(extensions): quiet-tools SHA-256s the ~26 MB gentle-ai dev binary on every bash render call
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1115
- **gentle-shell#1119** — bug(extensions): pi-pretty dynamic-import wrapper still fails under pnpm isolated layout
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1119
- **gentle-shell#1145** — bug(subagents): Git stderr leaks into TUI input when launching from a non-Git workspace
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1145
- **gentle-shell#1174** — bug(agents): an explicit mode:"task" still forces foreground under an enabled background-subagents policy
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1174
- **gentle-shell#1201** — bug(ui): /gentle:profiles panel ignores q, breaking the q-to-close convention
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1201
- **gentle-shell#1202** — bug(guard): guarded-command matching ignores position, so a read-only search prompts or is blocked
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1202
- **gentle-shell#1210** — bug(shell): NaN usage only works when the custom provider id is exactly "nan"
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1210
- **gentle-shell#1212** — bug(review): session review consent re-prompts for every candidate when reviews run in per-PR throwaway clones (grant keyed to one canonical git common-dir identity)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1212
- **gentle-shell#1226** — fix(profiles): reconcile live thinking when an orchestrator omits it
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1226
- **gentle-shell#1231** — bug(profiles): /gentle:profiles never shows agent models on terminals narrower than 60 columns (portrait mobile)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1231
- **gentle-shell#1244** — feat(startup): allow disabling the runtime info panel (stats table) entirely
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1244
- **gentle-shell#1245** — feat(sdd): add a documented way to remove gentle-pi-owned SDD assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1245
- **gentle-shell#1253** — Provider review.start transition unresolvable from headless/relay session (no consent envelope; native START rejects target)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1253
- **gentle-shell#1256** — bug(orchestrator): writer pre-check rejects valid task surfaces with non-specific reason (regression-class of #484)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1256
- **gentle-shell#1261** — Support opencode-go subscription usage in /gentle:usage
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1261
- **gentle-shell#1264** — bug(startup): text logo missing below 122 columns and 5s animation cap freezes last letters on slow devices
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1264
- **gentle-shell#1277** — bug(ask): first-party ask_user_question conflicts with @juicesharp/rpiv-ask-user-question and hard-fails Pi load
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1277
- **gentle-shell#1284** — bug(harness): the ODD delegation gate deterministically misses the second distinct direct file
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1284
- **gentle-shell#1308** — orchestrator_send_message with no recipient_session_id parks the call on a single-select human picker
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1308
- **gentle-shell#1309** — gentle-ai-worker edit surfaces resolve only against the session's repository, and a zero-write task is rejected
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1309
- **gentle-shell#1324** — bug(review): targeted validation fails opaquely, then bound STATUS returns unrelated on unchanged candidate
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1324
- **gentle-shell#1349** — bug(profiles): applying a newly created empty profile wipes models.json and clears every agent's routing
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1349
- **gentle-shell#1359** — feat(orchestrator): automatic non-blocking delegation reminders that keep inline-vs-delegate decision with the model
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1359
- **gentle-shell#1367** — bug(todo): dynamic stale-turn counter in system prompt invalidates prompt cache every turn
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1367
- **gentle-shell#1371** — bug(review): approved closure envelope offers acknowledgement input the facade refuses, with no lineage-only hint
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1371
- **gentle-shell#1460** — feat(communication): configurable clarity layer for user-facing replies, plans, and docs
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1460
- **gentle-shell#1466** — orchestrator_send_message: parallel sends show only one consent prompt; the other blocks indefinitely with no visible prompt
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1466
- **gentle-shell#1473** — review.capture-validation slot is always rejected under contract v2 (singular `value` wire shape gated on v5)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1473
- **gentle-shell#1478** — feat(models): explicit orchestrator model/effort selection in /gentle-models so profiles stop silently overwriting the live session
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1478
- …and 59 more in this subsystem

### `gentle-shell` — `lib` (98 issues)

- **gentle-shell#1022** — bug(sdd-status): Pi-side reportIsClearlyPassing cannot read v2 pass_with_warnings envelopes, permanently blocking sync/archive
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1022
- **gentle-shell#1023** — Windows: trusted helper path resolution fails before native review START
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1023
- **gentle-shell#1025** — feat(agents): support launch-local routing classes without mutating global profiles
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1025
- **gentle-shell#1031** — Review subagent dispatch rejects the run tool's own fields (label, workspace_root, …): SUBAGENT_RUN_KEYS out of sync
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1031
- **gentle-shell#1033** — bug(sdd): fresh OpenSpec research locator rejected outside exact scope
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1033
- **gentle-shell#1042** — feat(skills): native selected-only skill resolution and loading
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1042
- **gentle-shell#1043** — bug(changes): session change capture stops after 256 write/edit records
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1043
- **gentle-shell#1044** — Engram tools are never detected when the MCP adapter prefixes tool names (hybrid preflight unreachable + SDD agents silently lose memory)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1044
- **gentle-shell#1051** — feat(sdd): coordinate classical workflow parity across Pi runtime and assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1051
- **gentle-shell#1077** — bug(review): provider usage exhaustion is discovered only after START freezes the candidate and the human authorizes the forecast
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1077
- **gentle-shell#1092** — bug(agents): unread background completion becomes transcript-only during a long parent tool call
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1092
- **gentle-shell#1093** — bug(changes): the capture-limit warning repeats on every later write/edit
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1093
- **gentle-shell#1115** — bug(extensions): quiet-tools SHA-256s the ~26 MB gentle-ai dev binary on every bash render call
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1115
- **gentle-shell#1137** — bug(review): a slot-deterministic pi-empty-output relay failure never stops, so STATUS reoffers the same slot forever
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1137
- **gentle-shell#1139** — bug(review): a reviewer child terminated by a signal is reported as a generic pi-failed transport failure
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1139
- **gentle-shell#1145** — bug(subagents): Git stderr leaks into TUI input when launching from a non-Git workspace
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1145
- **gentle-shell#1187** — bug(review): the prompt-size-derived reviewer relay timeout has ~0% margin, so lens runs are killed 16-18ms over the bound
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1187
- **gentle-shell#1201** — bug(ui): /gentle:profiles panel ignores q, breaking the q-to-close convention
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1201
- **gentle-shell#1207** — bug(review): facade main rejects gentle-ai main's negotiated status/v8 — every review operation fails as schema-incompatible under the dev-binary override
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1207
- **gentle-shell#1210** — bug(shell): NaN usage only works when the custom provider id is exactly "nan"
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1210
- **gentle-shell#1212** — bug(review): session review consent re-prompts for every candidate when reviews run in per-PR throwaway clones (grant keyed to one canonical git common-dir identity)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1212
- **gentle-shell#1231** — bug(profiles): /gentle:profiles never shows agent models on terminals narrower than 60 columns (portrait mobile)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1231
- **gentle-shell#1232** — fix(todo): validate persisted Gentle snapshots before replay
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1232
- **gentle-shell#1235** — bug(review): in-process lens completion never sends the provider session header, so no opencode-go model can serve any reviewer role
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1235
- **gentle-shell#1236** — bug(agents): Agents widget crashes when task model metadata is missing
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1236
- **gentle-shell#1245** — feat(sdd): add a documented way to remove gentle-pi-owned SDD assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1245
- **gentle-shell#1251** — bug(subagents): sdd-init stalls with zero turns on phase-shaped prompts while trivial prompts complete (controlled A/B, servable model)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1251
- **gentle-shell#1259** — bug(review): an empty-output refusal discards the reviewer model and its token usage — the evidence that separates truncation from an empty answer
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1259
- **gentle-shell#1260** — Native review cannot complete on OpenCode-hosted providers: the in-process completion omits x-opencode-session
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1260
- **gentle-shell#1261** — Support opencode-go subscription usage in /gentle:usage
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1261
- **gentle-shell#1262** — perf(agents): avoid re-reading unchanged remote activity files on every presence poll
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1262
- **gentle-shell#1284** — bug(harness): the ODD delegation gate deterministically misses the second distinct direct file
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1284
- **gentle-shell#1293** — Subagent thread scroll accumulates hidden offset past the bottom
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1293
- **gentle-shell#1296** — bug(shell): solid black block renders over transcript during rail wheel-scroll
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1296
- **gentle-shell#1297** — bug(ask): stale transcript frame bleeds into ask_user_question dialog right after reading an image
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1297
- **gentle-shell#1298** — feat(shell): make fullscreen header position configurable (top header vs lateral rail)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1298
- **gentle-shell#1325** — feat(review): let the in-process reviewer return its result through one strict tool call so local OpenAI-compatible models stop failing admission on JSON escaping
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1325
- **gentle-shell#1349** — bug(profiles): applying a newly created empty profile wipes models.json and clears every agent's routing
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1349
- **gentle-shell#1355** — fix(openspec): preserve internal markdown dividers in requirement content
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1355
- **gentle-shell#1359** — feat(orchestrator): automatic non-blocking delegation reminders that keep inline-vs-delegate decision with the model
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1359
- …and 58 more in this subsystem

### `gentle-ai` — `internal/cli` (55 issues)

- **gentle-ai#1673** — fix(sync): reconcile the complete managed OpenCode plugin set
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1673
- **gentle-ai#1677** — fix(sync): fail closed when persisted persona state is invalid
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1677
- **gentle-ai#1724** — fix(backup): make restore atomic and conflict-aware
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1724
- **gentle-ai#1734** — feat(cli): add `gentle-ai account link` to connect a machine to an existing Engram Cloud account
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1734
- **gentle-ai#1793** — fix(review): status cannot recover multi-lineage compact-v2 authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1793
- **gentle-ai#1795** — fix(review): preserve staged target selectors and support atomic scope replacement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1795
- **gentle-ai#1973** — feat(review): scope the RDD kill switch per worktree and announce its blast radius
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1973
- **gentle-ai#1989** — feat(gemini): modularize GEMINI.md root to survive Antigravity 12k truncation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1989
- **gentle-ai#2123** — feat(sync): preserve user customizations in managed agent instruction files during sync
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2123
- **gentle-ai#2521** — fix(cli): restore --yes=false and --list=false exit 0 without restoring, listing, or reporting
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2521
- **gentle-ai#2628** — fix(cli): component modifiers report success when their component is not scheduled
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2628
- **gentle-ai#2732** — docs(cli): expose valid --persona values in install --help
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2732
- **gentle-ai#3026** — feat(opencode): add configurable reviewer and worker agents for non-SDD work
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3026
- **gentle-ai#3294** — fix(reporting): make review tool-fault reports evidence-only and reuse canonical publication
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3294
- **gentle-ai#3373** — Lock contention is reported as authority corruption in three places
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3373
- **gentle-ai#3384** — Stop transitions emit a bare reason_code, so consumers invent their own menus
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3384
- **gentle-ai#3474** — ci(policy): required product-behaviour checks never revalidate against the branch tip, so two green PRs can land a red main
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3474
- **gentle-ai#3485** — feat(review): add immutable receipt-review transport adapter for Antigravity
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3485
- **gentle-ai#3491** — feat(skills): a capability that decides whether a verified observation should change a future authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3491
- **gentle-ai#3550** — feat(opencode): enable background subagents by default with post-install controls
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3550
- **gentle-ai#3595** — fix(cli): make the refusal-resolution ratchet enforce the runnable-command grammar the benchmark already classifies
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3595
- **gentle-ai#3669** — design(review): one store load per STATUS call — make negotiated STATUS a pure reader over the runtime's bytes
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3669
- **gentle-ai#4031** — review and issues: negotiated v2 lifecycle on Pi — 3 escalation rounds, 12 sequential lens runs, opaque admission grammar, receipt invisible after burn
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4031
- **gentle-ai#4046** — fix(review): finish root 18's representation sweep — opaque instruction handles, Git environment classes, degenerate-candidate refusal
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
- **gentle-ai#4147** — refactor(review): decompose the review status god-function and contract validator
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4147
- **gentle-ai#4153** — refactor(review): decompose the review start facade pipeline
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4153
- **gentle-ai#4262** — bug(doctor): state:json skips config-dir verification for most agents — agentConfigDir uses drifted agent IDs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4262
- **gentle-ai#4263** — bug(doctor): state:json remedy tells users to delete state.json on a permission error
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4263
- **gentle-ai#4288** — bug(review): capture-result folds six preflight preconditions into one refusal, so a host assembly error is indistinguishable from a contract fault
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4288
- **gentle-ai#4289** — feat(review): emit a runnable command on native capture collect inputs so hosts stop assembling the invocation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4289
- **gentle-ai#4316** — bug(cli): review stop-hook crashes with Go runtime panic (unknown caller pc) during RDD-mode resolution on Windows
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4316
- **gentle-ai#4371** — doctor: tool:gga PATH check is hardcoded (coreTools) and ignores state.json components → permanent false "unhealthy" after deregistration
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4371
- **gentle-ai#4378** — bug(install): Windows compatibility skills refusal names no exit when .agents/skills is a reparse point
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4378
- **gentle-ai#4397** — feat(tui): configure Pi agent model presets by subscription
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4397
- **gentle-ai#4552** — bug(tui): Claude model picker always reopens as Custom — preset tables include "orchestrator" but persistence strips it
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4552
- **gentle-ai#4600** — feat(sync): list the files sync --dry-run would touch instead of only step counts
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4600
- **gentle-ai#4641** — RTK setup fails when adding Claude Code after a Pi-only install
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4641
- **gentle-ai#4715** — fix(doctor): mise shims and Omarchy launcher stubs are counted as duplicate copies of the same tool
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4715
- **gentle-ai#4792** — fix(docs): concurrent review contract claims approved authority is already burned before acknowledgement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4792
- **gentle-ai#4794** — bug(community-tool): a CLI install de-registers Pi CodeGraph and sync can never repair it — the deleted manifest is the existence probe
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4794
- …and 15 more in this subsystem

### `gentle-shell` — `tests` (39 issues)

- **gentle-shell#1017** — Recognized global postinstall resets an explicit tuiMode:"regular" back to fullscreen on every update
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1017
- **gentle-shell#1025** — feat(agents): support launch-local routing classes without mutating global profiles
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1025
- **gentle-shell#1033** — bug(sdd): fresh OpenSpec research locator rejected outside exact scope
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1033
- **gentle-shell#1047** — feat(shell): show kimi-coding subscription usage in the bar and /gentle:usage panel
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1047
- **gentle-shell#1051** — feat(sdd): coordinate classical workflow parity across Pi runtime and assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1051
- **gentle-shell#1111** — test(binary): skip POSIX executable-bit assertion on Windows
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1111
- **gentle-shell#1157** — bug(tests): wall-clock deadline assertion cancels all rdd-status-line tests in local full-suite runs
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1157
- **gentle-shell#1226** — fix(profiles): reconcile live thinking when an orchestrator omits it
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1226
- **gentle-shell#1232** — fix(todo): validate persisted Gentle snapshots before replay
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1232
- **gentle-shell#1256** — bug(orchestrator): writer pre-check rejects valid task surfaces with non-specific reason (regression-class of #484)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1256
- **gentle-shell#1259** — bug(review): an empty-output refusal discards the reviewer model and its token usage — the evidence that separates truncation from an empty answer
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1259
- **gentle-shell#1283** — bug(agents): a matching FIFO cannot block presence discovery is load-sensitive - a 1000 ms child bound breaks under full-suite load
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1283
- **gentle-shell#1284** — bug(harness): the ODD delegation gate deterministically misses the second distinct direct file
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1284
- **gentle-shell#1340** — [Bug]: a long option preview grows the ask_user_question panel past the terminal and hides the transcript
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1340
- **gentle-shell#1359** — feat(orchestrator): automatic non-blocking delegation reminders that keep inline-vs-delegate decision with the model
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1359
- **gentle-shell#1398** — bug(launcher): gentle-shell cannot find the bundled pi runtime (ERR_PACKAGE_PATH_NOT_EXPORTED)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1398
- **gentle-shell#1430** — bug(tests): Vim fixtures assume one Pi TUI Editor constructor
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1430
- **gentle-shell#1431** — bug(tests): Jiti reload child cannot resolve nested dependency
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1431
- **gentle-shell#1487** — bug(launcher): --package-root warning is wrong when a path declaration plus a different requested root forces the take-over
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1487
- **gentle-shell#1494** — bug(orchestrator): small fixes trigger disproportionate ODD, memory and review overhead
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1494
- **gentle-shell#1514** — test(history): mtime fallback tests in history-session-scan-extract fail intermittently
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1514
- **gentle-shell#1625** — bug(vim): the >=0.99.2 Pi bump leaves the host gate pinned to 0.99.1 — verify is red on main with 114 failing tests
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1625
- **gentle-shell#391** — refactor(models): enforce canonical routing names and target authority
  - https://github.com/Gentleman-Programming/gentle-shell/issues/391
- **gentle-shell#414** — feat(parity): consume upstream SDD harness-attempt correction
  - https://github.com/Gentleman-Programming/gentle-shell/issues/414
- **gentle-shell#449** — feat(runtime): classify one direct Pi foreground run outcome
  - https://github.com/Gentleman-Programming/gentle-shell/issues/449
- **gentle-shell#463** — bug(orchestrator): command presence forces subagent verification for bounded checks
  - https://github.com/Gentleman-Programming/gentle-shell/issues/463
- **gentle-shell#511** — fix(orchestrator): enforce parent hot memory persistence on inline direct tasks
  - https://github.com/Gentleman-Programming/gentle-shell/issues/511
- **gentle-shell#593** — bug(agents): SDD child sessions lose mem_* tools because the engram extension is never provisioned
  - https://github.com/Gentleman-Programming/gentle-shell/issues/593
- **gentle-shell#670** — Candidate view materialization fails on Windows for repositories with committed symlinks
  - https://github.com/Gentleman-Programming/gentle-shell/issues/670
- **gentle-shell#687** — feat(shell): show z.ai (GLM Coding Plan) subscription usage in the bar and /gentle:usage panel
  - https://github.com/Gentleman-Programming/gentle-shell/issues/687
- **gentle-shell#719** — fix(review): harden the intended-untracked inspect seam (retention discriminant, verified retain, shape guards, consent-clear test)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/719
- **gentle-shell#759** — feat(sdd-profiles): add native SDD agent configuration profiles
  - https://github.com/Gentleman-Programming/gentle-shell/issues/759
- **gentle-shell#800** — feat(shell): show xAI SuperGrok subscription usage in the bar and /gentle:usage panel
  - https://github.com/Gentleman-Programming/gentle-shell/issues/800
- **gentle-shell#871** — bug(review): select-intended-untracked deterministically rejects an exact inspect selectionBinding
  - https://github.com/Gentleman-Programming/gentle-shell/issues/871
- **gentle-shell#923** — bug(gentle-shell): framePromptLines consumes the last autocomplete row — single-match slash dropdown renders nothing
  - https://github.com/Gentleman-Programming/gentle-shell/issues/923
- **gentle-shell#939** — feat(agents): show task labels in the Agents overlay
  - https://github.com/Gentleman-Programming/gentle-shell/issues/939
- **gentle-shell#967** — bug(windows): hide remaining internal CodeGraph and review process launches
  - https://github.com/Gentleman-Programming/gentle-shell/issues/967
- **gentle-shell#973** — test(shell): add unit tests for lib/shell-gauge.ts
  - https://github.com/Gentleman-Programming/gentle-shell/issues/973
- **gentle-shell#990** — ci(windows): candidate owner preparation fails when a PowerShell spawn exceeds its 5 s timeout
  - https://github.com/Gentleman-Programming/gentle-shell/issues/990

### `gentle-ai` — `docs` (35 issues)

- **gentle-ai#1213** — Engram protocol is injected three times per session (~4,950 tokens of duplication) on claude-code
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1213
- **gentle-ai#128** — feat(architecture): separate multi-agent and single-agent skill distribution with delegation model awareness
  - https://github.com/Gentleman-Programming/gentle-ai/issues/128
- **gentle-ai#1724** — fix(backup): make restore atomic and conflict-aware
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1724
- **gentle-ai#1734** — feat(cli): add `gentle-ai account link` to connect a machine to an existing Engram Cloud account
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1734
- **gentle-ai#1739** — feat: Grok CLI integration as native agent (MCP, SDD, skills, Engram, personas)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1739
- **gentle-ai#1863** — feat(workflow): establish canonical workflow doctrine and exact embedded mirror
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1863
- **gentle-ai#1873** — test(adapters): certify installed capabilities through each agent's native runtime
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1873
- **gentle-ai#2156** — feat(release): declare the provider surface as a signed release artifact
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2156
- **gentle-ai#3292** — docs(pi): pi.md omits the managed background-subagents policy added in b6dbb4c3
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3292
- **gentle-ai#3490** — docs(contributing): add a "Contributing a Skill" section built from decisions already made in closures
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3490
- **gentle-ai#3491** — feat(skills): a capability that decides whether a verified observation should change a future authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3491
- **gentle-ai#3530** — feat(pi): resolve and invoke the installed model-routing contract
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3530
- **gentle-ai#3550** — feat(opencode): enable background subagents by default with post-install controls
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3550
- **gentle-ai#3619** — fix(antigravity): unify global skills and MCP paths under ~/.gemini/config and update skill-registry
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3619
- **gentle-ai#3738** — bug(docs): exclude terminally approved unchanged candidates from fresh PR-readiness review
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3738
- **gentle-ai#4116** — [bug] update: 'Homebrew ownership ... is outside installed Homebrew paths' when formula symlink points outside the prefix
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4116
- **gentle-ai#4164** — feat(antigravity): unify canonical config paths and skill discovery (Phase 1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4164
- **gentle-ai#4428** — docs: quickstart and trigger-rules still name v2.6.0 as the current stable release (2.7.0)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4428
- **gentle-ai#4468** — bug(pi): `install --agent pi` writes a runtime-derived pinned duplicate of npm:gentle-engram into Pi's settings.json, and `pi remove` deletes both entries
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4468
- **gentle-ai#4786** — feat(integration): learned phase-aware model+effort router for SDD phases (external reference implementation)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4786
- **gentle-ai#4813** — bug(community-tool): injected codegraph-guidance claims the CLI auto-syncs, so CLI reads serve stale results silently
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4813
- **gentle-ai#4823** — feat(pi): support opt-in community plugin discovery and installation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4823
- **gentle-ai#4916** — docs/intended-usage.md and routing.go describe the long-session backstop with different conditions
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4916
- **gentle-ai#4934** — fix(cursor): Judgment Day does not install jd-judge or jd-fix agents
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4934
- **gentle-ai#4940** — bug(installer): post-apply verification requires V2-skipped logo files (tui.json, gentle-logo.tsx), so install can never pass on OpenCode V2
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4940
- **gentle-ai#4982** — feat(pi): phase-bound capability packs for selective per-project subagent extension
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4982
- **gentle-ai#4990** — feat(agents): add native Factory Droid adapter support
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4990
- **gentle-ai#5054** — docs(roadmap): community roadmap still sends outside contributors to #1983, closed as completed on 2026-08-30
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5054
- **gentle-ai#5066** — bug(opencode-plugin): OpenCode V2 community-plugin refusal is classified as a failed apply step, so install runs end in error and roll back
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5066
- **gentle-ai#5073** — feat(odd): critique substantial feature intent with fresh context before implementation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5073
- **gentle-ai#5082** — feat(cli): resolve multi-repository workspaces explicitly instead of git-init or refusing
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5082
- **gentle-ai#5152** — bug(pi-packages): host-provided pi-tui and typebox declared as runtime dependencies
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5152
- **gentle-ai#5168** — docs(sdd): remove retired SDD references from living docs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5168
- **gentle-ai#931** — feat(agents): Add MiniMax Code as a supported agent
  - https://github.com/Gentleman-Programming/gentle-ai/issues/931
- **gentle-ai#969** — feat(agents): add native Crush adapter support
  - https://github.com/Gentleman-Programming/gentle-ai/issues/969

### `gentle-ai` — `internal/reviewtransaction` (25 issues)

- **gentle-ai#1308** — feat(review): require candidate-bound evidence for materially distinct behavior
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1308
- **gentle-ai#1718** — fix(review): contain Unix descendants that escape the Git process group
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1718
- **gentle-ai#1720** — fix(review): anchor authority parent creation and state publication
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1720
- **gentle-ai#1763** — feat(review): require concrete defects for language-style findings
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1763
- **gentle-ai#1793** — fix(review): status cannot recover multi-lineage compact-v2 authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1793
- **gentle-ai#1869** — bug(review): valid recovery successor can block rollback to exact approved target
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1869
- **gentle-ai#1973** — feat(review): scope the RDD kill switch per worktree and announce its blast radius
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1973
- **gentle-ai#2036** — feat(review): derive required skills from the frozen candidate instead of binding them per asset
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2036
- **gentle-ai#2998** — fix(docs): rdd-shadow-evaluation.md references retired GENTLE_AI_RDD_SHADOW switch
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2998
- **gentle-ai#3370** — Canonical 4R missed a deterministic CRITICAL that a second 4R over the same code found
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3370
- **gentle-ai#3373** — Lock contention is reported as authority corruption in three places
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3373
- **gentle-ai#3669** — design(review): one store load per STATUS call — make negotiated STATUS a pure reader over the runtime's bytes
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3669
- **gentle-ai#4003** — bug(review): acknowledge-approved burn leaves the lineage's read-only candidate views with no cleanup owner
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4003
- **gentle-ai#4031** — review and issues: negotiated v2 lifecycle on Pi — 3 escalation rounds, 12 sequential lens runs, opaque admission grammar, receipt invisible after burn
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4031
- **gentle-ai#4046** — fix(review): finish root 18's representation sweep — opaque instruction handles, Git environment classes, degenerate-candidate refusal
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
- **gentle-ai#4120** — Tighten the deadcode baseline: remove clusters proven dead even from tests
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4120
- **gentle-ai#4308** — review: reviewer admission still prose-scans evidence and rejects completed inspections that honestly scope out base files
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4308
- **gentle-ai#4316** — bug(cli): review stop-hook crashes with Go runtime panic (unknown caller pc) during RDD-mode resolution on Windows
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4316
- **gentle-ai#4369** — bug(2.7.0): capture-result refuses a canonical proof path containing spaces — admission tokenizes evidence on whitespace and adjudicates the trailing fragment
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4369
- **gentle-ai#4459** — Windows: nested Gentle AI Git launch can show a console window during gentle-pi use
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4459
- **gentle-ai#4579** — bug(review): explicit lineage STATUS loses committed correction without frozen selector
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4579
- **gentle-ai#4880** — bug(review): a generated ORM migration designer consumes 99% of the lens context budget, making the authored change unreviewable
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4880
- **gentle-ai#4997** — bug(review): capture-validation derives the correction from the live worktree while STATUS uses the frozen snapshot, so a dirty reviewed path makes the reissued rctx2 handle unresolvable (3.7.0 stable)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4997
- **gentle-ai#5079** — [provider defect] Pi host relay: targeted validation result refused as not binding the provider-owned correction request (3.7.0 stable, clean worktree)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5079
- **gentle-ai#5082** — feat(cli): resolve multi-repository workspaces explicitly instead of git-init or refusing
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5082

### `gentle-shell` — `docs` (19 issues)

- **gentle-shell#1017** — Recognized global postinstall resets an explicit tuiMode:"regular" back to fullscreen on every update
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1017
- **gentle-shell#1042** — feat(skills): native selected-only skill resolution and loading
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1042
- **gentle-shell#1160** — feat(odd): derive a feature index so `odd/tasks/` never has to be read in full
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1160
- **gentle-shell#1210** — bug(shell): NaN usage only works when the custom provider id is exactly "nan"
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1210
- **gentle-shell#1235** — bug(review): in-process lens completion never sends the provider session header, so no opencode-go model can serve any reviewer role
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1235
- **gentle-shell#1245** — feat(sdd): add a documented way to remove gentle-pi-owned SDD assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1245
- **gentle-shell#1277** — bug(ask): first-party ask_user_question conflicts with @juicesharp/rpiv-ask-user-question and hard-fails Pi load
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1277
- **gentle-shell#1349** — bug(profiles): applying a newly created empty profile wipes models.json and clears every agent's routing
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1349
- **gentle-shell#1398** — bug(launcher): gentle-shell cannot find the bundled pi runtime (ERR_PACKAGE_PATH_NOT_EXPORTED)
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1398
- **gentle-shell#1442** — feat(shell): acknowledge accepted third-party usage sources
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1442
- **gentle-shell#1518** — bug(agents): receiver-side session message enters the model context with triggerTurn and no consent or sender authentication
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1518
- **gentle-shell#1524** — bug(docs): README's exact-version install pin freezes users on that release; no documented update path
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1524
- **gentle-shell#1578** — Warning del extension loader: @earendil-works/pi-tui debe ir en peerDependencies
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1578
- **gentle-shell#1583** — feat(shell): per-session statistics module — cost, tokens, time and a billable report
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1583
- **gentle-shell#1618** — bug(history): prompt history store and transcript bootstrap ignore the active agent home and always use ~/.pi/agent
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1618
- **gentle-shell#1622** — feat(agents): publish the ODD phase (with its source) in the session presence record
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1622
- **gentle-shell#1633** — Identidad de agente configurable, separada del nombre del harness (las flotas multi-agente responden todas como "el Gentleman")
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1633
- **gentle-shell#1636** — bug(review): a truncated reviewer stream fails hard with no bounded retry, and the error names the wire adapter (Anthropic), not the provider
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1636
- **gentle-shell#734** — Bug: model selected via /model is not persisted — new sessions always start with the first-ever default model
  - https://github.com/Gentleman-Programming/gentle-shell/issues/734

### `gentle-ai` — `internal/assets/skills` (16 issues)

- **gentle-ai#128** — feat(architecture): separate multi-agent and single-agent skill distribution with delegation model awareness
  - https://github.com/Gentleman-Programming/gentle-ai/issues/128
- **gentle-ai#1286** — feat(skills): add verifiable skill loading and compliance validation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1286
- **gentle-ai#1730** — fix(sdd): detect pure Engram artifact stores without hidden signals
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1730
- **gentle-ai#1842** — feat(review): expose managed/advisory RDD enforcement and install a controller contract
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1842
- **gentle-ai#1863** — feat(workflow): establish canonical workflow doctrine and exact embedded mirror
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1863
- **gentle-ai#3220** — feat(skills): let systemic-issue-triage assign cluster labels, so root classification survives the run
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3220
- **gentle-ai#3490** — docs(contributing): add a "Contributing a Skill" section built from decisions already made in closures
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3490
- **gentle-ai#3491** — feat(skills): a capability that decides whether a verified observation should change a future authority
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3491
- **gentle-ai#3738** — bug(docs): exclude terminally approved unchanged candidates from fresh PR-readiness review
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3738
- **gentle-ai#3752** — fix(issue-creation): require causal ownership before upstream reporting
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3752
- **gentle-ai#4647** — refactor(skills): single-source the 400 changed-line review budget policy
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4647
- **gentle-ai#4792** — fix(docs): concurrent review contract claims approved authority is already burned before acknowledgement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4792
- **gentle-ai#4931** — feat(skill-registry): stop instructing agents to edit project .gitignore
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4931
- **gentle-ai#4934** — fix(cursor): Judgment Day does not install jd-judge or jd-fix agents
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4934
- **gentle-ai#5018** — bug(install): OpenCode orchestrator prompt ships an ODD pointer without the Implementation Routing section
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5018
- **gentle-ai#5168** — docs(sdd): remove retired SDD references from living docs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5168

### `gentle-ai` — `internal/tui` (16 issues)

- **gentle-ai#2142** — feat(tui): Android/Termux support — termux-open-url for browser commands
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2142
- **gentle-ai#268** — fix(tui): welcome menu navigation is delayed by repeated agent detection
  - https://github.com/Gentleman-Programming/gentle-ai/issues/268
- **gentle-ai#2723** — fix(agentbuilder): preserve overwritten agents and surface incomplete installs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2723
- **gentle-ai#3003** — feat(tui): add keyboard shortcut help overlay (? key)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3003
- **gentle-ai#3053** — TUI: add a "My setup" menu entry to read back the installed configuration
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3053
- **gentle-ai#4111** — bug(tui): Upgrade Tools shows (unknown) and false 'All up to date' — 10s timeout insufficient for brew-heavy systems (2.5.0)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4111
- **gentle-ai#4183** — fix(tui): explicit Upgrade and sync is suppressed by update-check cooldown
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4183
- **gentle-ai#4397** — feat(tui): configure Pi agent model presets by subscription
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4397
- **gentle-ai#4593** — bug(tui): fresh cooldown results contradict the current release advisory
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4593
- **gentle-ai#4917** — A corrupt custom-agents.json silently drops the registry entry of a successful install
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4917
- **gentle-ai#4961** — docs: 8 references to nonexistent repo charmbracelet/textarea return 404 — the component lives at charmbracelet/bubbles/textarea
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4961
- **gentle-ai#5031** — bug(codex): the Codex home is hardcoded to ~/.codex across the integration, so CODEX_HOME is ignored everywhere except the agent-role directory
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5031
- **gentle-ai#5066** — bug(opencode-plugin): OpenCode V2 community-plugin refusal is classified as a failed apply step, so install runs end in error and roll back
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5066
- **gentle-ai#570** — feat(agents): multi-install support — discover, target, and persist per-install state
  - https://github.com/Gentleman-Programming/gentle-ai/issues/570
- **gentle-ai#869** — feat(tui): add StrictWorkflow mode — sequential PR gate and atomic commit enforcement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/869
- **gentle-ai#995** — feat(tui): add BTW OpenCode community plugin
  - https://github.com/Gentleman-Programming/gentle-ai/issues/995

### `gentle-ai` — `internal/components/sdd` (15 issues)

- **gentle-ai#1673** — fix(sync): reconcile the complete managed OpenCode plugin set
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1673
- **gentle-ai#1739** — feat: Grok CLI integration as native agent (MCP, SDD, skills, Engram, personas)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1739
- **gentle-ai#1845** — feat(agents): move agent definitions from opencode.json to agents/ markdown files
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1845
- **gentle-ai#1989** — feat(gemini): modularize GEMINI.md root to survive Antigravity 12k truncation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1989
- **gentle-ai#2197** — feat(tui): expose OpenCode native fallback agents (general/explore) in TUI model picker
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2197
- **gentle-ai#2441** — fix(review): judge and refuter agents can read live state while adjudicating a frozen candidate
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2441
- **gentle-ai#2471** — meta: the 20 roots behind ~250 open issues, and what done means
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2471
- **gentle-ai#2914** — feat(claude): configure native review subagent models and effort
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2914
- **gentle-ai#3026** — feat(opencode): add configurable reviewer and worker agents for non-SDD work
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3026
- **gentle-ai#3043** — feat(opencode): extend the SDD orchestrator with native background subagents
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3043
- **gentle-ai#3298** — bug(hooks): Codex SessionStart hook is POSIX-only and never migrates to a Windows command
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3298
- **gentle-ai#4589** — bug(claude-code): jd-fix-agent/jd-judge-a/jd-judge-b hardcode mcp__plugin_engram_engram__* prefix, unlike sdd-* agents
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4589
- **gentle-ai#4792** — fix(docs): concurrent review contract claims approved authority is already burned before acknowledgement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4792
- **gentle-ai#4928** — bug(claude): the `default` model-assignment row accepts an effort that organic delegation can never apply
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4928
- **gentle-ai#869** — feat(tui): add StrictWorkflow mode — sequential PR gate and atomic commit enforcement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/869

### `gentle-shell` — `assets` (15 issues)

- **gentle-shell#1051** — feat(sdd): coordinate classical workflow parity across Pi runtime and assets
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1051
- **gentle-shell#1085** — bug(skills): packaged gentle-ai skill contradicts the injected orchestrator contract
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1085
- **gentle-shell#1117** — feat(orchestrator): mechanical delegation-pressure guard — the long-session rule is prompt-only
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1117
- **gentle-shell#1160** — feat(odd): derive a feature index so `odd/tasks/` never has to be read in full
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1160
- **gentle-shell#1174** — bug(agents): an explicit mode:"task" still forces foreground under an enabled background-subagents policy
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1174
- **gentle-shell#1272** — bug(odd): the 400-line review budget is prose-only — agent PRs exceed it without asking
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1272
- **gentle-shell#1359** — feat(orchestrator): automatic non-blocking delegation reminders that keep inline-vs-delegate decision with the model
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1359
- **gentle-shell#1460** — feat(communication): configurable clarity layer for user-facing replies, plans, and docs
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1460
- **gentle-shell#348** — fix(orchestrator): enforce inline skill output contracts
  - https://github.com/Gentleman-Programming/gentle-shell/issues/348
- **gentle-shell#414** — feat(parity): consume upstream SDD harness-attempt correction
  - https://github.com/Gentleman-Programming/gentle-shell/issues/414
- **gentle-shell#463** — bug(orchestrator): command presence forces subagent verification for bounded checks
  - https://github.com/Gentleman-Programming/gentle-shell/issues/463
- **gentle-shell#511** — fix(orchestrator): enforce parent hot memory persistence on inline direct tasks
  - https://github.com/Gentleman-Programming/gentle-shell/issues/511
- **gentle-shell#545** — meta(backlog): causal map and execution order for Gentle Pi's open backlog
  - https://github.com/Gentleman-Programming/gentle-shell/issues/545
- **gentle-shell#59** — feat(sdd): implement project-generated TDD rubric for Pi SDD init
  - https://github.com/Gentleman-Programming/gentle-shell/issues/59
- **gentle-shell#877** — bug(orchestrator): SDD phase delegation forces foreground task mode against enabled background subagent policy
  - https://github.com/Gentleman-Programming/gentle-shell/issues/877

### `gentle-ai` — `internal/components/communitytool` (14 issues)

- **gentle-ai#1290** — feat: Android/Termux native platform support for CodeGraph
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1290
- **gentle-ai#2143** — feat(system): Android/Termux first-class platform detection + external CodeGraph support
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2143
- **gentle-ai#2146** — fix(community-tool): treat MCP initialize EOF during Pi CodeGraph sync as non-fatal pending action
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2146
- **gentle-ai#3927** — fix(guidance): injected codegraph worktree placement rule is ambiguous for nested project layouts
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3927
- **gentle-ai#4641** — RTK setup fails when adding Claude Code after a Pi-only install
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4641
- **gentle-ai#4656** — bug(community-tool): Pi CodeGraph capture builds allowed roots without the workspace, aborting install for any workspace .pi/agents child
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4656
- **gentle-ai#4691** — fix: add Kilo Code support to RTK community tool
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4691
- **gentle-ai#4794** — bug(community-tool): a CLI install de-registers Pi CodeGraph and sync can never repair it — the deleted manifest is the existence probe
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4794
- **gentle-ai#4809** — bug(pi): CodeGraph child overlay corrupts tools frontmatter into invalid YAML — Pi fails to start
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4809
- **gentle-ai#4813** — bug(community-tool): injected codegraph-guidance claims the CLI auto-syncs, so CLI reads serve stale results silently
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4813
- **gentle-ai#4982** — feat(pi): phase-bound capability packs for selective per-project subagent extension
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4982
- **gentle-ai#5119** — bug(communitytool): shell-centric CodeGraph guidance injected into bash-less Pi agents causes retry loops
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5119
- **gentle-ai#5150** — bug(community-tool): Pi is permanently reported missing — the pending adapter-health sentinel is consumed as a failed status check, so CodeGraphReconcileSatisfied() can never be true when Pi is detected
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5150
- **gentle-ai#984** — feat(community-tool): add version-aware upgrade/reconcile for CodeGraph
  - https://github.com/Gentleman-Programming/gentle-ai/issues/984

### `gentle-ai` — `internal/tui/screens` (14 issues)

- **gentle-ai#1739** — feat: Grok CLI integration as native agent (MCP, SDD, skills, Engram, personas)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1739
- **gentle-ai#2704** — feat(tui): add a screen-reader mode
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2704
- **gentle-ai#2914** — feat(claude): configure native review subagent models and effort
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2914
- **gentle-ai#3004** — feat(tui): add paging keys and position indicator to long lists
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3004
- **gentle-ai#3026** — feat(opencode): add configurable reviewer and worker agents for non-SDD work
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3026
- **gentle-ai#3053** — TUI: add a "My setup" menu entry to read back the installed configuration
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3053
- **gentle-ai#3550** — feat(opencode): enable background subagents by default with post-install controls
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3550
- **gentle-ai#4378** — bug(install): Windows compatibility skills refusal names no exit when .agents/skills is a reparse point
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4378
- **gentle-ai#4397** — feat(tui): configure Pi agent model presets by subscription
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4397
- **gentle-ai#4552** — bug(tui): Claude model picker always reopens as Custom — preset tables include "orchestrator" but persistence strips it
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4552
- **gentle-ai#4593** — bug(tui): fresh cooldown results contradict the current release advisory
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4593
- **gentle-ai#4905** — feat(tui): add provider search filter in OpenCode model picker
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4905
- **gentle-ai#4961** — docs: 8 references to nonexistent repo charmbracelet/textarea return 404 — the component lives at charmbracelet/bubbles/textarea
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4961
- **gentle-ai#869** — feat(tui): add StrictWorkflow mode — sequential PR gate and atomic commit enforcement
  - https://github.com/Gentleman-Programming/gentle-ai/issues/869

### `gentle-ai` — `internal/components/engram` (13 issues)

- **gentle-ai#1734** — feat(cli): add `gentle-ai account link` to connect a machine to an existing Engram Cloud account
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1734
- **gentle-ai#1989** — feat(gemini): modularize GEMINI.md root to survive Antigravity 12k truncation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1989
- **gentle-ai#2141** — feat(engram): Android/Termux install paths and upgrade mapping
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2141
- **gentle-ai#2762** — fix(doctor): engram:reachable false positive on opencode.json with top-level  (custom slash commands)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2762
- **gentle-ai#4164** — feat(antigravity): unify canonical config paths and skill discovery (Phase 1)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4164
- **gentle-ai#4172** — test(engram): TestStdioHandshake_GarbageOutput races the helper exit and reports broken pipe instead of invalid MCP stdout
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4172
- **gentle-ai#4201** — bug(bench): engram-download journeys j2138/j3043 flake on CI with GitHub API 403 from the shared-runner rate limit
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4201
- **gentle-ai#4834** — bug(engram): Claude Code MCP entry is written without "type": "stdio" and, on Linuxbrew, with a PATH-dependent command
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4834
- **gentle-ai#4995** — doctor: engram:reachable false positive for OpenCode configs with a top-level "command" key
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4995
- **gentle-ai#5031** — bug(codex): the Codex home is hardcoded to ~/.codex across the integration, so CODEX_HOME is ignored everywhere except the agent-role directory
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5031
- **gentle-ai#5061** — test(cli): install and sync tests inherit the host codex binary and fail when its version probe fails
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5061
- **gentle-ai#5168** — docs(sdd): remove retired SDD references from living docs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5168
- **gentle-ai#5175** — bug(engram): sync overwrites a user-customized Claude Code mcpServers.engram wrapper on every run (3.7.0)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5175

### `gentle-ai` — `internal/assets/opencode` (12 issues)

- **gentle-ai#1286** — feat(skills): add verifiable skill loading and compliance validation
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1286
- **gentle-ai#1730** — fix(sdd): detect pure Engram artifact stores without hidden signals
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1730
- **gentle-ai#1739** — feat: Grok CLI integration as native agent (MCP, SDD, skills, Engram, personas)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1739
- **gentle-ai#3026** — feat(opencode): add configurable reviewer and worker agents for non-SDD work
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3026
- **gentle-ai#3128** — fix(opencode): workspace scope installs config in an undiscoverable directory
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3128
- **gentle-ai#3550** — feat(opencode): enable background subagents by default with post-install controls
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3550
- **gentle-ai#3738** — bug(docs): exclude terminally approved unchanged candidates from fresh PR-readiness review
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3738
- **gentle-ai#4047** — feat(sddtaskresult): enforce worker-result admission and degenerate-call guards — completed-empty and endless-pending become unrepresentable
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4047
- **gentle-ai#4703** — bug(persona): "extend the existing project's language" escape hatch licenses regional register leakage into artifacts (residual of #1702)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4703
- **gentle-ai#5018** — bug(install): OpenCode orchestrator prompt ships an ODD pointer without the Implementation Routing section
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5018
- **gentle-ai#5168** — docs(sdd): remove retired SDD references from living docs
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5168
- **gentle-ai#707** — feat(opencode): show model used by background delegations
  - https://github.com/Gentleman-Programming/gentle-ai/issues/707

## Hotspot files

The directory view hides a single file carrying most of a directory's reports. Same
data, second reading.

| Repository | File | Issues | Without a band |
| --- | --- | --- | --- |
| `gentle-shell` | `extensions/gentle-ai.ts` | **51** | 36 |
| `gentle-shell` | `extensions/gentle-agents.ts` | **17** | 13 |
| `gentle-ai` | `internal/tui/model.go` | **14** | 7 |
| `gentle-shell` | `extensions/gentle-shell.ts` | **14** | 7 |
| `gentle-ai` | `docs/agents.md` | **11** | 3 |
| `gentle-ai` | `internal/cli/run.go` | **11** | 7 |
| `gentle-ai` | `internal/components/sdd/inject.go` | **11** | 5 |
| `gentle-ai` | `internal/cli/sync.go` | **10** | 5 |
| `gentle-shell` | `lib/review-host-relay.ts` | **10** | 8 |
| `engram` | `internal/store/store.go` | **9** | 0 |
| `gentle-ai` | `internal/components/communitytool/pi_codegraph.go` | **9** | 5 |
| `gentle-shell` | `assets/orchestrator-delegation.md` | **9** | 4 |

## The grey area, read through this lens

Of the **718** issues the engine leaves without a band, **251** name at least one path. Those are the ones a cluster can
reach. The rest name no path, carry no structural evidence, and **no rule reaches
them**: they need a human read or a language-model pass, and saying so is the honest
boundary of this module.

A cluster does **not** say its issues are urgent, related in cause, or worth fixing
together. It says they touch the same place, which is a fact about their text.

## What this module does NOT say

- **No priority, no severity, no ordering by importance.** The data carries no
  deterministic proxy for impact, so any band here would be invented.
- **No routing.** It does not decide which column an issue belongs to; it groups.
- **No causality.** A cluster is co-location, not a shared root cause.
- **No judgment about quality.** `veredicto_humano` stays `pendiente` for every row.

## Limits

- Paths come from a deterministic extractor over the issue text, so an issue that
  describes a location in prose without naming a path lands in no cluster.
- Only the top 15 subsystems and the top 12 files are shown with
  their issues; the counts above state what the selection covers.
- The extractor takes the first few paths per issue, so a report mentioning many files
  is attributed to the ones it names first.
- 'Without a band' is the engine's own output (`band is None`). It does not mean the
  issue is unimportant, and it is not the same as 'unrouted': routing also involves the
  board's completeness path, which this module deliberately does not read.
