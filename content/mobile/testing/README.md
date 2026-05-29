# Mobile Testing

The mobile testing pyramid — unit at the base, snapshot, integration, UI, and E2E at the apex — implemented with JUnit5 plus Turbine on Android, XCTest plus Swift Testing on iOS, Paparazzi and iOSSnapshotTestCase for screenshots, Maestro for cross-platform UI, and Firebase Test Lab for the device matrix.

**Section:** `mobile/` | **Subsection:** `testing/`
**Alignment:** Google Testing Pyramid | Apple WWDC Testing | ISO/IEC 25010 Reliability | Consumer-Driven Contracts
**Audience:** Mobile Engineers · QA Engineers · Test Architects

---

## Overview

The mobile testing strategy that holds up at scale has been stable for half a decade and is widely misimplemented in practice. The pyramid base is unit tests: pure JVM tests on Android (no emulator), pure XCTest tests on iOS (no simulator), running in milliseconds per test, covering ViewModels and Use Cases by the thousand. The next layer is snapshot tests: render a component, screenshot it, diff against a golden image, fail on regression. Then integration tests: repository plus database plus API mock together, verifying the contract between layers. Then UI tests: run on a device or emulator, exercise user journeys end to end, slow but high-fidelity. Then E2E smoke tests on physical devices for the critical paths only.

Programmes that misimplement the pyramid usually invert it — too many UI tests, too few unit tests, slow CI, flaky pipelines, the team disabling failing tests because the noise is unbearable. Programmes that implement it correctly have ten thousand unit tests, a thousand snapshot tests, a hundred integration tests, fifty UI tests, and five E2E tests. The number ratios are not exact but the shape is.

The architectural shift is not "we have tests." It is: **the mobile testing strategy is a pyramid with explicit ratios per layer, JVM-based unit and snapshot tests as the high-volume base, contract tests between mobile and API, Firebase Test Lab for the device matrix, and a CI pipeline that completes the full suite in under 30 minutes — because a slow pipeline is one that engineers learn to ignore.**

---

## Core Principles

### 1. The pyramid shape is non-negotiable

Many fast unit tests at the base, few slow E2E tests at the apex. Inverted pyramids (many UI tests, few unit tests) produce slow, flaky CI that teams learn to circumvent. The shape is the strategy.

### 2. Tests run on the JVM where possible

Robolectric, Paparazzi, and JVM-based unit tests run in seconds without emulator startup. Reserve the emulator for tests that genuinely need the Android runtime. Every emulator-required test is a deliberate, justified choice.

### 3. Snapshot tests catch the UI regressions unit tests cannot

A ViewModel test cannot detect that a button has migrated 8 dp off-screen. A snapshot test can. The cost is committing golden images and reviewing them deliberately on change; the benefit is catching every visual regression at PR time.

### 4. Contract tests guard the mobile-API boundary

The mobile app's API expectation is captured as a contract; the backend is verified against the contract before deployment. Pact framework or OpenAPI-driven contract testing prevents the most-common breakage: "the API team changed something the mobile team did not expect."

### 5. Test data is realistic and bounded

Fixtures use realistic field names, realistic payload sizes, realistic edge cases. Random fakers produce flaky tests when the random data happens to hit a parser bug. Deterministic, intentional fixtures hold up.

### 6. CI feedback in under 30 minutes for the full suite

A 90-minute CI run is a CI run engineers do not wait for; they merge and move on. Sub-30-minute pipelines preserve the test-driven feedback loop. Parallelisation, test shard splitting, and aggressive use of JVM tests over emulator tests are the levers.

---

## Architecture Deep-Dive

**Android Unit Tests with JUnit5 and MockK**

JUnit5 is the current test framework standard. MockK is the Kotlin-native mocking library; it handles `suspend` functions, coroutines, and final classes (Kotlin's default) without configuration. Turbine is the canonical library for testing Kotlin Flow emissions:

```kotlin
class AccountViewModelTest {
    private val getAccount = mockk<GetAccountUseCase>()
    private val vm = AccountViewModel(getAccount)

    @Test
    fun `emits loading then content`() = runTest {
        coEvery { getAccount() } returns flowOf(Result.Success(fakeAccount))
        vm.uiState.test {
            assertEquals(AccountUiState.Loading, awaitItem())
            assertEquals(AccountUiState.Content(fakeAccount), awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

`runTest` uses the test coroutine dispatcher; Turbine's `test` block expects emissions in order; failures are diagnosed at the specific awaited item.

**iOS Unit Tests with XCTest and Swift Testing**

Swift Testing (introduced in Xcode 16) is the new framework — `@Test` macro replaces XCTest's class-based pattern; expectations use `#expect` and `#require`; parameterised tests are first-class. XCTest remains supported and is the right answer for codebases already invested in it.

```swift
@Test func emitsLoadingThenContent() async throws {
    let mockUseCase = MockGetAccountUseCase()
    mockUseCase.result = .success(fakeAccount)
    let vm = AccountViewModel(getAccount: mockUseCase)

    #expect(vm.state == .loading)
    await vm.load()
    #expect(vm.state == .content(fakeAccount))
}
```

**Snapshot Tests — Paparazzi and iOSSnapshotTestCase**

Paparazzi renders Compose UI on the JVM (no emulator), produces a PNG, diffs against a golden image, fails on regression. Tests run in milliseconds; the entire snapshot suite finishes in under a minute for hundreds of components.

```kotlin
class PrimaryButtonSnapshotTest {
    @get:Rule val paparazzi = Paparazzi(deviceConfig = PIXEL_5, theme = "AscendionTheme")

    @Test fun primaryButton_default() {
        paparazzi.snapshot { AscendionTheme { PrimaryButton(label = "Continue", onClick = {}) } }
    }

    @Test fun primaryButton_disabled() {
        paparazzi.snapshot { AscendionTheme { PrimaryButton(label = "Continue", onClick = {}, enabled = false) } }
    }
}
```

iOSSnapshotTestCase (originally from Facebook, now community-maintained as `swift-snapshot-testing` from Point-Free) does the equivalent on iOS, rendering SwiftUI views to images and diffing.

**Robolectric for Integration**

Repository + Room + API mock integration tests run on the JVM with Robolectric providing the Android stub. Faster than emulator; sufficient for tests that exercise Room queries and Repository orchestration without needing real device behaviour.

**Espresso and XCUITest for UI**

Espresso uses IdlingResource to wait for async work. The pattern integrates with Compose through `androidx.compose.ui.test.junit4.createComposeRule()`. XCUITest uses accessibility identifiers to find elements; the discipline of setting `accessibilityIdentifier` on every interactable element is non-optional for stable iOS UI tests.

**Maestro for Cross-Platform UI**

Maestro is YAML-defined UI tests that run against both Android and iOS:

```yaml
appId: com.ascendion.app
---
- launchApp
- tapOn: "Sign in"
- inputText: "user@example.com"
- tapOn: "Continue"
- assertVisible: "Enter password"
```

Maestro is the simplest cross-platform UI testing tool currently available; the trade-off is shallower native-feature coverage than Espresso / XCUITest.

**Consumer-Driven Contract Tests with Pact**

The mobile app publishes a contract describing the API responses it expects. Pact's broker stores contracts; the backend's CI verifies the backend's actual behaviour against the published contracts before deployment. Breaking changes surface before deployment, not after.

**Firebase Test Lab**

Physical device cloud — Pixel, Galaxy, Xiaomi, OnePlus, on Android 10 through Android 15 — running the app's instrumented tests. Configured as a CI matrix:

```yaml
devices:
  - pixel6a, api28
  - pixel6a, api33
  - samsungs22, api34
  - xiaomi13, api35
```

The cost is real ($1 per device hour); the value is catching device-specific issues that the team's local emulator misses.

---

## Implementation Guide

### Step 1: Establish the pyramid ratios

Document the target test counts per layer: thousands of unit, hundreds of snapshot, tens of integration, tens of UI, a handful of E2E. Track the actuals quarterly.

### Step 2: Wire JVM-based unit tests with Turbine and MockK

JUnit5 + Turbine + MockK as the standard on Android. Swift Testing + custom mocks as the standard on iOS. Tests run in seconds.

### Step 3: Add Paparazzi and snapshot tests for every design-system component

Each component variant captured as a snapshot. Golden images committed; updates require explicit `--update-snapshots` flag.

### Step 4: Wire integration tests with Robolectric and SwiftUI Preview

Robolectric on Android; SwiftUI Preview testing on iOS for hosted view inspection.

### Step 5: Adopt Maestro for the cross-platform critical paths

5-10 Maestro flows covering the highest-business-value user journeys. Run on every release in CI.

### Step 6: Configure Firebase Test Lab matrix

5-10 device-and-OS combinations covering the 80 percent of installed-base configurations. Nightly run; release gating.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Test pyramid ratios documented | Test Architect | Target counts per layer; actuals tracked quarterly | Required |
| Unit test coverage threshold | Test Architect | Minimum 70 percent line coverage on ViewModel / UseCase / Repository layers | Required |
| Snapshot tests per design-system component | Mobile Engineering Lead | Every component variant covered; goldens reviewed on update | Required |
| Pact contracts with backend | Mobile + API Architects | Critical endpoints under contract; backend CI verifies against contracts | Required |
| Maestro flows for top-5 user journeys | QA Lead | Flows green on every release in CI | Required |
| Firebase Test Lab matrix run | Build Engineering | Nightly run; release gated on green status | Required |

---

## Security Considerations

- Test fixtures must not contain real PII, real API keys, or real tokens. Detect and remove via secret-scanning hooks on the fixtures directory.
- Snapshot golden images can leak UI containing sensitive data if produced from production fixtures; verify golden generation uses synthetic data only.
- UI tests on Firebase Test Lab run on cloud devices; do not test against production API endpoints, and ensure the test build does not contain release credentials.
- Pact contracts are part of the contract documentation; treat them as API-spec artefacts and protect with the same access controls.

---

## Performance Considerations

- Full test suite under 30 minutes; sub-15-minute pipelines if achievable. Long pipelines are pipelines engineers ignore.
- Unit test runs under 5 minutes for the full Android module graph using `kotest`'s parallel runner or JUnit5's `@Execution(CONCURRENT)`.
- Paparazzi runs in under 1 minute for hundreds of snapshots — JVM rendering, no emulator boot.
- Firebase Test Lab cost: budget $200-500 per month for a typical matrix at typical release cadence; emerging-market device coverage justifies higher spend.
- Maestro flows: target each flow under 30 seconds; flows over 2 minutes are signals of test scope creep.

---

## Anti-Patterns to Avoid

### ⚠️ The Inverted Pyramid

The team has 30 Espresso tests, 50 unit tests, and 0 snapshot tests. CI takes 45 minutes. Developers stop running tests locally. The fix is rebuilding the pyramid from the base — adding unit tests for every ViewModel, snapshot tests for every component — until the ratios are correct.

### ⚠️ Flaky UI Tests That Get Disabled

A UI test fails 1 in 20 runs due to timing. The team disables it "until we fix the flake." The disabled test rots; the regression it would have caught ships. The fix is the no-disable rule: a flaky test is either fixed (preferable: proper IdlingResource or accessibility-identifier waits) or deleted (acceptable: the test was not pulling its weight). Never disabled-but-still-checked-in.

### ⚠️ Mocks That Become the Contract

The team mocks the API in unit tests using fake responses. The fakes drift from the real API. The unit tests pass; integration breaks. The fix is the contract test (Pact, OpenAPI verification) that keeps mocks and real API in sync.

### ⚠️ Random Data Producing Random Failures

`faker.email()` produces a string that happens to fail the email validator's regex once in a thousand runs. The team chases the ghost for weeks. The fix is the deterministic fixture: real-looking but specific values; randomness only where genuinely required and only with a seed.

### ⚠️ Snapshot Tests with Wholesale Updates

A small UI change updates 200 goldens; the engineer runs `--update-snapshots` and merges without reviewing the diffs. A regression slips through unreviewed. The fix is the code-review discipline of reviewing every golden update, and the CI gate that surfaces the count of golden changes per PR.

---

## AI Augmentation Extensions

### AI-Assisted Test Generation

LLM coding assistants generate unit tests for ViewModels and Use Cases from the source code, covering happy path and edge cases. The engineer reviews and accepts; the typing is compressed; the architectural judgement on coverage remains human.

### AI-Assisted Snapshot Diff Triage

Snapshot diffs are surfaced to an LLM that classifies them as "expected change," "regression," or "needs human review." The reviewer's attention is drawn to the suspicious diffs; the obvious ones are auto-approved.

---

## References

1. [Google Testing on the Toilet](https://testing.googleblog.com/) — *testing.googleblog.com*
2. [Turbine — Testing Kotlin Flow](https://github.com/cashapp/turbine) — *github.com/cashapp*
3. [Paparazzi — Android Snapshot Testing](https://github.com/cashapp/paparazzi) — *github.com/cashapp*
4. [swift-snapshot-testing by Point-Free](https://github.com/pointfreeco/swift-snapshot-testing) — *github.com*
5. [Maestro — Mobile UI Testing](https://maestro.mobile.dev/) — *maestro.mobile.dev*
6. [Pact — Consumer-Driven Contract Testing](https://docs.pact.io/) — *docs.pact.io*
7. [Firebase Test Lab](https://firebase.google.com/docs/test-lab) — *firebase.google.com*
8. [Swift Testing](https://developer.apple.com/xcode/swift-testing/) — *developer.apple.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/testing/` | Aligned to Google Testing Pyramid · Apple WWDC Testing · Pact*
