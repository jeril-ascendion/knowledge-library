# Technology Decisions — Native vs Cross-Platform

> **Section:** `technology/mobile/technology-decisions/`
> **Alignment:** TOGAF Technology Architecture | IEEE 1471 | Gartner Mobile Platform Guide | Google MAD | Flutter Architecture
> **Audience:** Solutions Architects · CTOs · Mobile Engineering Leads · Client Technology Decision-Makers

The native versus cross-platform decision is the highest-stakes technology choice in mobile engineering. It determines team structure, hiring pool, long-term cost, performance ceiling, and the feasibility of certain feature categories. It is also frequently made on insufficient information — based on team familiarity, vendor marketing, or replication of a prior project's choice rather than structured evaluation against client-specific quality attributes.

## Overview

There is no universally correct answer. The correct answer is the option that best satisfies the weighted quality attributes of the specific project, team, and client context. This section provides the evaluation framework, the honest capability assessment of each option, and the decision rules that govern Ascendion's recommendations.

## Platform Options

### Pure Native — Kotlin (Android) + Swift (iOS)
Two separate codebases. Each platform uses its canonical language, framework, and tooling. Maximum performance, maximum platform API access, maximum platform-native user experience. Highest cost — two engineering teams, two CI pipelines, two release tracks, duplicated business logic unless Kotlin Multiplatform is adopted for the domain layer.

Mandatory when: frame rate SLA below 16ms, deep device API access required (custom camera pipeline, BLE peripherals, NFC writing, SecureEnclave-bound cryptographic operations), or when regulatory requirements mandate platform-specific attestation capabilities not available through cross-platform bridges.

Real-world validation: Uber's ride-matching engine uses a shared C++ core with native Android (Kotlin) and iOS (Swift) UI layers. The rationale is explicit: real-time location processing at millisecond precision cannot tolerate the overhead of a cross-platform rendering layer.

### Flutter — Dart, Impeller Rendering
Single Dart codebase compiled to native ARM for iOS and Android. Impeller rendering engine provides predictable 60/120fps with hardware-accelerated frame preparation. Does not use platform UI widgets — draws all UI through its own rendering pipeline, producing pixel-perfect visual consistency across platforms.

Performance ceiling: 95% of native for most application categories. The remaining 5% gap appears in extreme GPU workloads, deep platform API integration, and startup time (Flutter's Dart VM initialisation adds ~200ms to cold start that native avoids).

Preferred default for: new cross-platform applications where frame rate SLA is above 16ms, device API requirements are met by the Flutter plugin ecosystem, and the team can absorb a 3-6 week Dart learning curve.

Production scale: Google Pay, BMW Connected, Nubank (37 million users), eBay Motors.

### React Native — JavaScript/TypeScript, New Architecture
JavaScript/TypeScript bridge to native platform components. Old Bridge architecture serialised every JS-to-native call as JSON — measurable performance ceiling on list scrolling and animations. New Architecture (JSI + Fabric) eliminates the Bridge, giving JavaScript direct C++ memory access and synchronous UI updates. Performance ceiling rises to 85-90% of native on New Architecture.

Uses actual platform UI widgets — platform-native look and feel is automatic. JavaScript/TypeScript skills are widely available, reducing hiring friction and onboarding cost.

Permitted when: existing JS/TS mobile capability in the team, Expo-based development workflow reduces ops overhead, and performance requirements are met by New Architecture. Requires explicit New Architecture migration plan and dependency compatibility audit.

Production scale: Meta (Facebook, Instagram), Microsoft Office Mobile, Shopify, Discord.

### MAUI — C#/.NET
C# codebase targeting native platform controls on iOS, Android, Windows, and macOS. Right choice only when the delivery team has existing .NET investment and mobile is an extension of that investment. Not recommended for greenfield mobile teams where Dart or TypeScript skills are more available.

### Kotlin Multiplatform — Shared Logic, Native UI
Shares Kotlin business logic (Use Cases, Repositories, domain models) compiled to native JVM bytecode (Android) and native binary via Kotlin/Native (iOS). UI layer remains native — Compose (Android) and SwiftUI (iOS). Compose Multiplatform extends Compose UI to iOS and Desktop.

Best choice for: teams with strong Kotlin expertise that want platform-native UI fidelity without duplicating domain logic. CashApp's open-source architecture demonstrates KMP sharing financial calculation logic and API clients across Android and iOS.

## Decision Framework

Evaluate each project across eight dimensions with weights:

Performance SLA (22%) · Device API Depth (18%) · Development Speed (16%) · 5-Year TCO (15%) · Team Skills (12%) · Maintainability (9%) · Security Attestation (5%) · Regulatory Compliance (3%)

Run the decision framework as a formal exercise in the project discovery phase. Document the scores and present to the ARB before platform commitment.

## Anti-Patterns to Avoid

> **⚠ Choosing Platform by Team Familiarity Alone** — Selecting React Native because "our team knows JavaScript" without evaluating performance requirements or device API needs.
> **CORRECT:** Team familiarity scores in the Team Skills dimension (12% weight) — not as the sole decision criterion. A team can learn Dart in 3-6 weeks; recovering from a wrong platform choice costs months.

> **⚠ Starting Cross-Platform, Switching to Native Mid-Project** — Airbnb's 2018 experience: committed to React Native for two years, discovered limitations in brownfield integration and debugging depth, rewrote in native. The switch cost was significantly higher than choosing native initially.
> **CORRECT:** Run a two-day technical spike on the highest-risk screen before platform commitment. If the spike surfaces blockers, evaluate platform change before sunk cost accumulates.

## References

1. Airbnb Engineering — Sunsetting React Native. medium.com/airbnb-engineering, 2018.
2. Flutter — Architecture Overview. docs.flutter.dev/app-architecture
3. JetBrains — Kotlin Multiplatform. kotlinlang.org/docs/multiplatform.html
4. Nubank Engineering — Flutter at Scale. building.nubank.com.br
5. Meta — React Native New Architecture. reactnative.dev/docs/new-architecture-intro
