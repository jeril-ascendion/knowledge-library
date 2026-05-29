# Cross-Platform Frameworks

The four serious cross-platform options for mobile in 2026 — Flutter, React Native, Kotlin Multiplatform, and .NET MAUI — compared honestly on rendering model, performance ceiling, app-size overhead, and the production scars that the marketing decks omit.

**Section:** `technology/mobile/` | **Subsection:** `cross-platform/`
**Alignment:** TOGAF ADM | Gartner Mobile App Strategy | OWASP MASVS | Framework Vendor Roadmaps
**Audience:** Mobile Engineers · Solutions Architects · Technical Leads

---

## Overview

Cross-platform mobile is no longer a single conversation. The four options that ship at production scale in 2026 — Flutter, React Native, Kotlin Multiplatform (KMP), and .NET MAUI — make different architectural trade-offs. Flutter renders every pixel itself with Skia or Impeller and never touches a platform widget; React Native uses JavaScript and TypeScript to drive actual native UI controls through a bridge; KMP shares only the non-UI layers, with SwiftUI on iOS and Compose on Android keeping their full native fidelity; MAUI compiles C# and XAML into native controls through the .NET runtime. The frameworks are not interchangeable, and choosing between them by "popularity" is choosing badly.

The trade-off space is named by four orthogonal axes: rendering model (own engine vs platform widgets), shared scope (UI included vs business logic only), language and runtime tax (Dart, JS/TS, Kotlin, C#), and ecosystem maturity (plug-in availability, native-module integration, hot-reload quality). The right framework for a banking app whose iOS users compare it against the first-party Apple Wallet is not the right framework for a custom-canvas creative tool whose UI is entirely bespoke. Pretending one answer fits both is the easiest way to ship the wrong app twice.

The architectural shift is not "we use cross-platform." It is: **the cross-platform decision is a matrix decision against rendering model, shared scope, runtime tax, ecosystem maturity, and team skill — chosen with eyes open about which native capabilities will require platform-specific engineers anyway and budgeted accordingly.**

---

## Core Principles

### 1. The rendering model decides whether the app feels native

Flutter and game engines paint their own pixels — pixel-perfect cross-platform, but every iOS user notices that the iOS share sheet isn't really there and the Material ripple is a Flutter approximation. React Native and MAUI drive actual platform widgets — the share sheet is real, the keyboard contract is real, the typography scale is real. KMP keeps native UI entirely. Match the rendering model to the user's platform expectation, not to the team's preference for tooling.

### 2. Shared scope is not "all of it"

Most production cross-platform apps share 60-85 percent of the codebase. The remaining 15-40 percent is platform-specific: Apple Watch / Wear OS, AR camera, biometric attestation, deep platform-services integrations (Apple Pay, Google Pay, Health Kit). Planning for 95 percent shared code is planning for disappointment when year-two feature requests demand the platform-specific work.

### 3. The runtime tax is real and is paid every install and every frame

Flutter ships a 6-8 MB Skia/Impeller engine on Android; React Native ships Hermes plus JSI; MAUI ships .NET runtime libraries; KMP ships LLVM-compiled Kotlin/Native or JVM bytecode. The install overhead, the cold-start overhead, and the per-frame overhead are framework constants — they do not go away with engineering work. Budget for them.

### 4. The platform-team-of-record stays native

Behind every successful cross-platform app at scale, there are native iOS and Android engineers fixing what the framework cannot reach — bridging native modules, debugging crashes the framework's stack traces hide, integrating App Store and Play Store rules that frameworks have no opinion about. Plan to hire them; the saving over "two pure-native teams" is real but smaller than the marketing decks claim.

### 5. Framework lock-in is a multi-year commitment

Choosing Flutter is choosing Dart for the life of the app. Choosing React Native is choosing JavaScript and Meta's ongoing investment. Choosing MAUI is choosing .NET and Microsoft's mobile-strategy stability. Choosing KMP is choosing JetBrains and Google's joint roadmap. The frameworks are not migration-friendly; switching frameworks is a rewrite.

### 6. Hot reload is real productivity; ship cycles still matter

Cross-platform frameworks all have stronger hot-reload stories than native (Compose Live Edit and SwiftUI Previews have closed the gap but not eliminated it). The productivity gain is real for UI iteration. The ship cycle — App Store and Play Store review — is unchanged. Hot reload accelerates the inner loop; it does not accelerate the outer loop.

---

## Architecture Deep-Dive

**Flutter (Dart, Skia / Impeller rendering, AOT-compiled to native ARM):**

Flutter compiles Dart to native ARM machine code for release builds. The UI is rendered by Flutter's Skia engine on older versions and by Impeller on iOS (since Flutter 3.10) and Android (Impeller GA on Android in 2024). Impeller pre-compiles shaders, eliminating the first-frame stutter that Skia historically caused on iOS. Hot reload preserves widget state and updates the running app in under a second. Flutter's widget catalogue is enormous; the trade-off is that every widget is a Flutter widget, not a platform widget — iOS share sheets are simulated, Material You's dynamic colour is approximated, the iOS keyboard contract is honoured as a special case rather than as a default. Strong fit for branded canvas UIs (Reflectly, Alibaba Xianyu, Google Pay's redesign). Performance ceiling is approximately 95 percent of native for typical UIs; the 5 percent gap is the framework overhead and the inability to access platform-private rendering hints.

**React Native (JavaScript / TypeScript, JS engine drives platform widgets):**

React Native runs JavaScript through Hermes (or JSC on older versions) and drives actual `UIView` and `Android View` widgets through a bridge. The old Bridge architecture is asynchronous JSON serialisation across the JS-native boundary — every prop update is a round trip. The New Architecture (Fabric for rendering, JSI for synchronous calls, TurboModules for native modules, Codegen for type-safe interfaces) eliminates the round-trip cost for synchronous operations and unlocks features that Bridge-era apps cannot reach. Migration from Bridge to New Architecture matters because new React Native features are New-Architecture-first. Production-scale users: Meta (Facebook, Instagram, Marketplace), Microsoft (Office Mobile, Outlook on iOS for some flows), Shopify, Discord. Discord's late-2024 migration story documents the New Architecture migration in detail. Performance ceiling 85 percent of native for typical UI work, 95 percent for compute that lives in TurboModules.

**Kotlin Multiplatform (KMP — Kotlin compiles to JVM bytecode on Android, LLVM native code on iOS):**

KMP shares business logic only — networking, persistence, domain models, ViewModel state machinery — and keeps SwiftUI on iOS and Compose on Android as the native UI layers. The shared module compiles to a JAR on Android (added to the Gradle build) and to an XCFramework on iOS (consumed by Xcode as a Swift Package or CocoaPod). Ktor handles networking cross-platform; SQLDelight or Room-KMP handles persistence; the ViewModel state machinery sits in shared code with platform-specific UI binding it to SwiftUI's `@Observable` or Compose's `StateFlow`. Compose Multiplatform extends KMP to share UI as well; production adoption is rising but Compose Multiplatform on iOS is still less mature than SwiftUI for HIG-compliant apps. Production users: Netflix, McDonald's, 9GAG, Cash App. Cash App at Block has documented KMP as "the architecture we wish we'd had from the start." Performance ceiling 100 percent — the shared code is real native code, the UI layer is real native UI.

**.NET MAUI (C# / XAML, .NET runtime drives native controls):**

MAUI is the Xamarin successor; Xamarin's Linux Foundation transition and Microsoft's strategy ambiguity have hurt MAUI's perception but the framework itself is technically credible. C# and XAML compile to .NET assemblies; the .NET runtime drives `UIView` on iOS and `Android View` on Android. Hot Reload works; the developer experience inside Visual Studio is excellent for Windows-host development; on macOS-host development the gaps are larger. Best fit for organisations already deep in .NET — Microsoft-shop enterprises, internal tools where C# muscle exists. Production users: smaller and quieter than Flutter or React Native, but real: organisations like the Government of Singapore's SingPass app and various internal enterprise apps. Performance ceiling 88 percent of native.

Honest production app-size comparison (release builds, ARM64 Android, ARM64 iOS, baseline Hello World after R8 / App Thinning):

| Framework | Android (AAB) | iOS (IPA) |
|---|---|---|
| Pure native (Kotlin / Swift) | 3-5 MB | 4-6 MB |
| Flutter | 7-9 MB | 14-18 MB |
| React Native (Hermes) | 8-11 MB | 12-16 MB |
| .NET MAUI | 14-20 MB | 18-25 MB |
| KMP (shared logic only) | 3-5 MB + 1-3 MB shared | 4-6 MB + 1-3 MB shared |

App-size matters in emerging markets where Play Store install-size warnings deter installs above 25 MB and where data plans price MB at scale.

---

## Implementation Guide

### Step 1: Build the framework comparison matrix

Score each candidate against: rendering model fit, shared-scope target, runtime tax tolerance, ecosystem maturity, hiring market in your geography, framework sponsor stability, five-year TCO. The scoring drives the decision.

### Step 2: Run the framework-specific spike

Two weeks. Three hardest screens. Real device deployment. Measure cold start, frame budget on a tier-2 device, integration cost with one platform-specific native SDK that your roadmap will demand.

### Step 3: Set up the dual-platform build pipeline

For Flutter / React Native / MAUI, one repo, one CI pipeline branches into Android and iOS build legs. For KMP, the shared module produces JAR + XCFramework artefacts consumed by `androidApp` and `iosApp` Xcode project.

### Step 4: Wire native-module interop deliberately

Identify the surfaces that will require native code: camera, biometrics, push notifications, Apple Pay, Google Pay, payments SDK. Write the native bridges first; verify they work; only then build features on top of them.

### Step 5: Establish the platform-specific UX overrides

Document where the cross-platform widget is acceptable and where the platform widget must be substituted (iOS pickers, Material You theming, share sheets). The decision must be deliberate, not accidental.

### Step 6: Plan for native engineering hire

Budget for at least one senior native iOS engineer and one senior native Android engineer on a team of five-plus cross-platform engineers. The framework will not cover every roadmap requirement.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Framework comparison matrix approved | Mobile Architect | Weighted scoring against all four candidates documented in ADR | Required |
| Two-week framework spike completed | Mobile Engineering Lead | Three hardest screens prototyped; cold-start and frame-budget measured | Required |
| Native interop boundary defined | Mobile Architect | Inventory of platform-specific surfaces with native engineer ownership | Required |
| Platform-UX override policy ratified | UX Lead + Mobile Architect | List of screens where native widgets override cross-platform defaults | Required |
| Framework upgrade cadence documented | Build Engineering | Major-version upgrade policy with risk-budget allocation | Required |
| TestFlight / Play Internal smoke test | QA | Release-mode build verified on real devices each release | Required |

---

## Security Considerations

- Framework-distributed binary artefacts (Flutter engine binaries, React Native pre-built libraries, MAUI runtime libraries) carry supply-chain risk; verify checksums and pin versions in CI to prevent silent malicious updates.
- The JavaScript / Dart / .NET runtime is an in-process attack surface in addition to the native platform's; sensitive operations (decryption, key derivation, biometric attestation) should still happen in native code via TurboModules or KMP `expect/actual` boundaries, not in the cross-platform runtime.
- Source-map exposure for React Native bundles in release builds leaks application structure; ensure source-map upload to Sentry is configured but source maps are NOT included in the shipped bundle.
- Flutter and React Native both encode their app logic in the bundle in plaintext under default settings — reverse engineering is easier than for native Kotlin/Swift with R8/Bitcode. Pair with Play Integrity / App Attest for server-side trust.

---

## Performance Considerations

- Cold start on a tier-2 device: Flutter 1.8-2.5 s, React Native (Hermes + New Architecture) 2.0-2.8 s, MAUI 2.5-3.5 s, KMP 1.5-2.2 s (native UI), pure native 1.2-2.0 s. Budget against your slowest target device.
- Frame budget 16.67 ms (60 fps). Flutter sustains 60 fps on most UIs; 120 fps on ProMotion needs Impeller and careful widget design. React Native with the New Architecture sustains 60 fps on typical lists; long lists need FlashList or recyclerlistview. MAUI matches React Native. KMP UI is native and matches native performance.
- App-size budget under 25 MB Android, 35 MB iOS for emerging-market deployment. Flutter and React Native have to fight for this; MAUI rarely makes it; pure native and KMP have headroom.
- Tooling: Flutter `flutter analyze --performance`, React Native Perf Monitor and Flipper, MAUI Visual Studio profiler, KMP standard Android Profiler and Xcode Instruments.

---

## Anti-Patterns to Avoid

### ⚠️ Choosing Flutter for HIG-Compliant Banking

The team chooses Flutter because the demo is gorgeous. The bank's iOS users compare the app against the first-party Apple Wallet and rate it 3.5 stars because the share sheet doesn't feel right, the swipe-back gesture is approximated, and the typography doesn't match the system. The fix is naming platform-native UX as a hard constraint before the framework choice.

### ⚠️ Bridging Everything in React Native

The team builds React Native modules around every platform capability — including camera, biometrics, payments, deep linking — and the bridge layer becomes the single biggest source of production crashes. The fix is the New Architecture (JSI, TurboModules) plus the discipline of using mature community modules (react-native-camera-kit, react-native-keychain, react-native-mmkv) instead of bespoke bridges.

### ⚠️ KMP Without Native Engineers

The team adopts KMP expecting Kotlin-everywhere productivity, then discovers that SwiftUI on iOS requires real Swift engineering and Compose on Android requires real Compose engineering. The team without native specialists ships broken iOS UI and overflowing Compose layouts. The fix is staffing native specialists from day one; KMP saves logic-layer code, not UI-layer skill.

### ⚠️ MAUI Without .NET Muscle

The team picks MAUI because the cross-platform marketing matches their hopes, but no engineer on staff has shipped a production C# app. The framework's strengths are inaccessible; the framework's quirks dominate. The fix is honesty about existing skills — MAUI rewards .NET shops and punishes everyone else.

### ⚠️ Treating Hot Reload as a Goal

The team's framework selection is dominated by hot reload quality. They miss that the App Store review cycle is 24-48 hours regardless of how fast the inner loop is. The fix is weighting inner-loop productivity at appropriate magnitude (real but not dominant) against ship-cycle and TCO metrics.

---

## AI Augmentation Extensions

### AI-Assisted Cross-Platform Native Bridge Generation

LLM coding assistants can generate the boilerplate native bridge code for React Native TurboModules, Flutter platform channels, and KMP `expect/actual` declarations from a typed interface specification. The generated code follows the framework's idioms; engineers focus on the integration logic.

### AI-Assisted Multi-Framework Spike Comparison

When the framework decision is open, AI assistants generate the "three hardest screens" in parallel across Flutter, React Native, and KMP. The team evaluates the resulting apps on real devices with measurement, not vibes — the comparison spike compresses from weeks to days.

---

## References

1. [Flutter Documentation](https://docs.flutter.dev/) — *docs.flutter.dev*
2. [React Native — The New Architecture](https://reactnative.dev/architecture/landing-page) — *reactnative.dev*
3. [Kotlin Multiplatform Documentation](https://kotlinlang.org/docs/multiplatform.html) — *kotlinlang.org*
4. [.NET MAUI Documentation](https://learn.microsoft.com/en-us/dotnet/maui/) — *Microsoft Learn*
5. [Cash App KMP Adoption Story](https://code.cash.app/) — *code.cash.app*
6. [Discord — Why React Native](https://discord.com/blog/why-discord-is-sticking-with-react-native) — *discord.com*
7. [Flutter Impeller Architecture](https://docs.flutter.dev/perf/impeller) — *docs.flutter.dev*
8. [Compose Multiplatform](https://www.jetbrains.com/compose-multiplatform/) — *JetBrains*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/cross-platform/` | Aligned to TOGAF · Gartner · OWASP MASVS*
