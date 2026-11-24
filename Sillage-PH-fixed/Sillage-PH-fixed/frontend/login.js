const session = window.sillageSession;
const form = document.querySelector("#loginForm");
const message = document.querySelector("#authMessage");
const mode = document.querySelector("#authMode");
const password = form.elements.password;
const submit = form.querySelector("button[type=submit]");
const from = new URLSearchParams(location.search).get("from");
let signingUp = false;

function enterAccount(user) {
  location.replace(from === "catalog" ? "index.html#collection" : session.accountPage(user.role));
}

mode.addEventListener("click", () => {
  signingUp = !signingUp;
  document.querySelector("h1").textContent = signingUp ? "Create an account" : "Welcome back.";
  submit.textContent = signingUp ? "Sign up" : "Sign in";
  mode.textContent = signingUp ? "Already registered? Sign in" : "New here? Create an account";
  password.minLength = signingUp ? 8 : 1;
  password.autocomplete = signingUp ? "new-password" : "current-password";
  message.textContent = signingUp ? "Use at least 8 characters for your password." : "";
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  submit.disabled = mode.disabled = true;
  message.textContent = signingUp ? "Creating account..." : "Signing in...";
  try {
    const data = await session.request(signingUp ? "/auth/signup" : "/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({email: form.elements.email.value.trim(), password: password.value})
    });
    if (signingUp) {
      form.reset();
    } else {
      session.signIn(data.access_token);
      enterAccount(data);
    }
    if (signingUp) {
      mode.disabled = false;
      mode.click();
      message.textContent = data.message;
    }
  } catch (error) {
    message.textContent = error.message;
  } finally {
    submit.disabled = mode.disabled = false;
  }
});

if (session.token()) {
  session.request("/auth/me").then(enterAccount).catch(error => {
    message.textContent = error.message;
  });
}
