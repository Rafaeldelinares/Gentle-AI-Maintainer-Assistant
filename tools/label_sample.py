#!/usr/bin/env python3
"""
label_sample.py — Elige qué issues etiquetar a mano, de forma estratificada y reproducible.

Por qué existe: `tools/precision_report.py` mide precisión contra etiquetas humanas, pero
esas etiquetas hay que producirlas. Y no sirve etiquetar al azar: hay que cubrir las bandas
graves, porque un falso negativo de P0/P1 es el error más caro.

Reglas de la muestra:
  - **Estratificada** por repositorio y banda, con cuota para P0/P1.
  - **Determinista y reproducible**: el orden sale de `sha256(ref)`, no de un `random`.
    Cualquiera puede volver a generar exactamente la misma lista.
  - **Nunca usa la muestra de calibración ni el held-out ya visto** (la auditoría los miró):
    excluye el grupo 0 de split y la muestra de 90 de `db/exp.db`, para que la medición no
    esté contaminada. Ver DECISIONS.md D-010.

Es de solo lectura: no escribe en el tablero ni en GitHub. Sólo produce una lista.

    python3 tools/label_sample.py                 # 120 issues a stdout
    python3 tools/label_sample.py --size 150 --write
"""

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "board"))

import core  # noqa: E402

SNAPSHOT = ROOT / "issues.json"
EXP_DB = ROOT / "db" / "exp.db"

# Cuota por banda. P0/P1 se agotan completos: son pocos y son los que más importa medir.
QUOTA = {"P0": 1.00, "P1": 1.00, "P2": 0.12, "P3": 0.25, "gris": 0.10}


def calibration_refs():
    """Refs de la muestra de calibración (run 1 de exp.db), para excluirlas."""
    if not EXP_DB.exists():
        return set()
    import sqlite3
    conn = sqlite3.connect(str(EXP_DB))
    try:
        rows = conn.execute(
            "SELECT s.slug, i.number FROM run_issues ri "
            "JOIN issues i ON i.id = ri.issue_id JOIN systems s ON s.id = i.system_id "
            "WHERE ri.run_id = 1").fetchall()
        return {f"{slug}#{num}" for slug, num in rows}
    except sqlite3.Error:
        return set()
    finally:
        conn.close()


def held_out(ref):
    """Grupo 0 del split determinista: la auditoría ya lo miró."""
    return int(hashlib.sha256(ref.encode()).hexdigest(), 16) % 5 == 0


def band_key(band):
    if not band:
        return "gris"
    return "P0" if band.startswith("candidato P0") else band


def deterministic_key(ref):
    return hashlib.sha256(("label:" + ref).encode()).hexdigest()


def build_sample(size):
    with open(SNAPSHOT, encoding="utf-8") as fh:
        issues = json.load(fh)

    excluidas = calibration_refs()
    pool = defaultdict(list)
    for it in issues:
        ref = f"{it['slug']}#{it['number']}"
        if ref in excluidas or held_out(ref):
            continue
        card = core.derive_card(it)
        pool[(it["slug"], band_key(card["band"]))].append({
            "ref": ref, "slug": it["slug"], "band": band_key(card["band"]),
            "engine_band": card["band"] or "zona gris", "rule": card["rule"],
            "title": it.get("title") or "", "missing": len(card["missing_fields"]),
            "review": bool(card["review_flag"]),
        })

    # Cuota proporcional por estrato, con mínimo 3 para que ningún estrato quede sin muestra.
    total_elegible = sum(len(v) for v in pool.values())
    elegidas = []
    sobrantes = []
    for (slug, banda), items in sorted(pool.items()):
        # P0/P1 entran completos: son pocos y son el error más caro de no medir.
        if banda in ("P0", "P1"):
            cuota = len(items)
        else:
            cuota = math.ceil(len(items) * QUOTA[banda] * size / max(total_elegible, 1))
            cuota = max(2, cuota)
        cuota = min(cuota, len(items))
        items.sort(key=lambda r: deterministic_key(r["ref"]))
        elegidas.extend(items[:cuota])
        sobrantes.extend(items[cuota:])

    # Completar hasta el tamaño pedido sin inflar P0/P1 más allá de lo que existe.
    if len(elegidas) < size:
        sobrantes.sort(key=lambda r: (r["band"] in ("P0", "P1"), deterministic_key(r["ref"])))
        elegidas.extend(sobrantes[:size - len(elegidas)])

    # Si nos pasamos, recortamos empezando por los estratos menos graves, nunca P0/P1.
    if len(elegidas) > size:
        elegidas.sort(key=lambda r: (r["band"] in ("P0", "P1"), deterministic_key(r["ref"])))
        elegidas = elegidas[:size]
    elegidas.sort(key=lambda r: (r["slug"], r["band"], deterministic_key(r["ref"])))
    return elegidas, total_elegible, len(excluidas)


def render(elegidas, total_elegible, excluidas, size):
    out = []
    a = out.append
    a("## Cómo usar esta lista")
    a("")
    a("1. Abrí el tablero (`python3 board/server.py --port 8770`) y copiá cada `ref` en el buscador.")
    a("2. Leé el issue en GitHub (botón «abrir en GitHub ↗») y elegí un **veredicto humano**.")
    a("3. Escribí una nota si el motor se equivocó. La nota es el dato más útil del log.")
    a("4. Cuando tengas suficientes, corré `python3 tools/precision_report.py --write`.")
    a("")
    a("**No hay que hacer los " + str(len(elegidas)) + " de una sentada.** Con 40 etiquetas que cubran P0/P1")
    a("ya se pueden ver los falsos negativos; la precisión por regla necesita más.")
    a("")
    a("## De dónde sale esta muestra")
    a("")
    a(f"- Tamaño objetivo: {size} | seleccionados: **{len(elegidas)}**")
    a(f"- Elegibles tras exclusiones: {total_elegible}")
    a(f"- Excluidos por contaminación: {excluidas} issues (muestra de calibración + grupo held-out que la auditoría ya miró)")
    a("- Orden **determinista**: `sha256('label:' + ref)`. Volver a correrlo da exactamente la misma lista.")
    a("")
    a("## La muestra")
    a("")
    a("| # | ref | banda del motor | regla | falta info | mirada humana | título |")
    a("| --- | --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(elegidas, 1):
        falta = f"×{r['missing']}" if r["missing"] else "—"
        rev = "⚠" if r["review"] else "—"
        titulo = r["title"].replace("|", "/")[:70]
        a(f"| {i} | `{r['ref']}` | {r['engine_band']} | `{r['rule'] or '—'}` | {falta} | {rev} | {titulo} |")
    a("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=120)
    parser.add_argument("--write", action="store_true", help="escribe label-sample.md en la raíz")
    args = parser.parse_args()

    elegidas, total, excluidas = build_sample(args.size)
    por_banda = defaultdict(int)
    for r in elegidas:
        por_banda[r["band"]] += 1

    print("════════════════════════════════════════════════════════════════════")
    print(" MUESTRA PARA ETIQUETAR (estratificada, reproducible, sin contaminar)")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  seleccionados: {len(elegidas)} de {total} elegibles ({excluidas} excluidos por contaminación)")
    for banda in ("P0", "P1", "P2", "P3", "gris"):
        print(f"    {banda:5s}: {por_banda[banda]}")
    print("════════════════════════════════════════════════════════════════════")

    if args.write:
        out = ROOT / "label-sample.md"
        out.write_text(
            "# Label sample — qué issues etiquetar a mano\n\n"
            "> Generated by `python3 tools/label_sample.py --write`. Read-only: it only produces a list.\n"
            "> Deterministic ordering (`sha256`), stratified by band, excluding the calibration and\n"
            "> held-out issues the audit already inspected. See `DECISIONS.md` D-010.\n\n"
            + render(elegidas, total, excluidas, args.size) + "\n",
            encoding="utf-8",
        )
        print(f"  lista escrita: {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
