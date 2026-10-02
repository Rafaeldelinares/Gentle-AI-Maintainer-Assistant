# Module A — Report Completeness

> **Read-only module.** Compares each open report against the required fields of its own repository's issue form. It is a **completeness signal**, not an accusation.
>
> **Nothing is applied.** The maintainer decides whether to ask for the missing data. `veredicto_humano: pendiente` is stated for every entry; the tool never fills it.
>
> Reproduce with `python3 modules/completeness.py`.

## Summary

| Metric | Value |
| --- | --- |
| Issues matched to a template (bug/feature) | 1114 |
| Filed through the form (>=1 template heading present) | 1043 |
| Outside the form (no template heading; pre-template or automated) | 71 |
| Complete: every required content field present and non-empty | 730 |
| **Incomplete: missing >= 1 required content field** | **313** |

_Only issues filed through the form are counted in the incomplete metric. Attestation checkboxes are reported separately because a missing checkbox is not missing information._

### Incomplete issues by repository

| Repository | Incomplete | Share of its form-filed issues |
| --- | --- | --- |
| `engram` | 4 | 7.1% |
| `gentle-ai` | 201 | 32.1% |
| `gentle-shell` | 108 | 30.0% |

### Most frequently missing required content fields

| Required field | Issues missing or empty |
| --- | --- |
| AI Agent / Client | 159 |
| Gentle AI Version | 153 |
| 📋 Affected Area | 151 |
| Operating System | 150 |
| 🔄 Steps to Reproduce | 113 |
| 📝 Bug Description | 94 |
| gentle-pi version | 65 |
| Pi version | 64 |
| Operating system | 62 |
| ❌ Actual Behavior | 48 |
| Steps to reproduce | 37 |
| Proposed outcome | 32 |
| Expected and actual behavior | 31 |
| Problem | 30 |
| 📦 Proposed Solution | 19 |

### Template fields parsed (ground truth)

- `engram/bug_report.yml`
  - required content: 📝 Bug Description, 🔄 Steps to Reproduce, ✅ Expected Behavior, ❌ Actual Behavior, Operating System, Engram Version, Agent / Client
  - attestations: —
- `engram/docs.yml`
  - required content: 📄 Documentation Reference, 📄 Which Document?, 🔍 What's Wrong or Missing?
  - attestations: —
- `engram/feature_request.yml`
  - required content: 🔍 Problem Description, 💡 Proposed Solution, 📦 Affected Area
  - attestations: —
- `engram/question.yml`
  - required content: Question, Why does this need issue tracking?, Affected Area
  - attestations: —
- `gentle-ai/bug_report.yml`
  - required content: 📝 Bug Description, 🔄 Steps to Reproduce, ✅ Expected Behavior, ❌ Actual Behavior, Gentle AI Version, Operating System, AI Agent / Client, 📋 Affected Area
  - attestations: Pre-flight Checklist
- `gentle-ai/feature_request.yml`
  - required content: 🔍 Affected Area, 💡 Problem Statement, 📦 Proposed Solution
  - attestations: Pre-flight Checklist
- `gentle-shell/bug_report.yml`
  - required content: Problem, Steps to reproduce, Expected and actual behavior, gentle-pi version, Pi version, Operating system
  - attestations: Before submitting
- `gentle-shell/feature_request.yml`
  - required content: Problem or opportunity, Proposed outcome
  - attestations: Before submitting

## Incomplete issues (up to 15 per repository)

### `engram` — 4 incomplete

- **engram#182** — feat(security): optional encryption at rest for engram.db
  - Link: https://github.com/Gentleman-Programming/engram/issues/182
  - Missing: 🔍 Problem Description (missing); 💡 Proposed Solution (missing)
  - veredicto_humano: pendiente
- **engram#184** — feat(store): observation version history for topic_key upserts
  - Link: https://github.com/Gentleman-Programming/engram/issues/184
  - Missing: 🔍 Problem Description (missing); 💡 Proposed Solution (missing)
  - veredicto_humano: pendiente
- **engram#849** — sync_apply_deferred dead rows have no retention policy and can grow without bound
  - Link: https://github.com/Gentleman-Programming/engram/issues/849
  - Missing: 💡 Proposed Solution (missing); 📦 Affected Area (missing)
  - veredicto_humano: pendiente
- **engram#201** — security(sync): make Git-based memory sync safer by default, especially for prompts
  - Link: https://github.com/Gentleman-Programming/engram/issues/201
  - Missing: 🔍 Problem Description (missing)
  - veredicto_humano: pendiente

### `gentle-ai` — 201 incomplete

- **gentle-ai#4872** — bug(review): worker refuses explicitly unreviewed candidate
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/4872
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ✅ Expected Behavior (empty); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#1213** — Engram protocol is injected three times per session (~4,950 tokens of duplication) on claude-code
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1213
  - Missing: 📝 Bug Description (missing); ✅ Expected Behavior (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#1443** — chore(review): v2.1.8 follow-ups from bounded review findings
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1443
  - Missing: 🔄 Steps to Reproduce (missing); ✅ Expected Behavior (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#1903** — fix(engram): proactive memory search is ineffective — agent does not discover user projects before searching
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/1903
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ✅ Expected Behavior (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing)
  - veredicto_humano: pendiente
- **gentle-ai#2094** — Hermes adapter ignores HERMES_HOME and writes to the wrong config directory on Windows
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2094
  - Missing: 📝 Bug Description (missing); ✅ Expected Behavior (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#2625** — bug(gga): claude provider times out silently on pre-commit review (v2.10.1)
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2625
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#2648** — bug(review): commit review hook inserts fabricated/unverified technical narrative into committed markdown
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/2648
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ✅ Expected Behavior (missing); ❌ Actual Behavior (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3275** — Reviewer launch fails when gentle-ai is unavailable to the review executor
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3275
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3373** — Lock contention is reported as authority corruption in three places
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3373
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3374** — Recovery transition reads as maintainer-authorized but is self-service, and its trigger is inverted
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3374
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3384** — Stop transitions emit a bare reason_code, so consumers invent their own menus
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3384
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3389** — A candidate with a single path over 4 MiB starts, then loops on a refusal that can never resolve
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3389
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3401** — Self-service recovery records the maintainer git identity as authorizing actor and ignores --actor
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3401
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3693** — Automated review hook selects unsupported Codex model for ChatGPT account
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3693
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente
- **gentle-ai#3991** — bug(review): Claude Code reviewer lens intermittently exceeds the output token limit and returns no result
  - Link: https://github.com/Gentleman-Programming/gentle-ai/issues/3991
  - Missing: 📝 Bug Description (missing); 🔄 Steps to Reproduce (missing); ❌ Actual Behavior (missing); Gentle AI Version (missing); Operating System (missing); AI Agent / Client (missing); 📋 Affected Area (missing)
  - veredicto_humano: pendiente

### `gentle-shell` — 108 incomplete

- **gentle-shell#1052** — bug(provider): kimi-k3 tool calls fail with 400 'tool_call_id is not found' after compaction or parallel batch
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/1052
  - Missing: Problem (missing); Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#369** — fix(skill-registry): mirror Pi-resolved loaded skills
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/369
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#373** — fix(skill-registry): degrade truthfully when the project registry is unwritable
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/373
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#464** — bug(release): latest v2.2.0 still strands corrected lineages before last-event migration
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/464
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#511** — fix(orchestrator): enforce parent hot memory persistence on inline direct tasks
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/511
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#531** — Windows: CodeGraph Pi tool reports ENOENT because execFile("codegraph") does not resolve npm/Scoop shims
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/531
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#597** — bug(review): RENAMED arrow headings are double-counted in native line budgets
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/597
  - Missing: Problem (missing); Steps to reproduce (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#617** — fix: reconcile parent todos at SDD phase boundaries
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/617
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#654** — bug(review): acknowledge-approved loses committed-only baseRef selector
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/654
  - Missing: Problem (missing); Steps to reproduce (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#688** — La barra de status no muestra los MCP conectados
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/688
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#696** — START results labeled answer-consent even when no consent envelope exists
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/696
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#700** — bug(tests): the documented env var makes test:dev-binary skip all 10 checks silently
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/700
  - Missing: Steps to reproduce (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#722** — bug(windows): intermittent git rev-parse spawn failure in non-Git workspace
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/722
  - Missing: Problem (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#734** — Bug: model selected via /model is not persisted — new sessions always start with the first-ever default model
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/734
  - Missing: Problem (missing); Steps to reproduce (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
- **gentle-shell#825** — [Bug] RDD reviewer capture fails with 404 transport error
  - Link: https://github.com/Gentleman-Programming/gentle-shell/issues/825
  - Missing: Problem (missing); Expected and actual behavior (missing); gentle-pi version (missing); Pi version (missing); Operating system (missing)
  - veredicto_humano: pendiente
