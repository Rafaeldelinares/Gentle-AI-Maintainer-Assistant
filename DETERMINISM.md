# DETERMINISM.md — Qué es determinista, qué no, y qué falta

> **Para quién es esto.** Para quien necesita saber exactamente qué puede reproducir de este sistema y qué no, antes de confiar en un número. La misma explicación está dentro del tablero, en el botón **«Determinismo y límites»**, con los contadores en vivo.
>
> **La idea central:** el sistema tiene **dos capas separadas a propósito**. Una es determinista y se comprueba; la otra *no debe serlo*, porque es donde decide una persona.

---

## 1. Capa derivada — determinista y verificada

Es todo lo que el sistema **calcula** desde el snapshot congelado:

- la banda de cada issue y la regla que la produjo,
- el contrato de decisión estructurado (`decide()`),
- la columna sugerida,
- los campos faltantes del formulario y su severidad,
- los contadores de cada etiqueta y de cada columna,
- los cuatro reportes de módulos.

**Mismo snapshot ⇒ mismo resultado, byte a byte, en cualquier proceso y cualquier máquina.**

### Cómo se comprueba (no es una afirmación: es un digest)

| Qué | Chequeo | Resultado |
| --- | --- | --- |
| Contrato de decisión del motor | `decide(..., include_evidence=True)` sobre los primeros 400 issues, dos semillas | digest idéntico: `python3 tools/determinism_check.py` → `engine decision contract: 29528cd3d38784c2…` |
| Proyección derivada del tablero | ingest fresco en base temporal, dos semillas | digest idéntico: `python3 tools/determinism_check.py` → `board derived projection: b0a61cf3325ef7f1…` |
| Reportes de módulos A–D | dos procesos distintos, dos semillas | cuatro digests byte-idénticos: `python3 tools/determinism_check.py` → A `0c0ccaca24fb234b…`, B `7e63683152dd4e70…`, C `684fcc589d8629bc…`, D: **por comando, no por valor** — depende del estado de refs locales (D-037); hoy `8fbadbf59b5fabaa…`; y **E** `ef25e084b66efe0d…` |
| Cifras publicadas | `tools/metrics.py` las recalcula | ninguna escrita a mano |
| Contratos de datos | `schemas/validate.py` | 12/12 |

```bash
python3 tools/determinism_check.py     # los siete digests de salida derivada byte-idénticos entre procesos
python3 tools/verify_all.py --full     # todo el gate, incluido lo anterior
```

### Qué cubre y qué no cubre el digest del motor

El nuevo digest (`29528cd3d38784c2…`) cubre el contrato de decisión estructurado emitido por `decide(row, labels, cross_refs, include_evidence=True)`: banda, regla, clasificación cross-system, flag de revisión humana, motivo, `decided_by`, traza ordenada de `rules_considered`, y el bloque completo de `evidence` con spans y estados de predicados.

Qué **no** cubre deliberadamente:
1. **Los issues 401 a 1.228 con evidencia rica:** la generación de evidencia detallada (10 evaluaciones regex y extracción de contexto por issue) es costosa en tiempo. Acotar a los primeros 400 issues mantiene el chequeo en ~40s corriendo dos veces bajo semillas distintas. Los issues restantes están cubiertos sin bloque de evidencia por la proyección del tablero y por el test de consistencia mutua en `test_rules.py` §15.
2. **Decisiones humanas (columna en el tablero, veredicto):** por diseño son no deterministas y pertenecen a la Capa 2; su auditabilidad se verifica mediante reconstrucción del log append-only con `tools/board_rebuild_check.py`.
3. **Resolución de la zona gris (718 issues):** el digest sí cubre los registros de decisión deterministas de los issues de zona gris dentro de los primeros 400 (donde 309 issues tienen `band is None`), certificando que el motor los clasifica como indeterminados de forma determinista; lo que no cubre es la **resolución por LLM** posterior de esos issues, que opera fuera de las reglas deterministas de código.

### Limitación honesta: qué detecta `determinism_check.py` y qué no

`tools/determinism_check.py` compara la salida del motor ejecutada bajo dos semillas distintas de hash (`PYTHONHASHSEED=0` vs `PYTHONHASHSEED=42`). Por diseño, este chequeo **solo detecta no determinismo dependiente del proceso o de las semillas de hash** (por ejemplo, iteración sobre conjuntos o diccionarios sin orden estable). **No** compara contra un valor dorado almacenado, por lo que una regresión en el orden o en el contenido que sea *determinista* alterará el digest resultante pero seguirá pasando el chequeo de dos semillas. La protección contra regresiones deterministas en estos campos proviene del fixture dorado (`board/fixtures/explain-golden.json`), no de `determinism_check.py`.

### Por qué importa que sea determinista

Porque permite **auditar**. Si el motor sugirió `P1` para `gentle-shell#1606`, cualquiera puede volver a correr el motor sobre el mismo snapshot y obtener exactamente el mismo `P1`, con la misma regla y la misma evidencia. Sin eso, no habría forma de discutir una sugerencia: sólo se podría creer o no creer.

El snapshot congelado se identifica con **`39553742aa7bf1ea`** — `sha256("issues.json")[:16]`, emitido por `board/core.py::snapshot_meta()` y expuesto en `/api/health`. Citar ese digest es lo que permite afirmar que dos mediciones hablan del mismo dato.

### El límite del determinismo: el snapshot

Es determinista **dentro de un snapshot**. Si el snapshot cambia (issues nuevos, issues cerrados), los números cambian. Por eso el hash y la fecha del snapshot están **siempre visibles** en la barra superior: un número sin su snapshot no significa nada.

**El sistema nunca descarga datos solo.** «Recalcular» vuelve a correr las reglas sobre el snapshot local; no toca GitHub.

---

## 2. Capa decidida — no determinista, a propósito

Son las decisiones humanas:

- en qué **columna** está cada tarjeta,
- el **veredicto humano** (`P0`–`P3` / `no válida`),
- la nota que lo acompaña.

**Esto no debe ser determinista.** Si fuera predecible por el motor, no sería una decisión: sería otra sugerencia. El proyecto entero se apoya en que la autoridad final es humana.

### Lo que sí se garantiza: auditabilidad

Cada movimiento y cada veredicto se agrega a un **registro append-only**. Nada se sobreescribe nunca. Y el estado (`card_state`, `human_labels`) es sólo una **caché reconstruible** desde ese registro.

```
$ python3 tools/board_rebuild_check.py
  simulated cycle on the real snapshot: 1228 cards, 2 labels, 5 events
    ✔ card_state rebuilt from events matches exactly
    ✔ human_labels rebuilt from events matches exactly
    ✔ the event log was not modified by the rebuild
  THE EVENT LOG IS THE SINGLE SOURCE OF TRUTH
```

Ese chequeo **rompe las cachés a propósito**, reconstruye desde los eventos y exige que coincidan. Es la diferencia entre «determinista» y «auditable»: el estado no lo predice el sistema, pero cualquiera puede reconstruir cómo llegó ahí.

---

## 3. ¿El sistema aprende de los movimientos? **No**

Acumula las decisiones humanas, pero **no las usa para cambiar ninguna regla, ninguna banda ni ninguna sugerencia**.

### Verificado con un experimento

Sobre el **mismo** snapshot, dos tableros: uno limpio, y otro con **40 movimientos y 40 veredictos** aplicados a 40 tarjetas distintas.

| | |
| --- | --- |
| Decisiones humanas registradas | 80 eventos, 40 veredictos |
| Sugerencias que cambiaron | **0** |
| Sugerencias idénticas al tablero limpio | **1.228 de 1.228** |
| Lo único que cambió | la columna de esas 40 tarjetas |

Está codificado como test permanente: si algún día el motor empezara a ajustarse solo con el uso, `test_board.py` falla.

### Por qué *no* aprende, y por qué es deliberado

**Porque rompería el determinismo de la sección 1.** Si el motor ajustara sus reglas con el uso, la misma snapshot dejaría de dar el mismo resultado: dos personas con el mismo backlog obtendrían tableros distintos según lo que hubieran clickeado antes. Y sería imposible auditar por qué sugirió lo que sugirió, porque la respuesta sería «porque en el pasado alguien movió otra cosa».

Es una tensión real entre dos cosas buenas —adaptarse al uso y ser reproducible— y el proyecto eligió **reproducible**, con una salida explícita para mejorar.

### Lo que sí hace hoy con tus decisiones

**Guardarlas para poder medir.** Cada veredicto humano es una etiqueta de referencia. Con suficientes etiquetas se puede calcular, por regla:

- **falsos negativos de P0/P1** (casos graves que el motor no marcó),
- **precisión por regla**, con su `n` (cuántos casos la respaldan).

Hoy eso **no está implementado**: es el siguiente paso. Mientras tanto, todas las cifras del proyecto son de **cobertura**, nunca de acierto.

### Cómo se cambiaría una regla, cuando toque

1. Leer las etiquetas humanas acumuladas.
2. Calcular dónde la regla se equivoca y cuánto.
3. Escribir el cambio **a mano**, con su test de caso real y su decisión registrada en `DECISIONS.md`.
4. Versionarlo en un commit, con su hash.

Nunca en silencio, nunca sola, nunca sin dejar rastro. El sistema **propone y mide**; la mejora de sus reglas es una decisión de ingeniería revisable, no un ajuste automático.

---

## 3b. ¿Y la edición de reglas desde la interfaz? No, y es deliberado

Es la pregunta natural después de entender lo anterior. **Falta, sí, pero es lo último a propósito.**

### Por qué no puede ser una edición desde el tablero

Si las reglas se editaran desde la interfaz y se guardaran en la base local, se romperían **las dos propiedades de la sección 1**:

| Propiedad | Qué pasaría |
| --- | --- |
| **Determinismo** | la misma snapshot dejaría de dar el mismo resultado: dependería de lo que cada persona editó en su máquina |
| **Auditabilidad** | el revisor externo **no puede leer una regla que vive en tu base local**. No podría verificar nada |
| **Medición** | no habría forma de saber contra qué reglas se tomaron las decisiones pasadas |

Dicho de otro modo: una regla invisible y mutable convierte al sistema en una caja negra, que es exactamente lo contrario de lo que este proyecto promete.

### Dónde viven las reglas hoy

Son **código versionado** en `db/rules.py`. Cada una tiene:

- su patrón explícito (una expresión regular legible),
- sus guardas (qué la cancela),
- tests con **casos reales nombrados** (`test_rules.py`, 129 tests),
- un chequeo de determinismo entre procesos.

### Cómo se cambia una regla, entonces

1. **Encontrar el problema con datos.** El simulador y los veredictos humanos dicen dónde la regla se equivoca.
2. **Diseñar el cambio** en el simulador: pegás los casos que la regla actual matchea de más y ves por qué. Nada de esto modifica nada.
3. **Escribirlo a mano** en `db/rules.py`.
4. **Agregar un test** con ese caso real nombrado, que falle antes del cambio.
5. **Registrar la decisión** en `DECISIONS.md`, con las alternativas que descartaste.
6. **Commit.** El cambio queda versionado y el revisor lo puede leer.

Es más lento que un botón «guardar». Es la velocidad que cuesta que las cosas sean verificables.

### El simulador de reglas (lo que sí está)

El tablero tiene un botón **«Probar una regla»**: pegás un título y un cuerpo, y ves **qué habría decidido el motor**, con qué regla, **sobre qué evidencia**, y **qué guardas se activaron**. No edita nada y no toca ningún issue (hay un test que verifica que la actividad humana no cambia al usarlo).

Sirve para las dos mitades del problema: entender por qué un issue quedó donde quedó, y **diseñar** un cambio de regla antes de escribirlo.

`explain.py` reutiliza las **funciones reales** del motor, y hay un test que compara su resultado contra la clasificación real de 400 issues: si el orden de las reglas cambia y el explicador no, el test falla. Un explicador que miente es peor que no tener explicador.

### Lo que falta de verdad en este eje

**Propuestas de regla.** Que el tablero registre, a partir de los issues donde tu veredicto **contradijo** al motor, una propuesta concreta («esta regla matchea estos 12 casos de más»), y la vuelque en un reporte para que una persona decida. Eso no cambia ninguna conducta y no rompe nada: genera el insumo para el paso 1 de arriba.

Está listado como pendiente. No está hecho.

---

## 4. Lo que falta, según el propio sistema

Nada de esto está hecho. Se lista para que no se confunda con lo entregado.

| Pendiente | Estado | Por qué importa |
| --- | --- | --- |
| **Medición desde etiquetas humanas** | **instrumento listo, faltan etiquetas** | el script existe (`tools/precision_report.py`): calcula falsos negativos de P0/P1, precisión por regla con su `n` y un intervalo de Wilson 95%, **solo con etiquetas humanas**. Con 0 etiquetas dice «no disponible» en vez de inventar. Falta que una persona etiquete: la muestra está en `label-sample.md` (120 issues estratificados, 12 P0 y 13 P1) |
| **Señales de los módulos B, C y D por tarjeta** | parcial | duplicados, enlaces entre repos y obsolescencia existen como reportes en la raíz, pero todavía **no se ven como insignia** en cada tarjeta. Hoy la tarjeta muestra banda, regla, `falta info` y `mirada humana` |
| **Vista de sistema** | no implementado | agregar por **clase raíz** en vez de por caso: «313 reportes con los mismos campos faltantes» es *un* problema de plantilla, no 313 tareas. Con límite de trabajo en curso y envejecimiento por columna |
| **Zona gris sin pasada de LLM** | no implementado | 718 issues (58,5%) quedan sin clasificar por reglas. Es demasiado para leerlos a mano |
| **Propuestas de regla desde los veredictos** | no implementado | falta la pieza que convierte tus contra-veredictos en un reporte accionable: «esta regla matchea de más en estos 12 casos». Sin eso, cambiar una regla depende de que alguien note el patrón a mano |
| **Módulo A: calidad, no sólo presencia** | parcial | hoy mide si el campo **está**, no si está **bien escrito**. Un reporte con los 8 campos en dos palabras cada uno pasa el chequeo |
| **Enlaces cruzados: adjudicación** | parcial | se proponen 15 enlaces explícitos que resuelven; el resto son menciones en prosa que requieren criterio humano |
| **Revisión nativa del tablero** | **sin cerrar** | el ciclo de 4 lentes encontró 5 fallas críticas, todas corregidas. La validación dirigida **sí funciona**: se cerró una el 2026-10-03 (D-028, diagnóstico corregido). Lo que sigue abierto es la línea que se detuvo por un rechazo hoy considerado intermitente |
| **Publicación del trabajo actual** | **publicado** | el árbol está limpio, todo commiteado y **todo pusheado** (`origin/master` = `a5b4ce1`). El workflow `gate` corre en cada push y está verde (corrida `37181123862`) |
| **`REPORT.md` para maintainers** | no implementado | informe acotado a 15 ítems por sección, cada uno con `verificado_por_humano: no` |
| **Modo sombra** | no implementado | calcular prioridad sugerida sin mostrarla ni aplicarla, para comparar contra las decisiones humanas |

El detalle con evidencia y estado está en [`PROMISES.md`](PROMISES.md) y [`STATUS.md`](STATUS.md).

---

## 5. Resumen en una tabla

| Pregunta | Respuesta |
| --- | --- |
| ¿El motor da el mismo resultado con el mismo snapshot? | **Sí**, byte a byte, verificado entre procesos |
| ¿La banda depende de decisiones pasadas? | **No** |
| ¿La columna depende de una persona? | **Sí**, y es el punto |
| ¿Se puede reconstruir el estado desde el log? | **Sí**, verificado |
| ¿El sistema aprende de los movimientos? | **No** |
| ¿Guarda las decisiones para medir después? | **Sí** |
| ¿Hay alguna cifra de acierto publicada? | **No.** Sólo cobertura. Precisión pendiente de validación humana |
| ¿El tablero escribe en GitHub? | **No**, y hay un chequeo que lo verifica |

---

## 6. Lo que ninguna cifra de este proyecto significa todavía

Vale decirlo junto, porque aplica a todo:

1. **Cobertura no es acierto.** Que una regla toque 399 issues no dice que los clasifique bien.
2. **Las reglas no están validadas por personas.** Los cambios posteriores a la auditoría están marcados como *pendientes de validación humana*, y no se declara ninguna mejora de precisión hasta que exista una muestra etiquetada a mano.
3. **El snapshot es un corte.** Los números son de ese corte, no del backlog vivo.
4. **Nada de esto se aplicó en los repositorios.** El sistema no etiqueta, no comenta, no cierra ni transfiere: no hay una sola escritura hacia GitHub.
