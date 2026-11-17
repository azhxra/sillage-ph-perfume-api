/* Sillage PH account demo. Stores the access token only in this tab's sessionStorage. */
const BASE = (window.SILLAGE_API_URL || "").replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);
const TOKEN_KEY = "sillage_access_token";
const form = document.getElementById("loginForm");
const account = document.getElementById("account");
const message = document.getElementById("authMessage");
const tokenField = () => sessionStorage.getItem(TOKEN_KEY);

function showUser(data) {
  account.hidden = false;
  form.hidden = true;
  document.getElementById("accountEmail").textContent = data.email || data.id;
  document.getElementById("accountRole").textContent = data.role;
  document.getElementById("roleDescription").textContent = data.role === "admin"
    ? "You can create, update, and delete perfume records using the API."
    : "You can browse, search, compare, and take the quiz. You cannot change perfume records.";
}
function showSignedOut() {
  account.hidden = true;
  form.hidden = false;
}
async function api(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (HTTP ${res.status}).`);
  return data;
}
form.addEventListener("submit", async event => {
  event.preventDefault();
  message.textContent = "Signing in…";
  const submit = form.querySelector('button[type="submit"]');
  submit.disabled = true;
  try {
    const data = await api("/auth/login", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ email: form.elements.email.value.trim(), password: form.elements.password.value })
    });
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    form.reset();
    showUser(data);
    message.textContent = "Signed in successfully.";
  } catch (error) {
    message.textContent = error.message;
    showSignedOut();
  } finally {
    submit.disabled = false;
  }
});
document.getElementById("copyToken").addEventListener("click", async () => {
  const token = tokenField();
  if (!token) return;
  try { await navigator.clipboard.writeText(token); message.textContent = "Token copied. Do not share it."; }
  catch { message.textContent = "Clipboard unavailable. Please use Swagger in a supported browser."; }
});
document.getElementById("logout").addEventListener("click", () => {
  sessionStorage.removeItem(TOKEN_KEY);
  message.textContent = "Signed out of this browser tab.";
  showSignedOut();
});
(async function restore() {
  const token = tokenField();
  if (!token) return;
  try {
    const user = await api("/auth/me", {headers: {Authorization: `Bearer ${token}`}});
    showUser(user);
  } catch {
    sessionStorage.removeItem(TOKEN_KEY);
    showSignedOut();
  }
})();
