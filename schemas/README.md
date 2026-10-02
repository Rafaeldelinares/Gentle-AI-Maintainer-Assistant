# Schemas — Gentle AI Maintainer Assistant

Contratos tipados en formato **JSON Schema Draft 2020-12** para el pipeline de triaje, inferencia y decisiones del asistente en el ecosistema `Gentleman-Programming` (`gentle-ai`, `engram`, `gentle-shell`).

Siguen el estándar de contratos de `gentle-ai/contracts/`:
- Esquemas estrictos con `additionalProperties: false`.
- Pruebas automatizadas con fixtures válidas e inválidas (`validate.py`).
- Separación estructural entre inferencia del asistente (recomendación) y decisión humana (autoridad).

---

## Catálogo de Esquemas

| Esquema | ID de Contrato | Descripción |
| --- | --- | --- |
| `issue-record.schema.json` | `gentle-ai.maintainer-assistant.issue-record/v1` | Representación canónica de un issue ingerido de GitHub en cualquiera de los 3 repositorios. |
| `triage-inference.schema.json` | `gentle-ai.maintainer-assistant.triage-inference/v1` | Recomendación emitida por el asistente (código determinista o modelo LLM). Incluye banda (P0-P3), confianza, citas y justificación operativa de P1 vs P2. |
| `maintainer-decision.schema.json` | `gentle-ai.maintainer-assistant.maintainer-decision/v1` | Decisión canónica emitida por un maintainer humano (`accept`, `override`, `defer`, `close`). Requiere actor humano explícito y razón. |
| `triage-batch-report.schema.json` | `gentle-ai.maintainer-assistant.triage-batch-report/v1` | Reporte contenedor para corridas en batch o inspecciones en masa, con agregaciones y lista de inferencias. |

---

## Principios de Diseño en los Contratos

1. **Separación Estructural Inferencia vs Decisión**:
   `triage-inference` nunca contiene un campo de aprobación o ejecución; es una sugerencia puramente inferencial. La aprobación es una entidad separada (`maintainer-decision`) que exige el handle de un maintainer humano (`actor`).

2. **Soporte de Pipeline Híbrido (Código vs LLM)**:
   `triage-inference` implementa una discriminación condicional (`allOf` + `if/then`):
   - Si `source == "deterministic_rule"`, exige `rule_name` (`rule:feature_request`, `rule:docs_chore_question`, `rule:candidato_p0_requiere_revision_humana`, `rule:hard_crash`, `rule:crash_with_workaround_demoted_to_p2`), fija `model: null` y `confidence: "high"`.
   - El invariante de gobernanza se aplica en ambas direcciones: `band == "candidato P0, requiere revisión humana"` exige `rule:candidato_p0_requiere_revision_humana`, y esa regla no puede emitir un `P0` final.
   - Si `source == "llm_judge"`, exige el nombre del `model` y deja `rule_name: null`.

3. **Política Calibrada de P1 vs P2**:
   El campo `operational_rationale` exige documentar la justificación operativa acordada con el maintainer:
   - Si existe un workaround manual documentado, se demota a **P2**.
   - Si el fallo es intermitente y se recupera con reintento, se demota a **P2**.
   - **P1** queda estrictamente reservado para bloqueos totales sin salida.

4. **Escrow Asimétrico ("Hogar + Vista")**:
   En `maintainer-decision`, las reubicaciones de issues mal ubicados (`misplaced`) registran el estado de custodia (`escrow_status`: `home_notified`, `claimed_by_target`, `transferred`, `rejected`), asegurando que ningún issue se mueva automáticamente sin que el repositorio destino lo reclame explícitamente.

---

## Ejecución del Test Runner de Esquemas

```bash
# Validar esquemas y fixtures (positivo y negativo)
.venv/bin/python schemas/validate.py
```
