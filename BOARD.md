# BOARD.md — Tablero Kanban de mantenimiento (local, en pruebas)

> **Qué es.** Una consola local que muestra los issues abiertos como tarjetas en un tablero Kanban, **separados por aplicación** (`gentle-ai`, `engram`, `gentle-shell`), para que un maintainer los mueva por fases hasta que alguien se hace cargo.
>
> **Qué NO es.** No es un bot. No comenta, no etiqueta, no cierra, no transfiere nada en GitHub. No contacta maintainers. El estado del tablero es **nuestro**, vive en una base local.
>
> **Estado.** En pruebas. Nada de lo que muestra está validado por humanos todavía.

---

## 0. Cómo se levanta

```bash
python3 board/server.py --ingest          # http://127.0.0.1:8770/
python3 board/server.py --port 8780       # otro puerto, si hace falta
python3 board/server.py --host 0.0.0.0    # RECHAZADO a propósito: el tablero es local
```

- Puerto por defecto **8770**, distinto del **8000** que ya ocupa el cockpit del CRM de ByBusiness.
- Bindea **solo a `127.0.0.1`**. El servidor rechaza cualquier otra interfaz: es una consola local, no un servicio de red.
- No necesita build, ni npm, ni dependencias externas: Python stdlib y HTML/JS plano.

---

## 1. Por qué el estado no vive en GitHub

```
   GitHub (Gentleman-Programming)                    GitHub
        │                                              ▲
        │  sync-products.sh  (solo lectura)            │
        ▼                                              │  NADA. Cero escrituras.
   products/ + issues.json (snapshot, 1.228)           │  No existe camino de vuelta.
        │                                              │
        ▼                                              │
  ┌──────────────────────────────┐                     │
  │  Motores deterministas       │                     │
  │   db/rules.py   → banda sug. │                     │
  │   modules/A..D  → señales    │                     │
  └──────────────┬───────────────┘                     │
                 │  derivado (sin decisión)            │
                 ▼                                     │
  ┌──────────────────────────────┐   ┌─────────────────────────┐
  │  db/board.db (SQLite local)  │◄─►│  events  append-only    │
  │   cards (proyección)         │   │  quién, cuándo, por qué │
  │   card_state / human_labels  │   └─────────────────────────┘
  └──────────────┬───────────────┘
                 │  HTTP 127.0.0.1:8770
                 ▼
  ┌──────────────────────────────┐
  │  UI Kanban (HTML+JS)         │
  │  arrastrar = decisión humana │
  └──────────────────────────────┘
```

`db/board.db` está **fuera de git**: es tu estado local, no un artefacto publicable. Lo que sí se publica es el esquema y los reportes.

---

## 2. Tres tableros, nunca mezclados

Cada aplicación tiene su propio tablero. Las tarjetas no se cruzan y no hay vista "todo junto".

```
[ gentle-ai ]  [ engram ]  [ gentle-shell ]        ← pestañas en la barra superior
```

Distribución **derivada por el motor**, del snapshot **`39553742aa7bf1ea`** — que es `sha256("issues.json")[:16]`, emitido por `board/core.py::snapshot_meta()` y expuesto en `/api/health`. El **digest del snapshot es Clase A** (reproducible por comando desde un dato del árbol); la **distribución por columna es Clase C**, porque se mide sobre `db/board.db`, que está fuera de git: se reproduce con `python3 board/server.py --ingest --port 8770`.

| Aplicación | Total | Entrada | Falta información | Revisión humana | Listo | En manos |
| --- | --- | --- | --- | --- | --- | --- |
| `gentle-ai` | 733 | 492 | 231 | 10 | 0 | 0 |
| `gentle-shell` | 424 | 272 | 146 | 6 | 0 | 0 |
| `engram` | 71 | 60 | 7 | 4 | 0 | 0 |

Ninguna tarjeta arranca en "Listo" ni en "En manos": esas columnas solo se llenan cuando una persona las mueve.

---

## 2b. Qué significa cada cosa

La leyenda completa — bandas P0–P3, `falta info ×N`, `⚠ mirada humana`, `zona gris` y el uso de la barra lateral — está en **[`GLOSSARY.md`](GLOSSARY.md)**, y también dentro del tablero con el botón **«¿Qué significa?»**.

### Completitud no disponible

Si `products/` no está (los checkouts vendorizados, **fuera de git**), la completitud **no se
puede calcular** y el tablero lo dice: las tarjetas muestran **`completitud no disponible`**,
un badge neutro y punteado, y **ninguna se sugiere a `falta_info`**. No saber si a un reporte
le falta información no es lo mismo que saber que está completo, y el tablero no confunde las
dos cosas. Se arregla con `./sync-products.sh` y una reingesta.

## 3. Las columnas

```
┌───────────┬──────────────────┬──────────────────┬─────────────────────────┬──────────────┐
│ ENTRADA   │ FALTA INFORMACIÓN│ REVISIÓN HUMANA  │ LISTO PARA EL MANTENEDOR│ EN MANOS DEL │
│           │                  │                  │                         │ MANTENEDOR   │
│ sin triar │ al reporte le    │ candidato P0,    │ triado y confirmado     │ alguien lo   │
│           │ falta algún campo│ señal dura bajo  │ por una persona, sin    │ tomó         │
│           │ que su propio    │ prefijo no-bug,  │ bloqueos                │              │
│           │ formulario pide  │ o duplicado      │                         │              │
│           │                  │ fuerte           │                         │              │
└───────────┴──────────────────┴──────────────────┴─────────────────────────┴──────────────┘
      ↑                ↑                 ↑                    ↑                     ↑
   derivado         derivado          derivado            confirmado            confirmado
   (entrada)     (Módulo A)      (motor + Módulo B)      (humano)              (humano)
```

Más **Archivado**, que no es una columna de trabajo: se muestra con un interruptor y guarda lo descartado (duplicado confirmado, no aplica). Un issue descartado nunca se borra.

---

## 4. La regla de diseño que hace útil el tablero

> **El motor solo puede sugerir columnas de bloqueo. Nunca "Listo para el mantenedor".**

- `falta_info` (Módulo A: falta un campo requerido del formulario) → se sugiere.
- `revision_humana` (candidato P0, o señal dura bajo prefijo no-bug) → se sugiere.
- `listo_mantener` y `en_manos` → **jamás** las sugiere el motor. Promover trabajo hacia un maintainer es un juicio humano.

Verificado por tests: `test_board.py` comprueba que ninguna tarjeta se auto-promueve.

---

## 5. Derivado vs. decidido

| | Derivado por el motor | Decidido por una persona |
| --- | --- | --- |
| banda sugerida (`P0`–`P3` o candidato P0) | sí | — |
| regla aplicada y campos faltantes | sí | — |
| columna sugerida (solo bloqueos) | sí | — |
| **columna actual** | — | sí (arrastrar) |
| **veredicto humano** (`P0`–`P3` / `no válida`) | — | sí (botón) |
| notas | — | sí |

La herramienta **nunca** escribe `veredicto_humano`. Lo escribe una persona, y queda en el registro.

---

## 6. Registro append-only y auditabilidad

Cada movimiento y cada veredicto se agrega como evento; nunca se reescribe nada.

```
events:  id | ts | ref | kind (move|verdict) | from | to | actor | note | payload
```

`card_state` y `human_labels` son **cachés reconstruibles** desde ese log. No es una promesa: hay un chequeo.

```
$ python3 tools/board_rebuild_check.py
  simulated cycle on the real snapshot: 1228 cards, 2 labels, 5 events
    ✔ card_state rebuilt from events matches exactly
    ✔ human_labels rebuilt from events matches exactly
    ✔ the event log was not modified by the rebuild
  THE EVENT LOG IS THE SINGLE SOURCE OF TRUTH
```

El chequeo corre sobre copias temporales y también sobre `db/board.db` si existe. **Nunca toca el tablero vivo.**

---

## 7. API (solo local)

| Método | Ruta | Para qué |
| --- | --- | --- |
| `GET` | `/api/health` | snapshot vigente, columnas |
| `GET` | `/api/boards` | los tableros y su conteo por columna |
| `GET` | `/api/boards/<slug>/cards?column=&q=&limit=&offset=` | tarjetas de un tablero |
| `GET` | `/api/card?ref=slug%23num` | una tarjeta con su registro de eventos |
| `POST` | `/api/move` | mover una tarjeta (acción humana) |
| `POST` | `/api/verdict` | fijar el veredicto humano |
| `POST` | `/api/ingest` | recalcular señales desde el snapshot local |

Todo lo demás vive en `board/core.py`: el HTTP solo traduce. La UI no tiene reglas.

---

## 8. Qué NO hace

- No escribe en GitHub: `tools/readonly_check.py` ahora también falla si aparece **cualquier cliente HTTP saliente** (`http.client`, `urllib.request`, `requests`) en el código del proyecto.
- No comenta, etiqueta, cierra ni transfiere.
- No contacta maintainers ni redacta mensajes para ellos.
- No guarda nombres de personas: el actor por defecto es `human-1`, configurable con `BOARD_ACTOR`.
- No rellena `veredicto_humano`.
- No esconde issues: si un issue deja de estar abierto, la tarjeta se puede archivar; nunca desaparece sola.
- No mezcla aplicaciones: no hay vista conjunta.

---

## 9. Límites y estado de validación

1. **En pruebas.** El tablero no tiene validación de uso real todavía.
2. **Señales integradas hasta ahora:** banda y regla (`db/rules.py`), flag de mirada humana, y campos faltantes (Módulo A). Duplicados (B), enlaces cruzados (C) y obsolescencia (D) todavía **no** se muestran como badge por tarjeta; sus reportes en la raíz siguen siendo la fuente.
3. **Snapshot congelado.** La fecha y el hash del snapshot se muestran siempre arriba. Recalcular no baja datos nuevos de GitHub, solo reprocesa el snapshot local.
4. **Sin autenticación, a propósito:** bindea a `127.0.0.1`. No lo expongas en la LAN.
5. **UI en español:** es una consola interna, y va al lado del cockpit de ByBusiness. Los artefactos técnicos del repositorio siguen en inglés.

---

## 10. Verificación

```bash
python3 tools/verify_all.py          # puerta rápida: tests, invariantes, figuras
python3 tools/verify_all.py --full   # agrega regeneración de reportes y determinismo
```

Cubre: `test_rules.py` (129), `test_board.py` (85), contratos (12), invariante read-only, invariante de privacidad, reconstruibilidad del log del tablero y recálculo de figuras publicadas.
