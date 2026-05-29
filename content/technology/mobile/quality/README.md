# Quality Engineering — Testing, Performance & Accessibility

> **Section:** `technology/mobile/quality/`
> **Alignment:** IEEE 829 Test Documentation | WCAG 2.2 AA | Google Android Vitals | Apple MetricKit | ISTQB Mobile Testing
> **Audience:** QA Architects · Mobile Engineers · Accessibility Engineers · SREs

---

## Mobile Testing Pyramid

Five layers from base to apex, with explicit population ratios and target durations per layer.

**Base — Unit Tests**. No device or emulator. Run in milliseconds per test. Test every Use Case and every ViewModel state transition. Target 90 percent line coverage on Use Cases and 80 percent on ViewModels — Repository and DataSource coverage tracked separately. Roughly 10,000 tests on a mature codebase; full suite executes in two to five minutes on a CI runner.

**Layer 2 — Snapshot Tests**. Render Compose or SwiftUI components on the JVM (Android) or in a hosted UIWindow (iOS), capture screenshots, diff against golden images committed to the repository. No emulator. Roughly 1,000 snapshots covering every component and every variant (theme, Dynamic Type size, locale direction). Full suite under one minute.

**Layer 3 — Integration Tests**. Repository plus in-memory Room database plus stubbed network layer running together on JVM (Robolectric on Android, XCTest in-process on iOS). Verify data flows through multiple layers without a device. Roughly 100 tests covering critical cross-layer contracts; suite under five minutes.

**Layer 4 — UI Tests**. Full user journeys on emulator or simulator using Espresso, XCUITest, or Maestro. Scope strictly to the top ten critical paths — sign-in, account view, transfer, payment, search, settings change, push-notification handling, deep-link entry, biometric unlock, onboarding. Roughly 50 tests; suite under ten minutes.

**Apex — E2E Tests**. Physical device matrix via Firebase Test Lab or BrowserStack App Automate. Smoke tests for the top five flows only. Run on every release candidate, not every PR. Roughly 5 tests; suite under fifteen minutes.

Programmes that invert the pyramid — many UI tests, few unit tests — ship slow, flaky CI that engineers learn to circumvent. The shape is the strategy.

---

## Unit Testing

**JUnit5 on Android**. `@Test` is the test marker; `@BeforeEach` and `@AfterEach` replace JUnit4's `@Before` / `@After`; `@ParameterizedTest` with `@MethodSource` drives data-driven tests cleanly. **Mockk** is the Kotlin-native mocking library: `coEvery { useCase.invoke() } returns Result.Success(fake)` handles `suspend` functions correctly; `coVerify { repo.save(any()) }` verifies suspending interactions; `slot<Type>()` captures arguments for assertion. **Turbine** is the canonical library for testing Kotlin Flow emissions:

```kotlin
@Test fun `emits loading then content`() = runTest {
    viewModel.uiState.test {
        assertEquals(AccountUiState.Loading, awaitItem())
        viewModel.load()
        assertEquals(AccountUiState.Content(fakeAccount), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

`MainDispatcherRule` replaces `Dispatchers.Main` with a `TestCoroutineDispatcher` in unit tests, eliminating the "Main dispatcher not initialised" error.

**Swift Testing framework** (Xcode 16) is the new iOS standard. `@Test` macro replaces XCTest's class hierarchy; `#expect` and `#require` replace `XCTAssert*`; `@Suite` groups related tests; parameterised tests use the `@Test(arguments:)` form; tests run in parallel by default. XCTest remains supported for codebases already invested.

**Pact contract tests**. The mobile app publishes the contracts it expects from each API endpoint as a Pact file; the broker stores published contracts; the backend's CI runs Pact verification against its actual behaviour before any deploy. Breaking changes surface before deployment, not after. The pattern eliminates the most common mobile-API incident: the backend team changed something the mobile team did not expect.

---

## Snapshot Testing

**Paparazzi** for Android. Renders Compose UI on the JVM using LayoutLib — the same rendering engine Android Studio's Compose Preview uses. No emulator. Under one second per component. The test compares the rendered PNG against a golden image committed to the repository; any pixel difference fails the test. `RecordPaparazziTest` mode updates the goldens; the team commits golden updates explicitly in their own PR for review:

```kotlin
class PrimaryButtonSnapshotTest {
    @get:Rule val paparazzi = Paparazzi(deviceConfig = PIXEL_5, theme = "AscendionTheme")
    @Test fun primaryButton_default() {
        paparazzi.snapshot { AscendionTheme { PrimaryButton(label = "Continue") {} } }
    }
}
```

**iOSSnapshotTestCase** (Facebook's library, now community-maintained) and the more modern **swift-snapshot-testing** by Point-Free are the iOS equivalents. Both render UIKit or SwiftUI to a `UIImage`, store as PNG, and use a perceptual diff algorithm tolerating subpixel antialiasing differences.

**Update goldens deliberately**: intentional design changes only, in their own commit, with team-lead approval. The discipline is what makes snapshot tests catch regressions instead of becoming a routine `--update` flag.

**Testing matrix** for every component: all theme variants (light, dark, high contrast), at least three Dynamic Type sizes (`xSmall`, `medium`, `accessibility3`), at least two locales with significantly different text length (English, Arabic for RTL, German for long compound words).

---

## Performance Engineering

**Cold start budget**: under 2 seconds on a median three-year-old mid-range device (Pixel 6a, iPhone 11). **Warm start** (process resident, Activity not): under 200 ms. **Hot start** (Activity in memory): under 100 ms. Measured by `adb shell am start -W` on Android and Instruments Time Profiler on iOS, automated nightly on Firebase Test Lab device matrix.

**Baseline Profiles** generate a 30 percent cold-start improvement on the Now in Android reference app, 22 percent on Reddit, 25 percent on Lyft — verified by Google. The Profile is a text file listing class and method names that ART compiles ahead-of-time at install. `BaselineProfileGenerator` runs through Jetpack Macrobenchmark with `CompilationMode.Full`, executes a recorded critical-path script, and emits the profile committed to the repository and packaged in the App Bundle.

**Frame budget**. 60fps means 16.67ms per frame; 90fps means 11.11ms; 120fps (ProMotion iPad, iPhone 13 Pro and later, Pixel 8 Pro) means 8.33ms. **Jank** is a frame that exceeds budget by more than itself (a 33ms frame at 60fps target). Jetpack Macrobenchmark's `FrameTimingMetric` produces P50, P95, P99 frame-time histograms.

**StrictMode** in debug builds throws an exception on any main-thread disk or network access:

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads().detectDiskWrites().detectNetwork()
            .penaltyDeath().build()
    )
}
```

The single most effective catch-early tool for the entire class of "the app feels slow" bugs.

**Compose recomposition optimisation**. `remember(key) { expensiveCalculation }` caches across recompositions. `derivedStateOf { ... }` computes a derived value that only triggers downstream recomposition when the derived value changes. `key(item.id)` in `LazyColumn` items lets Compose match items across data changes and skip recomposing unchanged items. Compose Compiler's stability inference logs in CI (the `composeCompilerReports` task) reveal which composables Compose treats as "unstable" — usually due to a non-stable parameter type — and forces unnecessary recomposition.

**iOS performance instruments**. **Core Animation** instrument: red overlay marks offscreen rendering (a GPU copy that the developer can usually eliminate by avoiding rounded-corner masks on opaque layers); green marks blended layers (alpha compositing cost — set `isOpaque = true` where opacity isn't required). **Time Profiler** is the function-level CPU sampler. **Allocations** tracks heap growth and the retain cycle that causes a memory leak. **Memory Graph Debugger** in Xcode visualises retain cycles as graph loops and identifies leaked objects by type.

**Battery**. **WorkManager** on Android for guaranteed background work that must survive process death — never `Service` with `START_STICKY` as a battery-eating workaround. iOS **significant-change location** API rather than continuous GPS polling. Coalesce network requests so the radio wakes once not five times. **Doze mode** compatibility on Android — the developer accepts that the OS decides when background work runs.

---

## Accessibility

**Legal landscape**. The 2019 *Robles v. Domino's Pizza* US Supreme Court decision established that mobile apps providing access to public-accommodation services are subject to ADA Title III; lawsuits target inaccessible apps with settlements ranging from $50,000 to seven figures. The **EU European Accessibility Act** has been mandatory for public-sector apps since 2018 and for in-scope private-sector consumer apps (banking, e-commerce, transport, telecoms) since June 2025. **Philippines RA 10524** mandates accessibility for government digital services. **AODA** (Ontario), **Section 508** (US federal), and the **UK Equality Act 2010** complete the regulatory ring.

**WCAG 2.2 Level AA** is the practical compliance target — four principles, **P**erceivable, **O**perable, **U**nderstandable, **R**obust. Level A is too weak; Level AAA is too costly to achieve uniformly.

**TalkBack on Android**. `contentDescription` on every interactive element describes function not appearance ("Add to cart" not "Green button"). `importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_NO` hides decorative elements (icons inside a labelled button). `accessibilityLiveRegion` announces dynamic content updates (a toast appearing, a count incrementing). Custom `AccessibilityAction`s replace gesture-only interactions (swipe-to-delete becomes "Delete" action announced by TalkBack). `accessibilityTraversalBefore` / `After` adjusts the focus order when the visual layout does not match intended reading order.

**VoiceOver on iOS**. `accessibilityLabel` is the spoken name; `accessibilityHint` is the spoken action description; `accessibilityTraits` describes the kind (`.button`, `.header`, `.selected`, `.adjustable`). `UIAccessibility.post(notification: .screenChanged, argument: ...)` notifies VoiceOver of a major content update. SF Symbols carry accessible names automatically.

**Dynamic Type** on iOS: every text styled with semantic font tokens (`Font.body`, `Font.title`, `Font.headline` — never `Font.system(size: 16)`). Test at all twelve size categories, especially `accessibility1` through `accessibility5`. No text truncation at any size. **Scalable `sp` units** on Android serve the same purpose — text scales with the user's system font preference.

**Touch targets**. 48×48 dp minimum on Android (Material 3 guideline); 44×44 pt minimum on iOS (HIG guideline). Visible icon may be smaller; touch surface matches the minimum via `Modifier.size(48.dp)` or `.frame(minWidth: 44, minHeight: 44)`.

**Colour contrast**. WCAG 2.2 AA: 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt+ bold), 3:1 for UI components and graphical objects. Colour Contrast Analyser (free, Android and iOS) audits per token. **Never colour as the sole conveyor of information** — every red error pairs with an icon and label; every green success pairs with a checkmark.

**Switch Access** (Android) and **Switch Control** (iOS): every interactive element reachable via single-switch sequential focus or two-switch direct selection. Hidden gestures (long-press menus, swipe shortcuts) must have keyboard or switch equivalents.

**Testing tools**. **Accessibility Scanner** (Google, Android) automated checks; **Accessibility Inspector** in Xcode for iOS audit. Both miss experiential issues — bad reading order, confusing announcements, focus traps. **Manual testing with TalkBack and VoiceOver enabled and the screen off** is the single highest-leverage accessibility test and the one most teams skip.

---

## Anti-Patterns

### 1. The Inverted Pyramid

30 Espresso tests, 50 unit tests, 0 snapshot tests, CI takes 45 minutes. Developers stop running tests locally.

**CORRECT:** The fix is rebuilding the pyramid from the base.

### 2. Flaky UI Tests That Get Disabled

A UI test fails 1 in 20 runs. The team disables it "until we fix it." The disabled test rots; the regression it would have caught ships.

**CORRECT:** The fix is the no-disable rule: a flaky test is fixed (proper IdlingResource / accessibility-identifier waits) or deleted (it wasn't pulling its weight).

### 3. Snapshot Tests Updated Without Review

A small UI change updates 200 goldens; the engineer runs `--update-snapshots` and merges. A regression slips through unreviewed.

**CORRECT:** The fix is the code-review discipline of reviewing every golden update plus a CI gate that surfaces the count of golden changes per PR.

### 4. Cold Start Optimisation Without Measurement

The team adds five "optimisations" to cold start and ships. Nobody measured before; nobody measures after; the cold start is the same or worse.

**CORRECT:** The fix is Macrobenchmark in CI and the per-PR cold-start gate.

### 5. Accessibility as a Pre-Launch Audit

The team treats accessibility as a checklist run two weeks before App Store submission. Hundreds of findings; nothing ships on time.

**CORRECT:** The fix is accessibility designed in from day one — semantics in every design-system component, Dynamic Type in every screen, audit at PR not at release.

---

## References

1. [Now in Android — Testing strategy](https://github.com/android/nowinandroid) — *github.com*
2. [Turbine — Testing Kotlin Flow](https://github.com/cashapp/turbine) — *github.com*
3. [Paparazzi — Android Snapshot Testing](https://github.com/cashapp/paparazzi) — *github.com*
4. [Swift Testing](https://developer.apple.com/xcode/swift-testing/) — *developer.apple.com*
5. [Pact Contract Testing](https://docs.pact.io/) — *docs.pact.io*
6. [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — *developer.android.com*
7. [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/) — *w3.org*
8. [Robles v. Domino's Pizza](https://cdn.ca9.uscourts.gov/datastore/opinions/2019/01/15/17-55504.pdf) — *uscourts.gov*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/quality/` | Aligned to IEEE 829 · WCAG 2.2 AA · Google Android Vitals · Apple MetricKit · ISTQB*
