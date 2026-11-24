# API usage

Public GET routes require no key:

- `/perfumes` returns `{count,perfumes}`. Optional gender, scent_family and sort parameters filter/order in SQL. Sort accepts price_asc or price_desc.
- `/perfumes/search?q=Ian` returns `{query,count,results}`. Search is a case-insensitive literal substring match, including nested stores, notes and dupes.
- `/perfumes/compare?ids=2,1` returns `{count,perfumes}` in requested order. Supply 2 or 3 distinct integer IDs.
- `/perfumes/1` returns the complete object; absent IDs return 404.
- `/health` performs a real table query; 200 connected or 503 unavailable.

POST /perfumes requires X-API-Key and the complete input body; it returns 201 with a database-assigned ID. PUT /perfumes/{id} requires the key and full replacement body and returns 200. Omitted other_stores defaults to []; other required fields must be present. DELETE /perfumes/{id} requires the key and returns an empty 204. Missing update/delete IDs return 404. PATCH is not implemented.

Create a safe request file from a public record, with a new unique name:

```powershell
$body = Invoke-RestMethod "$env:API_BASE_URL/perfumes/1"
$body.PSObject.Properties.Remove('id')
$body.name = 'My unique demonstration perfume'
$body | ConvertTo-Json -Depth 8 | Set-Content sample-request.json
curl.exe -i -X POST "$env:API_BASE_URL/perfumes" -H "Content-Type: application/json" -H "X-API-Key: $env:ADMIN_API_KEY" --data-binary '@sample-request.json'
```

Use the returned ID for subsequent GET, PUT and DELETE. Never alter a seed record for a demonstration. Keep expanded key headers out of screenshots. Variables in .env are loaded by Python, not automatically by PowerShell; set the shell environment privately before running curl. The Python test runner reads .env for you.

Open /docs for the complete generated input schema. Real local failure examples and pending cloud examples appear in report section 6.
