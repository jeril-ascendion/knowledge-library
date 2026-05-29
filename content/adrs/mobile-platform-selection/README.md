# Mobile Platform Selection

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

## Executive Summary

A context-driven platform selection framework is adopted. Flutter is the preferred default for new cross-platform mobile applications. Pure Native (separate Kotlin and Swift codebases) is mandated when performance SLA requires frame latency below 16ms, deep device API access is required, or regulatory requirements mandate platform-native attestation. React Native is permitted for teams with existing JavaScript and TypeScript capability. MAUI is permitted only for organisations with an existing .NET mobile codebase. Kotlin Multiplatform is adopted for sharing business logic when platform-native UI is required on both platforms.

## Decision Framework — Eight Weighted Criteria

| Criterion | Weight | What It Measures |
|---|---|---|
| Performance & UX Fidelity | 22% | Frame rate SLA, startup time, animation smoothness |
| Device API Access Depth | 18% | NFC, custom camera, BLE, SecureEnclave, biometric |
| Development Speed | 16% | Time to first release, parallel development overhead |
| Total Cost of Ownership (5yr) | 15% | Team size, tooling, hiring premium, maintenance |
| Team Skills & Ecosystem | 12% | Existing capability, hiring pool, community size |
| Maintainability | 9% | Framework stability, vendor commitment, tech debt |
| Security & Attestation | 5% | Play Integrity, AppAttest, regulatory compatibility |
| Regulatory Compliance | 3% | Data residency, BSP Circular 982, PDPA |

## Platform Options and Scores

| Platform | Weighted Score | Performance Ceiling | TCO Multiplier | Recommended When |
|---|---|---|---|---|
| Pure Native (Kotlin + Swift) | Context-dependent | 100% | 1.0× baseline | Frame rate < 16ms SLA, deep device API, regulatory attestation |
| Flutter (Dart, Impeller) | 4.38 / 5.0 | 95% of native | 0.58× | Default for new cross-platform apps |
| React Native (New Architecture) | 3.52 / 5.0 | 85-90% of native | 0.65× | Existing JS/TS mobile team, Expo workflow |
| MAUI (.NET) | 3.42 / 5.0 | 88% of native | 0.70× | Existing .NET mobile codebase only |
| Kotlin Multiplatform | 4.09 / 5.0 | 100% (native UI) | 0.80× | Complex shared domain logic, two native UI teams |

## Decision Rules

| Condition | Platform Decision |
|---|---|
| Frame rate SLA < 16ms OR deep native API (NFC, custom camera, BLE) | Pure Native |
| New cross-platform app, standard device APIs | Flutter (DEFAULT) |
| Existing JS/TS mobile team, React ecosystem investment | React Native New Architecture |
| Existing .NET codebase, C# team | MAUI (restricted) |
| Complex shared domain logic, two native UI teams | Kotlin Multiplatform + Native UI |

## Mandatory ARB Review Triggers

1. Any platform selection other than Flutter for a new cross-platform engagement requires ARB review.
2. Any React Native selection must document New Architecture adoption plan.
3. Any pure native selection costing more than 40% above Flutter equivalent requires cost justification.
4. Platform switches mid-project require ARB emergency review and client CTO sign-off.

## Trade-offs

| Trade-off | Consequence | Mitigation |
|---|---|---|
| Flutter uses own rendering engine | Platform-native feel requires deliberate implementation | Flutter Material 3 and Cupertino libraries approximate native behaviour |
| Flutter deep native API access requires platform channels | NFC, custom camera need native Kotlin/Swift modules | Assess device API requirements in discovery. If > 3 complex channels, evaluate native. |
| React Native New Architecture migration in progress | Not all libraries migrated from Bridge | Audit all dependencies for New Architecture compatibility before project start |

## Anti-Patterns to Avoid

### 1. Platform Choice by Team Familiarity Only
Selecting React Native because the team knows JavaScript without evaluating performance requirements or device API needs.

**CORRECT:** Team familiarity scores 12% weight — not the sole criterion. A team learns Dart in 3-6 weeks. Recovering from a wrong platform choice costs months.

### 2. Cross-Platform Start, Native Rewrite Mid-Project
Airbnb 2018: committed to React Native for two years, discovered brownfield integration and debugging limitations, rewrote in native. Switch cost exceeded choosing native initially.

**CORRECT:** Two-day technical spike on the highest-risk screen before platform commitment.

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
