# Scalability Evolution Model

> **Section:** `technology/mobile/scalability-evolution-model/`
> **Alignment:** Evolutionary Architecture | Fitness Functions | Strangler Fig Pattern | Martin Fowler
> **Audience:** Solutions Architects · Engineering Managers · CTOs

A mobile application that starts as a three-engineer MVP and scales to a hundred-engineer platform does not scale linearly — it evolves through distinct architectural phases, each with different dominant constraints. Planning the evolutionary path before beginning development prevents the most expensive form of technical debt: architecture that is correct for today's scale but structurally incompatible with tomorrow's.

## Overview

The Scalability Evolution Model defines five stages of mobile application growth, the architectural characteristics that are appropriate at each stage, and the transition triggers that indicate readiness for the next stage. Advancing a stage prematurely adds overhead that slows a small team. Delaying a stage transition creates structural debt that multiplies remediation cost.

## Evolution Stages

### Stage 1: MVP (1-5 Engineers, 0-6 Months)
Single-module application with MVVM + Clean Architecture applied consistently. Domain layer (Use Cases, domain models, repository interfaces) separated from data and presentation layers but all in one Gradle module or Swift Package. Lightweight DI (Hilt with simple module structure). No feature modularization — premature optimization. Full test coverage on Use Cases and ViewModels established from day one. Build time: under 2 minutes. The technical discipline established at Stage 1 determines how much debt must be repaid at Stage 3.

### Stage 2: Growth (5-15 Engineers, 6-18 Months)
First feature modularization: split the application into `:app`, `:core:*`, and `:feature:*` modules when the build time exceeds 3 minutes or when two or more features are actively developed simultaneously. Introduce CI/CD with code signing automation (fastlane Match). Establish snapshot testing for design system components. Introduce Crashlytics and Firebase Performance Monitoring. The architecture from Stage 1 accommodates this transition without structural change — only physical module boundaries are added.

### Stage 3: Scale (15-50 Engineers, 18-36 Months)
Strict module ownership assigned to feature teams. Build system optimization: Gradle build cache, remote build cache, parallel execution. Architecture fitness functions in CI: automated tests that verify no feature module imports another feature module, no Use Case imports Android SDK classes. Performance SLA monitoring with alerting. Dynamic feature delivery (Play Feature Delivery on Android) for optional feature modules reducing install size. Design system formalized as a shared library with versioning.

### Stage 4: Enterprise (50-200 Engineers, 3+ Years)
Multi-team, multi-product architecture. Shared platform capabilities (authentication, push notifications, analytics, crash reporting) extracted to a Platform SDK consumed by multiple applications. Monorepo or polyrepo governance decision formalized. Inner source model for shared components: platform team owns core modules, feature teams contribute through pull requests with platform team review. Dependency governance board reviews new third-party library additions.

### Stage 5: Platform (200+ Engineers)
Multiple standalone applications sharing a common platform layer. Micro-frontend architecture with dynamically loaded feature modules. Independent release cadences per feature team. The architecture at this stage resembles distributed systems more than a mobile application — Conway's Law produces module boundaries that match organisational boundaries.

## Transition Triggers

| From → To | Trigger |
|---|---|
| Stage 1 → 2 | Build time > 3min OR 2+ concurrent active features OR team > 5 engineers |
| Stage 2 → 3 | Build time > 5min OR team > 15 engineers OR merge conflicts in shared modules > 5/week |
| Stage 3 → 4 | Multiple products sharing infrastructure OR team > 50 engineers |
| Stage 4 → 5 | Multiple applications, independent release tracks needed |

## Anti-Patterns to Avoid

> **⚠ Premature Modularization** — Splitting a three-engineer codebase into 12 Gradle modules. The overhead of managing module boundaries, version catalogs, and build configurations slows a small team significantly with minimal benefit.
> **CORRECT:** Start with a well-structured single module following Clean Architecture. Split when a specific trigger (build time, team size, concurrent features) is hit.

> **⚠ Big Bang Architecture Migration** — Attempting to move from Stage 1 monolith to Stage 3 modular architecture in a single multi-month project while feature development continues.
> **CORRECT:** Strangler Fig pattern: extract one feature into its own module per sprint while continuing feature development. The migration proceeds incrementally without halting delivery.

## References

1. Ford, Neal, Parsons, Rebecca, Kua, Patrick — Building Evolutionary Architectures. O'Reilly, 2017.
2. Fowler, Martin — Strangler Fig Application. martinfowler.com/bliki/StranglerFigApplication.html
3. Google — Android App Modularization Guide. developer.android.com/topic/modularization
