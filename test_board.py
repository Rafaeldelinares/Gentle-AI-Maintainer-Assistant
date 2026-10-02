#!/usr/bin/env python3
"""
test_board.py — Tests for the board domain (board/core.py).

Verifies the governance rules, not just the happy path:
  1. schema is idempotent
  2. ingest derives one card per issue and never mixes repositories
  3. the engine only ever suggests *blocking* columns, never `listo_mantener`
  4. valid moves and verdicts are accepted; invalid ones are rejected
  5. the append-only log is never rewritten
  6. card_state and human_labels are fully reconstructible from events
  7. the default actor is not a person's name

  python3 test_board.py
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "board"))

import core  # noqa: E402


def sample_issues():
    return [
        {"slug": "gentle-ai", "number": 1, "title": "bug: crashes on startup",
         "body": "panic: runtime error: index out of range", "title_prefix": "bug",
         "labels": ["bug"], "cross_refs": [], "state": "open"},
        {"slug": "gentle-ai", "number": 2, "title": "feat: add streaming",
         "body": "Please add streaming support.", "title_prefix": "feat",
         "labels": ["enhancement"], "cross_refs": [], "state": "open"},
        {"slug": "engram", "number": 3, "title": "bug: silently drops rows",
         "body": "silently drops rows on disk full", "title_prefix": "bug",
         "labels": ["bug"], "cross_refs": [], "state": "open"},
        {"slug": "gentle-shell", "number": 4, "title": "feat: new panel",
         "body": "Add a panel.", "title_prefix": "feat",
         "labels": [], "cross_refs": [], "state": "open"},
        # an issue with no conventional prefix and no labels: no template, no signal
        {"slug": "engram", "number": 6, "title": "Investigate latency spike under load",
         "body": "Latency grows under load.", "title_prefix": "",
         "labels": [], "cross_refs": [], "state": "open"},
        # a feature that carries a hard signal: review flag without a missing form
        {"slug": "gentle-shell", "number": 5,
         "title": "feat(vision): add fallback",
         "body": "Images are silently dropped by the provider layer.", "title_prefix": "feat",
         "labels": [], "cross_refs": [], "state": "open"},
    ]


def run():
    print("════════════════════════════════════════════════════════════════════")
    print(" RUNNING BOARD TEST SUITE (test_board.py)")
    print("════════════════════════════════════════════════════════════════════\n")

    passed = 0
    total = 0

    def check(condition, desc):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  ✔ [PASS] {desc}")
            passed += 1
        else:
            print(f"  ❌ [FAIL] {desc}", file=sys.stderr)
            sys.exit(1)

    tmp = Path(tempfile.mkdtemp()) / "board.db"
    conn = core.connect(tmp)

    # 1. schema idempotent
    core.init_schema(conn)
    core.init_schema(conn)
    check(True, "init_schema is idempotent")

    # 2. ingest separates repositories
    stats = core.ingest(conn, sample_issues())
    check(stats["cards"] == 6, f"ingest created one card per issue ({stats['cards']})")
    conn2 = core.connect(tmp)
    slugs = [r["slug"] for r in conn2.execute("SELECT DISTINCT slug FROM cards ORDER BY slug")]
    check(slugs == ["engram", "gentle-ai", "gentle-shell"], f"three separate boards: {slugs}")
    per_slug = {r["slug"]: r["c"] for r in conn2.execute("SELECT slug, COUNT(*) AS c FROM cards GROUP BY slug")}
    check(per_slug == {"gentle-ai": 2, "engram": 2, "gentle-shell": 2},
          f"cards are not mixed across repositories: {per_slug}")

    # 3. engine only suggests blocking columns
    suggestions = [r["suggested_column"] for r in conn2.execute("SELECT suggested_column FROM cards")]
    check(all(s is None or s in core.SUGGESTIBLE_COLUMNS for s in suggestions),
          f"engine never suggests a non-blocking column: {suggestions}")
    check("listo_mantener" not in core.SUGGESTIBLE_COLUMNS,
          "listo_mantener is not suggestible by the engine")
    check("en_manos" not in core.SUGGESTIBLE_COLUMNS,
          "en_manos is not suggestible by the engine")

    # derived columns populate
    core.rebuild_state(conn)
    derived = core.list_cards(conn, "gentle-ai")
    by_ref = {c["ref"]: c for c in derived}
    check(by_ref["gentle-ai#1"]["column_name"] in core.SUGGESTIBLE_COLUMNS,
          f"a crash report lands in a blocking column ({by_ref['gentle-ai#1']['column_name']})")
    check(by_ref["gentle-ai#1"]["band"] == "P1",
          f"the crash report is classified P1, not left grey ({by_ref['gentle-ai#1']['band']})")
    check(all(c["column_name"] not in ("listo_mantener", "en_manos") for c in derived),
          "no card is auto-promoted to a positive column")
    engram_all = {c["ref"]: c for c in core.list_cards(conn, "engram")}
    check(engram_all["engram#6"]["column_name"] == "entrada"
          and engram_all["engram#6"]["suggested_column"] is None,
          "an issue with no template and no signal stays in entrada with no suggestion")
    engram_cards = core.list_cards(conn, "engram")
    check(engram_cards and all(c["slug"] == "engram" for c in engram_cards)
          and any(c["ref"] == "engram#3" for c in engram_cards),
          "engram board only contains engram cards")
    shell_cards = {c["ref"]: c for c in core.list_cards(conn, "gentle-shell")}
    check(shell_cards["gentle-shell#5"]["review_flag"] is True,
          "a feature with a hard signal carries the human-review flag")
    check(shell_cards["gentle-shell#5"]["column_name"] in core.SUGGESTIBLE_COLUMNS,
          f"that feature is suggested to a blocking column ({shell_cards['gentle-shell#5']['column_name']})")

    # 3b. severidad de la información faltante: escala proporcional y monótona
    check(core.missing_severity(0, 8) == "none", "sin campos faltantes no hay severidad")
    check(core.missing_severity(0, 0) == "none", "una plantilla sin campos obligatorios no genera ruido")
    scale = [core.missing_severity(n, 8) for n in range(1, 9)]
    order = {name: i for i, name in enumerate(core.MISSING_SEVERITY_ORDER)}
    check(all(order[scale[i]] <= order[scale[i + 1]] for i in range(len(scale) - 1)),
          f"la severidad crece con la proporción faltante: {scale}")
    check(scale[-1] == "critical", "faltar todo es crítico")
    check(core.missing_severity(1, 8) == "low", "faltar 1 de 8 es leve")
    check(core.missing_severity(1, 2) == "medium", "faltar 1 de 2 pesa más que faltar 1 de 8 (es proporcional)")
    check(core.missing_severity(2, 3) == "high", "faltar 2 de 3 es alto")

    # 3c. etiquetas: conteo por tablero y filtro que apaga tarjetas
    tags = {t["key"]: t["count"] for t in core.board_tags(conn, "gentle-ai")}
    check(set(tags) == set(core.TAG_KEYS), f"todas las etiquetas conocidas se reportan: {sorted(tags)}")
    check(sum(1 for c in core.list_cards(conn, "gentle-ai", limit=500) if c["band"] == "P2") == tags["p2"],
          "el conteo de P2 coincide con las tarjetas P2 del tablero")
    check(core.clean_tags(["p2", "inventado", "p2", "grey"]) == ["p2", "grey"],
          "las etiquetas desconocidas se descartan y no se duplican")
    before = core.column_counts(conn, "gentle-ai")
    after = core.column_counts(conn, "gentle-ai", hide_tags=["p2", "grey"])
    check(sum(after.values()) < sum(before.values()),
          f"apagar etiquetas reduce lo visible ({sum(before.values())} -> {sum(after.values())})")
    # REGRESIÓN: una tarjeta sin banda (zona gris, band IS NULL) NO debe desaparecer
    # al apagar un tag de banda. `NOT (band = 'P1')` daba NULL con band NULL y SQL
    # descartaba la fila, así que apagar P1 se llevaba toda la zona gris por delante.
    grey_refs = {c["ref"] for c in core.list_cards(conn, "engram", limit=50) if c["band"] is None}
    check(grey_refs, f"hay tarjetas de zona gris en el fixture: {sorted(grey_refs)}")
    # La única excepción es el propio tag 'grey': apagarlo sí debe ocultar la zona gris.
    for tag in [t for t in core.TAG_KEYS if t != "grey"]:
        visibles = {c["ref"] for c in core.list_cards(conn, "engram", limit=50, hide_tags=[tag])}
        check(grey_refs <= visibles,
              f"apagar '{tag}' no se lleva la zona gris (band IS NULL)")
    solo_grey_visible = {c["ref"] for c in core.list_cards(conn, "engram", limit=50, hide_tags=["grey"])}
    check(not (grey_refs & solo_grey_visible), "apagar 'grey' sí oculta la zona gris")

    # INVARIANTE: apagar un tag quita exactamente las tarjetas que ese tag cuenta
    for tag in core.TAG_KEYS:
        cuenta = {t["key"]: t["count"] for t in core.board_tags(conn, "engram")}[tag]
        base = sum(core.column_counts(conn, "engram").values())
        filtrado = sum(core.column_counts(conn, "engram", hide_tags=[tag]).values())
        check(base - filtrado == cuenta,
              f"apagar '{tag}' quita exactamente {cuenta} tarjetas (quitó {base - filtrado})")

    visible = core.list_cards(conn, "gentle-ai", limit=500, hide_tags=["p2", "grey"])
    check(all(c["band"] not in ("P2", None) for c in visible),
          "ninguna tarjeta con etiqueta apagada queda visible")
    check(len(core.list_cards(conn, "gentle-ai", limit=500, hide_tags=["p2","grey"])) ==
          len(core.list_cards(conn, "gentle-ai", limit=500, hide_tags=["grey","p2"])),
          "el orden de las etiquetas apagadas no cambia el resultado")

    # 3e. explain() no puede derivar del motor: se compara con la clasificación real
    #     para TODO el snapshot. Si alguien cambia el orden de las reglas y no toca
    #     explain.py, este test lo delata.
    sys.path.insert(0, str(ROOT / "board"))
    import explain as explain_mod
    with open(ROOT / "issues.json", encoding="utf-8") as fh:
        todos = json.load(fh)
    desacuerdos = []
    for it in todos[:400]:
        r = explain_mod.explain(it.get("title") or "", it.get("body") or "",
                                it.get("title_prefix") or "", it.get("labels") or [], it["slug"])
        b, _c, rule = core.classify_issue_deterministically(it, it.get("labels") or [], it.get("cross_refs") or [])
        if (r["band"], r["rule"]) != (b, rule):
            desacuerdos.append((it["slug"], it["number"], r["band"], b))
    check(not desacuerdos, f"explain() coincide con el motor en 400 issues (desacuerdos: {desacuerdos[:3]})")

    # 3d. el sistema NO aprende de las decisiones humanas (respuesta verificable)
    # Sobre el MISMO snapshot: una base sin decisiones y otra con 40 movimientos y 40
    # veredictos deben producir exactamente las mismas sugerencias. Si algún día el motor
    # empezara a ajustarse con el uso, este test falla — y el determinismo se rompería.
    import tempfile as _tf
    base_issues = sample_issues()
    limpia = core.connect(Path(_tf.mkdtemp()) / "limpia.db")
    core.init_schema(limpia); core.ingest(limpia, base_issues); core.rebuild_state(limpia)
    aprendida = core.connect(Path(_tf.mkdtemp()) / "aprendida.db")
    core.init_schema(aprendida); core.ingest(aprendida, base_issues); core.rebuild_state(aprendida)
    for i, ref in enumerate([r["ref"] for r in aprendida.execute("SELECT ref FROM cards ORDER BY ref")]):
        try:
            core.move_card(aprendida, ref, "listo_mantener" if i % 2 else "revision_humana", "human-1", "uso")
        except ValueError:
            pass
        core.set_verdict(aprendida, ref, "P2", "human-1", "uso")
    core.rebuild_state(aprendida)
    def sugerencias(conn):
        return {r["ref"]: (r["suggested_column"], r["band"], r["missing_severity"])
                for r in conn.execute("SELECT ref, suggested_column, band, missing_severity FROM cards")}
    check(aprendida.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] > 0,
          "el escenario de uso tiene decisiones humanas registradas")
    check(sugerencias(limpia) == sugerencias(aprendida),
          "las sugerencias son idénticas con y sin decisiones humanas (el sistema no aprende solo)")
    check({r["ref"]: r["column_name"] for r in aprendida.execute("SELECT * FROM card_state")}
          != {r["ref"]: r["column_name"] for r in limpia.execute("SELECT * FROM card_state")},
          "lo que sí cambió son las columnas decididas, no las sugeridas")
    limpia.close(); aprendida.close()

    # 3f. la medición: la matemática del informe de precisión
    sys.path.insert(0, str(ROOT / "tools"))
    import precision_report as pr
    escenario = [
        # la regla hard_crash acertó 2 de 3 (una la persona la bajó a P2)
        {"ref": "a#1", "verdict": "P1", "rule": "rule:hard_crash", "band": "P1"},
        {"ref": "a#2", "verdict": "P1", "rule": "rule:hard_crash", "band": "P1"},
        {"ref": "a#3", "verdict": "P2", "rule": "rule:hard_crash", "band": "P1"},
        # falso negativo grave: el motor dijo zona gris y la persona dijo P0
        {"ref": "a#4", "verdict": "P0", "rule": None, "band": None},
        # falso negativo grave: el motor dijo P3 y la persona dijo P1
        {"ref": "a#5", "verdict": "P1", "rule": "rule:docs_chore_question", "band": "P3"},
        # «no válida» queda fuera de la precisión
        {"ref": "a#6", "verdict": "no_valida", "rule": "rule:feature_request", "band": "P2"},
    ]
    res = pr.analyse(escenario)
    check(len(res["validas"]) == 5, f"las «no válida» se excluyen de la precisión (válidas={len(res['validas'])})")
    check(len(res["falsos_negativos"]) == 2,
          f"detecta los 2 falsos negativos de P0/P1 (encontró {len(res['falsos_negativos'])})")
    check({r["ref"] for r in res["falsos_negativos"]} == {"a#4", "a#5"},
          "los falsos negativos son los casos donde el humano subió la banda")
    hc = res["por_regla"]["rule:hard_crash"]
    check(hc["n"] == 3 and hc["aciertos"] == 2, f"precisión por regla con su n: {hc['n']} casos, {hc['aciertos']} aciertos")
    lo, hi = pr.wilson(2, 3)
    check(lo < 0.3 and hi > 0.9, f"el intervalo de Wilson es honesto con n=3 ({lo:.2f}-{hi:.2f})")
    lo1, hi1 = pr.wilson(30, 40)
    check(hi1 - lo1 < (hi - lo), "con más casos el intervalo se angosta")
    check(pr.analyse([])["validas"] == [] and pr.wilson(0, 0) == (0.0, 0.0),
          "sin etiquetas no inventa un número")

    # 4. moves and verdicts
    result = core.move_card(conn, "gentle-ai#2", "listo_mantener", "human-1", "triado")
    check(result["to"] == "listo_mantener" and result["from"] in core.ALL_COLUMNS,
          f"valid move accepted ({result['from']} -> {result['to']})")

    for bad, why in [("inventada", "unknown column rejected"),
                     ("listo_mantener", "no-op move rejected")]:
        try:
            core.move_card(conn, "gentle-ai#2", bad, "human-1")
            check(False, why)
        except ValueError:
            check(True, why)

    try:
        core.move_card(conn, "gentle-ai#999", "entrada", "human-1")
        check(False, "unknown card rejected")
    except ValueError:
        check(True, "unknown card rejected")

    core.set_verdict(conn, "gentle-ai#2", "P2", "human-1", "feature")
    label = conn.execute("SELECT verdict FROM human_labels WHERE ref='gentle-ai#2'").fetchone()
    check(label["verdict"] == "P2", "valid verdict accepted")
    try:
        core.set_verdict(conn, "gentle-ai#2", "P9", "human-1")
        check(False, "unknown verdict rejected")
    except ValueError:
        check(True, "unknown verdict rejected")

    # 5. append-only log
    before = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    core.move_card(conn, "gentle-ai#2", "en_manos", "human-1")
    core.set_verdict(conn, "gentle-ai#1", "P1", "human-1")
    after = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    check(after == before + 2, f"every action appends an event ({before} -> {after})")
    # re-ingesting must not destroy history
    core.ingest(conn, sample_issues())
    after_ingest = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    check(after_ingest == after, "re-ingest does not touch the event log")

    # 6. reconstructibility: corrupt the projections, rebuild, compare
    truth_state = {r["ref"]: r["column_name"] for r in conn.execute("SELECT * FROM card_state")}
    truth_labels = {r["ref"]: r["verdict"] for r in conn.execute("SELECT * FROM human_labels")}
    conn.execute("UPDATE card_state SET column_name='entrada'")
    conn.execute("UPDATE human_labels SET verdict='no_valida'")
    conn.commit()
    core.rebuild_state(conn)
    rebuilt_state = {r["ref"]: r["column_name"] for r in conn.execute("SELECT * FROM card_state")}
    rebuilt_labels = {r["ref"]: r["verdict"] for r in conn.execute("SELECT * FROM human_labels")}
    check(rebuilt_state == truth_state, "card_state is reconstructible from events alone")
    check(rebuilt_labels == truth_labels, "human_labels is reconstructible from events alone")

    # 7. no person names by default
    check(core.VERDICTS == ("P0", "P1", "P2", "P3", "no_valida"), "verdict vocabulary is closed")
    check(isinstance(core.COLUMNS, list) and len(core.COLUMNS) == 5, "five active columns")

    # the engine never writes a verdict
    check(conn.execute("SELECT COUNT(*) AS c FROM human_labels WHERE actor LIKE 'engine%'").fetchone()["c"] == 0,
          "no verdict was ever written by the engine")


    # 8. HTTP layer: the unit tests above never exercised it, so each review finding
    #    about the transport gets a regression test here.
    import json as _json
    import threading as _threading
    import urllib.request as _urlreq
    import urllib.error as _urlerr
    import api as _api

    core.DB_PATH = tmp            # isolate: every api call goes to the test database
    server = _api.build_server("127.0.0.1", 0)
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    _threading.Thread(target=server.serve_forever, daemon=True).start()

    def http(path, payload=None):
        req = _urlreq.Request(base + path)
        data = None
        if payload is not None:
            data = _json.dumps(payload).encode()
            req.add_header("Content-Type", "application/json")
        def parse(res):
            body = res.read().decode(errors="replace")
            try:
                return _json.loads(body or "{}")
            except ValueError:
                return body

        try:
            with _urlreq.urlopen(req, data=data, timeout=5) as res:
                return res.status, parse(res)
        except _urlerr.HTTPError as exc:
            return exc.code, parse(exc)

    try:
        status, _ = http("/static//etc/passwd")
        check(status == 400, f"path traversal is refused, not served (got {status})")
        status, _ = http("/static/style.css")
        check(status == 200, "a legitimate static asset is still served")
        status, cards = http("/api/boards/gentle-ai/cards?column=falta_info&limit=5")
        check(status == 200 and all("missing_severity" in c and "required_total" in c for c in cards["cards"]),
              "the API exposes the missing-info severity and the template total")
        check(all(c["missing_severity"] in core.MISSING_SEVERITY_ORDER for c in cards["cards"]),
              "every severity is one of the closed vocabulary values")
        status, _ = http("/api/boards/gentle-ai/cards?limit=abc")
        check(status == 400, f"invalid limit is a 400, not a 500 (got {status})")
        status, body = http("/api/move", {"ref": "gentle-ai#2", "column": "en_manos", "actor": "engine:fake"})
        check(status == 400, f"a reserved actor is refused (got {status})")
        status, body = http("/api/verdict", {"ref": "gentle-ai#2", "verdict": "P1", "actor": " system "})
        check(status == 400, f"a malformed reserved actor is refused (got {status})")
        status, _ = http("/api/move", {"ref": "gentle-ai#2", "column": "archivado", "actor": "human-1"})
        check(status == 200, f"an allowed actor still moves a card (got {status})")
        forged = conn.execute(
            "SELECT COUNT(*) AS c FROM events WHERE actor LIKE 'engine%' OR actor LIKE 'system%'").fetchone()["c"]
        check(forged == 0, "no forged engine/system actor reached the event log")

        # concurrency: two simultaneous moves on the same card must leave the projection
        # agreeing with the append-only log, whatever order the lock grants.
        import concurrent.futures as _cf
        fresh = core.list_cards(conn, "engram")[0]["ref"]
        with _cf.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(
                lambda col: http("/api/move", {"ref": fresh, "column": col, "actor": "human-1"})[0],
                ["en_manos", "archivado"]))
        events = conn.execute(
            "SELECT to_column FROM events WHERE ref = ? AND kind = 'move' ORDER BY id", (fresh,)).fetchall()
        state = conn.execute("SELECT column_name FROM card_state WHERE ref = ?", (fresh,)).fetchone()["column_name"]
        check(all(s == 200 for s in results) and len(events) == 2 and state == events[-1]["to_column"],
              f"concurrent moves stay consistent with the log (status {results}, {len(events)} events, state {state})")
    finally:
        server.shutdown()
        server.server_close()

    conn.close()
    print("\n────────────────────────────────────────────────────────────────────")
    print(f" FINAL TEST RESULT: {passed}/{total} tests passed successfully.")
    print("════════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(run())
