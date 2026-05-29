# Mobile State Management

> **Section:** `technology/mobile/mobile-state-management/`
> **Alignment:** Redux Architecture | Google MAD StateFlow Guide | Point-Free TCA | Swift Observation Framework
> **Audience:** Mobile Engineers · Senior Engineers · Architects

State management is the discipline of deciding where application state lives, how it changes, how changes propagate to the UI, and how state survives or resets across configuration changes, process death, and navigation. Errors in state management produce some of the most difficult bugs in mobile development: intermittent UI inconsistencies, data appearing twice or not at all, state surviving when it should reset, and race conditions between concurrent state mutations.

## Overview

The fundamental tension in mobile state management is between consistency and performance. A single immutable state object (MVI pattern) guarantees consistency but copies the entire object on every mutation. Multiple independent observable properties (MVVM with multiple StateFlows) is more performant but allows the possibility of inconsistent intermediate states — a loading indicator true while content is also visible.

The correct resolution is: use MVI for screens with many interdependent state fields; use MVVM with a single UiState sealed class for screens with simpler, largely independent state.

## State Primitive Selection

### Android: StateFlow and SharedFlow
`StateFlow<UiState>` is the primary state primitive. Hot, always has a value, conflated (only the latest value is delivered if the collector is slow). The UI observes StateFlow and re-renders on every new emission. `SharedFlow` is used for one-time events that must not replay: navigation events, error toasts, analytics triggers. A navigation event stored in `StateFlow` would re-trigger on screen rotation.

The `UiState` sealed class pattern eliminates impossible states:
- `Loading`: spinner shown, no data
- `Content(data: T, isRefreshing: Boolean)`: data shown, optional refresh indicator
- `Error(message: String, retryable: Boolean)`: error shown, optional retry action

### iOS: @Observable and Combine
Swift 5.9's `@Observable` macro uses fine-grained property observation — only Views that read a specific property recompose when that property changes. This outperforms `@ObservableObject` + `@Published`, which recomposed all observing Views on any property change. For one-time events, use `PassthroughSubject` or an event queue to prevent SwiftUI's declarative model from replaying navigation events on View reconstruction.

### The Composable Architecture (TCA) for Complex iOS Flows
TCA's `Reducer` is a pure function of `(State, Action) -> (State, Effect)`. All state mutations go through the Reducer — no direct state mutation from the View. Effects are explicit, typed, and testable. `TestStore` allows asserting every state transition in sequence. Use TCA for flows with 10+ interdependent state fields, complex multi-step wizards, or screens where the test suite for state behaviour is more valuable than the overhead of the framework.

## State Persistence

State that must survive process death is not the same as state that must survive configuration changes. ViewModel survives configuration changes (rotation) but not process death. For process death survival: `rememberSaveable` in Compose for simple scalar state, `SavedStateHandle` in ViewModel for navigation arguments and form state, Room/DataStore for user data that must always persist, Keychain/Keystore for credentials.

## Anti-Patterns to Avoid

> **⚠ Mutable State Exposed from ViewModel** — `val accounts = mutableListOf<Account>()` as a public ViewModel property. Any collaborator can mutate the list, breaking the single source of truth contract.
> **CORRECT:** Expose only immutable types: `val uiState: StateFlow<AccountsUiState>`. Mutation occurs only inside the ViewModel through `_uiState.update { }`.

> **⚠ Navigation Events in StateFlow** — Storing a navigation destination in `StateFlow`. On screen rotation, the View resubscribes and receives the navigation event again, causing a double navigation.
> **CORRECT:** Use `SharedFlow` with `replay = 0` for one-time events. Consume and clear the event immediately in the View.

## References

1. Google — StateFlow and SharedFlow Guide. developer.android.com/kotlin/flow/stateflow-and-sharedflow
2. Point-Free — The Composable Architecture. github.com/pointfreeco/swift-composable-architecture
3. Apple — Swift Observation. developer.apple.com/documentation/observation
4. Spotify Android — MVI Architecture Series. engineering.atspotify.com
