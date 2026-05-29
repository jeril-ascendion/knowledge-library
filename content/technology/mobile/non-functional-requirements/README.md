# Non-Functional Requirements (NFRs)

> **Section:** `technology/mobile/non-functional-requirements/`
> **Alignment:** ISO 25010 Software Quality Model | Google Android Vitals | Apple MetricKit | OWASP MASVS | WCAG 2.2
> **Audience:** Solutions Architects · Product Managers · QA Architects · Mobile Engineering Leads

Non-functional requirements define the quality envelope within which a mobile application must operate. They are frequently treated as aspirational — mentioned in the kickoff, forgotten during development, and rediscovered as production incidents. At Ascendion, NFRs are specified as measurable, testable criteria before development begins, with CI gates that surface regressions continuously rather than at release.

## Overview

Mobile NFRs differ from backend NFRs in one critical dimension: the measurement environment is hostile and heterogeneous. A backend service runs in a controlled data centre on known hardware. A mobile application runs on thousands of device models, across six major Android versions, across variable network conditions from gigabit Wi-Fi to 2G cellular, in contexts ranging from a banker reviewing a transaction at a desk to a field worker scanning documents in direct sunlight on a cracked screen.

NFRs must be specified with this hostile environment in mind. "The app shall be fast" is not an NFR. "Cold start shall complete in under 2.0 seconds on the 25th-percentile Android device (3-year-old mid-range) measured by Firebase Performance Monitoring across the production user base" is an NFR.

## NFR Categories and Standards

### Performance
Cold start (process not in memory): under 2.0 seconds on median device. Warm start: under 200 milliseconds. Hot start: under 100 milliseconds. Sustained frame rate: 60fps with no jank frames exceeding 16.67ms. Time to interactive on critical screens: under 1.5 seconds. Network payload per session: defined per app vertical (financial apps typically under 500KB per session on cellular).

### Reliability
Crash-free users rate: above 99.5% measured by Firebase Crashlytics across the production install base. ANR (Application Not Responding) rate on Android: below 0.2%. Force-close rate: below 0.1%. Successful API call rate: above 99.0% (failures isolated at the Repository layer with retry).

### Availability
The mobile application itself is always available (it is on-device). The NFR is the graceful degradation under network unavailability — the application must remain usable for read operations using cached data when network is unavailable, with clear staleness indicators.

### Security
OWASP MASVS Level 1 minimum for all applications. Level 2 mandatory for financial services, healthcare, and government. Mandatory controls: hardware-backed credential storage, OAuth 2.0 + PKCE, TLS 1.2 minimum, certificate pinning for regulated apps, no PII in logs.

### Accessibility
WCAG 2.2 Level AA compliance for all screens. All interactive elements must have accessible labels. Dynamic Type / font scaling must be supported across all 12 size categories. Touch target minimum: 48×48dp Android, 44×44pt iOS. Colour contrast ratio: 4.5:1 for normal text, 3:1 for large text.

### Maintainability
Test coverage: Use Cases above 90%, ViewModels above 80%. Code duplication below 5% (measured by SonarQube). Technical debt ratio below 10%. Build time under 5 minutes for a full clean build (enforced by Gradle build caching and modularisation).

### Battery and Resource Efficiency
Background battery usage below 2% per hour when app is backgrounded with no active work. Memory baseline below 150MB on the median device. Wake lock acquisitions: zero unless actively processing user-requested background work (WorkManager on Android, BGTaskScheduler on iOS).

## NFR Measurement Tooling

| NFR Category | Primary Tool | Secondary Tool | Gate |
|---|---|---|---|
| Performance | Firebase Performance | Jetpack Macrobenchmark / Instruments | CI regression alert |
| Reliability | Firebase Crashlytics | Google Play Android Vitals | 99.5% crash-free SLA |
| Security | OWASP Dependency Check | Detekt Security / SwiftLint | CI block on P1/P2 CVE |
| Accessibility | Accessibility Scanner | Accessibility Inspector (Xcode) | Pre-release audit |
| Coverage | JaCoCo / Xcode Coverage | SonarQube | PR gate |
| Build Time | Gradle Build Scan | — | 5-minute ceiling |

## Anti-Patterns to Avoid

> **⚠ NFRs as Aspirations** — Performance and reliability requirements written as "the app should be fast and stable" with no measurement methodology or threshold.
> **CORRECT:** Every NFR has a numeric threshold, a measurement tool, a measurement frequency, and a responsible owner. NFRs are reviewed in sprint retrospectives, not only in post-incident reviews.

> **⚠ Testing NFRs Only at Release** — Running performance benchmarks and accessibility audits only before the App Store submission, discovering regressions with no time to fix them.
> **CORRECT:** Performance benchmarks run in CI on every PR. Accessibility checks run on every UI component. Crash-free rate monitored continuously in production dashboards.

## References

1. ISO/IEC 25010:2011 — Systems and Software Quality Requirements and Evaluation (SQuaRE).
2. Google — Android Vitals. play.google.com/console/about/vitals
3. W3C — Web Content Accessibility Guidelines 2.2. w3.org/TR/WCAG22
4. OWASP — Mobile Application Security Verification Standard v2.0.
5. Apple — MetricKit Documentation. developer.apple.com/documentation/metrickit
