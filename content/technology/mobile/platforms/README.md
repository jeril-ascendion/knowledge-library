# Platform Foundations & Technology Decisions

> **Section:** `technology/mobile/platforms/`
> **Alignment:** TOGAF Technology Architecture | Google MAD | Apple Platform Standards | CNCF Mobile | IEEE 730
> **Audience:** Solutions Architects · Mobile Engineering Leads · CTOs · Technical Strategists

The platform decision is the single most expensive choice a mobile programme makes. Get it wrong and the next five years are spent rewriting; get it right and the team compounds productivity release after release. Written by a Principal Mobile Architect who has evaluated platform choices for twenty enterprise clients and shipped production apps on Android, iOS, Flutter, React Native, and Kotlin Multiplatform.

---

## The Platform Landscape

Four deployment models are credible in 2026 and each is the correct engineering answer for a specific kind of programme. **Pure Native** ships two separate codebases — Swift with SwiftUI on iOS, Kotlin with Jetpack Compose on Android — and accepts the staffing and coordination overhead in exchange for the highest UX fidelity and deepest platform-API access. **Cross-Platform Compiled** is Flutter's territory: Dart compiles ahead-of-time to native ARM, the Impeller engine paints every pixel, and the same binary widget tree renders identically on both platforms. **Cross-Platform Interpreted** is React Native's New Architecture — TypeScript bridging to actual UIKit and Android View widgets through JSI and Fabric, paying a runtime cost for ecosystem leverage. **Hybrid** wraps a WebView around an HTML/CSS/JavaScript application via Capacitor or the legacy Ionic framework, appropriate only when the team is web-native and the UX expectations match a website's.

The global market reality matters. Statcounter places Android at roughly 72 percent of global mobile market share through 2025; iOS at roughly 27 percent. The headline mis-leads. iOS users monetise at 2.5x the per-user rate in premium markets including Philippines retail banking (BPI, BDO, and Maya consistently see 60-plus percent of mobile-banking sessions on iOS even though Android holds 75 percent of devices) and US enterprise SaaS. Android dominates emerging markets — India, Brazil, Indonesia, sub-Saharan Africa — where price-tier-two and tier-three devices and intermittent connectivity define the engineering brief. Choose without per-geography and per-segment data and you choose against a fiction.

Enterprise reality is sharper still. iOS dominates US, UK, Japan, Australia, Canada financial services, healthcare, and any sector where the user is also the buyer. Android dominates emerging-market consumer apps, retail point-of-sale, kiosks, dedicated devices, and any government programme distributing devices at scale. Mixed-platform enterprise apps over the past five years have skewed toward the platform their employees or customers carry first — the architecture follows the user, not the other way.

---

## Native Android — Modern Android Development

Google's Modern Android Development (MAD) stack is the canonical 2026 architecture for native Android and the published reference at developer.android.com/topic/architecture. **Jetpack Compose** replaces XML layouts as the UI layer — composable functions, declarative state-driven rendering, no findViewById, no inflated views. State hoisting is the architectural principle: stateful composables (those that own `var`s through `remember`) are reserved for the deepest leaf widgets; everything above is stateless and renders from the state passed in. The performance benefit is measurable — Compose's Snapshot system tracks which composables read which state and recomposes only those reads, where the XML view system invalidated the entire layout subtree on any change.

**ViewModel** is the lifecycle-aware state owner. The pattern survived configuration changes that destroyed Presenter and Controller patterns of the prior decade because the ViewModel scope outlives the Activity and Fragment hosts. **StateFlow** carries UI state — hot, conflated, always has a current value — and **SharedFlow** carries one-time events like navigation and toast triggers. The **UiState sealed class** pattern (`sealed class ScreenUiState { data class Content(val data: List<Item>) ; object Loading ; data class Error(val message: String) }`) is the integration contract between ViewModel and Compose: the screen's branch on UiState is exhaustive and the compiler enforces handling every case.

**Hilt** is the dependency-injection container the platform endorses. Scopes are explicit: `@Singleton` for app-lifetime services (Retrofit, Room, Auth), `@ActivityRetainedScoped` for state surviving configuration change, `@ViewModelScoped` for ViewModel-lifetime collaborators, `@ActivityScoped` and `@FragmentScoped` for shorter spans. The compile-time graph catches missing bindings before the build completes. **Room** owns local persistence with type-safe `@Query`, parameterised by design, with explicit migration paths between schema versions. `@TypeConverter`s handle complex types; `@Embedded` flattens value objects into the table. **Kotlin Coroutines** with intentional dispatcher selection — `Dispatchers.IO` for network and disk, `Dispatchers.Default` for CPU work, `Dispatchers.Main` only for UI — replaces RxJava and the legacy AsyncTask. **KSP** (Kotlin Symbol Processing) replaces KAPT for annotation processing with measured 2x speed; Hilt, Room, and Moshi all support KSP.

**Baseline Profiles** are the recent performance breakthrough. A Baseline Profile is a text file listing class and method names that Play Store pre-compiles ahead of time at install. Jetpack Macrobenchmark generates the profile from a recorded critical-path script; Google measured 30 percent cold-start improvement on the Now in Android reference app, 22 percent on Reddit, 25 percent on Lyft. Feature modularisation — by feature not by layer (each Gradle module `feature-account` contains its own UI, ViewModel, domain, data) — accelerates parallel compilation, the dependency graph is a directed acyclic enforcement boundary, and the App Bundle dynamic delivery becomes possible. **Now in Android** at github.com/android/nowinandroid is the canonical reference every Android programme should read first.

---

## Native iOS — Modern iOS Development

SwiftUI has matured into the default UI layer with documented interop strategy for the small set of UIKit-only surfaces that remain (complex text engine, `UICollectionViewCompositionalLayout`, AVFoundation camera previews, ARKit). **Swift Concurrency** — `async`/`await`, `Actor`, `AsyncStream`, structured concurrency with `TaskGroup` — replaces completion handlers, `DispatchQueue`, and Combine's reactive complexity for new code. The compiler under strict concurrency catches data races at compile time. `@MainActor` is the type-system annotation that the function or property is touched only on the main thread; the compiler rejects calls from other contexts.

The **@Observable macro** introduced in Swift 5.9 supersedes `@ObservableObject` and `@Published`. The macro generates per-property observation infrastructure; SwiftUI's `withObservationTracking` reads the access pattern at render time and redraws only the views that read the property that changed — not every view in the observation graph. The measured performance improvement on screens with many observable fields is substantial.

**SwiftData** is the property-wrapper persistence layer integrated with SwiftUI, the recommended path for new persistence work over Core Data. `@Model` declares the persistent class; `@Query` exposes a reactive query into the SwiftUI view. The store is SQLite under the hood; the migration path supports schema evolution.

Dependency injection has no Apple-blessed framework. **Factory** by Michael Long provides compile-time-checked service location; **Resolver** offers property-wrapper-based injection. Hand-rolled composition roots are appropriate for projects that resist third-party dependencies. The decision is less consequential than on Android because Swift's type system catches more wiring errors at compile time.

**Instruments Time Profiler** is the irreplaceable performance tool. Pre-main startup time (dyld linking, static initialisers, framework loads) measured via `DYLD_PRINT_STATISTICS=1` reveals the dynamic-framework cost; converting dynamic frameworks to static libraries via `MACH_O_TYPE = staticlib` is a high-leverage optimisation. Post-main startup (`UIApplicationMain` through first frame) is measured by Instruments. The App Startup lifecycle blurs the legacy `UIApplicationDelegate` and the new `App` protocol: `@UIApplicationDelegateAdaptor` bridges them when push notifications and deep-link bootstrap require AppDelegate hooks. **BGTaskScheduler** (`BGAppRefreshTask` for short opportunistic windows, `BGProcessingTask` for longer power-attached work) is the iOS background-work API; the OS decides when, the developer requests but does not command.

---

## Flutter

Flutter compiles Dart to native ARM machine code for release builds. The UI is rendered by Flutter's own engine — historically Skia, now Impeller on iOS since Flutter 3.10 and Impeller GA on Android in 2024. Impeller pre-compiles shaders, eliminating the first-frame stutter that plagued Skia on iOS. Hot reload preserves widget state and ships changes to the running app in under a second; the developer-experience gap over native is real for UI iteration.

**BLoC** (Business Logic Component) is the Flutter community's canonical state-management pattern: Events flow in, States flow out, the Bloc is a pure transformation in the middle, tests assert state transitions on event input. **Riverpod** by Remi Rousselet is the modern Provider successor — compile-time-safe dependency injection plus reactive providers that subscribe widgets to specific reads. **GetX** is the lightweight choice for smaller programmes that value pragmatism over rigour.

Flutter's tree model has three layers: the **Widget tree** is the immutable declarative description the developer writes; the **Element tree** is the instantiated runtime graph maintaining identity across rebuilds; the **Render tree** is the layout-and-paint backing graph that produces the on-screen pixels. Understanding the three is the difference between a Flutter developer who fights frame drops and one who avoids them.

**Platform channels** are the contract to native code — `MethodChannel` for request-response, `EventChannel` for streams, `BasicMessageChannel` for arbitrary payloads. The Pigeon code generator produces type-safe bindings on both sides. Real production adoption: Google Pay's redesign on Flutter, BMW's My BMW app, Alibaba's Xianyu marketplace, eBay Motors, Cash App's Cash App for Families feature. Flutter's strength is custom-canvas UIs and brand-consistent multi-platform apps; its weakness is HIG-compliant iOS apps where pixel-identical-across-platforms is a liability not a feature.

---

## React Native — New Architecture

The fundamental shift from React Native's Old Architecture to the New Architecture is the biggest engineering change in the framework's history. The **Old Architecture** used a Bridge — JavaScript-to-native calls serialised as JSON across an asynchronous boundary, batched and flushed each frame. Every prop update was a round-trip with measurable cost; lists felt laggy under load; performance-sensitive features required native modules and ad-hoc bridging.

The **New Architecture** replaces the Bridge with three primitives. **JSI** (JavaScript Interface) gives JavaScript direct C++ memory access — synchronous native calls, no serialisation overhead. **Fabric** is the new UI rendering layer with synchronous updates and a more efficient measurement and layout pipeline. **TurboModules** lazy-load native modules on first use and expose them through JSI with type-safe Codegen-generated bindings. Lists that previously felt laggy now perform within 10-15 percent of native; the long-standing performance gap has narrowed to the point where React Native is a credible default again for non-graphical apps.

**Expo** is the zero-configuration framework that sits on top of React Native. **Expo Router** provides file-based navigation that matches the Next.js mental model React developers already have; **EAS Build** runs Android Gradle and iOS Xcode builds in the cloud against Expo-managed credentials; **EAS Submit** uploads to TestFlight and Play Console. Expo's prebuild flow lets teams switch from the managed workflow to the bare workflow when native customisation is required.

Production adoption is broad: Meta (Facebook, Instagram, Marketplace), Microsoft (Office Mobile, Outlook on iOS for some flows), Shopify, Coinbase, and Discord — the last published a detailed migration to the New Architecture with documented performance results in late 2024.

---

## Kotlin Multiplatform

Kotlin Multiplatform (KMP) shares Kotlin business logic — domain models, repositories, networking, state machinery — and compiles it to JVM bytecode on Android and to native ARM via Kotlin/Native on iOS. The native UI stays native: SwiftUI on iOS, Compose on Android. Targets extend to Kotlin/JS for web and JVM for desktop.

**Compose Multiplatform** by JetBrains extends Compose UI to iOS, Desktop, and Web — Compose for iOS reached 1.0 in 2024 and adoption is rising for teams willing to accept the iOS UI fidelity trade-off. Cash App at Block has documented KMP as the architecture they "wish they'd had from the start," with shared logic powering multiple Block products. KMP wins over Flutter when the team values platform-native UI fidelity over UI code sharing; it wins over React Native when the team is Kotlin-fluent and the iOS team accepts the consume-the-shared-XCFramework workflow. The five-year TCO for KMP is 70-80 percent of pure native — the saving is logic-layer code, not UI-layer skill.

---

## Platform Decision Matrix

The decision is a weighted-criteria spreadsheet, not a framework enthusiasm. Eight dimensions, each weighted 1-5 by business context, each scored 1-5 per candidate. Sum and compare.

| Dimension | Pure Native | Flutter | React Native | KMP | MAUI |
|---|---|---|---|---|---|
| Team skills already in place | varies | low | medium | medium | low unless .NET |
| UX fidelity to platform | 5 | 3 | 4 | 5 | 4 |
| Performance SLA | 5 | 4 | 4 | 5 | 3 |
| Device API depth | 5 | 3 | 3 | 5 | 3 |
| Time to first release | 2 | 4 | 4 | 3 | 3 |
| Five-year TCO | 2 | 4 | 4 | 3 | 3 |
| Vendor commitment stability | 5 (Apple/Google) | 4 (Google) | 3 (Meta) | 4 (JetBrains+Google) | 2 (Microsoft strategy unclear) |
| Regulatory + attestation | 5 | 3 | 3 | 5 | 3 |

Recommended combinations for four client archetypes: **Fintech startup** — Flutter for speed plus native specialists for biometrics and Apple Pay / Google Pay. **Enterprise bank** — pure native iOS plus pure native Android, with KMP for shared business rules once the programme matures. **Healthcare provider** — pure native with HIPAA-compliant tooling and rigorous attestation. **Government agency** — pure native with rigorous accessibility audits and on-premise distribution via MDM rather than the public stores.

---

## Anti-Patterns

### 1. Choosing platform by developer preference

The CTO picks React Native because their existing web team can be redeployed without retraining. Six months later the team is fighting JSI bridge bugs they have no skills to debug. The fix is honesty: name the hiring constraint as a constraint in the ADR, accept the trade-offs, and budget for native specialists on the integration boundary.

### 2. Starting cross-platform then switching to native mid-project

Airbnb's 2018 migration off React Native is the documented case study. The cross-platform saving never materialised because cross-team coordination cost exceeded the code-sharing benefit. The fix is the two-week framework spike before commitment and the ADR with explicit rejection criteria that would re-open the decision.

### 3. Choosing React Native for a performance-critical real-time feature

The team picks React Native for a live-trading or real-time-multiplayer app. The JavaScript runtime cost is the bottleneck. The fix is naming the performance SLA at decision time and pricing it into the framework comparison.

### 4. Flutter app with a web team that has never used Dart

The team's React and Vue muscle is genuine; their Dart muscle is zero. The first six months are spent learning Dart's syntax, the Widget tree mental model, and the platform-channel pattern. The fix is the two-week spike, honest skills mapping, and budgeted retraining time.

### 5. MAUI without an existing .NET mobile codebase

MAUI is the right answer for organisations already deep in .NET — Microsoft-shop enterprises, internal tools where C# expertise exists. For everyone else the framework's strengths are inaccessible and the framework's quirks dominate. The fix is honest skills inventory before the framework choice.

---

## References

1. [Modern Android Development](https://developer.android.com/modern-android-development) — *developer.android.com*
2. [Now in Android Reference App](https://github.com/android/nowinandroid) — *github.com*
3. [Apple Swift Concurrency Roadmap](https://www.swift.org/documentation/concurrency/) — *swift.org*
4. [Flutter Impeller](https://docs.flutter.dev/perf/impeller) — *docs.flutter.dev*
5. [React Native — The New Architecture](https://reactnative.dev/architecture/landing-page) — *reactnative.dev*
6. [Kotlin Multiplatform Production Cases](https://www.jetbrains.com/lp/kotlin-multiplatform-production/) — *JetBrains*
7. [Airbnb — Sunsetting React Native](https://medium.com/airbnb-engineering/sunsetting-react-native-1868ba28e30a) — *Airbnb Engineering*
8. [Discord — Why React Native](https://discord.com/blog/why-discord-is-sticking-with-react-native) — *discord.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/platforms/` | Aligned to TOGAF · Google MAD · Apple Platform Standards · CNCF Mobile*
