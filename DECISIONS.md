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

## D-028 — El validador dirigido se rechaza de forma INTERMITENTE (diagnóstico corregido)

> **Este diagnóstico fue refutado por la medición.** La versión anterior de esta entrada afirmaba que el slot `provider_targeted_validator` **no se podía** completar desde la herramienta, y atribuía la causa a un "triple escapado" obligado por los `\n` embebidos en `fixClassifications[].proof` y `policyContent`. **Las dos cosas eran falsas**, y una documentación que miente sobre sí misma es el defecto más caro de todos, porque es la que se cita. Queda registrada la corrección, no el error.

- **Lo que se midió el 2026-10-03:** el mismo tipo de binding, con los mismos `\n` embebidos, fue **aceptado en pronóstico y la corrida nativa pasó**. La validación dirigida corrió, validó una corrección de **8 líneas** sobre `tools/determinism_check.py`, y la revisión cerró en **`approved`** (lineage `review-6d5f3bde4929dde0`). Es decir: **el transporte del binding funciona**, y la causa nunca fueron los saltos de línea.
- **La caracterización correcta:** el rechazo es **intermitente**, no una incapacidad. Hubo **tres fallos previos en dos líneas distintas y un éxito posterior**. Y los fallos **no fueron todos del mismo tipo**:
  1. el más viejo: `capture-binding-rejected` al parsear el binding;
  2. el inmediatamente anterior a hoy: el pronóstico fue **aceptado** y después vino `native-operation-failed`, con el estado mostrando `escalation.cause: targeted_validator_rejected`. O sea: **rechazo en la admisión nativa del validador, no en el transporte** — que es exactamente lo contrario de lo que decía este diagnóstico.
- **Qué NO implica:** nada se pierde ni se corrompe. La autoridad no se consume, la corrección queda registrada y verificada por tests, y el estado queda en `targeted_validation_required`.
- **Qué implica ahora, corregido:** la validación dirigida **sí se puede cerrar desde acá** — se cerró hoy. Lo que queda abierto es una **consecuencia histórica**, no una imposibilidad: la línea de C3b (`review-89d595ab697fb35e`) se detuvo **terminalmente** por un rechazo que hoy sabemos probablemente transitorio, y una línea terminal no se reanuda. Su corrección está aplicada y commiteada (`54a8498`), pero su validación formal nunca se obtuvo.
- **Lo que queda pendiente de verdad, y no es lo mismo que antes:**
  1. la **validación formal del arreglo de C3b** (`54a8498`): se puede conseguir rehaciendo la revisión del rango que lo contiene, o declararla perdida de forma explícita. Es una decisión del mantainer, no un bloqueo técnico.
  2. el **otro defecto del mismo ciclo**, que **sigue en pie y sí es determinista**: cuando el alcance de una revisión por rango cambia porque HEAD avanzó, el proveedor emite `action: recover` con `disposition: scope_changed` y un slot `external.authorize_recovery`, y el canal de captura responde literalmente `unsupported provider capture operation: external.authorize_recovery`. La operación `recover` de la fachada pide seis valores nativos —`predecessorLineage`, `expectedPredecessorRevision`, `successorLineage`, `disposition`, `actor`, `reason`— de los cuales `successorLineage`, `actor` y `reason` no son derivables. Inventarlos está prohibido. Ese slot **no** se puede ejecutar desde acá, y eso está reproducido con el mensaje del proveedor, no inferido.
- **La lección, que es la parte que importa:** un defecto **intermitente** diagnosticado como **determinista** produce conclusiones **falsas y permanentes** en la documentación. La regla que deja: **antes de escribir "no se puede", hay que exigir una reproducción repetida y un mecanismo aislado** — no tres intentos fallidos seguidos. Este diagnóstico se escribió sin haber aislado la causa, y la causa que se inventó era falsa. Es la misma clase de falla que D-029 y D-032: afirmar más de lo que se midió.
- **Salidas, corregidas:**
  1. **Reintentar la validación dirigida cuando falle**, en vez de asumir incapacidad: hoy el mismo slot que se rechazó pasó sin cambios de fondo.
  2. Si vuelve a fallar, **capturar el mensaje literal del proveedor** antes de caracterizar el defecto, y distinguir explícitamente el fallo de transporte del fallo de admisión nativa.
  3. Reportar a `gentle-ai` con la reproducción **corregida**: intermitente, dos puntos de fallo distintos (`capture-binding-rejected` y `targeted_validator_rejected`), y sin evidencia de que los `\n` sean la causa.
- **Por qué no se arregla acá:** la fachada y el formato del binding son del proveedor. Inventar un binding "parecido" sería peor que declarar el estado real.

## D-029 — Ninguna cifra se publica sin un comando que la produzca

- **Qué pasó:** al cerrar el hallazgo `R3-status-md-6-critical-claims` (la lente de confiabilidad de C3b escaló por `insufficient_evidence`), aparecieron **dos cifras inventadas** en la documentación del proyecto:
  1. `39553742aa7bf1ea`, presentado en `STATUS.md`, `BOARD.md` y `TAGS.md` como el "snapshot" del que salían los números, y explícitamente como **"reproducible con `python3 tools/metrics.py`"**. **Lo que estaba mal era el productor citado:** `metrics.py` no imprime ningún digest de snapshot. La cifra era verdadera por otro camino — ver la corrección al final de esta entrada.
  2. `2779c866aca75dc4…`, presentado en `DETERMINISM.md` como el "digest idéntico" de la clasificación del motor entre semillas. **Ningún comando lo producía**, y `tools/determinism_check.py` ni siquiera comprueba la clasificación del motor: cubre los módulos A–D y la proyección del tablero.
- **Por qué es grave:** es exactamente la clase de defecto que este proyecto existe para cazar —una cifra hardcodeada presentada como derivada— cometida en su propia documentación de estado y de determinismo. La regla del proyecto ("sin cifras escritas a mano") estaba violada por los archivos que **declaraban** cumplirla.
- **Qué reemplaza a cada una:**
  - El digest del tablero pasa a ser **`b0a61cf3325ef7f1`**, que **sí** emite `python3 tools/determinism_check.py`, junto con los digests de módulos **A** `0c0ccaca24fb234b…`, **B** `7e63683152dd4e70…`, **C** `684fcc589d8629bc…` y **E** `ef25e084b66efe0d…`.
  - **El digest del módulo D se cita por comando, no por valor.** Depende del **estado de refs locales** de los checkouts, no del commit fijado (ver D-037): un `git fetch` lo mueve sin que nadie edite nada. Su valor de hoy es `8fbadbf59b5fabaa…`, y mañana puede no serlo — publicarlo como fijo sería la misma clase de afirmación que esta entrada prohíbe.
  - La distribución por columna del tablero deja de presentarse como derivada y pasa a **Clase C: medición local, no verificable desde el artefacto**, porque requiere `db/board.db`, que está fuera de git por diseño.
  - El digest del motor se declara **inexistente**: el motor no emite uno propio, y su determinismo se comprueba por la salida derivada, que sí está cubierta.
- **La regla, que es la decisión:** **ninguna cifra se publica sin haber corrido, al menos una vez, el comando que la produce.** Una etiqueta de procedencia al lado de un número no es evidencia: la procedencia hay que **ejecutarla** antes de publicar. Y si un número no tiene comando, se declara explícitamente no verificable en vez de decorarlo con una fuente plausible.
- **Clasificación de cifras que queda vigente:** **Clase A** (derivada por comando desde datos del árbol, legible por un revisor), **Clase B** (solo por ejecución de la suite; explícitamente **no** verificable de forma estática: `assert_test(` aparece 31 veces contra un reporte de 125 porque hay casos en bucles, y `pytest` no recolecta porque son harness propios), **Clase C** (local, no verificable desde el artefacto). `STATUS.md` publica la tabla completa.
- **Aprendizaje lateral:** `verify_all.py` sin `--full` → **10/10** y con `--full` → **12/12**. Declarar solo el conteo del modo completo sin decir el modo es otra forma de cifra sin contexto.

## D-030 — No hay reescritura: tres costuras hexagonales en vez de una arquitectura nueva

- **Contexto:** el mantainer preguntó si rehacer la aplicación con arquitectura hexagonal, porque el ciclo de revisión nativa se había vuelto tedioso.
- **Qué dice la medición, no la opinión:** el esqueleto **ya es hexagonal en la práctica** (`server.py → api.py → core.py/explain.py → rules.py`: HTTP afuera, `modules/common.py` solo la biblioteca estándar, el motor sin conocer el transporte). Y el tedio **no es arquitectónico**: escala con el tamaño del diff y con si es ejecutable. Las unidades de solo Markdown (`6be5093`, `c97874e`) cerraron en tres llamadas con **cero lentes**; una unidad que toca archivos ejecutables exige lentes; y un lote de **4.524 líneas ejecutables fue rechazado** con `lens_context_budget_exceeded`.
- **Las tres fugas reales, medidas:**
  1. `board/explain.py` importa **20 internals del motor** (`RE_*`, `EXPLICIT_*`): depende de *cómo* se implementan las reglas, no de *qué* decidió el motor. El test de 400 issues existe **solo** porque pueden divergir — deuda arquitectónica pagada como test.
  2. `board/core.py` **mezcla dominio y persistencia**: `derive_card`, `missing_severity` y `clean_tags` (puras) conviven con `connect`, `init_schema` y `_ensure_state`, y toda función de dominio recibe un `conn` crudo.
  3. `db/rules.py` importa **`sqlite3`** — dos líneas, ambas dentro de `main()`. El clasificador ya es puro: los tests lo llaman con un diccionario, sin base de datos.
- **Alternativas consideradas:**
  - *Reescribir la aplicación con arquitectura hexagonal:* **rechazada.** Sería el diff más grande posible compuesto **enteramente** de archivos ejecutables (tablero ~1.000 + motor 554 + módulos ~600), del mismo orden que el lote ya rechazado por presupuesto de lentes. No pasaría la revisión, e invalidaría la autoridad de revisión ya ganada para volver a correr la misma herramienta que hoy devuelve `targeted_validator_rejected`.
  - *Reorganizar carpetas en `domain/`, `application/`, `infrastructure/`:* **rechazada.** Hexagonal es una regla sobre la **dirección de las dependencias**, no una estructura de carpetas. Mover archivos sin cambiar quién depende de quién no elimina ninguna de las tres fugas.
  - *No hacer nada:* rechazada — las features pendientes (vista sistémica por clase raíz, señales por tarjeta de los Módulos B/C/D) obligarían a inventar un segundo camino, porque los módulos escriben Markdown y el tablero solo muestra banda, regla y campos faltantes.
- **Decisión:** tres extracciones quirúrgicas, **alcance A** de tres alcances ofrecidos, cada una una unidad de trabajo revisable.
- **Decisión de diseño central — el puerto es aditivo, no un cambio de firma.** `classify_issue_deterministically(row, labels, cross_refs)` devuelve la tupla `(band, cross, rule)` y tiene **seis callers** (`board/core.py`, `board/explain.py`, `db/rules.py`, `test_board.py`, `test_rules.py`, `tools/metrics.py`). Cambiar la firma pondría seis archivos en juego. Se **agrega** `decide(...)` con la decisión estructurada y las funciones actuales quedan como **wrappers finos**. Solo `explain.py` migra en la tarea 1.
- **Oráculo de regresión:** las **figuras publicadas** (`python3 tools/metrics.py`) y los **cinco digests derivados** (`python3 tools/determinism_check.py`) deben ser idénticos antes y después de cada tarea. Los tests nuevos son evidencia adicional, **no** el oráculo.
- **Riesgo principal de la tarea 1, declarado:** si el objeto de decisión omite una señal que el explicador hoy deriva por su cuenta, el simulador se degrada en silencio. Mitigación: capturar la salida actual del explicador como **fixture dorado** antes del refactor.
- **Dónde vive el plan:** `odd/tasks/hexagonal-seams.md`, que está **fuera de git a propósito** — `.gitignore` lo clasifica como estado local de Pi junto a `.atl/` y `.codegraph/`, y un revisor no ve subdirectorios. Por eso la decisión y el alcance quedan registrados acá, en un documento de la raíz.
- **Consecuencia:** ninguna afirmación de este repositorio dice que la aplicación haya sido rediseñada. Se removieron tres fugas medidas, con el **comportamiento de decisión intacto**.

## D-031 — Aceptar deliberadamente la rigidez del digest del fixture dorado de explain()

- **Contexto y hallazgo:** la revisión nativa dejó una observación informativa señalando que el test del fixture dorado (`board/fixtures/explain-golden.json`, comprobado en `test_board.py` §3f) es "frágil" o rígido: cualquier cambio material en `explain()` rompe el digest SHA-256 global (`2170d7307bfd8ddc…`) sin proporcionar un diagnóstico campo por campo de qué issue o propiedad cambió.
- **Alternativas consideradas:**
  - *Relajar la aserción a campos aislados (banda/regla) o ignorar cambios en spans y evidencia interna:* **rechazada.** Si el test solo valida banda y regla, ignora regresiones silenciosas en los extractores de evidencia, negadores o predicados que alimentan el simulador interactivo del tablero.
  - *Construir diffing automático issue por issue dentro del fallo de la aserción:* **rechazada por complejidad innecesaria.** Sobrecarga el arnés de tests para un evento infrecuente cuando ya existen muestras estructuradas en el fixture.
  - *Aceptar deliberadamente el digest duro y acompañarlo con muestras de diagnóstico:* **elegida.**
- **Decisión:** **aceptar deliberadamente la rigidez del digest.** El digest estricto es precisamente el propósito del guard: atrapó un cambio real de banda inyectado que ambos tests de consistencia mutua habían dejado pasar desapercibido.
- **Trade-off y mitigación:** la rigidez es el precio consciente de blindar el explicador contra cualquier desviación silenciosa. Ante una rotura legítima provocada por una evolución deliberada, el desarrollador cuenta con dos herramientas inmediatas:
  1. Las **tres muestras completas almacenadas** en el propio `explain-golden.json` (`sample` con issues representativos: `gentle-ai#5007` [candidato P0 cancelado por negación de data loss], `gentle-ai#4809` [crash demovido a P2 por workaround], y `gentle-ai#4807` [negación de deadlock con crash por agotamiento de memoria]). Las tres pertenecen a `gentle-ai`, lo cual es adecuado porque la cascada de clasificación del explicador es independiente del repositorio (`slug` no ramifica la evaluación de reglas ni la extracción de evidencia, por lo que issues de otros repositorios no añadirían cobertura de ramas). El test comprueba la salida contra las muestras y, en caso de discrepancia, reporta qué `ref` difiere; aislar la propiedad o campo específico que cambió requiere comparar la salida en una sesión interactiva o script de diagnóstico contra el registro almacenado.
  2. Un **comando explícito de regeneración** para recomputar el fixture una vez que la nueva regla o formato fue validado con tests específicos:
     ```bash
     python3 -c "import json, hashlib, sys; sys.path.insert(0, 'board'); import explain; issues = json.load(open('issues.json', encoding='utf-8')); res400 = [explain.explain(it.get('title') or '', it.get('body') or '', it.get('title_prefix') or '', it.get('labels') or [], it['slug']) for it in issues[:400]]; d = hashlib.sha256(json.dumps(res400, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest(); by_ref = {it['slug'] + '#' + str(it['number']): it for it in issues}; s = {ref: {k: v for k, v in explain.explain(by_ref[ref].get('title') or '', by_ref[ref].get('body') or '', by_ref[ref].get('title_prefix') or '', by_ref[ref].get('labels') or [], by_ref[ref]['slug']).items() if k != 'input'} for ref in ['gentle-ai#5007', 'gentle-ai#4809', 'gentle-ai#4807']}; json.dump({'digest': d, 'sample': s}, open('board/fixtures/explain-golden.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False); open('board/fixtures/explain-golden.json', 'a').write('\\n'); print(f'Regenerated explain-golden.json (digest: {d})')"
     ```
- **Qué cambiaría la decisión:** si la evolución de las reglas de clasificación pasara a una fase de alta frecuencia donde la regeneración del digest se convirtiera en un trámite automático que adormezca la atención ante errores reales, o si la muestra de 3 issues resultara insuficiente para diagnosticar discrepancias genuinas, se evaluará almacenar un digest individual por issue o generar un reporte estructurado de diferencias.
- **Consecuencia:** el digest `2170d7307bfd8ddc129824687c7d6e84951f05c25721c62e03ac201b5b20c7a7` se mantiene como invariant de regresión estricto en `test_board.py`.

## D-032 — Los contadores publicados no tienen guardián, y ya fallaron dos veces

- **Qué pasó:** en este trabajo un recuento de tests publicado quedó obsoleto **dos veces**. La primera, `AGENTS.md` declaraba **27** tests de tablero cuando el real era 76 — lo cazó una lente, y una segunda ocurrencia en `OBSERVABILITY.md:179` que la lente **no citó** la encontró un `grep`. La segunda, después de que la tarea 1 subiera las suites a **129** y **79**, los contadores `125/125` y `76/76` sobrevivieron en **cinco** documentos: `AGENTS.md`, `EVALUATION.md`, `OBSERVABILITY.md`, `PROMISES.md` y `README.md`.
- **Por qué es la misma clase de defecto que D-029:** D-029 prohibió publicar una cifra sin haber corrido el comando que la produce. Esto es el paso siguiente y peor: **nada vuelve a correrlo después**. La cifra era cierta el día que se escribió.
- **La lección medida:** arreglar la línea citada **no alcanza nunca**. En las dos veces la ocurrencia sobreviviente estaba en **otro archivo**. El barrido tiene que ser `grep -rn` sobre todo el repositorio versionado, y el número de ocurrencias hay que contarlo antes y después.
- **Qué NO se hizo, y por qué está declarado en vez de disimulado:** la solución sistémica es un guardián que compare las cifras publicadas contra la realidad y falle si divergen. No se hizo en ese momento porque **agregar ese check cambia el recuento de checks de `tools/verify_all.py`, que es a su vez una cifra publicada**: hacerlo obliga a actualizar los conteos del gate en varios documentos, es decir, reproduce el problema mientras lo arregla. Merecía su propia feature, y la tuvo:
- **Actualización — el guardián existe.** Es `tools/figures_check.py`, y está enganchado en el gate como **`published figures match the documents`**. El paso que se llamaba así —y que solo recomputaba las cifras con `tools/metrics.py`— pasó a llamarse **`figure recomputation`**: su nombre afirmaba más de lo que hacía, que es la misma clase de defecto un nivel más arriba.
- **La convención que usa:** un reclamo de conteo se escribe **`rótulo → N/N`** o **`rótulo (N/N)`**, y el rótulo puede ser parte de un token mayor, como una ruta. Eso último no es cosmético: la primera versión exigía la flecha pegada a la palabra y por eso **no cubría los conteos de suite, que son justamente los que se derivaron dos veces**. Con el arreglo, la cobertura pasó de 9 a **16 reclamos canónicos**, todos verificados. Se llegó ahí después de dos intentos fallidos, y los dos están documentados en el propio archivo: chequear todo ratio gritó 44 veces sobre ratios legítimos (`385/997`, `32/34`, `×8/8` de campos faltantes), y atribuir por cercanía al marcador más próximo falló porque la prosa a veces pone el rótulo antes del número y a veces después, y porque `sin --full` **contiene** `--full`. Un guardián que adivina se equivoca; uno que exige la forma no.
- **La prueba de que sirve:** engancharlo movió los conteos del gate de 8 a 9 en modo rápido y de 10 a 11 en completo, así que los documentos quedaron obsoletos **por construcción**. El guardián encontró las cuatro afirmaciones que había que corregir. Un guardián que no caza su propio cambio no sirve.
- **Lo que NO cubre, declarado:** las cifras métricas en prosa, los valores de los digests, y los conteos escritos en otra forma que la canónica. La convención primero tiene que migrar la prosa vieja, y eso es seguimiento.
- **Consecuencia mientras tanto:** todo cambio de recuento de tests obliga a un barrido manual con `grep -rn` sobre el repositorio completo, contando ocurrencias antes y después. Queda escrito para que la próxima vez no lo descubra una lente.

## D-033 — El plan de corrección se declara ANTES de aplicar el cambio

- **Qué pasó:** en la corrección del guardián de cifras (`review-73b34d2b598617bb`) declaré el plan de corrección **después** de haber aplicado y commiteado el arreglo. El proveedor entonces **reemitió el mismo binding**, cuyo `target` es el candidato **previo** a la corrección, y lo rechazó con *"does not carry one non-empty matching provider lineage and target token"*. En la unidad anterior, donde el plan se declaró **primero**, el ciclo cerró limpio.
- **El mecanismo:** el binding del slot de plan está atado al candidato **como estaba antes de la corrección**. Aplicar y commitear primero **cierra esa ventana**: el candidato ya cambió, y el token que el propio proveedor acaba de emitir deja de coincidir.
- **La secuencia correcta, y no es opcional:**
  1. `STATUS` → obtener el slot `correction_plan_required`;
  2. **declarar `correctionLines`** —medido contra el diff real, no estimado— **antes de tocar un solo archivo**;
  3. **recién ahí** aplicar los cambios;
  4. **commitear** (sin commit, la proyección no los ve: devuelve `stop` / `corrected_candidate_unavailable`);
  5. `STATUS` → validación dirigida.
- **Consecuencia de haberlo invertido:** la corrección quedó aplicada, probada y commiteada, pero **su validación dirigida formal no se pudo pedir**, y la línea quedó estacionada. Una revisión posterior cuyo rango contenga esa corrección la cubre en sustancia.
- **Por qué queda escrito acá y no solo en el plan local:** el plan ODD vive en `odd/`, que está **fuera de git**. Una regla que solo existe donde nadie la lee no es una regla, es una intención — que es exactamente lo que D-032 documentó sobre las cifras.

## D-034 — Marcadores de lock obsoletos: el diagnóstico que miente

- **El síntoma:** dos `START` seguidos devolvieron `{"operation":"answer-consent", "outcome":"consent-binding-stale"}` con bindings **distintos**, y `diagnostics.message` = *"expired after 10 minutes without an answer"*. `lineage_created: false`, `mutation_performed: false`. **Parecía una pregunta de consentimiento esperando respuesta humana.**
- **No había ninguna pregunta.** Lo que había eran **dos marcadores de lock obsoletos** —`.git/gentle-ai/REVIEW-MAINTENANCE.lock` y `.git/gentle-ai/review-transactions/v2/LOCK`, ambos de 0 bytes— con la fecha congelada en 11:25/11:29, del ciclo de corrección que murió al cerrarse la ventana del plan (D-033). **Ninguna línea de revisión se escribió durante ~7 horas** y los `START` posteriores no escribieron nada.
- **El diagnóstico era engañoso:** hablaba de consentimiento cuando el problema era de estado. **Un solo error de secuencia explicaba los tres bloqueos del día**: la ventana del plan perdida → marcadores obsoletos → todo lo posterior reportando consentimiento inexistente.
- **La receta, reproducible:**
  1. `stat -c '%n %s bytes %y' .git/gentle-ai/REVIEW-MAINTENANCE.lock .git/gentle-ai/review-transactions/v2/LOCK` → ver tamaño y fecha;
  2. comparar con `date` y con la última línea escrita en `review-transactions/v2/`;
  3. **probar que ningún proceso los sostiene**: recorrer `/proc/[0-9]*/fd/*` resolviendo los symlinks. **Cero dueños = seguro borrarlos** — es verificar que nadie está usando la llave antes de sacarla de la cerradura;
  4. borrarlos → el `START` siguiente **creó la línea al primer intento**.
- **Qué está probado y qué es hipótesis, y la distinción importa:** está **probado experimentalmente** que sacar esos marcadores destrabó el ciclo. Es **hipótesis** el mecanismo (que el flujo compare la antigüedad del marcador contra ahora y se niegue a avanzar si quedó vieja). Se deja dicho para que nadie lo cite como hecho.
- **Un detalle que corrige el diagnóstico inicial:** los marcadores **vuelven a existir** tras un ciclo exitoso —con la fecha del `acknowledge`— así que **su presencia es normal**. Lo que estaba mal era su **obsolescencia**, no su existencia.
- **Aprendizaje lateral:** `pgrep` lista procesos que pueden haber muerto antes de que los mires; para saber si algo está vivo de verdad, `/proc/<pid>/fd` es la fuente.
- **Qué reportar a `gentle-ai`:** no hay auto-recuperación de marcadores obsoletos, y el diagnóstico apunta al lugar equivocado. Un `consent-binding-stale` que en realidad es un estado trabado costó horas.

## D-035 — Los inputs auditados se fijan, y en un solo lugar

- **Qué pasó:** `sync-products.sh` clonaba y después hacía `git pull --ff-only origin main`. O sea: **traía lo que hubiera hoy en upstream**, mientras `MODULES.md` y los reportes citan commits concretos —`gentle-ai@9dfe17d8`, `engram@0f79d5e`, `gentle-shell@7a27c1c0`—. Reejecutar el setup documentado y regenerar los reportes **habría movido todas las cifras de completitud y obsolescencia en silencio, bajo las mismas citas**.
- **Por qué es la misma clase de siempre:** es D-029 un nivel más abajo. No es una cifra sin comando: es un **comando cuyo resultado depende del día en que lo corrés**. Una promesa de reproducibilidad que depende de lo que upstream tenga hoy no es una promesa de reproducibilidad.
- **Cómo se forzó a la luz:** CI. Un CI sin pins es **no determinista**, y el guardián de cifras pasaría o fallaría según upstream.
- **La decisión:** los pins viven en **un solo lugar**, `tools/vendor.py`, con los hashes **completos** y las listas de plantillas fijadas también. `--templates-only` trae los diez formularios desde `raw.githubusercontent` **en el commit exacto** (sin git, sin clon, verificado byte-idéntico al checkout local). `--full` clona o actualiza y hace `checkout` del pin, verificando que `HEAD` sea el pin. **Los dos modos fallan fuerte si el pin no está** — un fetch que "siempre funciona" tomando otra cosa en silencio es el defecto que esto reemplaza. `sync-products.sh` conserva el nombre y pasa a ser un envoltorio de `--full`, para que todas las referencias existentes sigan siendo válidas.
- **Un pin en dos lugares es un pin que deriva.** Por eso los reportes citan hashes cortos y el tool tiene los completos: una cita y un pin son cosas distintas, y la verificación las une.

## D-036 — El invariante de solo lectura es sobre ESCRITURAS, no sobre HTTP

- **Qué pasó:** `tools/vendor.py` necesita **leer** por HTTPS, y `tools/readonly_check.py` prohibía `http.client`, `urllib.request` y `requests.*` **de plano**. El gate se puso en rojo.
- **Por qué la regla estaba mal formulada:** el invariante real siempre fue **no escribir** en repositorios de terceros. "Sin cliente HTTP" era un **proxy** — y funcionaba porque el tablero no tenía ninguno. Dejó de ser cierto en cuanto hizo falta traer inputs, y **prohibir la lectura habría sido cumplir la letra y perder el punto**.
- **La decisión:** el invariante se enuncia por lo que siempre quiso decir. Siguen prohibidos: escrituras HTTP (`requests.post/put/patch/delete`, `urllib.request.Request(... method='POST'...)`, `curl -X POST`, `gh api -X POST`), todo `gh` mutante (`issue`/`pr`/`label`), y `git push`. Se **permiten las lecturas**. `socket.create_connection` sigue prohibido: un socket crudo puede hacer cualquier cosa, y `urlopen` cubre las lecturas que este proyecto hace — es un hueco deliberado, no un olvido.
- **Consecuencia:** la frase "el tablero no puede escribir en GitHub porque no tiene cliente HTTP" había que cambiarla igual, porque ahora **sí hay** un cliente HTTP en el proyecto — que solo lee. El invariante no se debilitó: **se hizo verificable de nuevo**, que es distinto.

## D-037 — La cifra del Módulo D depende del estado de refs, no del commit que cita

- **Qué se observó, sin buscarlo:** al correr `tools/vendor.py --full`, que hace `git fetch` en los checkouts, la cifra de rutas borradas del Módulo D para `gentle-ai` pasó de **1247 a 1252**. Nadie editó nada.
- **La causa:** el módulo recorre **refs locales** para encontrar rutas borradas en la historia. Un `fetch` trae refs nuevos, y con ellos más historia que contiene borrados. **Su cifra depende de algo distinto del commit que documenta.**
- **Por qué es grave en este proyecto:** el reporte cita `gentle-ai 9dfe17d8` como si la cifra fuera una propiedad de ese commit. No lo es. Es, otra vez, **procedencia mal atribuida** — la misma clase que D-029 y que el error del digest del snapshot (D-029, corrección).
- **Qué queda declarado, y qué no se hace acá:** la cifra del reporte se deja en el valor que el código produce hoy (**1252**), y `MODULES.md` se alinea; **el alcance del recorrido tiene que ser el pin** (`git log <pin>` en vez de todos los refs), y eso es una unidad propia. Mientras tanto, la cifra queda como **Clase C**: reproducible solo con el mismo estado de refs.
- **Cómo se descubrió, y vale registrarlo:** mirando un `git diff` que no debía existir. **Un archivo generado que cambia solo cuando nadie lo tocó es una cifra dependiendo de algo que no está declarado** — y eso es exactamente lo que un guardián de cifras debería poder ver.
