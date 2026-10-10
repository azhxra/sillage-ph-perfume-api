/* ==========================================================================
   Sillage PH — perfume.html (all 14 details of one perfume)
   Reads ?id=7 from the address, then calls GET /perfumes/{id}.
   ========================================================================== */

/* ---------- 1. API SETUP (address comes from config.js) ---------- */
const API_URL = (window.SILLAGE_API_URL || "").replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);
const page = document.getElementById("detail");

const COLORS = {
  Amber: ["#faf0e9", "#d9b48f"], Floral: ["#f8edf2", "#d8afc2"], Fruity: ["#faf2ed", "#e3bdab"],
  Fresh: ["#eff4f2", "#b1c9c0"], Woody: ["#f2efeb", "#bea88a"], Gourmand: ["#f5e9ec", "#b7798a"],
  Leather: ["#f1eae7", "#b5927a"],
};

/* ---------- 2. HELPERS ---------- */
const safe = text => String(text).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);

function safeShopURL(value) {
  try { const url = new URL(value); return url.protocol === "https:" ? url.href : "#"; }
  catch { return "#"; }
}

// One "label / value" pair of the detail lists
const row = (number, label, value) => `<dt>${number} · ${label}</dt><dd>${value}</dd>`;

/* ---------- 3. DRAW THE PAGE ---------- */
function showPerfume(p) {
  const [tile, juice] = COLORS[p.scent_family] || COLORS.Floral;
  const number = String(p.id).padStart(2, "0");
  document.title = `Sillage PH — ${p.name}`;

  const otherStores = p.other_stores.length
    ? `<dt>Also available at</dt><dd><ul class="other-stores">${p.other_stores.map(s =>
        `<li><a href="${safe(safeShopURL(s.url))}" target="_blank" rel="noopener noreferrer">${safe(s.store)} — ${safe(s.dupe)} ↗</a></li>`).join("")}</ul></dd>`
    : "";

  page.innerHTML = `
    <a class="back-link" href="index.html#collection">← Back to the collection</a>

    <section class="detail-hero" style="--tile:${tile};--juice:${juice}">
      <div class="detail-art" aria-hidden="true">
        <div class="mini-bottle"><div class="mini-cap"></div><div class="mini-glass"><div class="mini-label">sillage<small>SCENT ${number}</small></div></div></div>
      </div>
      <div>
        <p class="brand">${safe(p.brand)}</p>
        <h1>${safe(p.name)}</h1>
        <p class="vibe">${safe(p.vibe)}</p>
        <div class="cta-row">
          <a class="btn" href="${safe(safeShopURL(p.where_to_buy.url))}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a>
          <a class="btn secondary" href="compare.html?a=${p.id}">Compare this perfume</a>
        </div>
      </div>
    </section>

    <div class="detail-panels">
      <section class="panel" aria-labelledby="first-seven">
        <h2 id="first-seven">The essentials</h2>
        <p class="sub">Details 01 – 07</p>
        <dl>
          ${row("01", "Perfume", safe(p.name))}
          ${row("02", "Brand", safe(p.brand))}
          ${row("03", "Scent family", safe(p.scent_family))}
          ${row("04", "Key notes", p.key_notes.map(safe).join(", "))}
          ${row("05", "Affordable dupe", p.dupes.map(safe).join(" / "))}
          ${row("06", "Dupe price", safe(p.dupe_price_php))}
          ${row("07", "Where to buy in PH", safe(p.where_to_buy.store))}
        </dl>
      </section>

      <section class="panel" aria-labelledby="last-seven">
        <h2 id="last-seven">Know it better</h2>
        <p class="sub">Details 08 – 14</p>
        <dl>
          ${row("08", "Gender", safe(p.gender))}
          ${row("09", "Year launched", safe(p.year_launched))}
          ${row("10", "Concentration", safe(p.concentration))}
          ${row("11", "Best season", safe(p.best_season))}
          ${row("12", "Best occasion", safe(p.best_occasion))}
          ${row("13", "Dupe bottle size", safe(p.dupe_size))}
          ${row("14", "Vibe", safe(p.vibe))}
          ${otherStores}
        </dl>
        <p class="stock-note">${safe(p.where_to_buy.note)}</p>
      </section>
    </div>`;
}

/* ---------- 4. LOAD ---------- */
async function loadPerfume() {
  const id = new URLSearchParams(location.search).get("id");
  if (!/^\d+$/.test(id || "")) {
    page.innerHTML = `<div class="empty-state"><h3>Pick a perfume first.</h3><p><a href="index.html#collection">Browse the collection</a> and click a bottle.</p></div>`;
    return;
  }
  try {
    const res = await fetch(`${API_URL}/perfumes/${id}`);
    if (res.status === 404) {
      page.innerHTML = `<div class="empty-state"><h3>We couldn’t find that perfume.</h3><p><a href="index.html#collection">Back to the collection</a></p></div>`;
      return;
    }
    if (!res.ok) throw new Error("Request failed");
    showPerfume(await res.json());
  } catch {
    page.textContent = "We couldn't load this perfume. Please refresh and try again.";
  }
}

loadPerfume();
