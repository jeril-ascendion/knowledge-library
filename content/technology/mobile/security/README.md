# Security Architecture & Compliance

> **Section:** `technology/mobile/security/`
> **Alignment:** OWASP MASVS 2.0 | NIST SP 800-163 r1 | ISO 27001 | BSP Circular 982 | PCI DSS v4.0 Mobile | PDPA Philippines
> **Audience:** Security Architects · Mobile Engineers · Compliance Officers · Penetration Testers

---

## Overview

This reference covers mobile security architecture: the OWASP Mobile Top 10, authentication, secure storage, and runtime attestation. It defines the MASVS compliance baseline and the layered, hardware-backed controls mandated for regulated applications.

## OWASP Mobile Top 10 (2024) — All Ten In Depth

**M1 Improper Credential Usage**. Hardcoded API keys in source detectable in under 60 seconds with GitLeaks or TruffleHog. Keys in `BuildConfig` are visible in any decompiled APK — `jadx-gui` is the public-domain tool that exposes them in minutes. Credentials in the Android Manifest read by any app on a rooted device. **Correct:** secrets are fetched from the backend at runtime after authentication, stored in Android Keystore or iOS Keychain, never embedded in the binary. The mobile app's only embedded credential is a per-app public key used to verify the backend's signed response.

**M2 Inadequate Supply Chain Security**. Third-party SDKs requesting excessive permissions or collecting analytics data without disclosure. Gradle dependency verification with checksums on Android; Swift Package Manager checksums on iOS; lockfiles (`Package.resolved`, `gradle.lockfile`) committed and reviewed. The SDK risk-assessment process: stated privacy practices, declared data collection, the SDK's own dependencies, the publisher's incident history. The 2022 `ua-parser-js` compromise reached every React Native app that depended on it transitively.

**M3 Insecure Authentication**. Broken OAuth implementations using the **Implicit Flow** (token returned in URL fragment, observable to any installed clipboard or screen-recording app) — deprecated by RFC 9700 and OAuth 2.1. Missing **state parameter** CSRF protection. Missing **PKCE**. **Correct:** OAuth 2.0 Authorization Code with **PKCE** (RFC 7636) using **AppAuth-Android** or **AppAuth-iOS** libraries — these handle PKCE generation, deep-link callback, and token exchange correctly.

**M4 Insufficient Input Validation**. SQL injection via raw SQLite queries (`db.execSQL("SELECT * FROM users WHERE id = '" + userId + "'")`) — Room's `@Query` with parameter binding eliminates this. XSS in WebView: any untrusted HTML rendered with JavaScript enabled is a vulnerability — call `setJavaScriptEnabled(false)` unless required, sanitise loaded content, configure `setAllowFileAccess(false)`. JavaScript-interface attacks where the native bridge exposes a method to arbitrary JavaScript — restrict to specific authenticated domains via `WebViewClient.shouldInterceptRequest`.

**M5 Insecure Communication**. Missing certificate pinning — the HTTP client trusts any certificate signed by any trusted CA on the device, including corporate MITM proxies and rogue CAs in the system trust store. Cleartext HTTP fallback enabled in **Network Security Config** (Android) or via **ATS exceptions** (iOS). **Correct:** SPKI hash-based pinning (`OkHttp` `CertificatePinner` on Android; `URLSession` custom delegate `urlSession(_:didReceive:completionHandler:)` on iOS) — SPKI hashes survive certificate rotation as long as the underlying key pair is unchanged. Two backup pins per host (current and next) prevent the pin from bricking the app on rotation.

**M6 Inadequate Privacy**. Excessive permission requests at launch — the user denies and the app's value proposition collapses. PII in Logcat (or NSLog) shipping in release builds; a logger abstraction with structured redaction is non-negotiable. Clipboard surveillance through `ClipboardManager.OnPrimaryClipChangedListener` — flagged by the App Store's privacy review. Screen recording detection for sensitive screens via `Window.setSecure(FLAG_SECURE)` on Android and screenshot suppression in `applicationDidEnterBackground` on iOS.

**M7 Insufficient Binary Protections**. `android:debuggable="true"` in release manifest — anyone with the binary can attach a debugger. Exported Activities without permission checks accept Intents from any installed app. R8 not configured in `full` mode loses additional 10-15 percent code shrinking. No root or jailbreak detection for financial apps — though detection alone is bypassable; pair with Play Integrity / App Attest server-side attestation for adequate trust.

**M8 Security Misconfiguration**. Network Security Config allowing cleartext to any domain. ATS exceptions without justification or sunset dates. Exported `ContentProvider`s without `android:protectionLevel="signature"` permissions. Debug endpoints accessible in release builds because the conditional was on `BuildConfig.DEBUG` and the build variant was misconfigured.

**M9 Insecure Data Storage**. Sensitive data in `SharedPreferences` (plaintext XML world-readable on rooted devices). SQLite without encryption. Keychain items with `kSecAttrAccessibleAlways` (accessible even when locked, even on iCloud-restored devices). Log files containing session tokens or PII. **Correct:** EncryptedSharedPreferences on Android, Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` on iOS, SQLCipher for encrypted SQLite, the master key hardware-backed in Keystore or Secure Enclave.

**M10 Insufficient Cryptography**. MD5 or SHA-1 for password hashing (broken since 2017 for collision resistance). AES-ECB mode — leaks structure (the famous penguin image demonstration). RSA without OAEP padding (`Cipher.getInstance("RSA")` defaults to PKCS#1 v1.5 padding which is vulnerable). Weak random for token generation (`Random()` not `SecureRandom()`). Static IV for AES-CBC — defeats the security guarantee. **Correct:** AES-256-GCM via authenticated encryption with associated data (AEAD), ChaCha20-Poly1305 as alternative, scrypt or Argon2id for password hashing, Ed25519 for signatures.

---

## Authentication Architecture

**OAuth 2.0 + PKCE** is the mandatory mobile auth flow. **Why no `client_secret`**: any value embedded in a mobile binary is extractable by anyone who downloads the app — APK decompilation takes under 60 seconds with `jadx`, iOS binaries are similarly extractable via `class-dump` and `frida`. The architectural answer is PKCE (RFC 7636).

**PKCE flow**. The client generates a random 128-character `code_verifier` from a cryptographically secure source. It hashes the verifier with SHA-256 to produce the `code_challenge`. It sends `code_challenge` and `code_challenge_method=S256` in the authorization request. After the user authenticates and the authorization server redirects with an authorization code, the client sends both the code and the `code_verifier` in the token exchange. The server hashes the verifier and verifies it matches the original challenge — proving the token request came from the same client that initiated the authorization. **AppAuth-Android** and **AppAuth-iOS** libraries handle all of this correctly; rolling it yourself is unjustified.

**Biometric authentication**. `BiometricPrompt` API on Android with the `BiometricManager.canAuthenticate(BIOMETRIC_STRONG)` capability check ensures only Class 3 (formerly STRONG) biometrics are used for cryptographic operations. iOS `LAContext.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)` with `kSecAccessControlBiometryCurrentSet` binds the key to the currently enrolled biometric set — re-enrolment invalidates the key, a critical security property.

**Session management**. Access token lifetime 15 minutes. Refresh token stored hardware-backed in Keystore or Secure Enclave. **Refresh token rotation** on every use (RFC 6819 §5.2.2.3) — each refresh exchange returns a new refresh token and invalidates the prior one; reuse detection triggers immediate session revocation. Backend revocation propagates within seconds to all client devices via a short-TTL JWT introspection cache or via streaming session events.

---

## Secure Storage

**Android**. Hardware-backed key generation via `KeyGenParameterSpec.Builder` with `.setIsStrongBoxBacked(true)` on devices with StrongBox (Pixel and Samsung flagships with a dedicated security chip). `EncryptedSharedPreferences` using AES-256-GCM via the AndroidX Security library for all sensitive key-value data. `SQLCipher` for encrypted SQLite databases with the master key derived from a Keystore-bound user secret. **Never** plain `SharedPreferences` for credentials, session tokens, or PII.

**iOS**. Keychain items with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` — accessible only when the device is unlocked (not at rest, not during background fetch), not backed up to iCloud, not migrated to new devices. The `ThisDeviceOnly` attribute is the device-binding that prevents an iCloud-restored backup from carrying credentials forward. `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` for background-task tokens that must work between unlocks. **Secure Enclave** for biometric-bound EC keys on A7 chips and later (every iPhone since 2013); the private key never leaves the Secure Enclave hardware boundary.

**iOS Data Protection** class **`.complete`** on sensitive files — encrypted with a key derived from the user's passcode, decryption keys evicted from memory when the device locks, files inaccessible to the app's own process while locked.

---

## Attestation and Runtime Protection

**Google Play Integrity API**. Server-side verification that the app is a genuine Play-distributed binary running on a genuine unmodified Android device. Returns a signed JSON verdict with three signals: `MEETS_DEVICE_INTEGRITY` (unmodified Android), `MEETS_BASIC_INTEGRITY` (general integrity, weaker), `MEETS_STRONG_INTEGRITY` (hardware-backed attestation on supported devices). Call on every sensitive transaction — login, transfer, profile change — and reject anything below the policy threshold.

**Apple AppAttest and DeviceCheck**. **AppAttest** generates a hardware-bound attestation key in the Secure Enclave per app installation; the server validates the assertion signature against Apple's published certificate chain. Subsequent sensitive requests are signed with the device key; the server validates signatures against the attested public key. **DeviceCheck** provides a per-device two-bit fraud signal that survives reinstall — useful for fraud-prevention systems that need stable device-level state.

**Jailbreak and root detection** layers. Cydia or Sileo app presence; suspicious file paths (`/bin/bash`, `/Applications/Cydia.app`, `/usr/sbin/sshd`); `otool` output anomalies; `RootBeer` library on Android. Treat as one signal among many — sophisticated attackers bypass detection. The architectural answer is server-side attestation, not client-side detection alone.

**Emulator detection** for fraud prevention in financial apps: `Build.PRODUCT` containing "sdk", `Build.HARDWARE` "goldfish" or "ranchu", `Build.FINGERPRINT` patterns; combined with Play Integrity device verdict.

---

## Compliance Frameworks

**BSP Circular 982** (Philippines mobile banking). Mandatory **MFA** for transactions above a threshold (typically PHP 50,000 per transaction). **Session timeout 5 minutes** inactivity. **Certificate pinning** required. **Root/jailbreak detection** required. **Customer notification** for every account change via SMS or push with details sufficient for fraud detection. **Incident notification** to BSP within 2 hours of confirmed incident.

**PCI DSS v4.0 mobile**. No PAN (Primary Account Number) storage on device — tokenisation through the payment processor required. Encrypted transmission (TLS 1.2+ with strong cipher suites). Access control with documented role definitions. Regular vulnerability scans; quarterly external penetration test for Level 1 merchants.

**PDPA Philippines** (RA 10173, Data Privacy Act). **Privacy notice** before data collection — granular consent for distinct processing purposes. **Data minimisation** — collect only what is necessary, no behavioural-tracking by default. **Right to access** and **right to erasure** implementation — the user can export their data and request deletion through an in-app flow that completes within the regulatory timeline.

**HIPAA** for health apps. **PHI encryption** at rest and in transit — every database is encrypted, every backup is encrypted, every cache is bounded. **Automatic logoff** after configurable inactivity (typically 15 minutes). **Audit controls** with tamper-evident logs of every PHI access — who, what, when, from where.

---

## Anti-Patterns

### 1. Embedded API Keys with Sensitive Scopes

An AWS access key with S3 write access embedded "just for uploads." Within weeks the key is on GitHub via reverse engineering and an unrelated bucket is mining cryptocurrency.

**CORRECT:** The fix is per-user STS tokens minted by the backend after authentication.

### 2. Pinning a Specific Certificate

The pinned certificate rotates; the app stops working overnight. Customer support floods.

**CORRECT:** The fix is SPKI hash pinning with two backup pins.

### 3. Trusting Root Detection Alone

The app blocks rooted devices via SafetyNet (legacy) or `RootBeer`. A Magisk module bypasses it.

**CORRECT:** The fix is server-side attestation via Play Integrity / App Attest with client-side detection as one signal among many.

### 4. AES-ECB Because "It Is Simpler"

A developer picks AES-ECB because the API needs only a key, not an IV. ECB leaks structure.

**CORRECT:** The fix is the cryptography review that bans ECB and prefers high-level libraries (CryptoKit on iOS, Tink on Android) where the wrong choice is hard to make.

### 5. Logging Refresh Tokens for "Troubleshooting"

A debug logger prints the full token. The log ships in release. Crash reports leak tokens to the analytics provider.

**CORRECT:** The fix is the logger abstraction that redacts by secret-name regex and the CI scan that fails the build on raw `Log.`/`print` of secret-tagged values.

---

## References

1. [OWASP MASVS 2.0](https://mas.owasp.org/MASVS/) — *owasp.org*
2. [OWASP Mobile Top 10 2024](https://owasp.org/www-project-mobile-top-10/) — *owasp.org*
3. [OAuth 2.0 PKCE (RFC 7636)](https://datatracker.ietf.org/doc/html/rfc7636) — *IETF*
4. [Google Play Integrity API](https://developer.android.com/google/play/integrity) — *developer.android.com*
5. [Apple AppAttest](https://developer.apple.com/documentation/devicecheck) — *developer.apple.com*
6. [Android Keystore](https://developer.android.com/training/articles/keystore) — *developer.android.com*
7. [BSP Circular 982](https://www.bsp.gov.ph/) — *bsp.gov.ph*
8. [NIST SP 800-163 r1](https://csrc.nist.gov/publications/detail/sp/800-163/rev-1/final) — *NIST*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/security/` | Aligned to OWASP MASVS 2.0 · NIST SP 800-163 · BSP 982 · PCI DSS v4.0 · PDPA*
