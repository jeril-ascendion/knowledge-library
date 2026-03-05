# Metrics

> **Section:** `observability/` | **Subsection:** `metrics/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

RED/USE metrics methodology, custom metrics, Prometheus + Grafana, and metric cardinality management.

This document is part of the **Observability** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Four Golden Signals for Every Service

Every production service must emit Latency, Traffic, Errors, and Saturation metrics. These four signals, combined, surface virtually every class of production problem within minutes.

### 2. USE Method for Infrastructure

Every infrastructure component (CPU, memory, disk, network, queue) must expose Utilization, Saturation, and Errors metrics. USE metrics identify resource bottlenecks that golden signals alone may not pinpoint.

### 3. Design Metrics for SLO Measurement

Metrics are instrumentation for SLOs. Before writing metrics code, know your SLO. Design the metric labels, buckets, and cardinality to make the SLO calculation accurate and efficient.

### 4. Cardinality is a Cost

Every unique label combination creates a new time series. High-cardinality labels (user ID, request ID, IP address) are metrics system killers. Use labels for dimensions you will filter by in queries; use logs for high-cardinality per-request data.


---

## Implementation Guide

**Step 1: Define SLIs Before Instrumenting**

Write down your SLO in measurable form: '99.9% of API requests complete in under 500ms.' Then design the metric that lets you calculate this: a request_duration_seconds histogram with 0.5s bucket boundary.

**Step 2: Instrument with OpenTelemetry**

Use the OpenTelemetry SDK for your language. Emit counters for request counts, histograms for latency distributions, and gauges for resource utilization. Route to a Prometheus-compatible backend via OTLP exporter.

**Step 3: Build RED Dashboards per Service**

In Grafana: create one dashboard per service with panels for Request Rate (req/s), Error Rate (%), and Duration (p50/p95/p99). Make these dashboards the first thing on-call engineers open during an incident.

**Step 4: Set SLO-Based Alerts**

Configure alerts based on error budget burn rate (the approach recommended by Google SRE book), not raw thresholds. A burn rate alert fires when you're consuming your error budget too fast, giving advance warning before the SLO is actually breached.

**Step 5: Run Quarterly Metrics Hygiene**

Audit your metrics cardinality quarterly. Remove unused metrics. Consolidate high-cardinality labels. Recording rules should pre-aggregate expensive queries. Keep Prometheus storage under 10M active series.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Four Golden Signals Instrumented | Platform Team | All production services emit L/T/E/S metrics via OpenTelemetry | Required |
| Grafana RED Dashboards Live | SRE / Platform | Per-service RED dashboards published and linked in runbooks | Required |
| SLO Burn Rate Alerts Configured | SRE | Error budget burn rate alerts firing correctly in staging | Required |
| Cardinality Audit Passed | Platform Team | No single metric exceeds 100k active time series | Quarterly |


---

## Recommended Patterns

### Error Budget Alerting

Alert when the error budget is being consumed at a rate that will exhaust it before the end of the SLO window. Two alert tiers: fast burn (consuming 5% error budget in 1 hour) and slow burn (consuming 10% error budget in 6 hours).

### Recording Rules

Pre-compute expensive PromQL expressions as recording rules that run at scrape time. This transforms expensive range queries (summing across hundreds of instances) into cheap lookups of pre-computed series.

### Exemplar-Linked Metrics

Associate individual trace exemplars with histogram metrics. When a p99 latency spike fires an alert, engineers can jump from the alerting metric directly to a representative slow trace. Supported by OpenTelemetry + Tempo + Grafana.


---

## Anti-Patterns to Avoid

### ⚠️ Alert on Every Metric

Configuring alerts for every metric that exceeds a static threshold creates alert storms that train engineers to ignore pages. Alert on symptoms (SLO breach, error rate spike) not causes (CPU > 70%). Alert fatigue is an existential risk to on-call programs.

### ⚠️ Metrics Without Dashboards

Collecting metrics that no one has built a dashboard for. These metrics are theoretical — no one knows how to read them or what threshold indicates a problem. Every metric used in alerting must have a corresponding dashboard panel.


---

## AI Augmentation Extensions

### AIOps Anomaly Detection

ML models trained on historical metric patterns detect anomalies in real time — catching subtle degradations (a 5% p99 latency increase that's still within thresholds but represents a genuine regression) that static threshold alerts miss.

> **Note:** AIOps anomaly detection generates false positives for the first 30 days while learning normal patterns. Don't route AIOps alerts to PagerDuty until the false positive rate is below 5%.


---

## Related Sections

[`observability/logs`](../observability/logs) | [`observability/traces`](../observability/traces) | [`observability/sli-slo`](../observability/sli-slo) | [`observability/incident-response`](../observability/incident-response) | [`nfr/reliability`](../nfr/reliability)

---

## References

1. [Site Reliability Engineering — Google](https://sre.google/sre-book/table-of-contents/) — *sre.google*
2. [Prometheus Documentation — prometheus.io](https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Prometheus+Documentation+%E2%80%94+prometheus.io) — *IEEE Xplore*
3. [OpenTelemetry Documentation — opentelemetry.io](https://opentelemetry.io/docs/) — *opentelemetry.io*
4. [Systems Performance — Brendan Gregg](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) — *brendangregg.com*
5. [Accelerate — Forsgren, Humble, Kim](https://itrevolution.com/product/accelerate/) — *IT Revolution*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `observability/metrics/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
