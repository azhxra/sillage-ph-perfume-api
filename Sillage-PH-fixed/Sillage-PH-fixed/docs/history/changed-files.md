# Files created or changed

Paths are relative to the application root, the directory containing requirements.txt. Frontend files and vercel.json were unchanged. Generated local environments, caches and ignored logs are not source deliverables.

- `api/index.py` — Changed: database-backed routes, write-key authentication, clean errors and health.
- `api/database.py` — Created: reusable PostgreSQL pool and parameterized database operations.
- `api/models.py` — Created: strict input models and domain validation.
- `api/__init__.py` — Created: API package marker.
- `index.py` — Created: local/Vercel application entry point.
- `seed_data.py` — Created: original 25 records and helpers, outside the runtime request path.
- `seed.py` — Created: idempotent seed insertion and safe sequence advancement.
- `sql/schema.sql` — Created: table, constraints, indexes, search trigger, backend role and RLS.
- `.env.example` — Created: variable names with no real credentials.
- `.gitignore` — Created: excludes local secrets, keys, environments, caches and logs.
- `requirements.txt` — Changed: pinned database, validation, environment and HTTP dependencies.
- `requirements-dev.txt` — Created: application requirements plus the local HTTP test dependency.
- `requirements-lock.txt` — Created: exact installed dependency inventory.
- `tests/test_local.py` — Created: ten local contract and failure-path tests.
- `tests/run_api_tests.py` — Created: live HTTP runner, cleanup and manual persistence checkpoints.
- `README.md` — Created: application root, commands and setup/status links.
- `docs/01-existing-api-assessment.md` — Created: original behavior and endpoint inventory.
- `docs/02-database-design.md` — Created: PostgreSQL field definitions, validation and data diagram.
- `docs/03-architecture.md` — Created: system diagram and five request-flow diagrams.
- `docs/04-database-setup.md` — Created: exact user-run Supabase and local setup steps.
- `docs/05-api-usage.md` — Created: endpoint usage and credential-safe command examples.
- `docs/06-security-assessment.md` — Created: validation, errors, authentication and credential assessment.
- `docs/07-deployment.md` — Created: Vercel steps, ten verification checks and screenshot placements.
- `docs/local-test-results.md` — Created: actual local contract and HTTP smoke results.
- `docs/test-results.md` — Created: actual live runner result, blocked by unconfigured database.
- `docs/secret-scan.md` — Created: credential pattern scan, runtime seed check and Git limitations.
- `docs/report/01-executive-summary.md` — Created: 1 Executive Summary; actual results and pending evidence clearly identified.
- `docs/report/02-existing-api-assessment.md` — Created: 2 Existing API Assessment; actual results and pending evidence clearly identified.
- `docs/report/03-database-design.md` — Created: 3 Database Design and Data Model; actual results and pending evidence clearly identified.
- `docs/report/04-system-architecture.md` — Created: 4 System Architecture and Integration Design; actual results and pending evidence clearly identified.
- `docs/report/05-implementation-details.md` — Created: 5 Implementation Details; actual results and pending evidence clearly identified.
- `docs/report/06-api-documentation.md` — Created: 6 API Documentation and Usage Guide; actual results and pending evidence clearly identified.
- `docs/report/07-testing-methodology.md` — Created: 7 Testing Methodology and Results; actual results and pending evidence clearly identified.
- `docs/report/08-deployment-and-environment.md` — Created: 8 Deployment and Environment Configuration; actual results and pending evidence clearly identified.
- `docs/report/09-challenges-and-troubleshooting.md` — Created: 9 Challenges and Troubleshooting; actual results and pending evidence clearly identified.
- `docs/report/10-technical-evaluation.md` — Created: 10 Technical Evaluation and Limitations; actual results and pending evidence clearly identified.
- `docs/report/11-conclusion-and-reflection.md` — Created: 11 Conclusion and Reflection; actual results and pending evidence clearly identified.
- `docs/report/12-references.md` — Created: 12 References; actual results and pending evidence clearly identified.
- `docs/report/13-appendices.md` — Created: 13 Appendices Index; actual results and pending evidence clearly identified.
- `docs/changed-files.md` — Created: this one-line-per-file inventory.

- `docs/cloud-verification.md` — Created: actual cloud schema, seed, role and advisor results; remaining connection prerequisite.
