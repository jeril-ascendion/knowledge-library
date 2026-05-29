# Observability and Operational Excellence

> **Section:** `technology/mobile/observability-operational-excellence/`
> **Alignment:** SRE Principles (Google) | OpenTelemetry | DORA Metrics | Firebase Platform
> **Audience:** Mobile Engineers · SREs · DevOps Engineers · Product Managers

Observability is the ability to understand the internal state of a running system from its external outputs. For mobile, the "external outputs" are crash reports, performance traces, analytics events, and user behaviour signals emitted by the application running on millions of devices. Without observability, production issues are discovered through user reviews and support tickets — too slow, too late, and too opaque to diagnose efficiently.

## Overview

Mobile observability has four pillars: crash reporting (what broke), performance monitoring (what is slow), user analytics (what users do), and session recording (how users experience failures). These four pillars together provide the signal needed to diagnose production issues and make data-driven product decisions.

## Crash Reporting

Firebase Crashlytics is the primary crash reporting tool. Configuration: custom keys attached to every crash report — hashed user identifier (never raw PII), current feature flags, app state machine state, last 5 user actions (breadcrumbs). Non-fatal exception logging for handled errors: `Crashlytics.recordException(e)` for errors that produce an error state in the UI but do not crash the app. These non-fatals illuminate degraded states that users experience but do not report.

Primary SLA metric: crash-free users rate above 99.5% across the production install base, measured as the percentage of users who opened the app in the last 28 days without experiencing a crash. Secondary metric: ANR rate below 0.2% (Android only — Application Not Responding when the main thread is blocked for more than 5 seconds). Both metrics monitored in Firebase Crashlytics and Google Play Android Vitals dashboards with alerting configured.

## Performance Monitoring

Firebase Performance Monitoring instruments: all HTTP network requests (DNS lookup time, connect time, SSL handshake time, request time, response time, response size, success/failure) automatically. Custom traces for business-critical user journeys: start the trace when a user initiates checkout, stop it when the confirmation screen appears. Firebase aggregates P50, P75, P90, P95 timing across the user base — enabling regression detection without requiring production reproduction.

MetricKit on iOS delivers system-provided diagnostic reports every 24 hours: launch time histogram, hang duration histogram, CPU time, disk writes, memory peak. These device-level metrics complement Firebase's network-level metrics.

## Analytics

Analytics serves two audiences: engineering (performance and reliability) and product (usage and conversion). Mixpanel for product analytics — cohort analysis, retention modelling, funnel conversion. Firebase Analytics for standard event tracking when deep product analytics are not required. Amplitude for A/B testing integrated with analytics.

Event schema governance: all analytics events follow a typed schema defined and versioned by the platform team. Feature teams fire domain events (`AccountViewed(accountId: String, accountType: AccountType)`); the analytics SDK maps domain events to provider-specific payload format. This abstraction enables provider switching without changing feature code.

## Session Recording

FullStory or Heap for session recording — records user interactions as a video-like replay. Mandatory PII masking configuration: all text input fields are masked automatically, sensitive display fields are masked via element configuration, network request and response bodies are excluded from recording. GDPR/PDPA consent required before recording in markets with personal data regulations. Session recording is invaluable for diagnosing user experience failures that users cannot articulate in support tickets.

## Anti-Patterns to Avoid

> **⚠ Observability Bolted On Post-Launch** — No crash reporting, no performance monitoring, no analytics until the first production incident triggers a reactive investigation.
> **CORRECT:** Crashlytics, Firebase Performance, and analytics initialized from the first production release. Alerting configured before launch. Production observability is not optional.

> **⚠ Raw PII in Crash Reports** — User names, email addresses, account numbers, or device identifiers attached as custom keys to Crashlytics reports. Violates PDPA, GDPR, and BSP Circular 982 data minimisation requirements.
> **CORRECT:** Attach only hashed identifiers (SHA-256 of user ID is acceptable), boolean state flags, and non-identifying context to crash reports. Never attach raw PII.

## References

1. Google — Firebase Crashlytics. firebase.google.com/docs/crashlytics
2. Google — Firebase Performance Monitoring. firebase.google.com/docs/perf-mon
3. Beyer, Betsy et al. — Site Reliability Engineering. Google, 2016. sre.google/books
4. OpenTelemetry — Mobile Instrumentation. opentelemetry.io/docs/instrumentation/android
