# Gold Standard Calibration Dataset: Candidate P0 and P1 Rule Matches

> **Purpose:** Ground-truth audit artifact recording every issue currently flagged by the deterministic rules as candidate P0 (`rule:candidato_p0_requiere_revision_humana`) or P1 (`rule:hard_crash`) across the ecosystem census (`issues.json` / `db/exp.db`).

> **Governance invariant:** deterministic P0 is strictly **"candidato P0, requiere revisión humana"** — a candidate requiring human review, never an autonomous final decision. Human maintainers retain final authority; the `veredicto_humano` field is left `pendiente` on purpose.

> **Reproduce this list:** `python3 db/rules.py` recomputes the counts; `python3 test_rules.py` re-verifies the named regression cases.

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

Total: 2

---

### gentle-ai#3190
- **Title:** `bug(review): review start aborts on Windows when Go runtime cannot allocate memory`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-ai/issues/3190
- **Deterministic Rule:** `rule:hard_crash` 
- **Trigger Snippet:** `d. - Attempt 2 aborted with exit code 2 and `fatal error: runtime: cannot allocate memory`. - The Go stack ide`
- **veredicto_humano:** pendiente

---

### gentle-shell#1606
- **Title:** `bug(skill-registry): unhandled async EMFILE from directory watcher crashes pi on startup`
- **Issue Link:** https://github.com/Gentleman-Programming/gentle-shell/issues/1606
- **Deterministic Rule:** `rule:hard_crash` 
- **Trigger Snippet:** `p ### Problem  `pi` exits on startup with an uncaught exception coming from the skill-registry extension's d`
- **veredicto_humano:** pendiente

---

## 3. Released False Positives (Corrected by Negation & Context Safeguards)

These issues were flagged by earlier, unguarded regexes and are **no longer flagged** after the negation and context safeguards. They are recorded here for auditability, with the reason and the regression test that locks the behavior in.

| Issue | Trap | Reason released | Regression test |
| --- | --- | --- | --- |
| `gentle-ai#5007` | `No workaround data loss: the local store is intact` | Explicit negation (`no ... data loss`) | `test_rules.py` §2, §4 |
| `gentle-ai#4792` | `No observed runtime failure or data loss is claimed.` | Explicit negation (`no observed ... data loss`) | `test_rules.py` §2, §4 |
| `gentle-ai#2628` | `from being silently dropped to being rejected` | Fix description, not a defect | `test_rules.py` §3, §4 |
| `gentle-ai#4807` | `It is a fork bomb, not a deadlock.` | Negated deadlock | `test_rules.py` §6, §4 |
| `gentle-ai#5094` | `the review is deadlocked` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-ai#4286` | `The two rules deadlock each other.` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-ai#2366` | `ordinary review denials deadlock the agent` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
| `gentle-shell#1087` | `sdd-remediate run can deadlock before phase work` | Metaphorical deadlock, no process/thread context | `test_rules.py` §6 |
