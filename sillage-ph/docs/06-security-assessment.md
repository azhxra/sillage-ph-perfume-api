# Security and reliability assessment

GET is public. POST, PUT and DELETE require X-API-Key checked against ADMIN_API_KEY using secrets.compare_digest. Missing configuration fails closed with 401. Encoding both strings permits safe comparison of non-ASCII headers. The shared key identifies administrator clients; there is no individual-user account system, rate limit or audit log. Use HTTPS, rotate compromised credentials through environment configuration and keep the key outside the public browser.

Pydantic forbids unknown fields, rejects text/integer coercion, trims strings, enforces lengths, list bounds, enums and ranges, and validates HTTPS URLs with hosts. PUT replaces the full body. Omitted other_stores becomes []. Clients cannot choose IDs. Validation responses contain only a generic detail string, excluding input values. SQL adds constraints but does not duplicate every nested JSON rule; privileged direct writes can bypass API validation.

Status codes: 200 read/update; 201 create; 204 delete; 401 unauthorized; 404 absent; 409 unique conflict; 422 invalid input; 503 connection/pool unavailable; 500 unexpected query/application failure. /health maps any failed real table query to 503. Errors return clean `{detail: ...}` JSON. Real exceptions remain in server logs; restrict log access because traces may contain SQL, data or hostnames.

SQL binds values as parameters, uses fixed model field names for identifiers and enum-controlled ordering. Search metacharacters are literal. CORS uses explicit ALLOWED_ORIGINS; no configuration means no cross-origin browser clients. Wildcards are ignored. Same-origin frontend calls work. Methods are GET, POST, PUT and DELETE; headers are Content-Type and X-API-Key. CORS does not authenticate requests.

The Supabase table enables RLS, revokes anon/authenticated grants and permits only the dedicated backend login through its policy. The backend uses TLS through Supavisor. It needs a database login, not a Supabase service-role API key. The browser receives neither credential. The project administrator remains privileged and can bypass ordinary RLS restrictions.

.gitignore excludes .env variants, key files, service-account JSON, virtual environments and Vercel local configuration. .env.example has names and empty values only. The archive has no .git directory, so tracked-file checks cannot be performed here. After initializing/opening the real checkout, run git status, git check-ignore and inspect the staged diff before committing.

Local contract results and live-run status are separate. Cloud advisors, Data API denial, actual SQL constraints, seeding, persistence and deployment remain unverified until setup. Mocked tests do not establish cloud security.
