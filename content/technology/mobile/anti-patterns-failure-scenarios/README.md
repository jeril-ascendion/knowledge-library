# Anti-Patterns and Failure Scenarios

> **Section:** `technology/mobile/anti-patterns-failure-scenarios/`
> **Alignment:** OWASP Mobile Top 10 | Google Android Anti-Patterns | Clean Architecture Violations | Production Incident Analysis
> **Audience:** All Mobile Engineers · Architects · Tech Leads · Code Reviewers

Anti-patterns are recurring solutions to recurring problems that produce negative consequences. They appear repeatedly across mobile codebases because they are natural: they are what a developer writes when following the path of least resistance without the benefit of architectural discipline. This section catalogues the most damaging anti-patterns observed across Ascendion's mobile portfolio with their symptoms, root causes, and correct approaches.

## Overview

Anti-patterns are categorised by severity: Critical (produce security vulnerabilities, data loss, or production crashes), High (produce significant technical debt and degraded quality), and Medium (reduce maintainability and team velocity without immediate production impact). Critical anti-patterns are blocking code review findings — no PR that introduces a critical anti-pattern is merged.

## Critical Anti-Patterns

### Credentials in Plaintext Storage
**Symptom:** Session tokens, API keys, or passwords stored in `SharedPreferences`, `UserDefaults`, or a plaintext SQLite column.
**Root Cause:** Developer unaware of platform secure storage APIs. Speed priority over security.
**Consequence:** Any party with filesystem access (rooted/jailbroken device, backup extraction, physical access) reads the credential.
**Correct approach:** Android Keystore + EncryptedSharedPreferences. iOS Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`.

> **⚠ Plaintext Credential Storage** — `sharedPrefs.putString("token", accessToken)` on Android or `UserDefaults.standard.set(accessToken, forKey: "token")` on iOS. P1 security finding. Blocking code review gate.
> **CORRECT:** `EncryptedSharedPreferences.create(...)` on Android. `KeychainSwift().set(accessToken, forKey: "token")` with appropriate accessibility attribute on iOS.

### Network Call in ViewModel
**Symptom:** ViewModel contains `Retrofit` or `URLSession` import. `apiService.getAccount()` called directly from ViewModel.
**Root Cause:** Architect specified clean architecture verbally but did not enforce it through static analysis or code review.
**Consequence:** Business logic mixed with network I/O. ViewModel untestable without mocking the entire network stack. Security audit cannot identify the data layer boundary.
**Correct approach:** Network calls are in Repository implementations only. ViewModel calls Use Cases. Use Cases call Repository interfaces.

> **⚠ Network Call in ViewModel** — `viewModelScope.launch { val account = apiService.getAccount(id) ... }` in a ViewModel class.
> **CORRECT:** `viewModelScope.launch { val result = getAccountUseCase(id); _state.update { it.copy(account = result.getOrNull()) } }`. The Use Case handles the Repository call.

### Implicit Flow for OAuth
**Symptom:** OAuth authorization URL contains `response_type=token`. Access token appears in the redirect URL fragment.
**Root Cause:** OAuth Implicit Flow was the recommended mobile pattern before 2017. Many tutorials still reference it.
**Consequence:** Access token transmitted in URL fragment is visible in server logs, browser history, and referrer headers. Attack surface for token interception.
**Correct approach:** OAuth 2.0 Authorization Code + PKCE. `response_type=code`. Access token received only in the token endpoint response body.

## High-Severity Anti-Patterns

> **⚠ God ViewModel** — ViewModel with 600+ lines handling networking, navigation, business logic, analytics, error handling, and UI state. Impossible to test, constant merge conflicts for large teams.
> **CORRECT:** Maximum 200 lines. Business logic in Use Cases. Navigation events in a dedicated NavigationEvent sealed class. Analytics in a separate event observer. Each concern in its own class.

> **⚠ Mutable State Exposed from ViewModel** — `val accounts: MutableList<Account>` as a public property. Any class can add, remove, or reorder accounts.
> **CORRECT:** Expose only immutable state. `val uiState: StateFlow<AccountsUiState>`. Internal mutable state is `private val _uiState: MutableStateFlow<AccountsUiState>`.

> **⚠ Hardcoded Strings for Configuration** — API base URL, feature flags, or environment identifiers hardcoded as string literals in source code. Different teams maintain different source files for different environments.
> **CORRECT:** Android BuildConfig fields injected from Gradle build variants. iOS xcconfig files with environment-specific values. CI injects values from encrypted secrets at build time.

> **⚠ Synchronous Network on Background Thread in Loop** — Fetching 500 records by making 500 sequential API calls in a for loop on a background thread. Each call adds 200ms on 4G — 100 seconds total.
> **CORRECT:** Batch endpoint returns all 500 records in a single API call. If a batch endpoint is not available, concurrent requests using `async/await` with `withContext(Dispatchers.IO)`.

## Medium-Severity Anti-Patterns

> **⚠ Context Passed as Use Case Parameter** — `GetUserUseCase(context: Context)` — the domain layer has a dependency on the Android platform.
> **CORRECT:** Domain layer imports no Android classes. Values that require Context (resources, file paths) are resolved at the Repository or data layer and passed as primitive types to the domain.

> **⚠ Magic Numbers in Domain Logic** — `if (account.balance > 50000) { applyPremiumTier() }` — business threshold embedded as a literal in source code.
> **CORRECT:** Named constants in the domain model: `const val PREMIUM_TIER_THRESHOLD = 50_000`. Document the business rule in a comment. Ideally, fetch the threshold from configuration to enable adjustment without a release.

## References

1. Fowler, Martin — Refactoring: Improving the Design of Existing Code. Addison-Wesley, 2018.
2. Google — Android Common Anti-patterns. developer.android.com/topic/performance/vitals
3. OWASP — Mobile Application Security Verification Standard. owasp.org/www-project-mobile-app-security
4. Nygard, Michael — Release It! Pragmatic Bookshelf, 2018.
