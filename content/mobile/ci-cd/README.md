# Mobile CI / CD

Fastlane automating code signing and store submission, Match solving the "works on my Mac" problem, GitHub Actions matrix for parallel Android + iOS builds, self-hosted vs hosted macOS runners economics, Xcode Cloud's free tier, and semantic-versioning automation driven by Git tags.

**Section:** `mobile/` | **Subsection:** `ci-cd/`
**Alignment:** Fastlane Documentation | GitHub Actions for Mobile | Apple Developer Code Signing | Google Play App Signing
**Audience:** Mobile Engineers · Build Engineers · DevOps

---

## Overview

Mobile CI / CD is harder than web CI / CD for one reason: code signing. Android requires a Keystore file, password, and key alias; iOS requires a Developer Certificate, a Distribution Certificate, a Provisioning Profile per environment, and an entitlements file that matches the profile. Get any of them wrong and the build fails late in the pipeline with cryptic errors that consume engineer-hours in the wrong direction. Multiply that by parallel CI workers each needing a fresh signing identity, by App Store submission flows that require interactive App Store Connect API tokens, by Play Store rollout stages that require Google API service accounts — and the surface area is enormous.

Fastlane is the automation layer that absorbs almost all of this. `fastlane match` stores iOS certificates and profiles encrypted in a Git repository so every CI machine checks them out fresh. `fastlane gym` builds the IPA. `fastlane deliver` and `fastlane supply` submit to App Store and Play Store respectively. `fastlane pilot` manages TestFlight builds. The pipeline shrinks from "every machine is an island" to "the pipeline checks out signing material and runs the lane." Mobile programmes that adopt Fastlane do not relitigate the "code signing this week" conversation; mobile programmes that do not, do.

The architectural shift is not "we have CI." It is: **the mobile CI pipeline runs Android and iOS builds in parallel, uses Fastlane Match for iOS signing material checked into a private Git repo, uses Google Play App Signing for Android, signs every build with a per-environment identity, submits to TestFlight and Play Internal automatically on every main-branch merge, and versions semantically from Git tags — with build numbers from CI run number.**

---

## Core Principles

### 1. Fastlane Match for iOS signing material

Match generates certificates and provisioning profiles if they don't exist, downloads them if they do. All certificates in the team share one identity; conflicts vanish. The encrypted Git repo storage means a fresh CI machine can sign a build in 30 seconds.

### 2. Google Play App Signing for Android

Google holds the upload key; the team holds an upload-only key. If the upload key is lost, Google re-issues it; if the team's distribution key were lost, the app could not be updated. Always opt into Play App Signing.

### 3. Self-hosted macOS runner for iOS builds (sometimes)

GitHub-hosted macOS runners cost 10× the Linux runner rate. A Mac Mini in the office, registered as a self-hosted runner, pays for itself within months for typical mobile programmes. The trade-off is responsibility for runtime maintenance and security.

### 4. Build variants for environment-specific configuration

Android BuildConfig fields plus product flavours; iOS xcconfig files plus build configurations. Environment-specific values (API base URL, Sentry DSN, feature flag client key) are baked at build time; runtime environment switching is a developer-tooling feature, not a production capability.

### 5. Semantic versioning from Git tags

Version name from the most recent Git tag (`v4.2.1` → version 4.2.1). Build number from CI run number (monotonically increasing). The release-build PR creates the tag; the CI pipeline tags propagate to the App Store and Play Store automatically.

### 6. TestFlight and Play Internal on every main-branch merge

Every merge to `main` produces a build distributed to internal testers via TestFlight and Play Internal. The team dogfoods every commit. External rollout is a separate decision; internal distribution is automatic.

---

## Architecture Deep-Dive

**Fastlane Match for iOS Signing**

```ruby
# Fastfile
platform :ios do
  lane :beta do
    match(type: "appstore", readonly: is_ci)
    increment_build_number(build_number: ENV["CI_RUN_NUMBER"])
    gym(scheme: "Ascendion", export_method: "app-store")
    pilot(skip_waiting_for_build_processing: true)
  end
end
```

`match` checks out the encrypted Git repo, decrypts the certificates and profiles with the team's match password (stored as a CI secret), and installs them in the runner's keychain. `gym` builds the IPA. `pilot` uploads to TestFlight. The lane runs in under 15 minutes on a self-hosted M2 Mac Mini.

The Match repo (`certificates` repo) contains:

```
certs/
  distribution/<TeamID>.cer
  distribution/<TeamID>.p12
profiles/
  appstore/<bundle_id>.mobileprovision
```

Files are encrypted with a passphrase known only to the team; the encrypted Git repo is private; access is the same as for production secrets.

**Google Play App Signing**

Upload key in a Java Keystore stored as a Base64-encoded GitHub Actions secret. The Gradle signing config reads the secret and decodes it at build time:

```kotlin
// app/build.gradle.kts
signingConfigs {
    create("release") {
        val keystoreFile = File("$rootDir/keystore.jks")
        keystoreFile.writeBytes(Base64.getDecoder().decode(System.getenv("UPLOAD_KEYSTORE_B64")))
        storeFile = keystoreFile
        storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
        keyAlias = System.getenv("UPLOAD_KEY_ALIAS")
        keyPassword = System.getenv("UPLOAD_KEY_PASSWORD")
    }
}
```

The signed AAB is uploaded to Google Play via Fastlane Supply or the Google Play Developer API. Google's App Signing service re-signs the AAB with the production distribution key before delivery to devices; the upload-key compromise is recoverable.

**GitHub Actions Matrix**

```yaml
jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: bundle exec fastlane android beta
        env:
          UPLOAD_KEYSTORE_B64: ${{ secrets.UPLOAD_KEYSTORE_B64 }}

  ios:
    runs-on: self-hosted-mac-mini
    steps:
      - uses: actions/checkout@v4
      - run: bundle exec fastlane ios beta
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.APP_STORE_API_KEY }}
```

The matrix parallelises Android (Ubuntu, cheap) and iOS (self-hosted Mac Mini, faster than GitHub-hosted macOS). Total pipeline time is the maximum of the two legs, not the sum.

**Self-hosted vs GitHub-hosted macOS Runners**

GitHub-hosted macOS runner: $0.08 per minute (`large`), $0.16 (`xlarge`), $0.32 (`12-core`). At 200 build-minutes per day, that's $480 per month for the large runner.

Mac Mini M2 (16 GB RAM, 512 GB SSD): one-time hardware $1,200. Amortised over three years, $33 per month. Network and electricity negligible. Saves 90 percent of hosted runner cost; pays for itself in three months.

The trade-off is operational: the Mac Mini needs Xcode updates, macOS security updates, runner agent updates, occasional physical-presence intervention. Teams without an office-located machine or without DevOps capacity should stay on GitHub-hosted.

**Xcode Cloud**

Apple's native CI: 25 free compute hours per month per organisation, direct TestFlight integration, Webhooks for downstream pipelines, integrated dependency caching. Best fit for small teams with light CI needs. The free tier covers most indie projects; paid tiers are competitive with GitHub Actions for moderate use.

**Build Variants**

Android product flavours plus build types:

```kotlin
flavorDimensions += "environment"
productFlavors {
    create("dev") {
        dimension = "environment"
        buildConfigField("String", "API_BASE_URL", "\"https://api-dev.ascendion.com\"")
        applicationIdSuffix = ".dev"
    }
    create("prod") {
        dimension = "environment"
        buildConfigField("String", "API_BASE_URL", "\"https://api.ascendion.com\"")
    }
}
buildTypes {
    release { isMinifyEnabled = true; signingConfig = signingConfigs.getByName("release") }
}
```

`devDebug`, `devRelease`, `prodDebug`, `prodRelease` — four variants. Different application IDs allow installing dev and prod side-by-side.

iOS xcconfig files:

```
// Dev.xcconfig
API_BASE_URL = https:/\/api-dev.ascendion.com
PRODUCT_BUNDLE_IDENTIFIER = com.ascendion.app.dev
```

The build configuration reads the xcconfig; the runtime reads constants from `Info.plist` substitutions.

**Semantic Versioning Automation**

```yaml
- name: Get version from tag
  id: vers
  run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
- name: Build with version
  run: bundle exec fastlane ios release --version ${{ steps.vers.outputs.version }} --build ${{ github.run_number }}
```

A tagged push (`v4.2.1`) triggers the release pipeline. Version name 4.2.1; build number from CI run number. The CI run number is monotonic across the repository's lifetime — required for app-store ordering.

**Branching Strategy**

Trunk-based development: all work on short-lived feature branches; merges to `main` are atomic and trigger CI. No long-lived develop branch. Release tags are immutable; release branches exist only when emergency patch backporting requires it.

---

## Implementation Guide

### Step 1: Adopt Fastlane on both platforms

Generate `Fastfile` with iOS and Android lanes. Test each lane locally before adding to CI.

### Step 2: Set up Match for iOS signing

Create the encrypted certificates repo. Generate distribution certificates and provisioning profiles via `match init`. Document the match password storage in the team's secret management.

### Step 3: Enable Play App Signing for Android

Upload the existing distribution key to Play Console; opt into App Signing; receive the new upload key; update CI to use the upload key.

### Step 4: Configure CI matrix

GitHub Actions, GitLab CI, Bitrise — whichever the team uses. Android leg on Linux; iOS leg on macOS (self-hosted or hosted).

### Step 5: Automate TestFlight and Play Internal distribution

Every main-branch merge produces a TestFlight build and a Play Internal Testing track build. Internal testers receive immediately.

### Step 6: Wire semantic-version tagging

GitHub Release creation tags the commit. CI reads the tag, builds with the tag's version, submits to stores.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Fastlane lanes per platform | Build Engineering | iOS and Android lanes documented, tested locally and in CI | Required |
| Match repo provisioned | Build + Security | Encrypted repo; password in secrets manager; access controls audited | Required |
| Play App Signing enabled | Build Engineering | Google holds the distribution key; team holds upload key | Required |
| CI matrix configured | DevOps | Android and iOS build in parallel; pipeline duration documented | Required |
| Internal distribution on every merge | Build Engineering | TestFlight and Play Internal receive builds within 30 minutes of main-branch merge | Required |
| Semantic-version tagging in place | Engineering Lead | Tags drive version; build number from CI run number; release notes auto-generated | Required |

---

## Security Considerations

- Match passphrase, Keystore password, App Store Connect API key, Play Service Account JSON — all stored in CI secrets, never in the repo. Rotate the Match passphrase annually.
- Self-hosted runners are inside the organisation's network; isolate them on a dedicated VLAN, prevent direct internet ingress, and update runner agent on Microsoft's release cadence.
- Code-signing identity stored on the Mac Mini is encrypted at rest with FileVault; the Mac Mini is physically secured.
- Provisioning profiles list device UDIDs for development; do not commit dev profiles to the Match repo, only AdHoc and AppStore profiles.

---

## Performance Considerations

- Pipeline target: under 20 minutes for the full Android + iOS matrix. Gradle build cache shared across CI machines saves 40-60 percent of build time on warm builds.
- Feature modularisation enables parallel compilation, saving 30-50 percent build time on multi-core CI machines.
- iOS Xcode build cache (`COMPILER_INDEX_STORE_ENABLE = NO` in CI, `SWIFT_USE_INTEGRATED_DRIVER = YES` for parallelism) cuts incremental iOS build time substantially.
- Snapshot tests run separately from instrumented tests; parallelise by test class for further speed.
- Pipeline failure feedback: signed-out screenshot of build log emailed to the engineer on failure; preserves debugging cycle time.

---

## Anti-Patterns to Avoid

### ⚠️ Manual Code Signing on the Engineer's Mac

Each engineer downloads certificates and profiles manually; the CI machine fails to sign because its certificate is different. The fix is Fastlane Match — every machine, including engineers' Macs, runs `match` to get the same signing material.

### ⚠️ Storing the Production Keystore in the Repo

The Android Keystore is checked into Git "for convenience." The repo is forked or leaked; the keystore is exfiltrated; anyone can sign apps as the organisation. The fix is Base64-encoded secrets storage and Play App Signing recovery path.

### ⚠️ Long-lived Develop Branch

A `develop` branch sits between `main` and feature branches. Merges are batched; conflicts accumulate; the release process loses traceability. The fix is trunk-based development: all work merges to `main` behind feature flags.

### ⚠️ No Build-Variant Discipline

The team uses runtime environment switching via a debug menu hidden in the app. A release build accidentally ships with the menu visible. The fix is build-variant discipline: dev and prod are separate variants compiled separately; no runtime environment switching.

### ⚠️ Version Number from `app/build.gradle` Hardcode

An engineer forgets to bump the version; two releases ship with the same number; the Play Store rejects the second. The fix is version-from-Git-tag automation.

---

## AI Augmentation Extensions

### AI-Assisted CI Failure Triage

LLM-based log analysis on failed CI runs classifies the failure (signing, dependency resolution, test failure, infrastructure flake) and proposes the fix. Routine failures are resolved by the engineer without manual log spelunking.

### AI-Assisted Release Notes

Release notes are generated from the commits since the last release tag, summarised by an LLM into App Store / Play Store-friendly user-facing text. The product manager reviews and refines.

---

## References

1. [Fastlane Documentation](https://docs.fastlane.tools/) — *docs.fastlane.tools*
2. [Fastlane Match — Code Signing](https://docs.fastlane.tools/actions/match/) — *docs.fastlane.tools*
3. [Google Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — *support.google.com*
4. [GitHub Actions for Mobile](https://docs.github.com/en/actions) — *docs.github.com*
5. [Apple App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi) — *developer.apple.com*
6. [Xcode Cloud](https://developer.apple.com/xcode-cloud/) — *developer.apple.com*
7. [Trunk-Based Development](https://trunkbaseddevelopment.com/) — *trunkbaseddevelopment.com*
8. [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html) — *gradle.org*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/ci-cd/` | Aligned to Fastlane · GitHub Actions · Apple Code Signing · Play App Signing*
