const DEPLOYED_API_URL = "";
const API_URL = DEPLOYED_API_URL.replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);
const list = document.getElementById("perfumeList");
const count = document.getElementById("resultCount");
const input = document.getElementById("searchInput");
let currentPerfumes = [];
let family = "All";
let searchController;
let requestNumber = 0;

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
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
function displayPerfumes() {
  const perfumes = currentPerfumes.filter(p => family === "All" || p.scent_family === family);
  count.textContent = `Showing ${perfumes.length} of 20 perfumes${family === "All" ? "" : ` · ${family}`}`;
  if (!perfumes.length) {
    stateMessage("No scent found just yet.", "Try a brand, a note like ‘jasmine’, or Show all to start again.");
    return;
  }
  const colors = {Amber:["#faf0e9","#d9b48f"],Floral:["#f8edf2","#d8afc2"],Fruity:["#faf2ed","#e3bdab"],Fresh:["#eff4f2","#b1c9c0"],Woody:["#f2efeb","#bea88a"],Gourmand:["#f5e9ec","#b7798a"],Leather:["#f1eae7","#b5927a"]};
  list.replaceChildren();
  perfumes.forEach(perfume => {
    const card = document.createElement("article");
    card.className = "perfume-card";
    const [tile,juice] = colors[perfume.scent_family] || colors.Floral;
    card.style.setProperty("--tile",tile); card.style.setProperty("--juice",juice);
    card.innerHTML = `
      <div class="card-art" aria-hidden="true"><span class="card-number">${String(perfume.id).padStart(2,"0")}</span><span class="family-tag">${escapeHTML(perfume.scent_family)}</span><div class="mini-bottle"><div class="mini-cap"></div><div class="mini-glass"><div class="mini-label">sillage<small>SCENT ${String(perfume.id).padStart(2,"0")}</small></div></div></div></div>
      <div class="card-body"><p class="brand">${escapeHTML(perfume.brand)}</p><h3>${escapeHTML(perfume.name)}</h3><p class="notes">${perfume.key_notes.map(escapeHTML).join(" · ")}</p>
      <div class="dupe-preview"><small>YOUR LOCAL MATCH</small><strong>${perfume.dupes.map(escapeHTML).join(" / ")}</strong></div>
      <details><summary aria-label="Show all details for ${escapeHTML(perfume.name)}">Show all 7 details</summary><div class="detail-body" aria-live="polite"></div></details></div>`;
    const details = card.querySelector("details");
    details.addEventListener("toggle", async () => {
      if (!details.open || details.dataset.loaded || details.dataset.loading) return;
      details.dataset.loading = "true";
      const body = details.querySelector(".detail-body");
      body.textContent = "Loading details…";
      try {
        const p = await fetchJSON(`/perfumes/${perfume.id}`);
        body.innerHTML = `<dl><dt>01 · Perfume</dt><dd>${escapeHTML(p.name)}</dd><dt>02 · Brand</dt><dd>${escapeHTML(p.brand)}</dd><dt>03 · Scent family</dt><dd>${escapeHTML(p.scent_family)}</dd><dt>04 · Key notes</dt><dd>${p.key_notes.map(escapeHTML).join(", ")}</dd><dt>05 · Affordable dupe</dt><dd>${p.dupes.map(escapeHTML).join(" / ")}</dd><dt>06 · Dupe price</dt><dd>${escapeHTML(p.dupe_price_php)}</dd><dt>07 · Where to buy in PH</dt><dd>${escapeHTML(p.where_to_buy.store)}</dd></dl><a class="shop-link" href="${escapeHTML(safeShopURL(p.where_to_buy.url))}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a><p class="stock-note">${escapeHTML(p.where_to_buy.note)}</p>`;
        details.dataset.loaded = "true";
      } catch { body.textContent = "Unable to load details. Close and reopen to retry."; }
      finally { delete details.dataset.loading; }
    });
    list.appendChild(card);
  });
}
document.getElementById("searchForm").addEventListener("submit", event => { event.preventDefault(); loadPerfumes(input.value.trim()); });
document.getElementById("showAll").addEventListener("click", () => {
  input.value = ""; family = "All"; updateFilters(); loadPerfumes();
});
function updateFilters() {
  document.querySelectorAll(".filter").forEach(button => {
    const active = button.dataset.family === family;
    button.classList.toggle("active",active); button.setAttribute("aria-pressed",String(active));
  });
}
document.querySelectorAll(".filter").forEach(button => button.addEventListener("click", () => {
  family = button.dataset.family; updateFilters();
  if (currentPerfumes.length) displayPerfumes();
}));
document.getElementById("docsLink").href = `${API_URL}/docs`;
