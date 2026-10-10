/* ==========================================================================
   Sillage PH — index.html (the collection)
   Sections: 1 API setup · 2 Helpers · 3 Loading data · 4 Drawing cards
             5 Filters & events
   ========================================================================== */

/* ---------- 1. API SETUP ----------
   The API address comes from config.js (empty = same site), so no URL is typed here.
   Endpoints used on this page:
     GET /perfumes              -> every perfume
     GET /perfumes/search?q=    -> text search
     GET /perfumes/{id}         -> one perfume (the "7 details" drawer)          */
const API_URL = (window.SILLAGE_API_URL || "").replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);

const list = document.getElementById("perfumeList");
const count = document.getElementById("resultCount");
const input = document.getElementById("searchInput");
const brandSelect = document.getElementById("brandFilter");

// Page state
let currentPerfumes = [];   // result of the latest load / search
let gender = "All";         // All | Men | Women | Unisex
let brand = "All";          // All | a brand name
let totalPerfumes = 0;      // size of the full collection
let searchController;       // lets a new search cancel the previous one
let requestNumber = 0;      // ignores out-of-date responses

// Order of the scent-family sections when everything is shown
const FAMILY_ORDER = ["Floral", "Fruity", "Fresh", "Woody", "Amber", "Gourmand", "Leather"];
// Card colours per scent family: [tile background, bottle liquid]
const COLORS = {
  Amber: ["#faf0e9", "#d9b48f"], Floral: ["#f8edf2", "#d8afc2"], Fruity: ["#faf2ed", "#e3bdab"],
  Fresh: ["#eff4f2", "#b1c9c0"], Woody: ["#f2efeb", "#bea88a"], Gourmand: ["#f5e9ec", "#b7798a"],
  Leather: ["#f1eae7", "#b5927a"],
};

/* ---------- 2. HELPERS ---------- */
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

// Only allow https links for the shop button
function safeShopURL(value) {
  try { const url = new URL(value); return url.protocol === "https:" ? url.href : "#"; }
  catch { return "#"; }
}

async function fetchJSON(path, signal) {
  const response = await fetch(`${API_URL}${path}`, { signal });
  if (!response.ok) throw new Error(`API returned HTTP ${response.status}`);
  return response.json();
}

function stateMessage(title, message) {
  list.innerHTML = `<div class="empty-state"><h3>${escapeHTML(title)}</h3><p>${escapeHTML(message)}</p></div>`;
}

/* ---------- 3. LOADING DATA ---------- */
async function loadPerfumes(query = "") {
  searchController?.abort();
  searchController = new AbortController();
  const number = ++requestNumber;

  list.setAttribute("aria-busy", "true");
  count.textContent = "Finding your scents…";
  stateMessage("A little luxury is on its way…", "Loading the perfume collection.");

  try {
    const path = query ? `/perfumes/search?q=${encodeURIComponent(query)}` : "/perfumes";
    const data = await fetchJSON(path, searchController.signal);
    if (number !== requestNumber) return;

    currentPerfumes = query ? data.results : data.perfumes;
    if (!Array.isArray(currentPerfumes)) throw new Error("Unexpected API response");

    // A full load tells us the collection size and fills the brand menu
    if (!query) { totalPerfumes = data.count; fillBrandMenu(currentPerfumes); }
    displayPerfumes();
  } catch (error) {
    if (error.name === "AbortError" || number !== requestNumber) return;
    currentPerfumes = [];
    count.textContent = "Collection unavailable";
    stateMessage("We couldn’t load the collection.", "Please check your connection and try Show all again.");
    console.error(error);
  } finally {
    if (number === requestNumber) list.setAttribute("aria-busy", "false");
  }
}

function fillBrandMenu(perfumes) {
  const brands = [...new Set(perfumes.map(p => p.brand))].sort();
  brandSelect.innerHTML = `<option value="All">All brands</option>` +
    brands.map(b => `<option value="${escapeHTML(b)}">${escapeHTML(b)}</option>`).join("");
  brandSelect.value = brand;
  document.getElementById("statCount").textContent = String(perfumes.length);
}

/* ---------- 4. DRAWING CARDS ---------- */
function displayPerfumes() {
  const perfumes = currentPerfumes.filter(p =>
    (gender === "All" || p.gender === gender) && (brand === "All" || p.brand === brand));

  const filterText = [gender !== "All" ? gender : "", brand !== "All" ? brand : ""].filter(Boolean).join(" · ");
  count.textContent = `Showing ${perfumes.length} of ${totalPerfumes || perfumes.length} perfumes${filterText ? ` · ${filterText}` : ""}`;

  if (!perfumes.length) {
    stateMessage("No scent found just yet.", "Try a brand, a note like ‘jasmine’, or Show all to start again.");
    return;
  }

  list.replaceChildren();

  // No gender/brand filter -> group by scent family. Otherwise one simple grid.
  if (gender === "All" && brand === "All") {
    const families = [...new Set([...FAMILY_ORDER, ...perfumes.map(p => p.scent_family)])];
    families.forEach(family => {
      const inFamily = perfumes.filter(p => p.scent_family === family);
      if (!inFamily.length) return;
      const section = document.createElement("section");
      section.className = "family-group";
      section.innerHTML = `<h3 class="family-title">${escapeHTML(family)} <small>${inFamily.length} perfume${inFamily.length > 1 ? "s" : ""}</small></h3>`;
      section.appendChild(buildGrid(inFamily));
      list.appendChild(section);
    });
  } else {
    list.appendChild(buildGrid(perfumes));
  }
}

function buildGrid(perfumes) {
  const grid = document.createElement("div");
  grid.className = "perfume-grid";
  perfumes.forEach(perfume => grid.appendChild(buildCard(perfume)));
  return grid;
}

function buildCard(perfume) {
  const card = document.createElement("article");
  card.className = "perfume-card";
  const [tile, juice] = COLORS[perfume.scent_family] || COLORS.Floral;
  card.style.setProperty("--tile", tile);
  card.style.setProperty("--juice", juice);

  const number = String(perfume.id).padStart(2, "0");
  const detailPage = `perfume.html?id=${perfume.id}`;

  card.innerHTML = `
    <a class="card-art" href="${detailPage}" aria-label="See all 14 details for ${escapeHTML(perfume.name)}">
      <span class="card-number">${number}</span>
      <span class="family-tag">${escapeHTML(perfume.gender)} · ${escapeHTML(perfume.scent_family)}</span>
      <div class="mini-bottle"><div class="mini-cap"></div><div class="mini-glass"><div class="mini-label">sillage<small>SCENT ${number}</small></div></div></div>
      <span class="art-hint">CLICK FOR ALL 14 DETAILS</span>
    </a>
    <div class="card-body">
      <p class="brand">${escapeHTML(perfume.brand)}</p>
      <h3>${escapeHTML(perfume.name)}</h3>
      <p class="notes">${perfume.key_notes.map(escapeHTML).join(" · ")}</p>
      <div class="dupe-preview"><small>YOUR LOCAL MATCH</small><strong>${perfume.dupes.map(escapeHTML).join(" / ")}</strong></div>
      <details>
        <summary aria-label="Show the first 7 details for ${escapeHTML(perfume.name)}">Show the first 7 details</summary>
        <div class="detail-body" aria-live="polite"></div>
      </details>
      <a class="more-btn" href="${detailPage}">See 7 more details →</a>
    </div>`;

  // Details 01–07 are fetched from the API the first time the drawer opens
  const details = card.querySelector("details");
  details.addEventListener("toggle", async () => {
    if (!details.open || details.dataset.loaded || details.dataset.loading) return;
    details.dataset.loading = "true";
    const body = details.querySelector(".detail-body");
    body.textContent = "Loading details…";
    try {
      const p = await fetchJSON(`/perfumes/${perfume.id}`);
      body.innerHTML = `
        <dl>
          <dt>01 · Perfume</dt><dd>${escapeHTML(p.name)}</dd>
          <dt>02 · Brand</dt><dd>${escapeHTML(p.brand)}</dd>
          <dt>03 · Scent family</dt><dd>${escapeHTML(p.scent_family)}</dd>
          <dt>04 · Key notes</dt><dd>${p.key_notes.map(escapeHTML).join(", ")}</dd>
          <dt>05 · Affordable dupe</dt><dd>${p.dupes.map(escapeHTML).join(" / ")}</dd>
          <dt>06 · Dupe price</dt><dd>${escapeHTML(p.dupe_price_php)}</dd>
          <dt>07 · Where to buy in PH</dt><dd>${escapeHTML(p.where_to_buy.store)}</dd>
        </dl>
        <a class="shop-link" href="${escapeHTML(safeShopURL(p.where_to_buy.url))}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a>
        <p class="stock-note">${escapeHTML(p.where_to_buy.note)}</p>`;
      details.dataset.loaded = "true";
    } catch {
      body.textContent = "Unable to load details. Close and reopen to retry.";
    } finally {
      delete details.dataset.loading;
    }
  });
  return card;
}

/* ---------- 5. FILTERS & EVENTS ---------- */
function updateGenderButtons() {
  document.querySelectorAll("[data-gender]").forEach(button => {
    const active = button.dataset.gender === gender;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

// Search
document.getElementById("searchForm").addEventListener("submit", event => {
  event.preventDefault();
  loadPerfumes(input.value.trim());
});

// Show all: clear everything and group the full collection by scent family
document.getElementById("showAll").addEventListener("click", () => {
  input.value = "";
  gender = "All";
  brand = "All";
  brandSelect.value = "All";
  updateGenderButtons();
  loadPerfumes();
});

// Gender buttons
document.querySelectorAll("[data-gender]").forEach(button => button.addEventListener("click", () => {
  gender = button.dataset.gender;
  updateGenderButtons();
  if (currentPerfumes.length) displayPerfumes();
}));

// Brand menu
brandSelect.addEventListener("change", () => {
  brand = brandSelect.value;
  if (currentPerfumes.length) displayPerfumes();
});

document.getElementById("docsLink").href = `${API_URL}/docs`;

loadPerfumes();
