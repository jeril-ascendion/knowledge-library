# ADR: Mobile Platform Selection

> **ADR Reference:** `ADR-MOB-002`
> **Alignment:** TOGAF Technology Architecture | IEEE 1471 | Gartner Mobile Platform Guide | Google MAD | Flutter Architecture
> **Audience:** Solutions Architects · CTOs · Mobile Engineering Leads · Client Technology Decision-Makers

Platform selection is the highest-stakes technology choice in mobile engineering. It determines team structure, hiring pool, five-year total cost of ownership, performance ceiling, and the feasibility of certain device API feature categories. This ADR establishes the structured evaluation framework that must be applied at project initiation — replacing informal, preference-driven decisions with weighted criteria and documented rationale.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-MOB-002 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice — Ascendion |
| Status | ACCEPTED |
| Domain | Mobile Architecture |
| ARB Approval | Required |
| Stakeholders | Solutions Architects · CTOs · Mobile Engineering Leads · Client Technology Decision-Makers |

## Executive Summary

**Decision:** A context-driven platform selection framework is adopted. Flutter is the preferred default for new cross-platform mobile applications. Pure Native (separate Kotlin and Swift codebases) is mandated when performance SLA requires frame latency below 16ms, deep device API access is required, or regulatory requirements mandate platform-native attestation. React Native is permitted for teams with existing JavaScript and TypeScript capability. MAUI is permitted only for organisations with an existing .NET mobile codebase. Kotlin Multiplatform is adopted for sharing business logic when platform-native UI is required on both platforms.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Performance & UX Fidelity | 22% | Frame rate SLA, startup time, animation smoothness |
| 2 | Device API Access Depth | 18% | NFC, custom camera, BLE, SecureEnclave, biometric |
| 3 | Development Speed | 16% | Time to first release, parallel development overhead |
| 4 | Total Cost of Ownership (5yr) | 15% | Team size, tooling, hiring premium, maintenance |
| 5 | Team Skills & Ecosystem | 12% | Existing capability, hiring pool, community size |
| 6 | Maintainability | 9% | Framework stability, vendor commitment, tech debt |
| 7 | Security & Attestation | 5% | Play Integrity, AppAttest, regulatory compatibility |
| 8 | Regulatory Compliance | 3% | Data residency, BSP Circular 982, PDPA |

## Considered Options

### Option A — Flutter (PREFERRED DEFAULT)
Dart with the Impeller rendering engine. 95% of native performance, 0.58× baseline TCO. The default for new cross-platform apps with standard device APIs. Weighted score: **4.38 / 5.0**

### Option B — Kotlin Multiplatform
Shared domain logic with native UI per platform. 100% performance ceiling (native UI), 0.80× TCO. Adopted for complex shared domain logic with two native UI teams. Weighted score: 4.09 / 5.0

### Option C — React Native (New Architecture)
JSI + Fabric. 85–90% of native performance, 0.65× TCO. Permitted for teams with existing JS/TS mobile capability and Expo workflow investment. Weighted score: 3.52 / 5.0

### Option D — MAUI (.NET) (RESTRICTED)
C# / .NET 8. 88% of native performance, 0.70× TCO. Permitted only for organisations with an existing .NET mobile codebase. Not for greenfield projects. Weighted score: 3.42 / 5.0

### Option E — Pure Native (Kotlin + Swift)
Separate Kotlin/Jetpack Compose and Swift/SwiftUI codebases. 100% performance ceiling, 1.0× baseline TCO. Mandated when frame rate SLA < 16ms, deep device API access, or regulatory attestation is required. Score is context-dependent — selected on hard requirements, not weighted average.

## Decision

Platform is selected by applying the decision rules below. Flutter is the default; any deviation requires documented rationale and ARB review.

| Condition | Platform Decision |
|---|---|
| Frame rate SLA < 16ms OR deep native API (NFC, custom camera, BLE) | Pure Native |
| New cross-platform app, standard device APIs | Flutter (DEFAULT) |
| Existing JS/TS mobile team, React ecosystem investment | React Native New Architecture |
| Existing .NET codebase, C# team | MAUI (restricted) |
| Complex shared domain logic, two native UI teams | Kotlin Multiplatform + Native UI |

| Platform | Weighted Score | Performance Ceiling | TCO Multiplier | Recommended When |
|---|---|---|---|---|
| Pure Native (Kotlin + Swift) | Context-dependent | 100% | 1.0× baseline | Frame rate < 16ms SLA, deep device API, regulatory attestation |
| Flutter (Dart, Impeller) | 4.38 / 5.0 | 95% of native | 0.58× | Default for new cross-platform apps |
| React Native (New Architecture) | 3.52 / 5.0 | 85-90% of native | 0.65× | Existing JS/TS mobile team, Expo workflow |
| MAUI (.NET) | 3.42 / 5.0 | 88% of native | 0.70× | Existing .NET mobile codebase only |
| Kotlin Multiplatform | 4.09 / 5.0 | 100% (native UI) | 0.80× | Complex shared domain logic, two native UI teams |

## Trade-off Analysis

| Trade-off Accepted | Consequence | Mitigation |
|---|---|---|
| Flutter uses own rendering engine | Platform-native feel requires deliberate implementation | Flutter Material 3 and Cupertino libraries approximate native behaviour |
| Flutter deep native API access requires platform channels | NFC, custom camera need native Kotlin/Swift modules | Assess device API requirements in discovery. If > 3 complex channels, evaluate native. |
| React Native New Architecture migration in progress | Not all libraries migrated from Bridge | Audit all dependencies for New Architecture compatibility before project start |

## Implementation Guidance

1. Apply the eight weighted criteria at project initiation — document the score for each candidate platform
2. Run a two-day technical spike on the highest-risk screen before committing to any platform
3. Default to Flutter unless a decision rule mandates otherwise — record the rule that applies
4. For Flutter, audit device API requirements; if more than 3 complex platform channels are needed, re-evaluate Pure Native
5. For React Native, confirm and document a New Architecture (JSI + Fabric) adoption plan before sprint 1
6. For any non-Flutter cross-platform selection, raise an ARB review with documented rationale
7. Configure the CI/CD pipeline (ADR-MOB-003) for the selected platform once chosen

## Compliance Checkpoints

| Checkpoint | Trigger | Owner | SLA |
|---|---|---|---|
| Platform Selection Review | Any platform other than Flutter for a new cross-platform engagement | ARB | Before sprint 1 |
| React Native New Architecture Plan | Any React Native selection | Solutions Architect | Before sprint 1 |
| Native Cost Justification | Pure Native costing > 40% above Flutter equivalent | ARB | Before commitment |
| Mid-Project Platform Switch | Any platform change after development start | ARB (emergency) + Client CTO | Sign-off before switch |

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-001 | Mobile Architecture Pattern | Architecture pattern applied once platform is chosen |
| ADR-MOB-003 | Mobile CI/CD Pipeline | CI/CD pipeline configured per platform selected here |
| ADR-SEC-011 | Mobile Security Controls | Attestation capabilities depend on this platform decision |

## References

1. Flutter — Architecture Overview. docs.flutter.dev/app-architecture
2. JetBrains — Kotlin Multiplatform. kotlinlang.org/docs/multiplatform.html
3. Meta — React Native New Architecture. reactnative.dev/docs/new-architecture-intro
4. Airbnb Engineering — Sunsetting React Native. medium.com/airbnb-engineering, 2018.
5. Nubank Engineering — Flutter at Scale. building.nubank.com.br

> **⚠ Platform Choice by Team Familiarity Only** — Selecting React Native because the team knows JavaScript without evaluating performance requirements or device API needs.
> **CORRECT:** Team familiarity scores 12% weight — not the sole criterion. A team learns Dart in 3–6 weeks. Recovering from a wrong platform choice costs months.

> **⚠ Cross-Platform Start, Native Rewrite Mid-Project** — Airbnb 2018: committed to React Native for two years, discovered brownfield integration and debugging limitations, rewrote in native. Switch cost exceeded choosing native initially.
> **CORRECT:** Two-day technical spike on the highest-risk screen before platform commitment.
