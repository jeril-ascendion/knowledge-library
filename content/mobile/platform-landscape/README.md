# Mobile Platform Landscape

The deliberate, weighted decision between pure-native Android, pure-native iOS, and the four serious cross-platform contenders — made early, defended in writing, and revisited when its assumptions shift.

**Section:** `mobile/` | **Subsection:** `platform-landscape/`
**Alignment:** TOGAF ADM | Gartner Mobile App Strategy | ISO/IEC 25010 | OWASP MASVS
**Audience:** Mobile Engineers · Solutions Architects · Technical Leads

---

## Overview

The mobile platform choice is the most expensive decision a mobile programme makes, and it is almost always made implicitly — by the loudest engineer in the room, by the framework the agency happens to know, by the last conference talk the CTO attended. The cost of that informality is visible five years later: in the Flutter app whose team is rewriting in native Swift because they hit a platform integration the framework cannot cover, in the React Native codebase whose hot reload broke when the new architecture migration stalled, in the dual-native teams that ship one platform six months behind the other because the iOS team is half the size and three times the cost.

Android holds approximately 72 percent global smartphone market share by Statcounter's 2025 numbers; iOS holds approximately 27 percent. Those headline figures hide what actually matters for enterprise mobile architecture: iOS dominates US enterprise (around 56 percent US market share), iOS dominates Philippines retail banking (BPI, BDO, Maya internal telemetry consistently show 60-plus percent of mobile-banking sessions on iOS despite Android's 75 percent device share — the iOS user base is wealthier and transacts more), iOS dominates Japan and Australia. Android dominates India, Brazil, Indonesia, sub-Saharan Africa, and the long tail of mid-market devices everywhere else. Targeting "mobile users" without targeting a specific geography and demographic is an architecture decision dressed up as a non-decision.

The architectural shift is not "we picked Flutter" or "we picked native." It is: **the platform choice is a weighted-criteria decision documented as an ADR, with specific scores against team skills, performance SLAs, device API access depth, time-to-market, five-year TCO, and platform-native UX requirements — re-litigated only when one of those inputs measurably changes.**

---

## Core Principles

### 1. Decide on weighted criteria, not framework enthusiasm

The decision criteria — team skills today, hiring market in your geography, performance SLA, depth of device-API access, time-to-market, five-year TCO, platform-native UX expectations — must be named, weighted, and scored before any framework is named. Frameworks enthusiastically chosen become frameworks defensively justified; weighted criteria force the conversation back to the user and the budget.

### 2. Geography determines platform mix

A US enterprise SaaS app where 70 percent of users are iOS can ship iOS-first for nine months and add Android later. A Philippines GCash-style consumer app where 75 percent of devices are Android cannot. The geography drives the sequencing; the sequencing drives the staffing model; the staffing model drives the framework choice. Decisions made without geographic data are decisions made against a fictional user.

### 3. Native is the default; cross-platform must earn its place

The default position in 2026 — for any app that will live more than three years, integrate with platform-specific hardware (camera, biometrics, AR, NFC, secure enclaves), or carry a platform-native UX expectation — is pure native Kotlin on Android and Swift on iOS. Cross-platform must earn the choice by clearing a documented bar: team is too small to staff two native lines, the UI is custom-rendered and platform conventions matter less, time-to-market is the overriding constraint. "We'll save 40 percent on engineering" is not a defence by itself.

### 4. Total cost of ownership is a five-year number

The framework whose first-year cost is lowest is rarely the framework whose five-year cost is lowest. Migration cost, dependency lock-in, hiring difficulty, framework-version churn (React Native's New Architecture migration, Flutter's null safety transition, MAUI's Xamarin sunset) all show up in years two through five. The TCO calculation must look at five years, not the first sprint.

### 5. Platform-native UX is a measurable user expectation

iOS users expect navigation bars at the bottom, swipe-back from the left edge, share sheets, system fonts, and the iOS keyboard contract. Android users expect Material 3 navigation rail or bottom bar, back gesture from either edge, system share intent, and Material's typography scale. Cross-platform frameworks that render their own widgets (Flutter) produce a consistent app across platforms but a non-native app on each — that trade-off is acceptable for some product categories (gaming, media, custom-canvas tools) and unacceptable for others (banking, productivity, government services where users compare against the platform's first-party apps).

### 6. The decision is an ADR; the inputs decay

Document the choice as an architecture decision record naming the criteria, the weights, the scores, the alternatives considered, the rejected options, and the inputs that — if they change — would re-open the decision. The inputs decay: market shares shift, framework architectures stabilise or fall apart, team composition changes. Schedule a review of the ADR every 18 months against the documented inputs.

---

## Architecture Deep-Dive

The five-year TCO comparison, normalised against pure native Android plus iOS at 100 percent baseline, looks roughly like this on enterprise programmes the practice has shipped:

- **Pure native (Kotlin + Swift)**: 100 percent baseline. Two teams, two codebases, two hiring pipelines. Highest engineering cost; lowest per-platform risk; highest UX fidelity.
- **Flutter**: 55 to 65 percent of native. One Dart codebase compiling to native ARM. The Skia (now Impeller) rendering engine paints every pixel — the app is pixel-identical across platforms but not natively rendered. Strong for custom-canvas UIs (Reflectly, Google Pay's redesign, Alibaba Xianyu). Weakness: every platform widget convention (iOS share sheets, Android Material You dynamic colour) is a workaround.
- **React Native**: 60 to 70 percent of native. JavaScript and TypeScript bridge to actual UIKit and Android Views. The old "Bridge" architecture (asynchronous JSON serialisation) is being replaced by the New Architecture: JSI (synchronous JS-to-native calls), Fabric (new UI rendering), TurboModules. The migration matters because Bridge-era apps cannot adopt features that require synchronous native calls. Meta uses it in Facebook, Instagram, and Marketplace — but those teams have native iOS and Android engineers fixing what JS cannot reach.
- **Kotlin Multiplatform (KMP)**: 70 to 80 percent of native for the shared layer. Share the business logic, networking, persistence, and ViewModel state machinery in Kotlin; keep SwiftUI on iOS and Jetpack Compose on Android. The most architecturally pure option for teams that can afford two native UI codebases. Used by Netflix, McDonald's, 9GAG, Cash App.
- **.NET MAUI**: 65 to 75 percent of native. C# and XAML targeting native controls (UIKit on iOS, Android Views). The right choice only when the team already has deep .NET muscle — otherwise the framework is fighting upstream against Xamarin's sunset legacy and a smaller community than the alternatives.

What top companies actually chose, with the evidence:

- **Uber**: Native iOS and Android UI, with a shared C++ ride-engine library compiled into both apps. The ride-matching algorithm, the trip-state machine, and the geospatial maths live in C++ — the UI is native because user trust requires native feel. Documented in their 2017 architecture talks and verified by the open-sourced ribs framework.
- **Airbnb**: Migrated to React Native in 2016, migrated away in 2018, documented the lessons publicly. The summary: cross-platform saved them code but cost them more in cross-team coordination than it saved, and the JS-native bridge surface became the single biggest source of production crashes. They are now pure native again.
- **Meta**: React Native everywhere it can be, but with first-party native engineers staffing the integration boundary. Meta owns the framework, so the framework's evolution roadmap matches Meta's needs. No other organisation has that leverage.
- **Google**: Flutter for Google Pay's redesign, Google Ads Mobile, Google Classroom on iOS, and many internal tools. Jetpack Compose for Android first-party products. Google does not eat its own Flutter dog food in its first-party Android apps — that signals the trade-off honestly.
- **Cash App (Block)**: Kotlin Multiplatform for business logic, SwiftUI and Compose for UI. Documented at KotlinConf and in their engineering blog as the architecture they wish they had started with.

The honest performance ceiling: Flutter achieves about 95 percent of native frame-budget performance because it owns rendering and avoids the bridge cost. React Native with the New Architecture achieves about 85 percent for typical UI work and within 95 percent for compute that lives in TurboModules. MAUI achieves about 88 percent because it uses native controls but pays the .NET runtime cost. KMP achieves 100 percent for the UI layer (it *is* native UI) and 100 percent for the shared layer (Kotlin compiles to JVM bytecode on Android and to LLVM native code on iOS).

App-size overhead is the cost the framework charge on every install: a Hello-World Flutter app is roughly 6-8 MB on Android and 14-18 MB on iOS after release-mode shrinking; React Native is 7-10 MB and 12-16 MB; MAUI is 14-20 MB and 18-25 MB; KMP shared logic adds 1-3 MB. On emerging-market devices where storage is precious and data plans price MB at scale, those numbers matter.

---

## Implementation Guide

### Step 1: Build the weighted decision criteria

Name the criteria — team skills today, hiring market in geography, three-year roadmap features, performance SLA, device API access depth, time-to-market, five-year TCO, platform-native UX expectations, accessibility compliance burden, and security/regulatory posture. Weight each on a 1-5 scale based on actual business context. The weights are the decision; the scoring follows.

### Step 2: Score each framework against the weighted criteria

Pure native Kotlin, pure native Swift, Flutter, React Native, Kotlin Multiplatform, and MAUI. Score each on a 1-5 scale per criterion. Multiply by weight, sum, compare. Show the spreadsheet in the ADR.

### Step 3: Validate with a two-week spike

The chosen framework gets a two-week throwaway spike implementing the three hardest screens in your roadmap: the one with custom hardware (camera or biometrics), the one with the heaviest animation, and the one with the deepest integration to an existing native SDK. The spike either confirms the choice or surfaces the rejection in two weeks rather than two years.

### Step 4: Document the ADR with rejection criteria

The ADR names what would re-open the decision: framework reaches end-of-life signal, market share in your geography shifts more than 10 points, team composition changes such that native skills become available, performance SLA fails on tier-2 devices. Without rejection criteria, the ADR is one-way and the next argument has no anchor.

### Step 5: Build the team to the framework, not the framework to the team

If the decision is Flutter, hire and train for Dart and Flutter widget development. If KMP, hire native engineers who can also operate in shared Kotlin. The wrong order — hiring a JavaScript-only team and then choosing React Native because that is what they know — produces frameworks chosen on hiring constraints rather than user needs.

### Step 6: Schedule the 18-month review

Calendar a review against the ADR's inputs every 18 months. Most reviews confirm the original choice; the value is in the reviews that don't.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Weighted criteria approved | Solution Architect | 8-12 criteria documented with explicit weights and business justification | Required |
| Geography and persona data validated | Product + Architect | App-store mix data, in-country device analytics, target persona income deciles documented | Required |
| Two-week framework spike completed | Mobile Engineering Lead | Three hardest screens prototyped; performance measurements captured | Required |
| Platform-choice ADR ratified | Architecture Review Board | ADR includes alternatives, scoring, rejection criteria, 18-month review date | Required |
| Five-year TCO model approved | Engineering Director | Cost model includes engineering, hiring, framework migration risk, training | Required |
| 18-month review scheduled | Solution Architect | Calendar entry created against ADR inputs with named reviewers | Required |

---

## Security Considerations

- Cross-platform frameworks expand the attack surface to the framework runtime itself — React Native's JavaScriptCore, Flutter's Dart VM, and the .NET runtime are all in-process attack surfaces in addition to the platform's. The supply-chain risk on framework-distributed binary releases is real (the 2022 ua-parser-js compromise touched many React Native apps). Pin framework versions; verify checksums against the publisher's release; run `npm audit` or its equivalent on every CI build.
- Cross-platform reduces the cost of code-level security work (one CodeQL scan covers iOS and Android) but increases the cost of native-platform security work (Android Keystore and iOS Keychain still need integrating per platform). The net is rarely a saving on enterprise apps.
- Platform-native APIs (Apple's Secure Enclave, Android's StrongBox, biometric attestation) are platform-specific by construction. Cross-platform plug-ins for these capabilities lag the platform by 6-18 months on average; for regulated workloads the gap is unacceptable.

---

## Performance Considerations

- Cold start under 2 seconds on a median 2023 mid-range device (Pixel 7a, iPhone 13). Cross-platform frameworks add 150-400 ms of cold-start overhead before any user code runs; Flutter's Impeller and React Native's Hermes have closed but not eliminated this.
- Frame budget at 60 fps is 16.67 ms; at 90 fps is 11.11 ms; at 120 fps is 8.33 ms. ProMotion iPad and Pixel 8 Pro hit 120 fps natively. Cross-platform frameworks regularly miss 120 fps on scrolling lists with heavy cells.
- App-size budget on emerging-market deployments: under 25 MB on Android (the Play Store warns above this), under 35 MB on iOS. Cross-platform baseline overhead can blow this budget before any feature code is added.
- Measurement tools: Android `adb shell am start` with `-W` for cold-start timing, Xcode Instruments time profiler for iOS, Flutter's `flutter analyze --performance`, React Native's Perf Monitor and Flipper.

---

## Anti-Patterns to Avoid

### ⚠️ The Framework-by-Vibes Decision

The team chooses a framework because someone read a Hacker News post or because the agency mentions Flutter on their landing page. No criteria are weighted, no TCO model is built, no two-week spike validates the choice. The decision is defended after the fact by selecting metrics that confirm it. The fix is the ADR with weighted criteria — and the discipline to follow the weighting even when the spreadsheet picks the option no one expected.

### ⚠️ The Cross-Platform Tax Surprise

The team adopts a cross-platform framework expecting 50 percent engineering savings and discovers in year two that platform-specific feature requests (Apple Watch app, Wear OS complications, Android Auto integration) require native engineers anyway. The blended team is now larger and more expensive than two pure-native teams would have been. The fix is honest scope analysis at decision time: list the platform-specific surfaces the roadmap will touch and price them into the TCO.

### ⚠️ The Pixel-Perfect Trap

The product team requests pixel-identical experiences across iOS and Android because "consistency matters." They get it from Flutter or a custom design system. iOS users perceive the app as foreign because the navigation, gestures, and typography do not match their platform expectations. App-Store reviews drop below 3.5 stars on iOS specifically. The fix is naming platform-native UX as a first-class criterion before the framework choice.

### ⚠️ The Hiring-Constraint Decision Disguised as a Strategy

The CTO chooses React Native because the existing web team can be redeployed. Six months later the team is fighting native-bridge bugs they have no skills to debug. The fix is honesty: name the hiring constraint as a constraint in the ADR, accept the trade-offs, and budget for native specialists on the integration boundary.

### ⚠️ Choosing for the Demo, Not the Decade

The framework chosen because it produces the fastest demo and the prettiest hot reload is rarely the framework that ages well. The seven-year-old Android app on Kotlin is still maintainable. The seven-year-old app on a deprecated cross-platform framework is a rewrite. The fix is the five-year TCO horizon — and a hard look at the framework's release cadence, breaking-change history, and sponsor stability.

---

## AI Augmentation Extensions

### AI-Assisted Platform Decision Modelling

LLM-based architecture assistants ingest the documented criteria, weights, and per-framework scoring rubric, then re-run the scoring as inputs change (new framework release, market-share shift, team composition change) and surface drift in the ADR. Tools: Cursor's project memory for documented criteria, Claude Code as a long-context reasoning partner for re-scoring sessions, GitHub Copilot for spike scaffolding once the choice is made.

### AI-Assisted Framework Spike Generation

When the two-week spike is approved, AI coding assistants generate boilerplate for each candidate framework's "three hardest screens" in parallel — the same scenes implemented in Flutter, React Native, and KMP — accelerating the validation phase from two weeks to roughly five days for the boilerplate phase. The engineering judgement on the result is unchanged; the typing has been compressed.

---

## References

1. [Statcounter Global Mobile OS Market Share](https://gs.statcounter.com/os-market-share/mobile/worldwide) — *gs.statcounter.com*
2. [Airbnb — Sunsetting React Native](https://medium.com/airbnb-engineering/sunsetting-react-native-1868ba28e30a) — *Airbnb Engineering*
3. [Flutter Showcase — Real production apps](https://flutter.dev/showcase) — *flutter.dev*
4. [React Native — The New Architecture](https://reactnative.dev/architecture/landing-page) — *reactnative.dev*
5. [Kotlin Multiplatform Production Cases](https://www.jetbrains.com/lp/kotlin-multiplatform-production/) — *JetBrains*
6. [Uber Engineering — Architecting Mobile at Scale](https://www.uber.com/blog/tag/mobile/) — *Uber Engineering*
7. [.NET MAUI — Migrating from Xamarin](https://learn.microsoft.com/en-us/dotnet/maui/migration/) — *Microsoft Learn*
8. [Gartner Magic Quadrant for Mobile App Development Platforms](https://www.gartner.com/en/documents/) — *gartner.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/platform-landscape/` | Aligned to TOGAF · Gartner Mobile · ISO 25010 · OWASP MASVS*
