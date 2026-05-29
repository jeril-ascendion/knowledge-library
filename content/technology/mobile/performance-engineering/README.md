# Performance Engineering

> **Section:** `technology/mobile/performance-engineering/`
> **Alignment:** Google Android Vitals | Apple MetricKit | Core Web Vitals (mobile) | RAIL Performance Model
> **Audience:** Mobile Engineers · Performance Engineers · QA Architects · SREs

Performance engineering for mobile is the systematic practice of measuring, setting targets for, and improving the runtime performance characteristics of mobile applications across the dimensions that users experience directly: how quickly the app starts, how smoothly it animates, how much battery it consumes, how much memory it uses, and how quickly it responds to user input.

## Overview

The RAIL performance model (Response, Animation, Idle, Load) adapted for mobile: Response to user input under 100ms (no perceptible lag). Animation at 60fps minimum (16.67ms frame budget). Idle time used for background work that does not consume the main thread. Load (cold start) under 2 seconds on the median device. These targets are specified as requirements, measured continuously in CI, and monitored in production.

## Startup Performance

Cold start begins when the OS creates the application process and ends when the first frame is visible. The two phases: pre-main (Android: class loading, DexOpt, static initializers; iOS: dylib linking, ObjC runtime setup, static initializers) and post-main (Application.onCreate / AppDelegate.application:didFinishLaunchingWithOptions, DI graph construction, first Activity/UIViewController creation).

Android optimizations: Baseline Profiles generate Ahead-of-Time compilation hints for the Play Store installer, reducing cold start by 30% by pre-compiling hot methods and classes. Generated with Jetpack Macrobenchmark in `CompilationMode.Full`. App Startup library parallelises Initializer execution. Hilt: avoid heavy work in singleton constructors.

iOS optimizations: Reduce dylib count (use static libraries where possible). Eliminate or defer static initializers. Use lazy initialization for expensive objects. Measure with Instruments Time Profiler — the pre-main and post-main timeline is visualised directly.

## Frame Rate and Jank

The 16.67ms frame budget covers: measure (layout calculation), draw (composable execution / view drawing), submit (GPU command submission). Any work on the main thread that exceeds the budget causes a dropped frame — visible to the user as stutter.

Compose recomposition optimization: `remember {}` caches expensive calculations, avoiding recomputation on every composition. `derivedStateOf {}` creates computed state that only re-emits when the computed value changes — preventing downstream recompositions from upstream state changes that don't affect the downstream computation. `key()` in `LazyColumn` items ensures correct reuse of composables when list items move.

iOS Core Animation: offscreen rendering (red overlay in Instruments) indicates a CALayer property requires an offscreen compositing pass. Common causes: `cornerRadius` with `masksToBounds`, non-opaque views, `shouldRasterize`. Blended layers (green overlay): semi-transparent views requiring alpha compositing.

## Memory Management

Android GC pauses cause jank — avoid object allocation in draw code (`Canvas.drawBitmap()`, custom View `onDraw()`). Use object pooling for frequently allocated objects in RecyclerView. Detect memory leaks with Android Studio Memory Profiler heap dumps and LeakCanary library. LeakCanary hooks into the GC and surfaces retained objects with stack traces.

iOS ARC retain cycles: a closure that captures `self` strongly, stored in a property of `self`, creates a retain cycle — both objects hold strong references and neither is deallocated. Fix with `[weak self]` or `[unowned self]` in the closure capture list. Use Xcode Memory Graph Debugger to visualise the object graph and identify cycle participants.

## Battery Optimization

Every wakeup has a cost. Batch background work using WorkManager (Android) or BGTaskScheduler (iOS) rather than scheduling frequent small tasks. Use significant-change location API instead of continuous GPS tracking when exact location is not required continuously. Avoid wake locks outside of active processing — use WorkManager's constraint system to run background work only when the device is charging or on Wi-Fi.

## Anti-Patterns to Avoid

> **⚠ I/O on Main Thread** — Reading from SharedPreferences, database queries, or network calls on the main thread. Produces ANR on Android (5 seconds), hangs the UI on iOS. Detected by StrictMode (Android) and Thread Sanitizer (iOS) in debug builds.
> **CORRECT:** Dispatchers.IO for all disk and network operations. Dispatchers.Default for CPU-intensive work. Main thread reserved exclusively for UI rendering and user interaction handling.

> **⚠ Unnecessary Recomposition** — A Compose function that reads from a large StateFlow object recomposes every time any field in that object changes, even fields it does not use.
> **CORRECT:** Decompose large state into smaller, independent state objects. Use `derivedStateOf` to compute derived values that only change when relevant inputs change.

## References

1. Google — App Startup Time. developer.android.com/topic/performance/vitals/launch-time
2. Google — Baseline Profiles. developer.android.com/topic/performance/baselineprofiles
3. Apple — MetricKit. developer.apple.com/documentation/metrickit
4. LeakCanary — Memory Leak Detection. square.github.io/leakcanary
