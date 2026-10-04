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
- The top 10 subsystems cover **299** of the 458 issues that mention a path (65%)

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
- …and 87 more in this subsystem

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
- …and 86 more in this subsystem

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
- …and 43 more in this subsystem

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
- …and 27 more in this subsystem

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
- …and 23 more in this subsystem

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
- …and 13 more in this subsystem

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
- …and 7 more in this subsystem

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
- …and 4 more in this subsystem

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
- …and 4 more in this subsystem

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
- …and 3 more in this subsystem

## Do the clusters collapse?

A pile of reports in one directory invites the next question: is it one problem
reported many times, or many problems landing in the same place? The deterministic
answer is the evidence signatures — an exception name, an error code, a Go frame, an
exit status, a long quoted error string. Issues that share no signature are not, by
that evidence, the same problem.

| Repository | Subsystem | Issues | Carrying a signature | Distinct signatures | Largest repeated group |
| --- | --- | --- | --- | --- | --- |
| `gentle-shell` | `extensions` | 99 | 60 | **58** | 3 |
| `gentle-shell` | `lib` | 98 | 56 | **56** | — |
| `gentle-ai` | `internal/cli` | 55 | 41 | **41** | — |
| `gentle-shell` | `tests` | 39 | 18 | **18** | — |
| `gentle-ai` | `docs` | 35 | 12 | **12** | — |
| `gentle-ai` | `internal/reviewtransaction` | 25 | 17 | **17** | — |
| `gentle-shell` | `docs` | 19 | 10 | **9** | 2 |
| `gentle-ai` | `internal/assets/skills` | 16 | 6 | **6** | — |
| `gentle-ai` | `internal/tui` | 16 | 8 | **8** | — |
| `gentle-ai` | `internal/components/sdd` | 15 | 6 | **6** | — |

**Read plainly: they do not collapse.** The largest repeated group across every
cluster above is a handful of issues, so a directory carrying many reports is carrying
many *different* problems. Concentration here is **accumulation, not duplication** —
a fact about where problems land, which is why this module reports location and never
claims a shared cause.

- The one repeated signature in `gentle-shell` `extensions` is shared by 3 issues (gentle-shell#531, gentle-shell#545, gentle-shell#962); every other issue in that cluster carries evidence of its own, or none at all.
- This is **absence of evidence, not proof of distinctness**: an issue with no
  signature is uncorrelated evidence, not established as a different problem. Same for
  two issues whose signatures differ but whose cause may be one.

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
- Only the top 10 subsystems and the top 8 files are shown with
  their issues; the counts above state what the selection covers.
- The extractor takes the first few paths per issue, so a report mentioning many files
  is attributed to the ones it names first.
- 'Without a band' is the engine's own output (`band is None`). It does not mean the
  issue is unimportant, and it is not the same as 'unrouted': routing also involves the
  board's completeness path, which this module deliberately does not read.
