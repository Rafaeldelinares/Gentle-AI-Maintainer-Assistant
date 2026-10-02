# Gold Standard Calibration Dataset: Candidate P0, P1 and H9 Demotions

> **Purpose:** Ground-truth audit artifact listing every issue the deterministic engine currently flags, so a maintainer can adjudicate it.

> **Governance invariant:** deterministic P0 is strictly **"candidato P0, requiere revisión humana"** — a candidate requiring human review, never an autonomous final decision. The `veredicto_humano` field is left `pendiente` on purpose; the tool never fills it.

> **Reproduce this list:** `python3 db/rules.py` (counts) and `python3 test_rules.py` (named regression cases). Counts: 14 candidate P0, 17 P1, 4 P2-from-H9.

> **Status:** these are candidates. None has been confirmed by a maintainer. Precision of the P1 vocabulary is **pending human validation** (see `PROMISES.md`).

---

## 1. Candidate P0 Issues (`rule:candidato_p0_requiere_revision_humana`)

Total candidates: 14

---

### gentle-ai#4917
- **Title:** `A corrupt custom-agents.json silently drops the registry entry of a successful install`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4917
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `A corrupt custom-agents.json silently drops the registry entry of a successful install T`
- **veredicto_humano:** pendiente

---

### gentle-ai#4795
- **Title:** `bug(opencode): engram plugin adapter still ships V1 shape — fails OpenCode 2.x loader (no default export)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4795
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `etup })`).  ### Impact  - Passive capture is silently lost: OpenCode session/prompt events never reach`
- **veredicto_humano:** pendiente

---

### gentle-ai#4701
- **Title:** `bug(repo): contributor-filed issues never receive the form-declared status:needs-review label — triage gate never starts`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4701
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `ad-back showed `labels: []`. The labels were silently dropped because the creating actor has no `triage` p`
- **veredicto_humano:** pendiente

---

### gentle-ai#4474
- **Title:** `bug(review): approved closure lists advisory findings without their claim text, and the acknowledgement deletes the only store that had it (2.7.0)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4474
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `UX report; this report isolates one concrete data loss on the `claude-code` runtime with the store`
- **veredicto_humano:** pendiente

---

### gentle-ai#4282
- **Title:** `bug(doctor): engram:reachable names only two persisted configs and reports healthy when three declare Engram`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4282
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `figs declare an Engram MCP entry. One config silently drops out of the reported set, and which one drops`
- **veredicto_humano:** pendiente

---

### gentle-ai#4031
- **Title:** `review and issues: negotiated v2 lifecycle on Pi — 3 escalation rounds, 12 sequential lens runs, opaque admission grammar, receipt invisible after burn`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4031
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `he escalation driver) + worktree SHA-capture data loss (`introduced`). Escalation is terminal; no c`
- **veredicto_humano:** pendiente

---

### gentle-ai#3774
- **Title:** `bug(install/sync): transient atomic-rename denial on Windows aborts the pipeline before 'skills' (last component) and leaves empty skill directories`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/3774
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `es turn one transient lock into total, quiet data loss:  **1. `skills` is the LAST component in the`
- **veredicto_humano:** pendiente

---

### gentle-ai#1829
- **Title:** `fix(theme): theme injection would overwrite TOML/YAML settings files with JSON`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/1829
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `havior  The TOML/YAML settings file would be silently overwritten with `{"theme":"gentleman-kanagawa"}` JSON,`
- **veredicto_humano:** pendiente

---

### gentle-ai#787
- **Title:** `fix(opencode): orchestrator agent permission override bypasses top-level sensitive-file read denies`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/787
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `t, but the agent-level `permission` override silently drops those `read` rules.  ### Gentle AI Version g`
- **veredicto_humano:** pendiente

---

### gentle-shell#1044
- **Title:** `Engram tools are never detected when the MCP adapter prefixes tool names (hybrid preflight unreachable + SDD agents silently lose memory)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1044
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `isible consequences, the second being silent data loss of agent memory.  ## Environment  - gentle-p`
- **veredicto_humano:** pendiente

---

### gentle-shell#923
- **Title:** `bug(gentle-shell): framePromptLines consumes the last autocomplete row — single-match slash dropdown renders nothing`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/923
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `appearing once this is fixed.** Today it is silently dropped, so a long list renders five rows and no cou`
- **veredicto_humano:** pendiente

---

### gentle-shell#883
- **Title:** `bug(pi-pretty): FFF native backend is unreachable on Android/Termux — pinned fff-node 0.9.6 ships no android-arm64 binary`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/883
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `ndency pin. The net effect is that pi-pretty silently loses its fastest tool on an entire platform, for`
- **veredicto_humano:** pendiente

---

### gentle-shell#748
- **Title:** `bug(review): host consent prompt outlives its binding TTL, silently drops late answers, and loops START`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/748
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `ost consent prompt outlives its binding TTL, silently drops late answers, and loops START ### Before sub`
- **veredicto_humano:** pendiente

---

### gentle-shell#715
- **Title:** `Shell bar drops extension statuses on narrow terminals (wrap instead of pop) + visibleWidth under-counts wide emoji`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/715
- **Deterministic Rule:** `rule:candidato_p0_requiere_revision_humana` (candidate P0, requires human review)
- **Trigger Snippet:** `en layouts, ~100 cols), the Gentle Shell bar silently drops **all** extension statuses (`ctx.ui.setStatu`
- **veredicto_humano:** pendiente

---

## 2. P1 Issues (`rule:hard_crash`)

Total: 17

---

### gentle-ai#4974
- **Title:** ``bug(install): Pi commands fail through pi.cmd on Windows`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4974
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `solves to that CMD launcher, the process can fail to start even though `pi --version` works in an inter`
- **veredicto_humano:** pendiente

---

### gentle-ai#4878
- **Title:** `[Automated provider defect] bug(sync): gentle-ai.exe missing from go/bin after 'sync' reports success (Windows)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4878
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `ename without `fsync` and can corrupt/revert on crash, but its own text scopes the **self-update**`
- **veredicto_humano:** pendiente

---

### gentle-ai#4816
- **Title:** `[Automated provider defect] bug(opencode): orchestrator calls unavailable tools (question, task) — TypeError crashes session before work begins`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4816
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `available tools (question, task) — TypeError crashes session before work begins ## Observed Behav`
- **veredicto_humano:** pendiente

---

### gentle-ai#4807
- **Title:** `bug(TUI) ResolveTarget can bake another tool's wrapper as the OpenCode target, creating a launcher cycle that fork-bombs`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4807
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `eter process per lap, until the machine runs out of memory.  <img width="2339" height="1323" alt="Image`
- **veredicto_humano:** pendiente

---

### gentle-ai#4677
- **Title:** `bug(cli): bare `gentle-ai` invocation crashes with Go runtime panic (traceback did not unwind completely) during startup dependency detection on Windows`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4677
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `bug(cli): bare `gentle-ai` invocation crashes with Go runtime panic (traceback did not unw`
- **veredicto_humano:** pendiente

---

### gentle-ai#4670
- **Title:** `bug(review): stop-hook and mode status fail on a Windows SMB share while RDD is off (2.9.1)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4670
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `nd phase, but the observable failure is a Go runtime panic.  ### Privacy  This report intentionally omi`
- **veredicto_humano:** pendiente

---

### gentle-ai#3190
- **Title:** `bug(review): review start aborts on Windows when Go runtime cannot allocate memory`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/3190
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `d. - Attempt 2 aborted with exit code 2 and `fatal error: runtime: cannot allocate memory`. - The Go stack ide`
- **veredicto_humano:** pendiente

---

### gentle-ai#2648
- **Title:** `bug(review): commit review hook inserts fabricated/unverified technical narrative into committed markdown`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/2648
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `biendo fallas observadas durante la corrida (crashes de subprocesos, sin causa raiz confirmada).`
- **veredicto_humano:** pendiente

---

### gentle-ai#1828
- **Title:** `fix(agent): uninstall fails for kimi because settings rewrite assumes JSON`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/1828
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `ug Description  `gga uninstall --agent kimi` crashes and exits 1 because the uninstall service un`
- **veredicto_humano:** pendiente

---

### gentle-ai#452
- **Title:** `Generation failed when trying to create your own agent.`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/452
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `eturn any content at all, causing the parser to crash.  <img width="632" height="358" alt="Image"`
- **veredicto_humano:** pendiente

---

### gentle-shell#1620
- **Title:** `fix(quiet-tools): re-rendering an expanded read-with-image result crashes Pi (text.setText is not a function)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1620
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `rendering an expanded read-with-image result crashes Pi (text.setText is not a function) ### Befo`
- **veredicto_humano:** pendiente

---

### gentle-shell#1606
- **Title:** `bug(skill-registry): unhandled async EMFILE from directory watcher crashes pi on startup`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1606
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `nhandled async EMFILE from directory watcher crashes pi on startup ### Problem  `pi` exits on sta`
- **veredicto_humano:** pendiente

---

### gentle-shell#1236
- **Title:** `bug(agents): Agents widget crashes when task model metadata is missing`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1236
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `bug(agents): Agents widget crashes when task model metadata is missing ### Befo`
- **veredicto_humano:** pendiente

---

### gentle-shell#1139
- **Title:** `bug(review): a reviewer child terminated by a signal is reported as a generic pi-failed transport failure`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1139
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `ild killed by `SIGKILL`/`SIGTERM` (or by the OOM killer) cannot report which signal ended it. `exit_`
- **veredicto_humano:** pendiente

---

### gentle-shell#962
- **Title:** `bug(skill-registry): recursive skill watcher crashes Pi with uncaughtException ENOENT when a watched skill subdirectory is removed`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/962
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `bug(skill-registry): recursive skill watcher crashes Pi with uncaughtException ENOENT when a watc`
- **veredicto_humano:** pendiente

---

### gentle-shell#750
- **Title:** `bug(pi-pretty): invalid StubText fallback crashes Pi in MouseRegion.render`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/750
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `bug(pi-pretty): invalid StubText fallback crashes Pi in MouseRegion.render ### Before submitti`
- **veredicto_humano:** pendiente

---

### gentle-shell#644
- **Title:** `bug(extensions): pi-pretty hard-crashes extension load when @heyhuynhgiabuu/pi-pretty is not installed`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/644
- **Deterministic Rule:** `rule:hard_crash`
- **Trigger Snippet:** `bug(extensions): pi-pretty hard-crashes extension load when @heyhuynhgiabuu/pi-prett`
- **veredicto_humano:** pendiente

---

## 3. P2 Issues demoted by Rule H9 (`rule:crash_with_workaround_demoted_to_p2`)

Total: 4

Each of these reports a crash **and** an explicit workaround or retry recovery, so Rule H9 keeps them at P2.

---

### gentle-ai#4809
- **Title:** `bug(pi): CodeGraph child overlay corrupts tools frontmatter into invalid YAML — Pi fails to start`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/4809
- **Deterministic Rule:** `rule:crash_with_workaround_demoted_to_p2`
- **Trigger Snippet:** `s` with a mapping item would catch this.  ## Workaround  Repair the two lines back to a valid list (`
- **veredicto_humano:** pendiente

---

### gentle-ai#3016
- **Title:** `fix(update): honor pnpm for OpenCode plugin upgrades`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/3016
- **Deterministic Rule:** `rule:crash_with_workaround_demoted_to_p2`
- **Trigger Snippet:** `wned tree.  A pnpm-based upgrade is the safe workaround. A proposed fix is prepared in the contribut`
- **veredicto_humano:** pendiente

---

### gentle-shell#1052
- **Title:** `bug(provider): kimi-k3 tool calls fail with 400 'tool_call_id is not found' after compaction or parallel batches`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1052
- **Deterministic Rule:** `rule:crash_with_workaround_demoted_to_p2`
- **Trigger Snippet:** `cription: Kimi Code (OAuth, device flow)  ## Workaround for users today  Use `kimi-coding/kimi-for-c`
- **veredicto_humano:** pendiente

---

### gentle-shell#745
- **Title:** `bug(gentle-shell): /reload crashes Pi — stale session ctx captured in prompt/footer render closures (uncaughtException)`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/745
- **Deterministic Rule:** `rule:crash_with_workaround_demoted_to_p2`
- **Trigger Snippet:** `t is a different instance, not a duplicate.  Workaround until fixed: `GENTLE_PI_SHELL=0` (or `false``
- **veredicto_humano:** pendiente

---

## 4. Released False Positives (kept out by negation and context safeguards)

These issues were flagged by earlier, unguarded regexes and are **no longer flagged** after the safeguards. They are recorded for auditability, with the reason and the test that locks the behavior in.

| Issue | Trap | Reason released | Regression test |
| --- | --- | --- | --- |
| `gentle-ai#5007` | `No workaround data loss: the local store is intact` | Explicit negation (`no ... data loss`) | `test_rules.py` §2, §4 |
| `gentle-ai#4792` | `No observed runtime failure or data loss is claimed.` | Explicit negation (`no observed ... data loss`) | `test_rules.py` §2, §4 |
| `gentle-ai#2628` | `from being silently dropped to being rejected` | Fix description, not a defect | `test_rules.py` §3, §4 |
| `gentle-ai#5166` | `dead-ending the lineage` | Metaphorical dead-end; `build cannot start` is a blocked build, not a crash | `test_rules.py` §6 |
| `gentle-ai#4991` | `RDD assessment cannot start` | Generic `cannot start` deliberately not matched | `test_rules.py` §6 |
| `gentle-ai#5094` | `the review is deadlocked` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-ai#4286` | `The two rules deadlock each other.` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-ai#2366` | `ordinary review denials deadlock the agent` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-shell#1087` | `sdd-remediate run can deadlock before phase work` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |

**Note on `gentle-ai#4807`:** it appeared here in an earlier revision because of its `not a deadlock` phrase. The deadlock trap is still rejected, but the widened vocabulary now detects a **different, real signal** in the same issue (the launcher consumes memory until the machine runs out of memory). It is therefore listed under P1, not released. See `DECISIONS.md` D-006.
