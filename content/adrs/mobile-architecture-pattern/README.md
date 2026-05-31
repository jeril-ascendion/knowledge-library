# ADR: Mobile Application Architecture Pattern Selection

> **ADR Reference:** `ADR-MOB-001`
> **Alignment:** Clean Architecture (Martin) | TOGAF Application Architecture | Google MAD | SOLID Principles
> **Audience:** Mobile Architects · Senior Engineers · Technical Leads · Security Architects · QA Lead

The architecture pattern is the highest-leverage structural decision in mobile engineering. It determines whether business logic is testable in isolation, whether security properties are auditable, and whether the codebase can scale across teams and years without accumulating irreversible structural debt.

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
| Stakeholders | Mobile Engineering Leads · Solutions Architects · Security Architecture · QA Lead · Product Management · Client CTO |

## Executive Summary

**Decision:** Clean Architecture combined with MVVM is adopted as the primary architectural pattern for all native mobile applications delivered by Ascendion. On Android: Jetpack Compose, ViewModel, Repository, Use Cases, Hilt for dependency injection. On iOS: SwiftUI, @Observable, Repository, Use Cases, Factory DI. MVVM is adopted over MVI, MVP, VIPER, and TCA based on weighted evaluation across security, performance, development speed, testability, and long-term maintainability.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Security | 25% | Financial services mandate security-by-architecture. Business logic isolation is a compliance requirement. |
| 2 | Testability | 20% | ≥ 80% unit test coverage on business logic is a mandatory delivery gate. |
| 3 | Performance | 18% | Client SLAs: < 2s cold start, 60fps rendering, < 100ms UI response. |
| 4 | Development Speed | 17% | Clear conventions reduce decision fatigue and accelerate onboarding. |
| 5 | Maintainability | 12% | Mobile applications have 3–5 year lifespans. Architecture must accommodate this. |
| 6 | Cost Optimisation | 8% | Shared patterns reduce cross-team knowledge transfer cost. |

## Considered Options

### Option A — Clean Architecture + MVVM (ADOPTED)
Three concentric rings with inward-only dependency rule. Entities (domain models, zero platform dependencies), Use Cases (business rules, returns Result types), Interface Adapters (ViewModel, Repository implementations), Frameworks & Drivers (outermost — Android SDK, UIKit, SwiftUI). ViewModel exposes StateFlow (Android) and @Observable (iOS). Testable at every layer without device or network. Weighted score: **4.62 / 5.0**

### Option B — MVI (Model-View-Intent)
Unidirectional data flow with Intent → Reducer → State → View. Excellent for complex interdependent state. Higher boilerplate. iOS ecosystem support weak at current maturity. Weighted score: 3.62 / 5.0

### Option C — MVP
Presenter is not lifecycle-aware — superseded by ViewModel in 2018. Not permitted for new projects. Legacy MVP codebases must document a migration plan. Weighted score: 2.96 / 5.0 — DISMISSED

### Option D — VIPER
iOS-only. Five files per screen. Poor SwiftUI compatibility. Cannot share pattern knowledge with Android team. Weighted score: 3.72 / 5.0

### Option E — TCA (The Composable Architecture)
Best-in-class iOS testability. iOS-only — no Android equivalent. 4–6 week onboarding for new engineers. Third-party dependency risk. Weighted score: 3.61 / 5.0

## Decision

Clean Architecture + MVVM is mandatory for all new native mobile projects from May 2025. The Dependency Rule is non-negotiable: all source code dependencies point inward. Domain layer must never import Presentation or Data layers.

**Mandatory Security Rules:**
1. ALL network calls originate from the Data layer only — network call in ViewModel is a blocking code review finding
2. Credentials: Android Keystore + EncryptedSharedPreferences; iOS Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly
3. OAuth 2.0 + PKCE is the only permitted authentication flow
4. All PII fields annotated with @Pii (Kotlin) or @Masked (Swift) — stripped from logs by ProGuard rule

**Mandatory Test Coverage:**

| Layer | Target | Tooling |
|---|---|---|
| Use Cases | ≥ 90% line coverage | JUnit5 + Mockk / XCTest + Swift Testing |
| ViewModels | ≥ 80% line coverage | Turbine (Flow) / Combine-schedulers |
| Repository | Integration tests per method | Room in-memory / URLProtocol stub |
| UI Components | Snapshot all states | Paparazzi / iOSSnapshotTestCase |

## Trade-off Analysis

| Trade-off Accepted | Consequence | Mitigation |
|---|---|---|
| Boilerplate per screen | A simple read screen requires entity, interface, impl, Use Case, ViewModel, View | Accepted explicitly. Discipline prevents spaghetti patterns that destroy maintainability at scale. |
| DI configuration complexity | Hilt module graph requires understanding for new engineers | Golden path scaffolding generates boilerplate automatically. 1-day onboarding target. |
| Kotlin/Swift language split | No shared UI code between Android and iOS | Shared domain logic via KMP where teams are large enough to justify it. |

## Implementation Guidance

1. Generate new feature modules using the golden path scaffold — do not copy existing modules
2. Domain layer classes are in separate Gradle/SPM modules with no Android SDK or UIKit imports
3. ViewModel maximum 200 lines — mandatory ARB review if exceeded
4. Use Case has a single execute() method returning Result<T, DomainError>
5. Repository interface defined in domain module; implementation in data module
6. StateFlow for ongoing state; SharedFlow with replay=0 for one-time navigation events
7. JaCoCo (Android) and Xcode Coverage (iOS) gates enforced in CI before PR merge

## Compliance Checkpoints

| Checkpoint | Trigger | Owner | SLA |
|---|---|---|---|
| Architecture Pattern Review | Every new mobile project kickoff | Solutions Architect | Before sprint 1 |
| Layer Boundary Violation | Any PR with network call in ViewModel | Tech Lead code review | Block PR merge |
| Coverage Gate | Every PR — automated CI | CI Pipeline | Real-time |
| ViewModel Size Review | Any ViewModel exceeding 200 lines | ARB | Within 5 business days |
| Security Pattern Audit | Before first production release | Security Architect | Release gate |

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-002 | Mobile Platform Selection | Platform governs which technology implements this pattern |
| ADR-MOB-003 | Mobile CI/CD Pipeline | Test coverage gates enforced by CI reference this ADR |
| ADR-SEC-011 | Mobile Security Controls | Security controls designed around the layer boundaries defined here |
| ADR-INT-005 | BFF API Design | Repository interface design maps to BFF endpoints |

## References

1. Martin, Robert C. — Clean Architecture. Prentice Hall, 2017.
2. Google — Android App Architecture Guide. developer.android.com/topic/architecture
3. Google — Now in Android (reference implementation). github.com/android/nowinandroid
4. Point-Free — The Composable Architecture. github.com/pointfreeco/swift-composable-architecture
5. Fowler, Martin — Patterns of Enterprise Application Architecture. Addison-Wesley, 2002.

> **⚠ God ViewModel** — ViewModel exceeds 200 lines handling networking, business logic, navigation, analytics, and error handling simultaneously. Untestable and a constant merge conflict source in teams larger than 3.
> **CORRECT:** Business logic in Use Cases. Navigation events as a sealed class. Each concern in its own class. ARB review triggers mandatory refactor before the PR is merged.

> **⚠ Network Call in ViewModel** — viewModelScope.launch { val data = apiService.get() } in a ViewModel class. Security boundary violated. Untestable without mocking the entire network stack.
> **CORRECT:** ViewModel calls Use Case. Use Case calls Repository interface. Repository implementation calls API client. Each layer is independently testable.

> **⚠ Domain Models with Android Annotations** — @Entity data class Account(...) used as both the Room database entity and the domain model. Imports Room into the domain layer, violating the Dependency Rule.
> **CORRECT:** Separate domain models (data class Account) from data layer entities (@Entity data class AccountEntity). Repository implementations map between them.
