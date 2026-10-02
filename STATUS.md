# STATUS.md — Gentle AI Maintainer Assistant, Project Status

> **Current state, what is done, what is missing, and what the owner must decide.**
> Updated on every delivery. The hash cited below is a real commit.

---

## Current Status: Delivery 5 — Medición, simulador y determinismo explicado (en revisión)

* **Delivery 4 commits:** pendientes de commit (ver abajo).
* **Este lote (Delivery 4 + 5) todavía NO está commiteado.** Se congela acá para pasar el ciclo de revisión nativa, y recién después se commitea.
* **Checks:** `python3 tools/verify_all.py --full` → **10/10**.
* **Tests:** `test_rules.py` 125 · `test_board.py` 76 · contratos 12.

### Qué entró en este lote

* **Tablero Kanban local** (`board/`), tres tableros separados por aplicación, puerto 8770, solo localhost. Detalle en `BOARD.md`.
* **Filtro por etiquetas** con contador por tag, y la corrección de un bug real: `NOT (band = 'P1')` con `band IS NULL` descartaba toda la zona gris por el `NULL` de SQL. Ahora `COALESCE` en cada condición y un test que exige que apagar un tag quite exactamente lo que el tag cuenta.
* **Severidad proporcional** de `falta info` (`N/T`), con color y tooltip.
* **`explain.py` + simulador de reglas** («Probar una regla»): muestra qué habría decidido el motor, con qué regla y sobre qué evidencia. No escribe nada. Un test compara el explicador contra el motor en 400 issues para que no derive.
* **Modal «Determinismo y límites»**: qué es determinista y cómo se comprueba, qué no y por qué, si el sistema aprende (no), y qué falta.
* **`TAGS.md`** y **`GLOSSARY.md`**: explicación detallada de cada etiqueta.
* **Medición**: `tools/precision_report.py` (falsos negativos de P0/P1, precisión por regla con `n` e intervalo de Wilson) y `tools/label_sample.py` → `label-sample.md` (120 issues estratificados, 12 P0 y 13 P1, sin contaminar).
* **Determinismo verificado**: se extendió `tools/determinism_check.py` a la proyección derivada del tablero, que antes no estaba cubierta.

### Estado de las revisiones nativas — nada de esto está "cerrado"

| Unidad | Contenido | Revisión nativa |
| --- | --- | --- |
| **C1a** — dominio y auditoría (`2d59094`) | 665 líneas | **línea abierta**, 4 lentes pendientes |
| **Unidad de índices y chequeos** (375 líneas) | docs + `tools/determinism_check`, `metrics`, `readonly_check` | 4 lentes **corrieron** → 1 CRITICAL (contradicciones de recuentos, corregidas en 8 líneas). **Validación dirigida PENDIENTE** por el defecto D-028 |
| **C1b, C2, C3** | el resto del lote | sin revisar todavía; se revisan como rangos commiteados |

* **Hallazgos reales encontrados por las lentes:** **6 CRITICAL**, todos introducidos por este trabajo y todos corregidos — path traversal en `/static/`, 500 por input inválido, README con el árbol roto, actor forjable, carrera en `move_card`, y contradicciones de recuentos en la documentación. Ninguno llegó a un revisor humano.
* **Línea estacionada:** `review-7cb7f5fd9a7b5c39` (C1a) quedó en `action: recover` / `scope_changed` porque HEAD avanzó mientras sus lentes corrían. Contiene **hallazgos ya producidos y no leídos** sobre `board/core.py`. Desbloquearla es una operación **del host**: ni el canal de captura ni la operación `recover` de la fachada pueden completarla desde acá sin valores nativos que no se deben inventar.
* **Regla corregida (D-027):** **un commit sin revisar por vez.** Commitear → revisar el rango → no commitear nada más hasta que cierre.
* **Validación dirigida pendiente (D-028):** la corrección de esas contradicciones está aplicada y verificada por tests, pero **no tiene cierre formal**: la fachada no puede entregar el slot `provider_targeted_validator`. Se declara **pendiente**, no cerrada.
* **Precisión sin medir**: el instrumento existe, las etiquetas humanas son 0. La cifra está pendiente de que una persona etiquete.
* **Vista de sistema, pasada de LLM sobre la zona gris, propuestas de regla, `REPORT.md` y modo sombra**: no implementados.

### Por qué sigue sin commitear a propósito

Commitear mueve la proyección del workspace e invalida la revisión en curso. El orden es: **congelar → revisar → commitear**. Los dos errores anteriores (commitear antes de revisar, y editar después de congelar) fueron el mismo error visto de dos lados.

---

## Delivery 4 — Tablero Kanban local, tres tableros separados (en pruebas)

* **Delivery 1 commits:** `ad7b6b1` (engine corrections, promise contract, decision log), `fc34e85` (privacy redaction + checker).
* **Delivery 2 commits:** `b07b282` (modules A/B/C, reports, docs), `8081020` (tier naming consistency).
* **Delivery 3 content commit:** `7638f09` (Module D, report determinism fix, `tools/determinism_check.py`).
* **This STATUS revision:** a documentation-only commit that follows the Delivery 4 content commit.
* **Date:** 2026-10-02
* **Checks:** no se repiten acá: el primer bloque de este documento es el único que declara recuentos vigentes.
* **Figures:** recomputed by `python3 tools/metrics.py`; nothing hardcoded.

---

## Delivery 4 — Tablero Kanban local (en pruebas)

Consola local en `http://127.0.0.1:8770/`, **un tablero por aplicación**, sin mezclar. Puerto distinto del 8000 que ocupa el cockpit del CRM de ByBusiness. Detalle completo en `BOARD.md`.

* **Modelo:** estado en SQLite local (`db/board.db`, fuera de git) + log **append-only**. `card_state` y `human_labels` son cachés reconstruibles desde eventos; `tools/board_rebuild_check.py` lo demuestra rompiendo las cachés y reconstruyéndolas.
* **Regla de diseño central:** el motor **solo sugiere columnas de bloqueo** (`falta_info`, `revision_humana`). Nunca sugiere `listo_mantener` ni `en_manos`: promover trabajo hacia un maintainer es un juicio humano. Verificado por tests.
* **Distribución derivada** (antes de que nadie mueva nada, snapshot `39553742aa7bf1ea`): `gentle-ai` 733 = 492 entrada + 231 falta info + 10 revisión; `gentle-shell` 424 = 272 + 146 + 6; `engram` 71 = 60 + 7 + 4. Ninguna tarjeta arranca en columnas positivas.
* **Sin red saliente:** `tools/readonly_check.py` ahora falla ante `http.client`, `urllib.request` o `requests` en cualquier parte del proyecto. El tablero no puede escribir en GitHub porque no tiene cliente HTTP.
* **Solo localhost:** el servidor rechaza cualquier interfaz que no sea `127.0.0.1`. Sin autenticación, a propósito.
* **Auditoría del diseño:** decisiones D-018 a D-023 en `DECISIONS.md` (estado local, tableros separados, solo bloqueos, log append-only, stdlib+puerto, UI en español).
* **No validado:** el tablero no tiene uso real todavía; las señales de los Módulos B, C y D **no** se muestran aún como badge por tarjeta (siguen a nivel de reporte).

---

## Delivery 3 — Module D and a real determinism defect

* **Module D — possibly obsolete issues** (`modules/obsolete.py` → `report-obsolete.md`), checked against the vendored commits `gentle-ai@9dfe17d8`, `engram@0f79d5e`, `gentle-shell@7a27c1c0`:
  * **Class A (verifiable):** the referenced path was deleted in the repository's own history → **54 issues** (34 `gentle-ai`, 20 `gentle-shell`). Examples: references to `internal/components/sdd/inject.go`, `internal/assets/opencode/...`, `internal/components/communitytool/rtk_runtime.go`.
  * **Class B (weak, explicitly not an obsolescence claim):** an unresolved path, flag or symbol with no deletion record → 155 issues. Most belong to another repository or to the installed package layout (e.g. `--claude-code`, `assets/agents/sdd-apply.md`).
  * Every row cites the token, the sentence and the commit; all are "posible, requiere verificación" with `veredicto_humano: pendiente`.
* **Defect found and fixed while validating:** Python randomizes string hashing per process, so iterating a `set` of tokens produced a different pair order in `report-duplicates.md` on every run. Ordering is now total (`-score, tier, pair keys`) and set iteration is sorted. `tools/determinism_check.py` runs each module under two `PYTHONHASHSEED` values and fails if a report changes — all four reports are byte-identical. Without this, every reproducibility claim in the project would have been hollow.
* **Not validated:** no module has human-verified precision; Class A still needs maintainer judgment per issue.

---

## Delivery 2 — Mechanical modules (this delivery)

Three read-only modules that need **no human labels** to be useful. Full method, embedded source and limits: `MODULES.md`. Reports: `report-completeness.md`, `report-duplicates.md`, `report-cross-links.md`. Regenerate with `python3 tools/run_reports.py`.

* **Module A — completeness.** Parses each repository's real `.github/ISSUE_TEMPLATE/*.yml` and checks whether an open report carries the required fields. Result: 1,114 issues matched to a template, 1,043 filed through the form, **313 missing at least one required content field**; 71 issues outside the form are excluded and reported separately. Attestation checkboxes are reported apart from triage-critical content.
* **Module B — probable duplicates.** Deterministic evidence only: exception/panic class, error code, `file:line` frame, quoted error string, exit code, normalized titles. Result: **108 candidate pairs, 7 with strong evidence**, 101 weaker. Tiers are named "strong/weaker evidence", never "duplicate"; the report never closes or merges.
* **Module C — cross-repo links.** A proposed link requires an explicit `repo#N` that resolves to an open issue. Result: 48 explicit references, **15 resolving**, 33 not resolving, 81 unnumbered `owner/repo` references, 914 bare mentions. It reframes `AUDIT.md`'s "345 mentions": the actionable subset is small, and a mention is not a dependency.
* **Guard:** `tools/readonly_check.py` now also scans `modules/`. No module writes to `cross_refs`, to the dataset, or to GitHub.
* **Not validated:** none of the three modules has human-verified precision yet. They are deterministic and useful for triage reading, but a maintainer must judge the reports.

---

## Delivery 1 — Post-audit corrections, promise contract and decision log

* **Delivery commit:** `ad7b6b1` — `feat(triage): widen crash vocabulary, recover title_prefix, fix rule order, flag hard signals`
* **Privacy correction commit:** `fc34e85` — `fix(privacy): redact maintainer handle from snapshot, add privacy check`
* **Tests:** `125/125` rule tests, `12/12` contract tests, read-only check green.
* **Figures:** recomputed by `python3 tools/metrics.py`; nothing hardcoded.

---

## What is done

### Phase 1 — Foundations
* Deterministic engine `db/rules.py`, sanitized snapshot `issues.json` (1,228 issues, no personal data), JSON Schema contracts, MIT license.

### Phase 1.1 — Rule hardening
* Negation and context safeguards; candidate-P0 governance invariant enforced by the schema.
* Human-review gold set `gold-p0-p1.md` with `veredicto_humano: pendiente`.

### Phase 1.2 — Read-only adversarial audit
* `AUDIT.md` audited H1–H10 and the P0–P3 bands over the full corpus with a deterministic `sha256(slug#number) mod 5` split (held-out group 0 = 231 issues, exploration = 997).
* H1, H2 and H5: 0 violations. H3, H4, H6, H7, H8: **not auditable with this dataset**. H9 and H10: detailed findings.

### Delivery 1 — Corrections and governance (this delivery)
* **Crash vocabulary widened:** `crashes`, `uncaughtException`, `Go runtime panic`, `fails to start`, `out of memory`, `OOM killer`. Generic `cannot start` deliberately excluded (blocked workflow, not a crash). P1 went from 2 to 17 issues.
* **`title_prefix` recovered** from the title when the ingested value is empty (leading backtick, `[Automated provider defect]`).
* **Rule order fixed:** an explicit `docs:`/`chore:` prefix now wins over a conflicting `enhancement` label (`gentle-ai#5168` is P3).
* **No auto-promotion:** a hard signal under `feat:`/`docs:` keeps its band and is flagged by `requires_human_review()` — 26 issues (17 loss, 9 crash).
* **H9 now fires:** workaround detection widened; `bypass`/`mitigation` removed. 4 real demotions.
* **New governance artifacts:** `PROMISES.md` (claim → evidence → status → gap), `DECISIONS.md` (12 decisions with alternatives), `tools/metrics.py` (recomputes every figure), `tools/readonly_check.py` (read-only invariant).
* **Docs aligned:** `README.md`, `AGENTS.md`, `EVALUATION.md`, `OBSERVABILITY.md` all carry the recomputed figures and point to the promise contract.

### Delivery 1.1 — Privacy correction
* The snapshot was re-audited for personal data. One maintainer handle inside an issue body (`gentle-ai#3312`) was found and redacted to `@[maintainer]`.
* The band/rule digest before and after the redaction is identical, so no rule depends on the handle.
* `tools/privacy_check.py` now verifies: no `author`/`user`/`login`/`email` field, no forbidden maintainer handle, no non-placeholder email address.

---

## Current figures (recomputed, not written by hand)

| Metric | Value |
| --- | --- |
| Open issues | 1,228 (`gentle-ai` 733, `gentle-shell` 424, `engram` 71) |
| Resolved deterministically | **510 (41.5%)** |
| Residual grey area | **718 (58.5%)** |
| Candidate P0 | 14 |
| P1 | 17 |
| P2 | 399 |
| P3 | 80 |
| Flagged for human review | 26 |

> Coverage is a census, not a correctness measure. **Precision of the post-audit rules is pending human validation.**

---

## What is NOT validated

* **No precision figure for the post-audit rules.** The crash vocabulary and rule order changed after the audit; both are pending a fresh human-labelled sample. The README states this explicitly and claims no improvement.
* **Grey area not run end-to-end.** The two-pass LLM pipeline was run only on the 90-issue calibration sample.
* **Cross-repo linking incomplete.** 345 issues mention another repository with no structured link.
* **Mechanical modules, shadow mode and the labelling tool are not implemented.** Tracked in `PROMISES.md` §4.

---

## What is missing (next, in planned order)

1. **Señales por tarjeta (Módulos B/C/D):** hoy solo banda, regla, flag de mirada humana y campos faltantes del Módulo A se muestran en la tarjeta. Duplicados, enlaces cruzados y obsolescencia siguen a nivel de reporte.
2. **Vista de sistema:** agregación por clase raíz (313 reportes con los mismos campos faltantes = un problema de plantilla, no 313 tareas), con límites de WIP y envejecimiento por columna. Es lo que hace que el tablero siga sirviendo a los tres meses.
3. **Métricas desde etiquetas humanas:** el tablero ya produce el `veredicto_humano`; falta el script que calcule falsos negativos de P0/P1 y precisión por regla con su `n`. Es lo único que convierte los "pendiente de validación" en hechos medidos.
4. **`REPORT.md` para maintainers** (plan item e): máx. 15 ítems por sección, todos `verificado_por_humano: no` hasta que se revisen.

El orden se puede reordenar solo con una decisión registrada en `DECISIONS.md`.

---

## What Rafael must decide

| # | Decision | Options | Blocks |
| --- | --- | --- | --- |
| 1 | Reorder the plan (labelling tool first, then modules)? | keep the proposed order / move shadow mode first / other | nothing today; the default is the proposed order |
| 2 | License | MIT is in place; confirm or change | nothing today |
| 3 | External contact / publishing | not requested; the tool stays internal until Rafael approves | any contact with maintainers |
| 4 | Fresh labelled sample | Rafael labels ~100–150 issues | every precision claim |

No question above blocks continued development; work proceeds on the proposed order until Rafael says otherwise.

---

## Constraints in force

* Read-only on third-party repositories; verified by `tools/readonly_check.py`.
* No maintainer names or person-level metrics.
* No `veredicto_humano` filled by the tool; every entry stays `pendiente`.
* No hardcoded figures in code or docs; everything is recomputed or cited.
* No irreversible operation without asking: no data deletion, no history rewrite, no force-push.
