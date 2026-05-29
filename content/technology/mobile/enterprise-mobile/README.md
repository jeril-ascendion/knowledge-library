# Enterprise Mobile (MDM / MAM)

The Mobile Device Management and Mobile Application Management landscape — Jamf Pro for iOS, Microsoft Intune for cross-platform, VMware Workspace ONE for breadth, MAM-without-enrollment for BYOD, managed app configuration, Zero Trust for mobile, and the Philippines BSP Circular 982 banking compliance overlay.

**Section:** `technology/mobile/` | **Subsection:** `enterprise-mobile/`
**Alignment:** NIST SP 800-124 r2 | Microsoft Intune Architecture | Apple Business Manager | Android Enterprise | BSP Circular 982
**Audience:** Mobile Architects · Enterprise IT · Security Architects

---

## Overview

Enterprise mobile sits at the intersection of three constituencies that rarely agree. The CIO wants centralised control over corporate data on every device that touches it. The end user wants their personal device to remain personal — photos, messages, banking apps untouched by IT. The regulator (BSP for Philippines financial services, FFIEC for US banking, MAS for Singapore) wants documented controls that survive a real audit. The architecture that satisfies all three is layered: MDM (Mobile Device Management) for corporate-owned devices, MAM (Mobile Application Management) for the corporate app on a personal device, and managed app configuration as the contract by which the enterprise tells the app what to do without writing custom enterprise versions of every app.

The market has consolidated. Microsoft Intune is the cross-platform leader for Microsoft-centric organisations — Azure AD integration, Conditional Access, the Intune App SDK or App Wrapping for MAM, deep Office 365 integration. Jamf Pro is the iOS specialist — used by approximately 75 percent of Fortune 500 for iOS device management, deep Apple Business Manager integration, the strongest macOS story. VMware Workspace ONE (recently Omnissa post-Broadcom spin-off) is the breadth play — iOS, Android, Windows, macOS managed from one console, used by organisations needing the full unified-endpoint-management spread.

The architectural shift is not "we have MDM." It is: **the enterprise mobile architecture distinguishes COPE (corporate-owned-personally-enabled), BYOD, and dedicated kiosks; applies MDM to corporate-owned and MAM-only to BYOD; uses managed app configuration as the contract for enterprise app settings; enforces Zero Trust on every API request regardless of network; and satisfies BSP / FFIEC / sector regulators with documented, audited controls.**

---

## Core Principles

### 1. COPE, BYOD, and dedicated kiosks have different architectures

Corporate-owned-personally-enabled (COPE): full MDM, separation of work and personal profile (Android work profile, iOS user enrollment). BYOD: MAM only — the enterprise manages the enterprise app, not the device. Dedicated kiosks: full MDM with lockdown, single-app mode, supervised mode on iOS.

### 2. MAM-without-enrollment is the BYOD answer

App-level policies (data isolation, copy/paste restrictions, screenshot block, IT-revocable wipe) applied to the enterprise app without requiring the user to enrol the device in MDM. The personal device remains personal; the enterprise data remains enterprise. Intune's MAM-without-enrollment is the canonical implementation.

### 3. App wrapping and SDK integration each have a role

Wrapping: take an existing app binary and apply MAM policies via code injection (Microsoft's Intune App Wrapping Tool, VMware's wrapper). Zero source-code changes. Works for off-the-shelf apps the enterprise doesn't control. SDK integration: link the Intune App SDK or AppConfig SDK into the app source. Finer-grained policy. Required for new apps. SDK preferred when source access exists.

### 4. Managed App Configuration is the API between MDM and apps

AppConfig Community standard defines a plist-based / XML-based key-value configuration that MDM pushes to the app at install. The app reads pre-configured server URLs, SSO settings, feature flags. No user input required for initial setup; the enterprise's deployment is one-touch.

### 5. Zero Trust for mobile: every request is untrusted

The mobile request is not trusted because it comes from a corporate network or a corporate device. Every request carries authentication; device health is checked via Conditional Access; high-value requests carry attestation. Network perimeter as a trust signal is dead.

### 6. Regulator-specific controls are baked in, not bolted on

BSP Circular 982 mandates specific mobile-banking controls: multi-factor authentication, transaction risk scoring, customer notification of changes. HIPAA mandates encryption at rest and in transit and audit logging. PCI DSS mandates card-data handling specifics. The architecture satisfies these by design; the audit is the easy step.

---

## Architecture Deep-Dive

**MDM Comparison**

- **Jamf Pro**: iOS-first; deep Apple Business Manager integration via Automated Device Enrollment (DEP-successor); the strongest macOS story; preferred in Fortune 500, healthcare, higher education. Pricing per device per month; on the higher end.
- **Microsoft Intune**: cross-platform UEM; native Azure AD Conditional Access integration; Intune App SDK for MAM; integrated with Microsoft Defender for Endpoint; included in Microsoft 365 E3 / E5 bundles, making it the cost-effective choice for Microsoft-shop enterprises.
- **VMware Workspace ONE / Omnissa**: breadth play for organisations needing iOS, Android, Windows, macOS, ChromeOS from one console; Workspace ONE Intelligence for analytics; strong Android Enterprise support.
- **Hexnode / Scalefusion / Kandji**: emerging alternatives; Kandji is Apple-only with a modern UX; Hexnode and Scalefusion offer cross-platform at lower price points.

**MAM Without Enrollment**

The user installs the corporate app from the public App Store / Play Store. On first launch, the app detects an enterprise identity (Azure AD sign-in) and applies the MAM policies declared in Intune. Policies enforce:

- **Data isolation**: corporate data cannot be copy/pasted into personal apps; the share sheet is filtered to approved enterprise apps.
- **Save-as restriction**: data export blocked; "Save to Files" filtered to OneDrive corporate.
- **Screenshot block**: enforced via `FLAG_SECURE` (Android) and screen-capture suppression (iOS).
- **Selective wipe**: IT can remotely wipe corporate data from the app without touching personal data.
- **Re-authentication interval**: requires login after N hours of inactivity.

The user never enrols their device; the enterprise has no visibility into personal apps, location, or device telemetry beyond what Microsoft Graph reports about the corporate identity.

**App Wrapping vs SDK Integration**

App wrapping: take the IPA / APK, run it through Microsoft's Intune App Wrapping Tool or VMware's wrapper. The tool injects MAM policies via Smali manipulation (Android) or runtime swizzling (iOS). The wrapped binary is distributed via the enterprise MDM. Zero source-code changes; supports apps the enterprise didn't write.

SDK integration: link the Intune App SDK into the app source; the SDK provides finer-grained API for policy queries (`shouldAllowSharing`, `shouldEncryptDataAtRest`). Required for new enterprise apps where the developer has source control. Preferred over wrapping because policy errors surface at compile time rather than at wrapping time.

**Managed App Configuration (AppConfig Community)**

The MDM pushes a key-value config to the app at install:

```xml
<dict>
  <key>SERVER_URL</key>
  <string>https://api.acme-corp.com</string>
  <key>SSO_DOMAIN</key>
  <string>acme.onelogin.com</string>
  <key>BIOMETRIC_REQUIRED</key>
  <true/>
</dict>
```

The app reads the config at startup:

```kotlin
val restrictionsManager = getSystemService(Context.RESTRICTIONS_SERVICE) as RestrictionsManager
val bundle = restrictionsManager.applicationRestrictions
val serverUrl = bundle.getString("SERVER_URL") ?: BuildConfig.DEFAULT_SERVER_URL
```

iOS reads via `UserDefaults.standard.dictionary(forKey: "com.apple.configuration.managed")`. The configuration pattern is documented in AppConfig.org's specification, supported by all major MDM vendors.

**Zero Trust for Mobile**

Every API request from the mobile app carries:

- **User identity**: OAuth 2.0 access token tied to a verified Azure AD or Okta identity.
- **Device health signal**: Intune compliance state via Conditional Access policy, or Okta Device Trust, or a custom attestation.
- **App attestation**: Play Integrity or App Attest signed token.

The backend's Zero Trust policy engine evaluates: is the user authorised? is the device compliant? is the app genuine? is the request consistent with normal behaviour (geographic anomaly, velocity, novel-device-novel-IP)? Anomalies trigger step-up authentication or block.

Microsoft Conditional Access is the canonical implementation: policies expressed in the Azure portal, enforced at the API gateway, signals from Intune feeding device-compliance state in real time. Okta's equivalent (Device Trust + ThreatInsight) is the non-Microsoft alternative.

**BSP Circular 982 (Philippines Mobile Banking)**

The Bangko Sentral ng Pilipinas Circular 982 mandates for mobile banking apps:

- **Strong customer authentication**: at least two-factor (PIN plus biometric or PIN plus OTP).
- **Transaction risk scoring**: high-value transactions require elevated authentication.
- **Customer notification**: SMS / push for every account change, with details sufficient to detect fraud.
- **Secure software development lifecycle**: documented SSDLC, security testing per release.
- **Audit logging**: customer-facing actions logged with sufficient detail for forensic investigation.
- **Incident response**: documented playbooks, BSP notification within 2 hours of confirmed incident.

The mobile architecture satisfies 982 by combining the OWASP MASVS L2 controls from the security subsection with explicit transaction-risk scoring on the backend and the customer-notification channel via push.

**PDPA (Philippines Data Privacy Act, RA 10173)**

Personal Information Controllers (PICs) — most enterprises operating in the Philippines — must implement organisational, physical, and technical security measures proportional to the sensitivity of the data. For mobile apps collecting personal information: data-flow mapping, lawful-basis documentation, breach notification within 72 hours, NPC (National Privacy Commission) registration for high-risk processing.

---

## Implementation Guide

### Step 1: Inventory device ownership categories

COPE, BYOD, dedicated devices. The architecture per category is different; conflate them and complexity multiplies.

### Step 2: Select the MDM / UEM platform

Microsoft Intune for Microsoft shops; Jamf for iOS-only enterprises; Workspace ONE for breadth. Document the selection criteria.

### Step 3: Implement MAM for the enterprise app

Intune App SDK linked into the app source. Policies declared in Intune; testing harness for policy enforcement.

### Step 4: Wire managed app configuration

AppConfig contract documented; MDM pushes config; app reads config; pre-configured deployments validated.

### Step 5: Integrate Conditional Access for Zero Trust

Backend API gateway checks Intune compliance state per request; non-compliant devices receive degraded access or block.

### Step 6: Document regulatory compliance evidence

Per regulator (BSP, PDPA, HIPAA, GDPR), document the controls implemented, the evidence collected, and the audit cadence.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Device-ownership categorisation | Enterprise Architect | COPE / BYOD / kiosk categories named; per-category architecture documented | Required |
| MDM / UEM platform selected | IT + Mobile Architect | Vendor chosen with documented selection criteria | Required |
| MAM SDK integrated in enterprise app | Mobile Engineering | Intune App SDK or Workspace ONE SDK linked; policies tested | Required |
| Managed app configuration deployed | IT + Mobile | AppConfig contract documented; MDM-push validated end to end | Required |
| Conditional Access policies live | Security + IT | Per-API compliance check; failure mode tested | Required |
| Regulatory compliance evidence archived | Compliance Officer | Per-regulator evidence kit reviewed and kept current | Required |

---

## Security Considerations

- MAM-without-enrollment provides app-level data protection but does not provide device-level controls; a jailbroken or rooted personal device can still access the corporate app data inside the MAM container if attestation is not also enforced.
- Conditional Access policies must include a "compliance failure" fallback for legitimate users with stale compliance state (just enrolled, OS-update pending); a hard block locks out users at 2am.
- Selective wipe of corporate data is reliable on cooperating apps; non-cooperating apps (the user has pasted corporate data into Notes) cannot be wiped — DLP at the corporate-app level is the prevention.
- BSP, HIPAA, GDPR breach notification clocks start at confirmed-breach detection; the incident-response process must include the regulatory clock as a first-order concern.

---

## Performance Considerations

- MAM SDK initialisation adds 100-300 ms to app cold start; budget the overhead.
- Managed app configuration read happens once at startup; cache for the session.
- Conditional Access checks add 50-200 ms to API gateway latency; mostly amortised by token caching.
- Intune compliance reporting from the device runs every 8 hours by default; reduce to 1-2 hours where real-time compliance state matters for Conditional Access.

---

## Anti-Patterns to Avoid

### ⚠️ Full MDM Enrollment on Personal Devices

The enterprise insists on MDM enrollment on BYOD devices; users refuse or accept under protest; usage drops; shadow IT proliferates. The fix is MAM-without-enrollment for BYOD.

### ⚠️ Custom Per-Enterprise App Builds

The mobile team maintains a separate fork per enterprise customer with branded URLs and customisations. The fork count grows; maintenance dominates engineering time. The fix is managed app configuration: one binary, runtime configuration per enterprise.

### ⚠️ Trusting the Corporate Network

The backend API trusts requests from the corporate VPN; the API is unauthenticated within. A compromised endpoint anywhere on the corporate network becomes a path to all data. The fix is Zero Trust: every request authenticated and authorised, every device's health checked.

### ⚠️ Compliance Theatre

Controls are documented but not implemented; the audit passes because the auditor doesn't probe. The next breach reveals the gap; the BSP / regulator notification proceeds. The fix is continuous compliance validation, not annual self-attestation.

### ⚠️ Wipe Without Backup

The selective wipe removes corporate data including the user's locally-stored work-in-progress. The user loses hours of work. The fix is the design that ensures work-in-progress is server-side-synced before wipe completes; offline draft state has documented backup mechanisms.

---

## AI Augmentation Extensions

### AI-Assisted Compliance Mapping

LLM-based mapping of controls against regulatory frameworks (BSP, PDPA, HIPAA, GDPR) surfaces gaps and overlaps. The compliance team's evidence kit assembles faster.

### AI-Assisted Conditional Access Policy Authoring

LLM assistants generate Conditional Access policy expressions from the team's plain-language requirements ("block access from non-compliant devices outside the Philippines"). Security architects review and ratify.

---

## References

1. [NIST SP 800-124 r2 — Mobile Device Security](https://csrc.nist.gov/publications/detail/sp/800-124/rev-2/final) — *NIST*
2. [Microsoft Intune Documentation](https://learn.microsoft.com/en-us/mem/intune/) — *learn.microsoft.com*
3. [Jamf Pro Documentation](https://docs.jamf.com/) — *docs.jamf.com*
4. [VMware Workspace ONE / Omnissa](https://www.omnissa.com/) — *omnissa.com*
5. [AppConfig Community Standard](https://www.appconfig.org/) — *appconfig.org*
6. [Android Enterprise](https://www.android.com/enterprise/) — *android.com/enterprise*
7. [Apple Business Manager](https://www.apple.com/business/it/) — *apple.com/business*
8. [BSP Circular 982](https://www.bsp.gov.ph/Regulations/Issuances/2017/c982.pdf) — *bsp.gov.ph*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/enterprise-mobile/` | Aligned to NIST SP 800-124 r2 · Intune · Jamf · Workspace ONE · BSP 982*
