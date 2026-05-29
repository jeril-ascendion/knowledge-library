# Mobile Application Security Controls

> **ADR Reference:** `ADR-SEC-011`
> **Alignment:** OWASP MASVS 2.0 | OWASP Mobile Top 10 (2024) | NIST SP 800-163 | ISO 27001 | BSP Circular 982 | PCI-DSS v4.0
> **Audience:** Security Architects · Mobile Engineering Leads · Compliance Officers · Penetration Testers · Client CISO

Mobile application security differs from backend security because the attack surface is distributed across millions of untrusted devices outside the engineering team's control. Every mobile binary is a potential attack artefact — decompilable, modifiable, repackageable. Every on-device data store is a breach target if the device is compromised. Security architecture for mobile must treat device compromise as a design input, not an edge case.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-SEC-011 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice & Security Architecture — Ascendion |
| Status | ACCEPTED |
| Domain | Mobile Security Architecture |
| ARB Approval | Required — Security Architect Sign-off Mandatory |

## Executive Summary

All Ascendion-delivered mobile applications must implement controls addressing the OWASP Mobile Top 10 (2024 edition) as a mandatory baseline. OWASP MASVS Level 1 is the minimum compliance target for all applications. Level 2 is mandatory for financial services, healthcare, and government applications. Controls are enforced through code review gates, CI/CD security scanning, and Security Architecture Review Board sign-off before first production release. OAuth 2.0 + PKCE is the mandatory authentication flow. Hardware-backed credential storage is mandatory for all sensitive data. Certificate pinning using SPKI hashes is mandatory for financial and healthcare applications.

## OWASP Mobile Top 10 — Control Matrix

| OWASP | Risk | Required Control | Implementation |
|---|---|---|---|
| M1 | Improper Credential Usage | No hardcoded credentials. CI secret scanning. | GitLeaks pre-commit + CI. Android Keystore / iOS Keychain. |
| M2 | Inadequate Supply Chain | SDK risk assessment. Dependency checksums. | Gradle verification. SPM checksum. OWASP Dependency Check CI. |
| M3 | Insecure Authentication | OAuth 2.0 + PKCE mandatory. No Implicit Flow. | AppAuth-Android and AppAuth-iOS libraries. |
| M4 | Insufficient Input Validation | Parameterised queries. WebView JS disabled. | Room parameterised queries. allowList for WebView URL schemes. |
| M5 | Insecure Communication | SPKI hash certificate pinning. TLS 1.2 minimum. | OkHttp CertificatePinner. iOS URLSession challenge handler. |
| M6 | Inadequate Privacy Controls | PII never in logs. Minimum permissions. | @Pii annotation + ProGuard rule. @Masked property wrapper. |
| M7 | Insufficient Binary Protections | debuggable: false. R8 full mode. | CI build verification. R8 configuration review. |
| M8 | Security Misconfiguration | cleartext blocked. No debug endpoints in release. | Network Security Config. ATS enforced. |
| M9 | Insecure Data Storage | No sensitive data in SharedPreferences / UserDefaults. | EncryptedSharedPreferences. Keychain kSecAttrAccessibleWhenUnlockedThisDeviceOnly. |
| M10 | Insufficient Cryptography | AES-256-GCM. No MD5/SHA1/ECB. | Detekt CryptoRule. SwiftLint cryptography rules. |

## Authentication Architecture

OAuth 2.0 Authorization Code + PKCE is the mandatory authentication flow. No client_secret in mobile binary — extractable from APK with jadx in under 60 seconds. PKCE eliminates the static secret requirement. Client generates code_verifier (128 random characters), hashes with SHA-256 to code_challenge, server verifies the hash on token exchange.

Biometric MFA mandatory for financial transactions and PHI access: BiometricPrompt API on Android with BIOMETRIC_STRONG requirement; LocalAuthentication on iOS with deviceOwnerAuthenticationWithBiometrics. Biometric-bound keys: KeyStore setUserAuthenticationRequired(true) on Android, kSecAccessControlBiometryCurrentSet on iOS.

## Secure Storage Standards

| Data Classification | Android Mechanism | iOS Mechanism | Accessibility |
|---|---|---|---|
| Credentials (tokens, passwords) | Android Keystore — hardware-backed AES-256 | Keychain — kSecAttrAccessibleWhenUnlockedThisDeviceOnly | When device unlocked, not backed up, device-bound |
| Sensitive user prefs | EncryptedSharedPreferences | Keychain — kSecAttrAccessibleWhenUnlocked | When device unlocked |
| Sensitive structured data | Room + SQLCipher or EncryptedFile | SwiftData with FileProtection .complete | Inaccessible at rest until device unlocked |
| Non-sensitive prefs | SharedPreferences — plaintext acceptable | UserDefaults — plaintext acceptable | No encryption required |
| PROHIBITED | SharedPreferences for credentials | UserDefaults for credentials | P1 finding — blocking code review gate |

## Runtime Attestation

Google Play Integrity API: MEETS_STRONG_INTEGRITY verdict verifies genuine Play-distributed app on genuine unmodified Android. Call on every sensitive transaction. Apple AppAttest: generates hardware-bound attestation key in SecureEnclave, server verifies assertion signature. Both mandatory for financial services and healthcare applications.

## MASVS Compliance by Vertical

| Application Category | MASVS Level | Additional Requirements |
|---|---|---|
| Financial Services (banking, payments) | Level 2 | BSP Circular 982 · PCI-DSS · Root detection · Cert pinning · Biometric MFA |
| Healthcare (PHI handling) | Level 2 | HIPAA · Automatic logoff 5 min · Audit logging · Jailbreak detection |
| Government / Public Sector | Level 2 | PDPA Philippines · Data residency · Government PKI |
| Enterprise Internal Apps | Level 1 | MDM/MAM enrollment · AppConfig · Corporate VPN |
| Consumer / Commercial Apps | Level 1 | Standard OWASP controls baseline |

## Security Review Gates

| Gate | Trigger | Owner | Blocking? |
|---|---|---|---|
| Security Architecture Review | Before first external API integration | Security Architect | YES |
| Credential Storage Code Review | Every PR touching auth or storage | Security-trained Tech Lead | YES |
| OWASP Dependency Check | Every CI build — automated | CI Pipeline | YES on P1/P2 CVE |
| Penetration Test | Before first production release | External Security Firm | YES for L2 apps |
| BSP Circular 982 Compliance Review | Philippines banking apps | Compliance Officer + Security Architect | YES |

## Anti-Patterns to Avoid

### 1. Credentials in SharedPreferences / UserDefaults
Session tokens stored in plaintext storage readable on rooted/jailbroken devices. P1 security finding.

**CORRECT:** Android Keystore + EncryptedSharedPreferences. iOS Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly.

### 2. Client Secret in Mobile Binary
OAuth client_secret embedded in BuildConfig, plist, or strings.xml. Extractable in under 60 seconds.

**CORRECT:** OAuth 2.0 + PKCE eliminates the client_secret requirement. If truly required, fetch from backend post-authentication only.

### 3. Sending Raw Biometrics to Cloud
Transmitting facial images or fingerprint data to a cloud API creates a high-value breach target.

**CORRECT:** On-device biometric verification using Face ID/Touch ID (iOS) or BiometricPrompt (Android). Biometrics never leave the device.

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-001 | Mobile Architecture Pattern | Security controls designed around Clean Architecture layer boundaries |
| ADR-MOB-002 | Mobile Platform Selection | Platform-specific attestation (Play Integrity vs AppAttest) |
| ADR-MOB-003 | Mobile CI/CD Pipeline | Dependency CVE scanning and security lint gates |
| ADR-INT-005 | BFF API Design | OAuth 2.0 PKCE token flows require BFF endpoint alignment |

## References

1. OWASP — MASVS 2.0. owasp.org/www-project-mobile-app-security
2. OWASP — Mobile Top 10 (2024). owasp.org/www-project-mobile-top-10
3. IETF RFC 7636 — PKCE. tools.ietf.org/html/rfc7636
4. BSP Circular 982. bsp.gov.ph
5. Google — Play Integrity API. developer.android.com/google/play/integrity
6. Apple — AppAttest. developer.apple.com/documentation/devicecheck
