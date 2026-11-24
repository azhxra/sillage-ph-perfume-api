
window.SILLAGE_API_URL = "";

window.sillageApiBase =
  window.SILLAGE_API_URL.replace(/\/$/, "") ||
  (location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : location.origin);

(() => {
  // Original Sillage PH backup collection
  const rows = [
    [1, "Baccarat Rouge 540", "Maison Francis Kurkdjian", "Amber", "Saffron|Jasmine|Cedar", "Ian Darcy 540|CG SCENT Baccarat Rouge", "Unisex", 2015, "Eau de Parfum", "Fall & Winter", "Evenings & dates", "Airy, sweet and glowing", "ID", "br", "baccarat"],

    [2, "English Pear & Freesia", "Jo Malone London", "Fruity", "Pear|Freesia|Patchouli", "Ian Darcy EP", "Unisex", 2010, "Cologne", "Spring & Summer", "Daytime & brunch", "Juicy, soft and polished", "ID", "ep"],

    [3, "Bright Crystal", "Versace", "Floral", "Yuzu|Peony|Musk", "Ian Darcy BC", "Women", 2006, "Eau de Toilette", "Spring & Summer", "Daytime & errands", "Fresh, watery and feminine", "ID", "bc"],

    [4, "Black Opium", "Yves Saint Laurent", "Gourmand", "Coffee|White flowers|Vanilla", "CG SCENT Black Opium", "Women", 2014, "Eau de Parfum", "Fall & Winter", "Nights out", "Sweet, dark and addictive", "CG", "black-opium"],

    [5, "Good Girl", "Carolina Herrera", "Amber", "Jasmine|Tuberose|Tonka bean", "CG SCENT Good Girl", "Women", 2016, "Eau de Parfum", "Fall & Winter", "Evenings & parties", "Bold, sweet and sultry", "CG", "good-girl"],

    [6, "Coco", "Chanel", "Amber", "Rose|Clove|Sandalwood", "CG SCENT Coco Chanel", "Women", 1984, "Eau de Parfum", "Fall & Winter", "Evenings & formal events", "Warm, spicy and classic", "CG", "coco-noir"],

    [7, "Light Blue", "Dolce & Gabbana", "Fresh", "Lemon|Apple|Cedar", "Ian Darcy DG", "Women", 2001, "Eau de Toilette", "Spring & Summer", "Beach days & casual wear", "Sunny, crisp and citrusy", "ID", "dg"],

    [8, "Omnia Amethyste", "Bvlgari", "Floral", "Iris|Rose|Heliotrope", "Ian Darcy BA", "Women", 2006, "Eau de Toilette", "Spring & Fall", "Office & daytime", "Soft, powdery and elegant", "ID", "ba"],

    [9, "Nectarine Blossom & Honey", "Jo Malone London", "Fruity", "Cassis|Acacia honey|Peach", "Ian Darcy NB", "Unisex", 2010, "Cologne", "Spring & Summer", "Garden parties & dates", "Honeyed, juicy and sunny", "ID", "nb"],

    [10, "Blackberry & Bay", "Jo Malone London", "Fruity", "Blackberry|Bay leaves|Cedar", "Ian Darcy BB", "Unisex", 2010, "Cologne", "Fall", "Casual & outdoors", "Fruity, green and woody", "ID", "bb"],

    [11, "Éclat d’Arpège", "Lanvin", "Floral", "Lilac|Green tea|Musk", "Ian Darcy EC|CG SCENT Éclat", "Women", 2002, "Eau de Parfum", "Spring", "Daytime & office", "Light, airy and clean", "ID", "ec", "eclat"],

    [12, "Weekend for Women", "Burberry", "Floral", "Mandarin|Hyacinth|Sandalwood", "Ian Darcy BW", "Women", 1997, "Eau de Parfum", "Spring & Summer", "Daytime & weekends", "Citrusy, floral and relaxed", "ID", "bw"],

    [13, "Aventus", "Creed", "Woody", "Pineapple|Birch|Oakmoss", "Ian Darcy CA", "Men", 2010, "Eau de Parfum", "All year", "Office & special events", "Confident, smoky-fruity and bold", "ID", "ca"],

    [14, "Bleu de Chanel", "Chanel", "Woody", "Grapefruit|Incense|Cedar", "Ian Darcy CB", "Men", 2010, "Eau de Toilette & Eau de Parfum", "All year", "Office & everyday", "Clean, woody and refined", "ID", "cb"],

    [15, "Eros", "Versace", "Fresh", "Mint|Green apple|Tonka bean", "Ian Darcy ER|CG SCENT Eros", "Men", 2012, "Eau de Toilette", "Spring & Summer", "Parties & nights out", "Minty, sweet and energetic", "ID", "er", "versace-eros"],

    [16, "Acqua di Giò", "Giorgio Armani", "Fresh", "Bergamot|Marine accord|Cedar", "Ian Darcy AG", "Men", 1996, "Eau de Toilette", "Summer", "Beach & casual", "Aquatic, fresh and easygoing", "ID", "ag"],

    [17, "Fucking Fabulous", "Tom Ford", "Leather", "Clary sage|Almond|Leather", "Ian Darcy FF", "Unisex", 2017, "Eau de Parfum", "Fall & Winter", "Nights out", "Smooth, leathery and creamy", "ID", "ff"],

    [18, "Pour Homme Extrême", "Bvlgari", "Woody", "Grapefruit|Tea|Vetiver", "Ian Darcy BE", "Men", 1999, "Eau de Toilette", "Spring & Summer", "Daytime & gym", "Zesty, green tea and woody", "ID", "be"],

    [19, "L’Eau d’Issey Pour Homme", "Issey Miyake", "Fresh", "Yuzu|Nutmeg|Sandalwood", "Ian Darcy IM", "Men", 1994, "Eau de Toilette", "Spring & Summer", "Daytime & casual", "Clean, citrusy-spicy and light", "ID", "im"],

    [20, "L.12.12 Blanc", "Lacoste", "Fresh", "Grapefruit|Tuberose|Vetiver", "Ian Darcy LW|CG SCENT Lacoste White", "Men", 2011, "Eau de Toilette", "Summer", "Daytime & sports", "Crisp, sporty and fresh", "ID", "lw", "lacoste-white"],

    [21, "Libre", "Yves Saint Laurent", "Floral", "Lavender|Orange blossom|Vanilla", "CG SCENT YSL Libre", "Women", 2019, "Eau de Parfum", "All year", "Daytime to evenings", "Fresh lavender with warm vanilla", "CG", "ysl-libre"],

    [22, "Dylan Blue Pour Homme", "Versace", "Fresh", "Bergamot|Black pepper|Patchouli", "CG SCENT Versace Dylan Blue", "Men", 2016, "Eau de Toilette", "Spring & Summer", "Daytime & dates", "Fresh, peppery and aromatic", "CG", "versace-db"],

    [23, "My Way", "Giorgio Armani", "Floral", "Orange blossom|Tuberose|Vanilla", "CG SCENT My Way", "Women", 2020, "Eau de Parfum", "All year", "Weddings & dates", "Creamy white flowers, soft and romantic", "CG", "my-way"],

    [24, "Chance", "Chanel", "Floral", "Pink pepper|Jasmine|Patchouli", "CG SCENT Chanel Chance", "Women", 2002, "Eau de Toilette & Eau de Parfum", "Spring & Fall", "Daytime & casual", "Spirited, floral and lightly spicy", "CG", "chanel-chance"],

    [25, "Noir", "Tom Ford", "Amber", "Bergamot|Rose|Vanilla", "CG SCENT Tom Ford Noir", "Men", 2012, "Eau de Parfum", "Fall & Winter", "Evenings & dates", "Warm, spicy-rose and smooth", "CG", "tom-ford-noir"]
  ];

  // Convert backup records to the existing API format.
  const saved = rows.map(row => {
    const [
      id, name, brand, scent_family,
      notes, alternatives, gender,
      year_launched, concentration,
      best_season, best_occasion, vibe,
      seller, slug, extra
    ] = row;

    const isIanDarcy = seller === "ID";

    let note = isIanDarcy
      ? "Philippine listing; check current stock and price. Pairing is a community comparison."
      : "Seller-listed inspired fragrance; check current stock, size and price.";

    if (id === 13 || id === 17) {
      note += " Listed as out of stock on 10 Oct 2026.";
    }

    return {
      id,
      name,
      brand,
      scent_family,
      key_notes: notes.split("|"),
      dupes: alternatives.split("|"),
      gender,
      year_launched,
      concentration,
      best_season,
      best_occasion,
      vibe,
      price_php_min: 450,
      dupe_price_php: isIanDarcy
        ? "PHP 450 / 100 ml (reference price)"
        : "From PHP 450 (check bottle size)",
      dupe_size: isIanDarcy
        ? "100 ml"
        : "Check the listing",
      where_to_buy: {
        store: isIanDarcy
          ? "Ian Darcy Philippines"
          : "CG SCENT Philippines",
        url: isIanDarcy
          ? `https://iandarcyfragrance.com/product/${slug}/`
          : `https://cgscent.com/product/${slug}`,
        note
      },
      other_stores: extra
        ? [{
            store: "CG SCENT Philippines",
            dupe: alternatives.split("|")[1],
            url: `https://cgscent.com/product/${extra}`
          }]
        : []
    };
  });

  // Clearly indicate when backup data is being displayed.
  function notice(active) {
    const existing = document.querySelector("#catalogPreview");

    if (!active) {
      existing?.remove();
      return;
    }

    if (existing) return;

    const message = document.createElement("p");
    message.id = "catalogPreview";
    message.className = "preview-notice";
    message.setAttribute("role", "status");

    message.textContent =
      "Preview mode: showing the original 25 perfumes while the live API is unavailable. Prices may be outdated. Account features require the live backend.";

    const main = document.querySelector("main");

    if (main) {
      main.before(message);
    } else {
      document.body.append(message);
    }
  }

  function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
      status,
      headers: {
        "Content-Type": "application/json",
        "X-Sillage-Preview": "1",
        "Cache-Control": "no-store"
      }
    });
  }

  // Backup API for catalog, search, comparison and details.
  function fallback(url) {
    const path = url.pathname.replace(/\/$/, "");
    const params = url.searchParams;
    const q = (params.get("q") || "").trim();

    // Compare perfumes
    if (path === "/perfumes/compare") {
      const ids = (params.get("ids") || "")
        .split(",")
        .map(Number);

      if (
        ids.length < 2 ||
        ids.length > 3 ||
        new Set(ids).size !== ids.length ||
        ids.some(id => !Number.isInteger(id) || id <= 0)
      ) {
        return json({
          detail: "Choose 2 or 3 distinct perfumes."
        }, 422);
      }

      const perfumes = ids.map(id =>
        saved.find(p => p.id === id)
      );

      if (perfumes.some(p => !p)) {
        return json({
          detail: "Perfume not found."
        }, 404);
      }

      return json({
        count: perfumes.length,
        perfumes
      });
    }

    // Individual perfume
    if (/^\/perfumes\/\d+$/.test(path)) {
      const id = Number(path.split("/").pop());
      const perfume = saved.find(p => p.id === id);

      return perfume
        ? json(perfume)
        : json({ detail: "Perfume not found." }, 404);
    }

    // Gender and scent-family filters
    let records = saved.filter(p =>
      (!params.get("gender") ||
        p.gender === params.get("gender")) &&
      (!params.get("scent_family") ||
        p.scent_family === params.get("scent_family"))
    );

    // Search
    if (path === "/perfumes/search") {
      if (!q || q.length > 100) {
        return json({
          detail: "Enter a search term of 1–100 characters."
        }, 422);
      }

      records = records.filter(p =>
        [
          p.name,
          p.brand,
          p.scent_family,
          p.gender,
          ...p.key_notes,
          ...p.dupes,
          JSON.stringify(p.where_to_buy),
          JSON.stringify(p.other_stores)
        ]
        .join(" ")
        .toLowerCase()
        .includes(q.toLowerCase())
      );

      return json({
        query: q,
        count: records.length,
        results: records
      });
    }

    // Price sorting
    const sort = params.get("sort");

    if (sort === "price_asc" || sort === "price_desc") {
      records.sort((a, b) =>
        (
          sort === "price_desc"
            ? b.price_php_min - a.price_php_min
            : a.price_php_min - b.price_php_min
        ) || a.id - b.id
      );
    }

    return json({
      count: records.length,
      perfumes: records
    });
  }

  // Validate the live API response.
  const isPerfume = p =>
    p &&
    Number.isInteger(p.id) &&
    typeof p.name === "string" &&
    Array.isArray(p.key_notes) &&
    Array.isArray(p.dupes) &&
    p.where_to_buy &&
    Array.isArray(p.other_stores);

  function valid(data, path) {
    if (/^\/perfumes\/\d+$/.test(path)) {
      return isPerfume(data);
    }

    const records =
      path === "/perfumes/search"
        ? data?.results
        : data?.perfumes;

    return Array.isArray(records) &&
      records.every(isPerfume);
  }

  // Try the live backend first, then use backup data.
  window.sillageCatalogFetch = async (
    input,
    options = {}
  ) => {
    const url = new URL(input, window.sillageApiBase);
    const path = url.pathname.replace(/\/$/, "");

    // Never simulate authentication or database writes.
    if (
      (options.method || "GET").toUpperCase() !== "GET" ||
      !/^\/perfumes(?:\/(?:search|compare|\d+))?$/.test(path)
    ) {
      return fetch(input, options);
    }

    const upstream = options.signal;
    const controller = new AbortController();
    const abort = () => controller.abort();

    if (upstream?.aborted) {
      throw new DOMException("Aborted", "AbortError");
    }

    upstream?.addEventListener("abort", abort, {
      once: true
    });

    const timer = setTimeout(abort, 4000);

    try {
      const response = await fetch(input, {
        ...options,
        signal: controller.signal
      });

      if (
        response.status === 404 &&
        /^\/perfumes\/\d+$/.test(path) &&
        (response.headers.get("Content-Type") || "")
          .includes("application/json")
      ) {
        const error = await response.clone().json();

        if (error.detail === "Perfume not found.") {
          return response;
        }
      }

      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }

      const data = await response.clone().json();

      if (!valid(data, path)) {
        throw new Error("Unexpected catalogue response");
      }

      if (upstream?.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }

      notice(
        response.headers.get("X-Sillage-Preview") === "1"
      );

      return response;

    } catch (error) {
      if (upstream?.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }

      console.warn(
        "Sillage PH: Live API unavailable. Using backup catalogue."
      );

      notice(true);
      return fallback(url);

    } finally {
      clearTimeout(timer);
      upstream?.removeEventListener("abort", abort);
    }
  };
})();
