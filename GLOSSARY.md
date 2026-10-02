# GLOSSARY.md — Qué significa cada cosa del tablero

> **Para quién es esto.** Para quien abre el tablero un martes con 40 issues pendientes y necesita entender en 30 segundos qué está mirando.
> La misma guía está dentro de la aplicación, en el botón **«¿Qué significa?»** de la barra superior.

---

## 1. La idea en una línea

El tablero **sugiere** y **vos decidís**. Todo lo que muestra se calcula desde un snapshot congelado de issues abiertos; no descarga nada en vivo y **no escribe nada en GitHub**.

---

## 2. Las cinco columnas (más el archivo)

| Columna | Para qué sirve |
| --- | --- |
| **Entrada** | Todo issue abierto cae acá al analizarse. Es la bandeja: todavía nadie lo miró. |
| **Falta información** | El reporte no trae lo que su propio formulario pide. Acá no hay nada que decidir: hay que pedir datos. |
| **Revisión humana** | Hay algo que requiere ojo humano: un candidato P0, o una señal dura bajo un prefijo que no es de bug. |
| **Listo para el mantenedor** | Vos lo triaste y confirmaste. Solo lo llena una persona. |
| **En manos del mantenedor** | Alguien se hizo cargo. Lo marcás vos. |
| **Archivado** | Descartado o duplicado confirmado. **No se borra**: se guarda y se ve con el interruptor «archivados». |

> **El motor solo puede sugerir columnas de bloqueo** (`Falta información` y `Revisión humana`).
> Nunca sugiere «Listo» ni «En manos»: promover trabajo hacia un mantenedor es un juicio humano.

---

## 3. Las bandas de prioridad

Acá está lo que preguntabas: **P0–P3 no son un puntaje de gravedad**, son un lugar donde mirar primero.

| Etiqueta | Qué significa |
| --- | --- |
| **candidato P0** | El texto describe **pérdida silenciosa de datos o corrupción**. En el tablero **nunca vas a ver un «P0» final**: el motor emite un *candidato* y lo tiene que confirmar una persona. Los 14 candidatos están en `gold-p0-p1.md` con `veredicto_humano: pendiente`. |
| **P1** | Crash duro: `panic:`, `SIGSEGV`, «no arranca», «se queda sin memoria», desborde de pila… **y no hay workaround ni recuperación al reintentar**. Es un bloqueo sin salida. |
| **P2** | Degrada funcionalidad, **o** existe un workaround manual, **o** se recupera al reintentar, **o** es un pedido de funcionalidad (`feat:`). Es donde cae la mayoría. |
| **P3** | Documentación, pregunta, tarea de mantenimiento (`chore`), cosmético. |
| **zona gris** | El motor **no pudo** clasificarlo con una regla determinista. **No significa «sin importancia»**: significa *sin clasificar todavía*. Necesita el pase con LLM o tu criterio. |

Los colores de la tarjeta siguen la misma lógica: rojo (candidato P0), amarillo (P1), azul (P2), gris (P3) y gris oscuro (zona gris).

### Por qué P1 es tan restrictivo

Se calibro con esta regla: **si existe un workaround o el fallo se recupera al reintentar, va a P2**. Sin eso, el ecosistema producía cientos de «urgentes» y el maintainer dejaba de mirarlos. Un P1 que se puede esquivar no es un P1.

---

## 4. Las insignias de cada tarjeta

| Insignia | Qué significa |
| --- | --- |
| `falta info ×N/T` | Al reporte le faltan **N de los T campos que su propio formulario de GitHub marca como obligatorios**. No es una opinión: sale de comparar el reporte contra `products/<repo>/.github/ISSUE_TEMPLATE/*.yml`. Pasando el mouse ves **cuáles** campos faltan. El color indica severidad (ver abajo). |
| `⚠ mirada humana` | Hay una **señal dura** (pérdida de datos o crash), pero el título tiene un prefijo que no es de bug (`feat:`, `docs:`). El motor **no** sube la banda en ese caso: solo te pide que mires. El prefijo lo eligió quien reportó y no se pisa solo. |
| `rule:...` | La regla determinista que decidió la banda. En la tarjeta se muestra en castellano («pedido de funcionalidad», «crash duro», «candidato P0»); el nombre crudo queda en el tooltip. |
| `veredicto P2` | **Tu** etiqueta humana, ya guardada. Esta es la que vale para medir precisión. |
| `sugerido: falta info` | El motor sugiere mover esta tarjeta. **No la movió**: espera tu confirmación. |

---

## 4b. La severidad de `falta info`

El color de la insignia es **proporcional**, no absoluto: faltar 1 de 2 campos pesa más que faltar 1 de 8. La proporción es `N/T`.

```
  poco             medio            alto             crítico
  ▓▓▓▓             ▓▓▓▓             ▓▓▓▓             ▓▓▓▓
  blanco           amarillo         naranja          rojo          ← color de la insignia
  < 34%            34% a 59%        60% a 79%        ≥ 80%         ← proporción de campos ausentes
```

| Severidad | Proporción ausente | Lectura para el maintainer |
| --- | --- | --- |
| **poco** (blanco) | menos de 34% | el reporte está casi completo; pedile el detalle que falta |
| **medio** (amarillo) | 34% a 59% | falta alrededor de un tercio: hay que pedir datos antes de triar |
| **alto** (naranja) | 60% a 79% | falta más de la mitad: no hay con qué decidir todavía |
| **crítico** (rojo) | 80% o más | falta casi todo lo que el formulario pide |

La regla se calcula en `board/core.py` (`missing_severity`) y la interfaz solo pinta el color: no hay lógica de negocio en el JavaScript (`DECISIONS.md` D-023). Está cubierta por tests, que verifican que la escala sea monótona y proporcional.

**Ojo con cómo se lee.** `falta info` no dice que el issue sea malo: dice que **el reporte no trae lo que su propio formulario pide**. Un issue con severidad crítica puede ser perfectamente válido — lo que falta es información para triarlo. Y al revés: un reporte completo puede estar igual de equivocado.

## 4c. Las etiquetas de arriba: prenden y apagan el Kanban

Cada etiqueta de la barra superior es un **interruptor** y muestra **entre paréntesis cuántos issues la llevan**:

```
[candidato P0 (9)] [P1 (10)] [P2 (210)] [P3 (43)] [zona gris (461)] [falta info (231)] [mirada humana (12)]
      ↑ prendida: sus tarjetas se ven          ↑ apagada: sus tarjetas desaparecen y se recalcula cada columna
```

| Etiqueta | Cuenta los issues que… |
| --- | --- |
| `candidato P0` | describen pérdida silenciosa de datos o corrupción |
| `P1` | tienen crash duro sin workaround |
| `P2` | degradan, tienen workaround, o son pedidos de funcionalidad |
| `P3` | son documentación, pregunta, tarea o cosmético |
| `zona gris` | **no** pudieron clasificarse de forma determinista |
| `falta info` | no traen todos los campos obligatorios de su formulario |
| `mirada humana` | tienen señal dura bajo un prefijo que no es de bug |

**Cómo se usa.** Mientras la etiqueta está prendida, sus tarjetas se ven. Cuando la apagás, **desaparecen del tablero** y los contadores de cada columna se recalculan. Sirve para dejar a la vista sólo lo que te interesa ahora: por ejemplo, apagar `zona gris` y `P2` para trabajar únicamente sobre lo urgente y lo bloqueado.

El número de cada etiqueta es del **tablero activo** y **no cambia al filtrar**: es el total de esa aplicación. Y filtrar **no mueve ninguna tarjeta ni borra nada**: es sólo una vista.

### La regla, sin ambigüedad (esto es lo que fallaba)

> **Una tarjeta desaparece cuando *lleva* la etiqueta que apagaste. No importa qué otras etiquetas tenga.**

Las etiquetas son independientes entre sí. Un issue con **varios tags** se comporta así:

| Issue | Banda | falta info | mirada humana | Apagás `P2` | Apagás `falta info` | Apagás `mirada humana` |
| --- | --- | --- | --- | --- | --- | --- |
| A | P2 | no | no | **desaparece** | sigue | sigue |
| B | candidato P0 | sí | no | sigue | **desaparece** | sigue |
| C | P3 | sí | sí | sigue | **desaparece** | **desaparece** |
| D | zona gris | sí | no | sigue | **desaparece** | sigue |

Fijate en el caso **B**: es un candidato P0 y aun así desaparece si apagás `falta info`, porque *lleva* ese tag. Y apagar `P2` **no** lo toca: la banda y la señal son ejes distintos.

### El bug que tenía (y por qué te confundía)

La primera versión evaluaba el filtro así:

```sql
NOT (band LIKE 'candidato P0%')   -- si band es NULL, esto da NULL, no TRUE
```

En SQL, `NULL` no es verdadero, así que **la fila se descartaba**. Y todo issue **sin banda** (`zona gris`) tiene `band = NULL`. Resultado: apagar **cualquier** banda se llevaba por delante **toda la zona gris**. En `gentle-ai`, apagar `P0` hacía desaparecer **470** tarjetas cuando el tag decía **9** (9 de P0 + 461 de zona gris).

Está corregido con `COALESCE` en cada condición, y hay un test de regresión que exige que **apagar un tag quite exactamente las tarjetas que ese tag cuenta** — verificado para los tres tableros y los siete tags:

```
gentle-ai    apagar p0 -> desaparecen 9 | tag dice 9 | quedan 724   ✔
             apagar p1 -> desaparecen 10 | tag dice 10 | quedan 723  ✔
             apagar p2 -> desaparecen 210 | tag dice 210 | quedan 523 ✔
             ...
```

## 5. La barra lateral (se abre al hacer clic en una tarjeta)

Era lo que veías vacío: **tenía un bug de CSS** (`display:flex` pisaba el atributo `hidden`, así que quedaba siempre abierta y «cerrar» no hacía nada). Ya está corregido. Se usa así:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TÍTULO Y ESTADO                                          │
│    banda sugerida · regla aplicada · mirada humana          │
│    columna sugerida · columna actual y desde cuándo         │
├─────────────────────────────────────────────────────────────┤
│ 2. CAMPOS QUE FALTAN — la lista concreta de lo que el       │
│    formulario pide y el reporte no trae                     │
├─────────────────────────────────────────────────────────────┤
│ 3. VEREDICTO HUMANO — seis botones: P0 P1 P2 P3 no válida   │
│    Elegís uno y queda guardado al instante.                 │
│    ⚠ Esto lo escribís vos: la herramienta NUNCA lo completa.│
├─────────────────────────────────────────────────────────────┤
│ 4. NOTA — una línea libre: por qué decidiste eso.           │
├─────────────────────────────────────────────────────────────┤
│ 5. REGISTRO (append-only) — todo lo que pasó con la tarjeta:│
│    cada movimiento y cada veredicto, con fecha y autor.     │
│    Nada se reescribe: si algo se equivocó, se agrega otro   │
│    evento.                                                  │
├─────────────────────────────────────────────────────────────┤
│ 6. abrir en GitHub ↗ — te lleva al issue real para leer el  │
│    hilo completo. La herramienta no lo abre por vos.        │
└─────────────────────────────────────────────────────────────┘
```

**Para mover una tarjeta de columna no uses la barra lateral: arrastrala** en el tablero. La barra lateral es para leer y para decidir, no para mover.

Se cierra con el botón «cerrar», con `Escape`, o haciendo clic afuera.

---

## 6. La barra superior

| Elemento | Qué hace |
| --- | --- |
| **Pestañas** `engram` · `gentle-ai` · `gentle-shell` | Un tablero por aplicación. **Nunca se mezclan**; no hay vista conjunta a propósito. El número es cuántas tarjetas abiertas tiene cada uno. |
| **Snapshot** | El hash y la fecha del corte de datos con el que estás trabajando. Si es viejo, se ve: es a propósito que no se refresque solo. |
| **Buscar** | Filtra por título o `#número` dentro del tablero activo. |
| **archivados** | Muestra u oculta la columna de descartados. |
| **Recalcular** | Vuelve a correr las señales deterministas sobre el snapshot local. **No descarga nada de GitHub** y **no toca tus decisiones**. |
| **¿Qué significa?** | Esta misma guía. |

---

## 7. Qué NO hace el tablero

- No etiqueta, no comenta, no cierra y no transfiere nada en GitHub.
- No contacta maintainers ni redacta mensajes para ellos.
- No rellena el veredicto humano: lo escribís vos.
- No guarda nombres de personas: el autor de cada movimiento es una etiqueta local (`human-1`).
- No esconde issues: si uno se cierra en GitHub, la tarjeta se archiva, no desaparece.

---

## 8. De dónde sale cada dato (para el revisor externo)

| Lo que ves | De dónde sale | Reproducible con |
| --- | --- | --- |
| Banda y regla | `db/rules.py` | `python3 db/rules.py` |
| `falta info ×N` | Módulo A contra los formularios reales de cada repo | `python3 modules/completeness.py` |
| Mirada humana | Señal dura bajo prefijo no-bug (`requires_human_review`) | `python3 db/rules.py` |
| Columna y veredicto | Decisiones humanas en un log append-only local | `python3 tools/board_rebuild_check.py` |
| Conteos y snapshot | `issues.json` congelado | `python3 tools/metrics.py` |

Todo lo publicable del proyecto vive en la raíz del repositorio; los módulos que generan estos datos están en `modules/` y el motor en `db/`.
