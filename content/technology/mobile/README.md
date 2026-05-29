# Mobile Development

Android, iOS, and cross-platform architecture — design patterns, security, performance, testing, CI/CD, accessibility, and enterprise mobile. Practitioner-grade reference for engineers, solutions architects, and technical leads shipping production mobile apps for financial services, healthcare, and enterprise clients.

**Section:** `technology/` | **Subsection:** `mobile/`
**Alignment:** Google MAD | Apple HIG | OWASP MASVS-L2 | WCAG 2.2 AA | NIST SP 800-163 r1
**Audience:** Mobile Engineers · Solutions Architects · Technical Leads

---

## Overview

The Mobile Development hub captures seventeen substantive architectural disciplines that together define a production-grade mobile programme in 2026. Pure native Kotlin on Android with Jetpack Compose; pure native Swift on iOS with SwiftUI and Swift Concurrency under strict mode; the four serious cross-platform options (Flutter, React Native, Kotlin Multiplatform, .NET MAUI) with their honest performance ceilings and TCO trade-offs; the structural patterns (MVVM, MVI, Clean Architecture, TCA) that scale; the design-system pipeline that puts tokens at the contract; the offline-first SQLite-as-source-of-truth model; the OWASP MASVS L2 security baseline; the performance discipline of Baseline Profiles and 16.67 ms frame budgets; the testing pyramid that completes under 30 minutes; WCAG 2.2 AA accessibility with TalkBack and VoiceOver discipline; the mobile BFF pattern for backend integration; the Fastlane Match CI/CD automation; the layered observability stack with PII redaction; staged-rollout release management with feature flags; the enterprise mobile MDM/MAM landscape; and the five-year TCO model that names each cost lever honestly.

Each subsection is an independently consumable architecture reference with core principles, a deep-dive into the technology and trade-offs, an implementation guide, governance checkpoints, named anti-patterns, and references to specifications and production teams that have shipped the patterns at scale. Use as a body of knowledge during ADR discussions, as a checklist during architecture reviews, or as onboarding material for new mobile engineers and solutions architects.

---

## Topics in this hub

The seventeen disciplines below cover the full lifecycle of a mobile programme from platform choice through cost optimisation. Read sequentially for a complete mobile architecture programme; read selectively for the discipline at hand.

---

## Related Sections

[`technology/cloud`](../cloud) | [`technology/api-backend`](../api-backend) | [`technology/devops`](../devops) | [`security`](../../security) | [`nfr`](../../nfr) | [`observability`](../../observability)

---

## References

1. [Modern Android Development](https://developer.android.com/modern-android-development) — *developer.android.com*
2. [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — *developer.apple.com*
3. [OWASP MASVS](https://mas.owasp.org/MASVS/) — *owasp.org*
4. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — *w3.org*
5. [NIST SP 800-163 r1 — Vetting Mobile Applications](https://csrc.nist.gov/publications/detail/sp/800-163/rev-1/final) — *NIST*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/` | Aligned to Google MAD · Apple HIG · OWASP MASVS-L2 · WCAG 2.2 AA · NIST SP 800-163 r1*
