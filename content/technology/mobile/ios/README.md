# iOS Architecture

Modern iOS engineering on SwiftUI and Swift Concurrency — Observable view-models with @Observable, SwiftData replacing Core Data, the Composable Architecture and Clean Swift as competing structural choices, and Keychain backed by the Secure Enclave for credential isolation.

**Section:** `technology/mobile/` | **Subsection:** `ios/`
**Alignment:** Apple Human Interface Guidelines | Swift Concurrency Roadmap | OWASP MASVS-L2 | NIST SP 800-163
**Audience:** iOS Engineers · Mobile Architects · Technical Leads

---

## Overview

iOS architecture in 2026 is in the late stage of two enormous transitions. SwiftUI has reached the threshold where new screens are written in SwiftUI by default, with UIKit interop for the specific surfaces (text engine, complex collection views, AR camera previews) where SwiftUI has not caught up. Swift Concurrency — `async/await`, `Task`, `Actor`, `AsyncStream` — has displaced Grand Central Dispatch as the asynchrony model for new code; the engineering bar is now whether the code is `Sendable`-clean under strict concurrency checking, and Swift 6's strict mode is non-optional for new projects.

The Combine framework, briefly the future of reactive state on iOS, is in stable-maintenance: existing code keeps working, new code adopts the `@Observable` macro (Swift 5.9) which eliminates the need for `@ObservableObject` and `@Published`, and the SwiftUI redraw model becomes more efficient because the macro tracks property access rather than re-evaluating the entire observation graph. SwiftData replaces Core Data for new persistence work — Core Data is not deprecated, but new SwiftUI-first apps adopt SwiftData and pay no Objective-C bridge cost.

The architectural shift is not "we adopted SwiftUI." It is: **the iOS app uses SwiftUI as the primary UI layer with named UIKit interop islands for justified gaps, structures state through @Observable view-models and a chosen Clean/TCA/MV pattern that is documented as an ADR, persists through SwiftData with Keychain for secrets in a hardware-backed enclave where available, and ships under Swift 6 strict concurrency with zero `@unchecked Sendable` escape hatches in production code paths.**

---

## Core Principles

### 1. SwiftUI-first, UIKit interop only where justified

New screens are SwiftUI. UIKit interop exists for specific surfaces — `UITextView` with rich-text editing, complex `UICollectionView` layouts that SwiftUI's `Grid` and `List` cannot match, AVFoundation camera and AR view controllers — but each interop island is documented as a gap with a "remove when SwiftUI catches up" trigger. The default is SwiftUI; the exception requires justification.

### 2. Swift Concurrency under strict mode

`async/await` replaces completion handlers. `Task` and `TaskGroup` replace `DispatchQueue`. `Actor` protects shared mutable state from data races at compile time. `AsyncStream` and `AsyncSequence` replace Combine publishers for new code. Swift 6 strict concurrency catches the data-race classes that have caused intermittent crashes for a decade; `@unchecked Sendable` is the escape hatch and the team's CI fails the build on any new usage of it.

### 3. @Observable as the state primitive

The `@Observable` macro (introduced Swift 5.9, mature in 5.10+) replaces `@ObservableObject` + `@Published`. The macro tracks property access at call sites, so SwiftUI redraws only the views that read the property that changed — not every view in the observation graph. Performance improves measurably on screens with many observable properties.

### 4. Pick a structural pattern and commit to it

Vanilla MVVM, Clean Swift (VIP/VIPER's evolution), or The Composable Architecture (TCA) by Point-Free. All three are defensible; mixing them inside one app produces inconsistency that compounds. The decision is an ADR; the ADR names the rejection criteria for switching.

### 5. SwiftData for new persistence; Core Data for legacy

SwiftData is the property-wrapper-based persistence layer integrated with SwiftUI. The model is a Swift class with `@Model`; queries use `@Query`; the underlying store is SQLite. Core Data remains supported and is the right answer for apps that already invested heavily in `NSFetchedResultsController` and complex relationship graphs.

### 6. Keychain for credentials with the right accessibility class

`kSecAttrAccessibleWhenUnlockedThisDeviceOnly` is the default for refresh tokens — the data is decryptable only while the device is unlocked and only on this specific device. `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` is appropriate for background-task tokens. `kSecAttrAccessibleAlways` is almost never the right answer and the Apple Security framework warns the engineer accordingly. Hardware backing via the Secure Enclave is automatic on devices that have one (A7 onward).

---

## Architecture Deep-Dive

The canonical SwiftUI screen with `@Observable` looks like this:

```swift
@Observable
final class AccountViewModel {
    var state: AccountState = .loading
    private let getAccount: GetAccountUseCase

    init(getAccount: GetAccountUseCase) { self.getAccount = getAccount }

    func load() async {
        state = .loading
        do {
            let account = try await getAccount.execute()
            state = .content(account)
        } catch {
            state = .error(error.localizedDescription)
        }
    }
}

enum AccountState {
    case loading
    case content(Account)
    case error(String)
}

struct AccountScreen: View {
    @State private var vm: AccountViewModel

    var body: some View {
        switch vm.state {
        case .loading: ProgressView()
        case .content(let account): AccountContent(account: account)
        case .error(let message): ErrorView(message: message, onRetry: { Task { await vm.load() } })
        }
    }
}
```

There is no `@ObservableObject`, no `@StateObject`, no `@Published`. The macro generates the observation infrastructure; SwiftUI's `withObservationTracking` reads the access pattern; redraws are surgical.

Dependency injection on iOS has no Apple-blessed framework. The community options are Factory (by Michael Long) for compile-time-checked service location, Resolver for property-wrapper-based injection, and hand-rolled composition roots for projects that want zero dependencies. The decision is less consequential than on Android (Hilt's compile-time graph) because Swift's type system catches more wiring errors at compile time, but the lack of a community consensus produces real fragmentation across the iOS ecosystem.

The structural-pattern decision in 2026:

- **Vanilla MVVM**: View, ViewModel, Repository. Minimum ceremony, maximum flexibility. Best fit for small to medium apps and for teams new to iOS.
- **VIPER**: View, Interactor, Presenter, Entity, Router. Five files per screen. Verbose, opinionated, born for the UIKit era. Still used in legacy banking apps; not recommended for new SwiftUI codebases.
- **Clean Swift (VIP)**: A simplification of VIPER for the UIKit era. Largely superseded by TCA and vanilla MVVM in 2026.
- **The Composable Architecture (TCA)**: Point-Free's State/Action/Reducer/Store/Effect framework. Unidirectional data flow, exhaustive switch statements, best-in-class testability. Steep learning curve. Third-party dependency that the team is locking the architecture to — Point-Free's stewardship has been excellent but the lock-in is real. Used by Reddit, Coinbase, and many indie developers. Best fit for complex apps with senior teams that value testability and explicit state machines.

Recommended decision matrix:

| Team size | App complexity | Recommended |
|---|---|---|
| 1-3 engineers | Simple | Vanilla MVVM |
| 1-3 engineers | Complex | Vanilla MVVM with strict ADR discipline |
| 4-10 engineers | Medium | Vanilla MVVM or TCA |
| 4-10 engineers | Complex | TCA |
| 10+ engineers | Complex | TCA with internal training programme |

Instruments is the iOS engineer's irreplaceable tool. The Time Profiler instrument captures pre-main and post-main startup; pre-main time (dyld linking, static initialisers) is reduced by removing unused frameworks and by dynamic-framework-to-static-library conversion. Post-main time is reduced by deferring non-critical work off `application(_:didFinishLaunchingWithOptions:)`. The Allocations instrument catches retain cycles before they ship; the Time Profiler catches main-thread blocking; the Animation Hitches instrument quantifies frame drops.

The App Lifecycle in SwiftUI:

```swift
@main
struct AscendionApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate

    var body: some Scene {
        WindowGroup {
            RootView()
        }
    }
}
```

`@UIApplicationDelegateAdaptor` bridges the SwiftUI App protocol to a UIKit `UIApplicationDelegate` for the cases where AppDelegate hooks (push-notification registration, deep-link handling on cold start) are still required. The pattern is the migration path: SwiftUI App protocol is the future; AppDelegate exists for the integrations that have not yet caught up.

---

## Implementation Guide

### Step 1: Set the Swift language version and concurrency mode

`swift-tools-version: 6.0` in `Package.swift` for SPM modules; `SWIFT_VERSION = 6.0` in Xcode build settings; strict concurrency checking enabled. The CI fails the build on `@unchecked Sendable` introductions in new code.

### Step 2: Establish the SPM module graph

Decompose the app into Swift Package Manager modules — `FeatureAccount`, `FeatureTransfer`, `CoreNetworking`, `CoreDesignSystem`. The package boundary enforces dependency rules; the modular structure speeds incremental compilation 2-4×.

### Step 3: Choose and document the structural pattern

ADR names the choice (vanilla MVVM / TCA / Clean Swift), the rejection criteria, the learning resources for new joiners. Pattern is consistent across all features; deviation requires architect approval.

### Step 4: Wire SwiftData (or Core Data) and Keychain

SwiftData `@Model` types in `CoreData` module. Keychain wrapper around `SecItem*` APIs with explicit `kSecAttrAccessible` constants and `kSecUseDataProtectionKeychain` for iCloud Keychain exclusion of sensitive material.

### Step 5: Configure App Transport Security

`Info.plist` `NSAppTransportSecurity` allows no arbitrary loads. Pinned domains use SPKI hash pinning via `URLSession` delegate callbacks. ATS exceptions are documented per-domain with sunset dates.

### Step 6: Instruments time-profile every release

Pre-main and post-main startup measured per release. A regression beyond a documented budget (typically 200 ms pre-main, 800 ms post-main) blocks release. Animation hitches measured on the three highest-traffic screens.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Swift 6 strict concurrency enabled | iOS Architect | Strict mode on for app target and all first-party modules | Required |
| SPM module graph documented | iOS Architect | Features and core modules named; circular dependencies forbidden | Required |
| Structural-pattern ADR ratified | Architecture Review Board | Pattern named with rejection criteria and onboarding doc | Required |
| Keychain accessibility audited | Security + iOS Architect | Every Keychain item has documented accessibility class and rationale | Required |
| ATS configuration approved | Security | No `NSAllowsArbitraryLoads`; pinned domains documented | Required |
| Instruments baseline captured | iOS Architect | Cold-start, hitch budget, and memory baseline captured per release | Required |

---

## Security Considerations

- Keychain items use `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` by default; the device-only constraint prevents iCloud Keychain sync of credential material that must never leave the device.
- App Transport Security is `On` with no arbitrary-loads exception; per-domain exceptions documented with sunset dates and tracked as security debt.
- Code signing identity verified at runtime via `SecCodeCopySelf` to detect tampered binaries (effective against amateur attacker; defeated by sophisticated re-signing — pair with App Attest server-side for adequate trust).
- Sensitive screens (transfer, OTP, biometrics enrolment) opt out of background-screenshot capture via the `becomeFirstResponder` blur overlay pattern, preventing the iOS task switcher from caching plaintext.
- App Attest API (iOS 14+) provides device attestation for high-value operations; combine with server-side verification to gate sensitive backend calls on attested clients only.

---

## Performance Considerations

- Cold start under 2 seconds on iPhone 11 (median 2023 device); pre-main under 200 ms, post-main under 800 ms. Measured via Xcode Instruments Time Profiler with `DYLD_PRINT_STATISTICS=1` environment variable.
- Frame budget 16.67 ms (60 fps) on iPhone; 8.33 ms (120 fps) on ProMotion devices. Measure with the Animation Hitches instrument; address hitches over 250 ms before release.
- Memory baseline under 80 MB at app launch on a tier-2 device; growth over 300 MB triggers iOS jetsam termination on the older devices that still run iOS 17+.
- Pre-main shrinking strategies: convert dynamic frameworks to static libraries (`MACH_O_TYPE = staticlib`), strip unused symbols, audit dependency count — each dynamic framework adds 5-30 ms of pre-main on a tier-2 device.
- `Task` priorities (`.userInitiated`, `.utility`, `.background`) influence scheduling; never default to `.high` for non-urgent work — it competes with UI rendering.

---

## Anti-Patterns to Avoid

### ⚠️ Combine in New Code

The team adopts Combine because the tutorials suggest it, then discovers two years later that Apple's investment is in Swift Concurrency and `AsyncStream`. The Combine code is not broken; it is just on the wrong side of the platform's roadmap. The fix is to write new asynchronous code in `async/await` and `AsyncStream`, and to migrate Combine code opportunistically as screens are touched.

### ⚠️ `@unchecked Sendable` as the Escape Hatch

Strict concurrency complains; the engineer adds `@unchecked Sendable` to shut it up. The data race the compiler caught now ships. The fix is the CI rule that fails on any new `@unchecked Sendable` and the architecture-review checklist that requires explicit justification for any remaining usage.

### ⚠️ Force-Unwrapped Optionals in Production

`!` after every optional access. The crash report is a flood of `Fatal error: unexpectedly found nil while unwrapping`. The fix is the SwiftLint rule that forbids force-unwrap outside test code, and a code-review culture that treats `!` as a flag for justification.

### ⚠️ Big Singleton View Models

`@Observable final class AppStore` holds every piece of state in the app. Every view re-renders on every change. The fix is feature-scoped observable types injected at the navigation boundary; global singletons are reserved for truly app-wide state (authenticated user, feature-flag values).

### ⚠️ Storyboards in 2026 New Code

A new screen ships in a Storyboard because "the team knows Storyboards." Merge conflicts on XML, no preview, no compile-time checking. The fix is the convention that new screens are SwiftUI; UIKit screens are coded in pure code (`viewDidLoad`-based) when SwiftUI cannot reach.

---

## AI Augmentation Extensions

### AI-Assisted SwiftUI Migration

Cursor, Claude Code, and GitHub Copilot can translate UIKit `UIViewController` screens to SwiftUI with high accuracy for simple screens and 60-70 percent accuracy for complex screens with table views or custom drawing. The remainder is human work. The migration accelerates from a quarter-per-feature to a sprint-per-feature on representative codebases.

### AI-Assisted Swift Concurrency Refactor

Completion-handler APIs are mechanically refactorable to `async throws` functions; AI assistants surface the call sites and propose the refactor in batches. The team reviews and accepts. The cognitive cost of the language transition is reduced; the architectural decision (which APIs become `async`, which become `AsyncStream`) remains human.

---

## References

1. [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — *developer.apple.com*
2. [Swift Concurrency Roadmap](https://www.swift.org/documentation/concurrency/) — *swift.org*
3. [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui) — *developer.apple.com*
4. [Observation Framework — @Observable Macro](https://developer.apple.com/documentation/observation) — *developer.apple.com*
5. [SwiftData](https://developer.apple.com/documentation/swiftdata) — *developer.apple.com*
6. [The Composable Architecture — Point-Free](https://github.com/pointfreeco/swift-composable-architecture) — *github.com*
7. [iOS Security Guide](https://support.apple.com/guide/security/welcome/web) — *Apple Platform Security*
8. [App Attest and DeviceCheck](https://developer.apple.com/documentation/devicecheck) — *developer.apple.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/ios/` | Aligned to Apple HIG · Swift Concurrency · OWASP MASVS-L2 · NIST SP 800-163*
