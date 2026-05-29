# Enterprise Mobile Architecture — Banking Applications

> **ADR Reference:** `ADR-ENT-MOB-001`
> **Alignment:** TOGAF | OWASP MASVS 2.0 | BSP Circular 982 | PCI-DSS v4.0 | PDPA Philippines | ISO 27001
> **Audience:** Enterprise Architects · Engineering Leadership · Mobile Architects · Security Teams · Compliance · Delivery Managers

Enterprise mobile architecture for banking applications is a systems-level discipline that spans engineering principles, non-functional requirements, security compliance, platform decisions, and long-term governance. This ADR is the authoritative reference for all mobile front-end decisions on banking and financial services programmes delivered by Ascendion.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-ENT-MOB-001 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice — Ascendion |
| Status | ACCEPTED |
| Domain | Enterprise Mobile Architecture — Banking |
| ARB Approval | Required |
| Scope | iOS and Android Mobile Front End — backend integration points where relevant to mobile contract obligations |

## Executive Summary

The Enterprise Mobile Banking ADR mandates a security-first, reliability-driven mobile architecture for all banking and financial services mobile applications. Clean Architecture with MVVM governs internal structure. OAuth 2.0 + PKCE governs all authentication. OWASP MASVS Level 2 is the mandatory security compliance target. Offline-capable, observable, and deterministic state management is required across all critical user journeys. The architecture treats security over convenience, reliability over velocity, and explicit dependencies over implicit coupling as non-negotiable engineering principles.

## Engineering Principles

### 1. Security Over Convenience
When security requirements and user convenience conflict, security wins unconditionally. This governs authentication session lifetimes, biometric re-authentication gates before high-value transactions, certificate pinning enforcement, and the prohibition of sensitive data in application caches. Feature requests that require relaxing security controls require a Security Architecture Exception signed by the CISO.

### 2. Reliability Over Feature Velocity
A degraded but stable application is always preferable to a fast-moving but unstable one. New features ship behind flags disabled by default. Crash-free session targets gate release approvals. The architecture tolerates deliberate capability reduction rather than undefined behaviour under partial failures.

### 3. Explicit Dependencies Over Implicit Coupling
All module dependencies must be declared, visible, and enforced at compile time. This drives the feature-module architecture, dependency injection containers, and the prohibition of service locators and ambient contexts.

### 4. Backward Compatibility by Default
Any change to a public API, module contract, or shared schema must preserve backward compatibility unless a formal deprecation process has been completed. Breaking changes require a minimum 90-day deprecation window with parallel support.

### 5. Observable Systems Over Opaque Systems
Any behaviour that cannot be observed in production cannot be trusted, debugged, or governed. All critical flows emit structured telemetry. Unobservable states are treated as architectural defects.

### 6. Fail-Safe Degradation Over Catastrophic Failure
Under adverse conditions the application must degrade gracefully to a safe, communicative state rather than crash or exhibit undefined behaviour. The application must always tell users what it cannot do and why.

### 7. Prefer Compile-Time Safety
Errors detected at compile time are categorically superior to errors detected at runtime, especially in financial workflows. This drives the choice of Swift and Kotlin, the use of sealed types, and the prohibition of force-unwrapping in production code.

### 8. Defensive Programming for Financial Workflows
All code handling financial transactions must assume inputs are malformed, network conditions are adversarial, and concurrent operations are possible. All transaction submission flows implement idempotency keys. All monetary values use fixed-precision decimal types, never floating-point.

## Non-Functional Requirements

| NFR Category | Metric | Target | Gate |
|---|---|---|---|
| Crash-free session rate | Firebase Crashlytics | ≥ 99.9% | Release gate |
| ANR-free session rate (Android) | Google Play Vitals | ≥ 99.95% | Release gate |
| Cold launch time P50 | Custom telemetry | ≤ 2.0s | Release gate |
| Cold launch time P95 | Custom telemetry | ≤ 3.5s | Monitoring |
| Frame rate | Systrace / Instruments | 60fps sustained | Release gate |
| Transaction submission latency P95 | APM tracing | ≤ 3.0s | Alert threshold |
| Auth token expiry enforcement | Session audit | 100% compliance | Continuous |
| Offline mode availability | Functional test suite | 100% of classified flows | Release gate |
| Accessibility compliance | WCAG 2.2 AA | All customer-facing screens | Release gate |

## Core Architecture

### Layer Boundaries — Clean Architecture
**Entities (Domain):** Pure Kotlin/Swift. Zero Android/iOS imports. Domain models, repository interfaces, business invariants. **Use Cases:** Application business rules. One Use Case per operation. Returns Result types. **Interface Adapters:** ViewModel, Repository implementations, DTO mappers, API clients. **Frameworks & Drivers:** Android SDK, UIKit, SwiftUI, Retrofit, Room, Hilt, Factory DI. Dependencies point only inward.

### Presentation Pattern — MVVM
ViewModel holds observable UiState as StateFlow (Android) or @Observable (iOS). View observes state and sends events — never writes state directly. No UI framework imports in the domain layer. Business logic lives in Use Cases, not ViewModels.

### Security Architecture
OAuth 2.0 + PKCE mandatory for all authentication flows. Hardware-backed credential storage: Android Keystore + EncryptedSharedPreferences; iOS Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly. SPKI hash certificate pinning for all financial API endpoints. Google Play Integrity API (Android) and Apple AppAttest (iOS) for runtime attestation. Biometric MFA mandatory for transactions above risk thresholds. PII never in logs, caches, or crash reports.

### Offline and Reliability
Local database (Room/SwiftData) as single source of truth. All network responses written to local DB before UI renders. Delta sync with since-timestamp watermark. Circuit breaker and exponential backoff with jitter for all API calls. WorkManager (Android) and BGTaskScheduler (iOS) for guaranteed background sync.

## Decision Summary

| Decision | Outcome |
|---|---|
| Architecture Pattern | Clean Architecture + MVVM (ADR-MOB-001) |
| Platform | Flutter default; Native when perf/API required (ADR-MOB-002) |
| Authentication | OAuth 2.0 + PKCE mandatory |
| Security Baseline | OWASP MASVS Level 2 for banking (ADR-SEC-011) |
| API Integration | BFF pattern mandatory (ADR-INT-005) |
| CI/CD | Fastlane + GitHub Actions (ADR-MOB-003) |
| Offline Strategy | Local DB as single source of truth |
| State Management | MVVM with StateFlow / @Observable |

## Anti-Patterns to Avoid

### 1. Floating-Point for Monetary Values
Using float or double for currency calculations produces rounding errors in financial computations.

**CORRECT:** Use BigDecimal (Java/Kotlin) or Decimal (Swift) exclusively for all monetary values.

### 2. Credentials in SharedPreferences / UserDefaults
Storing session tokens or credentials in plaintext storage readable on rooted/jailbroken devices.

**CORRECT:** Android Keystore + EncryptedSharedPreferences. iOS Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly. Blocking P1 security finding.

### 3. Implicit OAuth Flow for Banking
Using OAuth Implicit Flow exposes access tokens in URL fragments visible in server logs and referrer headers.

**CORRECT:** OAuth 2.0 Authorization Code + PKCE exclusively.

## Regulatory References

- BSP Circular 982 — Philippines banking mobile security requirements
- PDPA Philippines (RA 10173) — Personal data protection
- PCI-DSS v4.0 — Payment card data security
- HIPAA — Healthcare PHI handling (where applicable)
- OWASP MASVS 2.0 — Mobile application security standard

## References

1. OWASP — Mobile Application Security Verification Standard v2.0. owasp.org/www-project-mobile-app-security
2. BSP Circular 982. bsp.gov.ph
3. Google — Android App Architecture Guide. developer.android.com/topic/architecture
4. Apple — Human Interface Guidelines. developer.apple.com/design/human-interface-guidelines
5. IETF RFC 7636 — PKCE. tools.ietf.org/html/rfc7636
6. NIST SP 800-163 — Vetting Mobile Applications. csrc.nist.gov
