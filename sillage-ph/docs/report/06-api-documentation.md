# 6 API Documentation and Usage Guide

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](../cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


The endpoint inventory is in section 2; runnable usage is in ../05-api-usage.md. GET is public; POST/PUT/DELETE require X-API-Key. /docs exposes the generated body/query schema. A new record's ID is database-assigned and must be used for subsequent writes.

Actual local failure: GET /health without DATABASE_URL returns 503:

```json
{"detail":"Database unavailable"}
```

Actual contract test: authenticated POST /perfumes with an empty object returns 422:

```json
{"detail":"Invalid request data."}
```

Actual contract test: POST /perfumes without a key returns 401:

```json
{"detail":"Invalid or missing API key."}
```

Successful local route-contract checks use a test-only key and mocked database results. They do not prove persistence. No real cloud create response was observed. After setup, add sanitized POST/GET/PUT/DELETE request/response evidence using a unique temporary record and remove it afterwards.

[SCREENSHOT: real create and get responses, secret headers hidden]
[SCREENSHOT: real replacement and deletion responses]
