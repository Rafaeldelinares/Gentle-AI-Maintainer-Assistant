# Module D — Possibly Obsolete Issues

> **Read-only module.** Flags issues that reference source paths, CLI flags or symbols that no longer exist in the repository's current checkout — i.e. **possible obsolete issues**.
>
> **Nothing is closed or relabelled.** Every entry is `veredicto_humano: pendiente`.
>
> Reproduce with `python3 modules/obsolete.py` (requires the vendored checkouts under `products/`, see `sync-products.sh`).

## Summary

Two evidence classes, deliberately kept apart so the strong signal is not diluted by the weak one:

| Class | Meaning | Issues |
| --- | --- | --- |
| **A — deleted path** | The referenced path exists in this repository's git history as a deletion and is absent now. Verifiable obsolescence. | **54** |
| **B — unresolved reference** | A path, flag or symbol absent from this checkout with **no deletion record**. May belong to another repository, the installed package layout, or unlanded work. **Not** evidence of obsolescence. | 155 |

### Checked against these commits

| Repository | Commit | Tracked files | Deleted paths in history |
| --- | --- | --- | --- |
| `gentle-ai` | `9dfe17d8` | 1826 | 1252 |
| `engram` | `0f79d5e` | 555 | 276 |
| `gentle-shell` | `7a27c1c0` | 733 | 1734 |

### Class A by repository

| Repository | Issues |
| --- | --- |
| `gentle-ai` | 34 |
| `gentle-shell` | 20 |

### Most frequently referenced deleted paths

| Deleted path | Issues referencing it |
| --- | --- |
| `internal/components/sdd/inject.go` | 11 |
| `lib/sdd-preflight.ts` | 6 |
| `internal/assets/opencode/sdd-orchestrator.md` | 4 |
| `lib/opaque-pi-reviewer-adapter.ts` | 4 |
| `assets/sdd-orchestrator-workflow.md` | 3 |
| `tests/sdd-agent-tools.test.ts` | 3 |
| `internal/assets/skills/_shared/sdd-status-contract.md` | 2 |
| `internal/components/sdd/boundedreview.go` | 2 |
| `internal/components/communitytool/rtk_runtime.go` | 2 |
| `internal/assets/skills/_shared/sdd-phase-common.md` | 2 |
| `internal/sddstatus/status.go` | 2 |
| `internal/assets/opencode/commands/sdd-status.md` | 2 |
| `internal/components/sdd/profiles.go` | 2 |
| `lib/openspec-deltas.ts` | 2 |
| `assets/chains/sdd-full.chain.md` | 2 |

## Class A — issues referencing a deleted path (up to 15 per repository)

These are the actionable rows. Each cites the deleted path, the sentence, the repository and the commit. A maintainer must confirm the issue is indeed obsolete before closing anything.

### `gentle-ai` — 34 issues (checked at `9dfe17d8`)

- **gentle-ai#707** — feat(opencode): show model used by background delegations
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/707
  - `internal/assets/opencode/plugins/background-agents.ts` — path was deleted in this repository's history
    - Evidence: ": - The model already appears to be resolved in `internal/assets/opencode/plugins/background-agents.ts` via `resolveAgentModel(...)`. - The resolved mod"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#869** — feat(tui): add StrictWorkflow mode — sequential PR gate and atomic commit enforcement
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/869
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "ScreenStrictWorkflow → ScreenDependencyTree` | | `internal/components/sdd/inject.go` | Inject skill + write flag when enabled | | `sk"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1286** — feat(skills): add verifiable skill loading and compliance validation
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1286
  - `internal/assets/opencode/sdd-orchestrator.md` — path was deleted in this repository's history
    - Evidence: "ndexes only skill name, description, and path. - `internal/assets/opencode/sdd-orchestrator.md` treats `paths-injected` as “all good”. - The aut"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1673** — fix(sync): reconcile the complete managed OpenCode plugin set
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1673
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "`` ### Additional Context Affected symbols: - `internal/components/sdd/inject.go`: `ManagedOpenCodePluginNames`, `RefreshInstalled"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1730** — fix(sdd): detect pure Engram artifact stores without hidden signals
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1730
  - `internal/sddstatus/status.go` — path was deleted in this repository's history
    - Evidence: "``` ### Additional Context Exact locations: - `internal/sddstatus/status.go:256-275` calls the Engram fallback when OpenSpec"
  - `internal/assets/skills/_shared/sdd-status-contract.md` — path was deleted in this repository's history
    - Evidence: "defines the three hidden eligibility signals. - `internal/assets/skills/_shared/sdd-status-contract.md:18-19` incorrectly describes the native dispatche"
  - `internal/assets/opencode/commands/sdd-status.md` — path was deleted in this repository's history
    - Evidence: "cribes the native dispatcher as OpenSpec-only. - `internal/assets/opencode/commands/sdd-status.md:20` and `sdd-continue.md:13` prohibit native Engr"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1739** — feat: Grok CLI integration as native agent (MCP, SDD, skills, Engram, personas)
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1739
  - `internal/components/sdd/profiles.go` — path was deleted in this repository's history
    - Evidence: "cks, idempotent | | **SDD Profile Generation** | `internal/components/sdd/profiles.go` | Per-phase model assignments | | **SDD Config I"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1845** — feat(agents): move agent definitions from opencode.json to agents/ markdown files
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1845
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "ed by merging overlay JSON into `opencode.json` (`internal/components/sdd/inject.go` + `opencode/sdd-overlay-*.json`). The OpenCode a"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#1989** — feat(gemini): modularize GEMINI.md root to survive Antigravity 12k truncation
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1989
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "route protocol to reference file via bootstrap - `internal/components/sdd/inject.go` — add bootstrap + sdd-stub blocks - `internal/co"
  - `internal/components/sdd/triggerrules.go` — path was deleted in this repository's history
    - Evidence: "d/inject.go` — add bootstrap + sdd-stub blocks - `internal/components/sdd/triggerrules.go` — stays inline (unchanged) - `internal/cli/sync."
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#2123** — feat(sync): preserve user customizations in managed agent instruction files during sync
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2123
  - `internal/agentbuilder/sdd.go` — path was deleted in this repository's history
    - Evidence: "agent builder's `custom-agent:<name>` markers in `internal/agentbuilder/sdd.go`). 2. If the marker is absent → clean injection,"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#2197** — feat(tui): expose OpenCode native fallback agents (general/explore) in TUI model picker
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2197
  - `internal/components/sdd/profiles.go` — path was deleted in this repository's history
    - Evidence: "viders/models for `general` and `explore`. 3. In `internal/components/sdd/profiles.go`, respect user-configured TUI model assignments f"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#2441** — fix(review): judge and refuter agents can read live state while adjudicating a frozen candidate
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2441
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "r holds `read: true` with no permission block** (`internal/components/sdd/inject.go:972`, byte-identical before and after #2417). It"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#2471** — meta: the 20 roots behind ~250 open issues, and what done means
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2471
  - `internal/advisoryreview/contract.go` — path was deleted in this repository's history
    - Evidence: "aude Code, OpenCode and Codex ride one solution (`internal/advisoryreview/contract.go:31-33`) and eligibility is computed from the comp"
  - `internal/components/sdd/boundedreview.go` — path was deleted in this repository's history
    - Evidence: "ed in embedded `skills/_shared/` and consumed by `internal/components/sdd/boundedreview.go:12`. ### Tier 2 - [ ] **7. A terminal carries n"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#2914** — feat(claude): configure native review subagent models and effort
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2914
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "_MODEL}}` and `{{CLAUDE_EFFORT_FRONTMATTER}}`. - `internal/components/sdd/inject.go` - Claude assignment resolution derives the key"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#3026** — feat(opencode): add configurable reviewer and worker agents for non-SDD work
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3026
  - `internal/assets/opencode/sdd-orchestrator.md` — path was deleted in this repository's history
    - Evidence: "ssets/opencode/sdd-overlay-{single,multi}.json`, `internal/assets/opencode/sdd-orchestrator.md`, `internal/components/sdd/inject.go`, `internal/"
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "`internal/assets/opencode/sdd-orchestrator.md`, `internal/components/sdd/inject.go`, `internal/cli/run_component_paths_test.go`, `in"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-ai#3043** — feat(opencode): extend the SDD orchestrator with native background subagents
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3043
  - `internal/components/sdd/inject.go` — path was deleted in this repository's history
    - Evidence: "ed-background path. ### 📎 Additional Context - `internal/components/sdd/inject.go:sddOrchestratorAsset()` currently selects complet"
  - **posible, requiere verificación** — veredicto_humano: pendiente

### `engram` — 0 issues (checked at `0f79d5e`)

_None._

### `gentle-shell` — 20 issues (checked at `7a27c1c0`)

- **gentle-shell#59** — feat(sdd): implement project-generated TDD rubric for Pi SDD init
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/59
  - `extensions/sdd-init.ts` — path was deleted in this repository's history
    - Evidence: "ent the Pi-specific side of that feature. Today, `extensions/sdd-init.ts` resolves Strict TDD too coarsely: ```ts const s"
  - `assets/agents/sdd-apply.md` — path was deleted in this repository's history
    - Evidence: "nsions/sdd-init.ts` - `assets/orchestrator.md` - `assets/agents/sdd-apply.md` - `assets/agents/sdd-verify.md` - `assets/suppor"
  - `assets/agents/sdd-verify.md` — path was deleted in this repository's history
    - Evidence: "rchestrator.md` - `assets/agents/sdd-apply.md` - `assets/agents/sdd-verify.md` - `assets/support/strict-tdd.md` - `assets/suppo"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#414** — feat(parity): consume upstream SDD harness-attempt correction
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/414
  - `assets/sdd-orchestrator-workflow.md` — path was deleted in this repository's history
    - Evidence: "y mirrors the orchestration contract through: - `assets/sdd-orchestrator-workflow.md`; - `assets/support/sdd-status-contract.md`; - `t"
  - `assets/support/sdd-status-contract.md` — path was deleted in this repository's history
    - Evidence: "ugh: - `assets/sdd-orchestrator-workflow.md`; - `assets/support/sdd-status-contract.md`; - `tests/native-sdd-attempt-authority.test.ts`."
  - `tests/native-sdd-attempt-authority.test.ts` — path was deleted in this repository's history
    - Evidence: "d`; - `assets/support/sdd-status-contract.md`; - `tests/native-sdd-attempt-authority.test.ts`. The existing gentle-pi test verifies contract"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#463** — bug(orchestrator): command presence forces subagent verification for bounded checks
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/463
  - `tests/sdd-agent-tools.test.ts` — path was deleted in this repository's history
    - Evidence: "ry route; - `tests/package-manifest.test.ts` and `tests/sdd-agent-tools.test.ts` pin that routing contract; - the extension rende"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#593** — bug(agents): SDD child sessions lose mem_* tools because the engram extension is never provisioned
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/593
  - `tests/sdd-agent-tools.test.ts` — path was deleted in this repository's history
    - Evidence: "ools), - and pin whichever contract is chosen in `tests/sdd-agent-tools.test.ts`. When a declared-but-unprovisioned tool is reje"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#597** — bug(review): RENAMED arrow headings are double-counted in native line budgets
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/597
  - `lib/openspec-deltas.ts` — path was deleted in this repository's history
    - Evidence: "w-snapshot.ts` — snapshot diff-line derivation - `lib/openspec-deltas.ts` — supported delta headings - `assets/agents/sdd-"
  - `assets/agents/sdd-spec.md` — path was deleted in this repository's history
    - Evidence: "openspec-deltas.ts` — supported delta headings - `assets/agents/sdd-spec.md` — current `RENAMED` support policy The exact do"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#608** — bug(assets): orphaned global SDD agents never refresh and are invisible to drift after pre-legacy-manifest upg
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/608
  - `lib/sdd-preflight.ts` — path was deleted in this repository's history
    - Evidence: "st hash does not match the pre-injection content (lib/sdd-preflight.ts:500). On that branch the file is still written an"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#681** — bug(review): opaque Pi reviewer inherits placeholder ANTHROPIC_API_KEY from session env → 401 invalid x-api-ke
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/681
  - `lib/opaque-pi-reviewer-adapter.ts` — path was deleted in this repository's history
    - Evidence: "with `env: options.environment ?? process.env` (`lib/opaque-pi-reviewer-adapter.ts`). The session env carries a harness-injected pla"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#757** — bug(review): opaque Pi reviewer freezes --no-extensions, unloading the extension that provides the selected mo
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/757
  - `lib/opaque-pi-reviewer-adapter.ts` — path was deleted in this repository's history
    - Evidence: "data. ### Problem `OPAQUE_PI_REVIEWER_ARGV` in `lib/opaque-pi-reviewer-adapter.ts` freezes `--no-extensions` into the reviewer argv"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#865** — Review orchestration spec still requires retired review-refuter agent
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/865
  - `lib/sdd-preflight.ts` — path was deleted in this repository's history
    - Evidence: "4–92. 2. Compare it with the retirement logic in `lib/sdd-preflight.ts`. 3. Compare it with the native capture roles in"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#877** — bug(orchestrator): SDD phase delegation forces foreground task mode against enabled background subagent policy
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/877
  - `assets/sdd-orchestrator-workflow.md` — path was deleted in this repository's history
    - Evidence: "human asked to wait. But the SDD workflow asset (assets/sdd-orchestrator-workflow.md, "SDD Phase Delegation Mode" section) says: > La"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#956** — bug(agents): model routing breaks block scalar descriptions and empties them
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/956
  - `lib/sdd-preflight.ts` — path was deleted in this repository's history
    - Evidence: "fter it. The same logic existed a second time in `lib/sdd-preflight.ts` as `updateAgentFrontmatterRouting`. The trigger"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#1022** — bug(sdd-status): Pi-side reportIsClearlyPassing cannot read v2 pass_with_warnings envelopes, permanently block
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/1022
  - `lib/sdd-status.ts` — path was deleted in this repository's history
    - Evidence: "reportIsClearlyPassing()` (installed Pi package, `lib/sdd-status.ts`) make a passing v2 report unreadable to that eng"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#1033** — bug(sdd): fresh OpenSpec research locator rejected outside exact scope
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/1033
  - `assets/chains/sdd-full.chain.md` — path was deleted in this repository's history
    - Evidence: "ontains incompatible artifact-name contracts: - `assets/chains/sdd-full.chain.md:25` declares the `sdd-explore` output as `explora"
  - `lib/sdd-research-capabilities.ts` — path was deleted in this repository's history
    - Evidence: "es `openspec/changes/<change>/exploration.md`. - `lib/sdd-research-capabilities.ts:138-143` accepts the artifact token `explore` and"
  - `tests/sdd-research-capabilities.test.ts` — path was deleted in this repository's history
    - Evidence: "uiring `openspec/changes/<change>/explore.md`. - `tests/sdd-research-capabilities.test.ts:151` explicitly codifies `explore.md`. - `extensi"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#1044** — Engram tools are never detected when the MCP adapter prefixes tool names (hybrid preflight unreachable + SDD a
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/1044
  - `lib/sdd-preflight.ts` — path was deleted in this repository's history
    - Evidence: "t the adapter registers prefixed names: ```ts // lib/sdd-preflight.ts:876-894 (duplicated at extensions/gentle-ai.ts:18"
  - **posible, requiere verificación** — veredicto_humano: pendiente
- **gentle-shell#1051** — feat(sdd): coordinate classical workflow parity across Pi runtime and assets
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/1051
  - `assets/sdd-orchestrator-workflow.md` — path was deleted in this repository's history
    - Evidence: "l failure/task truth and archive reports. Update `assets/sdd-orchestrator-workflow.md`, `assets/chains/sdd-full.chain.md`, `assets/chai"
  - `assets/chains/sdd-full.chain.md` — path was deleted in this repository's history
    - Evidence: "s. Update `assets/sdd-orchestrator-workflow.md`, `assets/chains/sdd-full.chain.md`, `assets/chains/sdd-verify.chain.md`, `assets/ag"
  - `assets/chains/sdd-verify.chain.md` — path was deleted in this repository's history
    - Evidence: "workflow.md`, `assets/chains/sdd-full.chain.md`, `assets/chains/sdd-verify.chain.md`, `assets/agents/sdd-apply.md`, `assets/agents/sd"
  - `assets/agents/sdd-apply.md` — path was deleted in this repository's history
    - Evidence: ".chain.md`, `assets/chains/sdd-verify.chain.md`, `assets/agents/sdd-apply.md`, `assets/agents/sdd-verify.md`, `assets/agents/s"
  - `assets/agents/sdd-verify.md` — path was deleted in this repository's history
    - Evidence: "-verify.chain.md`, `assets/agents/sdd-apply.md`, `assets/agents/sdd-verify.md`, `assets/agents/sdd-sync.md`, `assets/agents/sdd"
  - **posible, requiere verificación** — veredicto_humano: pendiente

## Class B — unresolved references (weak evidence, up to 8 per repository)

**These are not obsolescence claims.** They are references this checkout does not contain; most belong to another repository or to the installed package layout. The section exists so the signal is visible without being mistaken for proof.

### `gentle-ai` — 78 issues (checked at `9dfe17d8`)

- **gentle-ai#570** — feat(agents): multi-install support — discover, target, and persist per-install state
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/570
  - Unresolved: `internal/state/installs_test.go`, `internal/tui/install_targets_test.go`, `internal/cli/per_install_state_test.go`
  - veredicto_humano: pendiente
- **gentle-ai#705** — feat(runtime): add cross-agent token accounting via tool
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/705
  - Unresolved: `get_token_usage`
  - veredicto_humano: pendiente
- **gentle-ai#707** — feat(opencode): show model used by background delegations
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/707
  - Unresolved: `delegation_list`, `delegation_read`
  - veredicto_humano: pendiente
- **gentle-ai#713** — feat(skills): workflow-governance skill + Workflow agent() governance bridge for ultracode
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/713
  - Unresolved: `assets/governance-preamble.js`, `internal/assets/claude/sdd-orchestrator.md`
  - veredicto_humano: pendiente
- **gentle-ai#720** — Claude Code adapter: option to avoid CLAUDE.md section duplication when content is also provided via
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/720
  - Unresolved: `--no-embed`, `--import-only`
  - veredicto_humano: pendiente
- **gentle-ai#743** — feat(skill-registry): index installed plugin skills and generate a companion agent-registry
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/743
  - Unresolved: `--with-agents`
  - veredicto_humano: pendiente
- **gentle-ai#869** — feat(tui): add StrictWorkflow mode — sequential PR gate and atomic commit enforcement
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/869
  - Unresolved: `skills/sequential-branches/SKILL.md`, `internal/tui/screens/strict_workflow.go`
  - veredicto_humano: pendiente
- **gentle-ai#927** — feat(ci): distribute gentle-ai via winget for Windows install and upgrade
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/927
  - Unresolved: `.github/workflows/winget.yml`
  - veredicto_humano: pendiente

### `engram` — 7 issues (checked at `0f79d5e`)

- **engram#201** — security(sync): make Git-based memory sync safer by default, especially for prompts
  - Link: https://github.com/Gentleman-Programming/engram/issues/201
  - Unresolved: `--no-prompts`, `--exclude-prompts`
  - veredicto_humano: pendiente
- **engram#233** — Add semantic search layer on top of FTS5 to improve mem_search recall
  - Link: https://github.com/Gentleman-Programming/engram/issues/233
  - Unresolved: `--semantic-weight`
  - veredicto_humano: pendiente
- **engram#242** — feat(store): add atomic mem_consolidate tool for memory garbage collection
  - Link: https://github.com/Gentleman-Programming/engram/issues/242
  - Unresolved: `Store.Consolidate`
  - veredicto_humano: pendiente
- **engram#1078** — feat(ci): token budget ratchet — first slice over agent eager schemas and server instructions
  - Link: https://github.com/Gentleman-Programming/engram/issues/1078
  - Unresolved: `internal/mcp/testdata/token_budgets.json`
  - veredicto_humano: pendiente
- **engram#1407** — feat(sync): opt-in personal-scope export for `engram sync --project`
  - Link: https://github.com/Gentleman-Programming/engram/issues/1407
  - Unresolved: `--include-personal`
  - veredicto_humano: pendiente
- **engram#1533** — Pi plugin: memory protocol is lost on turns started without before_agent_start (breaks pi-claude-bri
  - Link: https://github.com/Gentleman-Programming/engram/issues/1533
  - Unresolved: `extensions/runner.js`
  - veredicto_humano: pendiente
- **engram#1582** — feat(cloud): add managed project API (POST /admin/projects) and local deployment tooling
  - Link: https://github.com/Gentleman-Programming/engram/issues/1582
  - Unresolved: `docs/engram-cloud/prod-local.md`
  - veredicto_humano: pendiente

### `gentle-shell` — 70 issues (checked at `7a27c1c0`)

- **gentle-shell#59** — feat(sdd): implement project-generated TDD rubric for Pi SDD init
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/59
  - Unresolved: `assets/support/tdd-rubric-template.md`
  - veredicto_humano: pendiente
- **gentle-shell#116** — feat: Add OpenCode MCP Bridge with Antigravity IDE error handling
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/116
  - Unresolved: `readOpenCodeConfig`, `detectCodeGraphServer`, `prePopulateCodeGraphState`, `interceptCodeGraphError`
  - veredicto_humano: pendiente
- **gentle-shell#327** — bug(agents): builtin agent source is permanently empty — builtinAgentDirs probes agents/ directories
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/327
  - Unresolved: `listBuiltinAgentNames`, `listBuiltinAgentNamesAsync`
  - veredicto_humano: pendiente
- **gentle-shell#347** — feat(pi): add an explicit session switch to a validated linked worktree
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/347
  - Unresolved: `SessionManager.forkFrom`
  - veredicto_humano: pendiente
- **gentle-shell#414** — feat(parity): consume upstream SDD harness-attempt correction
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/414
  - Unresolved: `internal/sddstatus/status.go`
  - veredicto_humano: pendiente
- **gentle-shell#440** — feat(runtime): add authoritative managed-task registry
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/440
  - Unresolved: `getSnapshot`
  - veredicto_humano: pendiente
- **gentle-shell#444** — feat(runtime): add isolated Pi AgentSession adapter
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/444
  - Unresolved: `extensions/agent-runtime.ts`, `AgentSession.subscribe`, `session.getActiveToolNames`
  - veredicto_humano: pendiente
- **gentle-shell#446** — feat(runtime): execute one prepared foreground Pi task through the authoritative registry
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/446
  - Unresolved: `session.subscribe`
  - veredicto_humano: pendiente

## Limits

- **Class A is verifiable but still needs human judgment**: an issue can deliberately discuss code that was removed, or the removal may be unrelated to the issue's request.
- **Class B is not evidence of obsolescence.** It exists because the absence of a reference is worth seeing, not because it proves anything. A path in the installed package layout (`assets/...`) or another repository naturally does not appear in this checkout.
- The check runs against the vendored commit listed above, not the live default branch. Re-run `./sync-products.sh` then this module to refresh.
- Flags and symbols are matched as substrings anywhere in tracked source, so a token that survives only in tests or docs resolves and is not reported (under-reporting, by design).
- Only repo-relative paths under plausible source roots are checked; user paths, URLs and prose are ignored.
- The module never closes, relabels or comments on anything.
