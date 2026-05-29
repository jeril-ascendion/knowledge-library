# Core Architecture Goals

> **Section:** `technology/mobile/core-architecture-goals/`
> **Alignment:** TOGAF Architecture Vision | SEI Quality Attribute Workshop | Clean Architecture | Google MAD
> **Audience:** Solutions Architects · Mobile Engineering Leads · CTOs

Architecture goals translate business intent into structural constraints on the engineering system. They are more durable than technology choices — the goal of testability persists whether the UI framework is XML Views, Jetpack Compose, UIKit, or SwiftUI. Defining goals explicitly prevents architecture drift: when a team faces a delivery trade-off, architecture goals provide the tiebreaker.

## Overview

Five architecture goals govern all Ascendion mobile engineering. They are ordered by priority — when goals conflict, higher-priority goals win. A decision that improves testability at the cost of short-term development speed is correct. A decision that improves development speed at the cost of security is never correct.

## Core Architecture Goals

### Goal 1: Security by Design (Highest Priority)
Security controls are structural, not additive. The Data layer is the single gateway for all external data — encryption, sanitisation, and credential management are applied once at this boundary. Business logic in Use Cases is isolated from the platform — preventing the class of vulnerability where platform APIs are called directly from UI components with inappropriate permissions. Security is auditable: the architecture makes it possible to verify security properties through code inspection, not just penetration testing.

### Goal 2: Testability
Every component of business consequence is testable without a device, emulator, or network. Use Cases are pure functions of their inputs and dependencies. ViewModels are observable state machines whose transitions can be asserted. Repositories are testable against in-memory data sources. The architectural constraint that enforces testability — no UI framework imports in the domain layer — is also the constraint that enforces Goal 1. Security and testability are aligned, not in tension.

### Goal 3: Modularity and Feature Independence
Features can be developed, tested, and delivered independently without modifying shared code. Module boundaries map to team boundaries — Conway's Law governs mobile as it governs distributed systems. A change to the Account feature does not require understanding or modifying the Transfer feature. Build times are proportional to the scope of a change — modifying one feature module rebuilds only that module and its dependents, not the entire application. On Android, this is Gradle multi-project builds with feature modules; on iOS, Swift Package Manager with explicit dependency declarations.

### Goal 4: Observability
Every production failure is diagnosable from logs, metrics, and crash reports without requiring a reproduction environment. The application emits structured telemetry: correlated request IDs across network calls, user journey breadcrumbs before a crash, performance traces around critical business operations. Observability is designed in — not bolted on after the first production incident.

### Goal 5: Evolvability (Lowest Priority, Not Unimportant)
The architecture accommodates change without requiring rewrites. New OS versions, new platform APIs, new business requirements are absorbed through extension rather than modification. This is achieved through the Dependency Rule of Clean Architecture — business logic has no dependency on platform details — and through the contract-based API design enforced by ADR-INT-005. The BFF pattern insulates mobile clients from backend evolution; the platform abstraction layer insulates business logic from platform evolution.

## Goal Trade-off Registry

| Decision Scenario | Goals in Conflict | Resolution |
|---|---|---|
| Skip unit tests to meet sprint deadline | Testability vs Delivery Speed | Testability wins. Coverage gate enforced by CI. |
| Store token in SharedPreferences for simplicity | Security vs Dev Speed | Security wins. Keystore/Keychain always. |
| Build monolithic feature module for speed | Modularity vs Dev Speed | Modularity wins if team > 3 engineers. |
| Add Crashlytics without consent flow | Observability vs Privacy/Security | Security wins. Consent required for analytics in regulated markets. |

## Anti-Patterns to Avoid

> **⚠ Architecture Goals as Wallpaper** — Goals written in a kickoff document and never referenced again. No connection between goals and code review criteria, CI gates, or sprint retrospectives.
> **CORRECT:** Architecture goals are referenced in code review checklists. Every PR template includes the question: "Does this change advance or compromise any of the five architecture goals?"

> **⚠ All Goals Equal** — Treating all five goals as having equal priority, leading to paralysis when they conflict.
> **CORRECT:** Explicit priority ordering documented and communicated. Security always beats delivery speed. Testability always beats simplicity of implementation.

## References

1. Bass, Len, Clements, Paul, Kazman, Rick — Software Architecture in Practice. 4th Ed. Addison-Wesley, 2021.
2. Ford, Neal, Richards, Mark — Fundamentals of Software Architecture. O'Reilly, 2020.
3. Google — Android App Architecture Guide. developer.android.com/topic/architecture
4. SEI — Quality Attribute Workshop. sei.cmu.edu/our-work/architecture/quality-attributes
