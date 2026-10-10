/* ==========================================================================
   Sillage PH — compare.html (compare 2–3 perfumes)
   Endpoints used:
     GET /perfumes                     -> fills the three drop-downs
     GET /perfumes/compare?ids=1,4,15  -> data for the table
   ========================================================================== */

/* ---------- 1. API SETUP (address comes from config.js) ---------- */
const API_URL = (window.SILLAGE_API_URL || "").replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);

const pickers = ["pickA", "pickB", "pickC"].map(id => document.getElementById(id));
const message = document.getElementById("message");
const result = document.getElementById("result");

// The 14 rows of the table: [number, label, how to read the value from a perfume]
const ROWS = [
  ["01", "Perfume",           p => p.name],
  ["02", "Brand",             p => p.brand],
  ["03", "Scent family",      p => p.scent_family],
  ["04", "Key notes",         p => p.key_notes.join(", ")],
  ["05", "Affordable dupe",   p => p.dupes.join(" / ")],
  ["06", "Dupe price",        p => p.dupe_price_php],
  ["07", "Where to buy",      p => p.where_to_buy.store],
  ["08", "Gender",            p => p.gender],
  ["09", "Year launched",     p => p.year_launched],
  ["10", "Concentration",     p => p.concentration],
  ["11", "Best season",       p => p.best_season],
  ["12", "Best occasion",     p => p.best_occasion],
  ["13", "Dupe bottle size",  p => p.dupe_size],
  ["14", "Vibe",              p => p.vibe],
];

/* ---------- 2. HELPERS ---------- */
const safe = text => String(text).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);

/* ---------- 3. DROP-DOWNS ---------- */
function fillPickers(perfumes) {
  const sorted = [...perfumes].sort((a, b) => a.name.localeCompare(b.name));
  const options = sorted.map(p => `<option value="${p.id}">${safe(p.name)} — ${safe(p.brand)}</option>`).join("");

  pickers.forEach((select, i) => {
    select.innerHTML = (i === 2 ? `<option value="">— none —</option>` : `<option value="">Choose a perfume…</option>`) + options;
    select.addEventListener("change", compare);
  });

  // ?a=7 (from a detail page) pre-selects Perfume A
  const start = new URLSearchParams(location.search).get("a");
  if (start && perfumes.some(p => String(p.id) === start)) pickers[0].value = start;
}

/* ---------- 4. COMPARE ---------- */
async function compare() {
  const ids = pickers.map(s => s.value).filter(Boolean);

  if (new Set(ids).size !== ids.length) {
    result.innerHTML = "";
    message.textContent = "Please choose different perfumes in each box.";
    return;
  }
  if (ids.length < 2) {
    result.innerHTML = "";
    message.textContent = "Pick at least two perfumes to compare.";
    return;
  }

  message.textContent = "Comparing…";
  try {
    const res = await fetch(`${API_URL}/perfumes/compare?ids=${ids.join(",")}`);
    if (!res.ok) throw new Error("Request failed");
    const { perfumes } = await res.json();
    drawTable(perfumes);
    message.textContent = `Comparing ${perfumes.length} perfumes.`;
  } catch {
    result.innerHTML = "";
    message.textContent = "We couldn't compare these perfumes. Please try again.";
  }
}

function drawTable(perfumes) {
  const head = perfumes.map(p =>
    `<th scope="col"><small>${safe(p.brand)}</small><a href="perfume.html?id=${p.id}">${safe(p.name)}</a></th>`).join("");

  const body = ROWS.map(([number, label, read]) => {
    const values = perfumes.map(read);
    const differs = new Set(values.map(String)).size > 1;   // highlight rows that are not all the same
    return `<tr${differs ? ' class="differs"' : ""}>
      <th scope="row">${number} · ${label}</th>
      ${values.map(v => `<td>${safe(v)}</td>`).join("")}
    </tr>`;
  }).join("");

  result.innerHTML = `
    <table class="compare-table">
      <thead><tr><th scope="col"></th>${head}</tr></thead>
      <tbody>${body}</tbody>
    </table>
    <p class="legend"><i></i>Highlighted rows are where the perfumes differ. Click a name for its full detail page.</p>`;
}

/* ---------- 5. START ---------- */
async function start() {
  try {
    const res = await fetch(`${API_URL}/perfumes`);
    if (!res.ok) throw new Error("Request failed");
    const { perfumes } = await res.json();
    fillPickers(perfumes);
    message.textContent = "Pick at least two perfumes to compare.";
    compare();
  } catch {
    message.textContent = "We couldn't load the perfumes. Please refresh and try again.";
  }
}

start();
