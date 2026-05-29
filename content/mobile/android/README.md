# Android Architecture

Modern Android Development on Kotlin and Jetpack Compose — feature-modularised Clean Architecture, StateFlow-driven UI, Hilt-scoped dependency injection, Room with encrypted storage, and Baseline Profiles delivering measured cold-start wins.

**Section:** `mobile/` | **Subsection:** `android/`
**Alignment:** Google MAD (Modern Android Development) | Android Architecture Guidelines | OWASP MASVS-L2 | NIST SP 800-163
**Audience:** Android Engineers · Mobile Architects · Technical Leads

---

## Overview

Modern Android Development (MAD) is Google's current architectural stance, and as of 2026 the stance has stabilised: Jetpack Compose for UI, Kotlin Coroutines and Flow for asynchrony, Hilt for dependency injection, Room for persistence, Kotlin Serialization for JSON, Gradle Kotlin DSL for build configuration, and version catalogs for dependency hygiene. The XML layout era is over for new code; the LiveData era is over for new code; the AsyncTask era ended six years ago. Programmes shipping Android in 2026 against XML, LiveData, or AsyncTask are programmes paying compounding interest on technical debt.

The architectural shape that has emerged from this consensus is feature-modularised Clean Architecture. Each Gradle module is a feature (`feature-login`, `feature-account`, `feature-transfer`) containing its own Composable screens, ViewModel, domain use cases, and data sources. The `app` module composes features and wires the navigation graph. A `core` module group provides shared building blocks — `core-network`, `core-database`, `core-design-system`, `core-common`. The compilation graph parallelises across modules; the navigation graph is type-safe; the architecture supports Gradle's build cache and configuration cache for double-digit-percentage build-time reductions on warm builds.

The architectural shift is not "we adopted Compose." It is: **the Android codebase is feature-modular, state-driven through StateFlow with a sealed UiState class, scoped through Hilt with explicit lifecycle annotations, persisted through Room with encrypted preferences for secrets, and measured through Baseline Profiles and Macrobenchmark — and every one of those choices is named in writing because the next architecture argument will be against an engineer who joined yesterday.**

---

## Core Principles

### 1. Compose-first, ViewModel as state-owner, sealed UiState as contract

The screen is a `@Composable` function reading a single `StateFlow<UiState>` exposed by the ViewModel. `UiState` is a sealed class (`Loading`, `Content(data)`, `Error(message, retry)`, `Empty`). The Composable never reaches into the ViewModel beyond `collectAsStateWithLifecycle()`, and the ViewModel never imports a Composable, Activity, Fragment, or anything from `android.view`. The state contract is the integration boundary; everything else is an implementation detail.

### 2. Feature modules over layered modules

Modules are organised by feature (`feature-account`, `feature-transfer`), not by layer (`ui`, `domain`, `data`). Inside a feature module, layers exist as packages, but a feature is a deployable, testable, self-contained unit. The `app` module is a thin composition root that wires features into a navigation graph. The Android Architecture Sample (Now in Android, NIA) is the reference implementation Google maintains.

### 3. Hilt for DI with explicit scoping

Hilt provides Application, Activity, ViewModel, and ServiceComponent scopes. Scopes are explicit and intentional: a singleton-scoped `Retrofit` instance, a ViewModelScoped repository per screen, an ActivityRetainedScope for configuration-change-surviving state. Manual DI containers (Koin's runtime resolution) trade compile-time safety for setup speed; on apps shipping for five-plus years that trade-off rarely pays.

### 4. Coroutines with dispatcher selection that names intent

`Dispatchers.IO` for network and disk. `Dispatchers.Default` for CPU-bound work. `Dispatchers.Main` only for UI updates. Never `withContext(Dispatchers.IO)` defensively around code that is already off the main thread — every dispatcher switch is a thread-pool transition with measurable overhead. The structured concurrency contract (parent scope cancels children) is non-negotiable; every coroutine launched outside a `viewModelScope` or `lifecycleScope` is a leak waiting to happen.

### 5. Room as the local source of truth, encrypted secrets via Keystore

Room owns local persistence with type-safe queries, migrations, and Flow-based observation. EncryptedSharedPreferences and the Android Keystore handle credentials, refresh tokens, and biometric-protected keys. The `MasterKey` is hardware-backed where the device supports StrongBox; software-backed Keystore on lower-tier devices is still the right answer over rolling your own.

### 6. Baseline Profiles as a release artefact

A Baseline Profile is a list of methods that ART (the Android Runtime) compiles ahead of time at install. Google measured a 30 percent cold-start improvement on the Now in Android app from Baseline Profile generation alone. Generating one per release with Jetpack Macrobenchmark and shipping it inside the app bundle is no longer optional on apps with cold-start SLAs.

---

## Architecture Deep-Dive

A canonical feature module looks like this:

```
feature-account/
├── src/main/kotlin/com/ascendion/app/account/
│   ├── ui/
│   │   ├── AccountScreen.kt          (@Composable)
│   │   ├── AccountViewModel.kt
│   │   └── AccountUiState.kt          (sealed class)
│   ├── domain/
│   │   ├── GetAccountUseCase.kt
│   │   └── RefreshAccountUseCase.kt
│   ├── data/
│   │   ├── AccountRepository.kt
│   │   ├── AccountRemoteDataSource.kt
│   │   └── AccountLocalDataSource.kt
│   └── di/
│       └── AccountModule.kt           (Hilt bindings)
└── build.gradle.kts                   (Kotlin DSL)
```

The package convention `com.<org>.app.<feature>.<layer>` makes dependency rules enforceable through Kotlin's `internal` modifier and through Android's `:feature-account` Gradle module boundary — `feature-account` cannot accidentally import from `feature-transfer` because Gradle has no declared dependency between them.

The Compose UI layer reads state and emits events:

```kotlin
@Composable
fun AccountScreen(viewModel: AccountViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    when (val state = uiState) {
        is AccountUiState.Loading -> LoadingIndicator()
        is AccountUiState.Content -> AccountContent(state.account, onRefresh = viewModel::onRefresh)
        is AccountUiState.Error   -> ErrorView(state.message, onRetry = viewModel::onRetry)
    }
}
```

The ViewModel exposes immutable `StateFlow`, holds a `MutableStateFlow` privately, and processes events through coroutines launched in `viewModelScope`:

```kotlin
@HiltViewModel
class AccountViewModel @Inject constructor(
    private val getAccount: GetAccountUseCase,
) : ViewModel() {
    private val _uiState = MutableStateFlow<AccountUiState>(AccountUiState.Loading)
    val uiState: StateFlow<AccountUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            getAccount().collect { result -> _uiState.value = result.toUiState() }
        }
    }
}
```

The use case is a single-responsibility callable; the repository decides cache vs network; the data sources speak Retrofit and Room. The dependency rule (Clean Architecture's "source code dependencies point only inward") is enforced by package convention plus Konsist tests in CI: any `data` import from `ui` fails the build.

KSP (Kotlin Symbol Processing) replaces KAPT for annotation processing in 2026. Hilt, Room, and Moshi all support KSP; the build speed improvement is 30-50 percent on cold builds. Kotlin Serialization is preferred over Gson and Moshi because it is compile-time safe (no reflection, smaller R8 output) and is first-party Kotlin tooling.

Baseline Profile generation runs in CI through Macrobenchmark:

```kotlin
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(packageName = "com.ascendion.app") {
        pressHome()
        startActivityAndWait()
        // Exercise critical paths: scroll feed, open account detail.
    }
}
```

The generated `baseline-prof.txt` is committed and packaged with the app bundle. The Play Store distributes it as part of the install; ART compiles the listed methods AOT; cold start drops measurably on every device that runs the install. Google measured 30 percent on NIA, 22 percent on Reddit's app, 25 percent on Lyft's app — the variance reflects each app's specific cold-start path.

Android Keystore generates and stores keys in hardware (TEE on most devices, StrongBox on newer Pixel and Samsung devices). The `setUserAuthenticationRequired(true)` flag on key generation requires biometric or device-credential unlock before the key can be used to encrypt or decrypt — useful for refresh-token storage where unlock-bound material is desirable.

What top Android programmes ship:

- **Now in Android (NIA)**: Google's reference open-source app. Feature modules, Compose, Hilt, Room, Macrobenchmark, Baseline Profiles, version catalogs. Every Android programme should start by reading NIA's `build.gradle.kts` files.
- **Tivi (by Chris Banes, ex-Google)**: Kotlin Multiplatform with shared business logic, Compose Multiplatform on Android and desktop. Reference for KMP migration paths.
- **Chrome for Android**: Native C++ engine, Java/Kotlin UI, custom build system. Reference for legacy-codebase modernisation patterns.

---

## Implementation Guide

### Step 1: Establish the module graph and dependency rules

Define `app`, `feature-*`, and `core-*` modules. Document the dependency rules: `app` depends on features; features depend on `core-*`; `core-*` modules depend only on each other where named. Enforce with Konsist or a CI Gradle task that fails the build on illegal dependencies.

### Step 2: Adopt the version catalog

Move every dependency to `gradle/libs.versions.toml`. Centralise Compose BOM, Kotlin version, Hilt version. The version catalog plus Renovate bot keeps the project current with minimal manual lifting.

### Step 3: Wire Hilt across the module graph

Annotate the `Application` class with `@HiltAndroidApp`. Annotate each entry-point Activity with `@AndroidEntryPoint`. Provide `@Module @InstallIn(...)` bindings in each feature's `di/` package. Use `@ViewModelScoped` for ViewModel-lifetime dependencies.

### Step 4: Implement the canonical screen template

One screen, one ViewModel, one sealed UiState, Compose Preview parameterised over each UiState variant. Every screen in the codebase follows the template. Variance from the template is reviewed in code review with explicit justification.

### Step 5: Set up Macrobenchmark and Baseline Profile generation in CI

A dedicated Macrobenchmark module runs nightly on a Firebase Test Lab device matrix. The Baseline Profile is generated, diffed against committed, and a PR is auto-opened if the diff is non-trivial.

### Step 6: Configure R8 with explicit `keep` rules

The default R8 minify and shrinking is correct for most apps. Custom `keep` rules are needed for libraries that use reflection (Retrofit interfaces, Room entities not annotated correctly, Hilt-generated code is keep-protected automatically). Test release builds in CI; a release build that crashes only after R8 shrinking is the most expensive bug to discover late.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Module graph documented | Mobile Architect | `app`, `feature-*`, `core-*` named; dependency rules in `README.md` and enforced in CI | Required |
| Version catalog established | Build Engineering | All dependencies in `libs.versions.toml`; no hardcoded versions in `build.gradle.kts` | Required |
| Screen template ratified | Mobile Architect | Canonical Compose + StateFlow + sealed UiState pattern documented and exemplified | Required |
| Baseline Profile in CI | Build Engineering | Macrobenchmark module runs nightly; profile diff tracked per release | Required |
| Keystore strategy approved | Security + Mobile Architect | Hardware-backed key generation, `setUserAuthenticationRequired` policy named per key | Required |
| R8 release-build verified | QA + Build | Release APK/AAB smoke-tested on Firebase Test Lab matrix before every store submission | Required |

---

## Security Considerations

- Store credentials and refresh tokens in EncryptedSharedPreferences backed by a hardware-bound `MasterKey`; never in regular `SharedPreferences`, never in Room without an encrypted SQLCipher build.
- `android:allowBackup="false"` and `android:fullBackupContent` rules in the manifest prevent ADB backup from exfiltrating app data on rooted or developer-mode devices.
- `android:debuggable="false"` and `isMinifyEnabled = true` in the release build type. R8 obfuscation increases the cost of reverse engineering; it does not prevent it — pair with Play Integrity attestation for server-side trust decisions.
- Network Security Config (`res/xml/network_security_config.xml`) enforces TLS 1.3 minimum, pins SPKI hashes for known production endpoints, and disables cleartext traffic globally. The config is platform-enforced; the app cannot accidentally regress to cleartext.
- Disable WebView's JavaScript-to-native bridge unless required; if required, restrict the bridge to the smallest possible API surface and validate every parameter on the native side.

---

## Performance Considerations

- Cold start under 2 seconds on a Pixel 6a (median 2023 mid-range device). Measure with `adb shell am start -W` and the App Startup library's reported metrics.
- Frame time under 16.67 ms (60 fps) on scrolling lists; under 11.11 ms (90 fps) on premium devices. Compose `LazyColumn` plus `key()` plus `derivedStateOf` for derived state plus `remember` for expensive calculations is the standard tuning quartet.
- StrictMode enabled in debug with `penaltyDeath()` on `detectDiskReadsOnMainThread()`, `detectDiskWritesOnMainThread()`, and `detectNetworkOnMainThread()`. Debug builds crash the moment an engineer accidentally puts disk or network on the main thread.
- Baseline Profile generation in every release; profile coverage above 90 percent of cold-start methods measured by Macrobenchmark.
- R8 full mode (`-allowaccessmodification`) shrinks the release APK by an additional 10-15 percent on average and removes more dead code than the default mode.

---

## Anti-Patterns to Avoid

### ⚠️ The Massive ViewModel

The ViewModel grows to 1,000 lines because the screen has six tabs and the team kept adding state to one class. Recomposition becomes unpredictable; testing requires mocking ten dependencies. The fix is to split per logical sub-screen, share state through a parent ViewModel only where genuinely shared, and use sealed UiState to make screen-state explicit.

### ⚠️ Coroutines Launched Outside Structured Scopes

Engineers reach for `GlobalScope.launch` because it is convenient. The coroutine outlives its caller, leaks the calling object, and writes to a UI that is no longer visible. The fix is the lint rule that fails the build on `GlobalScope` references and the code-review discipline that catches non-structured launches.

### ⚠️ Dispatchers.IO Around Already-Background Code

A defensive `withContext(Dispatchers.IO)` wraps a Repository call that is already invoked from a coroutine on `Dispatchers.IO`. Every defensive switch costs a thread-pool dispatch. The fix is naming the dispatcher contract at the public interface — repositories declare "I block; call me from `Dispatchers.IO`" — and never adding `withContext` defensively inside.

### ⚠️ XML Layouts in 2026 New Code

New screens are written in XML because "the team knows XML." The team is paying compounded interest on tooling that Google has effectively deprecated for new code. The fix is the convention that new screens use Compose; existing XML is migrated opportunistically as screens are rewritten, never on an island migration project that delivers no user value.

### ⚠️ Logging Secrets to Logcat

Refresh tokens, session IDs, and PII end up in `Log.d()` calls that ship in release builds. Logcat is readable by any app with the `READ_LOGS` permission on legacy devices, and crash reports often capture the buffer. The fix is a logger abstraction that strips secrets in release, lint rules that flag `Log.*` calls outside the abstraction, and a CI scan that fails the build on PII patterns in logs.

---

## AI Augmentation Extensions

### AI-Assisted Compose Migration

LLM coding assistants (Cursor, Claude Code, GitHub Copilot) can mechanically translate XML layouts to Compose with high accuracy for 70-80 percent of screens; the remaining 20-30 percent require human review for animation, accessibility, and gesture handling. Studio Bot (Gemini in Android Studio) provides in-IDE Compose suggestions that match the local codebase's style guide.

### AI-Assisted Baseline Profile Tuning

Profile generation runs against synthetic user journeys produced by Maestro or Espresso scripts. AI assistants generate candidate user journeys from the screen graph, surfacing journeys the team has not yet covered. The profile coverage metric improves measurably with AI-generated journey expansion.

---

## References

1. [Now in Android — Google's reference app](https://github.com/android/nowinandroid) — *github.com/android*
2. [Modern Android Development](https://developer.android.com/modern-android-development) — *developer.android.com*
3. [Guide to App Architecture](https://developer.android.com/topic/architecture) — *developer.android.com*
4. [Jetpack Compose Performance](https://developer.android.com/jetpack/compose/performance) — *developer.android.com*
5. [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — *developer.android.com*
6. [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android) — *developer.android.com*
7. [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — *developer.android.com*
8. [Android Keystore System](https://developer.android.com/training/articles/keystore) — *developer.android.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/android/` | Aligned to Google MAD · Android Arch Guide · OWASP MASVS-L2 · NIST SP 800-163*
