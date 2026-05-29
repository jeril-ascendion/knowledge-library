# Security and Compliance Architecture

> **Section:** `technology/mobile/security-and-compliance-architecture/`
> **Alignment:** OWASP MASVS 2.0 | NIST SP 800-163 | BSP Circular 982 | PCI-DSS v4.0 | PDPA Philippines | HIPAA
> **Audience:** Security Architects · Mobile Engineers · Compliance Officers · Client CISO

Mobile security architecture differs from backend security in one fundamental way: the attack surface is distributed across millions of untrusted devices that you do not control. Every mobile binary is a potential attack artefact — decompilable, modifiable, repackaged, and redistributed. Every on-device data store is a potential breach target if the device is compromised. Security architecture for mobile must assume device compromise as a design input, not an edge case.

## Overview

The security architecture is built around five layers, each with specific controls. Controls are enforced through code review gates, CI scanning, and — for regulated verticals — external penetration testing before first production release. The OWASP Mobile Application Security Verification Standard (MASVS) Level 1 is the minimum baseline. Level 2 is mandatory for financial services, healthcare, and government applications served by Ascendion.

## Security Architecture Layers

### Layer 1: Transport Security
TLS 1.2 minimum, TLS 1.3 preferred. Certificate pinning using SPKI hash pinning (not certificate pinning — certificates rotate, SPKI public key hashes survive certificate renewal). OkHttp CertificatePinner on Android with the pin computed as `sha256/BASE64(SubjectPublicKeyInfo)`. iOS: URLSession with custom URLAuthenticationChallenge handler verifying the server's public key hash. Cleartext HTTP blocked by default: Android Network Security Config; iOS App Transport Security. Pinning mandatory for all financial and healthcare applications per BSP Circular 982 and HIPAA requirements.

### Layer 2: Authentication and Authorisation
OAuth 2.0 Authorization Code + PKCE is the mandatory authentication flow. No client_secret in mobile binary — any embedded secret is extractable from a decompiled APK within 60 seconds. PKCE eliminates the client_secret requirement: the `code_verifier` generated at runtime replaces the static secret. Biometric authentication as the second factor for financial transactions: Android BiometricPrompt API with `BIOMETRIC_STRONG` requirement; iOS LocalAuthentication with `deviceOwnerAuthenticationWithBiometrics`. Session token lifetime: access token 15 minutes, refresh token stored in hardware-backed storage.

### Layer 3: Secure Data Storage
Android: Credentials in Android Keystore (hardware-backed on devices with dedicated security chip, software-backed on older hardware). Sensitive key-value data in EncryptedSharedPreferences (AES-256-GCM). Database: SQLCipher or Room with EncryptedFile. Never in SharedPreferences plaintext.
iOS: Credentials in Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` — accessible only when device is unlocked, not backed up to iCloud, not migrated to new devices. For biometric-bound operations: SecureEnclave key generation with `kSecAccessControlBiometryCurrentSet`.

### Layer 4: Binary and Runtime Protection
Android release builds: `debuggable: false` in manifest, R8 full mode with custom obfuscation rules, exported Activities protected by signature-level permissions. iOS release builds: App Store distribution certificate, no `get-task-allow` entitlement. Root and jailbreak detection mandatory for financial and healthcare apps: Google Play Integrity API for Android (provides `MEETS_STRONG_INTEGRITY` verdict), Apple AppAttest for iOS (hardware-bound attestation from SecureEnclave).

### Layer 5: Privacy and Data Classification
PII fields annotated with `@Pii` (Kotlin) or `@Masked` (Swift). ProGuard/R8 rule strips PII fields from log output. Clipboard access requires explicit user intent — no background clipboard surveillance. Screen content protection: `FLAG_SECURE` on financial screens (Android), `UITextField.isSecureTextEntry` and `sensitiveContent()` modifier (iOS 17+).

## Regulatory Compliance Matrix

| Regulation | Applies To | Key Mobile Requirements |
|---|---|---|
| BSP Circular 982 | PH Banking Apps | MFA mandatory, session timeout 5min, cert pinning, root detection |
| PDPA Philippines (RA 10173) | All PH apps collecting PII | Privacy notice, data minimisation, right to erasure |
| PCI-DSS v4.0 | Payment card apps | No PAN on device, encrypted transmission, access control |
| HIPAA | Healthcare PHI apps | PHI encryption at rest and transit, automatic logoff, audit trail |
| WCAG 2.2 AA | All apps | Accessibility — see NFR section |

## Anti-Patterns to Avoid

> **⚠ Credentials in SharedPreferences** — Session tokens, API keys, or user passwords stored in Android SharedPreferences (an XML file readable on rooted devices) or iOS UserDefaults (a plist readable with filesystem access).
> **CORRECT:** Android Keystore + EncryptedSharedPreferences for all credential-class data. iOS Keychain with appropriate accessibility attribute. P1 security finding — blocking code review gate enforced in CI.

> **⚠ Client Secret in Mobile Binary** — OAuth client_secret embedded in BuildConfig, plist, or strings.xml. Extractable from APK with jadx in under 60 seconds. Provides an attacker with full API access using your application's identity.
> **CORRECT:** OAuth 2.0 + PKCE eliminates the need for a client_secret. If a client_secret is genuinely required, it must be fetched from a backend after authentication — never embedded in the binary.

## References

1. OWASP — MASVS 2.0. owasp.org/www-project-mobile-app-security
2. IETF RFC 7636 — PKCE. tools.ietf.org/html/rfc7636
3. Google — Play Integrity API. developer.android.com/google/play/integrity
4. Apple — AppAttest. developer.apple.com/documentation/devicecheck
5. BSP Circular 982. bsp.gov.ph
