# Phase 1 — Ecosystem Inspection (Factual Findings)

> Status: **pre-approval analysis**. No production code, no APIs, no schemas, no automation.
> This document records what the ecosystem **is**, verified by reading source and docs.
> It makes no design decisions. Design lives in later phases.

## Provenance

| Repository | Revision inspected | Branch |
| --- | --- | --- |
| `gentle-ai` | `014750fe` (merge of PR #2742) | `main` |
| `engram` | `854fd41` | `fix/autosync-pull-non-enrolled-mutations` |
| `gentle-shell` | default branch, read via GitHub REST API (2026-10-01) | `main` |
| `Gentle-AI-Maintainer-Assistant` | `1028ea1` | `main` |

Method: three read-only reconnaissance passes (one per target repository), the GitHub REST API for
`gentle-shell` (whose local clone is stale), plus direct filesystem inspection of the workspace.
Claims below are marked as they were verified:
**[V]** verified by reading source/docs, **[A]** verified absent by search, **[?]** undetermined.

---

## 0. Workspace state

**[V]** The assistant repository contains only `AGENTS.md` (scaffolding stub, 4 lines),
`.gitignore`, `.git/`, and `.atl/`. There is no `docs/`, no `schemas/`, no `prompts/`, no source.

**[V]** `docs/` was created by this phase document. It is the first artifact in the repo.

**[?]** `AGENTS.md` on disk does **not** contain the Initial Development Protocol (Phases 0–7)
that the maintainer supplied. The governing protocol currently lives only in the conversation.
This is an open decision (see §7, Q1).

---

## 1. Target repository: `gentle-ai`

### 1.1 What it is

**[V]** A Go CLI + Bubbletea TUI that **configures the AI coding agents already installed** on a
machine. It is an *ecosystem configurator*: it injects prompts, skills, MCP entries, permissions,
personas, and memory wiring into agent runtimes. It does **not** run an agent, host a model, or
serve traffic. (`docs/CODEBASE-GUIDE.md`, `docs/architecture.md`)

Module: `github.com/gentleman-programming/gentle-ai/v2`.

### 1.2 Layout ownership

**[V]** `cmd/gentle-ai/main.go` is a thin entry point; all logic is under `internal/`:
`app/` (dispatch), `agents/` (16 agent adapters), `catalog/` (declarative registries),
`components/` (injection + verification per subsystem), `cli/`, `model/`, `pipeline/`,
`planner/`, `sddstatus/`, `reviewtransaction/`, `tui/`.

**[V]** `contracts/` holds **versioned JSON Schemas and fixtures** for integration protocols
(`review-integration/v1`, `v2`, `sdd-integration`). This is the repository's existing precedent
for schema-first design.

**[V]** `openspec/` holds architectural specifications and in-flight changes.
`bench/` is an independent Go module driving the compiled binary across scripted journeys.

### 1.3 Surfaces

**[V]** CLI (custom routing, no Cobra/Urfave): `install`, `uninstall`, `sync`, `restore`, `update`,
`upgrade`, `doctor`, `skill-registry`, `codegraph init`, `sdd-status`, `sdd-continue`, `sdd-attempt`,
`sdd-verify-validate`, `review mode`, and a large `review` facade (start, status, capture-*,
inspect-*, finalize, validate, repair, abandon, recover, reclaim, …).

**[A]** No `issue`, `triage`, or GitHub command exists in the CLI.

**[V]** MCP: gentle-ai **configures** MCP servers in other agents; it **does not expose** one.
It wires three: Engram (`engram mcp --tools=agent`), Context7, and CodeGraph (`codegraph serve --mcp`).

**[A]** No HTTP server, no daemon, no listener anywhere in the binary.

### 1.4 Agent / skill / persona mechanisms

**[V]** 16 supported agents; 4 persona modes (`gentleman`, `gentleman-neutral-artifacts`, `neutral`,
`custom`) injected via markers into agent instruction files.

**[V]** Subagent role definitions live as assets: SDD phases (`sdd-*`), Judgment Day
(`jd-judge-a`, `jd-judge-b`, `jd-fix-agent`), review lenses (`review-risk`, `review-resilience`,
`review-readability`, `review-reliability`, `review-refuter`).

**[V]** `skills/` holds 12 canonical Markdown skills with YAML frontmatter, delivered to agents.

**[V]** Model assignments are tracked in `~/.gentle-ai/state.json` per agent/per phase.

### 1.5 RDD / review authority (structural only)

**[V]** RDD is a gatekeeping framework bound to **Git tree hashes**: a `lineage` is a durable
transaction id; a `receipt` is a content-bound proof over frozen trees; lenses (Risk, Resilience,
Readability, Reliability) run only on frozen candidate trees; `validate --gate` checks
`pre-commit`/`pre-push`/`pre-pr`/`archive`.

**[V]** The review state engine (`internal/reviewtransaction/`, `contracts/review-integration/`)
has **no primitives for issues, discussions, or classification**. It is structurally
issue-agnostic. It is **not** reusable for issue triage as-is.

### 1.6 Issue-related capability that already exists

**[V]** Three skills exist and matter to this project:

| Skill | What it actually is | Inputs | Outputs | Automates GitHub? |
| --- | --- | --- | --- | --- |
| `systemic-issue-triage` | Prose procedure: bucket issues by **root class A–E** (superseded / duplicate-of-class / new bug cluster / feature / unclear); fix by shrinking the system | issue texts, `origin/main` code | triage report + fix-batch plan with test evidence and net line delta | **No** |
| `issue-root-resolution` | Prose procedure: build a read-only **mechanism map** (file:line), group issues under verified roots, rank deletion-first fixes, evidence-gated closures | full issue bodies **and comments**, `origin/main` code | mechanism map, roots table, ranking, closures table, maintainer choices | **No** |
| `issue-creation` | Prose procedure + templates: sanitize private data, match repo issue form, emit an example `gh issue create` string | bug/feature details, environment | structured issue body + privacy-sanitized text + example command | **No** (documents the command only) |

**[V]** All three are *prompts/procedures executed by an interactive agent under human direction*.
None contains code, none calls the GitHub API, none is triggered by a workflow.

### 1.7 GitHub conventions in `gentle-ai`

**[V]** Blank issues are disabled (`config.yml`).

**[V]** `bug_report.yml` auto-applies `["bug", "status:needs-review"]`.
`feature_request.yml` auto-applies `["enhancement", "status:needs-review"]`.

**[V]** PR template requires a closing keyword (`Closes`/`Fixes`/`Resolves #N`) and exactly one
`type:*` label. `size:exception` authorizes a PR over 400 lines.

**[V]** CI (`pr-check.yml`) enforces: PR ≤ 400 changed lines unless `size:exception`; a visible
closing issue reference; **every linked issue must carry `status:approved`**; exactly one `type:*` label.

**[V]** `ci.yml` runs gofmt check, unit tests, the bench module, a deadcode ratchet, cross-platform
runs, Docker E2E. Other workflows: release (GoReleaser + minisign), RC promotion, Discord notify.

**[A]** No workflow auto-assigns, auto-closes, auto-labels-incoming, or bot-comments issues.

### 1.8 Automation gaps

**[A]** No GitHub client library (`octokit`, `go-github`) anywhere.
**[A]** No issue fetching/ingestion (no API call, no `gh`-driven ingestion code).
**[A]** No classification, clustering, or deduplication engine.
**[A]** No issue store, cache, or state machine.
**[A]** No triage bot.

**[V]** Historical issue reports exist as *documents*, not code:
`docs/architecture/rdd-backlog-disposition.md` buckets 333 legacy issues/PRs into 5 dispositions;
`docs/releases/v2.2.0-closure-ledger.md` records closure rationale.

### 1.9 Runtime dependencies assumed

**[V]** `git` (mandatory), `gh` CLI (used throughout skills and release scripts),
`GITHUB_TOKEN` (CI), and managed binaries `engram`, `gga`, `codegraph`, plus platform package
managers. Auth is delegated to `gh auth login` / git credentials — gentle-ai stores no tokens.

---

## 2. Target repository: `engram`

### 2.1 What it is

**[V]** A single Go binary providing persistent memory for AI agents: SQLite + FTS5, exposed through
**CLI, local HTTP API, MCP (stdio), and a Bubbletea TUI**, plus opt-in cloud replication.

### 2.2 Storage and data model

**[V]** Core tables: `sessions`, `observations`, `observations_fts`, `user_prompts`,
`prompts_fts`, `memory_relations`, and a family of `sync_*` / tombstone tables.

**[V]** `observations` carries `sync_id`, `session_id`, `type`, `title`, `content`, `project`
(string), `scope` (`project|personal|global`), `topic_key`, `normalized_hash`, `revision_count`,
`duplicate_count`, `pinned`, `review_after`, `expires_at`, soft-delete `deleted_at`.

**[V]** FTS5 uses the `trigram` tokenizer (terms < 3 runes fall back to `LIKE`). Ranking is
BM25 weighted (title 10, topic_key 5, content 1) plus pinned/recency/stability boosts.

**[V]** There is **no `projects` table** — project is a free string on each row.

**[V]** `memory_relations` links **two observations** (`source_id`, `target_id` as `sync_id`) with
verbs `conflicts_with`, `supersedes`, `scoped`, `related`, `compatible`, `not_conflict`, plus
`judgment_status`, `confidence`, `reason`, `evidence`, and actor/model provenance.

**[A]** There is **no `issues` table, no issue column, and no entity linking an observation to a
GitHub issue or PR.** Relations connect memories to memories only.

### 2.3 Surfaces

**[V]** **MCP**: 23 tools, **stdio only**, implemented in `internal/mcp/mcp.go`, started by
`engram mcp`. Tool profiles: `all` (23), `agent` (19; excludes `mem_delete`, `mem_stats`,
`mem_timeline`, `mem_merge_projects`), `admin` (those 4).

Tool names: `mem_save`, `mem_search`, `mem_context`, `mem_get_observation`, `mem_save_prompt`,
`mem_session_summary`, `mem_update`, `mem_delete`, `mem_suggest_topic_key`, `mem_timeline`,
`mem_stats`, `mem_session_start`, `mem_session_end`, `mem_capture_passive`, `mem_current_project`,
`mem_list_projects`, `mem_doctor`, `mem_review`, `mem_pin`, `mem_unpin`, `mem_judge`, `mem_compare`,
`mem_merge_projects`.

**[V]** **Local HTTP API**: `engram serve`, `127.0.0.1:7437` or a Unix socket. Routes cover
`/health`, `/sessions*`, `/observations*`, `/search`, `/context*`, `/timeline`, `/review*`,
`/prompts*`, `/conflicts*`, `/projects*`, `/stats`, `/doctor`, `/export`, `/import`, `/sync/status`.
Auth via `ENGRAM_HTTP_TOKEN` (open when unset).

**[V]** **Cloud**: `engram cloud serve` adds `/sync/*`, `/admin/*`, `/dashboard/*` on PostgreSQL,
with bearer tokens, project grants, per-project pause, JSONL/gzip chunk sync, and a background
autosync worker under a SQLite lease.

**[V]** **CLI**: `serve`, `mcp`, `tui`, `test`, `search`, `save`, `delete`, `timeline`, `conflicts`,
`doctor`, `context`, `stats`, `export`, `import`, `init`, `projects`, `setup`, `protocol-mode`,
`sync`, `cloud`, `obsidian-export`, `instance-id`, `version`, `help`.

### 2.4 Integration model for a third-party tool

**[V]** Documented channels: **MCP stdio** (for agents), **local HTTP REST** (for external
programs, plugins, hooks), **CLI subprocess** (for scripts).

**[A]** **Go library import is impossible**: every core package is under `internal/`, which the Go
compiler forbids external modules from importing. Any consumer must use MCP, HTTP, or CLI.

### 2.5 Sync constraints a consumer must respect

**[V]** Local SQLite is the authority; cloud is opt-in replication.
**[V]** A project must be explicitly enrolled (`engram cloud enroll`) before its mutations can push.
**[V]** Un-enrolled projects with pending mutations put autosync into a loud **blocked** state
(no silent drops).
**[V]** `pinned` and `review_after` are local-only and never synced.
**[V]** Plugins are thin adapters by policy: memory semantics stay in Go.

### 2.6 Issue-related capability that already exists

**[V]** `skills/backlog-triage/SKILL.md` is an interactive maintainer protocol: fetch open issues
and PRs as JSON via `gh`, then classify each into exactly one disposition —
`MERGE`, `REQUEST CHANGES`, `CLOSE`, `NEEDS DESIGN`, `APPROVE ISSUE`, `REJECT ISSUE` — infer
maintainer philosophy from `MEMBER`/`OWNER` comments, and emit a Markdown report with a metric
summary, triage tables, pre-drafted comment templates, and recommended `gh` commands.

**[A]** It automates nothing: no triggers, no daemon, no webhook, no auto-labeling.

### 2.7 GitHub conventions in `engram`

**[V]** `.github/labels.yml` defines the label policy:
`type:*` (bug, feature, question, docs, refactor, chore, breaking-change — required singleton on PRs);
`status:*` (needs-review, approved, in-progress, blocked, stale, wontfix, possible-duplicate);
`resolution:duplicate`; `priority:*` (critical/high/medium/low); `effort:*` (small/medium/large);
plus `good first issue`, `help wanted`, `size:exception`.

**[V]** Issue forms: `bug_report.yml`, `feature_request.yml`, `docs_improvement.yml`,
`tracked_question.yml` — each auto-applies its `type:*` plus `status:needs-review`; blank issues disabled.

**[V]** Workflows: `ci.yml` (golangci-lint, templ generation check, deadcode ratchet, tests, e2e,
Windows suites, plugin tests, perf ratchet), `pr-check.yml` (closing reference **and**
`status:approved` on linked issues), `pr-label-check.yml` (exactly one `type:*`),
`stale.yml` (30 days → `status:stale`, +14 days → close; exempts `status:approved`,
`status:in-progress`, `priority:high`, `priority:critical`), plus release/cloud/publish workflows.

**[A]** No automated triage, clustering, or duplicate detection exists in the workflows.

---

## 3. Target repository: `gentle-shell`

**[V]** A real, public, actively developed repository: `Gentleman-Programming/gentle-shell`, MIT,
1,159 stars, created 2026-05-10, last push 2026-10-01. Issues enabled. **It is a first-class
system of the ecosystem, independent of `gentle-ai` and `engram`.**

**[V]** It is a TypeScript / pnpm workspace delivering the Pi-native harness published on npm as
`gentle-pi`. Repository description: *"Gentle Shell is a Pi-native coding-agent harness for
controlled development with Organic Driven Development, optional SDD/OpenSpec, subagents, TDD
evidence, review guardrails, skills, and memory integrations."*

**[V]** Top-level layout, verified against the default branch through the GitHub REST API:
`.github/`, `assets/`, `bin/`, `contracts/`, `docs/`, `extensions/`, `fixtures/`, `lib/`, `odd/`,
`prompts/`, `runtime/`, `scripts/`, `skills/`, `tests/`, `themes/`, plus `package.json`,
`pnpm-workspace.yaml`, `tsconfig.json`.

**[V]** Backlog at 2026-10-01: **422 open** issues (965 total) and **104 open** PRs (676 total).
It carries the highest open ratio of the three systems.

**[V]** Label inventory, 21 labels from the live API: GitHub defaults (`bug`, `documentation`,
`duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`),
plus Gentle labels (`status:approved`, `status:needs-review`, `status:needs-design`, `type:bug`,
`type:feature`, `type:chore`, `type:refactor`, `type:docs`, `type:breaking-change`,
`priority:high`, `size:exception`, `slop`).

**[V]** Issue templates: `.github/ISSUE_TEMPLATE/bug_report.yml` and `feature_request.yml`.
Workflows: `ci.yml`, `publish.yml`, `windows-hidden-processes.yml`, `windows-session-bootstrap.yml`.

**[V]** `contracts/` mirrors `gentle-ai`'s versioned-schema pattern: `review-integration/v1`,
`review-integration/v2`, and `review-provider-contract-mirror/v1.2.0`.

**[V]** Coupling to the other targets: it installs and executes the `gentle-ai` binary
(`scripts/gentle-ai-installer.mjs`, pinned to `v2.6.0`) and detects Engram's `mem_save` tool
(`extensions/gentle-ai.ts`, `hasWritableEngramTool`).

### 3.1 Naming note — this is not a caveat about the system

**[V]** `Gentleman-Programming/gentle-pi` **redirects** to
`Gentleman-Programming/gentle-shell`: the GitHub API returns the same repository id
(`1234537369`) for both URLs. The repository was renamed; the npm package is still published as
`gentle-pi`.

**This is a naming detail only.** `gentle-shell` is its own repository — not an alias, not a
directory, and not part of another system.

### 3.2 Correction note

**[V]** An earlier revision of this document claimed that `gentle-shell` "does not exist as a
system". **That claim was wrong** and is superseded by this section.

**[V]** Cause of the error: a local scratch directory formerly assumed to be the `gentle-shell`
checkout is a **stale Pi scratch directory** — three files (`/.atl/skill-registry.md`,
`/.atl/.skill-registry.cache.json`, `/.gitignore`), not a Git repository, and whose own
skill-registry header reads `# Skill Registry — kernel`. It is unrelated to the repository, which
is not cloned there.

**[V]** A separate stale local clone existed under the former project name (`gentle-pi`). It was
**stale**: branch `test/shell-gauge-coverage`, HEAD `a275e859` (2026-09-13), behind
`origin/main`. Any finding read from that working tree must be re-verified against the default
branch.

---

## 4. Cross-cutting findings

### 4.1 There is a shared approval gate — and it is the only shared label

**[V]** All three repositories carry the same approval gate: an issue receives
`status:needs-review`, and a maintainer applies `status:approved`. In `gentle-ai` and `engram`,
CI refuses a PR whose linked issue does not carry `status:approved`; the PR must also carry
exactly one `type:*` label.

**[V]** That gate is the **only** label vocabulary the three systems share. Type and priority
families diverge:

| | `gentle-ai` | `engram` | `gentle-shell` |
| --- | --- | --- | --- |
| central label declaration | none | `.github/labels.yml` | live API only |
| type labels | `bug`, `enhancement` | `type:*` | `type:*` **and** GitHub defaults |
| priority labels | none | 4 bands | `priority:high` only |
| duplicate labels | none | `possible-duplicate` + `resolution:duplicate` | `duplicate` (GitHub default) |

**This is the strongest existing constraint for the assistant**: the approval gate generalises
across all three systems; nothing else in the label space does.

### 4.2 Triage knowledge already exists — as prose, twice

**[V]** Three triage protocols exist across two repos with partially overlapping vocabularies:

- `gentle-ai/systemic-issue-triage` → root classes **A–E**
- `gentle-ai/issue-root-resolution` → mechanism map + evidence-gated closures
- `engram/backlog-triage` → dispositions **MERGE / REQUEST CHANGES / CLOSE / NEEDS DESIGN / APPROVE ISSUE / REJECT ISSUE**

**[V]** They are prompts, not engines: no code, no GitHub calls, no persistence, no repeatability
guarantee. This is precisely the gap the maintainer assistant would occupy.

### 4.3 Memory has no issue entity

**[V]** Engram can store arbitrary text observations with `topic_key` upserts and can relate
observation↔observation, but it **cannot natively represent "issue #123 of repo X"** and cannot
link an issue to a memory. Any issue-centric memory must either encode issues into existing
primitives (project/scope/topic_key conventions) or live outside Engram. This is the single
largest structural gap identified in Phase 1.

### 4.4 GitHub access is conventional, not institutionalized

**[V]** `gh` CLI is the established mechanism in every skill and script. No Go GitHub client
exists. No token is stored by either project outside CI. So the low-friction acquisition path is
`gh`-based and read-only by default.

### 4.5 No de-duplication or clustering engine exists anywhere

**[V]** Engram deduplicates *identical memory saves* by content hash. Nothing anywhere clusters or
deduplicates *issues*. `docs/architecture/rdd-backlog-disposition.md` shows this was done manually
once, by hand, for 333 items in `gentle-ai`.

### 4.6 Schema-first is an existing, respected pattern

**[V]** `gentle-ai/contracts/` versions JSON Schemas with fixtures, and
`gentle-ai/openspec/` holds formal specs. Phase 6 of the protocol (data contracts) has a direct
precedent to imitate in shape, though not in content.

---

## 5. Reusable capabilities (candidates, not decisions)

Recorded as evidence-backed candidates for Phase 3. No commitment is made here.

| # | Capability | Source (evidence) | Reuse shape |
| --- | --- | --- | --- |
| R1 | `status:*` / `type:*` / `priority:*` / `effort:*` label vocabulary | both repos' `.github/labels.yml` + templates | the triage result must speak this vocabulary |
| R2 | Six-disposition triage vocabulary | `engram/skills/backlog-triage/SKILL.md` | candidate taxonomy for triage output |
| R3 | Root-class bucketing A–E | `gentle-ai/skills/systemic-issue-triage/SKILL.md` | candidate taxonomy for root clustering |
| R4 | Mechanism map + evidence-gated closure rules | `gentle-ai/skills/issue-root-resolution/SKILL.md` | candidate evidence model |
| R5 | Pairwise relation verbs + confidence + provenance | Engram `memory_relations` | candidate vocabulary for relationship typing |
| R6 | Persistent store reachable over HTTP/MCP/CLI | Engram `internal/server`, `internal/mcp` | candidate persistence substrate |
| R7 | Schema-first contracts with fixtures | `gentle-ai/contracts/` | candidate shape for Phase 6 |
| R8 | `gh` CLI as acquisition mechanism | skills + release scripts | candidate acquisition path |
| R9 | Skill-as-delivery for agent behavior | `skills/*/SKILL.md` in both repos | candidate delivery mechanism for Phase 7 prompts |
| R10 | Existing skill/persona injection pipeline | gentle-ai `internal/components/skills`, `persona` | candidate distribution channel |

---

## 6. Integration points (candidates)

| Boundary | Candidate | Evidence |
| --- | --- | --- |
| Issue acquisition | `gh issue list/view --json` | established in both triage skills |
| Issue acquisition (alt) | GitHub REST with `GITHUB_TOKEN` | used by CI `pr-check` in both repos |
| Persistence | Engram local HTTP (`127.0.0.1:7437`) | documented for external clients |
| Persistence (alt) | Engram MCP stdio | documented for agents |
| Persistence (alt) | Engram CLI subprocess | documented for scripts |
| Delivery to agents | gentle-ai skill/persona injection | `internal/components/` |
| Human-facing output | Markdown report + suggested `gh` commands | both triage skills already end this way |

**[V]** Engram **cannot** be linked as a Go library — any integration is over MCP, HTTP, or CLI.

---

## 7. Open questions for the maintainer

These are decisions, not facts. Status as of 2026-10-01.

| # | Question | Status |
| --- | --- | --- |
| Q1 | Governing protocol written into `AGENTS.md`? | **ANSWERED — yes.** Not yet executed. |
| Q2 | What is `gentle-shell`? | **RESOLVED — its own repository.** See §3. |
| Q3 | Product shape: skill bundle, binary, both, or batch job? | OPEN |
| Q4 | Persistence: Engram conventions, dedicated store, or none in v1? | OPEN — blocks Phase 6 |
| Q5 | GitHub authority in v1? | **ANSWERED — read-only.** |
| Q6 | Repository scope? | **RESOLVED — the three systems.** |
| Q7 | Execution model: interactive, or batch report? | OPEN |
| Q8 | Cross-repository analysis in v1? | **ANSWERED — cross-repository only.** Internal blast radius deferred to v2. |
| Q9 | Language of artifacts? | **ANSWERED — English for repository artifacts.** |

Q3 blocks the delivery and maintainer-interaction decisions; Q4 blocks Phase 6; Q7 blocks the
maintainer-interaction surface. Q1, Q2, Q5, Q6, Q8 and Q9 are settled.

---

## 8. Compliance statement

- No application source code, API, database schema, container config, CI, or GitHub mutation was created.
- The only file created by this phase is this document.
- No write occurred in `gentle-ai`, `engram`, or `gentle-shell`; all inspection was read-only.
- Phase 1 is complete. Phases 2–4 are documented in `docs/problem-definition.md`,
  `docs/architecture.md` and `docs/triage-model.md`. Phase 5 is documented in
  `docs/decision-model.md`. Implementation still requires explicit maintainer approval.
