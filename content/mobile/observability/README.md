# Mobile Observability

Crashlytics and Sentry for crash and error reporting, Firebase Performance and Datadog Mobile APM for transaction tracing, Mixpanel and Amplitude for product analytics, FullStory and Heap for session replay with PII masking, MetricKit on iOS, and the SLOs that turn observability data into release-gating signal.

**Section:** `mobile/` | **Subsection:** `observability/`
**Alignment:** OpenTelemetry Mobile SIG | Google Firebase Best Practices | Datadog Mobile APM | Apple MetricKit
**Audience:** Mobile Engineers · SREs · Product Analytics

---

## Overview

Mobile observability differs from backend observability in three ways. First, the device is intermittently connected — telemetry must batch locally and ship opportunistically without dropping data on connectivity loss. Second, the client is the user's device with the user's expectation of privacy — sending raw URL paths, screen names, and field values risks PII leak that can become a GDPR notification event. Third, the unit of analysis is the user session, not the request — a crash that happens once per 1,000 sessions is critical; the same crash measured per HTTP request would look trivial.

The mobile observability stack in 2026 is layered. Crash reporting (Firebase Crashlytics or Sentry) catches fatal errors with stack traces de-obfuscated against the build's R8 mapping file. Performance monitoring (Firebase Performance, Datadog Mobile APM, or New Relic Mobile) traces network requests, screen rendering, and custom business-logic spans. Product analytics (Mixpanel, Amplitude, or Firebase Analytics) capture user events for funnel and cohort analysis. Session replay (FullStory, Heap, or LogRocket Mobile) records device-side video of user interactions for debugging — with mandatory PII masking. Apple MetricKit and Android Vitals provide platform-side aggregates the team cannot easily collect itself.

The architectural shift is not "we have analytics." It is: **mobile observability is a layered stack — crashes, performance, business events, session replay — each routed to its specific tool, with strict PII redaction by default, tied to release-gating SLOs (crash-free users above 99.5 percent, P95 cold start under 4 seconds, ANR rate under 0.1 percent) that block deploys when breached.**

---

## Core Principles

### 1. Crash reporting is mandatory, sampled at 100 percent

Every crash, every release, on every device. Crashlytics and Sentry both support symbol upload during CI for de-obfuscated stack traces. No "sample rate" on crashes — they are too rare and too important to sample.

### 2. Performance monitoring is automatic plus custom

Automatic network monitoring captures every HTTP request: DNS lookup time, connect time, response time, response size. Custom traces wrap business-critical user flows: checkout, transfer, search. Both are needed; automatic catches the regressions the team didn't think to instrument.

### 3. Product analytics is event-driven, not page-driven

Events are named actions: `signed_in`, `transfer_initiated`, `transfer_completed`, `transfer_failed`. Each event carries typed properties. Funnels and cohorts compose from events. Page-view-only analytics misses the user behaviour that matters.

### 4. PII redaction by default

Logs, analytics events, session replay, crash reports — every channel scrubs PII before send. Token-name regex, allowlist of safe property names, masking rules on session replay's text input capture.

### 5. SLOs gate releases

Crash-free users rate, cold-start P95, ANR rate, transaction-latency P95. SLOs documented; CI checks the previous release's metrics against thresholds; regressions block the next release.

### 6. The observability stack respects user consent

GDPR, CCPA, App Tracking Transparency on iOS, and Android 13+ permission model all require explicit consent for analytics that include cross-app tracking identifiers (IDFA on iOS, GAID on Android). Crash reporting is generally permitted under legitimate interest; analytics often requires explicit opt-in.

---

## Architecture Deep-Dive

**Firebase Crashlytics**

Crashlytics catches uncaught exceptions on Android and `NSException` plus signal-based crashes on iOS. The crash report includes the stack trace, the device model, the OS version, the app version, and configurable custom keys and breadcrumbs.

```kotlin
class CrashlyticsTree : Timber.Tree() {
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        Firebase.crashlytics.setCustomKey("feature", currentFeature)
        Firebase.crashlytics.log(message.redactPii())
        t?.let { Firebase.crashlytics.recordException(it) }
    }
}
```

Custom keys (`feature`, `user_tier_hashed`, `experiment_flag`) add context to the crash. Breadcrumb logs (the last N log messages before the crash) reconstruct the user's path. Non-fatal exception recording (`recordException`) tracks handled exceptions that should still be monitored.

R8 mapping file upload during CI is non-negotiable; without it, stack traces are obfuscated and useless. The Crashlytics Gradle plugin handles upload automatically when configured. Bitcode symbol upload on iOS does the equivalent.

Crash-free-users rate is the primary SLA. Target: above 99.5 percent on the highest-traffic release. Google Play and App Store reviewers consider crash rate when ranking apps.

**Sentry for Mobile**

Sentry is the multi-platform alternative with richer context: performance monitoring built in, source-map upload for JavaScript in React Native, session replay, and the option to self-host (Crashlytics is Google-only and Google-hosted).

Sentry's `setUser` (with hashed user ID, never raw), `setTag`, and `setContext` enrich events. Performance transactions (`startTransaction`) wrap business-critical operations and produce span trees that connect to backend traces if the backend is also on Sentry or sends compatible trace headers.

**Firebase Performance Monitoring**

Automatic monitoring: every `URLSession` request on iOS, every `OkHttp` request on Android (via the auto-instrumentation library) reports DNS, connect, request, response, response-size metrics. The Firebase console aggregates per-endpoint.

Custom traces around business flows:

```kotlin
val trace = Firebase.performance.newTrace("checkout_flow")
trace.start()
// ... user completes checkout ...
trace.putAttribute("cart_size_bucket", cartSize.toBucket())
trace.putMetric("items_count", cartSize.toLong())
trace.stop()
```

Screen rendering metrics: slow frames (above 16 ms), frozen frames (above 700 ms) reported automatically; the team sees which screens are problematic without manual instrumentation.

**Datadog Mobile APM**

Enterprise alternative with distributed tracing — the mobile request is correlated to the backend span via `traceparent` header. The full request path (mobile to BFF to microservice to database) shows in one trace. Resource timing attribution lets the team see which backend service is contributing the latency.

**Mixpanel vs Amplitude vs Firebase Analytics**

- **Mixpanel**: best-in-class product analytics with cohort analysis, funnels, retention curves, and revenue tracking. SaaS pricing scales with event volume.
- **Amplitude**: similar to Mixpanel with stronger funnel analytics and the "behavioural cohort" model. SaaS.
- **Firebase Analytics**: free, integrated with Firebase. Sufficient for standard event tracking. Less powerful than Mixpanel / Amplitude for sophisticated analysis. Best when already in the Firebase ecosystem.

The team usually picks one product analytics tool and one alone — multiple tools produce conflicting data and confused stakeholders.

**Session Replay — FullStory, Heap**

Records the user's interactions client-side (no actual video; reconstructed playback from event stream and view tree). Powerful for debugging: the engineer sees exactly what the user did before the bug.

PII masking is mandatory and must be configured at integration time, not bolted on later:

- **Element masking**: every Text composable / SwiftUI Text containing sensitive data marked with `FS.mask` / equivalent.
- **Text input suppression**: every TextField / SecureField defaults to masked — the recording shows asterisks, not the typed value.
- **Network request sanitisation**: URL query parameters scrubbed, request bodies redacted by header type.

Misconfigured session replay is a GDPR violation waiting to happen. The compliance review per integration is non-optional.

**Apple MetricKit**

iOS device-side aggregation delivered to the app daily as a `MXMetricPayload`. The payload contains:

- App launch metrics (foreground / background, time-to-first-frame)
- Hang diagnostics (`MXHangDiagnostic` — the call stack of any hang above 250 ms)
- CPU exceptions (`MXCPUExceptionDiagnostic`)
- Disk write exceptions
- Memory metrics

MetricKit data is collected by the OS in the background, with no in-app instrumentation, on every device. Ingest the payload into the observability stack as the iOS-side complement to Crashlytics.

**Custom Metric Instrumentation Pattern**

Wrap Use Case execution in a trace for business-logic performance:

```kotlin
class GetAccountUseCase @Inject constructor(
    private val repo: AccountRepository,
    private val performance: PerformanceMonitor,
) {
    suspend operator fun invoke(): Result<Account> {
        return performance.trace("get_account") {
            repo.getAccount()
        }
    }
}
```

The instrumentation is consistent across use cases; the team sees per-use-case latency in the dashboard.

---

## Implementation Guide

### Step 1: Integrate Crashlytics or Sentry with symbol upload

Gradle plugin or Xcode build phase uploads symbols on every release build. Verify in the console that obfuscation is resolved.

### Step 2: Configure performance auto-instrumentation

Firebase Performance or Datadog SDK installed; automatic network monitoring confirmed on staging build.

### Step 3: Define and instrument business events

Event taxonomy documented: `signed_in`, `transfer_initiated`, etc. with typed properties. Implementation in a centralised analytics wrapper, not scattered across the codebase.

### Step 4: Configure session replay with PII masking

If session replay adopted, configure masking rules per screen during integration; compliance review before production rollout.

### Step 5: Subscribe to MetricKit and Android Vitals

`MXMetricManagerSubscriber` on iOS; Play Console Android Vitals alerts piped into the team's Slack.

### Step 6: Define SLOs and CI gating

Crash-free above 99.5 percent, cold-start P95 under 4 s, ANR under 0.1 percent. CI checks against previous release; regressions trigger investigation.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Crash reporting with symbols | Mobile Engineering Lead | Crashlytics or Sentry integrated; symbol upload validated per release | Required |
| Performance auto-instrumentation | Observability Team | Network and screen rendering metrics ingested for top-5 screens | Required |
| Event taxonomy documented | Product Analytics + Mobile | Named events with typed properties; centralised wrapper enforced | Required |
| PII redaction validated | Privacy Officer | Logs, analytics events, session replay reviewed for PII before production | Required |
| MetricKit / Android Vitals subscription | Observability Team | Daily ingestion validated; alerting wired | Required |
| SLO dashboard live | SRE / Mobile Architect | Dashboards for crash-free users, cold-start P95, ANR; release-gating logic | Required |

---

## Security Considerations

- User IDs in observability tools must be hashed (HMAC-SHA256 with a server-side salt) to prevent cross-correlation if the analytics provider is breached.
- Custom keys / context fields are reviewed for PII before introduction; a CI scan that fails the build on raw email / phone / SSN patterns in `setCustomKey` calls.
- Network request URLs may contain sensitive path segments (`/users/123/account/456/transfers/789`); URL templating in observability ensures only the template (`/users/{id}/account/{id}/transfers/{id}`) is recorded.
- Session replay recordings are sensitive artefacts; access restricted to support and engineering, retention bounded, GDPR right-to-be-forgotten requests honoured.

---

## Performance Considerations

- Crash reporting overhead under 5 ms per crash report write; negligible.
- Performance monitoring overhead under 1 percent of CPU; well within budget on tier-2 devices.
- Analytics event flush: batched and shipped on connectivity; immediate flush on critical events (purchase complete) to reduce data loss on app kill.
- Session replay overhead 3-8 percent of CPU on tier-2 devices; sample at 5-25 percent of sessions rather than 100 percent to keep budget.
- MetricKit payload ingestion happens once per day; no per-request overhead.

---

## Anti-Patterns to Avoid

### ⚠️ Symbol Upload Skipped

The Crashlytics integration is in place but symbol upload is not part of CI. Stack traces are obfuscated. The team cannot triage crashes. The fix is the CI step that uploads symbols on every release build and the gate that fails the build if upload fails.

### ⚠️ Raw User IDs Sent to Analytics

The app sets `analytics.setUserId(user.email)` because "it's convenient." The email is a direct identifier; the analytics provider becomes a PII processor. The fix is the hashed user ID (HMAC-SHA256 with server-salt) and the lint rule that flags raw PII in analytics calls.

### ⚠️ Page-View-Only Analytics

The team tracks `home_screen_viewed`, `account_screen_viewed`. They cannot answer "how many users completed checkout this week" because they didn't instrument the action. The fix is event-driven analytics with named actions and properties.

### ⚠️ Session Replay Without Masking Audit

Session replay is integrated; the configuration is "off the shelf"; the recordings include credit card numbers and SSNs typed into fields. The next compliance review is a GDPR notification. The fix is the per-screen masking audit before any session-replay rollout.

### ⚠️ No SLOs, No Gates

The team ships releases without checking the crash rate of the previous release. Regressions accumulate. The fix is the release-gating dashboard plus the CI check.

---

## AI Augmentation Extensions

### AI-Assisted Crash Triage

LLM-based analysis of crash stack traces classifies by likely root cause, suggests the file and line to investigate, and links similar historical crashes. The triage backlog compresses; the engineer's attention focuses on the genuinely novel.

### AI-Assisted Event Taxonomy Validation

Analytics events submitted to a CI gate are validated against the taxonomy by an LLM; misnamed events, missing properties, or accidentally PII-laden properties are caught before merge.

---

## References

1. [Firebase Crashlytics](https://firebase.google.com/docs/crashlytics) — *firebase.google.com*
2. [Sentry for Mobile](https://docs.sentry.io/platforms/android/) — *docs.sentry.io*
3. [Firebase Performance Monitoring](https://firebase.google.com/docs/perf-mon) — *firebase.google.com*
4. [Datadog Mobile APM](https://docs.datadoghq.com/real_user_monitoring/mobile_and_tv_monitoring/) — *docs.datadoghq.com*
5. [Apple MetricKit](https://developer.apple.com/documentation/metrickit) — *developer.apple.com*
6. [Android Vitals](https://developer.android.com/quality/performance) — *developer.android.com*
7. [Mixpanel Documentation](https://docs.mixpanel.com/) — *docs.mixpanel.com*
8. [OpenTelemetry Mobile SIG](https://github.com/open-telemetry/community/blob/main/projects/mobile.md) — *github.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/observability/` | Aligned to OpenTelemetry Mobile · Firebase · Datadog · Apple MetricKit*
