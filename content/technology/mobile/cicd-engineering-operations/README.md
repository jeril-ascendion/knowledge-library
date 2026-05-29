# CI/CD and Engineering Operations

> **Section:** `technology/mobile/cicd-engineering-operations/`
> **Alignment:** DORA Metrics | Fastlane | GitHub Actions | Google Play Console | App Store Connect
> **Audience:** DevOps Engineers · Mobile Engineers · Release Managers · Platform Engineers

The CI/CD pipeline for mobile is more complex than for web services due to: macOS-only iOS builds, binary code signing with certificates and provisioning profiles that expire, multi-day App Store review processes, and staged rollout mechanisms that differ between Google Play and the App Store. A mature mobile CI/CD pipeline automates every step from commit to user and reduces human error in the highest-risk operations — code signing and store submission.

## Overview

Fastlane combined with GitHub Actions is the Ascendion standard for mobile CI/CD (specified in ADR-MOB-003). Fastlane handles mobile-specific automation — code signing, building, testing, distribution, store submission. GitHub Actions orchestrates the workflow with matrix strategy for parallel Android and iOS builds.

## Pipeline Stages

### Stage 1: Validate (Every PR, ~8 minutes)
Lint (Detekt/SwiftLint), unit tests with coverage gate (Use Cases > 90%, ViewModels > 80%), snapshot test diff (zero pixel regressions), security scan (OWASP Dependency Check, GitLeaks). Runs on Linux runner for Android, macOS runner for iOS lint only (Swift compilation). Gate: block PR merge on any failure.

### Stage 2: Build (Merge to Main, ~15 minutes)
Android: Gradle assembleRelease with R8 full mode. iOS: Xcode Archive with Release configuration. Parallel matrix: Android on ubuntu-latest, iOS on macos-latest. Post-build: code signing (Android Keystore decode from base64 secret; iOS fastlane match download from encrypted Git repo).

### Stage 3: Test (Post-Build, ~10 minutes)
Integration tests with in-memory database. UI tests on emulator (Android) and simulator (iOS) for top 10 critical user journeys. Paparazzi/iOSSnapshotTestCase screenshot comparison. Runs after build to avoid blocking the main test loop.

### Stage 4: Distribute (Post-Test, ~5 minutes)
Internal distribution: Firebase App Distribution for Android and iOS (both platforms). TestFlight for iOS internal testing. Automatic distribution to QA team. Deployment note generated from git log since last distribution.

### Stage 5: QA Gate (Manual, ~24-48 hours)
GitHub Actions Environment Protection Rule on the Production environment requires QA Lead approval. QA tests on physical devices using the distributed build. No automated gate can replace human QA for the release candidate.

### Stage 6: Release (Post-QA, ~10 minutes)
Android: `fastlane supply` uploads AAB to Google Play internal track, promotes to staged rollout (1% → 5% → 20% → 100% over 7 days). iOS: `fastlane deliver` uploads IPA to App Store Connect, submits for review. Automated release note generation from CHANGELOG.md.

## Code Signing

iOS code signing is the most complex operational aspect of mobile CI/CD. fastlane Match solves it: all certificates and provisioning profiles stored encrypted in a dedicated Git repository. Every CI machine and developer clones them fresh using the Match passphrase (stored as `MATCH_PASSWORD` encrypted secret in GitHub). Certificate expiry handled automatically: Match regenerates certificates 30 days before expiry.

Android code signing: release Keystore encoded as base64 string stored as `KEYSTORE_B64` encrypted secret. CI decodes to a temporary file, configures Gradle `signingConfigs` block reading credentials from environment variables, deletes the temporary file after signing. Enrolled in Google Play App Signing — Google manages the distribution key, protecting against Keystore loss.

## Anti-Patterns to Avoid

> **⚠ Manual Code Signing** — Engineer manually downloading a Provisioning Profile from Apple Developer Portal, installing it, building locally, and uploading to TestFlight. Undocumented, unreproducible, fails when that engineer is unavailable.
> **CORRECT:** fastlane Match. All signing materials in the encrypted repository. Any CI machine or developer with the passphrase can sign and release. Documented, reproducible, auditable.

> **⚠ No QA Gate Before Production** — Pipeline automatically promotes to production after passing automated tests.
> **CORRECT:** GitHub Environment Protection Rule requiring QA Lead approval before any production release. Automated tests catch regressions; human QA catches usability, visual, and contextual issues automated tests miss.

## References

1. Fastlane Documentation. docs.fastlane.tools
2. GitHub Actions Documentation — Environments. docs.github.com/en/actions/deployment/targeting-different-environments
3. Google — Play Console Staged Rollouts. support.google.com/googleplay/android-developer/answer/6346149
4. Forsgren et al. — Accelerate. IT Revolution, 2018.
