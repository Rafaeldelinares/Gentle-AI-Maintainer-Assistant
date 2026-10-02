# Prompts — Gentle AI Maintainer Assistant

Suite de prompts canónicos para el asistente de triaje y análisis cross-sistema en el ecosistema `Gentleman-Programming` (`gentle-ai`, `engram`, `gentle-shell`).

Diseñados bajo la disciplina de arnés de **el Gentleman**:
- Salidas estrictamente tipadas que validan contra `schemas/triage-inference.schema.json`.
- Política calibrada: Regla H9 (Workaround & Retry determinan P2; P1 reservado para dead-ends) y H10 (Código mata LLM).
- Separación visual y semántica entre hechos directos e inferencias.

---

## Catálogo de Prompts

| Archivo | Fase / Rol | Función |
| --- | --- | --- |
| **`system-triage-agent.md`** | **Master System Prompt** | Define la identidad, invariantes éticos, hechos del ecosistema, trampas de nombres (`gentle-shell` = `gentle-pi`), rúbrica calibrada y esquema JSON de salida. |
| **`pass-1-issue-analysis.md`** | **Pass 1 (A-Priori Analysis)** | Evalúa un issue aislado que cayó en la zona gris (no resuelto por `db/rules.py`). Chequea las 13 dimensiones (forzando honestidad: severidad, repro y bloqueo quedan `unknown`). Aplica el árbol de decisión operativo. |
| **`pass-2-cross-system-correlation.md`** | **Pass 2 (Cross-System)** | Evalúa correlaciones geográficas entre sistemas. Aplica los 4 patrones de implicación (a–d), verifica los bordes de acoplamiento de la arquitectura y genera recomendaciones de reubicación bajo custodia asimétrica ("Hogar + Vista"). |
| **`maintainer-summary-view.md`** | **Maintainer UI / Markdown** | Plantilla de presentación para el maintainer humano (`Alan-TheGentleman`, `rafael`). Separa hechos e inferencias, resalta alertas de incertidumbre en el borde P1/P2 y ofrece botones/checkboxes de acción (`Accept`, `Override`, `Relocate`, `Defer`). |

---

## Flujo de Ejecución Canónico

```
                      ┌────────────────────────────────────┐
                      │        Issue nuevo o backlog       │
                      └─────────────────┬──────────────────┘
                                        │
                         Paso 1: ¿Resuelve db/rules.py?
                         (feat, docs, panic, silent loss)
                                        │
                        ┌───────────────┴───────────────┐
                       SÍ                               NO
                        │                               │
             ┌──────────┴──────────┐         ┌──────────┴──────────┐
             │ CLASIFICACIÓN       │         │ Pass 1: A-Priori    │
             │ DETERMINISTA (P0-P3)│         │ LLM Analysis        │
             │ (5ms, 0 tokens)     │         │ (pass-1-issue.md)   │
             └──────────┬──────────┘         └──────────┬──────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                         Paso 2: ¿Hay cruce de sistemas?
                                        │
                        ┌───────────────┴───────────────┐
                       SÍ                               NO
                        │                               │
             ┌──────────┴──────────┐                    │
             │ Pass 2: Cross-System│                    │
             │ Correlation         │                    │
             │ (pass-2-cross.md)   │                    │
             └──────────┬──────────┘                    │
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                         Paso 3: Renderizado para Maintainer
                         (maintainer-summary-view.md)
                                        │
                        ┌───────────────┴───────────────┐
                        │ Decisión Humana (Alan/Rafael) │
                        │ (schemas/maintainer-decision) │
                        └───────────────────────────────┘
```
