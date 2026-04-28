# Metrics

Aggregated numerical signals about system behaviour — recognising that the choice of what to measure, how to label it, where to push or pull from, what shape (counter, gauge, histogram) to give it, and how long to retain it at what fidelity is an architectural commitment that determines whether the metrics system answers the operational questions you actually have.

**Section:** `observability/` | **Subsection:** `metrics/`
**Alignment:** Google SRE Book (Four Golden Signals) | RED Method (Tom Wilkie) | USE Method (Brendan Gregg) | Prometheus

---

## What "metrics as architecture" actually means

A *primitive* metrics approach instruments what's easy: response codes, request counts, maybe CPU utilisation. The metrics show up on a dashboard somebody made once. When something goes wrong, the dashboard looks fine — because the metrics aren't measuring what's wrong, only what was easy to instrument. The system has metrics; it doesn't have a metrics architecture, and the gap is paid for in incidents that surface in user complaints rather than in dashboards.

A *production* metrics architecture treats numerical signals as designed data with engineering properties. *What to measure* is informed by canonical methods: the RED method (Rate, Errors, Duration) for services facing requests; the USE method (Utilization, Saturation, Errors) for resources processing work; the Four Golden Signals (latency, traffic, errors, saturation) as the universal baseline. *Cardinality* — the number of distinct label combinations — is recognised as the failure mode that turns metrics systems from operational into expensive: a metric labelled with `userId` becomes one time series per user, and millions of users break the storage. *Push vs pull* is an architectural choice with implications for service discovery, network topology, and the failure modes of the collection layer. *Distributions* — histograms with quantile estimation — are recognised as what's actually needed for latency and other variable signals, where averages hide everything operationally meaningful. *Retention and downsampling* match the data's value over time: high-fidelity recent data, downsampled older data, archive or expiry beyond.

The architectural shift is not "we added Prometheus." It is: **metrics are aggregated numerical signals whose value is determined by what's measured, how it's labelled, what shape it takes, and how it's stored — and treating metric instrumentation as an engineering afterthought produces dashboards that show what was easy to capture rather than what's needed to operate the system.**

---

## Six principles

### 1. The Four Golden Signals are the universal baseline; RED for services, USE for resources is how to extend

The architectural question "what should we measure?" has surprisingly canonical answers. For *services facing user requests*, the [Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/) (Google SRE) — *latency, traffic, errors, saturation* — are the universal baseline. For services specifically, [Tom Wilkie's RED method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/) — *Rate, Errors, Duration* — is RED-coloured shorthand for the same idea: how many requests per second, what fraction are erroring, how long are they taking. For resources processing work (CPU, memory, network, disks), [Brendan Gregg's USE method](https://www.brendangregg.com/usemethod.html) — *Utilization, Saturation, Errors* — covers what you need to know to diagnose resource problems. These aren't all the metrics you'll ever want — domain-specific signals (orders processed, fraud signals fired, payment success rate) matter for their domains — but the canonical methods are the baseline that every service should have, and missing any of them creates blind spots that incidents will eventually surface.

#### Architectural implications

- Every service exposes the Four Golden Signals as standard metrics — request rate, error rate, latency distribution, saturation indicator — with consistent metric names across services.
- For each underlying resource the service depends on (CPU, memory, network, queue depth), USE-method metrics are exposed: utilization (how busy), saturation (queued work), errors.
- Domain-specific metrics layer on top of the canonical ones — orders/sec is a domain metric; HTTP request rate is the canonical one. Both are needed; neither replaces the other.
- The metric naming convention is documented and enforced: `service_requests_total`, `service_request_duration_seconds`, `service_errors_total` — not free-form names that vary by team.

#### Quick test

> Pick the most-trafficked service in your system. Does it expose request rate, error rate, latency distribution (P50, P90, P99), and saturation indicator with consistent naming? If any of the four are missing, the service has a known blind spot — and the next incident in that dimension will be diagnosed slowly because the data isn't there.

#### Reference

[Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) is the canonical reference for the Four Golden Signals. [The RED Method (Tom Wilkie)](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/) and [The USE Method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html) are the canonical practitioner-level extensions; the three frameworks together cover most of the metrics design space for production services.

---

### 2. Cardinality is the failure mode — labels matter more than they look

A metric called `http_requests_total{method="GET", status="200"}` has cardinality 2 × 5 × N, where N is the number of distinct services exposing the metric — manageable. The same metric with an additional label `userId="..."` becomes one time series per user, and at a million users the metric storage becomes unmanageable. The architectural reality of metrics systems (Prometheus, M3, Cortex, Mimir, and most cloud-native equivalents) is that storage and query cost is dominated by the *number of distinct label combinations* — the cardinality — not by the volume of data points. The discipline is to recognise high-cardinality labels as the architectural risk they are: identifiers (userId, requestId, sessionId) generally don't belong as metric labels (they belong as log fields or trace attributes); template paths (`/users/:id/profile`) belong as labels, but the template, not the concrete URL.

#### Architectural implications

- Each metric label has a documented expected cardinality — low (HTTP method, status code, region) is fine; medium (service, environment, tier) is fine; high (userId, requestId, full URL) is generally not fine for metrics and belongs in logs or traces instead.
- Cardinality is monitored: total time series count per metric, growth rate over time, with alerts if a metric's cardinality grows beyond budget.
- Cardinality budget is documented per service: a service can produce N time series, with the budget shared across the metrics it exposes; exceeding the budget is treated as a bug, not as a normal scaling concern.
- The metrics library or framework rejects high-cardinality labels at runtime — using `userId` as a label triggers a warning in development, a metrics emission failure in production.

#### Quick test

> Pick the metrics system your organisation runs. What's the total time series count, and what proportion of it comes from the top 10 highest-cardinality metrics? If 80% of the storage is from 5 metrics, those 5 are candidates for label-set audit — and the next cardinality explosion will probably come from one of them.

#### Reference

[Prometheus — Naming Best Practices](https://prometheus.io/docs/practices/naming/) and [Prometheus — Histograms and Summaries](https://prometheus.io/docs/practices/histograms/) cover the cardinality concerns at the practitioner level. [Honeycomb — Cardinality and the Limits of Observability](https://www.honeycomb.io/blog/cardinality-the-secret-sauce-of-observability) treats cardinality across observability backends with the same architectural framing.

---

### 3. Push vs pull is an architectural choice with consequences for service discovery, topology, and failure modes

The two dominant metric-collection patterns have different architectural implications. *Pull* (Prometheus's model): the metrics backend periodically scrapes each application's metrics endpoint, requiring service discovery (the backend has to know where the applications are), making firewall topology a constraint (the backend has to be able to reach each application), and making short-lived workloads a problem (a job that runs for 5 seconds may not be scraped before it exits). *Push* (StatsD, Datadog Agent, OpenTelemetry default): the application sends metrics to a collector or backend, requiring no service discovery from the backend's side, working through firewalls in the outbound direction (typically easier), and handling short-lived workloads naturally — but introducing the failure mode of metrics-system-overload-from-too-many-pushers and the security concern of any application with credentials being able to push arbitrary metrics. Neither is universally correct; the architectural discipline is to choose deliberately based on the system's topology, the workload's lifecycle, and the operational team's preferences.

#### Architectural implications

- The push/pull choice is documented per metrics surface, with documented reasoning (service-discovery cost, firewall topology, workload lifecycle, operational preference).
- For pull-based systems: service discovery is robust (auto-registration, health checks, deregistration on shutdown); short-lived jobs use a pushgateway or are excluded from pull; scrape interval is calibrated (10-60s is typical; 1s is wasteful for most signals).
- For push-based systems: rate limiting protects the collector from runaway pushers; authentication identifies pushers; the collector's own metrics are pulled (push-of-pushers becomes circular).
- Hybrid patterns (push for short-lived workloads, pull for stable services) are recognised and made explicit, not arrived at by accident.

#### Quick test

> Pick the metrics-collection pattern your organisation uses. Is it push, pull, or hybrid, with documented reasoning? What's the failure mode if (push) the collector is overwhelmed or (pull) service discovery is broken? If those failure modes haven't been thought through, the metrics system has reliability properties nobody has measured — and the next collection-layer incident will reveal them.

#### Reference

[Prometheus — Why Prometheus Pulls Instead of Pushing](https://prometheus.io/docs/practices/pushing/) treats the trade-offs from the pull-side; the StatsD documentation and OpenTelemetry's collector architecture treat the push-side with corresponding nuance. The architectural framing of the choice is treated in [Distributed Systems Observability — Cindy Sridharan](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/).

---

### 4. Distributions, not averages — the long tail of latency is operationally meaningful

A common pattern: applications emit a single average latency metric per service. The dashboard shows "average latency: 45ms — looks fine." The actual user experience: P50 is 20ms, P99 is 2 seconds, P99.9 is 15 seconds — and the users hitting the long tail are having a terrible time. Averages hide tail behaviour by design — they smooth across the distribution. The architectural answer is to emit *distributions*: histograms (with bucketed counts) or summaries (with quantile estimation), capturing the shape of the latency distribution rather than just its central tendency. The alternatives — pre-computed quantiles per pod that can't be aggregated, or T-Digest sketches that can — have different cost profiles, but the underlying architectural commitment is the same: latency and other variable signals deserve distribution treatment, not average treatment.

#### Architectural implications

- Latency is exposed as a histogram (Prometheus histogram, OpenTelemetry histogram, T-Digest aggregate) — not as a single average metric.
- Histogram bucket boundaries are calibrated to the actual distribution: buckets that span the relevant range with enough resolution at the percentiles that matter (P50, P90, P99, P99.9) without exploding cardinality.
- Aggregation is designed in: histograms aggregate across pods cleanly; summary-based pre-computed quantiles per pod don't aggregate honestly (averaging quantiles is mathematically meaningless), and the architectural choice reflects that.
- Other variable signals — response sizes, queue depths, time-in-queue, fan-out factors — receive the same distribution treatment when their tail behaviour matters.

#### Quick test

> Pick the most user-impacting latency metric in your system. Is it exposed as an average or as a distribution? What's its P99 right now, and how does that compare to its average? If the gap between P99 and average is large (and it usually is), the average is hiding most of the operationally meaningful information.

#### Reference

[Gil Tene — How NOT to Measure Latency](https://www.youtube.com/watch?v=lJ8ydIuPFeU) is the classic talk on why averages and naive percentiles fail; the conceptual framing transfers across measurement methodologies. [HDR Histogram](https://github.com/HdrHistogram/HdrHistogram) and [T-Digest (Dunning)](https://github.com/tdunning/t-digest) are the canonical algorithmic primitives for accurate distribution measurement at scale.

---

### 5. Pre-aggregation and downsampling match data fidelity to data value over time

A metrics data point captured at 1-second resolution is operationally valuable for the next hour: it's the granularity that matters for incident response. The same data point at 1-second resolution one month later is mostly noise — for retrospective analysis, you typically need 1-minute or 5-minute granularity, not 1-second. Storing all metrics at 1-second resolution forever pays the cost of fine granularity for data nobody queries at that granularity. The architectural discipline is *downsampling*: data is captured at high resolution, kept at high resolution for an operational window (24 hours to a week), then progressively downsampled — to 1-minute for the next month, 5-minute or 1-hour for the next quarter, daily aggregates for the next year, and either expired or archived beyond. Each tier has lower storage cost and matches the queries that actually run at that age.

#### Architectural implications

- Resolution tiers are documented: capture at 5-15s, hot-store at full resolution for 24h-7d, downsample to 1-minute for 7-30d, 5-minute for 30-90d, hourly or daily beyond.
- Pre-aggregation runs continuously: as data ages out of one resolution tier, the downsampled version is computed and stored; the high-resolution version is expired.
- Query layer is aware of resolution tiers: a query for the last hour returns 5-15s data; a query for last quarter returns 5-minute or hourly aggregates with explicit indication of resolution.
- The downsampling functions are appropriate to the metric type: counters use sum or delta; gauges use last-value or average; histograms preserve quantile estimation through merging.

#### Quick test

> Pick your metrics retention. Is the same resolution kept for the entire retention window, or does it tier? If uniform, the storage is overpaying for old data, or the operational window is undercovered. If tiered, what's the resolution at each tier, and does it match the queries that actually run at that age?

#### Reference

[Prometheus — Storage](https://prometheus.io/docs/prometheus/latest/storage/) covers the retention and downsampling model in the Prometheus ecosystem; [Thanos](https://thanos.io/) and [Cortex / Mimir](https://grafana.com/oss/mimir/) extend this with explicit tiered storage and downsampling. The conceptual framing applies equally to commercial backends (Datadog, Splunk, etc.) with platform-specific operational details.

---

### 6. Metric correlation with logs and traces is the architectural payoff

Metrics show that something changed at 14:32 — error rate spiked, latency widened, saturation hit a threshold. The metric tells you a problem exists; it doesn't tell you why. Logs and traces are the signals that carry the per-event detail needed to diagnose the cause. The architectural pattern that makes investigation tractable is *correlation*: every metric is associated with a service, environment, and time window that can be used to query the corresponding logs and traces; every log line and trace span carries identifiers that link back to the service emitting them. A dashboard alert at 14:32 on `service=checkout` should let the operator click through to logs from `service=checkout` for that time window and to traces from the same service. Without the correlation primitives in place, the operator copies timestamps and service names by hand from one tool to the next, multiplying time-to-diagnose. The metrics, logs, and traces are complementary; the correlation is what makes them an observability triad rather than three separate systems.

#### Architectural implications

- Metrics carry consistent service, environment, region, and (where applicable) tier labels — the same labels that appear in logs and traces — so correlation queries don't require translation.
- Dashboard tooling supports click-through correlation: from a metric anomaly to the corresponding logs and traces for the same time window and service.
- Trace exemplars (where supported by the metrics format, e.g. Prometheus exemplars) attach a sample trace ID to a metric data point, making "why did this latency spike happen" a one-click investigation rather than a multi-tool reconstruction.
- The correlation discipline is enforced at instrumentation time — services that emit metrics with one service-name format and logs with another break correlation for everyone investigating their behaviour.

#### Quick test

> Pick a recent incident that surfaced as a metric anomaly. From the dashboard alert, how many clicks does it take to reach the logs and traces for the same service and time window? If the answer is "we navigate through three tools by hand," the correlation primitives aren't in place — and the time-to-diagnose is paying the cost.

#### Reference

[OpenTelemetry — Exemplars](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#exemplars) treats trace-metric correlation as a first-class metrics-system feature. [Prometheus Exemplars](https://prometheus.io/docs/prometheus/latest/feature_flags/#exemplars-storage) implements the same idea in the Prometheus ecosystem. Modern observability platforms (Honeycomb, Datadog, Grafana Cloud) treat correlation as a primary architectural feature rather than an afterthought.

---

## Architecture Diagram

The diagram below shows the canonical metrics architecture: instrumentation in applications producing the Four Golden Signals plus domain-specific metrics; cardinality validation at emission time; collection layer (push or pull) with appropriate trade-offs; resolution tiers (high-fidelity recent, downsampled older); query layer aware of tier boundaries; dashboards and alerting consuming the metrics; correlation primitives (consistent service labels, exemplar trace IDs) linking metrics to logs and traces.

---

## Common pitfalls when adopting metrics-as-architecture thinking

### ⚠️ Instrumentation by what's easy

The application has whatever metrics happened to be easy to add. Some services have rich latency distributions; others have only request counts. Cross-service investigation is impossible because the metrics aren't comparable.

#### What to do instead

The Four Golden Signals as the universal baseline. RED for services, USE for resources. Consistent naming and labels. Domain-specific metrics layer on top of the canonical ones, not as substitutes for them.

---

### ⚠️ User-ID labels in metrics

A well-intentioned developer adds `userId` as a metric label to enable per-user analysis. Cardinality grows linearly with users. The metrics backend's storage cost surprise arrives the next month.

#### What to do instead

Per-user analysis belongs in logs (with structured userId field) or traces (with userId as span attribute). Metrics carry low-to-medium cardinality dimensions. The metrics library rejects high-cardinality labels at runtime.

---

### ⚠️ Push or pull by accident

The collection pattern is whatever the first tool the team adopted happened to use. Failure modes haven't been thought through. The next collection-layer incident reveals the unconsidered properties.

#### What to do instead

Push or pull as a documented architectural choice with reasoning. Failure modes are designed for. Hybrid patterns are explicit, not accidental.

---

### ⚠️ Average latency as the only latency metric

The dashboard shows average latency. The system looks fine. P99 is 50x the average; users on the tail are having a terrible time, and customer support escalations are the first signal.

#### What to do instead

Latency as histogram. P50, P90, P99, P99.9 visible. Bucket boundaries calibrated. Aggregation across pods designed in.

---

### ⚠️ Uniform retention at full resolution

All metrics kept at 5-second resolution for a year. Storage cost is dominated by data nobody queries at that resolution. Or: only 24 hours retained, so retrospective analysis is impossible.

#### What to do instead

Resolution tiers matched to data value over time. High-fidelity recent, downsampled older, archive or expire beyond. Query layer aware of tier boundaries.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Every service exposes the Four Golden Signals (latency, traffic, errors, saturation) with consistent naming ‖ Universal baseline. RED for services, USE for resources. Domain-specific metrics layer on top, not as substitutes. | ☐ |
| 2 | Each metric label has documented expected cardinality with matching emission policy ‖ Low-cardinality labels are fine; medium are fine; high (user IDs, request IDs) belong in logs or traces, not metrics. The metrics library enforces at runtime. | ☐ |
| 3 | Cardinality budget is documented per service; cardinality drift is monitored ‖ A service has a documented budget of time series; exceeding it is a bug. Drift detection catches the next cardinality explosion early. | ☐ |
| 4 | Push or pull collection is a documented choice with documented failure modes ‖ The choice is deliberate, not historical. Failure modes are designed for. Hybrid patterns are explicit. | ☐ |
| 5 | Latency and other variable signals are exposed as distributions (histograms), not averages ‖ Averages hide the tail behaviour that determines user experience. Histograms preserve the distribution; bucket boundaries are calibrated; aggregation across pods is designed in. | ☐ |
| 6 | Resolution tiers match data value over time — high-fidelity recent, downsampled older ‖ Storage cost matches query patterns. Hot at full resolution for operational window; warm at minute resolution; cold at hourly or daily aggregates. | ☐ |
| 7 | Pre-aggregation runs continuously and uses appropriate functions per metric type ‖ Counters use sum/delta; gauges use last-value or average; histograms preserve quantile estimation through merging. The downsampling preserves what the queries need. | ☐ |
| 8 | Metrics carry consistent service, environment, region labels matching logs and traces ‖ Correlation depends on consistent dimensions across the three pillars. Service-name conventions are enforced at instrumentation time, not normalised at query time. | ☐ |
| 9 | Dashboards support click-through to logs and traces for the same service and time window ‖ Time-to-diagnose depends on correlation. Click-through reduces investigation from multi-tool reconstruction to single-flow navigation. | ☐ |
| 10 | Trace exemplars are attached to metric data points where supported ‖ Exemplars are the correlation primitive that turns "why did this latency spike happen" into a one-click investigation. The metrics format and visualization tooling support exemplars first-class. | ☐ |

---

## Related

[`observability/sli-slo`](../sli-slo) | [`observability/logs`](../logs) | [`observability/traces`](../traces) | [`observability/incident-response`](../incident-response) | [`technology/devops`](../../technology/devops) | [`patterns/data`](../../patterns/data)

---

## References

1. [Google SRE Book — The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/) — *sre.google*
2. [The RED Method (Tom Wilkie)](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/) — *weave.works*
3. [The USE Method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html) — *brendangregg.com*
4. [Prometheus](https://prometheus.io/) — *prometheus.io*
5. [Prometheus — Histograms and Summaries](https://prometheus.io/docs/practices/histograms/) — *prometheus.io*
6. [Honeycomb](https://www.honeycomb.io/) — *honeycomb.io*
7. [HDR Histogram](https://github.com/HdrHistogram/HdrHistogram) — *github.com*
8. [T-Digest (Dunning)](https://github.com/tdunning/t-digest) — *github.com*
9. [Grafana](https://grafana.com/) — *grafana.com*
10. [OpenTelemetry](https://opentelemetry.io/) — *opentelemetry.io*
