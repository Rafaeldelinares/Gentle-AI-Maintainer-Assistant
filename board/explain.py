#!/usr/bin/env python3
"""
explain.py — Why did the engine classify this issue the way it did?

Read-only. It reuses the engine's own functions and regexes, so it cannot drift from the
real classification: if this says "P0 because of X", the engine fired on the same X.

Serves two purposes:
  - the board's rule simulator, so a maintainer can paste a phrase and see which rule
    fires and with what evidence, without touching anything;
  - a review aid for changing a rule: you can see exactly which spans the current rule
    matches before proposing a narrower one.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "modules"))

from rules import (  # noqa: E402
    RE_P0_SILENT_BASE, RE_DATA_LOSS_NEGATION, RE_FIX_DESCRIPTION, RE_SILENT_NEGATION,
    RE_P1_CRASH_CORE, RE_DEADLOCK_BASE, RE_DEADLOCK_NEGATION, RE_CONCURRENCY_CONTEXT,
    RE_CRASH_HANDLED, RE_WORKAROUND_POSITIVE, RE_WORKAROUND_NEGATIVE,
    RE_P3_DOCS, derive_title_prefix, has_silent_data_loss, is_hard_crash,
    has_active_workaround, EXPLICIT_DOCS_PREFIXES, EXPLICIT_FEATURE_PREFIXES,
    P0_CANDIDATE_LABEL, RULE_P0_CANDIDATE,
)

import core  # noqa: E402


def _spans(pattern, text, limit=3):
    """Matched snippets with a little context, for showing the evidence."""
    out = []
    for m in pattern.finditer(text or ""):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        out.append({
            "match": m.group(0),
            "context": re.sub(r"\s+", " ", text[start:end]).strip(),
        })
        if len(out) >= limit:
            break
    return out


def explain(title, body="", title_prefix="", labels=None, slug="gentle-ai"):
    """
    Returns the full, honest explanation of one classification.

    The `checks` list is ordered exactly as the engine evaluates, so the first check
    marked `matched` is the one that decided the band.
    """
    labels = list(labels or [])
    text = f"{title}\n{body}"
    prefix = derive_title_prefix(title, title_prefix)
    label_set = {l.lower() for l in labels}
    is_bug = prefix in ("bug", "fix") or "type:bug" in label_set or "bug" in label_set

    p0_matches = _spans(RE_P0_SILENT_BASE, text)
    p0_negations = _spans(RE_DATA_LOSS_NEGATION, text) + _spans(RE_SILENT_NEGATION, text)
    p0_fix_desc = _spans(RE_FIX_DESCRIPTION, text)
    crash_matches = _spans(RE_P1_CRASH_CORE, text)
    crash_handled = _spans(RE_CRASH_HANDLED, text)
    deadlocks = _spans(RE_DEADLOCK_BASE, text)
    deadlock_neg = _spans(RE_DEADLOCK_NEGATION, text)
    concurrency = _spans(RE_CONCURRENCY_CONTEXT, text)
    workaround_pos = _spans(RE_WORKAROUND_POSITIVE, text)
    workaround_neg = _spans(RE_WORKAROUND_NEGATIVE, text)

    p0_fires = has_silent_data_loss(text)
    crash_fires = is_hard_crash(text)
    workaround = has_active_workaround(text)
    feature_predicate = (prefix in EXPLICIT_FEATURE_PREFIXES
                         or bool(label_set & {"type:feature", "enhancement", "feature"}))
    docs_predicate = (prefix in EXPLICIT_DOCS_PREFIXES
                      or bool(label_set & {"type:chore", "documentation", "question", "discussion"})
                      or bool(RE_P3_DOCS.search(title or "")))

    card = core.derive_card({
        "slug": slug, "number": 0, "title": title, "body": body,
        "title_prefix": title_prefix, "labels": labels, "cross_refs": [], "state": "open",
    })

    # La cadena se evalua en el MISMO orden que classify_issue_deterministically.
    # Si el orden cambia alla, este test de coherencia lo detecta (hay un test que
    # compara el resultado de explain() contra el del motor para todo el snapshot).
    chain = [
        ("candidato P0",                        is_bug and p0_fires),
        ("P1 crash sin salida",                 is_bug and crash_fires and not workaround),
        ("P2 crash con workaround (regla H9)",  is_bug and crash_fires and workaround),
        ("P3 prefijo explícito de docs/tarea",  prefix in EXPLICIT_DOCS_PREFIXES or prefix in ("refactor", "test", "ci", "style")),
        ("P2 prefijo explícito de feature",     prefix in EXPLICIT_FEATURE_PREFIXES),
        ("P2 etiqueta de feature",              bool(label_set & {"type:feature", "enhancement", "feature"})),
        ("P3 etiqueta o encabezado de docs",    docs_predicate),
    ]
    winner = next((name for name, ok in chain if ok), None)

    detail = {
        "candidato P0": f"coincidencias={[s['match'] for s in p0_matches] or 'ninguna'}",
        "P1 crash sin salida": f"crash={[s['match'] for s in crash_matches] or 'ninguno'} deadlock={[s['match'] for s in deadlocks] or 'ninguno'}",
        "P2 crash con workaround (regla H9)": f"workaround={[s['match'] for s in workaround_pos] or 'ninguno'}",
        "P3 prefijo explícito de docs/tarea": f"prefijo='{prefix or '(ninguno)'}'",
        "P2 prefijo explícito de feature": f"prefijo='{prefix or '(ninguno)'}'",
        "P2 etiqueta de feature": f"etiquetas={labels or '[]'}",
        "P3 etiqueta o encabezado de docs": f"etiquetas={labels or '[]'} prefijo='{prefix or '(ninguno)'}'",
    }
    blocked = {
        "candidato P0": p0_negations + p0_fix_desc,
        "P1 crash sin salida": crash_handled + deadlock_neg,
        "P2 crash con workaround (regla H9)": workaround_neg,
    }
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
        "detail": f"prefijo='{prefix or '(ninguno)'}' etiquetas={labels or '[]'}",
        "note": "No decide una banda: habilita o bloquea P0/P1. Un feat: con señal dura no sube: se marca «mirada humana».",
    }]
    for name, ok in chain:
        checks.append({
            "name": name,
            "question": "",
            "matched": ok,
            "won": ok and name == winner,
            "detail": detail.get(name, ""),
            "blocked_by": blocked.get(name, []),
            "note": notes.get(name, ""),
        })

    decided = winner if winner else "(ninguna regla: zona gris)"

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
        "decided_by": decided,
        "checks": checks,
        "human_note": (
            "Esto es lo que el motor decidió, no lo que es cierto. El veredicto lo escribe una persona."
        ),
    }
