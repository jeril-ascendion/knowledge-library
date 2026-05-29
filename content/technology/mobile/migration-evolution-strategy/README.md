# Migration and Evolution Strategy

> **Section:** `technology/mobile/migration-evolution-strategy/`
> **Alignment:** Strangler Fig Pattern | Branch by Abstraction | Evolutionary Architecture
> **Audience:** Solutions Architects · Mobile Architects · Engineering Managers

Mobile codebases evolve continuously. Legacy XML-based Android views migrate to Jetpack Compose. UIKit codebases adopt SwiftUI. React Native codebases move to New Architecture. Monolithic feature code migrates to modular architecture. These migrations are business-critical engineering operations: the application must continue delivering value to users throughout the migration, with no big-bang rewrites that halt feature development for months.

## Overview

The Strangler Fig pattern is the primary migration strategy: incrementally replace the legacy system component by component while the legacy system continues to operate. The migration proceeds in parallel with feature development — it is never a "pause and migrate" operation. The migration is complete when the last legacy component is strangled by its replacement.

## Migration Patterns

### Strangler Fig for Architecture Migration
Apply the Strangler Fig to Clean Architecture adoption in a legacy codebase:

1. Create the `domain` package with repository interfaces and domain models — empty initially.
2. For each new feature: implement it following Clean Architecture fully. The new feature uses the domain layer.
3. For each bug fix in legacy code: leave the fix in place but add a corresponding domain model and repository interface.
4. For each legacy screen that requires significant modification: extract the business logic into a Use Case, leave the UI unchanged temporarily.
5. Over time, all new code uses the Clean Architecture pattern. Legacy code is progressively replaced as screens require modification.

### XML to Compose Migration (Android)
`ComposeView` in XML layouts and `AndroidView` / `AndroidViewBinding` in Compose allow the two UI frameworks to coexist in the same application. Migration strategy:

1. Add Compose dependency and a `ComposeView` in the XML layout of the target screen.
2. Implement the new screen or component in Compose inside the `ComposeView`.
3. Once the Compose implementation is complete and tested, remove the XML layout and replace with a `setContent {}` call in the Activity/Fragment.
4. Migrate screens in order of complexity: simple screens first, complex screens with many states last.

### UIKit to SwiftUI Migration (iOS)
`UIHostingController` wraps a SwiftUI View in a UIKit container. `UIViewRepresentable` embeds a UIKit view in a SwiftUI hierarchy. Migration strategy mirrors the Android approach: new screens in SwiftUI, legacy screens in UIKit with `UIHostingController`-wrapped components for new features, gradual replacement as screens require modification.

### React Native New Architecture Migration
Migration from Bridge to New Architecture (JSI + Fabric) requires: enabling the New Architecture in `android/gradle.properties` and Podfile, migrating each native module from `TurboModuleRegistry.getEnforcing` to the new TurboModule spec, migrating each native UI component to the new Fabric ComponentRegistry. Third-party libraries must be New Architecture compatible — audit all dependencies before migration.

## Migration Governance

Migration phases are tracked as engineering epics with explicit completion criteria. Each phase has a rollback plan. The migration is complete when: the last legacy component is removed, CI confirms no references to the legacy API remain, and the architecture fitness functions pass without exclusions.

Migration velocity is measured: percentage of codebase on new architecture, tracked monthly. Target: 10% migration per sprint for a medium-sized codebase. Migrations that stall at 50% complete are more dangerous than either the legacy system or the new system — they create dual-maintenance overhead and confusion for new engineers.

## Anti-Patterns to Avoid

> **⚠ Big Bang Rewrite** — "We'll rewrite the entire app in Compose/SwiftUI/Clean Architecture over the next quarter. Feature development is paused until the rewrite is complete." The rewrite always takes longer than estimated. The legacy system continues to accrue production issues that must be fixed in the legacy codebase, creating two codebases to maintain.
> **CORRECT:** Strangler Fig. The legacy system continues to operate. New code uses the new pattern. Migration proceeds incrementally without halting feature development.

> **⚠ Migration Without Fitness Functions** — Migrating the architecture without automated enforcement of the new standards. Engineers write new code in the old pattern because it is familiar. Six months in, the new and old patterns coexist chaotically.
> **CORRECT:** Architecture fitness functions in CI enforce the new standard from day one. New legacy code cannot be added without explicitly disabling the fitness function gate — which requires a documented justification.

## References

1. Fowler, Martin — Strangler Fig Application. martinfowler.com/bliki/StranglerFigApplication.html
2. Fowler, Martin — Branch by Abstraction. martinfowler.com/bliki/BranchByAbstraction.html
3. Ford et al. — Building Evolutionary Architectures. O'Reilly, 2017.
4. Google — Migrating to Jetpack Compose. developer.android.com/jetpack/compose/migrate
