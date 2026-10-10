# Sillage PH

Luxury perfumes and their affordable Philippine alternatives. FastAPI backend + plain HTML/CSS/JS frontend.

## Folder layout (this whole folder is ONE GitHub repo)

```
sillage-ph/
├── api/index.py        <- the API (the only Python file Vercel runs)
├── frontend/
│   ├── index.html + app.js        Website 1: the collection
│   ├── quiz.html  + quiz.js       Website 2: scent quiz
│   ├── compare.html + compare.js  Website 3: perfume comparing system
│   ├── perfume.html + perfume.js  Detail page (all 14 details)
│   ├── config.js                  API address setting (empty = same site)
│   └── style.css
├── requirements.txt
└── vercel.json
```

## Run locally

```
pip install -r requirements.txt
uvicorn api.index:app --reload
```
Open http://127.0.0.1:8000/catalog (API docs at /docs).

## Upload to GitHub (one folder)

1. On github.com click **New repository**, name it `sillage-ph`, leave it empty, **Create**.
2. On the empty repo page click **uploading an existing file**.
3. Drag the **contents** of the `sillage-ph` folder (api, frontend, requirements.txt, vercel.json, README.md) into the page. Dragging the folder itself also works and keeps the folders.
4. Click **Commit changes**.

## Deploy the API on Vercel and keep the API URL out of your code

1. vercel.com > **Add New > Project** > import the `sillage-ph` repo. Framework: FastAPI (detected from `vercel.json`).
2. **Settings > Environment Variables** > add `ALLOWED_ORIGINS` = your site address(es), comma separated, e.g. `https://sillage-ph.vercel.app`. Redeploy.
   `index.py` reads it with `os.getenv`, so only those websites may call the API.
3. The pages call the API with **no URL typed anywhere** (`config.js` is empty, so they use the same address that served the page). Nothing about the URL is stored in GitHub.

A browser can always see the address it is calling (DevTools > Network); that cannot be hidden. What this setup hides is the URL in your source code, and the environment variable limits who can use the API.

If your professor wants the frontend hosted separately (e.g. GitHub Pages) with only `index.py` on Vercel: put the Vercel URL in `frontend/config.js` (`window.SILLAGE_API_URL = "https://..."`) and set `ALLOWED_ORIGINS` to the Pages address.

## Adding a perfume

Copy any entry in `api/index.py`, give it a new unique `id`, fill the 14 details, and use `ian_darcy("code")` or `cg_scent("slug")` for the seller data. Only add a dupe pairing you can check on the seller's page.
