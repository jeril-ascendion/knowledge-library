# Scalability and Modularization

> **Section:** `technology/mobile/scalability-modularization/`
> **Alignment:** Conway's Law | Google MAD Modularization | Team Topologies | Gradle Build Performance
> **Audience:** Mobile Architects · Platform Engineers · Engineering Managers

Modularization is not primarily a technical problem — it is an organisational problem. Conway's Law states that systems reflect the communication structures of the organisations that produce them. A mobile application built by a team with no module boundaries will produce an application with no architectural boundaries. Modularization is the explicit alignment of code structure with team structure.

## Overview

Feature modularization divides the application into independently buildable, testable, and (where applicable) deliverable units aligned with product features and team ownership. The benefits compound over time: build times scale with change scope rather than codebase size, teams develop features in parallel without stepping on each other, and the module dependency graph enforces architectural rules that code reviews cannot.

## Module Architecture

### Android Gradle Multi-Module Structure

The recommended module graph for a medium-to-large Android application:

```
:app (application module — entry point, DI graph assembly)
:feature:account
:feature:transfer
:feature:onboarding
:feature:settings
:core:domain (shared domain models, repository interfaces, base Use Cases)
:core:network (API client infrastructure, interceptors, token refresh)
:core:database (Room database, shared DAOs)
:core:ui (shared design system components, theme)
:core:testing (test utilities, fake implementations)
```

Rules: feature modules depend only on `:core` modules, never on other feature modules. If two features need to share data, the shared data lives in `:core:domain`. If two features need to navigate to each other, navigation is mediated through the `:app` module's navigation graph.

### Module Type Classification
- **Application modules:** `:app` — assemble the app, configure DI
- **Feature modules:** `:feature:*` — screen-level UI, ViewModel, feature-specific Use Cases
- **Library modules:** `:core:*` — shared infrastructure, never contain UI
- **Dynamic feature modules:** Optional — for on-demand feature delivery via Play Feature Delivery

### Build Performance Impact
A change to `:feature:account` triggers rebuild of `:feature:account` and `:app`. All other feature modules are cache hits. Without modularization, any change triggers a full rebuild. At 100 engineers making 10 builds per day, the build time saving from modularization is measured in engineering weeks per year.

## iOS Swift Package Manager Modularization

The equivalent on iOS uses Swift Package Manager local packages. Each feature is a local Swift package with its own module targets: `AccountUI`, `AccountDomain`, `AccountData`. The main Xcode project imports only the packages it needs. SPM enforces the dependency graph — circular dependencies fail the build.

## Team Topology Alignment

Map module ownership to team ownership. The Account team owns `:feature:account`. The Platform team owns `:core:*`. Merge conflicts on a module signal a team boundary violation — two teams are modifying the same module, indicating their feature boundary needs redefinition.

## Anti-Patterns to Avoid

> **⚠ Modularization by Layer Instead of Feature** — `:ui`, `:domain`, `:data` as top-level modules. The entire UI team modifies `:ui`. Every feature change requires coordinating across three modules. Build times improve marginally because the entire `:ui` module rebuilds on any screen change.
> **CORRECT:** Modularize by feature: `:feature:account` contains its own UI, domain, and data layers. The account team works entirely within their module. Other teams' build caches are unaffected by account changes.

> **⚠ Feature Modules Depending on Each Other** — `:feature:transfer` imports `:feature:account` to reuse the AccountSummary composable. Creates tight coupling between features, breaking independent deployability.
> **CORRECT:** Move shared UI components to `:core:ui`. Move shared domain models to `:core:domain`. Features depend only on core modules.

## References

1. Google — Android Modularization Guide. developer.android.com/topic/modularization
2. Skelton, Matthew and Pais, Manuel — Team Topologies. IT Revolution Press, 2019.
3. Google — Build Performance Guide. developer.android.com/build/optimize-your-build
4. Gradle — Build Caching. docs.gradle.org/current/userguide/build_cache.html
