const API = "https://sillage-ph-perfume-api.vercel.app";
const page = document.getElementById("brands");

// Escape text before putting it into HTML
const safe = text => String(text).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);

// One card per perfume
const perfumeCard = p => `
  <article class="card">
    <p class="family">${safe(p.scent_family)}</p>
    <h3>${safe(p.name)}</h3>
    <p class="notes">${p.key_notes.map(safe).join(" · ")}</p>
    <div class="match">
      <small>YOUR LOCAL MATCH</small>
      <strong>${p.dupes.map(safe).join(" / ")}</strong><br>
      ${safe(p.dupe_price_php)}<br>
      <a href="${safe(p.where_to_buy.url)}" target="_blank" rel="noopener noreferrer">View Philippine listing ↗</a>
    </div>
  </article>`;

// One section per brand, with all of its perfumes
const brandSection = (brand, perfumes) => `
  <section class="brand-section">
    <h2>${safe(brand)}</h2>
    <p class="small">${perfumes.length} featured perfume${perfumes.length > 1 ? "s" : ""}</p>
    <div class="grid">${perfumes.map(perfumeCard).join("")}</div>
  </section>`;

async function loadBrands() {
  try {
    const res = await fetch(`${API}/perfumes`);
    if (!res.ok) throw new Error("Request failed");
    const { perfumes } = await res.json();

    // Group perfumes by brand: { "Dior": [...], "Chanel": [...] }
    const byBrand = {};
    perfumes.forEach(p => (byBrand[p.brand] ||= []).push(p));

    page.innerHTML = Object.keys(byBrand).sort()
      .map(brand => brandSection(brand, byBrand[brand]))
      .join("");
  } catch {
    page.textContent = "We couldn't load the brands. Please refresh and try again.";
  }
}

loadBrands();
