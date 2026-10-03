# STATUS.md — Gentle AI Maintainer Assistant, Project Status

> **Estado real, qué está hecho, qué falta y qué tiene que decidir el dueño.**
> **Cada cifra de este documento declara cómo se verifica** (ver «Cómo verificar cada cifra»).
> Ninguna cifra se afirma sin su comando de origen o su declaración explícita de no verificabilidad.

---

## Estado actual

* **El lote del tablero ESTÁ commiteado**, en seis unidades encadenadas y en el remoto:
  `2d59094` (C1a dominio) · `d35ffbb` (C1b servidor/UI) · `28174e5` (C2 medición) ·
  `9f32cb1` (C3a docs) · `806a466` (C3b índices) · `6be5093` (corrección de D-027).
* **Regla de secuencia vigente (D-027):** **un commit sin revisar por vez.**
  Commitear → revisar el rango → no commitear nada más hasta que esa revisión cierre.
* **Checks:** `python3 tools/verify_all.py --full` → **10/10**; sin `--full` → **8/8**.
* **Suites:** `python3 test_rules.py` → **129/129**; `python3 test_board.py` → **79/79**;
  contratos `python3 schemas/validate.py` → **12/12**.

### Revisiones nativas — nada de esto está «cerrado»

| Unidad | Commit | Líneas | Estado de la revisión nativa |
| --- | --- | --- | --- |
| C1a — dominio y auditoría | `2d59094` | 665 | **Estacionada.** `review-7cb7f5fd9a7b5c39` tiene las 4 lentes corridas y **hallazgos producidos y NO LEÍDOS** sobre `board/core.py`. Quedó en `action: recover` / `scope_changed` porque HEAD avanzó mientras las lentes corrían. Desbloquearla es una operación **del host** (ver D-028). |
| Corrección de D-027 | `6be5093` | 11 | **Aprobada y quemada.** Tier `low`, `selected_lenses: []`, `non_executable_only`, evidencia `gentle-ai.review-acknowledged/v1`. |
| C3b — índices y promesas | `806a466` | 332 | **Detenida.** `review-4b205b183f6e3028` escaló a `action: stop` terminal por `insufficient_evidence`, hallazgo `R3-status-md-6-critical-claims`. Ver «Defecto corregido en este documento». |
| C1b, C2, C3a | `d35ffbb`, `28174e5`, `9f32cb1` | — | **No revisables por separado.** El candidato por rango es `baseRef..HEAD`, así que solo quedó revisable la cola del rango. |
| Unidad de índices y chequeos | sin commit propio | 375 | 4 lentes **corrieron** → 1 CRITICAL (contradicciones de recuentos), corregido en 8 líneas. **Validación dirigida PENDIENTE** por el defecto D-028. |

* **Hallazgos reales encontrados por las lentes:** **6 CRITICAL**, todos introducidos por este
  trabajo y todos corregidos — path traversal en `/static/`, 500 por input inválido, README con
  el árbol roto, actor forjable, carrera en `move_card`, y contradicciones de recuentos en la
  documentación. Ninguno llegó a un revisor humano.
* **Precisión sin medir:** el instrumento existe (`tools/precision_report.py`), las etiquetas
  humanas son **0**. La cifra está pendiente de que una persona etiquete.
* **Vista de sistema, pasada de LLM sobre la zona gris, propuestas de regla, `REPORT.md` y modo
  sombra:** no implementados.

---

## Riesgos abiertos conocidos — sin vía de cierre desde este lado

Tres puntos viajan con el proyecto **abiertos y sin recuperación posible desde este repositorio**.
No están resueltos ni mitigados: están declarados, que es lo único honesto que se puede hacer con
ellos desde acá.

| # | Riesgo | Estado real | Vía de cierre |
| --- | --- | --- | --- |
| 1 | **Hallazgos sellados de C1a.** `review-7cb7f5fd9a7b5c39` tiene 4 lentes corridas, con hallazgos **producidos y NO LEÍDOS** sobre `board/core.py`, dentro del almacén nativo del proveedor. | Perdidos mientras no los recupere el host. | **Ninguna desde acá.** `external.authorize_recovery` no es una operación del canal de captura, y `recover` exige valores nativos no derivables (D-028). |
| 2 | **La validación dirigida funciona; la línea de C3b quedó detenida.** El slot `provider_targeted_validator` **sí se puede entregar**: el 2026-10-03 validó una corrección de 8 líneas y la revisión cerró en `approved`. El rechazo es **intermitente**, no una incapacidad (D-028, diagnóstico corregido). | Una corrección quedó formalmente validada; la de C3b no, porque esa línea se detuvo terminalmente por un rechazo hoy considerado transitorio. | Rehacer la revisión del rango que contiene `54a8498`, o declarar perdida esa validación formal. **Decisión del mantainer, no bloqueo técnico.** |
| 3 | **C1a y C1b no revisables por separado.** El candidato por rango es `baseRef..HEAD`, así que las unidades anteriores a la cola quedaron fuera del alcance revisable. | Confirmado por medición (ver D-027). | Solo revisando el rango completo, que excede el presupuesto de lentes. |

**Consecuencia que no se disimula:** estos tres puntos viajan con el proyecto. Un lector de este
documento **no** debe asumir que el lote está íntegramente revisado. **No lo está.**

---

## Defecto corregido en este documento (y en `BOARD.md` y `TAGS.md`)

La lente de confiabilidad de C3b escaló con `insufficient_evidence` sobre seis afirmaciones de
`STATUS.md`. **Tenía razón, y al verificarlas apareció algo peor que falta de evidencia: una
cifra inventada.**

* **Lo que decía:** «Distribución derivada (… snapshot `39553742aa7bf1ea`)», y en `BOARD.md` y
  `TAGS.md` la misma cifra presentada como **«reproducible con `python3 tools/metrics.py`»**.
* **Lo que es verdad:** **ningún comando del proyecto produce ese valor.** `tools/metrics.py` no
  imprime ningún digest de snapshot. Era una cifra **hardcodeada presentada como derivada** — es
  decir, exactamente la clase de defecto que este proyecto existe para cazar, cometida en su
  propia documentación y en su propio archivo de estado.
* **La corrección:** el digest que **sí** existe y **sí** se produce es el de la proyección
  derivada del tablero, **`b0a61cf3325ef7f1`**, emitido por `python3 tools/determinism_check.py`.
  La afirmación falsa se eliminó de los tres documentos.
* **Y la lección, que quedó en `DECISIONS.md`:** un número con una etiqueta de procedencia al lado
  no es evidencia. La procedencia hay que **ejecutarla** una vez antes de publicarla.

---

## Cómo verificar cada cifra

Tres clases, declaradas sin maquillaje. Un revisor atado al árbol congelado **no ejecuta nada**:
por eso lo importante no es que *pueda* correr el comando, sino que la cifra **no esté afirmada a
mano**.

### Clase A — Derivada por comando desde datos del árbol

El dato de entrada (`issues.json`) y el script que lo deriva están **ambos en el árbol**, así que
un revisor puede **leer el camino completo** desde el dato hasta la cifra. No puede ejecutarlo,
pero puede comprobar que la cifra **no está escrita a mano**.

```bash
python3 tools/metrics.py          # todas las cifras de "Current figures"
python3 tools/determinism_check.py # los seis digests de salida derivada
python3 tools/run_reports.py      # los cuatro reportes de módulos
```

| Cifra | Comando | Salida esperada |
| --- | --- | --- |
| Issues abiertos | `python3 tools/metrics.py` | `total open issues: 1228` |
| Por repositorio | `python3 tools/metrics.py` | `engram=71, gentle-ai=733, gentle-shell=424` |
| Resueltos por código | `python3 tools/metrics.py` | `classified by code (no LLM): 510 (41.5%)` |
| Zona gris residual | `python3 tools/metrics.py` | `residual grey area: 718 (58.5%)` |
| Bandas P0/P1/P2/P3 | `python3 tools/metrics.py` | `candidato P0 14 · P1 17 · P2 399 · P3 80` |
| Marcados para mirada humana | `python3 tools/metrics.py` | `flagged for human review: 26` |
| Digest del contrato de decisión del motor | `python3 tools/determinism_check.py` | `engine decision contract: 29528cd3d38784c2…` |
| Digest del tablero derivado | `python3 tools/determinism_check.py` | `board derived projection: b0a61cf3325ef7f1…` |
| Digest de cada módulo | `python3 tools/determinism_check.py` | `A 0c0ccaca24fb234b… · B 7e63683152dd4e70… · C 684fcc589d8629bc… · D 7cd51c438a563c4c…` |

### Clase B — Solo por ejecución de la suite: NO hay verificación estática

Estas cifras **no se pueden contar leyendo**. Vale la pena decir por qué, porque es incómodo y es
la verdad:

* `grep -c 'assert_test(' test_rules.py` → **35**, pero la suite reporta **129**: los casos
  restantes viven dentro de **bucles** sobre listas de issues reales.
* `pytest test_rules.py test_board.py` → **no recolecta nada**: son harness propios
  (`python3 test_rules.py`), no pruebas unittest/pytest.
* Por lo tanto un revisor **solo puede leer los casos con nombre** (14 grupos documentados en el
  encabezado de `test_rules.py`); el total **no es verificable sin ejecutar**.

| Cifra | Comando | Naturaleza |
| --- | --- | --- |
| 129/129 reglas | `python3 test_rules.py` | solo por ejecución |
| 79/79 tablero | `python3 test_board.py` | solo por ejecución |
| 12/12 contratos | `python3 schemas/validate.py` | solo por ejecución |
| 10/10 y 8/8 checks | `python3 tools/verify_all.py [--full]` | solo por ejecución |

### Clase C — Local: NO verificable desde el artefacto

Declaradas explícitamente como **no verificables por un revisor**. No se presentan como derivadas.

| Cifra | Por qué no es verificable |
| --- | --- |
| Distribución por columna del tablero (`gentle-ai` 733 = 492 + 231 + 10; `gentle-shell` 424 = 272 + 146 + 6; `engram` 71 = 60 + 7 + 4) | Requiere `db/board.db`, que está **fuera de git** por diseño. Es una medición **local** del 2026-10-02, reproducible con `python3 board/server.py --ingest --port 8770`, pero **no** desde el artefacto congelado. |
| Actividad humana del tablero (0 etiquetas) | Estado de una base local; por definición no vive en el árbol. |
| Fecha de cada medición | Reloj local. |

---

## Historial de entregas

### Fase 1 — Fundamentos
* Motor determinista `db/rules.py`, snapshot saneado `issues.json` (**Clase A**: 1,228 issues, sin
  datos personales, verificado por `tools/privacy_check.py`), contratos JSON Schema, licencia MIT.

### Fase 1.1 — Endurecimiento de reglas
* Salvaguardas de negación y de contexto; invariante de gobernanza de candidato-P0 forzado por el
  esquema. Conjunto de oro `gold-p0-p1.md` con `veredicto_humano: pendiente`.

### Fase 1.2 — Auditoría adversarial de solo lectura
* `AUDIT.md` auditó H1–H10 y las bandas P0–P3 sobre el corpus completo con split determinista
  `sha256(slug#number) mod 5` (grupo 0 held-out = 231 issues, exploración = 997).
* H1, H2 y H5: 0 violaciones. H3, H4, H6, H7, H8: **no auditables con este conjunto de datos**.
  H9 y H10: hallazgos detallados.

### Delivery 1 — Correcciones y gobernanza
* **Vocabulario de crash ampliado:** `crashes`, `uncaughtException`, `Go runtime panic`,
  `fails to start`, `out of memory`, `OOM killer`. El genérico `cannot start` queda excluido a
  propósito (workflow bloqueado, no un crash). P1 pasó de 2 a 17 issues.
* **`title_prefix` recuperado** del título cuando el valor ingerido viene vacío.
* **Orden de reglas corregido:** un prefijo explícito `docs:`/`chore:` gana sobre una etiqueta
  `enhancement` en conflicto (`gentle-ai#5168` es P3).
* **Sin auto-promoción:** una señal dura bajo `feat:`/`docs:` conserva su banda y queda marcada por
  `requires_human_review()` — 26 issues (17 de pérdida, 9 de crash).
* **H9 ahora dispara:** detección de workaround ampliada; `bypass`/`mitigation` eliminados.
* **Artefactos de gobernanza:** `PROMISES.md` (afirmación → evidencia → estado → hueco),
  `DECISIONS.md`, `tools/metrics.py`, `tools/readonly_check.py`, `tools/privacy_check.py`.
* Commits: `ad7b6b1`, `fc34e85`.

### Delivery 2 — Módulos mecánicos
Tres módulos de solo lectura que **no necesitan etiquetas humanas**. Método, fuente embebida y
límites en `MODULES.md`. Regenerables con `python3 tools/run_reports.py`.
* **Módulo A — completitud.** Parsea los `.github/ISSUE_TEMPLATE/*.yml` reales de cada repositorio:
  1,114 issues contra plantilla, 1,043 enviados por formulario, **313 con al menos un campo
  obligatorio faltante**; 71 fuera del formulario, reportados aparte.
* **Módulo B — duplicados probables.** Solo evidencia determinista: clase de excepción/panic,
  código de error, frame `file:line`, cadena de error citada, exit code, títulos normalizados.
  **108 pares candidatos, 7 con evidencia fuerte**, 101 más débiles. Nunca dice «duplicado».
* **Módulo C — enlaces entre repos.** Un enlace requiere un `repo#N` explícito que resuelva a un
  issue abierto: 48 referencias explícitas, **15 resolventes**, 33 sin resolver, 81 referencias
  `owner/repo` sin número, 914 menciones desnudas. Reencuadra las «345 menciones» de `AUDIT.md`.
* **No validado:** ninguno de los tres tiene precisión verificada por humanos.
* Commits: `b07b282`, `8081020`.

### Delivery 3 — Módulo D y un defecto real de determinismo
* **Módulo D — issues posiblemente obsoletas** (`modules/obsolete.py` → `report-obsolete.md`),
  contra los commits vendorizados `gentle-ai@9dfe17d8`, `engram@0f79d5e`, `gentle-shell@7a27c1c0`:
  * **Clase A (verificable):** la ruta referenciada fue borrada en la historia del propio
    repositorio → **54 issues** (34 `gentle-ai`, 20 `gentle-shell`).
  * **Clase B (débil, explícitamente NO una afirmación de obsolescencia):** ruta, flag o símbolo
    sin resolver y sin registro de borrado → 155 issues.
  * Cada fila cita el token, la oración y el commit; todo es «posible, requiere verificación» con
    `veredicto_humano: pendiente`.
* **Defecto encontrado y corregido al validar:** Python aleatoriza el hash de strings por proceso,
  así que iterar un `set` de tokens producía un orden de pares distinto en `report-duplicates.md`
  en cada corrida. El orden ahora es total (`-score, tier, pair keys`) y la iteración de sets está
  ordenada. `tools/determinism_check.py` corre cada módulo bajo dos `PYTHONHASHSEED` y falla si un
  reporte cambia — los cuatro son byte-idénticos. Sin esto, **toda** afirmación de reproducibilidad
  del proyecto habría sido hueca.
* Commit: `7638f09`.

### Delivery 4 — Tablero Kanban local
Consola local en `http://127.0.0.1:8770/`, **un tablero por aplicación**. Detalle en `BOARD.md`.
* **Modelo:** estado en SQLite local (`db/board.db`, fuera de git) + log **append-only**.
  `card_state` y `human_labels` son cachés reconstruibles; `tools/board_rebuild_check.py` lo
  demuestra rompiendo las cachés y reconstruyéndolas.
* **Regla de diseño central:** el motor **solo sugiere columnas de bloqueo** (`falta_info`,
  `revision_humana`). Nunca sugiere `listo_mantener` ni `en_manos`: promover trabajo hacia un
  maintainer es un juicio humano. Verificado por tests.
* **Sin red saliente:** `tools/readonly_check.py` falla ante `http.client`, `urllib.request` o
  `requests` en cualquier parte del proyecto. El tablero no puede escribir en GitHub porque no
  tiene cliente HTTP.
* **Solo localhost:** el servidor rechaza cualquier interfaz que no sea `127.0.0.1`. Sin
  autenticación, a propósito.
* **No validado:** el tablero no tiene uso real todavía; las señales de los Módulos B, C y D
  **no** se muestran aún como badge por tarjeta (siguen a nivel de reporte).
* Commit: `2d59094` + `d35ffbb`.

### Delivery 5 — Medición, simulador y determinismo explicado
* **Filtro por etiquetas** con contador por tag, y la corrección de un bug real: `NOT (band = 'P1')`
  con `band IS NULL` descartaba toda la zona gris por el `NULL` de SQL. Ahora `COALESCE` en cada
  condición y un test que exige que apagar un tag quite exactamente lo que el tag cuenta.
* **Severidad proporcional** de `falta info` (`N/T`), con color y tooltip.
* **`explain.py` + simulador de reglas** («Probar una regla»): muestra qué habría decidido el
  motor, con qué regla y sobre qué evidencia. No escribe nada. Un test compara el explicador
  contra el motor en 400 issues para que no derive.
* **Modal «Determinismo y límites»:** qué es determinista y cómo se comprueba, qué no y por qué,
  si el sistema aprende (**no**), y qué falta.
* **`TAGS.md`** y **`GLOSSARY.md`**: explicación detallada de cada etiqueta.
* **Medición:** `tools/precision_report.py` (falsos negativos de P0/P1, precisión por regla con
  `n` e intervalo de Wilson) y `tools/label_sample.py` → `label-sample.md` (120 issues
  estratificados, 12 P0 y 13 P1, sin contaminar).
* **Determinismo verificado:** `tools/determinism_check.py` extendido a la proyección derivada del
  tablero, que antes no estaba cubierta.
* Commits: `28174e5`, `9f32cb1`, `806a466`, `6be5093`.

---

## Current figures (Clase A — recomputadas, no escritas a mano)

Comando único para todas: `python3 tools/metrics.py`.

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

> La cobertura es un censo, **no** una medida de corrección. **La precisión de las reglas
> post-auditoría está pendiente de validación humana.**

---

## What is NOT validated

* **No hay cifra de precisión para las reglas post-auditoría.** El vocabulario de crash y el orden
  de reglas cambiaron después de la auditoría; ambos esperan una muestra etiquetada por humanos
  fresca. El README lo dice explícitamente y **no** declara ninguna mejora.
* **Zona gris no corrida de punta a punta.** El pipeline de dos pasadas se corrió solo sobre la
  muestra de calibración de 90 issues.
* **Enlace entre repos incompleto.** 345 issues mencionan otro repositorio sin enlace estructurado.
* **Módulos mecánicos, modo sombra y herramienta de etiquetado:** no implementados (seguimiento en
  `PROMISES.md` §4).
* **Las cifras de Clase B y Clase C no son verificables por un revisor**, y así están declaradas.

---

## What is missing (next, in planned order)

1. **Costuras hexagonales (feature autorizada, alcance A).** Tres extracciones para cerrar
   tres fugas medidas —el explicador importando 20 internals del motor, el dominio del
   tablero recibiendo un `conn` crudo, y `sqlite3` dentro del motor— **sin reescritura**. La
   evidencia y las alternativas rechazadas están en `DECISIONS.md` D-030. El plan vive en
   `odd/tasks/hexagonal-seams.md`, **fuera de git a propósito** (estado local de Pi), así que
   un revisor no puede leerlo: por eso el alcance quedó registrado en la raíz. Los puntos 2
   y 5 de esta lista **dependen** de estas costuras.
2. **Vista de sistema:** agregación por clase raíz (313 reportes con los mismos campos faltantes =
   un problema de plantilla, no 313 tareas), con límites de WIP y envejecimiento por columna. Es
   lo que hace que el tablero siga sirviendo a los tres meses.
3. **Cerrar las revisiones de la cola:** C3b (tras este arreglo), y luego C2 + C3a + C3b, cada una
   como su propio rango commiteado, respetando «un commit sin revisar por vez».
4. **Métricas desde etiquetas humanas:** el tablero ya produce el `veredicto_humano`; falta que
   una persona etiquete para convertir los «pendiente de validación» en hechos medidos.
5. **Señales por tarjeta (Módulos B/C/D):** hoy la tarjeta solo muestra banda, regla, flag de
   mirada humana y campos faltantes del Módulo A. Duplicados, enlaces y obsolescencia siguen a
   nivel de reporte.
6. **`REPORT.md` para maintainers** (plan item e): máx. 15 ítems por sección, todos
   `verificado_por_humano: no` hasta que se revisen.

El orden se puede reordenar solo con una decisión registrada en `DECISIONS.md`.

---

## What Rafael must decide

| # | Decision | Options | Blocks |
| --- | --- | --- | --- |
| 1 | Push de `6be5093` | pushear / dejar local | nada |
| 2 | Línea estacionada `review-7cb7f5fd9a7b5c39` | que el host la recupere / abandonarla perdiendo los hallazgos | los hallazgos de 4 lentes sobre `board/core.py` |
| 3 | Reordenar el plan (herramienta de etiquetado antes) | mantener el orden / modo sombra primero / otro | nada hoy |
| 4 | Licencia | MIT está puesta; confirmar o cambiar | nada hoy |
| 5 | Contacto externo / publicación | no solicitado; la herramienta queda interna hasta que Rafael apruebe | cualquier contacto con maintainers |
| 6 | Muestra etiquetada fresca | Rafael etiqueta ~100–150 issues | toda afirmación de precisión |

Ninguna pregunta de arriba bloquea el desarrollo: el trabajo avanza en el orden propuesto hasta
que Rafael diga otra cosa.

---

## Constraints in force

* **Solo lectura** sobre repositorios de terceros; verificado por `tools/readonly_check.py`.
* **Sin nombres de maintainers ni métricas por persona.**
* **Sin `veredicto_humano` llenado por la herramienta**; toda entrada queda `pendiente`.
* **Sin cifras escritas a mano** en código ni docs: todo se recomputa, se cita, o se declara
  explícitamente como no verificable (Clases A/B/C de este documento).
* **Sin operación irreversible sin preguntar:** nada de borrar datos, reescribir historia ni
  force-push.
