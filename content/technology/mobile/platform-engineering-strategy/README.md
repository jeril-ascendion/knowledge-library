# Mobile Platform Engineering Strategy

> **Section:** `technology/mobile/platform-engineering-strategy/`
> **Alignment:** Platform Engineering (Gartner) | Developer Experience (DX) | Team Topologies | Google Developer Platform
> **Audience:** Engineering Managers · Platform Engineers · CTO · Solutions Architects

Platform engineering for mobile is the discipline of building and maintaining the internal infrastructure, tooling, and golden paths that enable feature teams to deliver with high velocity and consistent quality. A mobile platform team is not a gatekeeper — it is a force multiplier. Every hour invested in a golden path template, a shared build pipeline component, or a well-documented internal library saves the equivalent across every feature team that uses it.

## Overview

The mobile platform engineering strategy covers four capability areas: the golden path (opinionated, supported development paths that work out of the box), shared platform capabilities (authentication, analytics, crash reporting, push), internal developer tooling (code generation, scaffolding, build optimization), and developer experience measurement (DORA metrics applied to mobile delivery).

## Golden Path

The golden path is the officially supported, documented, and maintained approach to common engineering tasks. Feature teams are not required to use it — but deviating from it means accepting the overhead of unsupported infrastructure. Golden path components for mobile:

**Project scaffolding:** A CLI or GitHub template that generates a new feature module pre-configured with MVVM + Clean Architecture, Hilt DI, unit test scaffolding, snapshot test scaffolding, and CI integration. A new screen should be commit-ready in under 10 minutes.

**API client generation:** Given a GraphQL schema or OpenAPI specification, generated Apollo Kotlin/iOS or Retrofit client code. Eliminates handwritten API integration code and the serialisation bugs that come with it.

**Shared design system:** A versioned `:core:ui` library with all design system components, tokens, and theming. Feature teams import and use — they do not re-implement Button, TextField, or LoadingState.

**Release pipeline:** A fastlane configuration and GitHub Actions workflow that any new project can adopt in under 30 minutes, preconfigured with code signing, testing gates, and distribution.

## Shared Platform Capabilities

Authentication, push notifications, analytics, crash reporting, and experiment assignment are infrastructure capabilities that should be implemented once and consumed by all mobile applications. Implementing these independently per application creates inconsistent behaviour, multiplied security surface, and duplicated maintenance burden. The platform SDK:

- Wraps Firebase Crashlytics, Performance, and Analytics behind a stable internal API
- Wraps the OAuth 2.0 + PKCE flow, handling token refresh, biometric authentication, and secure storage
- Provides a typed, versioned event schema for analytics — feature teams fire domain events, the platform SDK handles provider integration
- Abstracts push notification registration, token management, and payload handling

## Developer Experience Measurement

DORA metrics adapted for mobile delivery:
- **Deployment Frequency:** How often a production release reaches users (target: multiple per week)
- **Lead Time:** From commit to production (target: under 1 day for bug fixes, under 1 week for features)
- **Change Failure Rate:** Percentage of releases requiring rollback or hotfix (target: below 5%)
- **Recovery Time:** From incident to production fix deployed (target: under 4 hours)

Measure and publish DORA metrics to the engineering organisation monthly. Trend analysis identifies platform investments that will move the metrics.

## Anti-Patterns to Avoid

> **⚠ Platform Team as Gatekeeper** — All mobile infrastructure changes require platform team approval and are routed through the platform team's backlog. Feature teams blocked waiting for platform team capacity.
> **CORRECT:** Platform team builds self-service infrastructure. Feature teams are empowered to use and extend it without bottlenecks. Platform team reviews proposals, not every implementation.

> **⚠ No Golden Path — Every Team Chooses Differently** — One team uses Retrofit, another uses Ktor. One team uses Hilt, another uses Dagger directly. One team uses fastlane, another has custom shell scripts. Every new engineer must learn a different stack for each project.
> **CORRECT:** Opinionated golden path with clear documentation and active support from the platform team. Deviation allowed with architectural justification — but the default is always the golden path.

## References

1. Skelton, Matthew and Pais, Manuel — Team Topologies. IT Revolution Press, 2019.
2. Forsgren, Nicole, Humble, Jez, Kim, Gene — Accelerate. IT Revolution Press, 2018.
3. Gartner — Platform Engineering Hype Cycle. gartner.com
4. Google — Android Platform Engineering. developer.android.com/build
