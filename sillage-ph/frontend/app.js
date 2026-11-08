// Load the collection once per search; cards use the fields already returned.
const API_URL = (window.SILLAGE_API_URL || "").replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);

const list = document.getElementById("perfumeList");
const count = document.getElementById("resultCount");
const input = document.getElementById("searchInput");

// Page state
let currentPerfumes = [];   // result of the latest load / search
let gender = "All";         // All | Men | Women | Unisex
let totalPerfumes = 0;      // size of the full collection
let searchController;       // lets a new search cancel the previous one
let requestNumber = 0;      // ignores out-of-date responses

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

    // Keep the full collection count when searching.
    if (!query) totalPerfumes = data.count;
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

// Search results and gender filters share one grid.
function displayPerfumes() {
  const perfumes = currentPerfumes
    .filter(p => gender === "All" || p.gender === gender)
    .sort((a, b) => a.id - b.id);
  count.textContent = `Showing ${perfumes.length} of ${totalPerfumes || perfumes.length} perfumes`;
  if (!perfumes.length) {
    stateMessage("No scent found just yet.", "Try another search or Show all.");
    return;
  }
  list.replaceChildren(buildGrid(perfumes));
}

function buildGrid(perfumes) {
  const grid = document.createElement("div");
  grid.className = "perfume-grid";
  perfumes.forEach(perfume => grid.appendChild(buildCard(perfume)));
  return grid;
}

function buildCard(p) {
  const card = document.createElement("article");
  card.className = "perfume-card";
  card.setAttribute("role", "button");
  card.tabIndex = 0;
  card.setAttribute("aria-expanded", "false");
  card.setAttribute("aria-label", `${p.brand} ${p.name}, perfume details`);
  card.setAttribute("aria-controls", `card-details-${p.id}`);
  const [tile, juice] = COLORS[p.scent_family] || COLORS.Floral;
  card.style.setProperty("--tile", tile);
  card.style.setProperty("--juice", juice);
  const number = String(p.id).padStart(2, "0");

  card.innerHTML = `
    <div class="card-art" aria-hidden="true">
      <div class="mini-bottle"><div class="mini-cap"></div><div class="mini-glass"><div class="mini-label">sillage<small>SCENT ${number}</small></div></div></div>
    </div>
    <div class="card-body">
      <p class="brand">${escapeHTML(p.brand)}</p>
      <h3>${escapeHTML(p.name)}</h3>
      <p class="notes">${p.key_notes.map(escapeHTML).join(" · ")}</p>
      <span class="family-tag">${escapeHTML(p.scent_family)}</span>
      <p class="dupe-preview"><strong>${p.dupes.map(escapeHTML).join(" / ")}</strong> — ${escapeHTML(p.dupe_price_php || "Price unavailable")}</p>
      <div class="card-extra" id="card-details-${p.id}" hidden>
        <dl>
          <dt>Perfume</dt><dd>${escapeHTML(p.name)}</dd>
          <dt>Brand</dt><dd>${escapeHTML(p.brand)}</dd>
          <dt>Scent family</dt><dd>${escapeHTML(p.scent_family)}</dd>
          <dt>Key notes</dt><dd>${p.key_notes.map(escapeHTML).join(", ")}</dd>
          <dt>Affordable dupe</dt><dd>${p.dupes.map(escapeHTML).join(" / ")}</dd>
          <dt>Dupe price</dt><dd>${escapeHTML(p.dupe_price_php || "Price unavailable")}</dd>
          <dt>Where to buy in PH</dt><dd>${escapeHTML(p.where_to_buy.store)}</dd>
          <dt>Gender</dt><dd>${escapeHTML(p.gender)}</dd>
          <dt>Year launched</dt><dd>${escapeHTML(p.year_launched)}</dd>
          <dt>Concentration</dt><dd>${escapeHTML(p.concentration)}</dd>
          <dt>Best season</dt><dd>${escapeHTML(p.best_season)}</dd>
          <dt>Best occasion</dt><dd>${escapeHTML(p.best_occasion)}</dd>
          <dt>Dupe bottle size</dt><dd>${escapeHTML(p.dupe_size)}</dd>
          <dt>Vibe</dt><dd>${escapeHTML(p.vibe)}</dd>
        </dl>
        <a class="shop-link" href="${escapeHTML(safeShopURL(p.where_to_buy.url))}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a>
        <p class="stock-note">${escapeHTML(p.where_to_buy.note)}</p>
        <a class="shop-link" href="compare.html?a=${encodeURIComponent(p.id)}">Compare this perfume</a>
      </div>
    </div>`;

  const extra = card.querySelector(".card-extra");
  function toggleCard() {
    const expanded = card.getAttribute("aria-expanded") !== "true";
    card.setAttribute("aria-expanded", String(expanded));
    card.classList.toggle("expanded", expanded);
    extra.hidden = !expanded;
  }
  card.addEventListener("click", toggleCard);
  card.addEventListener("keydown", event => {
    if (event.target === card && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      toggleCard();
    }
  });
  // Let links open without toggling their card.
  card.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", event => event.stopPropagation());
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

// Show all clears the search and gender filter.
document.getElementById("showAll").addEventListener("click", () => {
  input.value = "";
  gender = "All";
  updateGenderButtons();
  loadPerfumes();
});

// Gender buttons
document.querySelectorAll("[data-gender]").forEach(button => button.addEventListener("click", () => {
  gender = button.dataset.gender;
  updateGenderButtons();
  displayPerfumes();
}));

document.getElementById("docsLink").href = `${API_URL}/docs`;

loadPerfumes();
