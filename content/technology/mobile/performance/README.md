# Mobile Performance

Cold start under 2 seconds, frame budget under 16.67 ms, Baseline Profiles delivering 30 percent cold-start wins, StrictMode catching main-thread offences in debug, and the platform tools that measure each — Macrobenchmark, Instruments, Compose recomposition tracing, and Animation Hitches.

**Section:** `technology/mobile/` | **Subsection:** `performance/`
**Alignment:** Android Vitals | Apple WWDC Performance Sessions | Google Play Core Web Vitals | ISO/IEC 25010 Performance Efficiency
**Audience:** Mobile Engineers · Mobile Architects · QA Performance

---

## Overview

Mobile performance is the discipline of measuring everything, budgeting against numeric targets, and rejecting any change that moves a metric in the wrong direction. Apps that ship without per-release performance gates regress invisibly — a refactor here, a new analytics SDK there, a third-party dependency upgrade somewhere — until the median cold start has crept from 1.4 seconds to 3.8 seconds and the team blames the user's "old phone." Apps that ship with budgets and CI-enforced gates do not have that conversation.

The targets in 2026 are well-established. Cold start under 2 seconds on a median three-year-old mid-range device — Pixel 6a on Android, iPhone 11 on iOS — is the consumer baseline that Google Play Vitals and App Store Analytics surface in the developer dashboards. Frame budget at 60 fps is 16.67 ms, at 90 fps is 11.11 ms, at 120 fps is 8.33 ms; jank is any frame that misses budget by more than the budget itself (i.e., a 33 ms frame at 60 fps target). Android Baseline Profiles deliver measured 30 percent cold-start improvements on apps that adopt them; iOS pre-main optimisation through dynamic-framework consolidation delivers similar wins on the iOS side.

The architectural shift is not "we made the app faster." It is: **mobile performance is a measured, budgeted, CI-gated discipline with cold-start, frame-budget, memory, and binary-size targets per device tier; the team has tools (Macrobenchmark, Instruments, Perfetto, Animation Hitches) to measure each; and any regression beyond the budget blocks the release until remediated.**

---

## Core Principles

### 1. Budget against a tier-2 device, not a tier-1 demo phone

The team measures on the median device, not the flagship. Pixel 6a, iPhone 11, mid-range Galaxy A. The flagship's performance is not the user's performance; the user's performance is what gets reviewed in the App Store.

### 2. Cold start is the first impression and is gated

Cold start under 2 seconds; regression beyond budget blocks release. Measured with `adb shell am start -W` on Android, Xcode Instruments Time Profiler on iOS, automated nightly on Firebase Test Lab device matrix.

### 3. Frame budget is non-negotiable on scrolling lists

LazyColumn, LazyVerticalGrid, List, ScrollView — anywhere the user scrolls, the frame budget governs. 60 fps is the floor; 90 / 120 fps where the device supports it. Animation Hitches instrument tracks hitches above 250 ms; budget zero hitches above 500 ms on a tier-2 device.

### 4. Recomposition and redraw discipline beats CPU optimisation

The single most-common cause of mobile frame-budget misses is unnecessary recomposition (Compose) or redraw (SwiftUI). `remember`, `derivedStateOf`, `key()`, `@Observable` access-tracking, and view-state hoisting reduce the work done per frame. CPU optimisation matters; redraw discipline matters more.

### 5. Baseline Profiles are mandatory on apps with cold-start SLAs

Generate per release with Jetpack Macrobenchmark. Ship in the App Bundle. Measure the improvement against the no-profile baseline. The 30 percent cold-start win is real and is free engineering effort beyond the initial setup.

### 6. StrictMode in debug, not in release

`StrictMode.setThreadPolicy(detectAll().penaltyDeath())` on Android, `os_signpost` and `MainActor`-checking assertions on iOS catch main-thread offences during development. Disabled in release because the penalties would crash users; the bug is caught before release in CI.

---

## Architecture Deep-Dive

**Cold Start Anatomy**

On Android, cold start is the time from `am start` to the first frame the user sees fully drawn. Three phases: process creation (OS work, 100-300 ms), Application onCreate (app's initialisation, target under 100 ms), and Activity onCreate plus first composition (target under 1500 ms on tier-2). Each phase has its measurement and optimisation playbook.

Application onCreate is the most common cold-start offender — initialisation of analytics, crash reporting, image loaders, dependency injection container, ad SDKs. The fix is App Startup library (`androidx.startup`) plus aggressive deferral: only the dependencies that the first screen requires synchronously initialise on the main thread; everything else moves to a `WorkManager` job or to lazy initialisation on first use.

```kotlin
// Application onCreate — keep minimal
override fun onCreate() {
    super.onCreate()
    AppStartup.getInstance(this).initializeComponent(CriticalInitializer::class.java)
    // Analytics, crash, image loader, ads — deferred to AppStartup background path
}
```

Baseline Profiles compile the app's cold-start methods AOT into machine code at install time. Without Baseline Profiles, ART uses JIT compilation, paying interpretation cost on every cold start until the methods are JIT-compiled. The Baseline Profile eliminates the interpretation cost on the documented hot path.

On iOS, cold start is split into pre-main and post-main. Pre-main time (dyld linking, static initialisers, framework loads) is measured with `DYLD_PRINT_STATISTICS=1`. Optimisations: convert dynamic frameworks to static libraries (eliminates the per-framework dyld cost), strip unused symbols, audit `__attribute__((constructor))` usage. Post-main time (UIApplicationMain through first frame) is measured with Xcode Instruments. Optimisations: defer `application(_:didFinishLaunchingWithOptions:)` work to background, lazy initialisation, splash-screen-to-content transition rather than blocking on data.

**Frame Budget**

60 fps → 16.67 ms per frame. 90 fps → 11.11 ms. 120 fps → 8.33 ms. ProMotion iPad and the iPhone 13 Pro and later support 120 fps; Pixel 8 Pro supports 120 fps; most premium 2024+ Android devices do.

Compose recomposition optimisation:

```kotlin
@Composable
fun AccountList(transactions: List<Transaction>) {
    val sortedTransactions = remember(transactions) {
        transactions.sortedByDescending { it.timestamp }
    }
    val totalAmount by remember(sortedTransactions) {
        derivedStateOf { sortedTransactions.sumOf { it.amount } }
    }
    LazyColumn {
        items(sortedTransactions, key = { it.id }) { txn ->
            TransactionRow(txn)
        }
    }
}
```

`remember` caches the sort across recompositions. `derivedStateOf` causes `totalAmount` to recompose only when the sorted list changes (not on every parent recomposition). `key = { it.id }` in `items` allows Compose to match items across data changes and skip recomposition for unchanged items.

SwiftUI's `@Observable` macro improves this story significantly: views read specific properties, the macro tracks access, and SwiftUI redraws only on the accessed properties' changes — without the explicit `derivedStateOf` discipline Compose requires.

**Dispatcher Selection on Kotlin Coroutines**

`Dispatchers.Main` only for UI updates. `Dispatchers.IO` for network and disk (up to 64 threads). `Dispatchers.Default` for CPU-bound work (one thread per CPU core). Mis-selection costs: CPU-bound work on `Dispatchers.IO` saturates the IO pool and blocks legitimate IO; disk work on `Dispatchers.Default` blocks CPU-bound work behind disk latency.

**Swift Concurrency Actors**

`Actor`-protected state serialises access to shared mutable data. The cost is real (actor hops are ~1 μs each) and bounded; the benefit is compile-time-checked freedom from data races. Use `MainActor` for UI-bound state; `actor` for repositories and caches; reserve `@unchecked Sendable` for measured cases where the actor cost is unacceptable.

**Measurement Tools**

Android:
- **Macrobenchmark**: cold start, frame-by-frame metrics, scroll performance, app startup phases.
- **Perfetto**: system-wide trace including ART, render thread, RenderEngine, GPU.
- **Android Studio Profiler**: real-time CPU, memory, network during interactive debugging.
- **Android Vitals (Play Console)**: in-the-wild ANR, slow start, slow frames aggregated across user devices.

iOS:
- **Xcode Instruments Time Profiler**: function-level CPU sampling.
- **Animation Hitches Instrument**: frame-budget misses with severity.
- **Allocations Instrument**: heap growth, retain cycles, leaked allocations.
- **MetricKit**: device-side aggregated metrics (CPU exceptions, disk writes, hang reports) delivered to the app daily.

**Memory Budget**

Android: keep heap under 100 MB on tier-2 devices; the Android Vitals "excessive memory" warning triggers above 256 MB; Java heap above 350 MB triggers OOM kill on devices with 4 GB total RAM. iOS: 80 MB baseline at launch; jetsam termination triggers above 300 MB on devices that still run iOS 17+ with 4 GB RAM.

---

## Implementation Guide

### Step 1: Establish numeric budgets per device tier

Document cold start, frame budget, memory ceiling, binary size for tier-1 (flagship), tier-2 (median), tier-3 (emerging market) devices. Budgets are committed to the architecture documentation.

### Step 2: Wire Macrobenchmark into CI

Macrobenchmark module runs nightly on Firebase Test Lab against a representative device matrix. Cold start, frame budget, scroll performance reported per build.

### Step 3: Generate and ship Baseline Profiles

`BaselineProfileGenerator` runs as part of Macrobenchmark. Generated `baseline-prof.txt` committed and packaged with the App Bundle. Cold-start improvement measured against the no-profile baseline; the result is in the release notes.

### Step 4: Enable StrictMode in debug builds

`detectAll().penaltyDeath()` on Application onCreate when `BuildConfig.DEBUG`. Debug builds crash on main-thread disk or network access. The bug is caught locally before it reaches the user.

### Step 5: Instrument the highest-traffic screens

Animation Hitches instrument run on Home, List, Detail, Checkout. Hitches above 250 ms tracked as bugs. Hitches above 500 ms block release.

### Step 6: Subscribe to MetricKit and Android Vitals alerts

Daily MetricKit reports ingested into the team's observability stack. Android Vitals slack alerts on regression of cold-start P95 or ANR rate.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Per-tier performance budgets documented | Mobile Architect | Cold start, frame, memory, binary-size budgets per device tier | Required |
| Macrobenchmark in CI | Build Engineering | Nightly runs on device matrix; results posted to dashboard | Required |
| Baseline Profile shipped | Mobile Engineering Lead | Profile committed; cold-start improvement reported per release | Required |
| StrictMode penalty=death in debug | Mobile Engineering Lead | Configured on Application onCreate; CI tests run with policy enabled | Required |
| Hitch budget enforced | Mobile Engineering Lead | Animation Hitches measured on top-5 screens per release; budget gated | Required |
| MetricKit / Android Vitals alerting | Observability Team | Alerts wired to on-call channel for cold-start P95 regressions | Required |

---

## Security Considerations

- Performance instrumentation collects telemetry that may include screen names, navigation paths, and timing data — none of this should include PII. Firebase Performance Monitoring's automatic URL capture redacts query parameters by default; verify the redaction covers your specific PII patterns.
- Background sync workers must respect Doze mode and App Standby on Android; aggressive scheduling drains battery and triggers OS throttling that can disable the app's background sync entirely.
- StrictMode penalties produce stack traces that may contain file paths and internal class names; configure penalty=death only in debug builds and penalty=log in release builds where the team genuinely needs the signal.

---

## Performance Considerations

- Cold start budget: under 2 s on tier-2; under 1.2 s on tier-1; under 3 s on tier-3. Measure on every release.
- Frame budget: 0 hitches above 500 ms on top-5 screens; 60 fps sustained on lists; 90 / 120 fps on ProMotion / 120 Hz devices.
- Memory budget: heap under 100 MB Android, under 80 MB iOS at launch; growth under 200 MB during heavy usage.
- Binary size: under 25 MB AAB Android, under 35 MB IPA iOS. Play Store install-size warnings trigger above 25 MB.
- ANR rate: under 0.47 percent (Google Play Vitals threshold for "exceeds the bad-behaviour threshold"); aim under 0.1 percent.
- Cold-start P95: under 4 s on Android Vitals; over 5 s flags the app.

---

## Anti-Patterns to Avoid

### ⚠️ Measuring on the Flagship Only

The team's CI runs on a Pixel 8 Pro because "we have one in the lab." Real users on Pixel 6a hit 3-second cold starts that nobody notices. The fix is the tier-2 device in CI as the gating measurement.

### ⚠️ Skipping the Baseline Profile

The team knows about Baseline Profiles, decides "we'll do them later," ships releases with 30 percent more cold-start time than necessary. The fix is the CI gate that produces the profile on every release.

### ⚠️ Compose Without `remember` / `derivedStateOf`

Engineers write `val sorted = items.sortedBy { it.date }` directly in the composable body. Every recomposition re-sorts. Scrolling stutters. The fix is the lint rule that flags expensive operations outside `remember`, and the code-review discipline that catches the rest.

### ⚠️ Synchronous SDK Initialisation in onCreate

Five analytics SDKs and an ads SDK initialise synchronously in `Application.onCreate`. Cold start adds 800 ms. The fix is App Startup library plus deferred initialisation; the home screen renders before the SDKs are ready.

### ⚠️ Treating Performance as Someone Else's Problem

Engineers ship features without measuring performance impact. The architect notices the regression in monthly review. By the time the fix is identified, three releases have shipped the regression. The fix is the per-PR performance check in CI — Macrobenchmark on the touched screen — that surfaces regressions when the engineer can still recall the cause.

---

## AI Augmentation Extensions

### AI-Assisted Performance Triage

LLM-based analysis of Macrobenchmark and Animation Hitches output classifies regressions by likely cause (recomposition spike, new SDK init, animation specification) and proposes investigation steps. The mobile engineer's triage time compresses from hours to minutes for routine regressions.

### AI-Assisted Baseline Profile Coverage

User-journey scripts for Baseline Profile generation are generated by LLMs from the screen graph and from analytics-tracked navigation patterns. Coverage of cold-start hot paths improves measurably.

---

## References

1. [Android App Startup](https://developer.android.com/topic/performance/vitals/launch-time) — *developer.android.com*
2. [Jetpack Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — *developer.android.com*
3. [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — *developer.android.com*
4. [Compose Performance](https://developer.android.com/jetpack/compose/performance) — *developer.android.com*
5. [WWDC 2023 — Analyse hangs with Instruments](https://developer.apple.com/videos/play/wwdc2023/10248/) — *developer.apple.com*
6. [MetricKit](https://developer.apple.com/documentation/metrickit) — *developer.apple.com*
7. [Perfetto Tracing](https://perfetto.dev/) — *perfetto.dev*
8. [Google Play Android Vitals](https://developer.android.com/quality/performance) — *developer.android.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/performance/` | Aligned to Android Vitals · Apple WWDC · ISO/IEC 25010*
