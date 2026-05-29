# Mobile Security

OWASP Mobile Top 10 2024 mapped to platform-specific controls, OAuth 2.0 PKCE for mobile, hardware-backed key storage, certificate pinning by SPKI hash, attestation via Play Integrity and App Attest, and MASVS L2 compliance for regulated workloads.

**Section:** `mobile/` | **Subsection:** `security/`
**Alignment:** OWASP MASVS L1/L2 | OWASP Mobile Top 10 2024 | NIST SP 800-163 r1 | OAuth 2.0 RFC 6749 + PKCE RFC 7636
**Audience:** Mobile Engineers · Security Architects · Application Security

---

## Overview

Mobile security in 2026 is governed by three architectural realities that desktop security does not face. First, the device is in the user's pocket, lost or stolen with statistical certainty over a fleet of millions, and the user installs apps from app stores curated by Apple and Google rather than by the enterprise. Second, no `client_secret` can be safely embedded in a mobile binary — every byte of the binary is reverse-engineerable, so authentication protocols designed for confidential clients (the classic OAuth 2.0 web flow) must be replaced by PKCE-protected public-client flows. Third, the OS provides hardware-backed cryptographic primitives (Secure Enclave on iOS, StrongBox or TEE on Android) that desktop apps largely lack — using them is the difference between "encrypted" in the marketing sense and "encrypted" in the engineering sense.

OWASP MASVS (Mobile Application Security Verification Standard) is the authoritative compliance framework, with Level 1 (L1) appropriate for typical consumer apps and Level 2 (L2) required for regulated workloads — banking, healthcare, government. The 2024 OWASP Mobile Top 10 enumerates the ten most common high-severity issues; mapping every issue to a platform-specific control is the practical work of mobile security architecture.

The architectural shift is not "we use HTTPS." It is: **mobile security is a hardware-backed, attestation-validated, PKCE-flowed, supply-chain-monitored, OWASP-MASVS-L2-aligned discipline whose controls are codified per platform, audited per release, and validated by a third-party mobile pentest before any regulated workload reaches production.**

---

## Core Principles

### 1. No `client_secret` in the binary — PKCE is mandatory

OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange, RFC 7636) is the only acceptable authentication flow for mobile public clients. The client generates a per-request `code_verifier`, derives the `code_challenge` (SHA-256 of verifier), sends the challenge with the authorization request, and proves possession of the verifier when exchanging the code for tokens. The server cannot rely on a secret the mobile binary cannot keep.

### 2. Hardware-backed key storage by default

Android Keystore with hardware backing (TEE on most devices, StrongBox on flagship Pixel and Samsung) generates and stores cryptographic keys outside the app's process. iOS Secure Enclave does the same for ECC keys. Keys never leave the hardware boundary; the app receives the result of cryptographic operations, not the keys themselves. Software-backed keystore is the fallback on lower-tier devices but never the design choice.

### 3. Certificate pinning by SPKI hash, not by certificate

Pinning to a specific certificate breaks when the certificate rotates (every 90 days for Let's Encrypt; annually for typical CA-issued certificates). Pinning to a Subject Public Key Info (SPKI) hash survives certificate rotation as long as the underlying key pair is unchanged. Two backup pins per host (current key + next key) prevent the pin from bricking the app when the key rotates.

### 4. Attestation gates sensitive backend operations

Google Play Integrity API on Android and Apple App Attest / DeviceCheck on iOS produce signed attestations that the request is coming from an unmodified app on a genuine device. The mobile app obtains the attestation and submits it with high-value requests (login, transfer, password reset); the backend validates the attestation before honouring the request. This blocks repackaged apps, emulators, and rooted devices from sensitive endpoints.

### 5. Network Security Config and App Transport Security as platform-enforced policy

Android's Network Security Config XML enforces TLS 1.3 minimum, pins SPKI hashes, and disables cleartext traffic globally. iOS App Transport Security (`NSAppTransportSecurity`) does the same. The policy is enforced by the platform; the app cannot accidentally regress to cleartext or to weaker TLS.

### 6. Logging and telemetry never contain PII or secrets

Refresh tokens, session IDs, account numbers, balances, names, email addresses, and device identifiers must not appear in Logcat, NSLog, crash reports, or analytics events. A logger abstraction with structured redaction, a CI scan that fails the build on PII patterns, and a privacy review per release ensure compliance.

---

## Architecture Deep-Dive

**OWASP Mobile Top 10 2024 — Mapped Controls**

- **M1 Improper Credential Usage**: No hardcoded credentials, no embedded API keys for sensitive scopes. Tokens stored in EncryptedSharedPreferences (Android) or Keychain with appropriate accessibility class (iOS). Mitigation: SAST scan for entropy patterns, secret-detection in CI.
- **M2 Inadequate Supply Chain Security**: Dependency scanning with Snyk, Dependabot, or GitHub Advanced Security. SBOM generation per release. Pin transitive dependencies via lockfiles (`Package.resolved` on iOS SPM, `gradle.lockfile` on Gradle).
- **M3 Insecure Authentication and Authorization**: OAuth 2.0 PKCE flow as the only auth pattern. Refresh tokens rotated on every use (refresh token rotation per RFC 6819). Biometric reauthentication for sensitive operations (transfer, password change).
- **M4 Insufficient Input/Output Validation**: SQLite queries via parameter binding (Room's `@Query` with named parameters, SwiftData's `Predicate`); never string concatenation. WebView output sanitisation against XSS; disable `setJavaScriptEnabled` unless required.
- **M5 Insecure Communication**: TLS 1.3 enforced. SPKI hash pinning with backup pins. Certificate Transparency monitoring (`certstream.calidog.io` or equivalent). HSTS preload for the app's API domains.
- **M6 Inadequate Privacy Controls**: Permission minimisation — request only at point of use, justify each permission in the App Store / Play Store privacy nutrition labels. PII redaction in logs. Privacy-preserving analytics (no IDFA / GAID without explicit consent on iOS / Android 13+).
- **M7 Insufficient Binary Protections**: R8 / ProGuard with `-keepattributes` only for required attributes; `android:debuggable="false"` in release; Bitcode (iOS) for App Store; root / jailbreak detection paired with attestation (do not rely on detection alone — it is bypassable).
- **M8 Security Misconfiguration**: Network Security Config (Android), App Transport Security (iOS). Disable `allowBackup`. Disable WebView debugging in release. ATS exceptions documented per-domain with sunset dates.
- **M9 Insecure Data Storage**: EncryptedSharedPreferences with hardware-backed master key on Android. Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` on iOS. Room with SQLCipher for sensitive databases. iOS `Data Protection` complete class on sensitive files.
- **M10 Insufficient Cryptography**: Approved algorithms — AES-256-GCM, ChaCha20-Poly1305, RSA-OAEP-2048+ or Ed25519. Banned algorithms — MD5, SHA-1, DES, 3DES, AES-ECB mode, RSA-PKCS1v1.5. Cryptography from platform libraries (CryptoKit on iOS, AndroidX Security on Android), never bespoke.

**OAuth 2.0 PKCE Flow**

```
1. Mobile app:
   code_verifier = random(43-128 chars URL-safe)
   code_challenge = BASE64URL(SHA-256(code_verifier))
2. Mobile app → Authorization Server:
   GET /authorize?response_type=code
     &client_id=<public_id>
     &redirect_uri=app.ascendion.com://callback
     &code_challenge=<challenge>
     &code_challenge_method=S256
     &state=<csrf_token>
3. User authenticates; AS redirects with code in deep link.
4. Mobile app → Authorization Server:
   POST /token
     grant_type=authorization_code
     code=<code>
     client_id=<public_id>
     code_verifier=<verifier>      ← proves possession
     redirect_uri=app.ascendion.com://callback
5. AS returns access_token + refresh_token; mobile stores in Keychain / EncryptedSharedPreferences.
```

The `code_verifier` proves the token request comes from the same client that initiated the authorization. No `client_secret` is required; PKCE replaces it for public clients.

**Android Keystore with StrongBox**

```kotlin
val keyGenerator = KeyGenerator.getInstance(KEY_ALGORITHM_AES, "AndroidKeyStore")
val spec = KeyGenParameterSpec.Builder(
    "transfer_signing_key",
    PURPOSE_ENCRYPT or PURPOSE_DECRYPT
)
    .setBlockModes(BLOCK_MODE_GCM)
    .setEncryptionPaddings(ENCRYPTION_PADDING_NONE)
    .setKeySize(256)
    .setUserAuthenticationRequired(true)
    .setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG)
    .setIsStrongBoxBacked(true) // hardware StrongBox where available
    .build()
keyGenerator.init(spec)
keyGenerator.generateKey()
```

The key never leaves StrongBox. Cryptographic operations gated on biometric authentication. The `BiometricPrompt` API initiates the unlock; on success the cipher can be used.

**Play Integrity API**

The app requests an integrity token from Google Play Services; Google returns a signed JWT containing verdicts about device integrity, app recognition, and license. The mobile app sends the token with sensitive requests; the backend validates the token's signature against Google's published keys and inspects the verdicts. Repackaged apps fail recognition; rooted devices fail integrity; emulators fail the strong device verdict.

**App Attest on iOS**

A per-app, per-device key pair generated in the Secure Enclave. The Secure Enclave produces an attestation object proving the key was generated on a genuine Apple device running the app's specific App Store binary. The backend validates the attestation against Apple's published certificate chain. Subsequent requests are signed with the device key; the backend validates signatures against the attested public key.

**MASVS L1 vs L2**

- **L1**: Standard hygiene — TLS, secure storage, parameterised queries, dependency scanning. Appropriate for typical consumer apps.
- **L2**: L1 plus defence in depth — root / jailbreak detection, anti-tampering, advanced cryptography requirements, attestation. Required for banking, healthcare, government, payment apps.
- **R (Resilience)**: L2 plus active anti-reverse-engineering and runtime application self-protection (RASP). Used for the most sensitive workloads.

The Philippines BSP Circular 982 mandates L2-equivalent controls for licensed banks; HIPAA, PCI DSS, and GDPR all map to L1 or L2 depending on the data category.

---

## Implementation Guide

### Step 1: Map OWASP Mobile Top 10 to your codebase

For each of the ten items, document the specific control in place, the file where it lives, and the test that validates it. Gaps become tickets.

### Step 2: Implement PKCE end-to-end

The authorization library (AppAuth-Android, AppAuth-iOS) generates verifier and challenge. The deep-link callback handler exchanges the code for tokens. Refresh token rotation enabled server-side.

### Step 3: Move all secrets to hardware-backed storage

Refresh tokens, biometric-protected keys, encryption keys — all in Keystore (StrongBox where available) or Keychain (Secure Enclave for ECC). Remove anything in `SharedPreferences` or `UserDefaults` that is secret-like.

### Step 4: Configure Network Security Config and App Transport Security

Android `res/xml/network_security_config.xml` pins SPKI hashes and disables cleartext. iOS `Info.plist` `NSAppTransportSecurity` mirrors the policy. Per-domain exceptions documented.

### Step 5: Integrate attestation

Play Integrity on Android, App Attest on iOS. Backend validates attestations before authorising sensitive operations. Operations list documented: login, transfer, password reset, profile update.

### Step 6: Engage third-party mobile pentest

Independent firm exercises OWASP MASVS L2 controls against the release candidate. Findings tracked to remediation. Pentest cadence at least annually plus before major release.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| OWASP Mobile Top 10 control matrix | Security Architect | Each item has documented control, file location, validating test | Required |
| PKCE flow end-to-end | Mobile + Security | Authorization library configured, refresh token rotation enabled | Required |
| Hardware-backed key storage audit | Security Architect | Every credential and key in Keystore / Keychain with appropriate accessibility | Required |
| Network policy enforced | Build Engineering | NSC and ATS configured; SPKI pins with backup pins committed | Required |
| Attestation gating ratified | Backend + Mobile | Attestation list for sensitive operations; backend validation tested | Required |
| Third-party pentest report closed | Security Architect | Findings remediated; report archived; cadence ≥ annual | Required |

---

## Security Considerations

- Root / jailbreak detection is a heuristic, not a guarantee. Pair with Play Integrity / App Attest for server-side trust decisions; do not block the app on client-side detection alone.
- Biometric authentication via `BiometricPrompt` (Android) and `LAContext` (iOS) is hardware-attested where supported; the cryptographic key bound to biometric unlock is the trust anchor, not the biometric flag alone.
- Background screenshot suppression: Android `FLAG_SECURE` on sensitive Activities; iOS overlays the app window in `applicationDidEnterBackground` so the task-switcher snapshot does not capture sensitive content.
- Clipboard hygiene: `setHtmlText` and `setText` calls on sensitive material clear after 60 seconds; iOS `UIPasteboard.setItems` with `expirationDate` provides similar semantics.

---

## Performance Considerations

- TLS 1.3 handshake under 1 RTT (zero RTT with session resumption); the additional latency over HTTP/2 is negligible on modern mobile networks.
- Cryptographic operations on hardware-backed keys add 5-50 ms per operation depending on device; cache results where appropriate (e.g., do not re-derive on every UI render).
- Attestation requests (Play Integrity, App Attest) cost 100-500 ms; perform off the critical path (background pre-fetch before sensitive flow, not during the user's tap).
- Certificate pinning validation costs are negligible; the optimisation work is on backup pin management.

---

## Anti-Patterns to Avoid

### ⚠️ Embedded API Keys with Sensitive Scopes

An AWS access key with S3 write access is shipped in the binary "just for uploads." Within weeks the key is on GitHub via reverse engineering and an unrelated S3 bucket is mining cryptocurrency. The fix is per-user STS tokens minted by the backend after authentication; no static credentials embedded.

### ⚠️ Pinning to a Specific Certificate

The pinned certificate rotates; the app stops working overnight. Customer-support tickets flood. The fix is SPKI hash pinning with two backup pins.

### ⚠️ Trusting Root / Jailbreak Detection Alone

The app blocks rooted devices via SafetyNet Attestation (the legacy API). The detection is bypassed by a Magisk module. The fix is attestation-based trust validation server-side, with client-side detection as one signal among many.

### ⚠️ Logging Refresh Tokens

The team adds a debug logger that prints the full token for "troubleshooting." The log ships in release. Crash reports leak tokens to the analytics provider. The fix is the logger abstraction that redacts secrets by token-name regex and the CI scan that fails the build on raw `Log.` / `print` of secret-tagged values.

### ⚠️ AES-ECB Because "It Is Simpler"

A developer chooses AES-ECB because the API requires only a key, not an IV. ECB leaks structure (the famous penguin image demonstration). The fix is the cryptography review that bans ECB and prefers high-level libraries (Tink, CryptoKit) where the wrong choice is hard to make.

---

## AI Augmentation Extensions

### AI-Assisted SAST and Dependency Triage

LLM-based code analysis tools surface false-positive reductions on SAST findings, classify dependency vulnerabilities by exploitability in mobile context, and prioritise remediation. Snyk's AI features and GitHub Advanced Security's AI-assisted triage compress the security backlog.

### AI-Assisted Threat Modelling

Threat modelling sessions ingest the architecture documentation; LLM assistants enumerate STRIDE-categorised threats per data flow, surfacing threats the human reviewers might miss. The security architect ratifies the model.

---

## References

1. [OWASP Mobile Application Security Verification Standard (MASVS)](https://mas.owasp.org/MASVS/) — *owasp.org*
2. [OWASP Mobile Top 10 2024](https://owasp.org/www-project-mobile-top-10/) — *owasp.org*
3. [OAuth 2.0 PKCE (RFC 7636)](https://datatracker.ietf.org/doc/html/rfc7636) — *IETF*
4. [Google Play Integrity API](https://developer.android.com/google/play/integrity) — *developer.android.com*
5. [Apple App Attest](https://developer.apple.com/documentation/devicecheck/establishing_your_app_s_integrity) — *developer.apple.com*
6. [Android Keystore System](https://developer.android.com/training/articles/keystore) — *developer.android.com*
7. [iOS Security Guide](https://support.apple.com/guide/security/welcome/web) — *Apple Platform Security*
8. [BSP Circular 982 — Mobile Banking Security](https://www.bsp.gov.ph/) — *bsp.gov.ph*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `mobile/security/` | Aligned to MASVS L2 · OWASP Mobile Top 10 2024 · NIST SP 800-163 r1*
