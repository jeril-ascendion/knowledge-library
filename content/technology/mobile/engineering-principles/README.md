# Engineering Principles

> **Section:** `technology/mobile/engineering-principles/`
> **Alignment:** SOLID Principles | 12-Factor App | Google MAD | Apple HIG | Clean Code (Martin)
> **Audience:** All Mobile Engineers · Architects · Tech Leads

Mobile engineering principles are not abstract rules — they are hard-won constraints derived from the failure modes that appear repeatedly in production mobile applications at scale. Every principle below maps to a class of defects, a category of technical debt, or a team coordination failure that Ascendion has observed across financial services, healthcare, and government mobile engagements.

## Overview

The difference between a mobile application that ships cleanly and one that accumulates entropy across releases is not talent. It is discipline — the consistent application of a shared set of engineering principles that every team member internalises and every code review enforces. These principles operate at three levels: the individual component (how a single class or function is written), the layer (how components relate to their layer), and the system (how the application relates to the platform and the network).

Applying these principles consistently reduces onboarding time, makes test coverage achievable, enables safe refactoring, and — most critically in regulated industries — makes security properties auditable rather than hoped for.

## Core Principles

### 1. Single Responsibility at Every Layer
Each class, function, and module has one reason to change. The ViewModel formats data for display — it does not fetch from the network. The Repository decides where data comes from — it does not transform it for the UI. The Use Case encodes one business operation — it does not manage lifecycle. Violating SRP is the root cause of the Massive View Controller and the God ViewModel — the two most common structural defects in mobile codebases.

### 2. Dependency Inversion — Depend on Abstractions
The domain layer depends on repository interfaces, not repository implementations. ViewModels depend on Use Case interfaces, not concrete Use Cases. This inversion enables testing without real network or database dependencies and enables implementations to be swapped without changing business logic. In Kotlin: `interface AccountRepository` in the domain module; `class AccountRepositoryImpl : AccountRepository` in the data module. In Swift: `protocol AccountRepository` in the domain target; `class AccountRepositoryImpl: AccountRepository` in the data target.

### 3. Platform Agnosticism in Business Logic
Business logic must not know it is running on Android or iOS. Use Cases are pure Kotlin or Swift with no Android SDK or UIKit imports. This is not merely a testing convenience — it is an architectural boundary that prevents the platform from leaking into the business domain. When Kotlin Multiplatform is used, platform-agnostic Use Cases compile to both platforms without modification.

### 4. Immutability as Default
Mutable shared state is the primary source of race conditions in concurrent mobile applications. Default to immutable data classes (`data class` in Kotlin, `struct` in Swift). Use `val` over `var`. Use `StateFlow` (immutable emission) over `MutableStateFlow` exposed to the UI. When mutation is necessary, isolate it behind a single actor or coroutine scope.

### 5. Explicit over Implicit
Side effects must be visible in the code structure — not hidden in property observers, implicit lifecycle hooks, or global singletons. A ViewModel that makes a network call inside `init` is an implicit side effect. A ViewModel that exposes a `loadAccount()` function called explicitly by the View is explicit. Explicit code is debuggable, testable, and reviewable.

### 6. Fail Fast in Development, Fail Gracefully in Production
StrictMode (Android) and Thread Sanitizer (iOS) are enabled in debug builds to surface violations at development time. In production, every failure has an explicit recovery path: retry with exponential backoff for transient network failures, graceful degradation to cached data for persistent failures, clear user messaging for unrecoverable states. No silent failures, no swallowed exceptions.

### 7. Test at the Right Layer
Unit tests test Use Cases and ViewModels without a device. Snapshot tests test visual components without a device. Integration tests test Repository plus data source without a device. UI tests run on a device only for the critical user journeys. The test pyramid is an economic principle: faster, cheaper tests at the base; slower, more expensive tests at the apex.

### 8. Performance as a First-Class Requirement
Performance requirements are specified before development and measured by CI. Cold start time, frame rate, memory baseline, and network payload size are metrics in the pull request, not afterthoughts in the release note. A composable that causes unnecessary recomposition or a coroutine launched on the wrong dispatcher is a defect, not a style preference.

## Implementation Guidance

Apply these principles through four mechanisms: code review checklists that check each principle explicitly, static analysis rules (Detekt for Kotlin, SwiftLint for Swift) that automate enforcement of the most common violations, architecture fitness functions that run in CI to catch layer boundary violations, and architecture decision records that document why each principle applies to the specific project context.

## Anti-Patterns to Avoid

> **⚠ God ViewModel** — A ViewModel that grows to handle every screen concern: networking, business logic, UI formatting, navigation, error handling, analytics. Becomes untestable and a merge conflict magnet for large teams.
> **CORRECT:** Separate Use Cases handle each business operation. ViewModel delegates to Use Cases and focuses on UI state transformation only. Maximum 200 lines before a mandatory refactor review.

> **⚠ Implicit Singleton Dependencies** — `UserManager.instance.getCurrentUser()` called from a ViewModel without injection. Creates invisible coupling, prevents testing, and hides the dependency graph.
> **CORRECT:** Inject all dependencies through the constructor. Use Hilt (Android) or Factory (iOS) for dependency injection. Every dependency is visible in the constructor signature.

> **⚠ Lifecycle Ignorance** — Coroutines launched without lifecycle awareness, leading to operations continuing after the screen is gone. Resources allocated in `onCreate` never released in `onDestroy`.
> **CORRECT:** Use `viewModelScope` for ViewModel coroutines. Use `lifecycleScope.launchWhenStarted` for View coroutines. Match every allocation with a corresponding release.

## References

1. Martin, Robert C. — Clean Architecture: A Craftsman's Guide to Software Structure and Design. Prentice Hall, 2017.
2. Google — Android Architecture Guide. developer.android.com/topic/architecture
3. Apple — Swift API Design Guidelines. swift.org/documentation/api-design-guidelines
4. Fowler, Martin — Refactoring: Improving the Design of Existing Code. 2nd Ed. Addison-Wesley, 2018.
5. Google — Now in Android (reference implementation). github.com/android/nowinandroid
