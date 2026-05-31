# Decision Summary

> **Section:** `technology/mobile/decision-summary/`
> **Alignment:** ADR Registry | Architecture Review Board | TOGAF Decisions Log
> **Audience:** Solutions Architects · CTOs · Engineering Leads · Client Technology Leadership

The Decision Summary consolidates the key architectural decisions across all 28 sections of the Mobile Development knowledge base into a single reference. Each decision includes its rationale, the alternatives considered, and the conditions under which the decision should be revisited. This section is the executive briefing for the full knowledge base.

## Overview

Architecture decisions have three properties: they are consequential (they constrain many subsequent decisions), they are hard to reverse (changing them is expensive after the system is built around them), and they decay (the context that made a decision optimal changes over time). The Decision Summary documents not only the decisions but the conditions that would prompt revisiting them.

## Decision Registry

### D-001: Architecture Pattern — Clean Architecture + MVVM
**Decision:** Clean Architecture with MVVM presentation pattern for all native mobile applications.
**Rationale:** Highest testability (Use Cases testable without device), security auditability (Data layer as single security gateway), and cross-platform knowledge transferability (same mental model on Android and iOS).
**Alternatives:** MVI (higher state predictability, higher boilerplate), TCA (best iOS testability, iOS-only, steep learning curve), MVP (lifecycle-unaware, superseded by ViewModel).
**Revisit when:** MVI becomes sufficiently tooled for iOS; TCA matures to cover both platforms; a new architectural pattern achieves substantially higher engineering velocity at equivalent quality.
**ADR:** ADR-MOB-001.

### D-002: Platform Selection Framework
**Decision:** Context-driven: Flutter as preferred default for cross-platform; Pure Native when performance SLA <16ms or deep device API required; React Native for existing JS teams; MAUI for existing .NET teams.
**Rationale:** No single platform is optimal for all contexts. Decision framework with weighted quality attributes is more defensible than a single mandated platform.
**Alternatives:** Mandate Flutter universally (ignores legitimate native requirements); mandate Native universally (ignores TCO advantage of cross-platform).
**Revisit when:** Flutter performance ceiling rises to 99%+ of native; React Native New Architecture stabilises fully; Kotlin Multiplatform + Compose Multiplatform matures for iOS.
**ADR:** ADR-MOB-002.

### D-003: CI/CD Tooling — Fastlane + GitHub Actions
**Decision:** Fastlane for mobile-specific automation (signing, building, distribution, store submission); GitHub Actions for pipeline orchestration.
**Rationale:** Fastlane Match solves code signing reliability at the root. GitHub Actions matrix enables Android/iOS parallel builds. Together: the most battle-tested combination in the mobile industry.
**Alternatives:** Bitrise (higher cost, vendor lock-in), Xcode Cloud (iOS-only, no Android), Codemagic (Flutter-optimised but narrow).
**Revisit when:** A platform provides integrated build, sign, test, and deploy for both Android and iOS at lower total cost with equivalent reliability.
**ADR:** ADR-MOB-003.

### D-004: Security Baseline — OWASP MASVS
**Decision:** MASVS Level 1 minimum for all applications; Level 2 mandatory for financial services, healthcare, and government.
**Rationale:** MASVS is the industry-standard mobile security verification framework, aligned with NIST, BSP Circular 982, and HIPAA requirements.
**Alternatives:** Custom security checklist (lower coverage, harder to audit); ISO 27001 only (not mobile-specific).
**Revisit when:** OWASP MASVS releases a major revision that changes the control set significantly.
**ADR:** ADR-SEC-011.

### D-005: Backend Integration — BFF Pattern, GraphQL Preferred
**Decision:** Mobile BFF mandatory (no shared web API). GraphQL preferred for new BFF implementations. REST with mobile conventions for existing REST infrastructure.
**Rationale:** Shared APIs are not designed for mobile's network constraints and battery budget. GraphQL's field selection eliminates over-fetching by design.
**Alternatives:** Direct microservice consumption (no aggregation layer, multiple round trips), shared GraphQL API with web (over-fetching, no mobile-optimised auth).
**Revisit when:** A new API paradigm (e.g., tRPC at mobile scale, server-driven UI) provides superior field selection and aggregation with lower implementation overhead.
**ADR:** ADR-INT-005.

### D-006: Authentication — OAuth 2.0 + PKCE
**Decision:** OAuth 2.0 Authorization Code + PKCE is the mandatory authentication flow for all mobile applications.
**Rationale:** PKCE eliminates the client_secret requirement that is fundamentally incompatible with mobile application security (client_secret extractable from binary). Industry standard since IETF RFC 7636 (2015).
**Alternatives:** OAuth Implicit Flow (deprecated, access token in URL fragment), Resource Owner Password Credentials (requires client to handle username/password — undermines IdP security controls), Custom authentication (no industry-standard security review, implementation errors likely).
**Revisit when:** A post-OAuth authentication standard (e.g., FIDO2 + Passkeys as primary) achieves equivalent adoption and security profile.

### D-007: Modularisation Strategy — Feature Modules
**Decision:** Feature-based modularisation (`:feature:account`, `:feature:transfer`) rather than layer-based (`:ui`, `:domain`, `:data`).
**Rationale:** Feature modules align with team ownership (Conway's Law aligned), enable parallel development without merge conflicts, and produce build time proportional to scope of change.
**Alternatives:** Layer-based modularisation (teams conflict on shared layer modules), no modularisation (build time scales linearly with codebase size).
**Revisit when:** A build toolchain achieves sub-2-minute incremental builds on large codebases without modularisation, eliminating the primary technical driver.

### D-008: Offline Strategy — Local Database as Single Source of Truth
**Decision:** Room (Android) or SwiftData (iOS) as the single source of truth. UI reads only from the local database.
**Rationale:** Eliminates the class of bugs where UI and local database are out of sync. Provides offline functionality without additional coding per screen.
**Alternatives:** Network-first (UI shows error when offline), in-memory caching (does not survive process death).
**Revisit when:** A reactive database synchronisation platform (e.g., Electric SQL, Turso) provides equivalent reliability with lower implementation overhead.

## Architectural Principles Summary

1. Security is structural — not additive.
2. Test at the lowest level where the behaviour can be verified.
3. Align module boundaries with team boundaries.
4. Explicit state machines over implicit lifecycle hooks.
5. Measure everything that matters; alert on everything measured.
6. Evolve incrementally — never rewrite.
7. Document decisions where they are made — in the repository, not in a wiki.

## Anti-Patterns to Avoid

> **⚠ Undocumented Architecture Decisions** — Choices made in chat threads or standups with no ADR, so the rationale is lost and the decision is silently relitigated every few months.
> **CORRECT:** Every Tier 1/Tier 2 decision is captured as an ADR with context, options, and consequences, versioned alongside the code and reviewed by the Architecture Council.

> **⚠ Decision Drift** — Teams quietly diverging from an accepted ADR without raising a superseding record, so the documented architecture and the shipped architecture disagree.
> **CORRECT:** Deviations are raised as a new ADR that supersedes the prior one; fitness functions and code review enforce the accepted decision until it is formally changed.

## References

1. All preceding 28 sections of the Mobile Development knowledge base.
2. ADR-MOB-001 through ADR-INT-005.
3. Clements, Paul et al. — Documenting Software Architectures: Views and Beyond. SEI, 2010.
