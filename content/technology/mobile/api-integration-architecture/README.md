# API Integration Architecture

> **Section:** `technology/mobile/api-integration-architecture/`
> **Alignment:** REST (Richardson Maturity Model) | GraphQL Foundation | gRPC | BFF Pattern (Sam Newman) | RFC 7807
> **Audience:** Mobile Architects · Backend Engineers · API Designers · Integration Specialists

Mobile applications are API consumers with specific constraints that generic API designs do not accommodate: metered network connections, battery budgets, intermittent connectivity, and a client-server contract that updates on a different cadence than the server. API integration architecture for mobile is the set of patterns that resolve these constraints.

## Overview

The Backend for Frontend (BFF) pattern is mandatory for all Ascendion mobile applications. Mobile clients do not share an API with web clients. A purpose-built mobile API layer aggregates microservice responses, applies field selection, implements mobile-appropriate pagination, and enforces mobile-specific authentication flows.

## API Style Selection

**GraphQL** is the preferred default for new BFF implementations. Field selection is native to the protocol — the mobile client requests only the fields it renders. A single GraphQL query replaces multiple REST round trips for screen composition. Apollo Kotlin and Apollo iOS generate type-safe client code from the GraphQL schema, eliminating serialisation errors at the integration boundary. GraphQL subscriptions provide real-time updates without separate WebSocket management.

**REST with Mobile Conventions** is adopted when the backend team has strong REST expertise and limited GraphQL experience. Mobile-specific conventions are mandatory: cursor-based pagination (opaque cursor, not page number — page number breaks when items are inserted mid-pagination), field selection via `?fields=` parameter, batch endpoints for related resources, conditional requests with ETag/If-None-Match headers, and Brotli compression for response bodies.

**gRPC with Protocol Buffers** supplements the BFF for high-frequency low-latency data streams: real-time location tracking, financial order book updates, live auction bidding, real-time chat. Protobuf binary encoding is 3-10× more compact than JSON for equivalent data. Bidirectional streaming eliminates the polling model for real-time features.

## Repository-to-API Mapping

Each Repository method maps to exactly one BFF operation. Aggregation is the BFF's responsibility — the Repository does not compose multiple API calls to build a domain model. This 1:1 mapping enables consumer-driven contract testing with Pact: the mobile client defines the contract it expects from each Repository method, and CI verifies the BFF satisfies it before any backend deployment.

## Push Notification Architecture

APNs (iOS) and FCM (Android) are the delivery mechanisms for push notifications. The BFF maintains device token registration and handles token rotation (410 Gone from APNs triggers immediate token deletion). Push payloads must never contain sensitive data — they contain a notification_id only. The mobile app calls the BFF to fetch actual content after notification open. Silent pushes (background-content-available on iOS, high-priority data message on FCM) trigger background delta sync without user-visible notification.

## Anti-Patterns to Avoid

> **⚠ Shared Web and Mobile API** — Mobile consuming the same REST API designed for web. Web APIs return full resource representations (47 fields); the mobile screen renders 8. Battery, bandwidth, and parse time wasted on 39 unused fields.
> **CORRECT:** Purpose-built mobile BFF. Field selection reduces payload 40-70%. Single round trip replaces multiple sequential requests. Mobile-specific authentication (PKCE) enforced at the BFF boundary.

> **⚠ Offset-Based Pagination for Infinite Scroll** — `GET /transactions?page=3&limit=20`. When a new transaction is inserted before page 3 is fetched, items shift and the user sees a duplicate or skipped transaction.
> **CORRECT:** Cursor-based pagination. `GET /transactions?after=eyJpZCI6IjEyMyJ9&limit=20`. Cursor is opaque — computed from the last item's ID or timestamp. Stable regardless of concurrent inserts.

## References

1. Newman, Sam — Backends for Frontends Pattern. samnewman.io/patterns/architectural/bff
2. GraphQL Foundation — GraphQL Specification. spec.graphql.org
3. Google — gRPC Documentation. grpc.io/docs
4. Pact Foundation — Consumer-Driven Contract Testing. docs.pact.io
5. RFC 7807 — Problem Details for HTTP APIs. tools.ietf.org/html/rfc7807
