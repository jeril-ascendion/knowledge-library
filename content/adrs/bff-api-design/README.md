# Backend for Frontend (BFF) API Design for Mobile Clients

> **ADR Reference:** `ADR-INT-005`
> **Alignment:** Richardson Maturity Model | GraphQL Foundation | gRPC Protocol | RFC 7807 | Pact Consumer-Driven Contracts
> **Audience:** Mobile Architects · Backend Engineers · API Designers · Integration Specialists

The Backend for Frontend pattern is the mandatory API integration model for all Ascendion mobile applications. Mobile clients have fundamentally different network, battery, and security constraints from web clients. Sharing a generic API across both channels produces over-fetching, security vulnerabilities, and performance degradation on mobile. This ADR mandates a purpose-built mobile API layer that eliminates these defects by design.

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

## Executive Summary

The Backend for Frontend (BFF) pattern is mandatory for all mobile applications connecting to backend services. Mobile clients must not share an API directly with web clients. GraphQL is the preferred BFF technology for new projects. REST with mobile-optimised conventions is adopted for projects with existing REST infrastructure. gRPC with Protocol Buffers is adopted for high-frequency low-latency data streams. The BFF aggregates microservice calls, applies mobile-appropriate field selection, and enforces mobile-specific authentication flows.

## Decision Drivers

| Priority | Quality Attribute | Weight | Rationale |
|---|---|---|---|
| 1 | Network Efficiency | 25% | Mobile data is metered. Round trips on cellular cost 50-300ms each. |
| 2 | Mobile Security | 22% | Mobile-specific auth (PKCE) enforced at BFF boundary. |
| 3 | Offline Capability | 18% | BFF must support delta sync for offline-first architecture. |
| 4 | Developer Experience | 15% | Type-safe generated clients reduce integration errors. |
| 5 | Backend Independence | 12% | BFF abstracts microservice changes from mobile clients. |
| 6 | Performance at Scale | 8% | Caching and aggregation at BFF layer. |

## Considered Options

### Option A — GraphQL BFF (PREFERRED)
Purpose-built GraphQL layer aggregating multiple microservices. Field selection is native — no over-fetching by design. Apollo Kotlin and Apollo iOS generate type-safe client code from the schema. GraphQL subscriptions for real-time without separate WebSocket management. Persisted queries reduce request payload size on low-bandwidth connections.

### Option B — REST BFF with Mobile Conventions (PERMITTED)
Purpose-built REST API for mobile. Cursor-based pagination, field selection via ?fields= parameter, batch endpoints, conditional requests with ETag/If-None-Match, Brotli compression. Adopted when backend team has strong REST expertise and limited GraphQL experience.

### Option C — Shared Generic API (PROHIBITED)
Mobile consuming the same API as web. Produces over-fetching, incorrect authentication flows, and performance degradation on mobile. Any proposed shared API requires ARB emergency review and documented waiver.

### Option D — gRPC Streaming (SUPPLEMENTARY)
Protocol Buffers binary encoding for high-frequency data. Bidirectional streaming for real-time features. 3-10x more compact than JSON. Adopted for real-time location, financial order books, live chat.

## Decision

GraphQL BFF is the preferred default. REST BFF permitted for existing REST infrastructure. gRPC supplementary for high-frequency streams. Shared API with web is unconditionally prohibited.

## Implementation Standards

### Repository-to-BFF Mapping
Each Repository method maps to exactly one BFF operation. Aggregation is the BFF's responsibility — the mobile Repository never composes multiple BFF calls.

### Offline Sync Contract
All collection endpoints support a since query parameter accepting ISO 8601 timestamp. Deleted records appear as tombstones (id + deletedAt) for minimum 30 days. Conflict detection via version field returning 409 on stale update.

### Push Notification Contract
Payloads must never contain sensitive data. Payloads contain notification_id only. App calls BFF to fetch actual content on notification open. Silent pushes trigger background delta sync.

### Consumer-Driven Contract Testing
Mobile team writes Pact consumer tests. Pact file published to Pact Broker. Backend deployment blocked if provider verification fails.

## Trade-offs

| Trade-off | Consequence | Mitigation |
|---|---|---|
| GraphQL requires DataLoader | N+1 queries without DataLoader | DataLoader mandatory in all GraphQL BFF implementations |
| BFF is additional service | Additional latency hop | Deploy as serverless function or lightweight container |
| Contract testing requires coordination | Backend deploys blocked on failure | Shared Pact Broker with agreed deprecation notice periods |

## Related ADRs

| Reference | Title | Relationship |
|---|---|---|
| ADR-MOB-001 | Mobile Architecture Pattern | Repository interface in clean architecture maps to BFF endpoints |
| ADR-SEC-011 | Mobile Security Controls | OAuth 2.0 PKCE flows implemented at BFF boundary |
| ADR-MOB-003 | Mobile CI/CD Pipeline | Pact contract tests run in CI pipeline |

## References

1. Newman, Sam — Backends for Frontends Pattern. samnewman.io/patterns/architectural/bff
2. GraphQL Foundation — GraphQL Specification. spec.graphql.org
3. Pact Foundation — Consumer-Driven Contracts. docs.pact.io
4. RFC 7807 — Problem Details for HTTP APIs. tools.ietf.org/html/rfc7807
5. Apollo — Apollo Kotlin. apollographql.com/docs/kotlin
