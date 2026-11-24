(() => {
  const tokenKey = "sillage_access_token";
  const token = () => sessionStorage.getItem(tokenKey);
  const signOut = () => sessionStorage.removeItem(tokenKey);
  async function request(path, options = {}) {
    const headers = new Headers(options.headers);
    if (token()) headers.set("Authorization", "Bearer " + token());
    const response = await fetch(window.sillageApiBase + path, {...options, headers});
    if (response.headers.get("X-Sillage-Preview") === "1") throw Object.assign(new Error("Live catalogue unavailable. Try again when the database is connected."), {status: 503});
    if (response.status === 204) return;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && path !== "/auth/login") signOut();
      throw Object.assign(new Error(data.detail || "Request failed (HTTP " + response.status + ")."), {
        status: response.status
      });
    }
    return data;
  }
  window.sillageSession = {
    request, token, signOut,
    signIn: value => sessionStorage.setItem(tokenKey, value),
    accountPage: role => role === "admin" ? "admin.html" : "account.html"
  };
})();
