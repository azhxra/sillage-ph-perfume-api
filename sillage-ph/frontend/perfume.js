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
        <div class="cta-row">
          <a class="btn" href="${safe(safeShopURL(p.where_to_buy.url))}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a>
          <a class="btn secondary" href="compare.html?a=${p.id}">Compare this perfume</a>
        </div>
      </div>
    </section>

    <section class="panel" aria-label="Perfume details">
      <dl>
          <dt>Perfume</dt><dd>${safe(p.name)}</dd>
          <dt>Brand</dt><dd>${safe(p.brand)}</dd>
          <dt>Scent family</dt><dd>${safe(p.scent_family)}</dd>
          <dt>Key notes</dt><dd>${p.key_notes.map(safe).join(", ")}</dd>
          <dt>Affordable dupe</dt><dd>${p.dupes.map(safe).join(" / ")}</dd>
          <dt>Dupe price</dt><dd>${safe(p.dupe_price_php || "Price unavailable")}</dd>
          <dt>Where to buy in PH</dt><dd>${safe(p.where_to_buy.store)}</dd>
          <dt>Gender</dt><dd>${safe(p.gender)}</dd>
          <dt>Year launched</dt><dd>${safe(p.year_launched)}</dd>
          <dt>Concentration</dt><dd>${safe(p.concentration)}</dd>
          <dt>Best season</dt><dd>${safe(p.best_season)}</dd>
          <dt>Best occasion</dt><dd>${safe(p.best_occasion)}</dd>
          <dt>Dupe bottle size</dt><dd>${safe(p.dupe_size)}</dd>
          <dt>Vibe</dt><dd>${safe(p.vibe)}</dd>
      </dl>
      ${otherStores ? `<dl>${otherStores}</dl>` : ""}
      <p class="stock-note">${safe(p.where_to_buy.note)}</p>
    </section>`;
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
