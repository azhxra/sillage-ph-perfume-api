from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="Sillage PH Perfume API", description="20 luxury and designer perfumes with affordable Philippine alternatives.", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["GET"], allow_headers=["*"])

perfumes = [{'id': 1,
  'name': 'Baccarat Rouge 540',
  'brand': 'Maison Francis Kurkdjian',
  'scent_family': 'Amber',
  'key_notes': ['Saffron', 'Jasmine', 'Cedar'],
  'dupes': ['Ian Darcy 540'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/br/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 2,
  'name': 'English Pear & Freesia',
  'brand': 'Jo Malone London',
  'scent_family': 'Fruity',
  'key_notes': ['Pear', 'Freesia', 'Patchouli'],
  'dupes': ['Ian Darcy EP'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ep/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 3,
  'name': 'Bright Crystal',
  'brand': 'Versace',
  'scent_family': 'Floral',
  'key_notes': ['Yuzu', 'Peony', 'Musk'],
  'dupes': ['Ian Darcy BC'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/bc/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 4,
  'name': 'Black Opium',
  'brand': 'Yves Saint Laurent',
  'scent_family': 'Gourmand',
  'key_notes': ['Coffee', 'White flowers', 'Vanilla'],
  'dupes': ['CG SCENT Black Opium'],
  'dupe_price_php': 'From PHP 450 (check bottle size)',
  'where_to_buy': {'store': 'CG SCENT Philippines',
                   'url': 'https://cgscent.com/',
                   'note': 'Seller-listed inspired fragrance; check current stock, size and '
                           'price.'}},
 {'id': 5,
  'name': 'Good Girl',
  'brand': 'Carolina Herrera',
  'scent_family': 'Amber',
  'key_notes': ['Jasmine', 'Tuberose', 'Tonka bean'],
  'dupes': ['CG SCENT Good Girl'],
  'dupe_price_php': 'From PHP 450 (check bottle size)',
  'where_to_buy': {'store': 'CG SCENT Philippines',
                   'url': 'https://cgscent.com/',
                   'note': 'Seller-listed inspired fragrance; check current stock, size and '
                           'price.'}},
 {'id': 6,
  'name': 'Coco',
  'brand': 'Chanel',
  'scent_family': 'Amber',
  'key_notes': ['Rose', 'Clove', 'Sandalwood'],
  'dupes': ['CG SCENT Coco Chanel'],
  'dupe_price_php': 'From PHP 450 (check bottle size)',
  'where_to_buy': {'store': 'CG SCENT Philippines',
                   'url': 'https://cgscent.com/',
                   'note': 'Seller-listed inspired fragrance; check current stock, size and '
                           'price.'}},
 {'id': 7,
  'name': 'Light Blue',
  'brand': 'Dolce & Gabbana',
  'scent_family': 'Fresh',
  'key_notes': ['Lemon', 'Apple', 'Cedar'],
  'dupes': ['Ian Darcy DG'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/dg/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 8,
  'name': 'Omnia Amethyste',
  'brand': 'Bvlgari',
  'scent_family': 'Floral',
  'key_notes': ['Iris', 'Rose', 'Heliotrope'],
  'dupes': ['Ian Darcy BA'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ba/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 9,
  'name': 'Nectarine Blossom & Honey',
  'brand': 'Jo Malone London',
  'scent_family': 'Fruity',
  'key_notes': ['Cassis', 'Acacia honey', 'Peach'],
  'dupes': ['Ian Darcy NB'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/nb/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 10,
  'name': 'Blackberry & Bay',
  'brand': 'Jo Malone London',
  'scent_family': 'Fruity',
  'key_notes': ['Blackberry', 'Bay leaves', 'Cedar'],
  'dupes': ['Ian Darcy BB'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/bb/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 11,
  'name': 'Éclat d’Arpège',
  'brand': 'Lanvin',
  'scent_family': 'Floral',
  'key_notes': ['Lilac', 'Green tea', 'Musk'],
  'dupes': ['Ian Darcy EC'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ec/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 12,
  'name': 'Weekend for Women',
  'brand': 'Burberry',
  'scent_family': 'Floral',
  'key_notes': ['Mandarin', 'Hyacinth', 'Sandalwood'],
  'dupes': ['Ian Darcy BW'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/bw/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 13,
  'name': 'Aventus',
  'brand': 'Creed',
  'scent_family': 'Woody',
  'key_notes': ['Pineapple', 'Birch', 'Oakmoss'],
  'dupes': ['Ian Darcy CA'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ca/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 14,
  'name': 'Bleu de Chanel',
  'brand': 'Chanel',
  'scent_family': 'Woody',
  'key_notes': ['Grapefruit', 'Incense', 'Cedar'],
  'dupes': ['Ian Darcy CB'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/cb/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 15,
  'name': 'Eros',
  'brand': 'Versace',
  'scent_family': 'Fresh',
  'key_notes': ['Mint', 'Green apple', 'Tonka bean'],
  'dupes': ['Ian Darcy ER'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/er/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 16,
  'name': 'Acqua di Giò',
  'brand': 'Giorgio Armani',
  'scent_family': 'Fresh',
  'key_notes': ['Bergamot', 'Marine accord', 'Cedar'],
  'dupes': ['Ian Darcy AG'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ag/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 17,
  'name': 'Fucking Fabulous',
  'brand': 'Tom Ford',
  'scent_family': 'Leather',
  'key_notes': ['Clary sage', 'Almond', 'Leather'],
  'dupes': ['Ian Darcy FF'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/ff/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 18,
  'name': 'Pour Homme Extrême',
  'brand': 'Bvlgari',
  'scent_family': 'Woody',
  'key_notes': ['Grapefruit', 'Tea', 'Vetiver'],
  'dupes': ['Ian Darcy BE'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/be/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 19,
  'name': 'L’Eau d’Issey Pour Homme',
  'brand': 'Issey Miyake',
  'scent_family': 'Fresh',
  'key_notes': ['Yuzu', 'Nutmeg', 'Sandalwood'],
  'dupes': ['Ian Darcy IM'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/im/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}},
 {'id': 20,
  'name': 'L.12.12 Blanc',
  'brand': 'Lacoste',
  'scent_family': 'Fresh',
  'key_notes': ['Grapefruit', 'Tuberose', 'Vetiver'],
  'dupes': ['Ian Darcy LW'],
  'dupe_price_php': 'PHP 450 / 100 ml (reference price)',
  'where_to_buy': {'store': 'Ian Darcy Philippines',
                   'url': 'https://iandarcyfragrance.com/product/lw/',
                   'note': 'Philippine listing; check current stock and price. Pairing is a '
                           'community comparison.'}}]

@app.get("/", tags=["Welcome"])
def home():
    return {"message": "Welcome to Sillage PH", "endpoints": ["/perfumes", "/perfumes/search", "/perfumes/{perfume_id}"], "website": "/catalog", "docs": "/docs"}

@app.get("/perfumes", tags=["Perfumes"])
def get_perfumes():
    return {"count": len(perfumes), "perfumes": perfumes}

@app.get("/perfumes/search", tags=["Perfumes"])
def search_perfumes(q: str = Query(..., min_length=1, max_length=100)):
    query = q.strip().casefold()
    if not query:
        raise HTTPException(status_code=422, detail="Enter at least one non-space character.")
    results = []
    for perfume in perfumes:
        searchable_text = " ".join([perfume["name"], perfume["brand"], perfume["scent_family"],
                                   *perfume["key_notes"], *perfume["dupes"], perfume["where_to_buy"]["store"]]).casefold()
        if query in searchable_text:
            results.append(perfume)
    return {"query": q.strip(), "count": len(results), "results": results}

@app.get("/perfumes/{perfume_id}", tags=["Perfumes"])
def get_perfume(perfume_id: int):
    for perfume in perfumes:
        if perfume["id"] == perfume_id:
            return perfume
    raise HTTPException(status_code=404, detail="Perfume not found.")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/catalog", include_in_schema=False)
def catalog():
    return FileResponse(FRONTEND / "index.html")

@app.get("/style.css", include_in_schema=False)
def stylesheet():
    return FileResponse(FRONTEND / "style.css", media_type="text/css")

@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(FRONTEND / "app.js", media_type="application/javascript")
