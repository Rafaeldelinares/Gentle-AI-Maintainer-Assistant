#!/usr/bin/env python3
"""
precision_report.py — Mide el acierto del motor usando SOLO etiquetas humanas.

Hasta ahora el proyecto podía afirmar *cobertura* (cuántos issues toca cada regla) pero
ninguna cifra de acierto. Esto cierra esa mitad.

Lee el log del tablero (`db/board.db`): los veredictos que una persona escribió.
Nunca escribe nada, ni en la base ni en GitHub.

    python3 tools/precision_report.py            # informe a stdout
    python3 tools/precision_report.py --write     # además escribe report-precision.md

Si no hay etiquetas humanas todavía, lo dice y sale con 0: no inventa un número.
Con pocos casos, el intervalo de confianza (Wilson 95%) muestra que la cifra no
significa nada — que es justamente el punto.
"""

import argparse
import json
import math
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "board"))

DB = ROOT / "db" / "board.db"

# Qué banda implica cada regla determinista, para comparar contra el veredicto humano.
RULE_BAND = {
    "rule:candidato_p0_requiere_revision_humana": "P0",
    "rule:hard_crash": "P1",
    "rule:crash_with_workaround_demoted_to_p2": "P2",
    "rule:feature_request": "P2",
    "rule:docs_chore_question": "P3",
}
SERIOUS = {"P0", "P1"}
MIN_MEANINGFUL_N = 10


def wilson(k, n, z=1.96):
    """Intervalo de confianza de Wilson al 95% para una proporción. Honesto con n chico."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (centre - margin) / d), min(1.0, (centre + margin) / d))


def load_labelled(db_path):
    """Etiquetas humanas + la banda que el motor había sugerido para esas mismas refs."""
    tmp = Path(tempfile.mkdtemp()) / "board-copy.db"
    shutil.copy2(db_path, tmp)
    conn = sqlite3.connect(str(tmp))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT h.ref, h.verdict, h.actor, h.ts,
               c.slug, c.number, c.title, c.band, c.rule, c.review_flag
        FROM human_labels h
        JOIN cards c ON c.ref = h.ref
        ORDER BY c.slug, c.number
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def analyse(rows):
    total = len(rows)
    no_validas = [r for r in rows if r["verdict"] == "no_valida"]
    validas = [r for r in rows if r["verdict"] != "no_valida"]

    # Falsos negativos graves: la persona dijo P0/P1 y el motor había dicho otra cosa.
    falsos_negativos = []
    for r in validas:
        motor = RULE_BAND.get(r["rule"]) or ("zona gris" if not r["band"] else r["band"])
        if r["verdict"] in SERIOUS and motor not in SERIOUS:
            falsos_negativos.append({**r, "motor": motor})

    # Precisión por regla: de lo que la regla marcó, cuánto confirmó la persona.
    por_regla = defaultdict(lambda: {"n": 0, "aciertos": 0, "desacuerdos": Counter()})
    for r in validas:
        if not r["rule"]:
            continue
        esperado = RULE_BAND.get(r["rule"])
        if esperado is None:
            continue
        entry = por_regla[r["rule"]]
        entry["n"] += 1
        if r["verdict"] == esperado:
            entry["aciertos"] += 1
        else:
            entry["desacuerdos"][r["verdict"]] += 1

    # Matriz motor -> humano
    matriz = defaultdict(Counter)
    for r in validas:
        motor = RULE_BAND.get(r["rule"]) or ("zona gris" if not r["band"] else r["band"])
        matriz[motor][r["verdict"]] += 1

    return {
        "total": total,
        "no_validas": no_validas,
        "validas": validas,
        "falsos_negativos": falsos_negativos,
        "por_regla": dict(por_regla),
        "matriz": {k: dict(v) for k, v in matriz.items()},
    }


def render(results):
    out = []
    a = out.append
    a("## Resultado")
    a("")
    a(f"- Etiquetas humanas cargadas: **{results['total']}**")
    a(f"- Marcadas «no válida» (excluidas de la precisión): {len(results['no_validas'])}")
    a(f"- Válidas para medir: **{len(results['validas'])}**")
    a("")

    if not results["validas"]:
        a("**No disponible.** Todavía no hay etiquetas humanas válidas. Este informe se completa")
        a("cuando alguien etiquete issues en el tablero. No se inventa un número.")
        return "\n".join(out)

    a("## Falsos negativos de P0/P1 — el error más caro")
    a("")
    a("Casos donde **una persona marcó P0 o P1** y el motor había dicho otra cosa.")
    a("Son los que importan: un grave que se escapó. Un falso positivo cuesta tiempo; esto cuesta más.")
    a("")
    if not results["falsos_negativos"]:
        a("**Ninguno** entre las etiquetas cargadas. No significa que no existan: significa que")
        a(f"no aparecieron en los {len(results['validas'])} casos etiquetados.")
    else:
        a(f"**{len(results['falsos_negativos'])} casos:**")
        a("")
        a("| Issue | El motor dijo | Veredicto humano | Regla | Título |")
        a("| --- | --- | --- | --- | --- |")
        for r in results["falsos_negativos"]:
            a(f"| `{r['ref']}` | {r['motor']} | **{r['verdict']}** | `{r['rule'] or '—'}` | {r['title'][:60]} |")
    a("")

    a("## Precisión por regla (con su intervalo honesto)")
    a("")
    a("| Regla | Banda esperada | n | Aciertos | Precisión | IC 95% (Wilson) |")
    a("| --- | --- | --- | --- | --- | --- |")
    for rule, e in sorted(results["por_regla"].items(), key=lambda kv: -kv[1]["n"]):
        k, n = e["aciertos"], e["n"]
        lo, hi = wilson(k, n)
        pct = f"{100 * k / n:.0f}%" if n else "n/a"
        warn = "" if n >= MIN_MEANINGFUL_N else " ⚠"
        a(f"| `{rule}` | {RULE_BAND.get(rule)} | {n} | {k} | {pct}{warn} | {100 * lo:.0f}% – {100 * hi:.0f}% |")
    a("")
    a(f"⚠ = menos de {MIN_MEANINGFUL_N} casos. **Con n chico el intervalo es enorme y la precisión no dice nada**:")
    a("«100% sobre 3 casos» es compatible con un 40% real. Por eso se reporta el intervalo y no sólo el porcentaje.")
    a("")

    a("## Matriz motor → humano")
    a("")
    bandas = ["P0", "P1", "P2", "P3", "zona gris"]
    presentes = [b for b in bandas if b in results["matriz"]]
    a("| El motor dijo ↓ / humano dijo → | " + " | ".join(presentes) + " |")
    a("| --- | " + " | ".join("---" for _ in presentes) + " |")
    for motor in presentes:
        fila = [str(results["matriz"].get(motor, {}).get(h, 0)) for h in presentes]
        a(f"| **{motor}** | " + " | ".join(fila) + " |")
    a("")

    a("## Desacuerdos por regla (qué dijo la persona en lugar de lo esperado)")
    a("")
    for rule, e in sorted(results["por_regla"].items(), key=lambda kv: -kv[1]["n"]):
        if e["desacuerdos"]:
            detalle = ", ".join(f"{k}×{v}" for k, v in e["desacuerdos"].most_common())
            a(f"- `{rule}`: {detalle}")
    a("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="escribe report-precision.md en la raíz")
    parser.add_argument("--db", default=str(DB))
    args = parser.parse_args()

    path = Path(args.db)
    if not path.exists():
        print("No hay tablero todavía (db/board.db). Etiquetá issues primero.")
        return 0

    rows = load_labelled(path)
    results = analyse(rows)

    print("════════════════════════════════════════════════════════════════════")
    print(" PRECISIÓN DEL MOTOR (medida SOLO con etiquetas humanas)")
    print("════════════════════════════════════════════════════════════════════")
    if not rows:
        print("  Etiquetas humanas: 0")
        print("  ** No disponible. ** Sin etiquetas humanas no hay nada que medir:")
        print("     este informe no inventa un número.")
        print("════════════════════════════════════════════════════════════════════")
        return 0
    print(f"  etiquetas: {results['total']} | válidas: {len(results['validas'])} | no válidas: {len(results['no_validas'])}")
    print(f"  falsos negativos de P0/P1: {len(results['falsos_negativos'])}")
    for rule, e in sorted(results["por_regla"].items(), key=lambda kv: -kv[1]["n"]):
        lo, hi = wilson(e["aciertos"], e["n"])
        print(f"    {rule:46s} n={e['n']:4d} precisión={100*e['aciertos']/e['n']:5.0f}%  IC95%={100*lo:.0f}-{100*hi:.0f}%")
    print("════════════════════════════════════════════════════════════════════")

    if args.write:
        out = ROOT / "report-precision.md"
        out.write_text(
            "# Motor precision (measured from human labels only)\n\n"
            "> Generated by `python3 tools/precision_report.py --write`. Read-only on the board.\n"
            "> Every figure here comes from human verdicts written in the board; nothing is hand-written.\n\n"
            + render(results) + "\n",
            encoding="utf-8",
        )
        print(f"  informe escrito: {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
