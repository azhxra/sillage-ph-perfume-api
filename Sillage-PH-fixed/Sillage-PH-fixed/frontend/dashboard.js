const session = window.sillageSession;
const statusLine = document.querySelector("#dashboardMessage");
const panel = document.querySelector("#dashboard");
const loginLink = document.querySelector("#signInLink");
const isAdminPage = document.body.dataset.page === "admin";

function report(error) {
  statusLine.textContent = error.message;
  if (error.status === 401) {
    panel.hidden = true;
    loginLink.hidden = false;
  }
}

async function loadFavorites() {
  const {perfumes} = await session.request("/auth/favorites");
  const list = document.querySelector("#favoritesList");
  list.replaceChildren();
  statusLine.textContent = perfumes.length ? "" : "You have no saved perfumes yet.";
  for (const perfume of perfumes) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = "perfume.html?id=" + encodeURIComponent(perfume.id);
    link.textContent = perfume.brand + " " + perfume.name;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "btn secondary";
    remove.textContent = "Remove";
    remove.setAttribute("aria-label", "Remove " + link.textContent + " from favorites");
    remove.addEventListener("click", async () => {
      remove.disabled = true;
      try {
        await session.request("/auth/favorites/" + perfume.id, {method: "DELETE"});
        item.remove();
        statusLine.textContent = list.children.length ? "Favorite removed." : "You have no saved perfumes yet.";
      } catch (error) {
        report(error);
        remove.disabled = false;
      }
    });
    item.append(link, remove);
    list.append(item);
  }
}

async function setupEditor() {
  const select = document.querySelector("#perfumeSelect");
  const editor = document.querySelector("#perfumeJson");
  const form = document.querySelector("#perfumeEditor");
  const save = form.querySelector("[type=submit]");
  const remove = document.querySelector("#deletePerfume");
  const template = {
    name: "", brand: "", scent_family: "Floral", key_notes: [], dupes: [],
    gender: "Unisex", year_launched: new Date().getFullYear(), concentration: "",
    best_season: "", best_occasion: "", dupe_size: "", vibe: "", dupe_price_php: "",
    price_php_min: 0, where_to_buy: {store: "", url: "", note: ""}, other_stores: []
  };
  let records = [];

  function displayRecord() {
    const record = records.find(item => String(item.id) === select.value);
    const fields = {...(record || template)};
    delete fields.id;
    editor.value = JSON.stringify(fields, null, 2);
    remove.disabled = !record;
  }

  async function refresh(id = "") {
    const data = await session.request("/perfumes");
    records = data.perfumes;
    select.replaceChildren(new Option("New perfume", ""), ...records.map(record =>
      new Option(record.brand + " " + record.name, record.id)
    ));
    select.value = String(id);
    displayRecord();
  }

  async function mutate(method) {
    const id = select.value;
    if (method === "DELETE" && !confirm("Delete " + select.selectedOptions[0].textContent + "?")) return;
    select.disabled = editor.disabled = save.disabled = remove.disabled = true;
    try {
      const options = {method};
      if (method !== "DELETE") {
        options.headers = {"Content-Type": "application/json"};
        try { options.body = JSON.stringify(JSON.parse(editor.value)); }
        catch { throw new Error("Enter valid JSON before saving."); }
      }
      const result = await session.request(id ? "/perfumes/" + id : "/perfumes", options);
      statusLine.textContent = method === "DELETE" ? "Perfume deleted." : "Perfume saved.";
      try { await refresh(result?.id); }
      catch {
        if (method === "DELETE") {
          select.selectedOptions[0]?.remove();
          records = records.filter(record => String(record.id) !== id);
          select.value = "";
          displayRecord();
        }
        statusLine.textContent += " Refresh the page to reload the record list.";
        save.disabled = true;
        return;
      }
    } catch (error) {
      report(error);
    } finally {
      select.disabled = editor.disabled = false;
      remove.disabled = !select.value;
    }
    save.disabled = false;
  }

  select.addEventListener("change", displayRecord);
  form.addEventListener("submit", event => {
    event.preventDefault();
    mutate(select.value ? "PUT" : "POST");
  });
  remove.addEventListener("click", () => mutate("DELETE"));
  await refresh();
}

document.querySelector("#logout").addEventListener("click", () => {
  session.signOut();
  location.replace("login.html");
});

(async () => {
  if (!session.token()) {
    report(Object.assign(new Error("Sign in to view this page."), {status: 401}));
    return;
  }
  try {
    const user = await session.request("/auth/me");
    if (isAdminPage && user.role !== "admin") {
      location.replace("account.html");
      return;
    }
    document.querySelector("#identity").textContent = (user.email || user.id) + " | " + user.role;
    document.querySelector("#adminLink").hidden = isAdminPage || user.role !== "admin";
    statusLine.textContent = "";
    panel.hidden = false;
    if (isAdminPage) await setupEditor();
    else await loadFavorites();
  } catch (error) {
    report(error);
  }
})();
