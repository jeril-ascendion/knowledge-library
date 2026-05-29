# Build vs Buy Evaluation Framework

> **Section:** `technology/mobile/build-vs-buy/`
> **Alignment:** Total Cost of Ownership | Make-or-Buy Analysis | Gartner | Harvard Business Review
> **Audience:** Solutions Architects · CTOs · Product Managers · Engineering Leads

Every mobile feature, component, and capability presents a build-versus-buy decision. Build custom: higher initial cost, full control, no vendor dependency, bespoke fit. Buy or integrate a third-party SDK or service: lower initial cost, faster time to market, vendor dependency, potential misfit with requirements. The decision is rarely obvious and the consequences persist for years — a payment SDK integrated in year one may be deeply embedded in the codebase by year three, making migration expensive.

## Overview

The build-versus-buy framework evaluates four dimensions: strategic fit (does this capability differentiate us or is it commodity infrastructure?), total cost of ownership over five years (not just initial integration cost), risk profile (vendor dependency, data sovereignty, supply chain exposure), and fit to requirements (does the solution meet the functional and non-functional requirements without bespoke modification?).

## Evaluation Framework

### Dimension 1: Strategic Differentiation
Capabilities that directly differentiate the client's product should be built. A custom biometric authentication flow that reinforces the brand. A proprietary recommendation algorithm. A novel interaction pattern specific to the use case. These are build decisions regardless of cost.

Commodity infrastructure capabilities should be bought. Authentication (use AppAuth + your IdP, not a custom OAuth implementation). Crash reporting (Crashlytics). Push notifications (FCM, APNs via a service like Firebase). Analytics (Mixpanel, Amplitude). Building these from scratch consumes engineering capacity without creating competitive advantage.

### Dimension 2: Total Cost of Ownership (5-Year)
Build cost: engineering time to design, implement, test, document, maintain, and evolve the capability over five years. SDK cost: licensing fees, per-call or per-user pricing, integration engineering time, migration cost if the vendor changes terms.

Five-year TCO calculation:
- Build: (design hours + implementation hours + test hours) × hourly rate + (annual maintenance hours × 5) × hourly rate
- Buy: integration hours × hourly rate + (annual licence fee × 5) + vendor risk premium

SDK licence terms often start cheap and escalate with scale — model the cost at 10× current user base before committing.

### Dimension 3: Risk Assessment
Vendor lock-in risk: how difficult is migration if the vendor raises prices, changes terms, or is acquired? Define an abstraction layer (Repository interface pattern) between the SDK and the business logic, enabling replacement with minimal business logic change.

Data sovereignty risk: where does the SDK send data? For regulated industries (banking, healthcare), SDKs that send user data offshore may violate BSP, PDPA, or HIPAA requirements. Evaluate data residency before adoption.

Supply chain risk: a compromised SDK distributed through Maven Central or CocoaPods affects every app that depends on it. Evaluate the SDK maintainer's security posture and incident history.

### Dimension 4: Requirements Fit
Does the solution meet 100% of functional requirements without modification? Does it meet the performance NFRs? Does it support the required OS versions? Does it comply with the applicable regulations?

A solution that meets 80% of requirements but requires 40% of build cost to fill the remaining 20% often costs more total than building from scratch.

## Build-vs-Buy by Category

| Category | Default Decision | Rationale |
|---|---|---|
| OAuth 2.0 + PKCE | Buy (AppAuth) | Security-critical, well-specified, bad implementation is dangerous |
| Crash Reporting | Buy (Crashlytics) | Commodity infrastructure, network effect (aggregated stack traces) |
| Custom Camera Pipeline | Build | Deep hardware access, platform-specific optimisation required |
| Payment Processing | Buy (Stripe, Adyen) | Regulated, complex, PCI-DSS compliance prohibitive to build |
| Design System Components | Build | Brand differentiation, platform-specific fidelity required |
| Analytics | Buy (Mixpanel/Amplitude) | Data science tooling built in, network effect |
| Biometric Authentication | Buy (BiometricPrompt/LocalAuthentication) | Platform-provided, hardware-backed |
| ML Model Inference | Build model, buy runtime (Core ML, TFLite) | Model is IP; runtime is commodity |

## Anti-Patterns to Avoid

> **⚠ Integration Before Evaluation** — Adding an SDK based on a blog post or a colleague recommendation without completing the evaluation framework. Discovering 18 months later that the SDK sends user data to servers outside the permitted jurisdiction.
> **CORRECT:** Dependency Governance process (Section 14) applies to all SDKs. Evaluation checklist completed and approved before first import.

> **⚠ Building Commodity Infrastructure** — Engineering team spends six sprints building a custom push notification service. The result is equivalent to Firebase Cloud Messaging but without the scale, reliability, and global delivery optimisation.
> **CORRECT:** Buy commodity infrastructure. Build differentiating capabilities. Use engineering capacity where it creates business value.

## References

1. Gartner — Build vs Buy Decision Framework. gartner.com
2. Harvard Business Review — When Should You Buy vs Build Technology? hbr.org
3. ThoughtWorks — Technology Radar. thoughtworks.com/radar
