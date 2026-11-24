// Leave the API URL empty for FastAPI hosting, or set it for a separate frontend host.
window.SILLAGE_API_URL = "";
window.sillageApiBase = window.SILLAGE_API_URL.replace(/\/$/, "") ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000" : location.origin);

window.sillageCatalogFetch = async (url, options) => {
  const response = await fetch(url, options);
  if (response.headers.get("X-Sillage-Preview") === "1" && !document.querySelector("#catalogPreview")) {
    const notice = document.createElement("p");
    notice.id = "catalogPreview";
    notice.className = "preview-notice";
    notice.textContent = "Showing the saved collection while the live catalog is unavailable. Account features may be temporarily unavailable.";
    const main = document.querySelector("main");
    if (main) main.before(notice);
  }
  return response;
};
