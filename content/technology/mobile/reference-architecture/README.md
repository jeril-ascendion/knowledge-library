# Reference Architecture

> **Section:** `technology/mobile/reference-architecture/`
> **Alignment:** C4 Model | TOGAF Application Architecture | Google MAD | Apple HIG | AWS Well-Architected
> **Audience:** Solutions Architects · Mobile Architects · Client Technical Decision-Makers · Engineering Leads

The reference architecture is the synthesised view of all architectural decisions across the preceding 27 sections, presented as an integrated system that can be adopted, adapted, or used as a benchmark. It is not a rigid prescription — it is a proven starting point that encodes best practices and eliminates the need to re-derive decisions that have already been made through hard experience.

## Overview

The reference architecture is presented at three levels of abstraction: the system context view (the mobile application in relation to external systems), the application architecture view (the internal structure of the mobile application), and the deployment view (how the application is built, distributed, and operated).

## System Context (C4 Level 1)

The mobile application sits at the centre of an ecosystem:
- **Mobile Application:** The iOS and/or Android application, built using the patterns defined in this knowledge base.
- **Mobile BFF (Backend for Frontend):** The purpose-built API layer that aggregates microservices and serves mobile clients exclusively. GraphQL preferred, REST with mobile conventions as alternative.
- **Identity Provider:** External IdP (Okta, Azure AD, Google Identity Platform) handling OAuth 2.0 authorisation. The mobile app uses OAuth 2.0 + PKCE; the BFF validates tokens.
- **Backend Microservices:** Business domain services (Account, Payment, Profile, Notification). Consumed by the BFF — never by the mobile app directly.
- **Push Notification Services:** Apple Push Notification Service (APNs) for iOS; Firebase Cloud Messaging (FCM) for Android. The BFF sends pushes; the mobile app receives them.
- **Analytics and Observability:** Firebase Crashlytics, Firebase Performance Monitoring, Mixpanel/Amplitude. The mobile app emits events; these platforms aggregate and visualise.
- **CI/CD Infrastructure:** GitHub Actions, fastlane, Firebase App Distribution, Google Play Console, App Store Connect.

## Application Architecture (C4 Level 2 and 3)

The mobile application is structured in three layers following Clean Architecture:

**Presentation Layer:** Compose UI (Android) or SwiftUI (iOS). ViewModels observing StateFlow / @Observable state. Navigation handled by Jetpack Navigation Compose or SwiftUI NavigationStack. Dependency injection through Hilt (Android) or Factory (iOS).

**Domain Layer:** Use Cases — one per business operation. Domain models — pure Kotlin/Swift data classes. Repository interfaces — the contract that data layer implementations must satisfy. No platform dependencies.

**Data Layer:** Repository implementations coordinating between remote and local data sources. Remote data source: Apollo Kotlin/iOS for GraphQL, Retrofit (Android) / URLSession (iOS) for REST. Local data source: Room (Android) or SwiftData (iOS) with encrypted storage for sensitive data. Credential storage: Android Keystore + EncryptedSharedPreferences; iOS Keychain.

## Technology Stack by Vertical

| Vertical | Android Stack | iOS Stack | BFF | Auth |
|---|---|---|---|---|
| Financial Services | Kotlin, Compose, Hilt, Room, Retrofit, Play Integrity | Swift, SwiftUI, Factory, SwiftData, URLSession, AppAttest | GraphQL + Apollo | OAuth2 + PKCE, Biometric MFA |
| Healthcare (PHI) | As above + SQLCipher | As above + SQLCipher | REST (field-selected) | OAuth2 + PKCE, HIPAA compliant IdP |
| Government | As above + BSP Circular 982 controls | As above | REST | OAuth2 + PKCE, Government PKI |
| Consumer / Commercial | Kotlin, Compose, Hilt, Room | Swift, SwiftUI, Factory | GraphQL or REST | OAuth2 + PKCE |
| Cross-Platform (Default) | Flutter with BLoC/Riverpod | — (shared Dart codebase) | GraphQL | OAuth2 + PKCE |

## Deployment Architecture

**Android:** Gradle multi-module build → R8 release AAB → fastlane sign with Android Keystore → Firebase App Distribution (QA) → Google Play staged rollout (production). Baseline Profiles included in release AAB for 30% startup improvement.

**iOS:** Xcode Archive with Release configuration → fastlane Match code signing → TestFlight (QA) → App Store review → App Store release. dSYM files uploaded to Crashlytics for symbolicated crash reports.

**CI/CD:** GitHub Actions matrix with ubuntu-latest (Android) and macos-latest (iOS) runners in parallel. Pipeline time target: under 30 minutes total from commit to distributed build.

## Anti-Patterns to Avoid

> **⚠ Treating Reference Architecture as a Checklist** — Adopting all components of the reference architecture regardless of project context. A three-screen MVP does not need Kotlin Multiplatform, dynamic feature modules, and a full Platform Engineering team.
> **CORRECT:** Use the reference architecture as a menu of proven decisions, not a mandatory specification. Adopt the components appropriate to the project's scale, team size, and client requirements. Apply the full architecture progressively as the project evolves through the scalability stages.

## References

1. Brown, Simon — C4 Model. c4model.com
2. Google — Android App Architecture. developer.android.com/topic/architecture
3. Amazon — AWS Well-Architected Framework. aws.amazon.com/architecture/well-architected
4. TOGAF — ADM. opengroup.org/togaf
