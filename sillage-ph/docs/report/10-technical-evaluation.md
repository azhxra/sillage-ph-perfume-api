# 10 Technical Evaluation and Limitations

> Current status: the cloud project is now accessible and 25 records are seeded. See [cloud verification update](../cloud-verification.md) for verified results and the remaining private connection setup. Earlier statements below describe the initial implementation session.


The implementation separates routes, validation, data access and seeding. Identity allocation and uniqueness move concurrency protections into PostgreSQL. JSONB sellers preserve frontend compatibility. A reusable client pool plus Supavisor bounds per-runtime connection use, although total connections still scale with concurrent serverless instances.

Persistence is an intended architectural property, not an observed result here. Schema execution, seed idempotence, RLS behavior, network/TLS and transaction-pooler compatibility need live verification. Direct privileged SQL can bypass some nested API validation. Duplicate detection is case-sensitive. Substring search scans the table; catalogue growth needs benchmarks and indexing decisions.

There is no pagination, per-user authorization, rate limiting, audit history, automatic migration deployment or backup verification. The shared write key must remain outside browser code. Full PUT avoids partial-update ambiguity; any future PATCH must atomically update only submitted fields. HTTP/syntax checks cannot prove browser runtime behavior. Cloud configuration and evidence remain the user's next steps.
