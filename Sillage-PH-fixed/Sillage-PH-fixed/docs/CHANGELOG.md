# Repair summary

- Reconstructed `api/index.py` because both uploaded Python index files were root re-export stubs. Added public reads, health, admin-only CRUD, signup/login, current account and authenticated favorite operations; frontend assets are allowlisted.
- Reconciled `public.favorites` versus `public.perfume_favorites`, added creator attribution on admin inserts, and required real role records; migration provisions roles and public profiles automatically while preserving existing admin assignments.
- Added non-destructive transaction-based reconciliation of the supplied schema, explicit delete actions, unique brand/name constraint, search trigger, indexes, least-privilege grants and owner-based favorites RLS. The SQL has not been executed against the user's Supabase database.
- Seed insertion now supports GENERATED ALWAYS identity. No fake live writes or account sessions in fallback mode.
- Added full ERD visualizer with all 19 perfume attributes, five public entities plus auth.users, seven relationships, zoom and connected-table highlighting. Cardinalities are 1 to 0..1 or 0..many except optional perfume creator (0..1 to 0..many).
- Changed live integration tests to bearer-token login and account isolation, updated incorrect seed search expectation, and added an independent preview contract suite.
- Dependency ranges replace the uploaded lock file; a fully resolved lock is not asserted because package download was unavailable here. Use the full requirements for deployment.
- Verified Python compilation, JavaScript syntax, and eight no-database HTTP contract tests; database operations in authorization and favorites contract checks were mocked. The live driver-dependent suite and SQL migration were not run because Psycopg and a private database connection were unavailable. Browser navigation over localhost was blocked by the execution environment; see any additional browser fixture results in `verified-local.txt`.
