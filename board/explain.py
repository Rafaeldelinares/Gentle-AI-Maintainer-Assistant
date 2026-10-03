#!/usr/bin/env python3
"""
explain.py — Why did the engine classify this issue the way it did?

Read-only. It consumes the engine's structured decision port (decide()), so it cannot
drift from the real classification: if this says "P0 because of X", the engine fired on
the same X.

Serves two purposes:
  - the board's rule simulator, so a maintainer can paste a phrase and see which rule
    fires and with what evidence, without touching anything;
  - a review aid for changing a rule: you can see exactly which spans the current rule
    matches before proposing a narrower one.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "modules"))

from rules import decide  # noqa: E402
import core  # noqa: E402


def explain(title, body="", title_prefix="", labels=None, slug="gentle-ai"):
    """
    Returns the full, honest explanation of one classification.

    The `checks` list is ordered exactly as the engine evaluates, so the first check
    marked `matched` is the one that decided the band.
    """
    labels = list(labels or [])
    row = {
        "slug": slug, "number": 0, "title": title, "body": body,
        "title_prefix": title_prefix,
    }
    decision = decide(row, labels, cross_refs=[], include_evidence=True)

    card = core.derive_card({
        "slug": slug, "number": 0, "title": title, "body": body,
        "title_prefix": title_prefix, "labels": labels, "cross_refs": [], "state": "open",
    })

    prefix = decision["evidence"]["derived_prefix"]
    is_bug = decision["evidence"]["is_bug"]

    notes = {
        "candidato P0": "Una negación («no data loss») o la descripción de un arreglo cancelan el disparo.",
        "P1 crash sin salida": "Un deadlock solo cuenta con contexto de proceso o hilo. «not a crash» y «crash-safe» lo cancelan.",
        "P2 crash con workaround (regla H9)": "Si existe salida, el crash baja a P2. «no configuration can work around it» NO cuenta como workaround: queda P1.",
        "P3 prefijo explícito de docs/tarea": "El prefijo explícito del título GANA sobre una etiqueta que lo contradiga.",
        "P2 prefijo explícito de feature": "",
        "P2 etiqueta de feature": "",
        "P3 etiqueta o encabezado de docs": "Última regla: si nada anterior coincidió.",
    }

    checks = [{
        "name": "compuerta de bug",
        "question": "¿es un bug? (prefijo bug:/fix: o etiqueta de bug)",
        "matched": is_bug,
        "won": False,
        "detail": decision["evidence"]["details"]["compuerta de bug"],
        "note": "No decide una banda: habilita o bloquea P0/P1. Un feat: con señal dura no sube: se marca «mirada humana».",
    }]

    for r in decision["rules_considered"]:
        name = r["name"]
        checks.append({
            "name": name,
            "question": "",
            "matched": r["matched"],
            "won": r["won"],
            "detail": decision["evidence"]["details"].get(name, ""),
            "blocked_by": decision["evidence"]["blocked_by"].get(name, []),
            "note": notes.get(name, ""),
        })

    return {
        "input": {"title": title, "title_prefix": title_prefix, "labels": labels, "slug": slug},
        "derived_prefix": prefix,
        "is_bug": is_bug,
        "band": card["band"],
        "rule": card["rule"],
        "suggested_column": card["suggested_column"],
        "review_flag": bool(card["review_flag"]),
        "review_reason": card["review_reason"],
        "missing_fields": card["missing_fields"],
        "required_total": card["required_total"],
        "missing_severity": card["missing_severity"],
        "decided_by": decision["decided_by"],
        "checks": checks,
        "human_note": (
            "Esto es lo que el motor decidió, no lo que es cierto. El veredicto lo escribe una persona."
        ),
    }
