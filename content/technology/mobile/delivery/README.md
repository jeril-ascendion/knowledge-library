# DevOps, CI/CD & Release Management

> **Section:** `technology/mobile/delivery/`
> **Alignment:** DORA Metrics | Google Play Console | App Store Connect | OWASP MASVS Cryptography | Fastlane Open Source
> **Audience:** Mobile DevOps Engineers · Release Managers · Platform Engineers · SREs

The mobile delivery pipeline is where most architectural decisions cash out as either compounding velocity or compounding pain. The discipline of code signing, automated testing, and staged rollout decides how fast the team can ship and how fast they can recover.

---

## Overview

This reference covers the mobile delivery pipeline end to end: CI/CD design, code signing, Fastlane automation, feature flags, and trunk-based development. It defines the quality gates and staged-rollout discipline that let teams ship quickly and recover even faster.

## Mobile CI/CD Pipeline Design

The complete pipeline from `git push` to the App Store:

**Branch push triggers lint, unit tests, snapshot tests** in under three minutes. The developer's PR build cycle stays tight; flaky tests trigger immediate triage. **Merge to main triggers a full build** — Android Gradle build on a Linux runner, iOS Xcode build on a macOS runner, **in parallel** through GitHub Actions matrix strategy. The two legs run independently; the total pipeline time is the maximum of the two, not the sum.

**Full test suite** including integration tests on JVM (Robolectric for Android, in-process XCTest for iOS) and instrumented tests on emulator. **Code signing** through Fastlane Match (iOS) and the Play upload-signing key (Android). **Internal distribution** to QA via Firebase App Distribution or TestFlight on every main-branch merge — the team dogfoods every commit. **Manual QA sign-off gate** for release candidates. **Staged production release** via Play Console staged rollout or App Store phased release.

**DORA elite performance benchmarks** mapped to mobile: **deployment frequency** multiple per week (mobile rarely matches web's per-day cadence — store review windows are the cap); **lead time for changes** under one day from merge to internal testers, one to seven days to public production; **change failure rate** under five percent of releases requiring hotfix; **time to restore service** under one hour for hotfixable bugs, capped by App Store expedited review in practice.

GitHub Actions matrix strategy cuts a sequential 45-minute pipeline to a parallel 25-minute pipeline. Self-hosted macOS runners on a Mac Mini in the office pay back the hardware cost in three to four months by avoiding the 10x premium GitHub charges for hosted macOS minutes.

---

## Code Signing

**iOS code signing complexity** explained for the team that has not lived it. Two artefacts work together: a **Certificate** proves developer identity (a development certificate for Xcode runs on the developer's Mac; a distribution certificate signs builds for TestFlight and the App Store); a **Provisioning Profile** binds a certificate to one or more App IDs and either a list of device UDIDs (for development and ad-hoc) or a distribution method (TestFlight, App Store).

The pain point is team sharing. Without `fastlane match`, each developer's Mac has a different certificate; CI machines fight to obtain certificates; "works on my Mac" is the daily complaint. **`fastlane match`** solves this by storing all certificates and provisioning profiles encrypted (AES-256) in a dedicated private Git repository or an S3 bucket. Every CI machine and every developer clones them fresh with a shared passphrase (stored in CI secrets, never in the repo). Everyone shares the same signing identity; conflicts vanish.

**Match modes**: `development` for device testing during build, `adhoc` for direct device distribution outside the App Store, `appstore` for TestFlight and App Store submissions. **Nuke mode** (`match nuke distribution`) resets all certificates and profiles when they expire or are compromised — required cleanup before regenerating.

**Android code signing** is simpler. A Keystore file contains a private key and a self-signed certificate; you signed the first release with it; you keep signing every subsequent release with the same key. **In CI**: export the Keystore as base64, store it as a GitHub Actions encrypted secret, decode to a temp file at build time, configure the Gradle `signingConfigs` block to read the credentials from environment variables, delete the temp file after signing completes.

**Google Play App Signing** is the protection layer. Google manages the **distribution key** that actually signs the binary delivered to devices; you only manage the **upload key** that authenticates uploads to Play Console. If your upload key is lost or compromised, Google can re-issue it; if you owned the distribution key and lost it, your app could never be updated again. Always opt into Play App Signing.

---

## Fastlane Automation

**Fastlane** is the automation layer that connects mobile build and release tooling end-to-end. `Appfile` declares per-app identity (`app_identifier`, `apple_id` for iOS; `package_name` for Android). `Fastfile` defines lanes as reusable Ruby automation scripts.

**Core lanes** every team should have:

- **`test`** — runs unit tests and UI tests; the lane CI runs on every PR.
- **`beta`** — builds the release-mode IPA / AAB and uploads to TestFlight or Firebase App Distribution; runs on every main-branch merge.
- **`release`** — builds, signs, and submits to the App Store or Play Store; runs on a tagged release commit.

**Key Fastlane actions**:

- **`gym`** builds the IPA via `xcodebuild` with the right export method (`app-store`, `ad-hoc`, `development`, `enterprise`).
- **`deliver`** uploads to App Store Connect, manages screenshots and metadata, and submits for review.
- **`supply`** uploads the AAB to Google Play, manages tracks (`internal`, `alpha`, `beta`, `production`), and supports staged rollout percentages.
- **`pilot`** manages TestFlight groups and tester expiry, adds external testers, and handles the build-processing wait.

The lane runs in under fifteen minutes on a self-hosted M2 Mac Mini and removes the entire "did someone update the screenshots manually" class of incidents.

---

## Feature Flags and Trunk-Based Development

**Trunk-based development** is the discipline that makes mobile CD work. All code merged to `main` with feature flags hiding in-progress work. No long-lived feature branches accumulating merge conflicts. Every commit to main is a potential release candidate.

**Feature flag providers**:

- **LaunchDarkly** for enterprise with rich targeting rules — percentage rollouts, user-attribute targeting (geography, app version, plan tier), kill switches that halt a misbehaving feature without a re-release.
- **Firebase Remote Config** for lightweight flag management with built-in A/B testing integrated with Firebase Analytics for funnel correlation. Free for most usage; sufficient for many programmes.
- **Statsig** for feature flags plus product analytics in one platform — appealing when the team wants flag and experiment data in one place.

**All new features behind flags**. All experiments behind flags. All performance-risky changes behind flags. The flag naming convention: `feature_<JIRA-ID>_<description>` — the JIRA ID ties the flag to its tracking issue, the description survives JIRA migrations.

**Flag cleanup discipline**: remove the flag and the dead code within two sprints of 100 percent rollout. Without cleanup, the codebase accumulates dozens of stale flags within a year, the cognitive cost compounds, and the next on-call wonders what the flag still gates.

---

## Observability and Monitoring

**Firebase Crashlytics**. **Crash-free users rate** is the primary SLA metric — target above 99.5 percent on the highest-traffic release. **ANR rate** below 0.2 percent. Custom keys for context: hashed user ID (never raw), current feature-flag state, last screen visited, current session duration. Breadcrumb logging for the user action trail before the crash. Non-fatal exception recording for handled errors worth monitoring.

The symbol-upload step in CI is non-negotiable — without it, every stack trace is obfuscated by R8 and the team chases ghosts. The Crashlytics Gradle plugin uploads mapping files automatically; iOS Bitcode symbol upload does the equivalent.

**Firebase Performance Monitoring**. Automatic HTTP request timing capturing DNS + connect + SSL + request + response milliseconds per call, aggregated per endpoint. Custom traces around business-critical journeys (`checkout`, `login`, `content_load`). Screen-rendering metrics tracking slow frames (over 16 ms) and frozen frames (over 700 ms).

**Datadog Mobile APM** for enterprise: distributed traces connecting the mobile span to the backend span through `traceparent` header propagation, enabling attribution of slow API responses to specific backend services.

**Session replay** through **FullStory** or **Heap** for debugging the bug nobody could reproduce. **PII masking is mandatory** and configured at integration time: every `TextField` defaults to masked; sensitive display values (account balance, transaction amount, personal name) explicitly marked with `FS.mask` or the equivalent; network request URLs scrubbed of query parameters. A misconfigured session replay is a GDPR notification waiting to happen.

**MetricKit on iOS**. The system delivers diagnostic reports every 24 hours containing histograms for app launch time, hang duration, CPU exception count, disk write exceptions. Subscribe via `MXMetricManagerSubscriber` and ingest into the team's observability stack as the iOS-side complement to Crashlytics.

---

## App Store Governance

**App Store review**. **Standard review** 24-48 hours from submission to "Pending Developer Release" or "Rejected". **Expedited review** 4-8 hours for critical bug fixes with documented user-impact justification. **Common rejection reasons**: privacy nutrition label mismatches (the actual data collection differs from the labels — most often caused by a third-party SDK collecting telemetry not declared); missing required functionality (subscription terms, account-deletion flow); Guideline 4.3 spam (duplicating existing App Store functionality with insufficient differentiation); metadata violations (screenshots showing features not in the build).

**Holiday freeze**. App Store review staff are reduced from November 15 through January 3 — submit your pre-Christmas release by November 8 and expect early-January submissions to face backlog. Plan the calendar accordingly.

**Google Play**. Updates review in 1-3 days, sometimes hours for trusted publishers. **Staged rollout** 1 percent → 5 percent → 20 percent → 100 percent over several days with **halt-and-rollback** capability — the team pauses or rolls back if ANR rate or crash-free-users rate regresses. Google has no formal expedited review; the **emergency rollout track** allows republishing a known-good build to bypass review for previously-shipped variants.

**Emergency hotfix process**. Documented runbook the on-call uses under pressure: triage (confirm user-impact severity; cosmetic bugs do not warrant expedited review), branch (cut from the production-tag commit, cherry-pick only the fix), test (smoke-test plus full unit suite), submit (App Store with expedited request and a clear justification field; Play emergency rollout track), rollout (100 percent immediately, bypassing staged rollout because the existing release is broken), postmortem (root cause, gaps that allowed the bug to ship, process changes to prevent recurrence).

**Versioning**. Semantic version (`major.minor.patch`) for the user-visible version string. Monotonically increasing integer build number for store ordering — automatically derived from the CI run number to guarantee monotonicity. Tag-driven version naming: a `git tag v4.2.1` triggers the release pipeline; the tag drives the version; the CI run number drives the build number.

---

## Anti-Patterns

### 1. Manual Code Signing on Each Mac

Engineers download certificates manually; the CI machine fails to sign because its certificate is different.

**CORRECT:** The fix is Fastlane Match — every machine, including engineers' Macs, runs `match` to get the same signing identity.

### 2. Storing the Production Keystore in the Repo

The Android Keystore is checked in "for convenience." The repo is forked or leaked; the Keystore is exfiltrated; anyone can sign apps as the organisation.

**CORRECT:** The fix is base64-encoded GitHub Actions secret plus Play App Signing recovery path.

### 3. Long-Lived Develop Branch

A `develop` branch sits between `main` and feature branches; merges batch; conflicts accumulate; release traceability is lost.

**CORRECT:** The fix is trunk-based development with feature flags.

### 4. 100 Percent Rollout on Day One

The release ships to all users immediately. A regression discovered hours later has already reached everyone.

**CORRECT:** The fix is the staged-rollout discipline.

### 5. Symbol Upload Skipped

Crashlytics is integrated but symbol upload is not part of CI. Stack traces are obfuscated; the team cannot triage crashes.

**CORRECT:** The fix is the CI step that uploads symbols on every release build and the gate that fails the build if upload fails.

---

## References

1. [Fastlane Documentation](https://docs.fastlane.tools/) — *docs.fastlane.tools*
2. [Fastlane Match](https://docs.fastlane.tools/actions/match/) — *docs.fastlane.tools*
3. [Google Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — *support.google.com*
4. [LaunchDarkly Mobile SDKs](https://docs.launchdarkly.com/sdk/client-side) — *docs.launchdarkly.com*
5. [Firebase Crashlytics](https://firebase.google.com/docs/crashlytics) — *firebase.google.com*
6. [DORA Metrics](https://dora.dev/) — *dora.dev*
7. [App Store Phased Release](https://developer.apple.com/app-store/phased-release/) — *developer.apple.com*
8. [Trunk-Based Development](https://trunkbaseddevelopment.com/) — *trunkbaseddevelopment.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/delivery/` | Aligned to DORA · Google Play · App Store Connect · Fastlane · OWASP MASVS*
