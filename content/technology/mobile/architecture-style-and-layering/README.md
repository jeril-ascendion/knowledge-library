# Architecture Style and Layering

> **Section:** `technology/mobile/architecture-style-and-layering/`
> **Alignment:** Clean Architecture (Martin) | TOGAF Application Architecture | Google MAD Architecture Guide | SOLID
> **Audience:** Mobile Architects · Senior Engineers · Tech Leads

The architecture style is the structural template that determines how code is organised, how dependencies flow, and where each concern lives. Choosing the wrong style — or applying the right style inconsistently — is the single highest-leverage decision in mobile software architecture because it determines the testability, security auditability, and long-term maintainability of the entire codebase.

## Overview

Ascendion adopts Clean Architecture as the structural framework and MVVM as the presentation layer pattern for all native mobile applications. This combination is specified in ADR-MOB-001. This section explains the reasoning, the layer responsibilities, the dependency rules, and the specific mapping to Android and iOS implementation constructs.

## The Three-Ring Model

Clean Architecture defines three concentric rings with a strict inward-only dependency rule. Source code dependencies must only point inward — never outward.

**Entities (innermost):** Domain models and repository interfaces. Pure Kotlin or Swift — zero Android SDK or UIKit imports. An Entity has no knowledge that Android or iOS exists. Repository interfaces define the contract that the data layer must satisfy, but contain no implementation.

**Use Cases:** Application business rules. One Use Case per business operation. Takes repository interfaces as constructor dependencies. Returns Result types. Unit-testable with mocked repository interfaces — no device, emulator, or network required. This is the layer where business validation, orchestration, and decision logic lives.

**Interface Adapters and Frameworks (outermost rings):** ViewModels, Repository implementations, API clients, Room DAOs, SwiftData models, Hilt modules, Factory DI configurations. All platform-specific code lives here. The boundary between the outermost ring and the middle ring is the primary integration test boundary.

## MVVM in the Presentation Layer

The ViewModel sits in the Interface Adapters ring. It imports the UI framework's lifecycle management (Android ViewModel, Combine's ObservableObject or Swift's @Observable) but imports no domain models' platform dependencies. It holds UI state as a StateFlow (Android) or @Observable property (iOS). It processes user events by delegating to Use Cases. It never calls a Repository directly — only through Use Cases.

The View (Compose UI or SwiftUI) observes ViewModel state and sends events. The View contains no business logic. The View does not call Use Cases. The View does not call Repositories. A Compose composable that calls `repository.getAccount()` is an architectural violation.

## Module Structure

On Android, each feature is a Gradle module. The module contains: `ui` package (Compose composables), `presentation` package (ViewModel, UiState), `domain` package (Use Cases, domain models, repository interfaces), `data` package (Repository implementations, DTO classes, data source classes). The `:core:domain` module contains shared domain models. `:core:network` contains shared API client infrastructure. Feature modules declare dependencies only on `:core:domain` and `:core:network` — never on other feature modules.

On iOS, each feature is a Swift Package target. The same layering applies through Swift access control: `internal` types within the feature, `public` protocols and models across feature boundaries.

## Anti-Patterns to Avoid

> **⚠ Network Calls in ViewModel** — ViewModel calling `apiService.getAccount()` directly, bypassing Use Cases and Repositories. Business logic bleeds into the presentation layer. Untestable without mocking the entire network stack.
> **CORRECT:** ViewModel calls `getAccountUseCase.execute(accountId)`. Use Case calls `accountRepository.getAccount(accountId)`. Repository calls `apiService.getAccount(accountId)`. Each layer is independently testable.

> **⚠ Domain Models with Android Annotations** — `@Entity data class Account(...)` as both the Room database entity and the domain model. Creates a direct dependency from the domain layer on the Room framework. Violates the inward-only dependency rule.
> **CORRECT:** Separate domain models (`data class Account`) from data layer entities (`@Entity data class AccountEntity`). Repository implementations map between them.

## References

1. Martin, Robert C. — Clean Architecture. Prentice Hall, 2017.
2. Google — Guide to App Architecture. developer.android.com/topic/architecture
3. Google — Now in Android. github.com/android/nowinandroid
4. Richards, Mark and Ford, Neal — Fundamentals of Software Architecture. O'Reilly, 2020.
