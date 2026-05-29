# Release Management

App Store and Google Play review timelines, staged rollouts with halt-and-rollback capability, mandatory feature flags for new functionality, trunk-based development with feature gating, semantic versioning, expedited review for emergency fixes, and the November–January App Store review freeze.

**Section:** `technology/mobile/` | **Subsection:** `release-management/`
**Alignment:** App Store Review Guidelines | Google Play Developer Policy | LaunchDarkly Feature Flagging | Semantic Versioning 2.0
**Audience:** Mobile Engineers · Product Managers · Release Managers

---

## Overview

Mobile release management is the discipline of shipping software to a distribution channel the team does not control. The App Store and Play Store each have their own review processes, their own rejection patterns, their own rollout mechanisms, and their own holiday freezes. The team that learns this rhythm ships predictably; the team that does not loses a sprint per quarter to last-minute rejections, surprise freezes, and emergency fixes that cannot reach users for three days because the expedited-review queue is also frozen.

The 2026 cadence: App Store reviews 24-48 hours for standard updates, 4-8 hours with documented expedited justification, longer for new apps and significant version updates. Google Play reviews 3-7 days for new apps and 1-3 days for updates; staged rollouts let the team ramp from 1 percent to 5, 20, 100 percent with halt-and-rollback. Feature flags decouple deployment from release: code merges to main behind a flag, the flag is dark in production until the team is ready to enable. Trunk-based development keeps branches short; the release tag is what's on main at the moment of cut.

The architectural shift is not "we have a release process." It is: **mobile release management is staged rollout discipline plus mandatory feature flags plus trunk-based development plus semantic versioning plus the published review-and-freeze calendar — with named processes for emergency fixes that respect each store's specific expedited-review mechanism.**

---

## Core Principles

### 1. Every new feature ships behind a flag

LaunchDarkly, Firebase Remote Config, or an in-house flag system gates new features. The code merges to main with the flag off; the flag is enabled by environment (dev first, internal next, then 1 percent of production, then ramped). Deployment is decoupled from release.

### 2. Staged rollouts default to 1 percent, ramp on telemetry

Google Play Console's staged rollout starts at 1 percent of the user base. The team watches crash-free users rate, ANR, and key business funnel events for 24-48 hours before ramping to 5 percent, then 20 percent, then 100 percent. Apple's phased release is the equivalent (1, 2, 5, 10, 20, 50, 100 percent over 7 days).

### 3. Trunk-based development with short-lived feature branches

All work merges to main daily. Feature branches are hours-to-days, not weeks. The release tag is whatever is on main at the moment of cut. No long-lived develop / release branches.

### 4. Semantic versioning, user-visible

`major.minor.patch` (4.2.1). Major bumps for breaking changes (new minimum OS version, removed features). Minor bumps for new features. Patch bumps for bug fixes. The user-visible version string communicates the change weight; the App Store and Play Store rely on monotonically increasing build numbers regardless of version string.

### 5. Emergency-hotfix process is documented and rehearsed

Production crashes do not wait for the standard 3-7 day review window. Apple's expedited review and Google Play's emergency rollout track allow bypass with justification. The team has the templates, the contact procedures, and the practice; the first time the team tries to expedite a review is not in the middle of an incident.

### 6. The review-freeze calendar is honoured

Apple's review staff are off for several weeks around US holidays (November 15-January 3 for typical years). Plan releases accordingly; submit by November 10 for pre-Christmas releases; expect December reviews to be slow and December rejections to be costly to fix.

---

## Architecture Deep-Dive

**App Store Review Timeline**

Standard review: 24-48 hours from submission to "Pending Developer Release" or "Rejected." Apple publishes the median (currently ~24 hours, was 7 days in 2017). First-time submissions and major version updates skew longer; iterative updates skew shorter.

Common rejection reasons:

- **Guideline 2.1 (App Completeness)**: The app crashes during review. Test on the device model and OS version Apple uses for review — usually the most recent iPhone and iOS.
- **Guideline 2.3 (Accurate Metadata)**: Screenshots show features not in the app; description claims functionality not present.
- **Guideline 4.3 (Spam)**: Apps duplicating other listings, refreshed templates with minor changes.
- **Guideline 5.1.1 (Privacy Labels)**: The App Privacy section doesn't match actual data collection. Common cause: third-party SDK collects telemetry not declared.
- **Guideline 5.1.2 (Data Use)**: Tracking across apps without ATT (App Tracking Transparency) consent.

Expedited review request: submitted through App Store Connect with a justification field. Apple's threshold for granting expedited review is real — user-impacting bug, time-sensitive event, regulatory deadline. "Marketing wants it sooner" does not qualify.

**Google Play Review Timeline**

Initial review (new app): 3-7 days, sometimes longer. Subsequent updates: 1-3 days for standard updates, sometimes hours for trusted publishers.

Common rejection reasons:

- **Policy violations**: Personal data handling, dangerous permissions without justification, financial-services without verification.
- **Target API level**: Google enforces minimum target SDK levels yearly; the August deadline catches every team that hasn't upgraded.
- **App Bundle issues**: Signing problems, missing required modules.
- **Content policies**: Inappropriate content, misleading claims.

Google Play has no formal expedited review — submit and hope. The emergency rollout track allows republishing a known-good build to bypass review for previously-shipped variants.

**Staged Rollout — Google Play**

Console UI configures the rollout percentage. The team rolls out 1 percent, watches Vitals (crash-free users rate, ANR rate, key business metrics) for 24-48 hours, ramps to 5 percent if green, ramps to 20 percent, ramps to 100 percent. Halt-and-rollback at any stage:

- **Halt**: pause the rollout at current percentage; new installs continue at the previous version.
- **Rollback**: the new version cannot be uninstalled (Play does not support that), but a hotfix can be uploaded and rolled out in the same way.

**Phased Release — App Store**

Apple's phased release: 1, 2, 5, 10, 20, 50, 100 percent over 7 days, automatic ramp. The team can pause manually if metrics regress. Phased release applies to automatic updates only — users who manually check the App Store and download see the new version immediately.

**Feature Flags**

LaunchDarkly is the enterprise leader: rich targeting rules (geography, app version, custom attributes), built-in A/B testing, percentage-based rollouts, server-side and client-side SDKs. Pricing scales with monthly active users.

Firebase Remote Config is the lightweight alternative: free for most usage, A/B testing built in, integrated with Firebase Analytics for funnel correlation. Less sophisticated than LaunchDarkly's targeting; sufficient for many programmes.

In-house systems: appropriate for organisations with the engineering capacity and the regulatory requirement to own the flag plane. The maintenance cost is real.

**Trunk-Based Development**

```
main: ──●──●──●──●──●──●──●  (deployable)
            │      │      │
       short feature branches (hours-days)
```

Every commit to main is a release candidate. New features are gated by feature flags; the flag is off in production until the team is ready. Long-lived feature branches accumulate merge conflicts and integration risk; trunk-based development eliminates this by integrating continuously.

**Semantic Versioning**

`major.minor.patch` user-visible. Build number monotonic across the entire app lifetime. CI increments build number; tag drives version. Pre-release suffixes (`-beta.1`, `-rc.2`) appear in TestFlight / Play Internal but never in production releases.

**Emergency Hotfix Process**

1. **Triage**: confirm user-impact severity. Cosmetic bugs do not warrant expedited review.
2. **Branch**: cut a hotfix branch from the production-tag commit; cherry-pick only the fix.
3. **Test**: smoke-test on the impacted scenario; run the full unit suite; deploy to internal testers for sanity check.
4. **Submit**: standard App Store and Play submission; request expedited review on App Store with clear justification.
5. **Rollout**: 100 percent rollout on confirmed fix, bypassing the standard staged-rollout discipline because the existing release is broken.
6. **Postmortem**: document root cause, gaps that allowed the bug to ship, process changes to prevent recurrence.

**Release Calendar**

| Period | Apple State | Google State | Action |
|---|---|---|---|
| November 15 – December 24 | Reduced review staff | Normal | Submit pre-holiday releases by November 10 |
| December 25 – January 3 | Full freeze | Normal | No releases; expedited reviews unlikely |
| January 4 – Q1 end | Backlog clearance | Normal | Expect longer review on first January submissions |
| Q2 – Q3 | Standard | Standard | Normal release cadence |
| August (annual) | Standard | Target SDK enforcement | Confirm Play target SDK compliance |

---

## Implementation Guide

### Step 1: Establish the feature-flag platform

LaunchDarkly, Firebase Remote Config, or in-house. Wrap the SDK in a thin abstraction so the platform is swappable.

### Step 2: Adopt trunk-based development

Branch-protection rules on main; PRs require passing CI; feature flags gate all in-progress features. No long-lived branches.

### Step 3: Configure staged rollout policy

Document the ramp schedule (1, 5, 20, 100 percent), the metrics watched (crash-free users, ANR, business KPIs), the thresholds that halt, the team that watches.

### Step 4: Wire semantic versioning automation

Tag on the release commit; CI reads the tag. Build number from CI run number. Release notes auto-generated from commits since the last tag.

### Step 5: Document the emergency-hotfix runbook

Step-by-step from triage to rollout. Expedited-review request templates pre-written. Quarterly tabletop exercises to keep the team fluent.

### Step 6: Calendar the freeze and key dates

Apple review freeze on the team calendar; Play target-SDK deadline; major OS releases (iOS 18 announcement, Android 16 stable). Plan releases around them.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Feature-flag platform integrated | Mobile Engineering Lead | Platform documented; SDK wrapped; flag taxonomy ratified | Required |
| Trunk-based development enforced | Engineering Manager | Branch protection on main; no long-lived branches; PR cycle time tracked | Required |
| Staged rollout policy documented | Release Manager | Ramp schedule, watched metrics, halt thresholds, on-call roster | Required |
| Versioning automation in place | Build Engineering | Tag-driven version; auto-generated release notes; build number from CI | Required |
| Emergency hotfix runbook | Mobile Architect + SRE | Step-by-step runbook; expedited-review templates; tabletop schedule | Required |
| Freeze calendar maintained | Release Manager | Apple freeze, Play target-SDK, OS-release dates on team calendar | Required |

---

## Security Considerations

- Feature flags can hide security-sensitive code paths in production; the flag is the control. Audit flag state per release; ensure the assumed-off flag is actually off.
- Emergency hotfix process should not bypass security review; the runbook includes a 30-minute security review even for expedited fixes.
- Rollback capability via phased release / staged rollout pause is a security control — a hotfix introducing a vulnerability can be halted before reaching most users.

---

## Performance Considerations

- Staged rollout's 24-48 hour soak per stage costs release cadence; acceptable trade-off for the regression catch.
- Feature flag SDK initialisation: under 500 ms cold start; cache the last-known-good config on disk for instant boot.
- LaunchDarkly streaming connection costs ~1 KB per minute idle, more on flag changes; budget bandwidth in offline-first contexts.

---

## Anti-Patterns to Avoid

### ⚠️ 100 Percent Rollout on Day One

A release ships to 100 percent of users immediately. A regression discovered hours later has already reached everyone; rollback is impossible (Play does not support rollback); hotfix takes 24+ hours. The fix is the staged-rollout discipline that catches the regression at 1 percent.

### ⚠️ Long-Lived Feature Branches Without Flags

A six-week feature branch accumulates merge conflicts; rebase becomes painful; the team batches the merge and discovers integration bugs at the worst time. The fix is trunk-based development with flags hiding the in-progress feature.

### ⚠️ Submitting in the Holiday Freeze

A release is submitted December 18; Apple reviewers are out; the review pends until January 6; the team's "holiday release" never lands. The fix is the published freeze calendar and the discipline to submit early.

### ⚠️ Emergency Hotfix Without Postmortem

The team expedites a fix, ships it, moves on. The next emergency has the same root cause. The fix is the mandatory postmortem; the process changes are real, not theatrical.

### ⚠️ Feature Flag Sprawl

Every developer creates flags; nobody cleans them up; the codebase has 200 flags, 150 of which are at 100 percent and untouched for a year. The fix is the quarterly flag-cleanup sprint and the lifecycle metadata (created date, owner, target removal date) on every flag.

---

## AI Augmentation Extensions

### AI-Assisted Release-Note Generation

LLM-based summarisation of commits since the last release produces user-facing release notes. The product manager reviews and refines. Notes ship to both stores plus the in-app "What's New" screen.

### AI-Assisted Rejection Analysis

When the App Store or Play Store rejects, the rejection text plus the relevant code is analysed by an LLM that classifies the likely cause and proposes the remediation. The team's response time to rejections compresses.

---

## References

1. [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) — *developer.apple.com*
2. [Google Play Developer Policy](https://support.google.com/googleplay/android-developer/topic/9858052) — *support.google.com*
3. [LaunchDarkly Mobile SDKs](https://docs.launchdarkly.com/sdk/client-side) — *docs.launchdarkly.com*
4. [Firebase Remote Config](https://firebase.google.com/docs/remote-config) — *firebase.google.com*
5. [Semantic Versioning 2.0](https://semver.org/) — *semver.org*
6. [Trunk-Based Development](https://trunkbaseddevelopment.com/) — *trunkbaseddevelopment.com*
7. [App Store Connect Phased Release](https://developer.apple.com/app-store/phased-release/) — *developer.apple.com*
8. [Google Play Staged Rollouts](https://support.google.com/googleplay/android-developer/answer/6346149) — *support.google.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/release-management/` | Aligned to App Store · Google Play · SemVer · LaunchDarkly*
