# Mobile CI/CD Pipeline Tooling

> **ADR Reference:** `ADR-MOB-003`
> **Alignment:** DORA Metrics | Fastlane Open Source | GitHub Actions | Google Play Console | App Store Connect | OWASP MASVS Cryptography
> **Audience:** Mobile DevOps Engineers · Release Managers · Platform Engineers · Security Architects · QA Lead

Mobile CI/CD presents unique engineering challenges absent from backend pipelines: iOS builds require macOS infrastructure, code signing involves certificates and provisioning profiles that expire and must be shared across a team, both app stores have multi-day review processes, and staged rollouts require coordination between the deployment pipeline and store dashboards. This ADR eliminates the class of failures that arise from ad-hoc, undocumented mobile release processes.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-MOB-003 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice — Ascendion |
| Status | ACCEPTED |
| Domain | Mobile DevOps / Platform Engineering |
| ARB Approval | Required |

## Executive Summary

Fastlane combined with GitHub Actions is adopted as the standard mobile CI/CD pipeline for all Ascendion mobile projects. Fastlane manages code signing via fastlane Match, build automation, test execution, and store submission. GitHub Actions orchestrates the pipeline using matrix strategy to run Android and iOS builds in parallel. Xcode Cloud is adopted as a supplementary option for iOS-only projects. The pipeline enforces test coverage gates from ADR-MOB-001: Use Cases above 90%, ViewModels above 80%. All production releases require QA sign-off as a mandatory pipeline gate.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Code Signing Reliability | 25% | Signing failures are the most common iOS release delay cause |
| 2 | Quality Gate Enforcement | 22% | Test coverage and snapshot gates must be automated |
| 3 | Pipeline Speed | 18% | Target under 30 minutes total. Slow pipelines are bypassed |
| 4 | Automation Coverage | 15% | Build, test, sign, distribute, submit — zero manual steps |
| 5 | Cost | 12% | macOS runner cost is 10× Linux. Minimise macOS minutes |
| 6 | Maintainability | 8% | Pipeline as code, versioned in Git, operable by any engineer |

## Considered Options

### Option A — Fastlane + GitHub Actions (ADOPTED)
Weighted score: **4.81 / 5.0**. fastlane Match solves code signing at the root — all certificates stored encrypted in a dedicated Git repo, every CI machine and developer clones fresh. GitHub Actions matrix runs Android (Linux) and iOS (macOS) in parallel, halving total pipeline time.

### Option B — Bitrise
Weighted score: 3.46 / 5.0 — DISMISSED. Cost at scale ($450-900/month) exceeds GitHub Actions with self-hosted macOS runner. Vendor lock-in on pipeline configuration prevents migration.

### Option C — Xcode Cloud (iOS supplement)
Apple-native CI. 25 free compute hours/month. Direct TestFlight integration. iOS/macOS only. Adopted as supplementary for iOS-only projects — cannot replace Fastlane for Android.

### Option D — Codemagic
Weighted score: 3.72 / 5.0 — DISMISSED. Valid for Flutter projects but adds separate vendor dependency. GitHub Actions + Fastlane provides equivalent capability at lower per-project cost at Ascendion engagement volume.

## Pipeline Architecture

| Stage | Trigger | Android | iOS | Time |
|---|---|---|---|---|
| Validate | Every PR | Detekt lint, unit tests (90% gate), snapshot diff, security scan | SwiftLint, unit tests (90% gate), snapshot diff | ~8 min |
| Build | Merge to main | Gradle assembleRelease, R8 full mode | Xcode Archive, Release config | ~15 min |
| Sign | Post-build | Keystore decode from base64 secret | fastlane match, appstore profile | ~3 min |
| Distribute | Post-sign | Firebase App Distribution, Play internal track | TestFlight internal | ~5 min |
| QA Gate | Manual | GitHub Environment protection rule | GitHub Environment protection rule | 24-48hr |
| Release | Post-QA | Play staged rollout 1%→5%→20%→100% | App Store review submission | ~10 min |

## Code Signing Standards

### iOS — fastlane Match (Mandatory)
All certificates and provisioning profiles stored encrypted in a dedicated private Git repository. Every CI machine and developer clones fresh using MATCH_PASSWORD encrypted secret. Certificate rotation: Match regenerates automatically 30 days before expiry. Eliminates the certificate-locked-to-one-Mac failure mode permanently.

### Android — Keystore via GitHub Secrets (Mandatory)
Release Keystore encoded as base64 stored as KEYSTORE_B64 encrypted secret. CI decodes to temporary file, configures Gradle signingConfigs, deletes after signing. Enrolled in Google Play App Signing — Google manages distribution key.

## Mandatory Quality Gates

| Gate | Tool | Threshold | Failure Action |
|---|---|---|---|
| Use Case Coverage | JaCoCo / Xcode Coverage | > 90% | Block PR merge |
| ViewModel Coverage | JaCoCo / Xcode Coverage | > 80% | Block PR merge |
| Snapshot Test Diff | Paparazzi / iOSSnapshot | Zero pixel regressions | Block PR merge |
| Lint and Static Analysis | Detekt / SwiftLint | Zero error-level violations | Block PR merge |
| Dependency CVE Scan | OWASP Dependency Check | No P1/P2 CVEs | Block merge, alert SA |
| QA Sign-off | GitHub Environment Protection | QA Lead approval | Block production deploy |

## Anti-Patterns to Avoid

### 1. Manual Code Signing
Engineer manually downloading provisioning profiles, building locally, uploading to TestFlight. Undocumented, unreproducible, fails when that engineer is unavailable.

**CORRECT:** fastlane Match. All signing materials in encrypted repository. Any CI machine or developer with the passphrase can sign and release.

### 2. No QA Gate Before Production
Pipeline automatically promotes to production after passing automated tests. Automated tests catch regressions; human QA catches usability and visual issues automated tests miss.

**CORRECT:** GitHub Environment Protection Rule requiring QA Lead approval before any production release.

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-001 | Mobile Architecture Pattern | Test coverage gates reference standards from this ADR |
| ADR-MOB-002 | Mobile Platform Selection | Platform determines Android vs iOS pipeline configuration |
| ADR-SEC-011 | Mobile Security Controls | Dependency CVE scanning gate references security standards |

## References

1. Fastlane Documentation. docs.fastlane.tools
2. GitHub Actions — Environments. docs.github.com/en/actions/deployment
3. Google — Play Console Staged Rollouts. support.google.com/googleplay/android-developer
4. Forsgren et al. — Accelerate. IT Revolution, 2018.
5. OWASP — Dependency Check. owasp.org/www-project-dependency-check
