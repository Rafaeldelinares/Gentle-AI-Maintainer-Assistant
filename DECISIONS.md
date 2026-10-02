# DECISIONS.md — Design Decisions

> Every decision that shapes what the tool does, with the alternatives that were considered and why they were rejected.
> A decision here is binding for the code; a change must be recorded as a new decision, not edited silently.

---

## D-001 — Deterministic first, LLM only in the grey area

- **Decision:** code resolves everything mechanically recognizable (prefix, labels, crash/loss patterns). The LLM runs only on what code cannot decide.
- **Why:** the backlog shows a long tail of very uniform reports. Code is free, instantaneous, reproducible, and auditable; an LLM call is none of those.
- **Alternatives considered:**
  - *LLM-first on every issue:* rejected — expensive, slow, and non-reproducible, with no accuracy advantage on structural cases.
  - *Embedding/NN classifier:* rejected for now — no labelled dataset large enough to train or evaluate it, and it would trade auditability for a black box.
- **Consequence:** deterministic coverage is a *census* (41.5% of open issues), not a correctness claim. Coverage and precision are tracked separately in `PROMISES.md`.

## D-002 — P0 is always a candidate, never a final decision

- **Decision:** a silent-data-loss match emits `candidato P0, requiere revisión humana` with rule `rule:candidato_p0_requiere_revision_humana`. The JSON Schema enforces it in both directions.
- **Why:** a false P0 erodes trust faster than any other error. Naming it a candidate tells the maintainer "look here first", which is useful; naming it P0 without evidence would be a lie.
- **Alternatives considered:**
  - *Emit `P0` directly:* rejected — the engine cannot verify data loss from prose.
  - *Emit `P0` plus a boolean `requires_human_review`:* rejected — two representations of the same fact can disagree; the label already carries the requirement.
- **Consequence:** the 14 candidate P0 issues are pending human adjudication in `gold-p0-p1.md`.

## D-003 — A hard signal under a non-bug prefix keeps its band and gets a review flag

- **Decision:** a `feat:`/`docs:` issue whose body describes data loss or a crash is **not** promoted to P0/P1. It keeps P2/P3 and is flagged by `requires_human_review()` (`AUDIT.md` audit 1; 26 issues).
- **Why:** the prefix is the reporter's own classification. Promoting on content alone would silently override the reporter and could flood P1 with feature proposals that merely *mention* a crash.
- **Alternatives considered:**
  - *Auto-promote to P1:* explicitly rejected by the owner — it would recreate the alert fatigue the tool exists to prevent.
  - *Do nothing (leave grey/P2 silently):* rejected — the audit showed `feat:` issues describing real silent loss (`gentle-ai#2123`, `#1562`, `gentle-shell#675`). Silence is the failure mode the tool must not have.
- **Consequence:** 17 loss-under-prefix and 9 crash-under-prefix issues are surfaced for a human look without changing the band.

## D-004 — Recover `title_prefix` from the title

- **Decision:** `derive_title_prefix()` parses the title when the ingested `title_prefix` is empty, tolerating a leading backtick and a bracketed prefix such as `[Automated provider defect]`.
- **Why:** `AUDIT.md` audit 4 found 6 issues whose title starts with a conventional token but whose ingested prefix is empty; 5 of them, including a crash report, fell into the grey area because of it.
- **Alternatives considered:**
  - *Fix only the ingestion pipeline and re-fetch:* rejected — it requires live GitHub access and would not fix the frozen snapshot the auditor reads.
  - *Trust the ingested field:* rejected — it is demonstrably wrong for those 6 issues.
- **Consequence:** `gentle-ai#4974`, `#4807`, `#4816`, `#2520`, `#1968`, `gentle-shell#1305` reclassify correctly. `#4974` (a crash report) leaves the grey area.

## D-005 — An explicit conventional prefix wins over a conflicting type label

- **Decision:** `docs:`/`chore:` prefixes are evaluated **before** the `enhancement`/`type:feature` labels.
- **Why:** `AUDIT.md` audit 3 found 4 `docs:`-titled issues classified P2 because they carried an `enhancement` label (`gentle-ai#5168`, `#3273`, `#2732`, `#3490`). A documentation task is P3 regardless of how it was labelled.
- **Alternatives considered:**
  - *Label wins:* rejected — labels are applied inconsistently; the title prefix is what the author chose deliberately.
  - *Leave the order as feature-then-docs:* rejected — the audit showed it decides the band against the author's own prefix.
- **Consequence:** 27 issues move from P2 to P3. The `bug:`-prefixed issue with a feature label stays P2; that residual conflict is documented, not hidden.

## D-006 — Crash vocabulary widened, but generic "cannot start" deliberately excluded

- **Decision:** `RE_P1_CRASH_CORE` recognizes `panic:`/`runtime panic`, `SIGSEGV`, `fatal error: runtime`, `NullPointerException`, `uncaughtException` (camelCase), `unhandled exception/rejection`, `stack overflow`, `out of memory`, `OOM killer`, `fail(s|ed) to start`, `crash(es|ed|ing)`, `bricked`. It does **not** match a bare `cannot start`.
- **Why:** `AUDIT.md` audit 2 showed genuine crash reports (e.g. `gentle-shell#962`, `gentle-ai#4677`) stuck in the grey area. But `cannot start` matched `review cannot start`, `build cannot start`, `work unit cannot start` — blocked workflows, not process crashes (`gentle-ai#5166`, `#4991`, `#4749`, `#4292`, `#4250`, `gentle-shell#941`).
- **Alternatives considered:**
  - *Broad `cannot start`:* rejected — 8+ false P1s on blocked-workflow issues.
  - *Keep the narrow original vocabulary:* rejected — it misses the crash reports the audit named.
- **Consequence:** P1 went from 2 to 17 issues on the snapshot. **Precision is not yet validated by humans** and is listed as such in `PROMISES.md`.

## D-007 — Negation and idiom guards on crash signals

- **Decision:** a crash token is ignored when it is negated (`not a crash`, `no system crash`, `has not been demonstrated`) or used as a compound modifier (`crash-safe`, `crash-recoverable`, `crash-window`, `crash-on-render ... does not apply`), or when it appears in a fix/avoidance description (`prevent ... from crashing`).
- **Why:** the widened vocabulary would otherwise recreate the false-positive class that `AUDIT.md` removed for data loss.
- **Alternatives considered:**
  - *No guards:* rejected — it flags `There is no system crash`, `Crash-window tests`, and `designed to be crash-safe`.
  - *Full NLP negation detection:* rejected — unjustifiable complexity for a rule engine; the guard list is explicit and testable.
- **Consequence:** `test_rules.py` §6 pins 16 rejected phrases and 6 accepted ones.

## D-008 — Widened workaround detection; `bypass` and `mitigation` removed

- **Decision:** `RE_WORKAROUND_POSITIVE` adds `works if/after`, `retry works/helps`, `restarting helps/fixes`, `re-run works/fixes`. `bypass` and `mitigation` were removed. `RE_WORKAROUND_NEGATIVE` now also catches `no ... work around`.
- **Why:** `bypass` produced a false workaround on a text saying *"not an authorization bypass"*, which wrongly demoted a crash to P2 — the most dangerous error class (`AUDIT.md` audit 1). `mitigation` is too often a design intention.
- **Alternatives considered:**
  - *Keep `bypass` with a negation guard:* rejected — the term is ambiguous even when unnegated.
  - *Leave H9 unfixed:* rejected — the audit showed real workaround sections (`## Workaround`) were not being detected because the issue also had to be classified P1 first.
- **Consequence:** H9 now demotes 4 real issues (`gentle-ai#4809`, `#3016`, `gentle-shell#745`, `#1052`), all with an explicit workaround section. Small n; stated as such.

## D-009 — Anti-overfit split by `sha256(slug#number) mod 5`

- **Decision:** audits and future validation splits are deterministic: group 0 (≈20%) is held-out, groups 1–4 are for exploration.
- **Why:** the 90-issue calibration sample informed the heuristics, so any number measured on it is optimistic. A deterministic, reproducible split lets a third party re-derive the same groups.
- **Alternatives considered:**
  - *`random.shuffle` with a seed:* rejected — Python's `hash()` is randomized per process; `sort_keys`-based shuffles are harder to reproduce in another language.
  - *Stratify by repo and band:* deferred — a better future split, but it needs human labels to stratify on.
- **Consequence:** `tools/metrics.py` reports exploration and held-out coverage separately (997 → 41.0%, 231 → 43.7%).

## D-010 — No precision claims until a fresh human-labelled sample exists

- **Decision:** post-audit rule changes are marked **"pending human validation"** everywhere. Only coverage and census figures are published as facts.
- **What "contaminated" means, precisely:**
  - The **90-issue calibration sample** authored the *original* heuristics (feature/docs/prefix rules), so an agreement figure measured on it for those rules is optimistic. It is contaminated **for those rules**.
  - The **post-audit changes** (crash vocabulary, rule order, H9 vocabulary) were derived from the full-corpus audit and from `AUDIT.md`, **not** tuned on the 90-issue sample. That sample is therefore *not* the contamination problem for them; the problem is different: the sample is small (34 deterministic matches) and the **held-out group was read during the audit**, so it is no longer blind.
  - Net effect: no unbiased precision estimate can come from the current data for any rule. Coverage, label census and cross-reference counts are unaffected because they are censuses, not estimators.
- **Why:** the honest requirement is not "the data is dirty" but "the data is not an independent test set". Reusing it would produce a number that flatters the tool.
- **Alternatives considered:**
  - *Report the new precision on the calibration sample:* rejected — the sample was used to author the original patterns and is too small for the new ones.
  - *Report the new precision on the held-out group:* rejected for now — the audit inspected those issues, so the group is compromised as a blind test; a fresh sample is cheaper than pretending otherwise.
  - *Claim improvement from the coverage delta:* rejected — coverage is not precision; more P1s could mean more false positives.
- **Consequence:** `PROMISES.md` P-14/P-15 and §5 carry the "pending" status. The owner labels a fresh sample before any precision number is published.

## D-011 — Every reviewable artifact lives in the repository root

- **Decision:** `PROMISES.md`, `DECISIONS.md`, `AUDIT.md`, `STATUS.md`, `OBSERVABILITY.md`, `EVALUATION.md`, `gold-p0-p1.md`, `README.md`, `AGENTS.md` are root files. Key code is quoted inside `EVALUATION.md` with `Fuente: ruta @ hash`.
- **Why:** the external reviewer reads raw GitHub URLs and cannot navigate directories.
- **Alternatives considered:**
  - *A `docs/`-only layout:* rejected — the reviewer cannot reach subdirectories.
  - *Publish a generated site:* rejected — adds a build step and a hosting dependency for no review benefit.
- **Consequence:** `OBSERVABILITY.md` lists the raw URL of every artifact and is kept current on each delivery.

## D-012 — The STATUS hash is recorded in a follow-up documentation commit

- **Decision:** each delivery is two commits: the content commit, then a documentation-only commit that records the content commit's hash in `STATUS.md`.
- **Why:** a commit cannot contain its own hash. Recording a pre-amend hash (the previous pattern) left `STATUS.md` pointing at a commit that no longer existed.
- **Alternatives considered:**
  - *`git commit --amend` after writing the hash:* rejected — it rewrites the hash and leaves a dead reference.
  - *Omit the hash:* rejected — the reviewer needs to match `STATUS.md` against a real commit.
- **Consequence:** `STATUS.md` always cites a commit that exists.

## D-013 — Module A measures completeness against the repository's own issue form

- **Decision:** parse the real `.github/ISSUE_TEMPLATE/*.yml` of each repository and check whether an open report carries the required fields. Separate required *content* fields from *attestation* checkboxes; report an issue as "outside the form" when it has no template heading.
- **Why:** asking for information the template already requested is the largest avoidable cost in triage. The template is ground truth authored by the maintainers, so no invented field list is needed.
- **Alternatives considered:**
  - *Invent a "good report" checklist:* rejected — it would encode our opinion, not the maintainers'.
  - *Use only `###` headings as field presence:* rejected — GitHub renders inputs as inline `**Label:** value`, so a heading-only check produced false "missing" on well-formed reports (verified on `gentle-ai#5062`).
  - *Count attestation checkboxes as missing information:* rejected — a missing pre-flight tick is not missing triage data.
- **Consequence:** 313 of 1,043 form-filed issues miss at least one required content field; issues outside the form (71) are excluded and reported separately.

## D-014 — Module B uses evidence tiers, never a confidence claim

- **Decision:** duplicates are ranked as "strong evidence" or "weaker evidence" from deterministic signals (rare exception class, error code, `file:line`, quoted error string, exit code, normalized-title equality/Jaccard). The report never says "duplicate"; it says "candidate pair" and marks `veredicto_humano: pendiente`.
- **Why:** a false duplicate can close a distinct bug, which is more damaging than a missed duplicate. The wording must not invite an automatic close.
- **Alternatives considered:**
  - *Label tiers "high/medium confidence":* rejected — the tool cannot measure confidence; it measures shared evidence.
  - *Call any shared rare signature a duplicate:* rejected — sibling feature issues share exception names and configuration strings (observed on `gentle-shell#446`/`#448`).
  - *Use embeddings/LLM similarity:* rejected — non-deterministic and unauditable.
- **Consequence:** 108 candidate pairs, 7 with strong evidence, and an explicit caveat that shared identifiers are evidence, not proof.

## D-015 — Module C proposes a link only from an explicit reference

- **Decision:** a proposed cross-repository link requires an explicit `owner/repo#N` or `repo#N` reference whose number resolves to an open issue. A bare repository-name mention never proposes a link.
- **Why:** `AUDIT.md` reported "345 issues mention another repo with no structured link", but a mention is not a dependency: install instructions, comparisons and unrelated prose mention repositories. Treating mentions as links would flood the maintainer.
- **Alternatives considered:**
  - *Propose links from bare slug mentions:* rejected — 914 issues mention another repository by name; only 33 carry an explicit reference, and only 15 of those resolve.
  - *Auto-populate `cross_refs`:* rejected — the structured field is maintainer-owned.
- **Consequence:** the audit's "345" is reframed: 15 explicit, resolving references are actionable; the rest are prose mentions reported as the weakest signal.
