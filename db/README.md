# Issue Store — experiment harness

> **Status: experiment harness, not the product.** It exists so the two-judge
> classification experiment is reproducible and auditable instead of living in a
> chat log. The production gate in `AGENTS.md` is still closed; the maintainer
> explicitly authorised this piece.

## Why SQLite and not Postgres-in-Docker

```
   1. Engram — the ecosystem's own memory system — IS SQLite + FTS5 with
      tokenize='trigram'. Same problem, same answer, already chosen.
   2. Engram's own architecture splits local (SQLite, "the absolute authority")
      from cloud (Postgres). This store is local.
   3. 20 MB, one writer, no concurrent access. A server buys nothing.
   4. A file cannot fail the way the container did — root-owned bind mount,
      stale mount inode, non-idempotent init script.
```

The discarded Postgres attempt is preserved, with its post-mortem, in
`postgres-alt/`. Docker becomes the right answer again **if** this ever needs to
be shared by several people — which is exactly the split Engram already made.

## The design decision that matters most

The schema **encodes the Phase 5 decision model**. Inference and decision live in
different tables and cannot mix:

```
   votes      ← what a judge (an LLM) said.       PURE INFERENCE
                has no column that could express a decision.

   judgments  ← what a maintainer decided.        AUTHORITATIVE
                requires actor + reason, and a CHECK refuses
                machine actors (judge*, bot*, llm*, ...).
```

The separation is structural, not a convention.

## Files

| File | Role |
| --- | --- |
| `schema.sql` | DDL. Idempotent: `sqlite3 exp.db < schema.sql` |
| `load.py` | Fetches via the host's authenticated `gh`, loads into SQLite, derives columns, extracts cross-refs |
| `sample.py` | Exports a reproducible stratified sample as chunk files, and records the run |
| `exp.db` | The database. Git-ignored |
| `postgres-alt/` | The discarded first attempt, kept for reference |

## Usage

```bash
cd db
./load.py                    # full fetch, all three systems
./load.py --cached           # reuse /tmp/gas/*-full.json, no network
./load.py --state open       # open issues only

sqlite3 -header -column exp.db 'SELECT * FROM v_triage_debt'
sqlite3 -header -column exp.db 'SELECT * FROM v_cross_system LIMIT 10'
```

## Tables

| Table | Purpose |
| --- | --- |
| `systems` | The three repositories |
| `issues` | One row per issue. `UNIQUE (system_id, number)` — the canonical key |
| `labels`, `issue_labels` | Per-system label catalog. Kept per-system because the three vocabularies diverge and that divergence is itself a finding |
| `comments` | Optional. Triage needs bodies **and** comments |
| `cross_refs` | Qualified references (`owner/repo#n`). The **only** high-confidence cross signal |
| `judges` | **The inference engine**: agent, model, provider, effort |
| `runs`, `run_issues` | An experiment run and its sample |
| `votes` | Judge output. Inference |
| `judgments` | Maintainer decision |

## Views

| View | Purpose |
| --- | --- |
| `v_triage_debt` | The headline metric: how much of the backlog never passed the first gate |
| `v_cross_system` | Issues carrying a qualified reference to another system |
| `v_label_vocabulary` | The three label vocabularies, side by side |
| `v_title_prefix` | Conventional-commit prefix distribution — the strongest a-priori signal |
| `v_judge_agreement` | Per issue: what each judge said, and whether they agreed |

## Two things SQLite costs, stated honestly

1. **No `similarity()`.** Postgres' `pg_trgm` would let cross-system duplicate
   detection (`#1540` / `#5119`) be a single SQL view. Here it runs in Python at
   analysis time. It is measured once, not on every run.
2. **No SQL `regexp`.** `refresh_derived()` therefore lives in `load.py` as Python.
   Still deterministic, still re-runnable without refetching.

## Verified on first load (2026-10-01)

```
   3 systems · 1,228 issues · 73 labels · 2,712 label links · 55 cross_refs
   FTS5 trigram search: OK

   v_triage_debt
     gentle-ai      505/733   68.9%
     gentle-shell   379/424   89.4%
     engram          55/71    77.5%
   ─────────────────────────────────
     total          939/1228  76.5%
```

This reproduces, exactly, the figure measured by hand in the analysis phase.
