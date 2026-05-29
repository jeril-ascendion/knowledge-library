# Testing Strategy

> **Section:** `technology/mobile/testing-strategy/`
> **Alignment:** Testing Pyramid (Fowler) | Android Testing Guide | XCTest Framework | ISTQB Mobile Testing
> **Audience:** QA Architects · Mobile Engineers · Test Engineers · Engineering Leads

The mobile testing strategy defines what is tested, at which layer, with which tools, and to which coverage threshold. A testing strategy that is too thin produces regressions in production. A testing strategy that is too heavy produces slow, brittle tests that engineers work around rather than with. The testing pyramid provides the economic framework: fast, cheap, deterministic tests at the base; slow, expensive, environment-dependent tests at the apex.

## Overview

Mobile testing has five layers in the pyramid. The base (unit tests) contains the most tests, runs the fastest, and provides the most actionable feedback. The apex (E2E tests on physical devices) contains the fewest tests, runs the slowest, and is reserved for smoke testing of critical production paths. Investment follows the pyramid: most engineering effort in unit tests, least in E2E.

## Testing Pyramid Layers

### Layer 1: Unit Tests (Foundation)
Tests Use Cases and ViewModels without any device, emulator, simulator, network, or database. Android: JUnit5 + Mockk (for mocking Kotlin interfaces) + Turbine (for testing Kotlin Flow/StateFlow emissions). iOS: XCTest + Swift Testing framework (Xcode 16) + mock protocols generated manually or with Mockingbird. Turbine's `collectLatest {}` test block allows asserting exact emission sequences from StateFlow. Coverage gates: Use Cases ≥ 90%, ViewModels ≥ 80%.

### Layer 2: Snapshot Tests
Capture pixel-level screenshots of UI components and diff against committed golden images. Android: Paparazzi library renders Compose UI on the JVM using LayoutLib (same engine as Android Studio Preview) — no emulator required. iOS: iOSSnapshotTestCase renders SwiftUI or UIKit views to UIImage and diffs with stored PNG files. Test matrix: all theme variants (light, dark, high contrast), all supported Dynamic Type sizes (minimum: xSmall, medium, AX3), all localisation variants with different text lengths. Golden images committed to the repository — PRs that change visual appearance fail CI until goldens are intentionally updated.

### Layer 3: Integration Tests
Test the Repository layer with its dependencies: in-memory Room database for Android, URLProtocol stubbing for network calls (iOS), in-memory SQLite for Core Data/SwiftData. Verify that data flows correctly from data source through mapping to domain model. These tests catch DTO-to-domain mapping bugs that unit tests (which mock the Repository) miss.

### Layer 4: UI Tests
Full application on an emulator (Android) or simulator (iOS). Scope to the top 10 critical user journeys only — not every screen. Tools: Espresso (Android) with IdlingResource for async synchronisation; XCUITest (iOS) with accessibility identifier-based element location; Maestro (cross-platform, YAML-based) as an alternative that is more maintainable than programmatic Espresso. Maestro's declarative YAML syntax is readable by QA engineers without Kotlin/Swift knowledge.

### Layer 5: E2E Tests (Apex)
Physical device matrix via Firebase Test Lab. 10-20 devices covering top Android OEM/version combinations. iOS: 5 physical device types. Scope: the 5 most critical user journeys (authentication, primary use case, payment if applicable, error recovery, push notification handling). Run on each release candidate, not on every PR.

### Contract Tests (Cross-cutting)
Consumer-driven contract tests with Pact framework. The mobile application defines the API contract it depends on as a Pact file. CI verifies the BFF satisfies the contract before any backend deployment. Prevents backend changes from breaking the mobile app. Runs in the backend CI pipeline, not the mobile CI pipeline.

## Anti-Patterns to Avoid

> **⚠ Testing Only Through the UI** — All tests use Espresso or XCUITest to drive the full application. Tests are slow (2-5 minutes each), brittle (fail on visual changes unrelated to the tested logic), and provide poor diagnostic information when they fail.
> **CORRECT:** Test business logic through unit tests (milliseconds each, thousands of them). Test visual components through snapshot tests (seconds each). Reserve UI tests for the small set of critical user journeys that require the full stack.

> **⚠ Coverage Theatre** — 80% code coverage achieved by testing getters, setters, and constructor wiring. No tests for actual business logic.
> **CORRECT:** Coverage targets applied specifically to Use Cases and ViewModels — the layers that contain business logic. A 90% Use Case coverage target means 90% of the lines in Use Case classes are executed by tests. Coverage tooling configured to exclude auto-generated code, data classes without logic, and DI configuration.

## References

1. Fowler, Martin — The Practical Test Pyramid. martinfowler.com/articles/practical-test-pyramid.html
2. Google — Android Testing Guide. developer.android.com/training/testing
3. Paparazzi — Android Snapshot Testing. github.com/cashapp/paparazzi
4. Pact Foundation — Consumer-Driven Contracts. docs.pact.io
5. Maestro — Mobile UI Testing. maestro.mobile.dev
