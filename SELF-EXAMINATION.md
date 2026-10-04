# What This Tool Can and Cannot Say

> A self-examination, written for the maintainers of `gentle-ai`, `engram` and
> `gentle-shell` — the people whose open issues this reads. It is the honest half of the
> project: not what we built, but what it is entitled to claim.
>
> Frozen snapshot: **1228 open issues** across three repositories, at the commits recorded
> in `tools/vendor.py`. Read-only: this project writes nothing into any repository, and
> every row it produces is `veredicto_humano: pendiente`.

## 1. What this is

A read-only analysis of the open issues of three repositories. It does five things:

| Module | Question it answers | Report |
| --- | --- | --- |
| A | Which filed reports are missing information you need? | `report-completeness.md` |
| B | Which pairs of issues look like the same report twice? | `report-duplicates.md` |
| C | Which issues refer to issues in the other repositories, and do those still exist? | `report-cross-links.md` |
| D | Which issues point at things that no longer exist? | `report-obsolete.md` |
| E | Where would a change land, if you had to pick a place to look? | `report-concentration.md` |

Plus a local Kanban board that turns the engine's output into columns on your own machine
(`BOARD.md`), and a deterministic rule engine that suggests a band for each issue
(`db/rules.py`).

**It does not comment, label, close, transfer or mail anything.** Section 5 says how that
is enforced rather than promised.

## 2. What it can tell you today

Every figure below is produced by the command named with it. Run it and you get the same
numbers — that is checked (`DETERMINISM.md`).

**Which reports are missing what** — `python3 modules/completeness.py`:

Of **1043** issues filed through a repository's issue form, **313** miss at least one
required content field. The most frequent gaps are `AI Agent / Client` (159),
`Gentle AI Version` (153), `📋 Affected Area` (151), `Operating System` (150),
`🔄 Steps to Reproduce` (113) and `📝 Bug Description` (94). By repository: `engram` 4
(7.1%), `gentle-ai` 201 (32.1%), `gentle-shell` 108 (30.0%).

This is the module with the shortest path to a maintainer's hands: it is a list of "ask
this one thing and the report becomes actionable".

**Which pairs look duplicated** — `python3 modules/duplicates.py`:

**108** candidate pairs, of which **7** carry strong evidence (shared distinctive
identifiers) and 101 weaker evidence. Strong evidence is an ordering of your reading, not
a verdict: two sibling issues about the same feature often share exception names.

**Cross-repository references** — `python3 modules/cross_repo.py`:

**48** explicit `repo#N` references, of which **15** resolve to an open issue in the
snapshot and **33** do not. A non-resolving reference may mean the target was closed,
renamed, or typo'd — the report says which, and does not guess.

**Possibly obsolete** — `python3 modules/obsolete.py`:

**54** issues reference a path that exists in the repository's history as a *deletion*
(Class A — verifiable obsolescence) and **155** reference a path, flag or symbol that is
absent with *no deletion record* (Class B). **Class B is not evidence of obsolescence**:
the path may belong to another repository, to the installed package layout, or to
unlanded work. The two classes are kept apart on purpose, so the strong signal is not
diluted by the weak one.

**Where problems land** — `python3 modules/concentration.py`:

**458** of 1228 issues name a repository path, **770** name none, and there are **164**
distinct subsystems. The top ten subsystems cover **299** of the 458 (65%) — led by
`gentle-shell` `extensions` (99), `gentle-shell` `lib` (98) and `gentle-ai` `internal/cli`
(55).

## 3. Two measurements that contradicted our own assumptions

This is the part we would keep if we threw the rest away, because both times the
measurement overturned a premise the project was built on.

### 3.1 "The unclassified issues are 718" was wrong by 45%

The engine leaves issues without a band when no rule fires. The count is **718** — and
that number was treated as "718 issues stuck". It is not. A session measurement found that
**255** of them were already being sent to a *blocking* column (usually "needs
information"), leaving about **400** that have no band, no suggested column, are complete,
and carry no human-review flag.

> **Declared:** that 255/400 arithmetic has **no committed producer** in this repository,
> so by our own taxonomy (`STATUS.md`) it is **Clase C** — a local measurement, not
> verifiable from the artifact. Only the 718 is reproducible (`decide()` returns
> `band: None`). Promoting the rest to a module is an open unit, not a footnote we forgot.

The lesson generalises: **a count is not a finding until you ask what it excludes.**

### 3.2 The clusters do not collapse — concentration is accumulation, not duplication

If 99 issues land in `gentle-shell/extensions`, the obvious hope is that they are one
problem reported 99 times, and that grouping gives you a short list. We measured it with
two independent instruments, and both say no:

| Cluster | Issues | Distinct evidence signatures | Largest repeated group |
| --- | ---: | ---: | ---: |
| `gentle-shell` `extensions` | 99 | 58 | 3 |
| `gentle-shell` `lib` | 98 | 56 | — |
| `gentle-ai` `internal/cli` | 55 | 41 | — |
| `gentle-shell` `tests` | 39 | 18 | — |
| `gentle-ai` `docs` | 35 | 12 | — |

Near-duplicate title analysis agrees: across those clusters, only **4** groups of similar
titles exist, all of size 2–3 — and every one of them is a feature request, not a bug.
Duplicate *features* are ordinary (several people want the same feature); duplicate *bugs*
are rare.

So a directory carrying many reports is carrying many **different** problems. That is a
claim about where problems accumulate, not about a shared cause — which is exactly why
Module E reports location and never causality. And the honest boundary: **absence of
evidence is not proof of distinctness.** An issue carrying no signature is uncorrelated,
not established as different.

Both of these measurements are in `report-concentration.md`, under "Do the clusters
collapse?", produced by the module itself.

## 4. What it cannot say

Not "not yet" — **cannot**, for structural reasons:

- **No priority, no severity, no "most important first".** The data has no deterministic
  proxy for impact: no SLA, no severity field, no affected-user count, no revenue. Any
  priority number would be invented, and an invented priority is worse than none, because
  someone would act on it.
- **No causality.** Co-location is not a shared root cause (§3.2 is the evidence).
- **No accuracy claim.** We have never measured whether the engine's P0/P1 suggestions are
  *correct*, because that requires a human-labelled sample and nobody has labelled one.
  That is decision D-010 and it still binds. What the engine claims is that its output is
  **reproducible and explainable** — every band comes with the rule that produced it.
- **No learning.** The system accumulates decisions; it does not train on them (D-025).
  Rules change when a human edits `db/rules.py`, never on their own.
- **No coverage of the 770 issues that name no path.** No rule reaches them; they need a
  human read. They are counted in the report rather than implied away.

## 5. What it will never do

The read-only invariant is enforced by a check that fails the build, not by discipline:
`python3 tools/readonly_check.py`. It scans every Python file in the repository for writes
to anything outside it — HTTP verbs, mutating `gh` subcommands, `git push`, raw
`http.client` (banned outright) — and it exempts exactly one call, a `POST` to
`127.0.0.1` in the board's own test suite.

`DECISIONS.md` D-036 records the correction that mattered: the invariant is about
**writes, not HTTP**. An earlier version banned HTTP clients wholesale, which conflated a
proxy with the rule. Reads are how this project gets its inputs.

## 6. How it checks itself

Five mechanisms, because the first four all caught real defects in the fifth:

- **Pinned inputs** (`tools/vendor.py`, D-035). The audited repositories are pinned by full
  commit hash in one place. Re-running the setup cannot silently change a figure. When we
  discovered a `git pull` was doing exactly that, it explained a published count that had
  moved on its own.
- **Determinism check** (`python3 tools/determinism_check.py`). Every generated report has
  a digest, recomputed from the same data under two different hash seeds and compared.
- **A figures guard** (`python3 tools/figures_check.py`). Published counts are written in a
  machine-readable form — `marker → N/N` — and the guard re-runs the producer and compares.
  It exists because a published count went stale twice, each time in a file nobody had
  looked at.
- **The gate** — `python3 tools/verify_all.py` → 10/10 for the fast gate.
- The same gate with `--full` → 12/12.
- **CI** on every push, in a clean environment with the pinned inputs fetched from
  `raw.githubusercontent.com` at the exact commit.

## 7. How to run it

```
git clone https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant
cd Gentle-AI-Maintainer-Assistant
./sync-products.sh              # fetch the audited repositories at their pinned commits
python3 tools/verify_all.py     # the gate
python3 modules/completeness.py # any module; each writes one report at the root
python3 board/server.py --ingest --port 8770   # the board, at http://127.0.0.1:8770/
```

Needs Python 3.12+. Reads nothing outside your machine except the pinned fetches.

## 8. What we do not know about our own tool

Stated plainly, because a reader deserves it more than we deserve to look finished:

- **No human has ever operated it.** The board records **zero** human decisions. The
  figures above are measurements of your repositories; they are not evidence that anyone
  found them useful. We are not claiming a service we have never watched being used.
- **The reviews that guard changes have a wall.** A high-tier four-lens review is
  relayed through the host with a bound of roughly sixteen minutes; two units today
  exceeded it and remain reviewed-by-nobody. Varying the candidate size in half did not
  move the wall, so the bound is the constraint, not the content.
- **Digest values are not covered by the figures guard.** A declared gap; when one drifted
  it was caught by reading the output, not by a check.
- **The single entry point and the widened scan have no tests.** The tools exist; the tests
  of the tools do not.
- **The reviews inspect the change, not the state of the world.** Four lenses passed over
  two documents while a true datum had been deleted from them with a false justification.
  It was found by opening the application, not by review.

## 9. Ideas worth stealing, even if you never run this

- **Pin your inputs in one place.** A count that depends on the day you ran it is not a
  figure. Put the commits in one file and make the fetch fail loudly.
- **Make your claims machine-readable.** We write counts as `marker → N/N`, so a script can
  re-run the producer and compare. A prose guard that guesses at attribution gets switched
  off, which is worse than no guard.
- **A failed search is not proof of absence.** Verifying "no command produces this value"
  requires enumerating the producers, not grepping for the value — a runtime-computed
  number has no literal anywhere. We deleted a true datum by getting this backwards.
- **Keep the strong evidence apart from the weak.** Class A (a recorded deletion) and
  Class B (an unresolved reference) are reported separately so that 54 verifiable rows do
  not get read as 209.
- **Put the instrument's limits inside the artifact.** "Absence of evidence is not proof"
  belongs in the report, not in the author's head.
- **Separate the decision from its explanation.** The engine's rules are one function
  returning a decision; the board's explanation layer imports none of the rule internals.
  It cost a refactor and repaid it the first time the two had to be tested apart.

## 10. If something here is wrong

Say so, ideally with the command that shows it. Every figure in this document has one, and
a figure without a producer is a bug in this project, not a rounding error.
