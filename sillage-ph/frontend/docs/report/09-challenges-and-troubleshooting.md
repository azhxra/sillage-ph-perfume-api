# 9 Challenges and Troubleshooting

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](../cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


## Nested archive layout

Problem: the expected root index.py was absent. Cause: another archive directory level and API code under api/. Diagnosis: recursive file inventory located api/index.py and sibling frontend/. Solution: work in the actual app directory and add a root import entry point. Result: local index:app imports work and original frontend resolution was confirmed correct.

## No accessible project

Problem: real cloud queries could not run. Cause: the connected Supabase account exposed no projects and no DATABASE_URL was configured. Diagnosis: list_projects returned an empty projects array. Solution: the user selected setup instructions; schema, login and connection steps were documented. Result: cloud checks remain explicitly pending.

## Python environment and network

Problem: venv creation failed during ensurepip and sandboxed pip could not resolve PyPI. Cause: environment bootstrap/network restrictions; the underlying ensurepip cause was not established. Diagnosis: the venv interpreter existed without pip, and package lookup reported DNS failure. Solution: install through base pip with --python .venv using approved network access. Result: pinned dependencies installed.

## Sandboxed TestClient

Problem: local contract tests stalled under sandbox execution. Cause: an execution-environment limitation; the precise mechanism was not established. Diagnosis: the same suite immediately completed outside the sandbox. Solution: run the local suite with approved execution access. Result: ten tests passed.
