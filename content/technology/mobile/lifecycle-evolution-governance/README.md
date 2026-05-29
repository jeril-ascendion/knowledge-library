# Lifecycle and Evolution Governance

> **Section:** `technology/mobile/lifecycle-evolution-governance/`
> **Alignment:** Semantic Versioning | App Store Review Guidelines | Google Play Policy | Technical Debt Management
> **Audience:** Mobile Architects · Engineering Managers · Product Managers · Release Managers

Mobile applications have a lifecycle that spans years. OS versions advance and deprecate APIs. Third-party libraries evolve and introduce breaking changes. Business requirements add features that stress the original architecture. User bases grow and expose performance limits not anticipated at launch. Lifecycle and Evolution Governance is the set of policies and processes that manage this multi-year evolution without accumulating unmanageable technical debt.

## Overview

Governance covers four time horizons: the release lifecycle (how each version of the application is planned, built, and deployed), the OS support policy (which platform versions the application targets), the technical debt management process (how architectural decisions are reviewed and revised), and the dependency evolution policy (how third-party libraries are kept current).

## Release Lifecycle

Versioning: semantic versioning (`MAJOR.MINOR.PATCH`) for the user-visible version string. Major: breaking changes to data formats or app behaviour. Minor: new features. Patch: bug fixes. Build number: monotonically increasing integer managed by CI (the CI run number). The App Store and Play Store use the build number for ordering — it must never decrease.

Release cadence: feature releases every 2-4 weeks (bi-weekly sprints align to bi-weekly releases). Hotfix releases as needed for P1/P2 production issues, targeting 4-8 hours from diagnosis to App Store submission. Hotfix process: create a hotfix branch from the release tag, apply the minimal fix, submit for expedited App Store review with documented user-impact justification.

## OS Version Support Policy

Support policy must be explicit and communicated to clients before project launch. The Ascendion default:

Android: support the last 5 major Android versions (currently Android 10-15), covering >95% of active Android devices as reported by Google Play Console. Minimum SDK version set accordingly. APIs introduced after the minimum SDK version use conditional availability checks (`Build.VERSION.SDK_INT >= Build.VERSION_CODES.X`).

iOS: support the current and previous two major iOS versions (currently iOS 16-18), covering >95% of active iOS devices as reported by App Store analytics. APIs introduced in newer iOS versions use `#available(iOS 17, *)` conditional availability.

OS support policy review: annually, after each major OS release (September-October). Dropping a platform version is a minor version increment — it removes user-visible capability (the ability to update the app on older OS versions).

## Technical Debt Management

Technical debt register maintained per project. Each debt item: description, affected layers, estimated remediation effort, business risk if unaddressed, severity (P1-P4). Reviewed in architecture retrospectives: monthly for active projects, quarterly for maintenance-mode projects.

Debt reduction policy: minimum 20% of sprint capacity allocated to technical debt reduction when the register exceeds 10 P2+ items. Debt reduction work is treated as equivalent to feature development — estimated, tracked, and celebrated as delivery.

Architecture fitness functions: automated tests in CI that verify architectural invariants. Example: a fitness function that fails the build if any Use Case class imports an Android SDK class. These catch architectural drift before it accumulates into structural debt.

## Anti-Patterns to Avoid

> **⚠ No OS Deprecation Planning** — Supporting Android 6 (API 23) because "some users still have old devices" while GoogleAPIs and security libraries have dropped support. Engineering effort spent working around deprecated APIs and missing security features.
> **CORRECT:** Explicit OS support policy agreed with the client at project inception. Annual review with data from Google Play Console and App Store analytics. OS version drops planned 6 months in advance with user communication.

> **⚠ Technical Debt Register Ignored After Creation** — A debt register created during an architecture review, never reviewed again. Debt accumulates until it produces a production incident.
> **CORRECT:** Technical debt reviewed monthly in architecture retrospectives. Debt reduction capacity allocated every sprint proportionally to register severity.

## References

1. Fowler, Martin — Technical Debt Quadrant. martinfowler.com/bliki/TechnicalDebtQuadrant.html
2. Ford et al. — Building Evolutionary Architectures. O'Reilly, 2017.
3. Semantic Versioning. semver.org
4. Google — Play Console — Distribution Dashboard. play.google.com/console
