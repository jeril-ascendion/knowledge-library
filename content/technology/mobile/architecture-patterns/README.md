# Mobile Architecture Patterns

MVC, MVVM, MVI, Clean Architecture, VIPER, and TCA — when to choose which structural pattern, on which platform, at which team size, and how to recognise the cargo-cult version of each.

**Section:** `technology/mobile/` | **Subsection:** `architecture-patterns/`
**Alignment:** Robert C. Martin Clean Architecture | Android Architecture Guidelines | Apple HIG | Point-Free TCA
**Audience:** Mobile Engineers · Mobile Architects · Technical Leads

---

## Overview

The mobile architecture pattern debate is older than the platforms themselves. Every five years the platform vendor publishes a new "guidance" that codifies whichever pattern is in fashion, every senior engineer brings the pattern from their last job, and every junior engineer learns the pattern from a tutorial that may or may not reflect what their team has chosen. The result is the most common mobile architecture issue in 2026: inconsistency within a single codebase, with five screens following five subtly different versions of "MVVM" and the sixth screen being VIPER because the engineer who joined last quarter learned it that way.

The patterns themselves are not interchangeable. MVC's separation is weak by modern standards. MVVM provides clean test boundaries but no opinion about state transitions. MVI enforces unidirectional flow at the cost of boilerplate. Clean Architecture provides discipline around dependency direction but says nothing about UI. VIPER provides five files per screen for thorough separation but ages poorly under SwiftUI. TCA composes scalably and is testable to the byte but locks the architecture to Point-Free's framework. The right pattern for a five-engineer startup ships is not the right pattern for a hundred-engineer banking app.

The architectural shift is not "we use MVVM." It is: **the codebase picks one structural pattern, documents the canonical implementation as an ADR with an exemplar screen, enforces the pattern in code review with explicit allowance for documented exceptions, and revisits the pattern only when the team or app scale changes the trade-offs that drove the original decision.**

---

## Core Principles

### 1. Pattern consistency beats pattern perfection

The fifth-best pattern applied consistently across 100 screens is better than the best pattern applied to 60 screens with 40 outliers. New joiners onboard in days against a consistent codebase and in months against a fragmented one. Consistency is the meta-pattern.

### 2. Pick the pattern at the team-size and complexity tier

A solo engineer's app does not need TCA; a 50-engineer banking app does not survive on vanilla MVC. The decision matrix names team size and app complexity; the pattern follows.

### 3. State is the integration boundary

In every modern pattern (MVVM, MVI, TCA, Compose / SwiftUI), the integration boundary between the UI and the rest of the system is a state value that the UI reads. Mutations are explicit and named (events, intents, actions). The era of two-way data binding and KVO-driven UI is over for new code.

### 4. The dependency rule points inward

Clean Architecture's dependency rule — domain depends on nothing, presentation depends on domain, data depends on domain, framework depends on data and presentation — is the single most-violated principle in mobile codebases. The fix is package-level visibility (Kotlin `internal`, Swift `public`/`internal` with module boundaries) and CI tests (Konsist on Kotlin, dependency-graph linting on Swift) that fail the build on violations.

### 5. Patterns evolve; codebases drift

Even with discipline, a codebase drifts from its declared pattern. The architect's job is to surface the drift quarterly and either codify the drift as a pattern update or correct the drift via refactor. Drift unchallenged becomes the new pattern by accident.

### 6. The pattern decision is platform-aware

Vanilla MVVM works on both platforms; TCA is iOS-only; MVI maps well to Kotlin's sealed classes and Compose's state model. The pattern must be plausible on both platforms if the codebase is cross-platform, or platform-appropriate if the codebase is pure native.

---

## Architecture Deep-Dive

**MVC and the Massive View Controller Problem**

iOS's UIKit-era MVC put the View Controller between View and Model. In practice, the View Controller absorbed everything — view assembly, model fetching, business logic, navigation, validation — and grew to 3,000-line classes that resisted testing and code review. The problem was not MVC per se; it was that UIKit's lifecycle hooks (`viewDidLoad`, `viewWillAppear`, gesture handlers) lived on the View Controller, which made it the natural place for logic to accumulate. MVVM emerged as the fix: extract a ViewModel that owns state and behaviour, leaving the View Controller as a thin coordinator.

**MVVM In Depth**

The ViewModel has no UIKit or SwiftUI imports on iOS, no Activity or Fragment references on Android. It exposes observable state — `StateFlow<UiState>` on Android, `@Observable var state: State` on iOS — and processes user events through methods that return new state. The integration test for a ViewModel is a unit test: provide mocked dependencies, send events, assert state transitions. No emulator, no simulator, no Robolectric. The clear test boundary is the single biggest architectural reason to adopt MVVM.

The canonical sealed UiState (Android) / enum State (iOS) makes the screen's state explicit:

```kotlin
sealed class AccountUiState {
    object Loading : AccountUiState()
    data class Content(val account: Account) : AccountUiState()
    data class Error(val message: String) : AccountUiState()
    object Empty : AccountUiState()
}
```

Every UI rendering branch is exhaustive; the compiler enforces handling every case. The screen never represents "nothing yet" implicitly — it represents `Loading` explicitly.

**MVI (Model-View-Intent)**

MVI extends MVVM with unidirectional flow. Intents represent user actions (`OnRefreshClicked`, `OnAccountSelected`); the Reducer or processor accepts the current state and an intent and produces the new state; the View renders state. Side effects (network calls, navigation, analytics) are explicit and named. MVI's strengths: complex screens with many interacting controls become tractable, time-travel debugging is feasible, the entire screen behaviour is one function. Weaknesses: boilerplate per screen is significantly higher than vanilla MVVM, simple screens feel over-engineered. Best fit on screens with high state complexity and on teams that value explicit state machines.

**Clean Architecture**

Robert C. Martin's three concentric rings: Entities at the centre (pure domain types with no outward dependencies), Use Cases (orchestrate Entities and Repositories), Interface Adapters (presenters, view models, controllers), Frameworks and Drivers at the outermost ring (UI framework, database, networking). The Dependency Rule states that source code dependencies point only inward — a Use Case never imports a Compose widget; an Entity never imports a `URLSession` extension. On mobile, the rings map to packages on Android (`domain`, `usecase`, `data`, `ui`) and SPM modules on iOS. The boundary is enforced by language access controls plus CI tests.

**VIPER — View Interactor Presenter Entity Router**

VIPER, born for the UIKit era, gives each screen five files: View (`UIViewController`), Interactor (business logic), Presenter (state preparation), Entity (model), Router (navigation). The thorough separation produces excellent testability and harsh ceremony. SwiftUI's declarative model and `@Observable` macro eliminate most of the boilerplate Presenter and View dance, making VIPER feel outdated on modern iOS. Still used in legacy banking codebases (HDFC, several US enterprise banks); not recommended for greenfield SwiftUI projects.

**TCA — The Composable Architecture (iOS-only)**

Point-Free's TCA gives each feature five primitives: State (immutable struct), Action (enum of all possible actions), Reducer (pure function from `(State, Action) -> Effect<Action>`), Store (runtime that holds state and dispatches actions), Effect (side-effect producer). Child features compose into parents via `Scope` and `IfLetStore`. Testability is exhaustive — `TestStore` lets the test assert every state change and every effect. The framework provides solutions to navigation, dependency injection, and effect cancellation that vanilla SwiftUI does not. Trade-offs: steep learning curve (8-12 weeks for a competent SwiftUI engineer to reach productivity), framework lock-in (the architecture *is* TCA), boilerplate at the action enum level. Best fit: 10+ engineer iOS teams shipping complex apps where exhaustive testability and explicit state machines are valued.

**Decision Matrix**

| Team Size | App Complexity | Android Recommendation | iOS Recommendation |
|---|---|---|---|
| 1-3 engineers | Simple | MVVM + Compose | MVVM + SwiftUI |
| 1-3 engineers | Complex | MVVM with sealed UiState | MVVM with enum state |
| 4-10 engineers | Medium | MVVM or MVI | MVVM or TCA |
| 4-10 engineers | Complex | MVI with Clean Architecture | TCA |
| 10+ engineers | Complex | MVI + Clean + feature-modular | TCA + Clean + SPM-modular |
| 10+ engineers | Banking / regulated | MVI + Clean + Konsist enforcement | TCA + Clean + SwiftLint enforcement |

---

## Implementation Guide

### Step 1: Document the canonical exemplar

Pick one feature and implement it as the textbook example of the chosen pattern. Every other feature is reviewed against the exemplar.

### Step 2: Codify the package / module structure

Android: `feature-X/ui`, `feature-X/domain`, `feature-X/data`, `feature-X/di`. iOS: `FeatureX/Sources/UI`, `FeatureX/Sources/Domain`, `FeatureX/Sources/Data`. The folder structure is the dependency boundary.

### Step 3: Enforce the dependency rule in CI

Konsist tests on Android assert that `ui` does not import `data` directly; Swift Package Manager's module visibility enforces the same on iOS plus SwiftLint custom rules for finer control.

### Step 4: Build the screen template generator

A script or template (Android Studio / Xcode template, or `cookiecutter`-style) generates the scaffolding for a new screen following the pattern. The team's default action is "use the template."

### Step 5: Run quarterly architecture drift reviews

A senior engineer audits a sampled set of screens against the canonical pattern. Drift is either codified (pattern update) or corrected (refactor). The review is a recurring 90-minute calendar event, not an unscheduled one-off.

### Step 6: Train new joiners on the pattern in week one

New joiners' first PR is a screen built from the template, reviewed by the architect, merged. The pattern is internalised by week-one practice, not by reading a wiki.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Pattern ADR ratified | Mobile Architect | Pattern named, exemplar screen committed, rejection criteria documented | Required |
| Module / package structure documented | Mobile Architect | Folder layout published, dependency rule explicit | Required |
| CI dependency-rule tests in place | Build Engineering | Konsist on Android, module-boundary linting on iOS | Required |
| Template generator delivered | Mobile Engineering Lead | New-screen scaffolding tool published and in use | Required |
| Quarterly architecture drift review scheduled | Mobile Architect | Calendar event recurring; outcomes recorded | Required |
| New-joiner pattern training in place | Engineering Manager | First-week PR review covers pattern adherence explicitly | Required |

---

## Security Considerations

- The pattern decision should make security boundaries explicit. The Repository (or its TCA equivalent) is the natural place for input validation, output sanitisation, and decryption — keep this responsibility there and resist letting it drift up into ViewModels.
- Dependency-direction discipline (the Use Case never imports a URLSession) prevents security-sensitive code (cryptographic primitives, keychain access) from being smuggled into the UI layer where review attention is lower.
- Pattern templates should include security defaults: every text input has an explicit `keyboardType` and `textContentType` to leverage iOS autofill / Android password-manager autofill correctly, every screen showing PII opts into screenshot suppression.

---

## Performance Considerations

- Pattern overhead is real but bounded: TCA adds 5-15 percent to compile time on iOS for typical features; MVI adds 5-10 percent of code volume per screen on Android. Neither pattern is the bottleneck for runtime performance — recomposition / redraw discipline is.
- The sealed UiState / enum State pattern, properly used, avoids redundant rendering: Compose's `derivedStateOf` and SwiftUI's `@Observable` access tracking respond only to the property the View actually reads.
- Pattern-driven dependency injection adds compile-time overhead (Hilt's KSP processor, Factory's compile-time registration) but adds zero runtime overhead on hot paths.

---

## Anti-Patterns to Avoid

### ⚠️ The Five-Pattern Codebase

Five engineers, five favourite patterns, one codebase. Every screen follows a different convention. New joiners cannot generalise from any one screen to predict the next. The fix is the ADR plus the canonical exemplar plus the review discipline.

### ⚠️ The Cargo-Cult MVVM

The team writes ViewModels but lets them import Compose / SwiftUI, hold references to Activities, and observe LiveData via lifecycle-bound observers from inside the ViewModel. The pattern's testability promise is broken. The fix is the strict "no UI imports in ViewModel" rule, enforced in CI.

### ⚠️ The Dependency Rule Violation

A Use Case imports a Retrofit interface or an `NSURLSession` extension; an Entity imports a Compose `Modifier`. The dependency direction reverses. The codebase drifts into "everything depends on everything." The fix is the Konsist or module-boundary tests that fail the build on violations.

### ⚠️ TCA-as-Cargo-Cult

The team adopts TCA because Point-Free's blog convinced them, then writes Reducers that mutate state in side-effect closures and Effects that fire without cancellation handling. The framework's testability is unused; the boilerplate is paid in full. The fix is the senior engineer who has shipped real TCA features running pattern reviews for the first quarter.

### ⚠️ The Premature Clean Architecture

The five-engineer team building a simple CRUD app insists on Use Cases, Repositories, Mappers, and Interactors for every screen. The Use Case is a one-line wrapper around the Repository. The team ships 30 percent slower than necessary. The fix is the decision matrix — Clean Architecture earns its place at scale and complexity, not as a default.

---

## AI Augmentation Extensions

### AI-Assisted Pattern Compliance Review

LLM coding assistants ingest the canonical exemplar and the pattern ADR, then review every new PR for pattern compliance — flagging ViewModels that import UI types, Use Cases that bypass Repositories, sealed UiState classes that miss a state branch. The architect's review queue compresses to the genuinely interesting violations.

### AI-Assisted Pattern Migration

When the pattern decision changes (vanilla MVVM → MVI, MVC → MVVM, MVVM → TCA), AI assistants generate migration PRs for individual screens following the new exemplar. The architect reviews the migrations; the typing happens autonomously.

---

## References

1. [Clean Architecture — Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) — *Amazon*
2. [Android Architecture Guidelines](https://developer.android.com/topic/architecture) — *developer.android.com*
3. [The Composable Architecture by Point-Free](https://github.com/pointfreeco/swift-composable-architecture) — *github.com*
4. [MVI on Android — Hannes Dorfmann](https://hannesdorfmann.com/android/mosby3-mvi-1/) — *hannesdorfmann.com*
5. [VIPER Architecture for iOS](https://www.objc.io/issues/13-architecture/viper/) — *objc.io*
6. [Now in Android — Reference Architecture](https://github.com/android/nowinandroid) — *github.com/android*
7. [Apple Human Interface Guidelines — App Architecture](https://developer.apple.com/design/human-interface-guidelines/) — *developer.apple.com*
8. [Konsist — Kotlin Architecture Tests](https://docs.konsist.lemonappdev.com/) — *konsist.lemonappdev.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/architecture-patterns/` | Aligned to Clean Arch · Android Arch Guide · Apple HIG · TCA*
