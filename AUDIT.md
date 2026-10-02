# AUDIT.md — Adversarial Design Audit (H1–H10 and Bands P0–P3)

> **Read-only audit. No engine, schema, or rules documentation was modified.**
> Scope: the 1,228 open issues in `issues.json`, evaluated against the deterministic engine in `db/rules.py`.
> Corrections are listed **only as proposals** (§11) and were **not implemented**.

---

## 0. One-Screen Summary

- **Split (deterministic, reproducible):** `sha256(slug + "#" + number) mod 5`; **group 0 = held-out (231 issues)**, **groups 1–4 = exploration (997 issues)**. Patterns were authored while looking **only at exploration**; the frozen patterns were then applied unchanged to held-out. No tuning on held-out.
- **Deterministic coverage:** exploration 385/997 (38.6%), held-out 98/231 (42.4%), total 483/1,228 (39.3%).
- **Highest-risk finding (audit 1):** the `is_bug` gate makes a `feat:`-prefixed issue **structurally unable** to reach candidate P0/P1. **25 `feat:` issues (18 exploration / 7 held-out) contain hard loss-or-crash signals and are all P2.**
- **Second-highest (audit 2):** **50 exploration / 9 held-out grey-area issues carry unnegated hard signals.** The crash vocabulary is too narrow: `uncaughtException` (camelCase, 5 issues) and `crashes Pi`, `fails to start`, `out of memory` are missed.
- **Rule order (audit 3):** the feature predicate runs **before** docs; **4 `docs:`-titled issues with an `enhancement`/`type:feature` label are P2 instead of P3.**
- **Manipulability (audit 4):** **6 issues whose title begins with a conventional token have an empty `title_prefix`** (leading backtick or `[Automated provider defect]` prefix); **5 of them are grey**, including a `bug()` crash report.
- **H9 never fires on real data:** **0 issues** are demoted to P2 by `rule:crash_with_workaround_demoted_to_p2` across 1,228 issues.
- **H1/H2/H5 hold:** 0 violations on the corpus. **H3, H4, H6, H7, H8 are not auditable with this dataset** (process rules or dimensions the dataset does not carry) — reported as such, not invented.
- **Cross-repo coverage (audit 8):** only **26** issues carry structured `cross_refs`; **345 issues (269 exploration / 76 held-out)** mention another repo slug in text with **no structured link**.

**Provenance note:** all counts are computed by a read-only harness over `issues.json`. Broad counts are an **upper bound** and contain heuristic noise (documented per audit). Where a number cannot be computed, it is written **"no disponible"**.

---

## 1. Findings Table

| id | auditátoría | gravedad | n exploración | n held-out | ejemplo |
| --- | --- | --- | --- | --- | --- |
| A1-broad | Demociones peligrosas (señal amplia) | **alta** | 101 | 31 | `gentle-ai#2123` |
| A1-feat-hard | `feat:` con señal dura → P2 garantizado | **alta** | 18 | 7 | `gentle-ai#1989` |
| A2-broad | Zona gris con señal amplia | **alta** | 250 | 51 | `gentle-ai#5056` |
| A2-tight | Zona gris con señal dura sin negación | **alta** | 50 | 9 | `gentle-shell#962` |
| A2-vocab | `crashes`/`uncaughtException`/`fails to start` fuera del vocabulario | **alta** | 42 | 10 | `gentle-ai#4677` |
| A3-order | Feature antes que docs decide la banda | media | 11 | 4 | `gentle-ai#5168` |
| A4-prefix | Prefijo no coincide con contenido (amplio) | media | 197 | 48 | `gentle-ai#4992` |
| A4-extract | `title_prefix` vacío pese a token convencional | **alta** | 5 | 1 | `gentle-ai#4974` |
| A5-labels | Contradicción labels ↔ prefijo | media | 8 | 0 | `gentle-ai#4046` |
| A6-H1 | H1 implicación sola no promueve | — | 0 violaciones | 0 violaciones | — |
| A6-H2 | H2 toda banda tiene razón y cita | — | 0 violaciones | 0 violaciones | — |
| A6-H3/H7/H8 | Proceso (no auditable aquí) | no disponible | no disponible | no disponible | — |
| A6-H6 | Dimensiones ausentes = unknown | no disponible | no disponible | no disponible | — |
| A7-H9 | H9 democión por workaround | media | 0 demotados | 0 demotados | `gentle-shell#889` |
| A8-cross | Cobertura cruzada estructurada | media | 269 sin índice | 76 sin índice | `gentle-ai#5175` |

---

## 2. Método (anti-sobreajuste)

1. **Split determinista y reproducible:** `int(sha256(f"{slug}#{number}").hexdigest(), 16) % 5`. Grupo 0 = held-out; 1–4 = exploración. Reproducible con cualquier lenguaje; no usa `hash()` aleatorio de Python.
2. **Patrones congelados tras explorar solo grupos 1–4.** Se fijaron como expresiones regulares y luego se aplicaron **sin modificación** al grupo 0. Los conteos de exploración y held-out se reportan por separado en cada auditoría.
3. **Dos niveles por auditoría:** *broad* (señal amplia, cota superior, con ruido) y *tight* (misma señal con guarda de negación). El nivel tight reduce el ruido pero **no lo elimina** (adjetivos compuestos como `crash-safe`, `crash-recoverable`, y usos hipotéticos).
4. **Sin propuestas implementadas.** §11 lista propuestas; el motor, los esquemas y `docs/triage-model.md` no se tocaron.

---

## 3. Auditoría 1 — Demociones peligrosas (mayor riesgo)

**Propiedad:** ningún issue cuyo texto describe pérdida de datos o crash debería quedar en P2/P3.

### 3.1 Mecanismo encontrado (el hallazgo central)

La evaluación de candidato P0 y P1 está **condicionada por `is_bug`**:

```
is_bug = title_prefix in ("bug","fix") or label in ("bug","type:bug")
if is_bug and has_silent_data_loss(...) -> candidato P0
if is_bug and is_hard_crash(...)        -> P1 o P2
# luego, y solo entonces:
if prefix in ("feat","feature") or ...  -> P2
```

Consecuencia: un issue `feat:` **nunca** puede llegar a candidato P0/P1, aunque su cuerpo describa pérdida silenciosa de datos o un crash. Medición:

- `feat:` con señal dura (loss/crash): **25 issues — 18 exploración / 7 held-out — los 25 clasificados P2.**

Ejemplos (señal dura bajo prefijo `feat`):

- `gentle-ai#1989` — *feat(gemini): modularize GEMINI.md root to survive Antigravity 12k truncation*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1989
  - quote: "every fresh `agy` session silently drops: `trigger-rules` (skill auto-loading) - the entire Engram protocol"
  - veredicto_humano: pendiente
- `gentle-shell#1591` — *feat(profiles): directory-based profile rules so unpinned clones stop silently falling back*
  - https://github.com/Gentleman-Programming/gentle-shell/issues/1591
  - quote: "One keypress silently overwrites the pinned profile with the global routing"
  - veredicto_humano: pendiente
- `gentle-shell#675` — *feat(vision): add capability-based vision fallback for text-only models*
  - https://github.com/Gentleman-Programming/gentle-shell/issues/675
  - quote: "pasted images, `read` on image files) are silently dropped: Pi's provider layer replaces each image block"
  - veredicto_humano: pendiente

### 3.2 Conteo por niveles

| Nivel | exploración | held-out |
| --- | --- | --- |
| broad (señal amplia, cota superior) | 101 (10.1% de 997) | 31 (13.4% de 231) |
| tight (señal dura sin negación) | 24 | 6 |

Desglose broad por regla: `rule:feature_request` 111, `rule:docs_chore_question` 21. Por familia: P0 59, P1 73.

Otros ejemplos tight (exploración):

- `gentle-ai#2123` — *feat(sync): preserve user customizations in managed agent instruction files during sync*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2123
  - quote: "tweaking their persona section or the Engram protocol) is silently lost on the next sync"
  - veredicto_humano: pendiente
- `gentle-ai#1562` — *feat(skill-registry): project-defined extra skill sources*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/1562
  - quote: "Every refresh silently drops all 8 (including the ones the project's CLAUDE.md marks as auto-loading)"
  - veredicto_humano: pendiente
- `gentle-ai#4463` — *feat(skills): branch-pr needs a repo-detection gate*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4463
  - quote: "a local patch gets silently overwritten on the next `gentle-ai sync`"
  - veredicto_humano: pendiente

**Ruido declarado del nivel tight (no son defectos reales):** `gentle-ai#4403` ("Crash-safe by kernel release"), `gentle-ai#3570` ("crash-recoverable"), `gentle-ai#3841` (inventario meta), `gentle-ai#3783` ("rather than silently overwriting", intención de diseño). Por eso el número tight es una **cota con ruido**, no una confirmación.

**Falsos positivos del nivel broad (documentados):** `gentle-ai#4600` dice literalmente *"nothing here is a crash or a failure"* y `gentle-ai#921` describe una obligación de diseño (*"must not silently drop cloud state"*). El broad los cuenta; el tight con guarda de negación aún puede fallar en el segundo caso.

---

## 4. Auditoría 2 — Zona gris con señales duras (falsos negativos P0/P1)

**Propiedad:** un issue sin banda cuyo texto describe pérdida o crash no debería quedar sin clasificar.

| Nivel | exploración | held-out |
| --- | --- | --- |
| broad | 250 (25.1% de 997) | 51 (22.1% de 231) |
| tight (sin negación) | 50 | 9 |

Por familia (broad): P0 113, P1 188.

### 4.1 Vocabulario de crash demasiado estrecho

`RE_P1_CRASH_CORE` solo reconoce `panic:`, `SIGSEGV`, `fatal error: runtime`, `segmentation fault`, `NullPointerException`, `uncaught exception` (con espacio) y `stack overflow`. No reconoce: `crashes`, `crashed`, `uncaughtException` (camelCase), `fails to start`, `out of memory`, `freeze`.

- Issues con `uncaughtException` (camelCase): **5**. Issues con `uncaught exception` (con espacio): **1**. Los 4 restantes quedan en banda `None` (o el único P1 detectado, `gentle-shell#1606`).

Ejemplos (held-out y exploración):

- `gentle-shell#962` — *bug(skill-registry): recursive skill watcher crashes Pi with uncaughtException ENOENT*
  - https://github.com/Gentleman-Programming/gentle-shell/issues/962
  - quote: "recursive skill watcher crashes Pi with uncaughtException ENOENT"
  - veredicto_humano: pendiente
- `gentle-ai#4677` — *bug(cli): bare `gentle-ai` invocation crashes with Go runtime panic*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4677
  - quote: "bare `gentle-ai` invocation crashes with Go runtime panic (traceback did not unwind completely)"
  - veredicto_humano: pendiente
- `gentle-ai#4816` — *[Automated provider defect] bug(opencode): orchestrator calls unavailable tools*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4816
  - quote: "TypeError crashes session before work begins"
  - veredicto_humano: pendiente
- `gentle-shell#745` — *bug(gentle-shell): /reload crashes Pi — stale session ctx captured*
  - https://github.com/Gentleman-Programming/gentle-shell/issues/745
  - quote: "/reload crashes Pi — stale session ctx captured in prompt/footer"
  - veredicto_humano: pendiente

### 4.2 Pérdida silenciosa no reconocida sin la palabra "silent"

- `gentle-ai#4809` — *bug(pi): CodeGraph child overlay corrupts tools frontmatter into invalid YAML — Pi fails to start*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4809
  - quote: "CodeGraph child overlay corrupts tools frontmatter into invalid YAML — Pi fails to start"
  - veredicto_humano: pendiente
- `gentle-ai#5056` — *[Automated provider defect] opencode: attributed-write guard refuses a session the store still reports open*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5056
  - quote: "End-of-session memory is silently lost exactly at the moment it matters most"
  - veredicto_humano: pendiente

### 4.3 `fails to start` / `out of memory`

- `gentle-ai#4974` — *`bug(install): Pi commands fail through pi.cmd on Windows*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4974
  - quote: "the process can fail to start even though `pi --version` works in an interactive terminal"
  - veredicto_humano: pendiente
- `gentle-ai#4807` — *bug(TUI) ResolveTarget can bake another tool's wrapper as the OpenCode target*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4807
  - quote: "until the machine runs out of memory"
  - veredicto_humano: pendiente

**Advertencia de honestidad:** estos 50/9 son candidatos del detector tight, no confirmaciones. Algunos contienen usos no defectuosos (referencias cruzadas a otros issues, condiciones hipotéticas). El `veredicto_humano` queda pendiente en todos.

---

## 5. Auditoría 3 — Conflictos y orden de reglas

**Propiedad:** cuando dos predicates coinciden, la banda depende del orden de evaluación.

Orden real en `classify_issue_deterministically`: **candidato P0 → P1/P2-crash → feature → docs**.

| Métrica | exploración | held-out |
| --- | --- | --- |
| issues con ≥2 predicates verdaderos | 11 | 4 |
| combinaciones observadas | `('feat','docs')` ×15 en total | ídem |
| casos donde un predicate de menor prioridad decidió | 15/15 (100%) | ídem |

### 5.1 El caso concreto: feature gana a docs

`title_prefix = docs` → 15 issues: **11 resultan P3**, pero **4 resultan P2** porque traen label `enhancement`/`type:feature` y el predicate feature se evalúa antes.

- `gentle-ai#5168` — *docs(sdd): remove retired SDD references from living docs* (labels: `enhancement`, `status:approved`)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5168
  - quote: "docs(sdd): remove retired SDD references from living docs"
  - banda actual: **P2** (`rule:feature_request`) — esperada por prefijo: P3
  - veredicto_humano: pendiente
- `gentle-ai#3273` — *docs(security): add a private vulnerability disclosure path* (labels: `enhancement`, `type:feature`)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/3273
  - quote: "docs(security): add a private vulnerability disclosure path"
  - banda actual: **P2** (`rule:feature_request`) — esperada por prefijo: P3
  - veredicto_humano: pendiente
- `gentle-ai#2732` — *docs(cli): expose valid --persona values in install --help*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/2732
  - quote: "docs(cli): expose valid `--persona` values in `install --help`"
  - banda actual: **P2** — veredicto_humano: pendiente

### 5.2 El conflicto estructural de la auditoría 1, visto como orden

`feat` + señal dura: el predicate `p0`/`p1` nunca se activa (por `is_bug`), así que el orden decide **siempre** a favor de P2. **25 issues (18/7)**.

---

## 6. Auditoría 4 — Manipulabilidad del prefijo

**Propiedad:** el prefijo del título debe describir el contenido; si no, la banda es manipulable.

| Nivel | exploración | held-out |
| --- | --- | --- |
| broad (prefijo no-bug + marcadores de bug) | 197 (19.8%) | 48 (20.8%) |
| k ind: `feat`+contenido de bug | 194 (total) | ídem |
| kind: prefijo no-bug + contenido de bug | 51 (total) | ídem |
| bandas resultantes | P2 212, P3 26, None 7 | ídem |

**Ruido declarado:** el marcador incluye `fails`, `error`, `regression`, `broken`, que aparecen en prosa legítima de features (p. ej. criterios de aceptación sobre regresiones). El número broad es cota superior.

### 6.1 El hallazgo preciso: extracción de `title_prefix` falla

**6 issues cuyo título comienza con un token convencional tienen `title_prefix` vacío**: **5 quedan grises** y 1 es P2. Causas: backtick inicial (`` `bug(install): ``) y prefijo `[Automated provider defect]`.

- `gentle-ai#4974` — **título:** `` `bug(install): Pi commands fail through pi.cmd on Windows `` → `title_prefix = ''` → `is_bug = False` → **banda None**
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4974
  - quote: "`bug(install): Pi commands fail through pi.cmd on Windows"
  - veredicto_humano: pendiente
- `gentle-ai#4816` — **título:** `[Automated provider defect] bug(opencode): orchestrator calls unavailable tools` → `title_prefix = ''` → **banda None**
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4816
  - quote: "[Automated provider defect] bug(opencode): orchestrator calls unavailable tools"
  - veredicto_humano: pendiente
- `gentle-ai#4807` — **título:** `bug(TUI) ResolveTarget ...` → `title_prefix = ''` → **banda None**
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4807
  - quote: "bug(TUI) ResolveTarget can bake another tool's wrapper as the OpenCode target"
  - veredicto_humano: pendiente

Otros afectados: `gentle-ai#2520`, `gentle-ai#1968`, `gentle-shell#1305`, `gentle-shell#804`.

Ejemplo de manipulación por contenido en exploración:

- `gentle-ai#4992` — *feat(review): classify provider usage-limit transport failures*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4992
  - quote: "the observed error text, and could leave commands hanging for a long time"
  - banda actual: **P2** — veredicto_humano: pendiente

---

## 7. Auditoría 5 — Etiquetas vs prefijo

**Propiedad:** si label y prefijo se contradicen, debe quedar documentado qué regla gana.

| Métrica | exploración | held-out |
| --- | --- | --- |
| contradicciones labels ↔ prefijo | 8 | 0 |

Desglose y regla ganadora:

- `docs` prefijo + label `bug` (3 casos) → gana **docs** (P3).
- `bug` prefijo + label `feature`/`enhancement` (5 casos) → gana **feature** (P2).

Ejemplos:

- `gentle-ai#4428` — *docs prefix + bug label* → banda **P3** (`rule:docs_chore_question`)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4428
  - quote: "docs: quickstart and trigger-rules still name v2.6.0 as the current stable release" (label `type:bug`)
  - veredicto_humano: pendiente
- `gentle-ai#4046` — *fix prefix + feature label* → banda **P2** (`rule:feature_request`)
  - https://github.com/Gentleman-Programming/gentle-ai/issues/4046
  - quote: "Executing the exact printed transition fails `git_command_failed` before mutation begins" (label `type:feature`)
  - veredicto_humano: pendiente

El held-out no repite el patrón (0 casos): la contradicción existe pero **no se repite** fuera de exploración con este split.

---

## 8. Auditoría 6 — Reglas H1–H10, una por una

| Regla | Propiedad comprobable | Violaciones | Ejemplos |
| --- | --- | --- | --- |
| **H1** | La banda no depende de `cross_refs` (implicación sola no promueve) | **0** | clasificar con `cross_refs=[]` vs original: 0 diferencias de banda |
| **H2** | Toda banda emitida tiene ≥1 razón (`rule_name`) y ≥1 cita (span de evidencia o `cross_ref`) | **0** | 483/483 bandas emitidas con ancla de evidencia; 25/25 con `cross != none` tienen `cross_ref` |
| **H3** | Inferencia siempre con `confidence` obligatoria | **no auditable con este dataset** | el dataset no lleva campo `confidence` |
| **H4** | Causas independientes se separan, no se promueven juntas | **no auditable con este dataset** | requiere las definiciones del patrón (c), ausentes del dataset |
| **H5** | Alcance cosmético nunca promueve | **0** (se sigue de H1) | ídem H1 |
| **H6** | Dimensión ausente = `unknown` | **no auditable con este dataset** | el dataset no lleva dimensiones |
| **H7** | Override del maintainer siempre gana | **no auditable con este dataset** | regla de proceso, sin eventos de override |
| **H8** | Pass-1 provisional, Pass-2 corrige | **no auditable con este dataset** | regla de proceso, sin corrida de 2 pases |
| **H9** | Crash con workaround/retry → P2 | ver auditoría 7 | 0 demotados |
| **H10** | Prefiltro determinista por patrón estructural | ver abajo | 4 derrotas de orden en `docs:` |

### 8.1 H10 en detalle

- Cobertura determinista: **exploración 385/997 (38.6%)**, **held-out 98/231 (42.4%)**, total 483/1,228 (39.3%).
- `title_prefix = feat` → **338/338 P2** (cumple).
- `title_prefix = docs` → **11/15 P3**; **4 van a P2** por orden (ver §5.1) → H10 incumplida para esos 4.
- La promesa "patrón estructural → banda determinista" se rompe además para los **6 issues con `title_prefix` vacío** (§6.1), que caen a gris pese a tener prefijo visual.

### 8.2 Ejemplo de H1/H5 con dato cruzado

- `gentle-ai#5166` — *bug(review): un lens admitió un CRITICAL TS6306 ... dead-ending the lineage*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5166
  - quote: "making fix_finding_ids unsatisfiable and dead-ending the lineage"
  - banda: **None** (correcto: "dead-end" metafórico sin contexto de hilo). veredicto_humano: pendiente

---

## 9. Auditoría 7 — H9 (workaround / retry)

| Métrica | exploración | held-out | total |
| --- | --- | --- | --- |
| issues crash-like (`crash`/`panic`/`fails to start`) | 42 | 10 | 52 |
| con workaround detectado por el regex actual | — | — | 6 |
| **demotados a P2 por `rule:crash_with_workaround_demoted_to_p2`** | **0** | **0** | **0** |

**Hallazgo:** H9 **no produce ninguna democión** sobre 1,228 issues reales. Motivo: P1 solo se emite 2 veces, y ninguna de esas dos contiene texto de workaround. Además, de los 52 issues crash-like, 46 no tienen texto de workaround y 6 sí, pero esos 6 caen en `None`/P3/P2 por otras vías.

**Cobertura de expresiones reales.** El regex `RE_WORKAROUND_POSITIVE` reconoce `workaround`, `temporary fix`, `mitigation`, `bypass`, `recovers upon retry`, `retry succeeds`, `restart fixes`. **No** reconoce expresiones reales presentes en el corpus:

- `gentle-shell#889` — *...works only after a manual step*
  - https://github.com/Gentleman-Programming/gentle-shell/issues/889
  - quote: "The same directory works after running `git init`"
  - banda actual: **None** — veredicto_humano: pendiente
- `gentle-ai#828` — *mem_save should work after gentle-ai installation*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/828
  - quote: "mem_save should work after gentle-ai installation"
  - banda actual: **None** — veredicto_humano: pendiente

Expresiones reales no cubiertas detectadas (`as a workaround`, `can work around`, `works if`, `works after`, `retry works`, `restarting helps`, `re-run works`): **4 issues (3 exploración / 1 held-out)**.

**Trampa de negación verificada:** `gentle-shell#1260` contiene *"no configuration can work around it"*, que un regex ingenuo interpretaría como workaround positivo. veredicto_humano: pendiente.

---

## 10. Auditoría 8 — Cobertura cruzada (H1)

| Métrica | exploración | held-out | total |
| --- | --- | --- | --- |
| issues con `cross_refs` no vacío | — | — | 26 |
| issues con `cross_ref` a otro sistema | — | — | 25 |
| `cross == "dependency"` emitido por el motor | — | — | 25 |
| issues que mencionan otro slug de repo en el texto | 301 | 69 | **370** |
| de ésos, **sin** `cross_ref` estructurado | 269 | 76 | **345** |

**Hallazgo:** la vinculación cruzada estructurada cubre **25** casos; el texto menciona otro repo en **370**. La diferencia (345) son menciones no indexadas. El motor no promueve por sí mismo (H1 se cumple), pero el router cruzado pierde señal.

- `gentle-ai#5175` — *bug(engram): sync overwrites a user-customized Claude Code mcpServers*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5175
  - quote: "sync overwrites a user-customized Claude Code mcpServers.engram wrapper on every run"
  - `cross` actual: **none** — veredicto_humano: pendiente
- `gentle-ai#5075` — *(mem_* tools fail)*
  - https://github.com/Gentleman-Programming/gentle-ai/issues/5075
  - quote: "gentle-engram could not confirm Engram session registration"
  - `cross` actual: **none** — veredicto_humano: pendiente

**Precisión de las menciones no indexadas: no disponible.** Muchas menciones son legítimas y no implican dependencia (p. ej. listas de instalación con `mise use -g engram`). Distinguir mención de dependencia requiere adjudicación humana.

---

## 11. Propuestas (NO implementadas)

> Ninguna propuesta fue aplicada. El motor, los esquemas y `docs/triage-model.md` quedan intactos.

1. **Desacoplar P0/P1 de `is_bug`.** Evaluar pérdida/ crash por contenido antes del gate de prefijo, o al menos cuando el prefijo sea `feat`/`docs` y el cuerpo tenga señal dura, degradar a "requiere revisión humana" en lugar de P2.
2. **Ampliar el vocabulario de crash (H10).** Añadir `crashes?/crashed`, `uncaughtException` (camelCase), `fails? to start`, `out of memory`, `unhandled exception`.
3. **Arreglar la extracción de `title_prefix`.** Tolerar backtick inicial y prefijos entre corchetes (`[Automated provider defect]`).
4. **Reordenar o hacer explícito el conflicto feature/docs.** Definir precedencia por prefijo del título sobre label de tipo.
5. **Ampliar `RE_WORKAROUND_POSITIVE`** con `as a workaround`, `can work around`, `works (if|after)`, `retry (works|helps)`, `restarting helps`, manteniendo la guarda de negación.
6. **Cobertura cruzada:** poblar `cross_refs` a partir de menciones de slug verificadas, sin promover banda (H1 intacto).
7. **Revisión humana del gold set** `gold-p0-p1.md` y de los candidatos listados aquí.

---

## 12. Límites y honestidad

- Los conteos **broad** son cotas superiores con ruido documentado. Los **tight** reducen ruido pero no lo eliminan.
- **Ningún ejemplo está confirmado**: todos llevan `veredicto_humano: pendiente`.
- **No disponible:** precisión humana de los candidatos; adjudicación completa de las 345 menciones cruzadas no indexadas; validez de H3/H4/H6/H7/H8 con estos datos.
- El split es reproducible con `sha256`; la semilla no se re-ejecutó entre exploración y medición a propósito.
