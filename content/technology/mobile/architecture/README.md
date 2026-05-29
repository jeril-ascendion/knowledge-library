# Architecture Patterns & Design Systems

> **Section:** `technology/mobile/architecture/`
> **Alignment:** TOGAF Application Architecture | Google MAD Architecture Guide | Apple HIG 2024 | Clean Architecture (Martin) | SOLID Principles
> **Audience:** Mobile Architects · Senior Engineers · Technical Leads

---

## The Architecture Evolution

**MVC and the Massive View Controller** is where every iOS architecture conversation begins. UIKit's original 2008 design coupled View and Controller at the framework level — `UIViewController` owned the view hierarchy, the lifecycle hooks (`viewDidLoad`, `viewWillAppear`, gesture handlers), and by accumulation the networking, business logic, UI configuration, and navigation. The result was the 3,000-line View Controller, untestable and impossible to review. Android's pre-2017 equivalent was the Massive Activity / Fragment. The industry's response over the next decade — MVVM, then MVP, then Clean Architecture, then MVI, then TCA — each pattern solved a specific problem the prior pattern left open. Patterns are not interchangeable; the right one for a five-engineer startup is not the right one for a hundred-engineer banking app.

---

## MVVM In Depth

MVVM is the pattern endorsed by both Google (Modern Android Development Architecture Guide) and Apple (implicit in SwiftUI's `@Observable` and binding model). The architecturally non-negotiable rule: **the ViewModel has zero UI framework imports** — no `Activity`, `Fragment`, `UIViewController`, `View`, or Compose / SwiftUI references. The compiler enforces the dependency boundary; the test runs without an emulator or simulator.

The ViewModel exposes **observable state**: `StateFlow<UiState>` on Android (hot, conflated, always has a value), `@Published var state: State` or `@Observable var state: State` on iOS. The View **observes** state and **sends events** — never writes to state directly. The event-to-state contract is the integration boundary; everything else is implementation.

The **UiState sealed class** pattern on Android:

```kotlin
sealed class AccountUiState {
    object Loading : AccountUiState()
    data class Content(val account: Account, val isRefreshing: Boolean = false) : AccountUiState()
    data class Error(val message: String, val retryable: Boolean) : AccountUiState()
}
```

The single state stream prevents the entire class of impossible UI states (loading AND error simultaneously; content AND empty simultaneously). The Compose `when (state)` is exhaustive; the compiler refuses to build if any case is missed.

**ViewModel scoping**: one ViewModel per screen as the default; shared ViewModels for sibling screens that need shared state (a master-detail layout, a tabbed flow); `viewModelScope` for coroutines that should be cancelled when the ViewModel is cleared. **What goes where**: UI logic — formatting numbers for display, deciding which button is enabled, validation feedback — belongs in the ViewModel. Business logic — the rules, calculations, decisions that would be true regardless of the UI — belongs in Use Cases.

---

## MVI — Model View Intent

MVI sharpens MVVM with **unidirectional data flow**. Intent (user action — `OnRefreshClicked`, `OnAccountSelected`) flows into a Reducer (pure function: current State + Intent → new State + Effects). The Reducer is the only place state changes. The View renders the State. Side effects (network calls, navigation, analytics) are modelled as explicit sealed class types and processed by a dedicated effect handler.

The architectural payoff is the **single immutable State object** representing complete screen state. A `data class` copy on every state change is the cost; the benefit is that the screen behaviour is one pure function of its history, time-travel debugging becomes feasible, and the test asserts every state transition exhaustively. **When MVI outperforms MVVM**: screens with ten-plus interdependent state fields — multi-step forms with cross-field validation, real-time collaborative features where remote events and local events both mutate state, complex search-and-filter UIs where the state space has many dimensions.

**Performance cost is real**. Immutable `data class` copy on every change creates GC pressure at high frequency. For a 60fps screen receiving 100 state mutations per second, MVI's overhead is measurable; MVVM with mutable observable state holds up better. Production adoption: Spotify's Android team published an MVI architecture series in 2019 and continues to use it for complex flows; Freeletics's open-source MVI library FlowRedux remains a strong reference.

---

## Clean Architecture

Uncle Bob's three concentric rings, applied to mobile:

**Entities** (innermost): enterprise business rules — domain models, business invariants, repository interfaces (`interface AccountRepository`). Pure Kotlin / Swift classes with zero framework imports. An Entity has no idea that Android or iOS exists.

**Use Cases**: application business rules — one Use Case per business operation (`GetUserProfileUseCase`, `PlaceOrderUseCase`, `AuthenticateUseCase`). Depends only on Entities and Repository interfaces (abstractions). Returns a `Result<T>` or throws explicit domain exceptions. The Use Case is the unit under test for business logic.

**Interface Adapters**: ViewModel, Repository implementations, API clients with DTO-to-Entity mappers, Room DAOs with Entity converters. This is the ring where translation happens — from the platform's representation to the domain's, and back.

**Frameworks and Drivers** (outermost): Android SDK, UIKit, SwiftUI, Retrofit, OkHttp, Room, SQLite, Hilt, Factory. All dependencies point inward, never outward — the Dependency Rule. The domain layer knows nothing about Android, iOS, or any specific framework.

**Module-level enforcement**: each feature is a Gradle module on Android (`feature-account`, `feature-transfer`) or a Swift Package on iOS, with its own Presentation, Domain, and Data layers. The module graph must be a directed acyclic graph — Gradle and SPM refuse to build circular dependencies. **Google's Now in Android** and **Cash App's open-source projects** are the canonical production implementations every architect should read.

---

## TCA — The Composable Architecture

Point-Free's functional iOS architecture, in a class of its own for testability. Five primitives:

- **State** — a value-type `struct` representing complete screen state.
- **Action** — an `enum` of every possible event (`signInTapped`, `accountResponse(Result<Account, Error>)`, `binding(...)`).
- **Reducer** — a pure function `(inout State, Action) -> Effect<Action>` mutating state and returning effects.
- **Store** — the runtime that holds state, dispatches actions, and runs effects.
- **Effect** — async work returning further Actions when complete.

Child features compose into parents through `Scope` (extract a child state slice and a child action prefix) and `IfLetStore` (mount a child feature when an optional child state is non-nil).

**TestStore** is the killer feature. It lets the test send an action, exhaustively assert every state mutation that resulted, and exhaustively assert every effect that was emitted, in deterministic sequence. The framework refuses to pass a test that ignored a state change or an effect — the test fails on any divergence. Coverage is total because the framework enforces it.

**Trade-offs are real**. The learning curve is four to six weeks before a competent SwiftUI engineer reaches TCA productivity; the boilerplate at the action-enum and reducer-composition level is significant; performance on large state trees with deep observation needs careful design. The lock-in is total — the architecture *is* TCA, and switching is a rewrite. Production use: isoWords (a New York Times game), Charcoal (Pixiv's design system), and several enterprise financial apps that prize exhaustive testability above all.

---

## State Management Patterns

**Android primitives**. `StateFlow<T>` — hot flow, always has a value, the right answer for UI state. `SharedFlow<T>` — hot flow with no initial value, the right answer for one-time events like navigation transitions and toast triggers. `Channel<T>` — FIFO queue with guaranteed delivery, the right answer when no event must be dropped. The `consumeSingleEvent` pattern using `Channel` plus `consumeAsFlow()` prevents the bug where rotating the device replays a navigation event; the event survives the configuration change in Channel's queue and is processed exactly once.

**iOS primitives**. `@State` — local transient state owned by the view, the right answer for the toggle the user just flipped. `@StateObject` / `@Observable` — owned for the lifetime of the view, the right answer for the ViewModel. `@EnvironmentObject` — app-wide shared state injected through the environment, valuable for truly global concerns (authenticated user, current theme) and dangerous when over-used as a back-channel. Combine `Publisher` for reactive streams when the codebase already invested in Combine; `AsyncStream` and `AsyncSequence` for new code under Swift Concurrency.

**Global store patterns**. Redux-style global state with TCA on iOS or with hand-rolled reducers and `StateFlow` on Android. Appropriate for apps requiring global state coordination across many screens — collaborative editors, multi-screen wizards, complex analytics dashboards. Inappropriate as a default — most apps are screen-scoped, and a global store applied to a screen-scoped problem creates ceremony without benefit.

---

## UI Design Systems

**Material Design 3** introduces dynamic colour: the system extracts a colour palette from the user's wallpaper via the Monet algorithm and applies it to apps that opt in via `DynamicColors.applyToActivitiesIfAvailable(application)`. Colour tokens (`primary`, `onPrimary`, `primaryContainer`, `secondary`, `tertiary`, `error`, `surface`, `background`) replace hardcoded hex throughout the design system. Elevation is expressed as tonal surface overlays — a `surface` at 4dp elevation is a tinted variant of the base surface — not as drop shadows. The typography scale runs from Display Large (57sp, 0sp tracking) to Label Small (11sp, 0.5sp tracking). Shape tokens run from extra-small (4dp corner radius) to extra-large (28dp). **Compose Material3** is the canonical Android implementation.

**Apple Human Interface Guidelines 2024**. **SF Symbols** is the system icon library — over 6,000 symbols with monochrome, hierarchical (depth via opacity layers), palette (multi-colour with developer control), and multicolour rendering modes, automatically tuned to Dynamic Type. **Dynamic Type** runs through twelve size categories from `xSmall` through `accessibility5`; all apps must support Dynamic Type or fail accessibility review. **Safe Area insets** carry the Dynamic Island, notch, and home-indicator avoidance — `safeAreaPadding(.top)` and friends are non-negotiable.

**Design tokens** are the platform-agnostic abstraction layer. Token source of truth in JSON (or the W3C Design Tokens emerging standard), driven through **Style Dictionary** by Amazon to produce platform outputs — Android resources XML, iOS Swift constants, Figma Variables — from a single source. Figma Variables mapping to design tokens enables Figma-to-Compose and Figma-to-SwiftUI code generation via tools like Locofy and Figma's Dev Mode. **Component catalogue**: Showkase for Android renders every Compose component variant into a discoverable in-app catalogue; Xcode Previews with `#Preview` macros provides the SwiftUI equivalent.

---

## Navigation Architecture

**Android — Jetpack Navigation Compose**. `NavHost` defines the graph; composable routes are typed via the Type-Safe Navigation API introduced in Navigation 2.8; arguments pass through `NavBackStackEntry` with serialisable types or `Parcelable` via savedStateHandle. Nested navigation graphs let feature modules expose their own graphs that the host wires into the app graph. Deep-link handling registers a URI pattern and routes to the matched composable. The back stack is managed automatically; explicit `popUpTo` calls handle the cases where the default behaviour is wrong.

**iOS — NavigationStack with NavigationPath**. The 2022 replacement for `NavigationView` resolved a multi-year frustration: programmatic navigation became reliable. `NavigationPath` is the path stack; `navigationDestination(for: Type)` wires types to destinations; `path.append(item)` pushes; `path.removeLast()` pops. For complex flows that span multiple screens and require business-logic decisions about routing — checkout flow with conditional steps based on payment method, onboarding with skippable sections — the **Coordinator pattern** owns the routing decisions outside the views. The architectural rule: the ViewModel emits navigation events through a `Flow` / `AsyncStream` / Combine publisher; the Coordinator observes and executes navigation; the View has no navigation imperative code.

---

## Anti-Patterns

### 1. The Massive ViewModel

The ViewModel grows to 1,000 lines because the screen has six tabs and the team kept adding state to one class. Recomposition becomes unpredictable; testing requires mocking ten dependencies.

**CORRECT:** The fix is splitting per logical sub-screen, sharing state through a parent ViewModel only where genuinely shared, and using sealed UiState to keep screen state explicit.

### 2. The Two-Way Binding Trap

The team uses two-way data binding because "it's less code." The ViewModel is mutated from the View; the source of truth becomes unclear; tests cannot reproduce the bug.

**CORRECT:** The fix is unidirectional flow: the ViewModel owns state; the View renders state and sends events.

### 3. The Cargo-Cult Clean Architecture

The five-engineer team building a simple CRUD app insists on Entities, Use Cases, Repositories, and Mappers for every screen. The Use Case is a one-line wrapper around the Repository. The team ships 30 percent slower than necessary.

**CORRECT:** The fix is the decision matrix — Clean Architecture earns its place at scale, not as a default.

### 4. The Mixed-Pattern Codebase

Five engineers, five favourite patterns, one codebase. Every screen follows a different convention. New joiners cannot generalise from any one screen.

**CORRECT:** The fix is the ADR plus a canonical exemplar plus code-review discipline.

### 5. Navigation Logic in the View

The View calls `navController.navigate(...)` based on a business condition. The condition is buried in the View; the test cannot reach it.

**CORRECT:** The fix is moving navigation decisions into the ViewModel and exposing them as events the Coordinator (or NavHost wrapper) executes.

---

## References

1. [Android — Guide to App Architecture](https://developer.android.com/topic/architecture) — *developer.android.com*
2. [Clean Architecture — Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) — *Amazon*
3. [The Composable Architecture by Point-Free](https://github.com/pointfreeco/swift-composable-architecture) — *github.com*
4. [Material Design 3](https://m3.material.io/) — *m3.material.io*
5. [Apple HIG 2024](https://developer.apple.com/design/human-interface-guidelines/) — *developer.apple.com*
6. [Style Dictionary](https://amzn.github.io/style-dictionary/) — *amzn.github.io*
7. [Spotify Engineering — MVI](https://engineering.atspotify.com/) — *engineering.atspotify.com*
8. [Now in Android](https://github.com/android/nowinandroid) — *github.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/architecture/` | Aligned to TOGAF · Google MAD · Apple HIG · Clean Architecture · SOLID*
