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

## D-016 — Module D separates verifiable obsolescence from an unresolved reference

- **Decision:** Module D reports two classes. **Class A:** a referenced path that exists in the repository's own git history as a deletion and is absent from the current tree — verifiable obsolescence. **Class B:** a path, flag or symbol absent from the checkout with no deletion record — reported as weak evidence and explicitly *not* an obsolescence claim.
- **Why:** the first implementation reported 194 issues, but inspection showed most were misattributions: `--claude-code` is not a gentle-ai flag string, and `assets/agents/sdd-apply.md` belongs to the installed package layout, not the developer checkout. Mixing those with genuine cases (`internal/components/communitytool/rtk_runtime.go`, deleted in history) would have taught the maintainer to ignore the report.
- **Alternatives considered:**
  - *Report every unresolved reference as obsolete:* rejected — it produced a 194-issue list dominated by paths that never existed in this repository.
  - *Drop the weak class entirely:* rejected — the absence of a reference is still worth seeing, and hiding it would make the module silently incomplete.
  - *Check `git log -S` per flag to prove a flag once existed:* rejected as too slow for hundreds of tokens; Class B already labels the uncertainty honestly.
- **Consequence:** Class A lists 54 issues (34 `gentle-ai`, 20 `gentle-shell`); Class B lists 155 issues and is labelled as non-evidence. Every row cites the token, the sentence and the commit.

## D-017 — Module reports must be byte-identical, and a checker enforces it

- **Decision:** every generated report must be identical across processes. Ordering is total (`-score, tier, pair keys`) and any iteration over a `set` of strings is sorted. `tools/determinism_check.py` runs each module twice under different `PYTHONHASHSEED` values and fails if a report changes.
- **Why:** the promise says reports regenerate deterministically. During delivery 3 a real defect surfaced: Python randomizes string hashing per process, so `for token in set(tokens)` produced a different pair order in `report-duplicates.md` on every run. A reviewer regenerating the report would have seen a spurious diff and lost trust in every other reproducible claim.
- **Alternatives considered:**
  - *Set `PYTHONHASHSEED=0` in the runner:* rejected — it hides the defect for direct module runs and depends on the caller.
  - *Commit a checksum without a checker:* rejected — nothing would catch a regression.
- **Consequence:** all four reports are byte-identical across seeds; the check is part of the verification suite and cited under P-43.

## D-018 — El estado del tablero vive local, nunca en GitHub

- **Decisión:** el tablero Kanban mantiene su estado en `db/board.db` (SQLite local). GitHub sigue siendo la fuente de verdad de *qué issues existen*; el tablero es la fuente de verdad de *qué decidió el humano*. No existe camino de escritura hacia GitHub.
- **Por qué:** el proyecto tiene un invariante no negociable de solo lectura sobre repos de terceros. Un Kanban cuyos estados vivieran en GitHub (etiquetas, proyectos, cierres) violaría ese invariante el primer día.
- **Alternativas consideradas:**
  - *Usar GitHub Projects:* rechazado — escribe en el repo ajeno.
  - *Escribir etiquetas "en progreso" desde el tablero:* rechazado — mismo motivo, y además crearía estado público que un maintainer no pidió.
- **Consecuencia:** el traspaso a un maintainer se hace con una planilla que una persona copia, no con una llamada a la API.

## D-019 — Un tablero por aplicación, sin vista conjunta

- **Decisión:** `gentle-ai`, `engram` y `gentle-shell` tienen tableros separados. Las tarjetas nunca se mezclan y no hay vista "todo junto".
- **Por qué:** pedido explícito del dueño. Además es correcto: cada repo tiene su propio formulario, su propio ciclo de release y su propio mantenedor; mezclarlos obligaría a comparar cosas que no se comparan.
- **Alternativas consideradas:**
  - *Un tablero único con filtro por repo:* rechazado — el filtro por defecto termina siendo "todos", y el ruido vuelve.
- **Consecuencia:** verificado por `test_board.py`, que comprueba que cada tablero solo contiene tarjetas de su repositorio.

## D-020 — El motor solo puede sugerir columnas de bloqueo

- **Decisión:** el motor sugiere `falta_info` (falta un campo requerido del formulario) o `revision_humana` (candidato P0, o señal dura bajo prefijo no-bug). **Nunca** sugiere `listo_mantener` ni `en_manos`.
- **Por qué:** promover trabajo hacia un maintainer es un juicio humano. Si el motor pudiera mover hacia adelante, el tablero reproduciría el problema que el proyecto existe para resolver: ruido con apariencia de autoridad.
- **Alternativas consideradas:**
  - *Auto-clasificar todo con el motor:* rechazado — convierte una sugerencia en una decisión.
  - *Permitir que el motor sugiera "listo" cuando la banda es P2/P3:* rechazado — una banda baja no significa que el reporte esté triado.
- **Consecuencia:** `SUGGESTIBLE_COLUMNS` es una constante cerrada y `test_board.py` verifica que ninguna tarjeta se auto-promueva a una columna positiva.

## D-021 — Registro append-only con proyecciones reconstruibles

- **Decisión:** cada movimiento y cada veredicto se agrega como evento inmutable. `card_state` y `human_labels` son cachés reconstruibles desde ese log, y `tools/board_rebuild_check.py` lo demuestra rompiendo las cachés y reconstruyéndolas.
- **Por qué:** decir "auditable" sin una prueba es una palabra. El chequeo corre sobre copias temporales y también sobre la base viva, sin tocarla.
- **Alternativas consideradas:**
  - *Actualizar el estado en el lugar:* rechazado — se pierde la historia y no se puede auditar ni deshacer.
  - *Guardar solo el estado actual y un log opcional:* rechazado — el log pasaría a ser decorativo.
- **Consecuencia:** el log es la única fuente de verdad; el estado es una vista.

## D-022 — Stdlib, puerto 8770, y solo localhost

- **Decisión:** servidor con `http.server` de la stdlib, UI con HTML/JS sin build, puerto **8770** bindeado a `127.0.0.1`. El servidor **rechaza** cualquier otra interfaz.
- **Por qué:** el puerto 8000 ya lo ocupa el cockpit del CRM de ByBusiness. La filosofía del proyecto es que un revisor pueda leer cada línea: cero dependencias que auditar y cero pipeline de build. Y sin autenticación, exponerlo en la LAN sería un riesgo gratuito.
- **Alternativas consideradas:**
  - *FastAPI/uvicorn:* disponible en el entorno, rechazado por superficie de dependencias sin beneficio para servir JSON y HTML.
  - *Bindear a `0.0.0.0`:* rechazado explícitamente en el arranque del servidor.
- **Consecuencia:** `python3 board/server.py` es todo lo que hace falta para levantarlo.

## D-023 — La UI está en español y es tonta a propósito

- **Decisión:** la interfaz del tablero está en español; toda la lógica vive en Python (`board/core.py`), el HTTP solo traduce (`board/api.py`) y la UI solo pinta.
- **Por qué:** es una consola interna que convive con el cockpit de ByBusiness. Y si una regla de negocio se filtra al JavaScript, quedan dos implementaciones que se contradicen y la mitad deja de ser testeable.
- **Alternativas consideradas:**
  - *UI en inglés:* rechazado — el contexto de uso es español y no es un producto público; los artefactos técnicos del repo sí siguen en inglés.
  - *Lógica de validación también en el frontend:* rechazado — duplica reglas.
- **Consecuencia:** `test_board.py` cubre el dominio completo sin tocar el navegador.

## D-024 — El filtro por etiquetas apaga lo que la tarjeta *lleva*, y es NULL-safe

- **Decisión:** una tarjeta desaparece del Kanban cuando **lleva** la etiqueta que se apagó, sin importar qué otras etiquetas tenga. Las etiquetas son ejes independientes: la banda (`P0`–`P3`, `zona gris`) y las señales (`falta info`, `mirada humana`) no se pisan entre sí.
- **Por qué:** es la única regla que un maintainer puede predecir sin leer el código: "apagué esto, se fue todo lo que tenía esto". Las alternativas (mostrar si tiene *algún* tag activo, o si tiene *todos*) fallan justo en los issues con más de un tag, que son la mayoría del backlog real.
- **El defecto que la motivó:** la primera implementación usaba `NOT (band LIKE 'candidato P0%')`. Con `band IS NULL` (zona gris) esa expresión evalúa a `NULL`, y SQL descarta la fila. Apagar `P0` borraba las 9 tarjetas de P0 **más las 461 de zona gris**. El síntoma que reportó el dueño fue "si hay issues con más de un tag no funciona bien".
- **Alternativas consideradas:**
  - *Mostrar la tarjeta si al menos un tag suyo está prendido:* rechazado — apagar un tag no tendría efecto sobre los issues multi-tag, que es la queja inversa.
  - *Mostrar la tarjeta solo si todos sus tags están prendidos:* es equivalente a la regla elegida, pero enunciada al revés y más difícil de leer.
  - *Filtro inclusivo ("mostrar sólo estos tags"):* rechazado por ahora — agrega un segundo modo y una segunda forma de equivocarse; si hace falta, se agrega como decisión nueva.
- **Garantía verificable:** `test_board.py` exige que, para cada tablero y cada etiqueta, `visibles_sin_filtro − visibles_con_tag_apagado == conteo_de_ese_tag`, y además que la zona gris sobreviva a apagar cualquier banda.
- **Consecuencia:** 76 tests del tablero, y la interfaz muestra "mostrando X de Y" para que el efecto del filtro sea visible y comprobable de un vistazo.

## D-025 — El sistema acumula decisiones humanas pero no aprende de ellas

- **Decisión:** el motor **no** ajusta ninguna regla, banda ni sugerencia con el uso. Los movimientos y veredictos se guardan como etiquetas de referencia para *medir*; cambiar una regla es una decisión de ingeniería escrita a mano, con test y registro en `DECISIONS.md`.
- **Por qué:** si el motor aprendiera de los movimientos, la misma snapshot dejaría de dar el mismo resultado. Dos personas con el mismo backlog obtendrían tableros distintos según lo que hubieran cliqueado antes, y sería imposible auditar por qué sugirió lo que sugirió. Se rompería exactamente el determinismo que `tools/determinism_check.py` acaba de demostrar.
- **La tensión, dicha de frente:** adaptarse al uso y ser reproducible son dos cosas buenas que se pelean. El proyecto elige **reproducible**, con una salida explícita para mejorar (la sección «cómo se cambiaría una regla» de `DETERMINISM.md`).
- **Alternativas consideradas:**
  - *Ajustar pesos con los veredictos (learning-to-rank):* rechazado — sin una muestra grande y held-out, ajustar con decenas de etiquetas es sobreajuste, que es justo lo que la auditoría externa nos marcó. Y volvería el resultado irreproducible.
  - *Reordenar sugerencias según lo que el humano movió antes:* rechazado por el mismo motivo.
  - *No guardar nada:* rechazado — sin etiquetas humanas no hay forma de medir precisión nunca.
- **Garantía verificable:** sobre el mismo snapshot, una base sin decisiones y otra con 40 movimientos y 40 veredictos producen **1.228 de 1.228 sugerencias idénticas**. Está codificado en `test_board.py`: si el motor empezara a aprender solo, el test falla.
- **Consecuencia:** la capa derivada queda determinista y auditable; la capa de medición (precisión por regla desde etiquetas humanas) queda como el próximo paso, declarada como pendiente y no como hecha.

## D-026 — Las reglas no se editan desde la interfaz; se explican y se versionan

- **Decisión:** el tablero **no** permite editar reglas. Ofrece un **simulador** que muestra qué habría decidido el motor y sobre qué evidencia, y el cambio real se hace en `db/rules.py`, con test y decisión registrada.
- **Por qué:** reglas editables y guardadas localmente romperían las dos propiedades ya verificadas. El **determinismo**: la misma snapshot dejaría de dar el mismo resultado según lo que cada uno hubiera editado. Y la **auditabilidad**: el revisor externo no puede leer una regla que vive en una base local, así que no podría verificar nada. Además no habría forma de saber contra qué reglas se tomaron las decisiones pasadas.
- **Alternativas consideradas:**
  - *Reglas en un `rules.yml` versionado, editables desde la UI y commiteadas por quien edita:* es la única variante coherente, y **queda como opción futura**, pero hoy no se justifica: hay que rediseñar el motor para reglas-como-datos (las expresiones regulares como texto son propensas a error), y el simulador ya cubre la necesidad real, que es **entender y diseñar** un cambio.
  - *Edición directa en base local:* rechazado — rompe determinismo y auditabilidad, y el cambio se vuelve invisible para el revisor.
  - *No dar ninguna herramienta:* rechazado — sin forma de ver por qué una regla disparó, discutir una clasificación es adivinar.
- **Garantía verificable:** el simulador no escribe nada (hay un test que comprueba que la actividad humana no cambia al usarlo), y `explain.py` se compara contra la clasificación real del motor en 400 issues: si el orden de las reglas cambia y el explicador no, el test falla.
- **Consecuencia:** 69 tests del tablero. Queda pendiente la pieza que convierte los contra-veredictos humanos en **propuestas de regla** accionables; eso sí es un faltante real y está declarado.

## D-027 — Un lote grande se entrega en commits encadenados, y cada uno se revisa como rango commiteado

- **Decisión:** cuando un lote supera lo que la revisión nativa puede abarcar, se parte en **commits encadenados por unidad de trabajo**, y cada unidad se revisa por separado como **rango commiteado** (`baseRef` completo + `committedOnly`), no como estado del árbol de trabajo.
- **Por qué:** la revisión rechazó el lote completo con `lens_context_budget_exceeded` (4.524 líneas contra las 1.890 que sí pasaron) y no truncó la evidencia: no creó autoridad. La salida que el proveedor prescribe es exactamente ésta.
- **Alternativas consideradas:**
  - *Revisar el árbol de trabajo en unidades lógicas sin commitear:* rechazado — la proyección abarca todo el árbol, así que no se puede aislar una unidad sin commitear el resto, y cualquier edición posterior invalida.
  - *Commitear todo junto y revisar el rango acumulado:* rechazado — es el mismo problema de tamaño, y el contrato dice que el candidato es una unidad de trabajo, nunca la rama acumulada.
  - *Achicar el lote editando para que entre:* rechazado — sería dejar trabajo afuera para que pase una revisión, que es lo contrario del objetivo.
- ## CORRECCIÓN — esta decisión tenía una creencia falsa, y costó caro
  - **Lo que creí:** que "un rango commiteado es inmutable, así que un commit posterior no lo invalida".
  - **Lo que es verdad, medido:** el candidato de una revisión por rango es **`baseRef..HEAD`**, no un rango fijo. El *árbol inicial* sí queda congelado (`initial_review_tree`), pero el candidato **sigue a HEAD**. Al commitear cuatro unidades más, el mismo pedido pasó de **3 a 28 archivos** y el proveedor devolvió `action: recover`, `disposition: scope_changed`.
  - **El costo concreto:** la línea quedó pidiendo una **autorización de recuperación** que es una operación **del host** (`external.authorize_recovery`): el canal de captura la rechaza con `unsupported provider capture operation`, y la operación `recover` de la fachada exige seis valores nativos (`predecessorLineage`, `expectedPredecessorRevision`, `successorLineage`, `disposition`, `actor`, `reason`) de los cuales **tres no se pueden derivar y no se deben inventar**. Los hallazgos de las 4 lentes sobre `board/core.py` quedaron encerrados en el almacén nativo, y **C1a y C1b ya no se pueden revisar por separado**: solo quedó revisable la cola del rango.
  - **La regla corregida, que es la que vale:** **un commit sin revisar por vez.** Commitear la unidad → revisar su rango (`baseRef` = el HEAD anterior) → **no commitear nada más hasta que esa revisión cierre** → recién entonces la siguiente unidad.
  - **Por qué esto no es burocracia:** cinco commits seguidos sin revisar no ahorraron tiempo, lo perdieron: encerraron la revisión más valiosa del lote y dejaron tres unidades fuera del alcance revisable.
- **Consecuencia operativa:** el orden es **commitear la unidad → revisar su rango → seguir con la siguiente**. Eso reemplaza el "congelar → revisar → commitear" que sirve para un candidato único, y explica por qué las dos veces anteriores el mismo error se vio desde dos lados distintos.
- **Aprendizaje concreto de la fachada:** la forma de pedir un rango commiteado por la herramienta es `{"mode":"ordinary","baseRef":"<commit de 40 caracteres completo>","committedOnly":true}`. Sin `mode` falla con un error que habla de Judgment Day; con el hash corto falla como `base-ref-unresolvable`; y si hay archivos sin seguimiento, pide una selección cuyo binding opaco es difícil de reenviar. Para revisar un rango commiteado conviene que esos archivos no estén: `.git/info/exclude` (local, nunca commiteado) los saca del inventario.

## D-028 — La fachada no puede entregar el slot del validador dirigido (defecto abierto)

- **Qué pasa:** el slot `provider_targeted_validator` no se puede completar desde la herramienta. Su binding opaco incluye `\n` embebidos en `fixClassifications[].proof` y en `policyContent`, que requieren un triple escapado; reproducirlo a mano falló **tres veces en dos líneas distintas**, siempre con `mutation_performed: false`.
- **Qué NO implica:** no se pierde ni se corrompe nada. La autoridad no se consume, la corrección queda registrada y verificada por tests, y el estado queda en `targeted_validation_required`. Tampoco es un problema del candidato: el mismo binding falló con contenidos distintos.
- **Qué implica:** la **validación dirigida de una corrección** no se puede cerrar desde acá. El resto del ciclo (lentes, corrección, plan) funciona correctamente.
- **Salidas, en orden de preferencia:**
  1. **Declarar la validación como pendiente**, con esa palabra, en `STATUS.md` y `PROMISES.md`. Es lo que se hace hoy: la corrección está aplicada y verificada por tests, pero sin cierre formal.
  2. Correr el comando nativo que el proveedor renderiza en `submission.argumentTokens`, con el JSON del validador que produce el host relay.
  3. Reportar el defecto a `gentle-ai` (es su repositorio), con la reproducción: mismo slot, dos contenidos distintos, tres intentos, siempre `capture-binding-rejected`.
- **Segundo defecto, del mismo ciclo:** cuando el alcance de una revisión por rango cambia porque HEAD avanzó, el proveedor emite `action: recover` con `disposition: scope_changed` y un slot `external.authorize_recovery`. **Ese slot tampoco se puede ejecutar desde acá**: el canal de captura responde `unsupported provider capture operation: external.authorize_recovery`, y la operación `recover` de la fachada pide seis valores nativos —`predecessorLineage`, `expectedPredecessorRevision`, `successorLineage`, `disposition`, `actor`, `reason`— de los cuales `successorLineage`, `actor` y `reason` no son derivables. Inventarlos está prohibido, así que la línea queda **estacionada** y solo el host puede desbloquearla.
- **Por qué no se arregla acá:** la fachada y el formato del binding son del proveedor, no de este proyecto. Inventar un binding "parecido" sería peor que declarar el pendiente.
- **Consecuencia:** ninguna afirmación de este repositorio dice que esa validación haya corrido. Donde corresponde, dice **pendiente**.

## D-029 — Ninguna cifra se publica sin un comando que la produzca

- **Qué pasó:** al cerrar el hallazgo `R3-status-md-6-critical-claims` (la lente de confiabilidad de C3b escaló por `insufficient_evidence`), aparecieron **dos cifras inventadas** en la documentación del proyecto:
  1. `39553742aa7bf1ea`, presentado en `STATUS.md`, `BOARD.md` y `TAGS.md` como el "snapshot" del que salían los números, y explícitamente como **"reproducible con `python3 tools/metrics.py`"**. **Ningún comando producía ese valor:** `metrics.py` no imprime ningún digest de snapshot.
  2. `2779c866aca75dc4…`, presentado en `DETERMINISM.md` como el "digest idéntico" de la clasificación del motor entre semillas. **Ningún comando lo producía**, y `tools/determinism_check.py` ni siquiera comprueba la clasificación del motor: cubre los módulos A–D y la proyección del tablero.
- **Por qué es grave:** es exactamente la clase de defecto que este proyecto existe para cazar —una cifra hardcodeada presentada como derivada— cometida en su propia documentación de estado y de determinismo. La regla del proyecto ("sin cifras escritas a mano") estaba violada por los archivos que **declaraban** cumplirla.
- **Qué reemplaza a cada una:**
  - El digest del tablero pasa a ser **`b0a61cf3325ef7f1`**, que **sí** emite `python3 tools/determinism_check.py` (junto con los cuatro digests de módulos: A `0c0ccaca24fb234b…`, B `7e63683152dd4e70…`, C `684fcc589d8629bc…`, D `7cd51c438a563c4c…`).
  - La distribución por columna del tablero deja de presentarse como derivada y pasa a **Clase C: medición local, no verificable desde el artefacto**, porque requiere `db/board.db`, que está fuera de git por diseño.
  - El digest del motor se declara **inexistente**: el motor no emite uno propio, y su determinismo se comprueba por la salida derivada, que sí está cubierta.
- **La regla, que es la decisión:** **ninguna cifra se publica sin haber corrido, al menos una vez, el comando que la produce.** Una etiqueta de procedencia al lado de un número no es evidencia: la procedencia hay que **ejecutarla** antes de publicar. Y si un número no tiene comando, se declara explícitamente no verificable en vez de decorarlo con una fuente plausible.
- **Clasificación de cifras que queda vigente:** **Clase A** (derivada por comando desde datos del árbol, legible por un revisor), **Clase B** (solo por ejecución de la suite; explícitamente **no** verificable de forma estática: `assert_test(` aparece 31 veces contra un reporte de 125 porque hay casos en bucles, y `pytest` no recolecta porque son harness propios), **Clase C** (local, no verificable desde el artefacto). `STATUS.md` publica la tabla completa.
- **Aprendizaje lateral:** `verify_all.py` sin `--full` da **8/8** y con `--full` da **10/10**. Declarar solo el 10/10 sin decir el modo es otra forma de cifra sin contexto.
