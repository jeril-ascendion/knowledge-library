# Mobile Reliability Engineering

> **Section:** `technology/mobile/mobile-reliability-engineering/`
> **Alignment:** SRE Principles (Google SRE Book) | Error Budget Policy | SLO Framework
> **Audience:** SREs · Mobile Engineering Leads · DevOps Engineers · Product Managers

Mobile Reliability Engineering applies Site Reliability Engineering principles to the unique operational context of client-side mobile applications. The core discipline is identical: define Service Level Objectives (SLOs), measure Service Level Indicators (SLIs), calculate error budgets, and use error budget burn rate to guide engineering prioritisation. The implementation differs from backend SRE because the application runs on user-owned devices with variable hardware, OS versions, and network conditions outside the engineering team's control.

## Overview

Reliability for mobile is a shared responsibility between engineering (code quality, architectural resilience, release quality) and product (understanding that reliability investment competes with feature velocity, and error budget policy governs the trade-off). The error budget framework makes this trade-off explicit and quantified.

## Service Level Objectives for Mobile

Define SLOs across four dimensions:

**Availability SLO:** Crash-free users rate > 99.5% (28-day rolling window). Measured by Firebase Crashlytics. This means at most 0.5% of active users experience a crash per 28-day period. For a 100,000 active user base, this is 500 users experiencing a crash — a meaningful quality bar.

**Performance SLO:** P75 cold start time < 2.5 seconds; P75 screen load time < 1.5 seconds; P90 API response time < 1.0 second. Measured by Firebase Performance Monitoring.

**ANR SLO (Android):** ANR rate < 0.2% across the active install base. Measured by Google Play Android Vitals.

**Release Quality SLO:** Change Failure Rate < 5% (percentage of releases requiring a hotfix or rollback within 48 hours of release).

## Error Budget Policy

The error budget is the allowed unreliability within the SLO period. If the crash-free SLO is 99.5% and actual performance is 99.8%, 60% of the error budget remains. If actual performance is 99.2%, 60% of the error budget is consumed — triggering a reliability focus sprint.

Error budget policy: when error budget consumption exceeds 50% in a 28-day window, the next sprint allocates 50% engineering capacity to reliability work. When budget is exhausted (SLO violated), feature development pauses until the SLO is restored. This policy is agreed with the product organisation before the project launches — not negotiated during an incident.

## Incident Response

Mobile incidents differ from backend incidents: the application is already deployed to user devices and cannot be rolled back instantly. Response options in order of speed: feature flag kill switch (immediate, if the failing feature is behind a flag), Play Store staged rollout halt (minutes — stops rollout, does not remove installed version), expedited App Store review for emergency hotfix (4-8 hours), standard hotfix release (24-48 hours for App Store).

Runbook for mobile incidents: (1) Identify the affected population using Crashlytics filtering. (2) Determine if the failure is behind a feature flag — toggle off if so. (3) Halt Play Store staged rollout if rollout is in progress. (4) Request expedited App Store review if iOS users are affected. (5) Fix, test, and submit hotfix. (6) Post-mortem within 5 business days.

## Anti-Patterns to Avoid

> **⚠ No SLOs Defined** — Releasing a mobile application without defined reliability targets. Reliability discussions happen reactively after incidents rather than proactively before them.
> **CORRECT:** SLOs defined and agreed with the product organisation during project inception. Monitored from the first production release. Error budget policy documented and enforced.

> **⚠ Feature Velocity Always Wins** — Engineering team always ships features regardless of error budget status. Reliability regressions accumulate silently until a critical incident.
> **CORRECT:** Error budget policy enforced. When the budget is exhausted, feature development pauses. This creates the incentive to maintain reliability proactively rather than reactively.

## References

1. Google — Site Reliability Engineering. sre.google/books
2. Google — The SRE Workbook. sre.google/workbook/table-of-contents
3. Beyer et al. — Site Reliability Engineering. O'Reilly, 2016.
4. Google — Android Vitals. play.google.com/console/about/vitals
