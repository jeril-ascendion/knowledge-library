# ADR: Backend for Frontend (BFF) API Design for Mobile Clients

> **ADR Reference:** `ADR-INT-005`
> **Alignment:** Richardson Maturity Model | GraphQL Foundation | gRPC | RFC 7807 | Pact Consumer-Driven Contracts
> **Audience:** Mobile Architects · Backend Engineers · API Designers · Integration Specialists

The Backend for Frontend pattern is the mandatory API integration model for all Ascendion mobile applications. Mobile clients have fundamentally different network, battery, and security constraints from web clients. A shared generic API forces over-fetching, incorrect authentication patterns, and performance degradation on every request. This ADR mandates a purpose-built mobile API layer that eliminates these defects by design.

## ADR Metadata

| Field | Value |
|---|---|
| ADR Reference | ADR-INT-005 |
| Version | 1.0 |
| Date Raised | May 2025 |
| Review Date | November 2025 |
| Author | Solutions Architecture Practice — Ascendion |
| Status | ACCEPTED |
| Domain | Integration Architecture / Mobile Backend |
| ARB Approval | Required |
| Stakeholders | Mobile Architects · Backend Engineers · API Designers · Mobile Engineering Leads · Integration Specialists |

## Executive Summary

**Decision:** The Backend for Frontend (BFF) pattern is mandatory for all mobile applications connecting to backend services. Mobile clients must not share an API directly with web clients. GraphQL is the preferred BFF technology for new projects. REST with mobile-optimised conventions is adopted for projects with existing REST infrastructure. gRPC with Protocol Buffers is adopted for high-frequency low-latency data streams. The BFF aggregates microservice calls, applies mobile-appropriate field selection, and enforces mobile-specific authentication flows per ADR-SEC-011.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Network Efficiency | 25% | Mobile data is metered. Round trips on cellular cost 50–300ms each. Field over-fetching wastes battery and data. |
| 2 | Mobile Security | 22% | Mobile-specific auth (PKCE) must be enforced at the BFF boundary. Web auth patterns are insecure on mobile. |
| 3 | Offline Capability | 18% | BFF must support delta sync and offline-first data access patterns. |
| 4 | Developer Experience | 15% | Type-safe generated API clients reduce integration errors. Contract testing prevents mobile breakage from backend changes. |
| 5 | Backend Independence | 12% | Mobile release cycles are slower than backend. BFF abstracts microservice changes from mobile clients. |
| 6 | Performance at Scale | 8% | Caching and aggregation at BFF layer handles 5,000+ concurrent mobile sessions. |

## Considered Options

### Option A — GraphQL BFF (PREFERRED DEFAULT)
Purpose-built GraphQL layer aggregating multiple microservices. Field selection is native to the protocol — no over-fetching by design. Apollo Kotlin and Apollo iOS generate type-safe client code from the GraphQL schema, eliminating an entire class of serialisation errors. GraphQL subscriptions provide real-time updates without separate WebSocket management. Weighted score: **4.83 / 5.0**

### Option B — REST BFF with Mobile Conventions (PERMITTED)
Purpose-built REST API for mobile with cursor-based pagination, field selection via ?fields= parameter, batch endpoints, conditional requests with ETag/If-None-Match, and Brotli compression. Adopted when backend team has strong REST expertise and limited GraphQL experience. Weighted score: 4.24 / 5.0

### Option C — Shared Generic API (PROHIBITED)
Mobile consuming the same API as web clients. Produces over-fetching, incorrect authentication flows, and performance degradation. Any proposed shared API requires ARB emergency review and documented waiver. Weighted score: 2.09 / 5.0

### Option D — gRPC Streaming (SUPPLEMENTARY)
Protocol Buffers binary encoding with bidirectional streaming. 3–10× more compact than JSON. Adopted as a supplement for high-frequency low-latency use cases: real-time location, financial order books, live chat. Not a replacement for the standard BFF pattern.

## Decision

GraphQL BFF is the preferred default for all new mobile integrations. REST BFF with mobile conventions is permitted for projects with existing REST infrastructure. Shared API with web is unconditionally prohibited. gRPC supplements the BFF for specific high-frequency streams only.

**Repository-to-BFF Mapping:** Each Repository method maps to exactly one BFF operation. Aggregation is the BFF's responsibility — the mobile Repository never composes multiple BFF calls.

**Offline Sync Contract:** All collection endpoints support a `since` query parameter accepting ISO 8601 timestamp. Deleted records appear as tombstones (id + deletedAt) for a minimum of 30 days.

**Push Notification Contract:** Payloads must never contain sensitive data — notification_id only. App calls BFF to fetch actual content on notification open.

## Trade-off Analysis

| Trade-off Accepted | Consequence | Mitigation |
|---|---|---|
| GraphQL requires DataLoader to prevent N+1 queries | Without DataLoader, 20-item query triggers 21 database calls | DataLoader mandatory in all GraphQL BFF implementations. Performance test with 100-item list queries. |
| BFF is an additional service to build and maintain | Additional infrastructure component, latency hop, operational overhead | Deploy as serverless function or lightweight container. BFF is typically under 2,000 lines of code. |
| Consumer-driven contract testing requires coordination | Contract test failures block backend deployments | Shared Pact Broker. Minimum 2 mobile release cycle deprecation notice period. |
| Delta sync API adds backend complexity | Backend must maintain tombstones and support since parameter | Define delta sync requirements in discovery phase. Not all resources require offline sync. |

## Implementation Guidance

1. Choose GraphQL or REST BFF based on team capability assessment in the first sprint
2. Configure Apollo Kotlin or Apollo iOS code generation from the GraphQL schema
3. Implement DataLoader pattern for all GraphQL resolvers that access databases
4. Set up Pact Broker and write consumer-side contract tests before first API integration
5. Configure delta sync endpoint with since parameter for all collection resources
6. Set up silent push for background sync — payload contains notification_id only
7. Implement cursor-based pagination for all list endpoints (REST) or connection-style (GraphQL)
8. Apply Brotli compression on BFF response middleware

## Compliance Checkpoints

| Checkpoint | Trigger | Owner | SLA |
|---|---|---|---|
| BFF API Architecture Review | New mobile project — before backend sprint 1 | Solutions Architect | Before first API integration |
| Shared API Exception Request | Any proposal to share API with web clients | ARB | Decision within 48 hours |
| Push Payload Security Review | Any new push notification type | Security Architect | Before notification goes to production |
| Pact Contract Broker Active | Before first backend deployment affecting mobile | DevOps Lead | Before first release |
| Delta Sync API Design Review | Projects with offline-first requirement | Solutions Architect | Before data layer implementation |

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-001 | Mobile Application Architecture Pattern | Repository interface maps directly to BFF endpoints |
| ADR-MOB-002 | Mobile Platform Selection | Platform determines API client library (Apollo Kotlin vs Apollo iOS) |
| ADR-MOB-003 | Mobile CI/CD Pipeline | Pact consumer tests run in the CI pipeline |
| ADR-SEC-011 | Mobile Application Security Controls | OAuth 2.0 PKCE flows implemented at the BFF boundary |

## References

1. Newman, Sam — Backends for Frontends Pattern. samnewman.io/patterns/architectural/bff
2. GraphQL Foundation — GraphQL Specification. spec.graphql.org
3. Pact Foundation — Consumer-Driven Contract Testing. docs.pact.io
4. Apollo — Apollo Kotlin Documentation. apollographql.com/docs/kotlin
5. IETF RFC 7807 — Problem Details for HTTP APIs. tools.ietf.org/html/rfc7807
6. Google — Firebase Cloud Messaging. firebase.google.com/docs/cloud-messaging

> **⚠ Shared API with Web Clients** — Mobile consuming the same REST or GraphQL API as web clients. Web APIs return full resource representations; the mobile screen renders a fraction. Battery, bandwidth, and parse time wasted on unused fields.
> **CORRECT:** Purpose-built mobile BFF with field selection. Reduces payload 40–70%. Single round trip replaces multiple sequential requests. Mobile-specific authentication enforced at the BFF boundary.

> **⚠ Offset-Based Pagination for Infinite Scroll** — GET /transactions?page=3&limit=20. When a new transaction is inserted before page 3, items shift and the user sees duplicates or skipped records.
> **CORRECT:** Cursor-based pagination. Cursor is opaque and stable regardless of concurrent inserts.
