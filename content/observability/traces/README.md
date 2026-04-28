# Distributed Tracing

The cross-service observability primitive that makes a request's full journey through a distributed system inspectable — recognising that without trace context propagation, logs and metrics are local signals that can't be assembled into the system-level story they imply, and that the trace itself is what turns "the checkout is slow somewhere" into "the checkout is slow because service C's database call is taking 1.4s in the cache-miss path."

**Section:** `observability/` | **Subsection:** `traces/`
**Alignment:** OpenTelemetry | W3C Trace Context | Jaeger | Distributed Tracing in Practice (Parker et al.)

---

## What "distributed tracing" actually means

A *primitive* approach to debugging a distributed system: when a request is slow, the engineer looks at logs from each service and tries to reconstruct what happened by correlating timestamps and request IDs by hand. This works at small scale and breaks down rapidly: services don't all use the same request ID format; clock skew makes timestamp correlation unreliable; the request's path through fan-out and fan-in patterns is opaque; and the engineer ends up reasoning about the system rather than reading a record of what actually happened.

A *production* distributed tracing architecture treats the request's journey as a first-class observable. Each service participating in handling a request creates a *span* — a record of the work it did, with start time, duration, attributes, and references to its parent span (the operation that called it) and child spans (the operations it called). Spans share a *trace ID* — a single identifier carried through the entire request, across every service it touches. The trace ID and span context propagate through HTTP headers, message queue metadata, and RPC envelopes following the [W3C Trace Context](https://www.w3.org/TR/trace-context/) standard. The collected spans are assembled into a *trace*: a tree (or DAG) of all the work that happened to fulfil the original request. The trace becomes the architectural artefact that lets engineers see what actually happened, in what order, with what timing, across services they may not even know about.

The architectural shift is not "we instrumented some services with traces." It is: **distributed tracing is a cross-cutting architectural primitive whose value depends on context propagation working across every service boundary, on sampling preserving the rare events worth investigating, on retention and cardinality being designed for the questions you'll ask, and on correlation with logs and metrics being instrumented at the same time — and treating tracing as an optional add-on per service produces partial traces that hide more than they reveal.**

---

## Six principles

### 1. Trace context propagation is the cross-service architectural primitive — without it, traces are local

The defining property of distributed tracing is *context propagation*: the trace ID and current span ID travel from one service to the next, encoded in the HTTP header, message queue metadata, RPC envelope, or whatever transport mechanism connects services. The receiving service reads the propagated context, creates a child span linked to the parent, and propagates the new context to anything it calls. If propagation works, the trace assembly produces a complete picture of the request's journey. If propagation breaks at any boundary, the trace splits into two unconnected fragments, and the assembly produces partial pictures that hide what actually happened. The architectural discipline is to use a propagation standard ([W3C Trace Context](https://www.w3.org/TR/trace-context/) is the industry default) consistently across every service, every transport, and every team — not as a per-service implementation choice but as a system-level invariant. A single service that drops propagation breaks tracing for every request that touches it.

#### Architectural implications

- W3C Trace Context (`traceparent`, `tracestate` headers) is the propagation standard, used consistently across all services regardless of language, framework, or team.
- The propagation is implemented by the framework or instrumentation library, not by application code — application code that has to handle propagation manually will get it wrong inconsistently.
- Asynchronous boundaries (message queues, event streams, scheduled jobs) propagate context through their own mechanisms (message attributes, event metadata) — without this, async-driven flows produce broken traces.
- The propagation invariant is testable: end-to-end tests that exercise multi-service flows can verify that the resulting trace is complete (no orphan spans, no missing parent links).

#### Quick test

> Pick a multi-service flow in your system. Start at the entry point, follow the trace through to a deep service. Is the trace complete — every service appearing as a span, parent-child relationships preserved, no orphan spans? If the trace is fragmented, propagation is breaking somewhere — and every investigation that depends on tracing through that boundary is currently working with partial information.

#### Reference

[W3C Trace Context Recommendation](https://www.w3.org/TR/trace-context/) is the canonical standard for context propagation; [OpenTelemetry — Context Propagation](https://opentelemetry.io/docs/concepts/context-propagation/) covers the operational implementation across languages and transports. The cross-language consistency is what makes the standard valuable — adopted by Jaeger, Zipkin, Honeycomb, Datadog, and most cloud providers' tracing offerings.

---

### 2. Span structure encodes the architecture — parent/child relationships are the system's story

A span is more than a timed operation; the parent-child relationship between spans encodes the system's call structure. When service A calls service B, which calls service C, the trace shows A's span as the root, B's span as A's child (with timing showing how long the call took including network), and C's span as B's child. When service A makes parallel calls to B and D, the trace shows both as children of A, with overlapping timings revealing the parallelism. When the request enters a fan-out pattern (one operation triggers many child operations), the trace shows the fan-out shape directly. The architectural reading: the trace IS a snapshot of the system's call graph for that request — every architectural decision about sync vs async, fan-out vs sequential, retry-on-failure vs fail-fast is visible in the span structure. The discipline is to instrument spans at the boundaries that matter (service entry, outbound calls, significant internal operations), with attributes (operation name, status, key parameters) that make the architecture readable from the trace.

#### Architectural implications

- Spans are created at architectural boundaries: incoming requests (the root span at service entry), outbound calls (a span for each call to another service), significant internal operations (database queries, cache interactions, complex processing).
- Span attributes (operation name, service name, status, key parameters) are documented and consistent — `db.statement`, `http.method`, `messaging.destination` follow the [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/).
- Parent-child relationships are correct: the span representing the call to service B is the parent of the span service B creates for handling the call; the relationship reflects causation, not just temporal proximity.
- Async patterns are represented honestly: a span that triggers async work and returns immediately should not have its caller's span waiting on it; the async span has its own root or follows-from link rather than a misleading parent-child.

#### Quick test

> Pick a recent investigation that used traces. Did the trace's structure correctly represent the system's call graph — fan-out shown as multiple children, async work shown as separate roots or follows-from, parallelism visible from overlapping timings? If the trace structure was misleading or required interpretation, span instrumentation isn't tracking the architecture correctly — and traces are providing weaker investigation support than they should.

#### Reference

[OpenTelemetry — Spans](https://opentelemetry.io/docs/concepts/signals/traces/) covers the span model and parent-child relationships; [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) standardises attribute names so spans from different services and frameworks are mutually comparable. [Distributed Tracing in Practice — Parker et al.](https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621/) treats span instrumentation patterns at practitioner depth.

---

### 3. Head sampling vs tail sampling — the choice determines which traces survive to be queried

At full instrumentation in a high-traffic system, every request produces a trace, and the resulting trace volume — millions or billions per day — exceeds practical storage and query capacity. Sampling is necessary; the *strategy* determines which traces survive and what they're useful for. *Head sampling* — the decision to keep or drop is made at the trace's start, propagated with the context, and inherited by every span — is simple and efficient: the sampling decision is made once, no trace is partially captured, and the cost is bounded by the sampling rate. The drawback: head sampling is blind to the trace's outcome, so a 1% head sample drops 99% of error traces just like it drops 99% of success traces. *Tail sampling* — the decision is made after the trace completes, based on its outcome (errors, slow tails, specific attributes) — preserves the rare-but-valuable traces. The drawback: tail sampling requires buffering complete traces before deciding, which is more expensive and operationally more complex. The architectural discipline is to choose deliberately based on what the traces are for: head sampling for general observability and statistical analysis; tail sampling for incident investigation where errors and slow tails are the queries that matter most; sometimes both, with head sampling for routine traffic and tail sampling on top to preserve outliers.

#### Architectural implications

- The sampling strategy is documented per service or per environment, with the rationale (cost vs investigation value).
- Head sampling rates are set explicitly (e.g. 1% for routine traffic, 100% for critical paths); the rate is recorded in the trace so analysts know how to interpret aggregates.
- Tail sampling, where adopted, has documented rules (keep all errors, keep all traces above latency P95, keep traces matching specific attributes) and the buffer-and-decide pipeline is monitored for capacity.
- The sampling architecture is tested: dropped routine traces should be statistically representative; preserved error traces should include the genuinely-investigation-worthy cases.

#### Quick test

> Pick the sampling strategy your tracing system uses. Is it head, tail, or a combination, with documented rationale? When an error happens in production, what's the probability that the relevant trace survived sampling and is queryable? If the answer is "1% — the head-sample rate," investigation is operating on luck.

#### Reference

[OpenTelemetry — Sampling](https://opentelemetry.io/docs/concepts/sampling/) covers head and tail sampling primitives. [Honeycomb — Dynamic Sampling by Example](https://www.honeycomb.io/blog/dynamic-sampling-by-example) treats sampling at practitioner depth, with patterns for stratified sampling that preserve rare events.

---

### 4. Trace cardinality and retention have the same architectural pressures as logs and metrics

Traces, like logs, can carry high-cardinality data — request IDs, user IDs, full URLs, query parameters. Like metrics, indexing and querying that data has cost that scales with cardinality. Like logs, retaining traces forever is wasteful for old traces nobody queries; tiered retention matches data value to cost. The architectural patterns transfer: indexed attributes are limited to those that matter for query (service, status, latency bucket); high-cardinality attributes (user ID, request ID) are preserved in the trace but indexed selectively or not at all; retention tiers (hot for recent, warm for last week, archive for compliance) reflect query patterns. The discipline is to recognise that traces are subject to the same data-architecture concerns as their sibling signals, and to design the architecture deliberately rather than letting it grow ad-hoc until the storage cost becomes the dominant infrastructure expense.

#### Architectural implications

- Indexed trace attributes are limited to those that drive queries — service name, status, latency bucket, environment, region — typically low-to-medium cardinality.
- High-cardinality attributes (user ID, request ID, full URL with parameters) are preserved in the trace but indexed selectively (only when needed for an investigation pattern) or not at all.
- Retention is tiered: hot storage for recent traces (24-72 hours typically), warm for last week or month, archive only where compliance requires it. Most traces older than a month are not queried; their retention should match.
- Cost monitoring covers traces specifically: trace ingest rate, indexed cardinality growth, storage utilisation per tier — separate from logs and metrics monitoring.

#### Quick test

> Pick the tracing backend your organisation uses. What's the trace retention period, and what proportion of traces are in hot vs warm vs archive storage? What's the indexed cardinality? If the answers are "we keep everything in hot storage forever," the cost is paying for data nobody queries — the next time volume doubles, the cost will too.

#### Reference

[Honeycomb — Cardinality](https://www.honeycomb.io/blog/cardinality-the-secret-sauce-of-observability) covers the architectural cost of high-cardinality observability data, applicable to traces specifically. [Jaeger Documentation — Storage Backends](https://www.jaegertracing.io/docs/) covers retention and indexing patterns at the practitioner level.

---

### 5. Critical path analysis is what traces are uniquely good for

When a request takes 2 seconds, the question "where did the time go?" has many possible answers — and the trace is the only signal that can answer it definitively. *Critical path analysis* — identifying the sequence of spans that determined the request's total duration — is what traces are uniquely good at. In a sequential call graph, the critical path is the chain from root to deepest span. In parallel patterns, the critical path runs through the slowest of the parallel branches; speeding up the others doesn't help. In retry patterns, the critical path includes the retried operation's full duration. The architectural pattern that makes critical path analysis tractable is good span instrumentation (the right boundaries are spanned), accurate timing (clock skew and propagation latency are accounted for), and tooling that highlights the critical path visually. The discipline is to use traces for critical-path investigation as the default approach to "this request is slow," rather than reasoning from logs or measurements about which service to suspect.

#### Architectural implications

- Tracing UI (Jaeger, Zipkin, Tempo, Honeycomb, Datadog) supports critical path highlighting — the slowest sequence is visible at a glance, with attribution to specific spans.
- Span timing accuracy is preserved: services use synchronised clocks (NTP, PTP); propagation latency between services is captured as part of the parent-child timing rather than hidden within either span.
- Investigation tooling links critical-path findings to logs and metrics for the implicated service — once a slow service is identified, jumping to its logs and metrics for the same time window is one click.
- Routine performance work uses critical path analysis on representative slow traces, not just on aggregate latency metrics; the metrics show *that* something is slow, the traces show *what*.

#### Quick test

> Pick a recent latency investigation. Did the team start with traces and identify the critical-path service, or did they start with logs and metrics and reason about which service to suspect? If the latter, the tracing capability either isn't trusted or isn't well-instrumented enough — and investigations are taking longer than they should.

#### Reference

[Distributed Tracing in Practice — Parker et al.](https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621/) covers critical-path analysis at practitioner depth, with concrete patterns for using traces to identify performance problems. [Jaeger — UI Documentation](https://www.jaegertracing.io/docs/latest/frontend-ui/) covers the visualisation primitives that make critical paths legible.

---

### 6. Trace correlation with logs and metrics is what makes the observability triad work as one

The three pillars of observability — logs, metrics, traces — are valuable independently and exponentially more valuable when correlated. The *trace ID* is the correlation primitive: every log line emitted while a trace is active should carry the trace ID; every metric data point should be correlatable to the traces that produced it (via exemplars or service-name correlation); every trace should link to logs and metrics from the same service in the same time window. With correlation in place, an investigation flows: a metric anomaly leads to a relevant trace, the trace's critical path identifies the implicated service, the service's logs for the trace's time window reveal the underlying cause. Without correlation, the same investigation requires manual stitching across three tools, three time-window translations, and a patient operator to reconstruct what the unified observability surface should have shown directly. The architectural discipline is to instrument correlation as a first-class concern, not as an afterthought: the logging library reads the active trace context and includes the trace_id and span_id in every emitted log; the metrics emission attaches trace exemplars where supported; the tracing UI links to logs and metrics for matching service and time window with one click.

#### Architectural implications

- Every log statement emitted during an active trace carries the trace_id and span_id as structured fields — the logging framework handles this automatically; application code doesn't.
- Metric exemplars (where supported by the metrics format and backend) attach a sampled trace ID to the metric data point, so "show me a trace from when this metric spiked" is a one-click investigation.
- Tracing UI provides click-through to logs (filtered by trace_id or by service+time window) and metrics (filtered by service+time window) — the operator stays in flow rather than copying identifiers between tools.
- Service-name conventions are consistent across the three signal types so that correlation works without translation: logs, metrics, and traces all use the same service-name format.

#### Quick test

> Pick a recent latency or error investigation. From a metric anomaly, how many clicks does it take to find a relevant trace? From the trace's critical-path service, how many clicks to that service's logs for the same time window? If either is "we navigate manually across tools, copying IDs," the correlation is breaking down — and the time-to-diagnose is paying the cost.

#### Reference

[OpenTelemetry — Trace and Log Correlation](https://opentelemetry.io/docs/specs/otel/logs/) covers the trace_id propagation into logs as a first-class concern. [OpenTelemetry — Exemplars](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#exemplars) covers metric-to-trace correlation. [Distributed Systems Observability — Cindy Sridharan](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) treats the three-pillar correlation as the architectural payoff that makes observability investigation tractable.

---

## Architecture Diagram

The diagram below shows the canonical distributed tracing architecture: services participating in a request flow, each creating spans linked to the propagated trace context (W3C Trace Context standard); span export to a collector with sampling decision (head and/or tail); trace storage with retention tiers; query and visualisation surface; correlation primitives (trace_id in logs, exemplars in metrics) linking the trace to the other observability signals.

---

## Common pitfalls when adopting distributed tracing thinking

### ⚠️ Partial instrumentation produces fragmented traces

Half the services emit spans; the other half don't. Traces fragment at the boundaries between them. Investigations that need to follow a request through the unspanned services hit a wall.

#### What to do instead

Tracing is treated as a system-level invariant, not a per-service choice. All services use the same propagation standard (W3C Trace Context). The framework or instrumentation library handles propagation; application code doesn't have to.

---

### ⚠️ Async boundaries break propagation

Synchronous calls between services have their context propagated correctly. Async work — message queues, event streams, scheduled jobs — drops the trace context. Traces fragment at every async boundary.

#### What to do instead

Async transport mechanisms propagate context through their own envelopes — message attributes, event metadata. The propagation works regardless of the synchrony of the call.

---

### ⚠️ Sampling chosen by accident

The sampling rate is whatever the default was when the tracing library was first installed. Errors are sampled at 1% along with everything else; investigation depends on luck.

#### What to do instead

Sampling strategy chosen deliberately. Head sampling for routine traffic; tail sampling for outliers and errors. Documented rationale; rate recorded in the trace. The strategy reflects what the traces are used for.

---

### ⚠️ Retention uniform regardless of value

All traces in hot storage for a year. Cost grows linearly with traffic; query patterns don't justify the retention.

#### What to do instead

Retention tiers matched to query patterns. Hot for recent (24-72h); warm for last week or month; archive only where compliance requires. Trace storage as carefully designed as log storage.

---

### ⚠️ Traces correlated only by hand

The trace exists; the logs exist; the metrics exist. Correlating across them requires manual stitching by the operator. Time-to-diagnose is multiplied by the friction.

#### What to do instead

Trace_id propagated into every log statement during the trace. Trace exemplars attached to metric data points. UI supports click-through across signal types. The operator stays in flow.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | W3C Trace Context is the propagation standard used consistently across all services ‖ Cross-language, cross-framework consistency. The standard is what makes tracing work; per-service propagation choices guarantee that traces fragment. | ☐ |
| 2 | Propagation is implemented by framework / instrumentation library, not application code ‖ Application code that handles propagation manually gets it wrong inconsistently. The framework handles it; application code is unaware. | ☐ |
| 3 | Async boundaries (queues, events, jobs) propagate context through their own envelopes ‖ Without async propagation, every async pattern produces broken traces. Message attributes, event metadata, scheduled-job context — all carry trace context. | ☐ |
| 4 | Spans are created at architectural boundaries with documented attribute conventions ‖ Service entry, outbound calls, significant internal operations. OpenTelemetry semantic conventions for attribute names. The trace structure encodes the architecture. | ☐ |
| 5 | Sampling strategy is chosen deliberately with documented rationale ‖ Head, tail, or combination. Rate recorded in trace. The strategy reflects what the traces are used for; defaults aren't accepted as the strategy. | ☐ |
| 6 | Sampling preserves rare-but-valuable traces — errors, slow tails, specific patterns ‖ Tail sampling or stratified head sampling that doesn't drop the genuinely-investigation-worthy traces. Routine traffic and outliers are sampled differently. | ☐ |
| 7 | Trace retention is tiered to match query patterns; cardinality is monitored ‖ Hot for recent, warm for medium-term, archive for compliance only. High-cardinality attributes preserved but indexed selectively. | ☐ |
| 8 | Critical-path analysis is the default approach to latency investigation ‖ Investigators start with traces, not with logs and reasoning. Tracing UI highlights the critical path visually. The capability is trusted and well-instrumented. | ☐ |
| 9 | Trace_id is automatically included in every log statement emitted during an active trace ‖ Logging framework reads the active trace context. Application code is unaware. Logs and traces correlate without manual stitching. | ☐ |
| 10 | Metric exemplars (where supported) link metric data points to representative traces ‖ "Why did this metric spike" becomes a one-click investigation through the linked exemplar trace. Correlation across the three pillars is operationally seamless. | ☐ |

---

## Related

[`observability/metrics`](../metrics) | [`observability/logs`](../logs) | [`observability/sli-slo`](../sli-slo) | [`observability/incident-response`](../incident-response) | [`technology/devops`](../../technology/devops) | [`patterns/structural`](../../patterns/structural)

---

## References

1. [OpenTelemetry](https://opentelemetry.io/) — *opentelemetry.io*
2. [W3C Trace Context Recommendation](https://www.w3.org/TR/trace-context/) — *w3.org*
3. [Jaeger](https://www.jaegertracing.io/) — *jaegertracing.io*
4. [Zipkin](https://zipkin.io/) — *zipkin.io*
5. [Distributed Tracing in Practice (Parker et al.)](https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621/) — *oreilly.com*
6. [OpenTelemetry — Sampling](https://opentelemetry.io/docs/concepts/sampling/) — *opentelemetry.io*
7. [Distributed Systems Observability (Cindy Sridharan)](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) — *oreilly.com*
8. [Honeycomb](https://www.honeycomb.io/) — *honeycomb.io*
9. [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — *sre.google*
10. [OpenTelemetry — Context Propagation](https://opentelemetry.io/docs/concepts/context-propagation/) — *opentelemetry.io*
