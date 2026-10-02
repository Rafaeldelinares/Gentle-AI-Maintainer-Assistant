/* Gentle AI board — vanilla JS, no build, no external assets.
   The UI is intentionally "dumb": it renders what the API returns and posts human
   actions. All rules (valid columns, valid verdicts) live in board/core.py. */

const state = {
  boards: [],
  hiddenTags: [],   // etiquetas apagadas: sus tarjetas no se muestran
  slug: null,
  cards: {},        // column -> [cards]
  counts: {},
  verdicts: {},
  query: "",
  showArchive: false,
  actor: "human-1",
};

const VERDICT_LABELS = {
  P0: "P0", P1: "P1", P2: "P2", P3: "P3", no_valida: "no válida",
};

// Nombres legibles para las reglas del motor: el nombre crudo queda en el tooltip.
const RULE_LABELS = {
  "rule:feature_request": "pedido de funcionalidad",
  "rule:docs_chore_question": "docs / tarea",
  "rule:hard_crash": "crash duro",
  "rule:candidato_p0_requiere_revision_humana": "candidato P0",
  "rule:crash_with_workaround_demoted_to_p2": "crash con workaround",
};

const MISSING_TITLES = {
  low: "Poco: faltan pocos campos obligatorios",
  medium: "Medio: falta alrededor de un tercio de los campos obligatorios",
  high: "Alto: falta más de la mitad de los campos obligatorios",
  critical: "Crítico: falta casi toda la información que el formulario pide",
};

const BAND_TITLES = {
  p0: "candidato P0: el texto describe pérdida silenciosa de datos o corrupción. Es un candidato, lo confirma una persona.",
  p1: "P1: crash duro sin workaround ni recuperación al reintentar.",
  p2: "P2: degrada, o hay workaround, o se recupera al reintentar, o es un pedido de funcionalidad.",
  p3: "P3: documentación, pregunta, tarea de mantenimiento o cosmético.",
  grey: "zona gris: el motor no pudo clasificarlo de forma determinista. Sin clasificar todavía, no 'sin importancia'.",
};

const $ = (sel) => document.querySelector(sel);

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.hidden = true; }, 2600);
}

function bandClass(band) {
  if (!band) return "";
  if (band.indexOf("candidato P0") === 0) return "band-p0";
  return "band-" + band.toLowerCase();
}

function esc(text) {
  return (text || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// ------------------------------------------------------------------ rendering

function renderFilterState() {
  const el = $("#filterState");
  const board = state.boards.find((x) => x.slug === state.slug);
  if (!el || !board) return;
  const visible = Object.entries(state.counts || {})
    .filter(([k]) => k !== "archivado")
    .reduce((acc, [, v]) => acc + v, 0);
  const apagadas = state.hiddenTags.length;
  el.innerHTML = apagadas
    ? `mostrando <b>${visible}</b> de ${board.total} · ${apagadas} etiqueta${apagadas > 1 ? "s" : ""} apagada${apagadas > 1 ? "s" : ""}`
    : `mostrando <b>${board.total}</b> de ${board.total} · todas las etiquetas prendidas`;
}

function renderMeta() {
  const b = state.boards.find((x) => x.slug === state.slug);
  if (!b) return;
  const s = b.snapshot;
  $("#meta").textContent =
    `${state.slug} · ${b.total} tarjetas abiertas · snapshot ${s.sha256} · ${s.mtime}`;
}

async function runSimulation() {
  const title = $("#simTitle").value.trim();
  const out = $("#simResult");
  if (!title) { out.innerHTML = `<p class="sim-blocked">Hace falta un título.</p>`; return; }
  out.innerHTML = `<p class="muted">calculando…</p>`;
  try {
    const { explanation: x } = await api("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        body: $("#simBody").value,
        title_prefix: $("#simPrefix").value.trim(),
        labels: $("#simLabels").value.trim(),
        slug: $("#simSlug").value,
      }),
    });
    const band = x.band || "zona gris";
    const cls = !x.band ? "" : (x.band.indexOf("candidato P0") === 0 ? "danger" : (x.band === "P1" ? "warn" : ""));
    const falta = x.missing_fields.length
      ? `<span class="badge miss-${esc(x.missing_severity)}">falta info ×${x.missing_fields.length}/${x.required_total}</span>`
      : "";
    const steps = x.checks.map((c) => `
      <div class="sim-step ${c.won ? "won" : (c.matched ? "" : "off")}">
        <span class="mark">${c.won ? "▶" : (c.matched ? "·" : "✗")}</span>
        <span><strong>${esc(c.name)}</strong>${c.question ? " — " + esc(c.question) : ""}
          ${c.detail ? `<br><span class="muted">${esc(c.detail)}</span>` : ""}
          ${c.blocked_by && c.blocked_by.length ? `<br><span class="sim-blocked">cancelado por: ${c.blocked_by.map((b) => esc(b.match)).join(", ")}</span>` : ""}
          ${c.note ? `<br><span class="muted">${esc(c.note)}</span>` : ""}
        </span>
      </div>`).join("");
    out.innerHTML = `
      <div class="sim-verdict">
        <span class="badge ${cls}">${esc(band)}</span>
        <code>${esc(x.rule || "—")}</code>
        ${x.review_flag ? `<span class="badge warn">⚠ mirada humana</span>` : ""}
        ${falta}
        <span class="muted">columna sugerida: <code>${esc(x.suggested_column || "ninguna")}</code></span>
        <span class="muted">prefijo detectado: <code>${esc(x.derived_prefix || "(ninguno)")}</code></span>
      </div>
      <p class="muted">Decidió: <strong>${esc(x.decided_by)}</strong>. ${esc(x.human_note)}</p>
      <div class="sim-chain">${steps}</div>`;
  } catch (err) {
    out.innerHTML = `<p class="sim-blocked">no se pudo calcular: ${esc(err.message)}</p>`;
  }
}

async function fillDeterminismPanel() {
  try {
    const health = await api("/api/health");
    const boards = await api("/api/boards");
    const ha = health.human_activity || {};
    $("#detSnapshot").textContent = `${health.snapshot.sha256} · ${health.snapshot.issues} issues · ${health.snapshot.mtime}`;
    $("#detEvents").textContent = String(ha.events ?? 0);
    $("#detBreakdown").textContent =
      `${ha.moves ?? 0} movimientos · ${ha.verdicts ?? 0} veredictos · ` +
      `${boards.boards.reduce((acc, b) => acc + b.total, 0)} tarjetas abiertas en ${boards.boards.length} tableros`;
  } catch (err) {
    $("#detSnapshot").textContent = "no disponible: " + err.message;
  }
}

function renderTagBar() {
  const board = state.boards.find((x) => x.slug === state.slug);
  const bar = $("#tagbar");
  if (!board) { bar.innerHTML = ""; return; }
  const tags = board.tags || [];
  bar.innerHTML = tags.map((t) => {
    const off = state.hiddenTags.includes(t.key);
    const cls = "tag-chip" + (off ? " off" : "") + (t.count === 0 ? " void" : "") + " tag-" + t.key;
    return `<button class="${cls}" data-tag="${esc(t.key)}" title="${off ? "Apagada: sus tarjetas no se muestran" : "Prendida: sus tarjetas se muestran"}">${esc(t.label)} <span class="n">(${t.count})</span></button>`;
  }).join("");
  bar.querySelectorAll(".tag-chip").forEach((btn) => {
    btn.onclick = () => {
      const key = btn.dataset.tag;
      state.hiddenTags = state.hiddenTags.includes(key)
        ? state.hiddenTags.filter((k) => k !== key)
        : state.hiddenTags.concat([key]);
      renderTagBar();
      reload();
    };
  });
}

function renderBoards() {
  const nav = $("#boards");
  nav.innerHTML = "";
  state.boards.forEach((b) => {
    const btn = document.createElement("button");
    btn.className = "board-tab" + (b.slug === state.slug ? " active" : "");
    btn.innerHTML = `${esc(b.slug)}<span class="n">${b.total}</span>`;
    btn.onclick = () => selectBoard(b.slug);
    nav.appendChild(btn);
  });
}

function cardElement(card) {
  const el = document.createElement("article");
  el.className = `card ${bandClass(card.band)}` + (card.suggested_column ? " suggested" : "");
  el.draggable = true;
  el.dataset.ref = card.ref;

  const badges = [];
  if (card.band) {
    const isP0 = card.band.indexOf("candidato P0") === 0;
    const cls = isP0 ? "danger" : (card.band === "P1" ? "warn" : "");
    const key = isP0 ? "p0" : card.band.toLowerCase();
    badges.push(`<span class="badge ${cls}" title="${esc(BAND_TITLES[key] || card.band)}">${esc(isP0 ? "candidato P0" : card.band)}</span>`);
  }
  if (card.review_flag) {
    badges.push(`<span class="badge warn" title="Hay una señal dura (pérdida de datos o crash) pero el título tiene un prefijo no-bug. El motor NO sube la banda: te pide que lo mires.">⚠ mirada humana</span>`);
  }
  if (card.missing_fields && card.missing_fields.length) {
    const detail = card.missing_fields.map(esc).join(", ");
    const total = card.required_total || card.missing_fields.length;
    const pct = Math.round((100 * card.missing_fields.length) / total);
    const sev = card.missing_severity || "low";
    const title = `${MISSING_TITLES[sev] || ""}. Falta ${card.missing_fields.length} de ${total} campos obligatorios del formulario (${pct}%): ${detail}`;
    badges.push(`<span class="badge miss-${esc(sev)}" title="${title}">falta info ×${card.missing_fields.length}/${total}</span>`);
  }
  if (card.human_verdict) {
    badges.push(`<span class="badge verdict" title="Veredicto humano guardado. Esta es la etiqueta que vale para medir precisión.">veredicto ${esc(VERDICT_LABELS[card.human_verdict] || card.human_verdict)}</span>`);
  }
  if (card.suggested_column && card.column_name === "entrada") {
    badges.push(`<span class="badge" title="El motor sugiere moverla, pero no la movió: espera tu confirmación.">sugerido: ${esc(card.suggested_column.replace("_", " "))}</span>`);
  }

  const ruleLabel = card.rule ? (RULE_LABELS[card.rule] || card.rule) : "zona gris";
  const ruleTitle = card.rule ? `Regla determinista: ${card.rule}` : BAND_TITLES.grey;

  el.innerHTML = `
    <div class="card-ref"><span>${esc(card.ref)}</span><span title="${esc(ruleTitle)}">${esc(ruleLabel)}</span></div>
    <p class="card-title">${esc(card.title.slice(0, 150))}</p>
    <div class="badges">${badges.join("")}</div>`;

  el.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", card.ref);
    el.classList.add("dragging");
  });
  el.addEventListener("dragend", () => el.classList.remove("dragging"));
  el.addEventListener("click", () => openCard(card.ref));
  return el;
}

function renderBoard() {
  const board = $("#board");
  board.innerHTML = "";
  const b = state.boards.find((x) => x.slug === state.slug);
  if (!b) return;

  b.columns.forEach((col) => {
    if (col.key === "archivado" && !state.showArchive) return;
    const column = document.createElement("section");
    column.className = "column";
    column.dataset.column = col.key;

    const cards = state.cards[col.key] || [];
    column.innerHTML = `
      <div class="column-head">
        <h3>${esc(col.label)}</h3>
        <span class="count">${col.count}</span>
      </div>
      <div class="column-body"></div>`;

    const body = column.querySelector(".column-body");
    cards.forEach((card) => body.appendChild(cardElement(card)));
    if (!cards.length) body.innerHTML = `<p class="empty-col">sin tarjetas en esta columna</p>`;
    if (col.count > cards.length) {
      const more = document.createElement("button");
      more.className = "more";
      more.textContent = `cargar más (${col.count - cards.length} restantes)`;
      more.onclick = () => loadCards(col.key, cards.length);
      body.appendChild(more);
    }

    column.addEventListener("dragover", (e) => { e.preventDefault(); column.classList.add("drop-target"); });
    column.addEventListener("dragleave", () => column.classList.remove("drop-target"));
    column.addEventListener("drop", async (e) => {
      e.preventDefault();
      column.classList.remove("drop-target");
      const ref = e.dataTransfer.getData("text/plain");
      if (!ref) return;
      try {
        await api("/api/move", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ref, column: col.key, actor: state.actor }),
        });
        toast(`${ref} → ${col.label}`);
        await reload();
      } catch (err) { toast("no se pudo mover: " + err.message); }
    });

    board.appendChild(column);
  });
}

// --------------------------------------------------------------------- loading

async function loadCards(column, offset = 0) {
  const params = new URLSearchParams({ column, limit: "60", offset: String(offset) });
  if (state.query) params.set("q", state.query);
  if (state.hiddenTags.length) params.set("hide", state.hiddenTags.join(","));
  const data = await api(`/api/boards/${state.slug}/cards?${params}`);
  if (offset === 0) state.cards[column] = [];
  state.cards[column] = state.cards[column].concat(data.cards);
  state.counts = data.counts;

  const board = state.boards.find((x) => x.slug === state.slug);
  if (board) {
    board.columns.forEach((c) => { c.count = data.counts[c.key] || 0; });
    if (data.tags) board.tags = data.tags;
  }
  renderBoard();
  renderMeta();
  renderFilterState();
}

async function reload() {
  state.cards = {};
  const board = state.boards.find((x) => x.slug === state.slug);
  for (const col of board.columns) {
    if (col.key === "archivado" && !state.showArchive) continue;
    await loadCards(col.key, 0);
  }
}

async function selectBoard(slug) {
  state.slug = slug;
  state.hiddenTags = [];
  const boards = await api("/api/boards");
  state.boards = boards.boards;
  state.actor = boards.actor;
  renderBoards();
  renderTagBar();
  await reload();
}

// ---------------------------------------------------------------- card drawer

async function openCard(ref) {
  const { card } = await api(`/api/card?ref=${encodeURIComponent(ref)}`);
  const drawer = $("#drawer");
  $("#drawer-ref").textContent = card.ref;
  $("#drawer-link").href = `https://github.com/Gentleman-Programming/${card.slug}/issues/${card.number}`;

  const events = card.events.map((e) => {
    if (e.kind === "move") return `<div>${e.ts} · mover ${esc(e.from_column || "?")} → <strong>${esc(e.to_column)}</strong> · ${esc(e.actor)}</div>`;
    const v = JSON.parse(e.payload || "{}").verdict;
    return `<div>${e.ts} · veredicto <strong>${esc(VERDICT_LABELS[v] || v)}</strong> · ${esc(e.actor)}${e.note ? " · " + esc(e.note) : ""}</div>`;
  }).join("") || "<div>sin eventos todavía</div>";

  const buttons = Object.keys(VERDICT_LABELS).map((v) =>
    `<button class="verdict-btn ${card.human_verdict === v ? "active" : ""}" data-verdict="${v}">${VERDICT_LABELS[v]}</button>`).join("");

  $("#drawer-body").innerHTML = `
    <p class="hint">Así se usa: <strong>elegí un veredicto</strong> con los botones de abajo, escribí una nota si querés,
    y cada acción queda en el registro. Para mover la tarjeta de columna, <strong>arrastrala</strong> en el tablero.
    Nada de esto toca GitHub.</p>
    <h4>Título</h4><div class="kv">${esc(card.title)}</div>
    <h4>Señales del motor (derivadas, no decisiones)</h4>
    <div class="kv">banda sugerida: <code>${esc(card.band || "—")}</code> <span class="muted">(el motor sugiere; vos decidís)</span></div>
    <div class="kv">regla aplicada: <code>${esc(card.rule || "zona gris (sin clasificar)")}</code></div>
    <div class="kv">mirada humana: <code>${card.review_flag ? "sí" : "no"}</code>${card.review_reason ? " · " + esc(card.review_reason) : ""}</div>
    <div class="kv">columna sugerida: <code>${esc(card.suggested_column || "ninguna")}</code></div>
    <div class="kv">columna actual: <code>${esc(card.column_name)}</code> desde ${esc(card.since)}</div>
    <h4>Campos que faltan (Módulo A)</h4>
    <div class="kv">${card.missing_fields.length ? card.missing_fields.map(esc).join(", ") : "ninguno"}</div>
    <h4>Veredicto humano</h4>
    <div class="kv">Lo escribís vos. La herramienta nunca lo completa sola, y es la etiqueta que vale para medir precisión.</div>
    <div class="verdict-row">${buttons}</div>
    <div class="note-row">
      <input id="note" placeholder="nota (opcional): por qué decidiste esto" value="${esc(card.human_note || "")}" />
      <button class="btn" id="save-note">guardar nota</button>
    </div>
    <h4>Registro append-only</h4>
    <div class="events">${events}</div>`;

  drawer.querySelectorAll(".verdict-btn").forEach((btn) => {
    btn.onclick = async () => {
      try {
        await api("/api/verdict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ref: card.ref, verdict: btn.dataset.verdict, actor: state.actor, note: $("#note").value }),
        });
        toast(`veredicto ${VERDICT_LABELS[btn.dataset.verdict]} guardado para ${card.ref}`);
        await openCard(card.ref);
        await reload();
      } catch (err) { toast("no se pudo guardar: " + err.message); }
    };
  });
  $("#save-note").onclick = () => {
    if (card.human_verdict) {
      api("/api/verdict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ref: card.ref, verdict: card.human_verdict, actor: state.actor, note: $("#note").value }),
      }).then(() => { toast("nota guardada"); openCard(card.ref); });
    } else {
      toast("elegí primero un veredicto");
    }
  };

  drawer.hidden = false;
}

// ------------------------------------------------------------------- bootstrap

function bindControls() {
  const toggle = (sel, show) => { $(sel).hidden = !show; };
  const toggleGuide = (show) => toggle("#guidePanel", show);
  $("#guide").onclick = () => toggleGuide(true);
  $("#guide2").onclick = () => toggleGuide(true);
  $("#guideClose").onclick = () => toggleGuide(false);
  $("#determinism").onclick = async () => { toggle("#detPanel", true); await fillDeterminismPanel(); };
  $("#detClose").onclick = () => toggle("#detPanel", false);
  $("#simulate").onclick = () => toggle("#simPanel", true);
  $("#simClose").onclick = () => toggle("#simPanel", false);
  $("#simRun").onclick = runSimulation;
  $("#simTitle").addEventListener("keydown", (e) => { if (e.key === "Enter") runSimulation(); });
  $("#guidePanel").addEventListener("click", (e) => { if (e.target.id === "guidePanel") toggleGuide(false); });
  $("#detPanel").addEventListener("click", (e) => { if (e.target.id === "detPanel") toggle("#detPanel", false); });
  $("#simPanel").addEventListener("click", (e) => { if (e.target.id === "simPanel") toggle("#simPanel", false); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { toggleGuide(false); toggle("#detPanel", false); toggle("#simPanel", false); $("#drawer").hidden = true; }
  });
  $("#drawer-close").onclick = () => { $("#drawer").hidden = true; };
  $("#showArchive").onchange = (e) => { state.showArchive = e.target.checked; reload(); };
  let t;
  $("#search").oninput = (e) => {
    clearTimeout(t);
    t = setTimeout(() => { state.query = e.target.value.trim(); reload(); }, 250);
  };
  $("#refresh").onclick = async () => {
    try {
      const res = await api("/api/ingest", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      toast(`señales recalculadas: ${res.ingested.cards} tarjetas`);
      await selectBoard(state.slug);
    } catch (err) { toast("no se pudo recalcular: " + err.message); }
  };
}

async function boot() {
  bindControls();

  // El logo es un asset de marca servido por GitHub. Si no hay red, mostramos un
  // monograma local en vez de un hueco roto. La herramienta no descarga nada: es el
  // navegador quien lo pide, y sólo para pintarlo.
  const logo = $("#brandLogo");
  const fallback = $("#brandFallback");
  const showFallback = () => { logo.hidden = true; fallback.hidden = false; };
  if (logo.complete && logo.naturalWidth === 0) showFallback();
  logo.addEventListener("error", showFallback);
  const boards = await api("/api/boards");
  state.boards = boards.boards;
  state.actor = boards.actor;
  if (state.boards.length) await selectBoard(state.boards[0].slug);
}

boot().catch((err) => { $("#meta").textContent = "error: " + err.message; });
