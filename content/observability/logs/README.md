# Logging

The data architecture of system events — recognising that logs are an asset only when their structure, cardinality, retention tiers, sampling strategy, and security posture are designed for the questions you'll need to ask of them long after the events that produced them.

**Section:** `observability/` | **Subsection:** `logs/`
**Alignment:** OpenTelemetry | Distributed Systems Observability (Cindy Sridharan) | Honeycomb | Charity Majors — Observability 2.0

---

## What "logging as architecture" actually means

A *primitive* logging approach treats logs as text. The application calls `printf` or `log.info("user logged in")` with a string, the strings accumulate in a file or a stream, and when something goes wrong somebody runs `grep` against the accumulation looking for clues. This works at small scale and stops working at large scale: text logs are unstructured, every team logs differently, queries that should be one-line become regex archaeology, retention is uniform regardless of value, and the storage cost grows linearly with traffic until it becomes the dominant infrastructure expense in the observability stack. The logs exist; the *value* extractable from them is much smaller than their volume suggests.

A *production* logging architecture treats logs as structured data with engineering properties that have to be designed. *Structured logs* — JSON or similar key-value records — let queries do exact field matches and aggregations rather than string parsing. *Cardinality* — the number of distinct values a field can take — is recognised as the resource constraint that determines whether a logging system stays performant or collapses into nightly index rebuilds. *Retention tiers* match the data's value over time: recent logs in hot storage for fast queries, older logs in warm storage for occasional investigation, archive in cold storage for compliance. *Sampling* is applied where the value of every-event capture is dominated by the cost of every-event storage. *Security surfaces* are recognised explicitly: logs leak credentials, PII, internal architecture details — and require redaction at the source, encrypted transport, controlled access, and retention limits aligned with regulatory requirements.

The architectural shift is not "we set up centralized logging." It is: **logs are a data architecture with cardinality, retention, sampling, and security as first-class design properties — and treating logs as text-streams-to-tail is what produces logging systems that cost more than they're worth and answer fewer questions than they should.**

---

## Six principles

### 1. Structured logging is the architectural baseline — string concatenation belongs in the past

A log line written as `log.info("user " + userId + " purchased " + itemId)` produces text that can be grepped but not queried. The same event written as `log.info({event: "purchase", userId, itemId, amount})` produces a structured record where queries like "all purchases by user X in the last hour, aggregated by item" are one-line operations. The cost difference at write time is negligible; the cost difference at query time is enormous, especially as log volume grows and questions become more sophisticated. The architectural discipline is that every log statement produces a structured record (JSON, logfmt, or equivalent), with consistent field names across services and a documented schema. Free-text descriptions still appear — usually as a `message` field — but the structured fields carry the queryable data. This single discipline determines whether the logging system becomes a queryable asset or remains a searchable text archive.

#### Architectural implications

- All log statements emit structured records; libraries (Pino, Logrus, structlog, slf4j with structured layouts) are chosen and configured to enforce structure rather than allow string concatenation.
- A field-name vocabulary is documented and maintained — `userId` not `user_id` not `userid` — so cross-service queries work without normalisation gymnastics.
- Common fields (timestamp, service, environment, request_id, span_id, severity) are added by the logging framework, not by application code, so they're consistent and present.
- The logging library validates that messages are structured at write time — string-only logs are warnings during development and prohibited in production code.

#### Quick test

> Pick a recent investigation in your organisation. Could the question "what was the response time distribution of the checkout service for premium users in EU between 14:30 and 14:45?" be answered with a single query against your logs? If the answer requires regex parsing of message strings, the logging architecture is text-based — and most of the value the logs could provide is locked behind query difficulty.

#### Reference

[Charity Majors — Observability 2.0](https://charity.wtf/2024/07/03/ohh-observability-the-2-0-version/) treats structured logs as the foundational architectural shift that distinguishes modern observability from log-tailing. [OpenTelemetry — Logs Specification](https://opentelemetry.io/docs/specs/otel/logs/) provides the canonical structured-log data model with cross-language consistency.

---

### 2. Cardinality is the resource constraint — high-cardinality fields are both the most useful and the most dangerous

Cardinality — the number of distinct values a field can take — is the property that determines a logging system's performance. A field like `severity` has cardinality of about 5 (debug, info, warn, error, fatal) and indexes cheaply. A field like `userId` has cardinality equal to the number of users — millions, in many systems — and is the field that lets you investigate a specific user's experience but costs significantly more to index. A field like `request_id` (one value per request) has cardinality equal to total request count and, indexed naively, will overwhelm any logging backend. The architectural discipline is to recognise high-cardinality fields as the most valuable for investigation (they let you slice to specific users, requests, or sessions) AND the most expensive to handle, and to make the trade-offs deliberately: which high-cardinality fields are indexed for fast query, which are stored but not indexed (queryable but slow), which are stripped or sampled.

#### Architectural implications

- Each log field has a documented expected cardinality — low (severity, environment), medium (service name, region), high (userId, accountId), unbounded (request_id, trace_id) — and the indexing strategy matches.
- High-cardinality fields are indexed selectively based on investigation value: `userId` typically yes, `request_id` typically as part of trace correlation rather than primary index.
- Unbounded-cardinality fields (anything generated per request or per event) are stored as data but not indexed individually; trace correlation and sampling provide the query path instead.
- Cardinality drift is monitored: a field that was low-cardinality may become high-cardinality if developers start putting variable values into it (e.g. `endpoint` becomes `/users/123/profile` instead of `/users/:id/profile`) — and the logging backend's degradation is the late signal.

#### Quick test

> Pick the highest-cardinality field in your logs. What's its distinct-value count, and what's the indexing strategy for it? If the answer is "we don't track that and it's indexed by default," the logging system is one volume spike or one schema change away from cardinality-driven cost or performance crisis.

#### Reference

[Honeycomb — Cardinality and the Limits of Observability](https://www.honeycomb.io/blog/cardinality-the-secret-sauce-of-observability) treats cardinality as the central architectural constraint of observability backends. The conceptual framing transfers across vendors (Datadog, Splunk, Elasticsearch) — the underlying physics of indexing cost is consistent.

---

### 3. Retention tiers match data value over time — not all logs deserve the same storage class

Logs from the last 24 hours are operationally critical: an incident that's happening now or just ended needs them at fast-query latency. Logs from the last week are valuable for trend analysis and post-incident investigation; query latency can be slower. Logs from the last quarter are valuable for occasional retrospective analysis; offline query is acceptable. Logs from a year ago are typically retained only for compliance or specific investigations; the storage cost should be minimised. Treating all logs uniformly — same storage class, same query latency, same cost per byte — overpays for old logs and underprovides for recent ones. The architectural discipline is to define retention tiers (hot / warm / cold / archive), with documented criteria for movement between tiers, and to monitor the distribution: a system where 90% of logs are in hot storage is overpaying; a system where 90% are in cold storage may be unable to investigate yesterday's incident at the speed the operational tempo requires.

#### Architectural implications

- Retention tiers are documented with storage class, query latency, cost per byte per day, and movement criteria (typically time-based: hot for 0-7 days, warm for 7-30, cold for 30-365, archive for compliance retention).
- The pipeline that moves logs between tiers runs continuously and is monitored — stuck migrations are a known failure mode.
- Query interfaces are aware of tier boundaries: a query for last 24 hours uses the hot index; a query for last quarter spans warm and cold and indicates expected latency to the user.
- Retention is bounded by regulatory minimums and maximums — keeping logs longer than necessary is both a cost and a security risk.

#### Quick test

> What proportion of your logs are in hot storage right now? If the answer is "all of them" or "we don't tier," the logging cost is higher than it needs to be — and the next time the volume doubles, the cost will too. If the answer is "none of them" or "we don't keep recent logs hot," operational queries are slower than they should be — and incident response is bottlenecked on log access.

#### Reference

[Distributed Systems Observability — Cindy Sridharan](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) treats retention tiering as a primary cost-and-performance lever in the logging architecture. AWS, GCP, and Azure all offer log-storage products with tiering primitives (S3 storage classes, GCS storage classes, Azure Blob tiers); the architectural discipline applies regardless of the underlying platform.

---

### 4. Sampling preserves signal at scale — capturing every event is sometimes the wrong default

At small volumes, capturing every log event is fine; the cost is negligible and the completeness is valuable. At large volumes — millions of events per second — capturing every event becomes the dominant infrastructure expense, often without proportional value: routine successful requests look the same as one another, and the 99,999th identical success log doesn't tell you more than the first one did. Sampling — recording a representative subset rather than every event — preserves the statistical signal while bounding cost. The architectural discipline is to apply sampling deliberately: not uniformly (which loses rare-but-important events) but with strategy (keep all errors, keep all slow tails, keep a representative sample of routine traffic, keep all events for a sampled set of users for full-trace investigation). The wrong default is everything-or-nothing; the right discipline is per-event-type policy.

#### Architectural implications

- Sampling strategy is documented per log category: error logs typically 100%, slow-tail traffic 100% (above latency threshold), routine traffic 1-10% representative sample, audit/security logs typically 100% with separate retention.
- The sampling decision is recorded in the log record itself (a `sampled: true/false` field, or a `sample_rate: 1/N` field) so analysts know how to interpret aggregates.
- Reservoir sampling (keep the first N, then probabilistic replacement) and stratified sampling (sample independently within categories) are common implementations; the choice depends on what aggregates need to be accurate.
- Sampling rate and strategy are revisited as traffic patterns shift — a sample rate that was right at last year's volume may be wasteful today.

#### Quick test

> Pick the highest-volume log source in your system. What's its sampling strategy, and what would the cost be at full capture vs current sampling? If the answer is "no sampling, full capture," the cost may be appropriate for the volume — or it may be 10x higher than it needs to be without proportional value. If the answer is "uniform random 1%," rare-but-important events are being missed at the same rate as routine ones.

#### Reference

[OpenTelemetry — Sampling](https://opentelemetry.io/docs/concepts/sampling/) covers the sampling primitives; the same conceptual framework applies to logs as to traces. [Honeycomb — Dynamic Sampling](https://www.honeycomb.io/blog/dynamic-sampling-by-example) treats sampling as a first-class architectural concern with concrete patterns for stratified-and-error-preserving sampling.

---

### 5. Logs, metrics, and traces are different signals — choose deliberately rather than logging everything

A common pattern: developers, faced with the question "should this be a log, a metric, or a trace?", default to logging everything. The result is a logging system carrying signals that should be metrics (counts, rates, distributions) or traces (request-spanning timing data) — and the logging system pays the storage cost for data that's expensive to query as logs and would be cheap as the appropriate signal. *Logs* are the right primitive for discrete events with rich context — what happened, with what arguments, in what state. *Metrics* are the right primitive for aggregated numerical signals — counts, rates, distributions over time, with low cardinality dimensions. *Traces* are the right primitive for cross-service request flow — what happened to this request as it moved through the system. The three are complementary; the discipline is to choose the right primitive per signal rather than defaulting to logs and forcing the others to live in the logging pipeline.

#### Architectural implications

- Each instrumentation point is classified: is this an event with rich context (log), an aggregated number (metric), or part of a request flow (trace)?
- Numerical signals (request count, latency distribution, error rate) emit metrics, not log lines that the metrics system parses; the parse-from-logs pattern works but is wasteful.
- Request-spanning signals (this request took N ms, traversed services A, B, C) emit traces; the same data captured as logs requires manual correlation by request_id later.
- Logs themselves are instrumented for correlation: every log line carries the trace_id and span_id of the active operation, so logs can be correlated with traces during investigation.

#### Quick test

> Pick the largest log source in your system. What proportion of its logs are events with rich context (genuinely log-like) vs aggregated numbers that should be metrics vs request-flow data that should be traces? If the answer is "mostly numbers and request data," the logging system is paying the price of carrying signals that belong in cheaper, more queryable systems.

#### Reference

[Distributed Systems Observability — Cindy Sridharan](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) treats the three-pillar model (metrics, logs, traces) as complementary primitives with different cost profiles and different query characteristics. [Charity Majors — Observability 2.0](https://charity.wtf/2024/07/03/ohh-observability-the-2-0-version/) extends this framing toward "wide events" that subsume traditional logs at sufficient cardinality.

---

### 6. Logs are a security surface — credentials, PII, and architectural details all leak through them

A log line that contains "user 12345 logged in with password ZXY" leaks credentials. A log line that contains a customer email address, social security number, or medical record leaks PII. A log line that contains "connecting to internal-db-prod-replica-3.us-east-1.amazonaws.com" leaks internal architecture. A stack trace leaks code paths and library versions to anyone with log access. The logging system collects all of this — accidentally, but at scale — and stores it for the retention period. The architectural response is layered: redaction at the source (the logging library or framework strips or hashes sensitive fields before emit); transport encryption (logs travel encrypted between application, ingestion, storage); access control (not everyone with cluster access has log access; log access is audited); retention limits matched to data sensitivity (PII subject to right-to-erasure has different retention than performance traces). Treating logs as a security surface is not optional; the alternative is an audit finding waiting to happen.

#### Architectural implications

- Redaction happens at the logging library or framework level, not at storage — sensitive fields never enter the log stream in unredacted form. Common patterns: mask credit card numbers as last-4, hash emails, replace SSN with `<redacted>`, drop password fields entirely.
- Transport between application, ingestion, and storage is encrypted (TLS); ingestion endpoints are authenticated.
- Log access is controlled and audited: who can query which logs is documented, queries are logged for forensic review, sensitive log streams (audit logs, security logs) have separate access policies.
- Retention is bounded both above (regulatory minimums for compliance) and below (data subject to right-to-erasure or limited-retention requirements has aggressive expiry); retention policy is documented per log category.

#### Quick test

> Pick a sample of recent logs from your production system. Are there fields that would be problematic if leaked — emails, names, identifiers that map to individuals, internal hostnames, stack traces with sensitive paths? If yes, what's the redaction at the source, what's the transport encryption, and who has access? If the answers are "we haven't audited that," the logging system is a latent security incident — the next leaked credential or doxxing event will surface what should have been redacted at write time.

#### Reference

[OWASP — Logging Vocabulary Cheat Sheet](https://owasp.org/www-project-cheat-sheets/cheatsheets/Logging_Vocabulary_Cheat_Sheet.html) and [OWASP — Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) cover the security and PII concerns at the practitioner level. The architectural framing of logs as security surface is treated extensively in regulatory guidance (GDPR, HIPAA, PCI DSS) — each framework has specific log-handling requirements that translate to engineering constraints.

---

## Architecture Diagram

The diagram below shows the canonical logging architecture: structured log emission at applications with redaction at source; transport over encrypted channels; ingestion with cardinality validation and sampling; storage with retention tiers (hot / warm / cold / archive); query layer aware of tier boundaries; access control and audit; correlation primitives (trace_id, span_id, request_id) tying logs to traces and metrics.

---

## Common pitfalls when adopting logging-as-architecture thinking

### ⚠️ String-concatenation logging at scale

Logs are emitted as `"user " + userId + " did " + action`. Queries become regex archaeology. Cross-service investigation requires custom parsers per service. The logging system's value is much lower than its volume suggests.

#### What to do instead

Structured logs as the architectural baseline. Field names consistent across services. Free-text in a `message` field; queryable data in structured fields. Logging libraries enforce structure at write time.

---

### ⚠️ Unbounded cardinality from naive endpoint logging

The `endpoint` field captures `/users/123/profile` and `/users/124/profile` as distinct values. Each unique URL is a new field value. Logging backend's index grows linearly with traffic. Performance degrades; cost surprises arrive.

#### What to do instead

Path templates, not concrete URLs: `/users/:id/profile`. High-cardinality identifiers (user IDs, request IDs) belong in their own dedicated fields with indexing strategies that match their cardinality.

---

### ⚠️ Uniform retention regardless of value

All logs are kept in hot storage for 90 days. The cost is dominated by 60-day-old logs that are queried once a quarter. Newer logs that need fast access compete for the same resources as old ones.

#### What to do instead

Retention tiers matched to data value over time. Hot for recent logs, warm for last month, cold for last quarter, archive for compliance. Movement between tiers automated, distribution monitored.

---

### ⚠️ No sampling at high volume

Every event is captured. The 99,999th identical success log goes through the same pipeline as the first one. Storage cost grows linearly with traffic; signal-to-noise drops as identical events accumulate.

#### What to do instead

Per-category sampling. Errors at 100%, slow tails at 100%, routine traffic at representative sample (1-10%), audit/security at 100% with separate retention. Sample rate recorded in each log so aggregates are correctly interpreted.

---

### ⚠️ Logs leak credentials and PII

A debug log line includes the request body. The body contains a password. Or an email. Or a credit card. Or a session token. The log persists for 90 days. The next breach is enabled by the log.

#### What to do instead

Redaction at the source — the logging library strips sensitive fields before emit. Transport encrypted. Access controlled and audited. Retention bounded both above (compliance minimums) and below (subject-deletion requirements).

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | All log statements emit structured records with consistent field-name vocabulary across services ‖ Structure at write time, not parse time. Libraries enforce structure. Field names normalised across the codebase. The logs become queryable. | ☐ |
| 2 | Common correlation fields (trace_id, span_id, request_id) are added by the logging framework, not by application code ‖ Consistency comes from infrastructure, not discipline. Every log line carries the correlation context of the operation that produced it. | ☐ |
| 3 | Each log field has documented expected cardinality with matching indexing strategy ‖ Cardinality is the resource constraint. Low-cardinality fields index cheaply; high-cardinality indexed selectively for investigation value; unbounded-cardinality stored but not individually indexed. | ☐ |
| 4 | Cardinality drift is monitored — fields whose distinct-value count grows suddenly are flagged ‖ The logging backend's degradation is the late signal. Monitoring distinct-value counts catches the drift early, before performance crisis. | ☐ |
| 5 | Retention tiers (hot / warm / cold / archive) are documented with movement criteria; pipeline runs continuously ‖ Storage cost matches data value over time. Recent logs in fast storage; older logs progressively cheaper; compliance-required retention in archive. | ☐ |
| 6 | Sampling is applied per log category — errors and tails at 100%, routine at representative sample ‖ Capturing every routine event is wasteful at scale; capturing zero loses rare-but-important events. Per-category strategy preserves signal while bounding cost. | ☐ |
| 7 | Sample rate is recorded in each log record so aggregates are correctly interpreted ‖ Without the rate in the record, downstream analytics produce silent under-counts of categories that were sampled. The rate field is not optional. | ☐ |
| 8 | Each instrumentation point is classified — log (event), metric (aggregate number), trace (request flow) — and uses the right primitive ‖ The three pillars are complementary. Default-to-logging puts data in the wrong system; cost is paid in storage and query difficulty. The discipline is to choose deliberately. | ☐ |
| 9 | Sensitive fields are redacted at the source — the logging library or framework, not at storage ‖ Once a credential or PII enters the log stream, retention starts a clock on a security incident. Redaction at source means sensitive data never enters the stream. | ☐ |
| 10 | Log access is controlled and audited; transport is encrypted; retention is bounded both above and below ‖ Logs are a security surface. Access matches least-privilege; transport assumes hostile network; retention matches regulatory and right-to-erasure requirements. | ☐ |

---

## Related

[`observability/metrics`](../metrics) | [`observability/traces`](../traces) | [`observability/sli-slo`](../sli-slo) | [`observability/incident-response`](../incident-response) | [`technology/devops`](../../technology/devops) | [`security/application-security`](../../security/application-security)

---

## References

1. [OpenTelemetry — Logs Specification](https://opentelemetry.io/docs/specs/otel/logs/) — *opentelemetry.io*
2. [Charity Majors — Observability 2.0](https://charity.wtf/2024/07/03/ohh-observability-the-2-0-version/) — *charity.wtf*
3. [Honeycomb](https://www.honeycomb.io/) — *honeycomb.io*
4. [Distributed Systems Observability (Cindy Sridharan)](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) — *oreilly.com*
5. [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — *sre.google*
6. [ELK Stack (Elastic)](https://www.elastic.co/elastic-stack/) — *elastic.co*
7. [Datadog](https://www.datadoghq.com/) — *datadoghq.com*
8. [Brendan Gregg Performance Tools](https://www.brendangregg.com/perf.html) — *brendangregg.com*
9. [OpenTelemetry — Sampling](https://opentelemetry.io/docs/concepts/sampling/) — *opentelemetry.io*
10. [Google SRE Workbook](https://sre.google/workbook/table-of-contents/) — *sre.google*
