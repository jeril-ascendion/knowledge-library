# Mobile Application Architecture Pattern Selection

> **ADR Reference:** `ADR-MOB-001`
> **Alignment:** Clean Architecture (Martin) | TOGAF Application Architecture | Google MAD Architecture Guide | SOLID Principles
> **Audience:** Mobile Architects · Senior Engineers · Technical Leads · Security Architects · QA Lead

The architecture pattern is the structural template governing code organisation, dependency flow, testability, security auditability, and long-term maintainability. This is the highest-leverage architectural decision in mobile engineering — it determines whether business logic is isolated and testable, whether security properties are auditable, and whether the codebase can scale across teams and years.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-MOB-001 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice — Ascendion |
| Status | ACCEPTED |
| Domain | Mobile Architecture |
| ARB Approval | Required |

## Executive Summary

Clean Architecture combined with MVVM is adopted as the primary architectural pattern for all native mobile applications delivered by Ascendion. On Android: Jetpack Compose, ViewModel, Repository, Use Cases, Hilt for DI. On iOS: SwiftUI, @Observable, Repository, Use Cases, Factory DI. MVVM is adopted over MVI, MVP, VIPER, and TCA based on weighted evaluation across security, performance, development speed, testability, and long-term maintainability.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Security | 25% | Financial services mandate security-by-architecture. Business logic isolation is a compliance requirement. |
| 2 | Testability | 20% | > 80% unit test coverage on business logic is a delivery gate. |
| 3 | Performance | 18% | Client SLAs: < 2s cold start, 60fps rendering, < 100ms UI response. |
| 4 | Development Speed | 17% | Clear conventions reduce decision fatigue and accelerate onboarding. |
| 5 | Maintainability | 12% | Mobile apps have 3–5 year lifespans. |
| 6 | Cost Optimisation | 8% | Shared patterns reduce cross-team knowledge transfer cost. |

## Considered Options

### Option A — Clean Architecture + MVVM (ADOPTED)
Three concentric rings: Entities (innermost, zero platform dependencies), Use Cases (application business rules), Interface Adapters (ViewModel, Repository implementations), Frameworks & Drivers (outermost). Dependency Rule: all source code dependencies point inward. ViewModel exposes StateFlow on Android and @Observable on iOS. Testable at every layer without device or network.

Weighted score: **4.62 / 5.0**

### Option B — MVI (Model-View-Intent)
Unidirectional data flow. Intent → Reducer → immutable State → View. Excellent for complex interdependent state screens. Performance cost from immutable data class copy on high-frequency updates. iOS ecosystem support weak.

Weighted score: 3.62 / 5.0

### Option C — MVP
Presenter is not lifecycle-aware. Replaced by ViewModel in 2018. New projects must not adopt MVP. Legacy MVP codebases plan migration.

Weighted score: 2.96 / 5.0 — DISMISSED

### Option D — VIPER
iOS-only. Five files per screen. Designed for UIKit era — poor SwiftUI compatibility. Cannot share pattern knowledge with Android team.

Weighted score: 3.72 / 5.0

### Option E — TCA (The Composable Architecture)
Best-in-class iOS testability. iOS-only — no Android equivalent at comparable maturity. 4-6 week onboarding for new engineers. Third-party dependency risk (Point-Free).

Weighted score: 3.61 / 5.0

## Layer Structure

| Layer | Android Package | iOS Module |
|---|---|---|
| Presentation | com.client.app.feature.{screen}.ui | Features/{Screen}/Presentation |
| ViewModel | com.client.app.feature.{screen}.viewmodel | Features/{Screen}/ViewModel |
| Domain | com.client.app.domain.usecase.{feature} | Domain/UseCases/{Feature} |
| Domain Models | com.client.app.domain.model | Domain/Models |
| Repository Interface | com.client.app.domain.repository | Domain/Repositories (protocols) |
| Data | com.client.app.data.repository.{feature} | Data/Repositories/{Feature} |
| Remote Source | com.client.app.data.remote.{feature} | Data/Remote/{Feature} |
| Local Source | com.client.app.data.local.{feature} | Data/Local/{Feature} |

## Mandatory Test Coverage

| Layer | Coverage Target | Tooling |
|---|---|---|
| Use Cases | ≥ 90% line coverage | JUnit5 + Mockk / XCTest + Swift Testing |
| ViewModels | ≥ 80% line coverage | Turbine (Flow) / Combine-schedulers |
| Repository | Integration tests per method | Room in-memory / URLProtocol stub |
| UI | Snapshot all component states | Paparazzi / iOSSnapshotTestCase |

## Non-Negotiable Security Rules

1. ALL network calls originate from the Data layer only. Network call in ViewModel = blocking code review finding.
2. Credential storage: Android Keystore + EncryptedSharedPreferences. iOS Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly.
3. Certificate pinning mandatory for financial and health data apps.
4. OAuth 2.0 + PKCE is the only permitted authentication flow. client_secret in mobile binary = P0 security finding.
5. All PII fields annotated with @Pii (Kotlin) or @Masked (Swift) — stripped from logs by ProGuard/SwiftLint rule.

## Anti-Patterns to Avoid

### 1. God ViewModel
ViewModel exceeds 200 lines handling networking, business logic, navigation, analytics, and error handling simultaneously. Untestable and a constant merge conflict source.

**CORRECT:** Maximum 200 lines. Business logic in Use Cases. Navigation events as sealed class. Each concern in its own class. ARB review triggers mandatory refactor.

### 2. Network Call in ViewModel
ViewModel calls apiService.getAccount() directly. Security boundary violated. Untestable without full network stack mock.

**CORRECT:** ViewModel calls Use Case. Use Case calls Repository interface. Repository implementation calls API client.

### 3. Domain Models with Android Annotations
`@Entity data class Account` breaks the Dependency Rule by importing Room into the domain layer.

**CORRECT:** Separate domain models from data layer entities. Repository implementations map between them.

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-002 | Mobile Platform Selection | Platform governs which tech implements this pattern |
| ADR-MOB-003 | Mobile CI/CD Pipeline | Test coverage gates enforced by CI reference this ADR |
| ADR-SEC-011 | Mobile Security Controls | Security controls designed around layer boundaries here |
| ADR-INT-005 | BFF API Design | Repository interface design maps to BFF endpoints |

## References

1. Martin, Robert C. — Clean Architecture. Prentice Hall, 2017.
2. Google — Android Architecture Guide. developer.android.com/topic/architecture
3. Google — Now in Android (reference implementation). github.com/android/nowinandroid
4. Point-Free — The Composable Architecture. github.com/pointfreeco/swift-composable-architecture
5. Fowler, Martin — Patterns of Enterprise Application Architecture. Addison-Wesley, 2002.
