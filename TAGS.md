# TAGS.md — Qué significa cada etiqueta, en detalle

> **Para quién es esto.** Para quien va a triar en serio y necesita saber exactamente qué está mirando, de dónde sale cada etiqueta, qué NO significa y qué hacer con ella. La versión corta está en [`GLOSSARY.md`](GLOSSARY.md); la misma guía está dentro del tablero con el botón **«¿Qué significa?»**.
>
> **Todos los números de este documento se recomputan** desde el snapshot `issues.json` (1.228 issues abiertos) con `python3 tools/metrics.py` y `python3 db/rules.py`. Ninguno está escrito a mano. El snapshot es **`39553742aa7bf1ea`**, es decir `sha256("issues.json")[:16]`, emitido por `board/core.py::snapshot_meta()` y visible en `/api/health` del tablero. *(Corregido: una versión intermedia de este documento lo dio por inexistente porque el comando citado era `tools/metrics.py`, que no lo imprime. El dato era verdadero, con otro productor.)*

---

## 0. Lo primero: hay dos ejes distintos, y no se pisan

Esto es la clave para no confundirse. Las etiquetas del tablero pertenecen a **dos familias independientes**:

```
┌─ EJE 1: BANDA (exactamente una por issue) ──────────────────────────────┐
│   candidato P0 · P1 · P2 · P3 · zona gris                              │
│   Responde: ¿dónde miro primero?                                       │
│   La decide el motor con reglas deterministas sobre el texto del issue. │
└────────────────────────────────────────────────────────────────────────┘
┌─ EJE 2: SEÑALES (cero o más por issue) ─────────────────────────────────┐
│   falta info · mirada humana                                            │
│   Responde: ¿este reporte está listo para decidir?                     │
│   No cambian la banda: la acompañan.                                   │
└────────────────────────────────────────────────────────────────────────┘
```

Una tarjeta puede llevar **una banda y varias señales a la vez**. Por eso un mismo issue puede verse así:

```
gentle-ai#4917   [candidato P0]  [falta info ×8/8]        ← banda + señal
gentle-shell#1591 [P2]           [mirada humana]          ← banda + señal
gentle-shell#1625 [zona gris]    [falta info ×3/6]        ← sin banda + señal
```

**Ninguna etiqueta decide por vos.** La banda dice dónde mirar; la señal dice si tenés con qué decidir. El veredicto final lo escribís vos en la barra lateral.

### Resumen de todas las etiquetas

| Etiqueta | Eje | Cuántos issues | gentle-ai | gentle-shell | engram |
| --- | --- | --- | --- | --- | --- |
| `candidato P0` | banda | **14** | 9 | 5 | 0 |
| `P1` | banda | **17** | 10 | 7 | 0 |
| `P2` | banda | **399** | 210 | 137 | 52 |
| `P3` | banda | **80** | 43 | 29 | 8 |
| `zona gris` | banda | **718** | 461 | 246 | 11 |
| `falta info` | señal | **384** | 231 | 146 | 7 |
| `mirada humana` | señal | **26** | 12 | 9 | 5 |

---

## 1. `candidato P0` — pérdida silenciosa de datos o corrupción

### Qué significa

El texto del issue **describe** una pérdida silenciosa de datos, una corrupción, un borrado o un sobrescritura que ocurre **sin que nadie se entere**. "En silencio" es la palabra clave: el usuario no recibe un error, simplemente después los datos no están.

### Cómo lo decide el motor

Una sola regla, `rule:candidato_p0_requiere_revision_humana`, con dos partes:

1. **Patrón de pérdida** (`RE_P0_SILENT_BASE`): `silently` + (`corrupt` / `delet` / `drop` / `overwrit` / `lost` / `fails to save`), o la frase `data loss`.
2. **Guardas que lo cancelan** — y esto es tan importante como el patrón:
   - **Negación**: `no data loss`, `without data loss`, `not data loss`, `prevents data loss`, `zero data loss`. Sin esta guarda, un pedido de funcionalidad que dice "que no haya pérdida de datos" se marcaría como pérdida de datos.
   - **Descripción de un arreglo**: `from being silently dropped to being rejected`. Eso describe una mejora, no un defecto.
   - **Negación cercana**: `no ... lost`, `has not been demonstrated`.

   Solamente se evalúa cuando el issue es un bug (`bug:`/`fix:` o etiqueta de bug). Un `feat:` nunca llega acá — para eso existe `mirada humana`.

### Ejemplos reales

| Issue | Frase que lo disparó |
| --- | --- |
| `gentle-ai#4917` | "A corrupt custom-agents.json **silently drops** the registry entry of a successful install" |
| `gentle-ai#4795` | "Passive capture is **silently lost**: OpenCode session/prompt events never reach" |
| `gentle-shell#1044` | "the second being **silent data loss** of agent memory" |
| `gentle-shell#923` | "Today it is **silently dropped**, so a long list renders five rows" |

### Qué NO significa

- **No es un P0 confirmado.** El motor leyó el texto, no ejecutó el código ni reprodujo el fallo. Puede que el reporter se equivoque, que sea un caso límite, o que la "pérdida" sea una decisión de diseño. Por eso se llama **candidato**.
- **No significa que ya esté resuelto ni que sea urgente hoy.** Significa "esto merece tu ojo antes que el resto".
- **No es una acusación a nadie.** El motor no sabe quién escribió el código.

### Qué hacer con él

1. Abrí el issue con **"abrir en GitHub ↗"** y leé el hilo real.
2. Confirmá si la pérdida existe y bajo qué condiciones.
3. Escribí el **veredicto humano**: `P0` si confirmás, `P1`/`P2` si es menos grave, `no válida` si el reporter se equivocó.
4. Dejá una **nota** con la razón. Queda en el registro para siempre.

> Los 14 candidatos están listados uno por uno en `gold-p0-p1.md`, con su `veredicto_humano: pendiente`. **Ninguno está confirmado por una persona todavía.**

### Límites conocidos

- Si el issue dice "corrupt" pero sin "silently" ni "data loss", el motor **no** lo detecta (por ejemplo `gentle-ai#4809`, que sí está detectado por otra vía).
- El motor no distingue "pérdida de datos del usuario" de "pérdida de una entrada de caché". Eso lo decide una persona.

---

## 2. `P1` — bloqueo duro sin salida

### Qué significa

Algo **se rompe de forma dura** —se cae, no arranca, se cuelga, se queda sin memoria— **y no hay forma de esquivarlo**: ni un workaround manual ni reintentar.

### Cómo lo decide el motor

Regla `rule:hard_crash`. Dos caminos:

**A. Crash directo** (`RE_P1_CRASH_CORE`). Reconoce:

```
panic:            runtime panic          SIGSEGV
fatal error: runtime                      segmentation fault
NullPointerException                      uncaught exception  / uncaughtException
unhandled exception / unhandled rejection  stack overflow
out of memory     OOM-killer               fail / failed / refuses / unable to start
crash / crashes / crashed / crashing       bricked
```

**B. Deadlock real**: la palabra `deadlock` **solo si** aparece cerca de un contexto de proceso o hilo (`goroutine`, `thread`, `mutex`, `lock`, `process`, `hang`, `worker`). Un "deadlock" metafórico —*"las dos reglas se bloquean entre sí"*— no cuenta como crash.

**Guardas que lo cancelan** (para no inventar crashes donde no los hay):

- Negación: `not a crash`, `no system crash`, `has not been demonstrated`, `does not apply`.
- Modificadores idiomáticos: `crash-safe`, `crash-recoverable`, `crash-window`, `crash-on-render`.
- Descripciones de arreglo: `prevent ... from crashing`.
- `cannot start` **genérico NO se acepta**: *"review cannot start"*, *"build cannot start"*, *"the work unit cannot start"* son flujos bloqueados, no procesos que se caen. Esto se excluyó a propósito porque generaba 8 falsos P1.

**Y después viene la regla H9**: si el texto trae un workaround o una recuperación por reintento, **se degrada a P2**.

### Ejemplos reales

| Issue | Frase / regla |
| --- | --- |
| `gentle-ai#4974` | "the process can **fail to start** even though `pi --version` works in an interactive terminal" |
| `gentle-ai#4677` | "bare `gentle-ai` invocation **crashes** with Go runtime panic" |
| `gentle-shell#1606` | "**crashes** pi on startup with uncaughtException EMFILE" |
| `gentle-shell#962` | "recursive skill watcher **crashes** Pi with uncaughtException ENOENT" |
| `gentle-shell#1139` | "terminated by the **OOM killer**" |

### Qué NO significa

- **No significa "más importante que un P0".** La banda P0 no existe como veredicto del motor; P1 es la máxima prioridad *automática* que puede emitir. Un candidato P0 sin confirmar no es "más grave" que un P1 detectado.
- **No significa que ya se reprodujo.** Igual que P0, el motor leyó texto.
- **No incluye problemas con workaround.** Si hay salida, va a P2.

### Qué hacer con él

Es la lista de **17 issues** donde mirar primero si tenés poco tiempo. Confirmá el crash, y si encontrás un workaround razonable, bajalo a P2 — tu veredicto manda sobre el del motor.

### Límites conocidos

- Los crashes descritos solo en prosa, sin palabra clave ("se cierra solo sin decir nada"), no se detectan.
- Un `chore:` o `refactor:` que menciona un crash puede entrar; el motor prioriza no perderse un crash antes que la precisión perfecta.

---

## 3. `P2` — degrada, tiene salida, o es un pedido

### Qué significa

Tres cosas distintas conviven acá, y el motor te dice cuál por la regla:

| Regla | Qué es | Cuántos |
| --- | --- | --- |
| `rule:feature_request` | pedido de funcionalidad: prefijo `feat:`/`feature:` o etiquetas `enhancement`/`type:feature` | **395** |
| `rule:crash_with_workaround_demoted_to_p2` | había un crash, **pero el reporte documenta un workaround o una recuperación por reintento** (regla H9) | **4** |

### Cómo lo decide el motor

- **Feature**: prefijo del título o etiqueta. Antes de eso se evalúa si hay una banda distinta (un `feat:` con señal dura no sube, ver `mirada humana`).
- **Democión H9**: el crash existía (pasó el patrón P1) pero el texto trae `workaround`, `work-around`, `temporary fix`, `recovers upon retry`, `retry succeeds`, `restart fixes`, `works if/after`, `re-run works`. Si además hay **negación** del tipo `no configuration can work around it`, el workaround se descarta y **el issue vuelve a P1**.

### Ejemplos reales

| Issue | Detalle |
| --- | --- |
| `gentle-ai#4809` | "*Pi fails to start* after the overlay corrupts the file", pero trae `## Workaround: Repair the two lines back to a valid list` → **P2** |
| `gentle-ai#3016` | "*A pnpm-based upgrade is the **safe workaround***" → **P2** |
| `gentle-shell#745` | "*/reload crashes Pi*", con `Workaround until fixed: GENTLE_PI_SHELL=0` → **P2** |
| `gentle-ai#5176` | `feat(agents): distribute gentle-ai-security subagent` → **P2** |

### Qué NO significa

- **P2 no es "poco importante".** Es "tiene salida o no es un defecto". Un feature request grande puede valer más que un crash esquivadle.
- **La democión no minimiza el bug.** Un crash con workaround sigue siendo un bug: sólo deja de ser la emergencia que bloquea a todos.

### Qué hacer con él

Es tu backlog de trabajo normal. Filtrá por `P2` cuando quieras planificar y no apagar incendios.

---

## 4. `P3` — documentación, pregunta, tarea, cosmético

### Qué significa

No hay nada roto y no hay nada que decidir sobre prioridad: es un cambio de documentación, una pregunta, una tarea de mantenimiento (`chore`, `refactor`, `test`, `ci`, `style`) o algo cosmético.

### Cómo lo decide el motor

Regla `rule:docs_chore_question`. Prefijo del título `docs:`/`doc:`/`chore:`/`typo:`/`refactor:`/`test:`/`ci:`/`style:`, o etiquetas `documentation`/`question`/`discussion`/`type:chore`.

**Un detalle que se corrigió a propósito:** el prefijo explícito del título **gana** sobre una etiqueta que lo contradice. `gentle-ai#5168` es `docs(sdd): ...` con etiqueta `enhancement`; antes salía P2 y ahora sale **P3**, porque el que lo escribió eligió decir `docs:`.

### Ejemplos reales

| Issue | Detalle |
| --- | --- |
| `gentle-ai#5168` | `docs(sdd): remove retired SDD references from living docs` (traía etiqueta `enhancement`) |
| `gentle-ai#5062` | `test(app): the documented-invocation sandbox is not hermetic` |
| `gentle-shell#1597` | `refactor(vim): make SUPPORTED_VERSIONS the single source of truth` |
| `engram#1383` | `refactor(setup): share OpenCode JSONC config I/O` |

### Qué NO significa

- **No significa "descartable".** Una pregunta sin responder deja a alguien bloqueado. Y `test`/`ci` rotos afectan a todos.
- **No es una banda de "ruido" para esconder.** Es la cola de trabajo planificable.

### Qué hacer con él

Agrupá por tema y resolvé en lote. Es ideal para una sesión de mantenimiento, no para una de incidentes.

---

## 5. `zona gris` — sin clasificar todavía

### Qué significa

**Ninguna regla determinista coincidió.** Eso es todo. No es una evaluación de importancia: es un *estado de procesamiento*.

Son **718 issues**: la mayor parte del backlog (58,5%). Es esperable: el motor resuelve lo estructural (prefijos, labels, señales de texto) y deja la prosa para el pase con LLM o para tu criterio.

### Cómo lo decide el motor

Es el **resultado por defecto**: si no disparó P0, ni P1, ni feature, ni docs, entonces no hay banda.

Ejemplos típicos que caen acá:

| Issue | Por qué |
| --- | --- |
| `gentle-ai#5175` | `bug(engram): sync overwrites a user-customized Claude Code mcpServers` — describe una sobrescritura, pero sin "silently" ni "data loss" |
| `gentle-shell#1646` | `bug(review): in-process reviewer completions carry no maxTokens` — un defecto real, descrito en prosa |
| `engram#1599` | `fix(cloud): managed principals see an empty project` — defecto sin palabra clave |

### Qué NO significa

- **No significa "sin importancia".** Significa **sin clasificar**. Varios de estos son bugs serios que el motor no supo leer.
- **No significa que el motor los descartó.** Siguen en el tablero, con su título y su link.
- **No es un error del reporter.**

### Qué hacer con él

Es exactamente donde tu criterio aporta más: el motor ya te sacó de encima lo mecánico, y acá decidís vos. Si apagás `zona gris` en el filtro, trabajás sobre lo que el motor sí pudo clasificar; si la dejás prendida, ves el panorama completo.

### Límite honesto

**718 issues es demasiado para leerlos a mano.** Por eso el siguiente paso del proyecto es el pase con LLM sobre esta zona y la vista de sistema agregada por clase raíz. Hoy está declarado como pendiente, no como hecho.

---

## 6. `falta info` — el reporte no trae lo que su propio formulario pide

### Qué significa

Al issue le faltan **N de los T campos** que **su propio formulario de GitHub** marca como obligatorios. El motor no opina sobre qué debería tener un buen reporte: lee el formulario real del repositorio en `products/<repo>/.github/ISSUE_TEMPLATE/*.yml` y compara.

### Cómo lo decide el motor (Módulo A)

1. Parsea el `.yml` del formulario que corresponde (bug o feature) y toma los campos con `validations.required: true`, **excluyendo los checkboxes** de atestación (un tilde faltante no es información faltante).
2. Detecta cada campo tanto por **encabezado** (`### 📝 Bug Description`) como por **etiqueta en línea** (`**Gentle AI Version:** …`). Esto último fue necesario porque GitHub renderiza los inputs así, y un detector solo-encabezado daba falsos "faltante".
3. Un campo está **presente** si aparece y su contenido no es vacío ni un placeholder (`1.\n2.\n3.`).

Campos obligatorios por plantilla:

| Repositorio | Plantilla | Campos obligatorios |
| --- | --- | --- |
| `gentle-ai` | bug | 8 |
| `gentle-shell` | bug | 6 |
| `engram` | bug | 7 |
| cualquiera | feature | 2 o 3 |

### La severidad tiene color, y es proporcional

Faltar 1 de 2 campos es peor que faltar 1 de 8: por eso la severidad usa la **proporción** `N/T`, no el número absoluto.

```
  poco             medio            alto             crítico
  ▓▓▓▓             ▓▓▓▓             ▓▓▓▓             ▓▓▓▓
  blanco           amarillo         naranja          rojo
  < 34%            34% a 59%        60% a 79%        ≥ 80%
```

Distribución actual: **147 críticos · 119 altos · 78 medios · 40 leves**.

### Ejemplos reales

| Issue | Faltan | Severidad | Qué falta |
| --- | --- | --- | --- |
| `gentle-ai#4917` | 8 de 8 | crítico | Bug Description, Steps, Expected, Actual, Version, OS, Client, Affected Area |
| `gentle-shell#1625` | 3 de 6 | medio | gentle-pi version, Pi version, Operating system |
| `engram#1152` | 3 de 3 | crítico | Problem Description, Proposed Solution, Affected Area |

Pasando el mouse por la insignia ves el porcentaje y **cuáles** campos son.

### Qué NO significa — y esto es lo más importante de esta sección

> **`falta info` no dice que el issue sea malo: dice que el reporte no trae lo que su propio formulario pide.** Un issue con severidad crítica puede ser perfectamente válido — lo que falta es información para triarlo. Y al revés: un reporte completo puede estar igual de equivocado.

- **No es una acusación al reporter.** Muchos issues son viejos (anteriores al formulario) o los generó una herramienta automática, y legítimamente no traen los campos.
- **No es una banda.** Un P0 con `falta info` sigue siendo un P0. Y de hecho **5 de los 14 candidatos P0** (36%) llevan esta señal.
- **No es falta de esfuerzo.** Es falta de *campos*, medible y objetiva.
- **No impide triar.** Muchas veces el título alcanza para decidir; la señal te avisa que si necesitás reproducirlo, no vas a poder.

### Qué hacer con él

- Si vas a **pedir datos**: apagá `zona gris` y `P2`, dejá prendido `falta info`, y tenés la lista de a quién pedirle qué. El tooltip te dice exactamente qué campos.
- Si vas a **decidir ahora**: tomalo como advertencia de que la decisión se basa en información parcial.

### Límite honesto

El módulo mide **presencia**, no calidad. Un reporte con los 8 campos escritos con dos palabras cada uno pasa el chequeo. La señal te dice "no falta nada", no "está bien explicado".

---

## 7. `mirada humana` — señal dura bajo un prefijo que no es de bug

### Qué significa

Esta es la etiqueta más sutil y la que más se malentiende, así que va con el mecanismo completo.

El motor tiene una compuerta: **P0 y P1 sólo se evalúan si el issue es un bug** (prefijo `bug:`/`fix:` o etiqueta de bug). Un issue con prefijo `feat:` **nunca** puede llegar a candidato P0 ni a P1. Esa compuerta existe porque el prefijo lo eligió quien reportó, y el motor no pisa esa decisión.

Pero a veces un `feat:` **describe** una pérdida de datos o un crash real — como motivación del pedido. Ejemplo real, `gentle-shell#1591`:

> `feat(profiles): directory-based profile rules so unpinned clones stop silently falling back…`
> "One keypress **silently overwrites** the pinned profile with the global routing"

Es un feature request **y** describe una pérdida de datos. El motor **no** lo va a subir a P0/P1 (no pisa el prefijo), pero tampoco lo va a callar. Entonces emite la señal: **"esto mantiene su banda, pero miralo vos"**.

> **Regla dura del proyecto: el motor nunca auto-promueve.** Una señal dura bajo un prefijo no-bug mantiene la banda y levanta la señal. Ver `DECISIONS.md` D-003.

### Cómo lo decide el motor

Función `requires_human_review()`:

```
la banda es P2 o P3            (una banda ya alta no necesita el aviso)
Y además
  has_silent_data_loss(texto)  → "silent data loss under a non-bug prefix"
  o bien
  is_hard_crash(texto)         → "crash under a non-bug prefix"
```

Nota que usa **los mismos detectores** que P0 y P1. No es un heurístico nuevo: es la misma evidencia, aplicada donde la compuerta de banda la bloqueaba.

### Ejemplos reales

| Issue | Banda | Motivo | Frase |
| --- | --- | --- | --- |
| `gentle-shell#1591` | P2 | pérdida silenciosa bajo `feat:` | "One keypress **silently overwrites** the pinned profile" |
| `gentle-ai#4905` | P2 | crash bajo `feat:` | "creating a potential `panic: runtime error: index out of range` on `Enter`" |
| `engram#1462` | P2 | crash bajo `feat:` | "no restart on **crash** or reboot, dies with the session" |

Reparto: **17 por pérdida de datos** y **9 por crash**, sobre 26 issues.

### Qué NO significa

- **No es un P0/P1 disfrazado.** La banda sigue siendo P2 o P3. Si el prefijo no es de bug, el motor respeta lo que dijo quien reportó.
- **No significa que el feature esté mal escrito.** Muchos son pedidos excelentes cuya motivación es un defecto existente.
- **No es ruido.** 26 de 1.228 issues (2,1%): es una lista corta y revisable, y contiene cosas que el resto del pipeline se perdería.

### Qué hacer con él

Apagá todo menos `mirada humana` y tenés **26 issues, revisables en una sentada**, donde hay algo real escondido detrás de un prefijo. Es, probablemente, la lista con mejor relación valor/tiempo del tablero.

Y ojo con lo que sigue: si al leerlo concluís que **además** hay un bug real, ese hallazgo es tuyo, no del motor. Anotalo en la nota del veredicto.

### Límite honesto

Esta señal depende de que el texto use las palabras clave: "silently drops", "crashes", etc. Un `feat:` que describe un defecto en lenguaje llano pasa desapercibido.

---

## 8. Vocabulario de reglas (`rule:...`)

Cada banda viene con la regla que la produjo. En la tarjeta se muestra en castellano; el nombre técnico aparece en el tooltip.

| Regla técnica | En la tarjeta | Qué la dispara | Cuántos |
| --- | --- | --- | --- |
| `rule:candidato_p0_requiere_revision_humana` | candidato P0 | pérdida silenciosa de datos, sin negación ni descripción de arreglo | 14 |
| `rule:hard_crash` | crash duro | crash o deadlock real, **sin** workaround | 17 |
| `rule:crash_with_workaround_demoted_to_p2` | crash con workaround | había crash, pero el reporte documenta salida (H9) | 4 |
| `rule:feature_request` | pedido de funcionalidad | prefijo `feat:`/`feature:` o etiqueta de feature | 395 |
| `rule:docs_chore_question` | docs / tarea | prefijo de docs/chore/refactor/test/ci, o etiqueta correspondiente | 80 |
| *(ninguna)* | zona gris | ninguna regla coincidió | 718 |

---

## 9. Cómo se combinan: la regla del filtro

Cuando prendés y apagás etiquetas en la barra superior, la regla es una sola:

> **Una tarjeta desaparece cuando *lleva* la etiqueta que apagaste. No importa qué otras etiquetas tenga.**

Los dos ejes son independientes. Con un issue de varios tags:

| Issue | Banda | falta info | mirada humana | Apagás `P2` | Apagás `falta info` | Apagás `mirada humana` |
| --- | --- | --- | --- | --- | --- | --- |
| A | P2 | no | no | **desaparece** | sigue | sigue |
| B | candidato P0 | sí | no | sigue | **desaparece** | sigue |
| C | P3 | sí | sí | sigue | **desaparece** | **desaparece** |
| D | zona gris | sí | no | sigue | **desaparece** | sigue |

Fijate en **B**: es candidato P0 y aun así desaparece si apagás `falta info`, porque lo lleva. Y apagar `P2` no lo toca: son ejes distintos.

El número entre paréntesis de cada etiqueta es el total del tablero activo y **no cambia al filtrar**. Arriba a la derecha el tablero muestra **"mostrando X de Y"** para que veas el efecto del filtro sin contar tarjetas.

**Filtrar no mueve ni borra nada:** es solo una vista.

---

## 10. Cómo verificar todo esto vos mismo

```bash
python3 db/rules.py                 # bandas, reglas y la muestra de calibración
python3 modules/completeness.py     # qué campos faltan y por qué (Módulo A)
python3 tools/metrics.py            # todos los números de este documento
python3 test_board.py               # incluye la regresión del filtro por etiquetas
python3 tools/verify_all.py         # todos los checks del proyecto a la vez
```

Los conteos de este documento salen del snapshot **`39553742aa7bf1ea`** (`sha256("issues.json")[:16]`, 1.228 issues abiertos) y se recomputan con `python3 tools/metrics.py`. Si el snapshot cambia, cambian los números: por eso el script los recalcula en vez de leerlos de acá.

---

## 11. Lo que ninguna etiqueta significa

Conviene decirlo junto, porque aplica a todas:

1. **Ninguna es un veredicto.** Son sugerencias derivadas del texto. El veredicto lo escribís vos, y es el único que vale para medir precisión.
2. **Ninguna se aplicó en GitHub.** El tablero no etiqueta, no comenta, no cierra. No hay una sola escritura en los repositorios.
3. **Ninguna está validada por personas todavía.** La precisión de estas reglas está **pendiente de validación humana**: no hay todavía una muestra etiquetada a mano contra la cual medirlas. Los números de este documento son de **cobertura** (cuántos issues toca cada regla), no de acierto.
4. **Ninguna esconde un issue.** Desaparece de la vista si apagás su etiqueta, pero sigue en el tablero, con su link, su registro y su lugar en las otras vistas.
