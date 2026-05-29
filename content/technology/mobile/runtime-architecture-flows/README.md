# Runtime Architecture Flows

> **Section:** `technology/mobile/runtime-architecture-flows/`
> **Alignment:** Android Activity/Fragment Lifecycle | iOS App Lifecycle | Background Execution Limits
> **Audience:** Mobile Engineers · Architects · SREs

Runtime architecture flows describe how the application behaves across the full lifecycle: from cold start through user interaction to backgrounding, process death, and restoration. Understanding and correctly implementing these flows is what separates apps that "just work" from apps that lose user data, consume unexpected battery, produce ANRs, or crash on rotation.

## Overview

The platform lifecycle is the contract between the operating system and the application. The OS calls lifecycle methods according to resource pressure, user navigation, and system events. Applications that honour this contract are well-behaved — they save state before suspension, release resources when backgrounded, and restore state correctly when resumed. Applications that ignore the contract produce data loss, crashes, and excessive battery drain.

## Android Lifecycle Flows

### Activity and Fragment Lifecycle
The Android Activity lifecycle has seven states: Created, Started, Resumed (visible and interactive), Paused (partially obscured), Stopped (fully obscured), Destroyed. Configuration changes (rotation, language, dark mode toggle) destroy and recreate the Activity — the most common source of state loss bugs. ViewModel survives configuration changes through `ViewModelStore` — this is the primary reason ViewModel exists. `SavedStateHandle` (backed by `onSaveInstanceState`) survives process death — use it for navigation arguments and form state that must survive even process termination.

### Process Death
Android may kill background processes to reclaim memory. There is no lifecycle callback for process death — the process is simply terminated. State that must survive process death: commit to Room database or DataStore before the app leaves the foreground. `onStop()` is the reliable final lifecycle event before potential process death. Do not rely on `onDestroy()` — it is not guaranteed to be called before process termination.

### Coroutine Lifecycle
Coroutines launched without lifecycle awareness continue after the Activity is destroyed — leaking resources and potentially crashing on dead UI references. `viewModelScope` cancels all coroutines when the ViewModel is cleared (Activity destroyed non-temporarily). `lifecycleScope.launchWhenStarted` cancels collection when the lifecycle moves below Started — correct for UI-bound coroutines. `repeatOnLifecycle(Lifecycle.State.STARTED)` is the preferred API for collecting from Flows in the View layer.

## iOS Lifecycle Flows

### UIApplication States
iOS application states: Not Running, Active (foreground, receiving events), Inactive (foreground, not receiving events — during interruptions like calls), Background (executing code, limited time), Suspended (no code execution). The transition from Active to Background triggers `applicationDidEnterBackground` — the last reliable point to commit state before potential termination. iOS gives approximately 5 seconds of background execution time after this event.

### Scene-Based Lifecycle
Modern iOS (iOS 13+) uses scene-based lifecycle for multi-window support on iPad and Catalyst. `UIWindowSceneDelegate` receives scene-specific lifecycle events alongside the app-level `UIApplicationDelegate`. SwiftUI's `@Environment(\.scenePhase)` provides a reactive scene phase value (`active`, `inactive`, `background`).

### Memory Pressure
iOS sends memory warnings (`applicationDidReceiveMemoryWarning`, `didReceiveMemoryWarning` on UIViewController) when the system is low on memory. Respond by releasing caches and non-critical resources. Applications that ignore memory warnings are terminated first when the system needs memory.

## Background Execution

Android background execution is managed by WorkManager — the only reliable mechanism for guaranteed background work that survives process death and device restart. WorkManager uses JobScheduler (API 21+) or AlarmManager (API < 21) under the hood, selecting the appropriate mechanism automatically. Constraints: `NetworkType.CONNECTED`, `requiresBatteryNotLow()`, `requiresCharging()`. Expedited work: `setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)` for time-sensitive operations.

iOS background execution: `BGProcessingTask` for longer operations (up to 30 minutes when charging and on Wi-Fi). `BGAppRefreshTask` for lightweight data refresh (up to 30 seconds, system-scheduled). Register tasks in `Info.plist` with permitted identifiers. The system assigns execution time based on device state, battery level, and user patterns — do not assume immediate execution.

## Anti-Patterns to Avoid

> **⚠ State Lost on Rotation** — Activity stores list of transactions in a local variable. User rotates device. Activity is destroyed and recreated. Variable is empty. User sees an empty screen.
> **CORRECT:** ViewModel stores the list. ViewModel survives rotation. The recreated Activity resubscribes to ViewModel's StateFlow and receives the existing data immediately.

> **⚠ Infinite Background Service** — Android Service that runs continuously in the background, consuming CPU and battery. Killed by Doze mode and background execution limits.
> **CORRECT:** WorkManager with appropriate constraints. The work is guaranteed to execute when constraints are met — not necessarily immediately, but reliably.

## References

1. Google — Android Activity Lifecycle. developer.android.com/guide/components/activities/activity-lifecycle
2. Google — WorkManager. developer.android.com/topic/libraries/architecture/workmanager
3. Apple — App Lifecycle. developer.apple.com/documentation/uikit/app_and_environment/managing_your_app_s_life_cycle
4. Apple — Background Tasks. developer.apple.com/documentation/backgroundtasks
