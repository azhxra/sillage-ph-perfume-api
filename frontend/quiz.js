const API = "https://sillage-ph-perfume-api.vercel.app";
const app = document.getElementById("app");

// Each question: text + answers as [label, scent family]
const questions = [
  { text: "Pick a perfect weekend.", answers: [
    ["A beach day by the sea", "Fresh"],
    ["Garden brunch with flowers", "Floral"],
    ["Cozy café and dessert", "Gourmand"],
    ["A glamorous night out", "Amber"] ] },
  { text: "What would you grab at a market?", answers: [
    ["Ripe peaches and berries", "Fruity"],
    ["Citrus and fresh herbs", "Fresh"],
    ["Sandalwood and cedar", "Woody"],
    ["A leather bag", "Leather"] ] },
  { text: "How do you want to be remembered?", answers: [
    ["Clean and effortless", "Fresh"],
    ["Soft and romantic", "Floral"],
    ["Warm and bold", "Amber"],
    ["Sweet and playful", "Fruity"] ] }
];

let picks = []; // scent family chosen for each question so far

// Escape text before putting it into HTML
const safe = text => String(text).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);

function showQuestion() {
  const n = picks.length;
  const { text, answers } = questions[n];

  app.innerHTML = `
    <p class="small">Question ${n + 1} of ${questions.length}</p>
    <h2>${safe(text)}</h2>
    ${answers.map(([label]) => `<button class="option">${safe(label)}</button>`).join("")}
  `;

  app.querySelectorAll(".option").forEach((button, i) => {
    button.onclick = () => {
      picks.push(answers[i][1]);
      picks.length < questions.length ? showQuestion() : showResults();
    };
  });
}

// The most common family wins (ties go to the earliest answer)
function topFamily() {
  const count = f => picks.filter(p => p === f).length;
  return [...new Set(picks)].sort((a, b) => count(b) - count(a))[0];
}

async function showResults() {
  const family = topFamily();
  app.textContent = "Finding your scent…";

  try {
    const res = await fetch(`${API}/perfumes`);
    if (!res.ok) throw new Error("Request failed");
    const { perfumes } = await res.json();

    const cards = perfumes
      .filter(p => p.scent_family === family)
      .map(p => `
        <article class="card">
          <p class="brand">${safe(p.brand)}</p>
          <h3>${safe(p.name)}</h3>
          <p class="notes">${p.key_notes.map(safe).join(" · ")}</p>
          <div class="match">
            <small>YOUR LOCAL MATCH</small>
            <strong>${p.dupes.map(safe).join(" / ")}</strong><br>
            ${safe(p.dupe_price_php)}
          </div>
        </article>`)
      .join("");

    app.innerHTML = `
      <p class="label">YOUR SCENT FAMILY</p>
      <h2 style="font-size:32px">${safe(family)}</h2>
      <div class="grid">${cards}</div>
      <button class="retake">Retake the quiz</button>
    `;

    app.querySelector(".retake").onclick = () => { picks = []; showQuestion(); };
  } catch {
    app.textContent = "We couldn't load your results. Please refresh and try again.";
  }
}
