"""Sillage PH Perfume API (FastAPI).

Sections:
  1. App setup (CORS reads an environment variable)
  2. Seller helpers (build the "where to buy" data once, not 25 times)
  3. Perfume data (14 details per perfume)
  4. API routes
  5. Frontend routes (serves the HTML / CSS / JS files)
"""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ---------------------------------------------------------------------------
# 1. APP SETUP
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Sillage PH Perfume API",
    description="Luxury and designer perfumes with affordable Philippine alternatives.",
    version="2.0.0",
)

# Set ALLOWED_ORIGINS in Vercel (Settings > Environment Variables), e.g.
#   https://your-site.github.io,https://sillage-ph.vercel.app
# If it is not set, any website may call the API (fine for local testing).
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 2. SELLER HELPERS
# ---------------------------------------------------------------------------
def ian_darcy(code, extra_note="", other_stores=None):
    """Philippine listing on iandarcyfragrance.com (100 ml, PHP 450 reference)."""
    note = "Philippine listing; check current stock and price. Pairing is a community comparison."
    return {
        "dupe_price_php": "PHP 450 / 100 ml (reference price)",
        "dupe_size": "100 ml",
        "where_to_buy": {
            "store": "Ian Darcy Philippines",
            "url": f"https://iandarcyfragrance.com/product/{code}/",
            "note": f"{note} {extra_note}".strip(),
        },
        "other_stores": other_stores or [],
    }


def cg_scent(slug):
    """Philippine listing on cgscent.com (price starts at PHP 450)."""
    return {
        "dupe_price_php": "From PHP 450 (check bottle size)",
        "dupe_size": "Check the listing",
        "where_to_buy": {
            "store": "CG SCENT Philippines",
            "url": f"https://cgscent.com/product/{slug}",
            "note": "Seller-listed inspired fragrance; check current stock, size and price.",
        },
        "other_stores": [],
    }


def cg_alt(dupe_name, slug):
    """A second seller offering another match for the same perfume."""
    return {"store": "CG SCENT Philippines", "dupe": dupe_name, "url": f"https://cgscent.com/product/{slug}"}


# ---------------------------------------------------------------------------
# 3. PERFUME DATA
# Details 01-07: name, brand, scent_family, key_notes, dupes, dupe_price_php, where_to_buy
# Details 08-14: gender, year_launched, concentration, best_season, best_occasion,
#                dupe_size, vibe
# (best_season / best_occasion / vibe are style-guide suggestions, not lab data)
# ---------------------------------------------------------------------------
perfumes = [
    # ---- Maison Francis Kurkdjian ----
    {"id": 1, "name": "Baccarat Rouge 540", "brand": "Maison Francis Kurkdjian", "scent_family": "Amber",
     "key_notes": ["Saffron", "Jasmine", "Cedar"], "dupes": ["Ian Darcy 540", "CG SCENT Baccarat Rouge"],
     "gender": "Unisex", "year_launched": 2015, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Evenings & dates", "vibe": "Airy, sweet and glowing",
     **ian_darcy("br", other_stores=[cg_alt("CG SCENT Baccarat Rouge", "baccarat")])},

    # ---- Jo Malone London ----
    {"id": 2, "name": "English Pear & Freesia", "brand": "Jo Malone London", "scent_family": "Fruity",
     "key_notes": ["Pear", "Freesia", "Patchouli"], "dupes": ["Ian Darcy EP"],
     "gender": "Unisex", "year_launched": 2010, "concentration": "Cologne",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & brunch", "vibe": "Juicy, soft and polished",
     **ian_darcy("ep")},
    {"id": 9, "name": "Nectarine Blossom & Honey", "brand": "Jo Malone London", "scent_family": "Fruity",
     "key_notes": ["Cassis", "Acacia honey", "Peach"], "dupes": ["Ian Darcy NB"],
     "gender": "Unisex", "year_launched": 2010, "concentration": "Cologne",
     "best_season": "Spring & Summer", "best_occasion": "Garden parties & dates", "vibe": "Honeyed, juicy and sunny",
     **ian_darcy("nb")},
    {"id": 10, "name": "Blackberry & Bay", "brand": "Jo Malone London", "scent_family": "Fruity",
     "key_notes": ["Blackberry", "Bay leaves", "Cedar"], "dupes": ["Ian Darcy BB"],
     "gender": "Unisex", "year_launched": 2010, "concentration": "Cologne",
     "best_season": "Fall", "best_occasion": "Casual & outdoors", "vibe": "Fruity, green and woody",
     **ian_darcy("bb")},

    # ---- Versace ----
    {"id": 3, "name": "Bright Crystal", "brand": "Versace", "scent_family": "Floral",
     "key_notes": ["Yuzu", "Peony", "Musk"], "dupes": ["Ian Darcy BC"],
     "gender": "Women", "year_launched": 2006, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & errands", "vibe": "Fresh, watery and feminine",
     **ian_darcy("bc")},
    {"id": 15, "name": "Eros", "brand": "Versace", "scent_family": "Fresh",
     "key_notes": ["Mint", "Green apple", "Tonka bean"], "dupes": ["Ian Darcy ER", "CG SCENT Eros"],
     "gender": "Men", "year_launched": 2012, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Parties & nights out", "vibe": "Minty, sweet and energetic",
     **ian_darcy("er", other_stores=[cg_alt("CG SCENT Eros", "versace-eros")])},
    {"id": 22, "name": "Dylan Blue Pour Homme", "brand": "Versace", "scent_family": "Fresh",
     "key_notes": ["Bergamot", "Black pepper", "Patchouli"], "dupes": ["CG SCENT Versace Dylan Blue"],
     "gender": "Men", "year_launched": 2016, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & dates", "vibe": "Fresh, peppery and aromatic",
     **cg_scent("versace-db")},

    # ---- Yves Saint Laurent ----
    {"id": 4, "name": "Black Opium", "brand": "Yves Saint Laurent", "scent_family": "Gourmand",
     "key_notes": ["Coffee", "White flowers", "Vanilla"], "dupes": ["CG SCENT Black Opium"],
     "gender": "Women", "year_launched": 2014, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Nights out", "vibe": "Sweet, dark and addictive",
     **cg_scent("black-opium")},
    {"id": 21, "name": "Libre", "brand": "Yves Saint Laurent", "scent_family": "Floral",
     "key_notes": ["Lavender", "Orange blossom", "Vanilla"], "dupes": ["CG SCENT YSL Libre"],
     "gender": "Women", "year_launched": 2019, "concentration": "Eau de Parfum",
     "best_season": "All year", "best_occasion": "Daytime to evenings", "vibe": "Fresh lavender with warm vanilla",
     **cg_scent("ysl-libre")},

    # ---- Carolina Herrera ----
    {"id": 5, "name": "Good Girl", "brand": "Carolina Herrera", "scent_family": "Amber",
     "key_notes": ["Jasmine", "Tuberose", "Tonka bean"], "dupes": ["CG SCENT Good Girl"],
     "gender": "Women", "year_launched": 2016, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Evenings & parties", "vibe": "Bold, sweet and sultry",
     **cg_scent("good-girl")},

    # ---- Chanel ----
    {"id": 6, "name": "Coco", "brand": "Chanel", "scent_family": "Amber",
     "key_notes": ["Rose", "Clove", "Sandalwood"], "dupes": ["CG SCENT Coco Chanel"],
     "gender": "Women", "year_launched": 1984, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Evenings & formal events", "vibe": "Warm, spicy and classic",
     **cg_scent("coco-noir")},
    {"id": 14, "name": "Bleu de Chanel", "brand": "Chanel", "scent_family": "Woody",
     "key_notes": ["Grapefruit", "Incense", "Cedar"], "dupes": ["Ian Darcy CB"],
     "gender": "Men", "year_launched": 2010, "concentration": "Eau de Toilette & Eau de Parfum",
     "best_season": "All year", "best_occasion": "Office & everyday", "vibe": "Clean, woody and refined",
     **ian_darcy("cb")},
    {"id": 24, "name": "Chance", "brand": "Chanel", "scent_family": "Floral",
     "key_notes": ["Pink pepper", "Jasmine", "Patchouli"], "dupes": ["CG SCENT Chanel Chance"],
     "gender": "Women", "year_launched": 2002, "concentration": "Eau de Toilette & Eau de Parfum",
     "best_season": "Spring & Fall", "best_occasion": "Daytime & casual", "vibe": "Spirited, floral and lightly spicy",
     **cg_scent("chanel-chance")},

    # ---- Dolce & Gabbana ----
    {"id": 7, "name": "Light Blue", "brand": "Dolce & Gabbana", "scent_family": "Fresh",
     "key_notes": ["Lemon", "Apple", "Cedar"], "dupes": ["Ian Darcy DG"],
     "gender": "Women", "year_launched": 2001, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Beach days & casual wear", "vibe": "Sunny, crisp and citrusy",
     **ian_darcy("dg")},

    # ---- Bvlgari ----
    {"id": 8, "name": "Omnia Amethyste", "brand": "Bvlgari", "scent_family": "Floral",
     "key_notes": ["Iris", "Rose", "Heliotrope"], "dupes": ["Ian Darcy BA"],
     "gender": "Women", "year_launched": 2006, "concentration": "Eau de Toilette",
     "best_season": "Spring & Fall", "best_occasion": "Office & daytime", "vibe": "Soft, powdery and elegant",
     **ian_darcy("ba")},
    {"id": 18, "name": "Pour Homme Extrême", "brand": "Bvlgari", "scent_family": "Woody",
     "key_notes": ["Grapefruit", "Tea", "Vetiver"], "dupes": ["Ian Darcy BE"],
     "gender": "Men", "year_launched": 1999, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & gym", "vibe": "Zesty, green tea and woody",
     **ian_darcy("be")},

    # ---- Lanvin ----
    {"id": 11, "name": "Éclat d’Arpège", "brand": "Lanvin", "scent_family": "Floral",
     "key_notes": ["Lilac", "Green tea", "Musk"], "dupes": ["Ian Darcy EC", "CG SCENT Éclat"],
     "gender": "Women", "year_launched": 2002, "concentration": "Eau de Parfum",
     "best_season": "Spring", "best_occasion": "Daytime & office", "vibe": "Light, airy and clean",
     **ian_darcy("ec", other_stores=[cg_alt("CG SCENT Éclat", "eclat")])},

    # ---- Burberry ----
    {"id": 12, "name": "Weekend for Women", "brand": "Burberry", "scent_family": "Floral",
     "key_notes": ["Mandarin", "Hyacinth", "Sandalwood"], "dupes": ["Ian Darcy BW"],
     "gender": "Women", "year_launched": 1997, "concentration": "Eau de Parfum",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & weekends", "vibe": "Citrusy, floral and relaxed",
     **ian_darcy("bw")},

    # ---- Creed ----
    {"id": 13, "name": "Aventus", "brand": "Creed", "scent_family": "Woody",
     "key_notes": ["Pineapple", "Birch", "Oakmoss"], "dupes": ["Ian Darcy CA"],
     "gender": "Men", "year_launched": 2010, "concentration": "Eau de Parfum",
     "best_season": "All year", "best_occasion": "Office & special events", "vibe": "Confident, smoky-fruity and bold",
     **ian_darcy("ca", extra_note="Listed as out of stock on 10 Oct 2026.")},

    # ---- Giorgio Armani ----
    {"id": 16, "name": "Acqua di Giò", "brand": "Giorgio Armani", "scent_family": "Fresh",
     "key_notes": ["Bergamot", "Marine accord", "Cedar"], "dupes": ["Ian Darcy AG"],
     "gender": "Men", "year_launched": 1996, "concentration": "Eau de Toilette",
     "best_season": "Summer", "best_occasion": "Beach & casual", "vibe": "Aquatic, fresh and easygoing",
     **ian_darcy("ag")},
    {"id": 23, "name": "My Way", "brand": "Giorgio Armani", "scent_family": "Floral",
     "key_notes": ["Orange blossom", "Tuberose", "Vanilla"], "dupes": ["CG SCENT My Way"],
     "gender": "Women", "year_launched": 2020, "concentration": "Eau de Parfum",
     "best_season": "All year", "best_occasion": "Weddings & dates", "vibe": "Creamy white flowers, soft and romantic",
     **cg_scent("my-way")},

    # ---- Tom Ford ----
    {"id": 17, "name": "Fucking Fabulous", "brand": "Tom Ford", "scent_family": "Leather",
     "key_notes": ["Clary sage", "Almond", "Leather"], "dupes": ["Ian Darcy FF"],
     "gender": "Unisex", "year_launched": 2017, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Nights out", "vibe": "Smooth, leathery and creamy",
     **ian_darcy("ff", extra_note="Listed as out of stock on 10 Oct 2026.")},
    {"id": 25, "name": "Noir", "brand": "Tom Ford", "scent_family": "Amber",
     "key_notes": ["Bergamot", "Rose", "Vanilla"], "dupes": ["CG SCENT Tom Ford Noir"],
     "gender": "Men", "year_launched": 2012, "concentration": "Eau de Parfum",
     "best_season": "Fall & Winter", "best_occasion": "Evenings & dates", "vibe": "Warm, spicy-rose and smooth",
     **cg_scent("tom-ford-noir")},

    # ---- Issey Miyake ----
    {"id": 19, "name": "L’Eau d’Issey Pour Homme", "brand": "Issey Miyake", "scent_family": "Fresh",
     "key_notes": ["Yuzu", "Nutmeg", "Sandalwood"], "dupes": ["Ian Darcy IM"],
     "gender": "Men", "year_launched": 1994, "concentration": "Eau de Toilette",
     "best_season": "Spring & Summer", "best_occasion": "Daytime & casual", "vibe": "Clean, citrusy-spicy and light",
     **ian_darcy("im")},

    # ---- Lacoste ----
    {"id": 20, "name": "L.12.12 Blanc", "brand": "Lacoste", "scent_family": "Fresh",
     "key_notes": ["Grapefruit", "Tuberose", "Vetiver"], "dupes": ["Ian Darcy LW", "CG SCENT Lacoste White"],
     "gender": "Men", "year_launched": 2011, "concentration": "Eau de Toilette",
     "best_season": "Summer", "best_occasion": "Daytime & sports", "vibe": "Crisp, sporty and fresh",
     **ian_darcy("lw", other_stores=[cg_alt("CG SCENT Lacoste White", "lacoste-white")])},
]
perfumes.sort(key=lambda p: p["id"])


# ---------------------------------------------------------------------------
# 4. API ROUTES
# ---------------------------------------------------------------------------
@app.get("/", tags=["Welcome"])
def home():
    return {
        "message": "Welcome to Sillage PH",
        "endpoints": ["/perfumes", "/perfumes/search?q=", "/perfumes/compare?ids=1,2,3", "/perfumes/{perfume_id}"],
        "website": "/catalog",
        "docs": "/docs",
    }


@app.get("/perfumes", tags=["Perfumes"])
def get_perfumes():
    return {"count": len(perfumes), "perfumes": perfumes}


@app.get("/perfumes/search", tags=["Perfumes"])
def search_perfumes(q: str = Query(..., min_length=1, max_length=100)):
    query = q.strip().casefold()
    if not query:
        raise HTTPException(status_code=422, detail="Enter at least one non-space character.")
    results = []
    for p in perfumes:
        searchable_text = " ".join(
            [p["name"], p["brand"], p["scent_family"], p["gender"], *p["key_notes"], *p["dupes"],
             p["where_to_buy"]["store"]]
        ).casefold()
        if query in searchable_text:
            results.append(p)
    return {"query": q.strip(), "count": len(results), "results": results}


# NOTE: this route must stay ABOVE /perfumes/{perfume_id}, or "compare" is read as an id.
@app.get("/perfumes/compare", tags=["Perfumes"])
def compare_perfumes(ids: str = Query(..., description="2 or 3 perfume ids, e.g. 1,4,15")):
    try:
        wanted = [int(i) for i in ids.split(",") if i.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="ids must be whole numbers separated by commas.")
    if not 2 <= len(wanted) <= 3 or len(set(wanted)) != len(wanted):
        raise HTTPException(status_code=422, detail="Choose 2 or 3 different perfumes.")
    by_id = {p["id"]: p for p in perfumes}
    missing = [i for i in wanted if i not in by_id]
    if missing:
        raise HTTPException(status_code=404, detail=f"Perfume not found: {missing}")
    return {"count": len(wanted), "perfumes": [by_id[i] for i in wanted]}


@app.get("/perfumes/{perfume_id}", tags=["Perfumes"])
def get_perfume(perfume_id: int):
    for p in perfumes:
        if p["id"] == perfume_id:
            return p
    raise HTTPException(status_code=404, detail="Perfume not found.")


# ---------------------------------------------------------------------------
# 5. FRONTEND ROUTES
# ---------------------------------------------------------------------------
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

# Pretty page URLs -> file
PAGES = {"/catalog": "index.html", "/quiz": "quiz.html", "/compare": "compare.html", "/perfume": "perfume.html"}

# Files the pages are allowed to load (anything else is a 404)
STATIC_FILES = {
    "index.html": "text/html", "quiz.html": "text/html", "compare.html": "text/html", "perfume.html": "text/html",
    "style.css": "text/css",
    "config.js": "application/javascript", "app.js": "application/javascript",
    "quiz.js": "application/javascript", "compare.js": "application/javascript",
    "perfume.js": "application/javascript",
}


def _make_page_route(filename):
    return lambda: FileResponse(FRONTEND / filename)


for _path, _file in PAGES.items():
    app.add_api_route(_path, _make_page_route(_file), methods=["GET"], include_in_schema=False)


@app.get("/{filename}", include_in_schema=False)
def static_file(filename: str):
    if filename not in STATIC_FILES:
        raise HTTPException(status_code=404, detail="Not found.")
    return FileResponse(FRONTEND / filename, media_type=STATIC_FILES[filename])
