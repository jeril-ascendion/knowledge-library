# Backend Integration for Mobile

The mobile Backend-for-Frontend pattern, GraphQL and REST trade-offs for mobile constraints, cursor-based pagination, push-notification architecture across APNs and FCM, gRPC for low-latency streams, and mobile-specific API versioning that survives forced upgrades.

**Section:** `technology/mobile/` | **Subsection:** `backend-integration/`
**Alignment:** Sam Newman BFF Pattern | RFC 7234 (HTTP Caching) | RFC 7232 (Conditional Requests) | OpenAPI 3.1 | gRPC Spec
**Audience:** Mobile Engineers · API Engineers · Solutions Architects

---

## Overview

Mobile clients are not web clients. The payload that the web app comfortably downloads in 200 ms over a fibre connection is the payload the mobile app downloads in 3 seconds over an LTE connection in a tunnel, then re-downloads on every cold start because nothing told the cache it was unchanged. The web app's six API calls become the mobile app's six round trips with associated TCP-and-TLS handshake costs. The pagination scheme that works on the web — offset and limit — breaks on the mobile app where the list scrolls slowly enough that records get inserted or deleted during pagination, producing duplicates and gaps.

The mobile Backend-for-Frontend (BFF) pattern, articulated by Sam Newman, is the architectural answer: the mobile client talks to a mobile-specific BFF service that aggregates calls to internal microservices, shapes responses to mobile-friendly payloads, applies mobile-appropriate caching policies, and abstracts API-version churn behind a stable interface. The BFF is owned by the mobile team — the team that knows what the mobile client actually needs — and is deployed alongside the mobile release cadence rather than the backend microservice cadence.

The architectural shift is not "we have an API." It is: **the mobile client talks to a mobile-specific BFF (or to a GraphQL gateway with mobile-aware schema), with cursor-based pagination, conditional requests, Brotli compression, push-notification payloads that carry ID rather than content, gRPC for low-latency streams where warranted, and minimum-supported-version enforcement so old clients can be retired safely.**

---

## Core Principles

### 1. The mobile client gets its own BFF (or a mobile-aware GraphQL gateway)

The mobile BFF shapes responses to the mobile UI. The web client gets its own BFF or its own GraphQL schema. Sharing one API between mobile and web is an architectural compromise that always favours the larger consumer.

### 2. GraphQL where field selection matters, REST where caching matters

GraphQL allows the mobile client to select only the fields it needs, reducing payload. REST with HTTP caching (ETag, If-None-Match, max-age) leverages CDN and on-device caches that GraphQL bypasses. Choose per resource based on the dominant property.

### 3. Cursor-based pagination, never offset-based

Offset pagination breaks when records are inserted or deleted during pagination. Cursor pagination (opaque cursor representing the position) survives concurrent edits. Pagination contract: `?cursor=<opaque>&limit=20`; response: `{items: [...], next_cursor: "..."}`.

### 4. Push notifications carry an ID, fetch content via API

Push payloads are not the place for sensitive data — they pass through Apple's APNs and Google's FCM servers and reside on the device's notification UI. Carry a notification ID; the app fetches content from the API when the user opens the notification.

### 5. gRPC for streaming, REST and GraphQL for request-response

Bidirectional streaming use cases (chat, live tracking, real-time updates) benefit from gRPC's persistent connections and Protobuf efficiency. Request-response remains on REST or GraphQL; gRPC's overhead is unjustified for occasional calls.

### 6. Minimum supported version enforced server-side

The mobile client identifies its version in every request (`User-Agent` or a custom header). The backend rejects requests from versions below the minimum supported version with a structured response telling the app to prompt the user to upgrade. Without this, old clients prevent backend evolution.

---

## Architecture Deep-Dive

**The Mobile BFF**

The BFF aggregates microservice calls and shapes responses:

```
GET /mobile/v3/home
→ BFF calls account-service, transaction-service, notification-service in parallel
→ BFF assembles a HomeResponse: { user, recent_transactions, balance, unread_count }
→ Mobile receives one response in one round trip
```

The shape is mobile-specific. The web BFF returns a different shape from the same backend services. The BFF is deployed and versioned alongside the mobile release.

**GraphQL for Field Selection**

```graphql
query Home {
  user { id, name, avatar_url }
  recent_transactions(limit: 10) {
    edges { node { id, amount, merchant_name, occurred_at } }
    page_info { has_next_page, end_cursor }
  }
  unread_notifications_count
}
```

The mobile client requests exactly the fields it needs. Payload shrinks 40-70 percent versus REST that returns full records. Apollo Client for Android and iOS provides typed client code generation, optimistic UI helpers, and cache management. Relay's Connection spec is the canonical pagination pattern.

**REST with HTTP Caching**

```http
GET /accounts/123 HTTP/2
If-None-Match: "v3-abc123"

→ 304 Not Modified  (no body)
or
→ 200 OK + ETag: "v3-xyz789" + body
```

The mobile client stores the ETag with the cached response. Subsequent requests send `If-None-Match`; the server responds 304 with no body if the resource is unchanged. CDN tiers (CloudFront, Cloudflare, Akamai) honour ETag and serve 304s without hitting origin. The bandwidth saving on stable resources is substantial.

`Cache-Control: max-age=300, stale-while-revalidate=600` lets the client serve a cached response for 5 minutes without revalidation, and for an additional 10 minutes while revalidating in background. Mobile networks reward this pattern; the user sees the cached response instantly while the app fetches fresh data behind the scenes.

**Brotli Compression**

Brotli compresses JSON 20-30 percent more than gzip on typical payloads. Mobile clients advertise `Accept-Encoding: br, gzip`; the server compresses with Brotli when the client supports it. Backends configured with both gzip and Brotli; CDN handles negotiation.

**Cursor Pagination**

```http
GET /transactions?cursor=eyJpZCI6MTIzfQ&limit=20
→ {
  items: [...],
  page_info: { end_cursor: "eyJpZCI6MTQzfQ", has_next_page: true }
}
```

The cursor is opaque to the client — typically a base64-encoded JSON object containing the last record's ID and timestamp. The server uses the cursor to construct the SQL `WHERE id > <last_id>` predicate. Inserts at the head of the list don't affect ongoing pagination; deletes don't produce duplicates.

**Push Notification Architecture**

APNs (Apple Push Notification Service) and FCM (Firebase Cloud Messaging) are the platform-native channels. The backend obtains the device token from the mobile app at registration; subsequent notifications target the token via APNs HTTP/2 API or FCM REST API.

Payload structure:

```json
{
  "aps": { "alert": { "title": "Transfer complete", "body": "₱5,000 received" }, "badge": 1 },
  "notification_id": "n_abc123",
  "type": "transfer_completed"
}
```

The body shown to the user is generic; the `notification_id` is the handle the app uses to fetch full content (transaction amount, sender, account) when the user opens the notification. Sensitive content (account balance, dollar amounts) is fetched, not delivered in the payload.

Silent pushes (`content-available: 1` on APNs, `data` only on FCM) wake the app briefly for background sync. iOS aggressively rate-limits silent pushes; treat them as a hint, not a guarantee. Android delivers more reliably but is also subject to Doze mode constraints.

**gRPC for Streaming**

gRPC with Protobuf for high-frequency low-latency streams — live order tracking, in-app chat, real-time presence. Bidirectional streaming maintains a single HTTP/2 connection; messages flow in both directions until either side closes. Protobuf payloads are 3-10× smaller than equivalent JSON.

Limitations: gRPC requires HTTP/2 (most networks support it; some corporate proxies do not), the streaming model requires careful client-side connection management, the debugging story is weaker than REST.

**API Versioning**

Major versions in the URL path (`/v3/`) for breaking changes. Header-based minor versioning (`X-API-Version: 3.4`) for additive changes. Mobile client sends `User-Agent: AscendionApp/4.2.0 (iOS 17.4; iPhone15,3)` on every request; backend extracts the version.

Minimum supported version (MSV) enforcement: the backend rejects requests with `X-App-Version` below the MSV with a structured 426 Upgrade Required response. The mobile app interprets the response, prompts the user to upgrade, and prevents the user from continuing without updating. The MSV is the lever that lets the backend retire support for old clients; without it, the oldest client in production determines the backend's evolution speed.

---

## Implementation Guide

### Step 1: Establish the mobile BFF (or GraphQL gateway)

Mobile-specific service owned by the mobile team, deployed alongside the mobile release. Aggregates microservice calls; shapes responses for the mobile UI.

### Step 2: Wire HTTP caching with ETag and Cache-Control

CDN, BFF, and mobile HTTP client all honour ETag. Cache-Control policies per resource: short max-age plus stale-while-revalidate for active resources; long max-age for immutable resources.

### Step 3: Adopt cursor-based pagination

All list endpoints return `{items, page_info: {end_cursor, has_next_page}}`. Cursors are opaque. Mobile clients store the cursor with the local list and continue pagination on demand.

### Step 4: Wire push notifications with content-by-fetch

APNs and FCM deliver notification IDs. The app fetches content from the API on open. Silent pushes used for background sync hints.

### Step 5: Adopt gRPC for the streaming use cases

Identify streaming use cases (chat, live tracking). Implement with gRPC plus Protobuf. Keep REST or GraphQL for request-response.

### Step 6: Implement minimum supported version enforcement

`X-App-Version` header on every request; backend rejects below MSV. Mobile app handles 426 with upgrade prompt that blocks usage.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Mobile BFF ownership ratified | Mobile + API Architects | BFF service named, owned by mobile team, on mobile release cadence | Required |
| HTTP caching strategy documented | API Architect | ETag and Cache-Control policies per resource; CDN configuration validated | Required |
| Cursor pagination on all lists | API Engineering Lead | Audit confirms no offset pagination on mobile-consumed endpoints | Required |
| Push notification security review | Security + Mobile | Payload contains no PII; content-fetch architecture validated | Required |
| MSV policy ratified | Product + Mobile | Minimum supported version process and user-facing upgrade UX agreed | Required |
| Contract tests with Pact | Mobile + API | Critical endpoints under contract; backend CI verifies | Required |

---

## Security Considerations

- Push payloads never contain authentication tokens, account numbers, balances, or PII; carry IDs only and fetch content through authenticated API calls.
- GraphQL endpoints are vulnerable to query-complexity attacks; implement complexity scoring and reject queries above a threshold; use persisted queries for production mobile clients.
- gRPC connections inherit TLS configuration from the platform; ensure the same SPKI pinning applies.
- Authentication tokens in HTTP headers; never in URL query strings (URLs are logged in CDN access logs, browser history, and proxy logs).
- Backend rate-limiting per device token (not per IP) prevents abuse from devices behind NAT-shared IPs.

---

## Performance Considerations

- Mobile payload budget: under 50 KB per typical response, under 200 KB for list responses. GraphQL field selection and Brotli compression keep within budget.
- Round-trip budget: under 4 RTTs to fully load a screen on a tier-2 device on LTE. BFF aggregation collapses 6-10 microservice calls into 1-2 BFF calls.
- HTTP/2 multiplexing eliminates head-of-line blocking on the connection layer; HTTP/3 (QUIC) further improves on lossy mobile networks.
- gRPC connection setup: ~150 ms on a fresh connection; reuse the channel across calls.
- Push notification delivery latency: APNs typically 100-500 ms, FCM 200-800 ms; tolerable for non-urgent notifications, not suitable for sub-second urgency.

---

## Anti-Patterns to Avoid

### ⚠️ Sharing the Web API with Mobile

The team has one REST API for both web and mobile. The web's needs dominate; the mobile payload is bloated; mobile users on weak networks suffer. The fix is the mobile BFF that shapes responses for the mobile client without compromising the web.

### ⚠️ Offset Pagination on Mobile Lists

`?offset=20&limit=20` works in tests; in production, the list grows during pagination and the user sees duplicates and gaps. The fix is cursor pagination from day one.

### ⚠️ Sensitive Data in Push Payloads

Push notifications carry account balances and transaction amounts "for richer notifications." Apple, Google, and (with a jailbreak) any local app can read the payloads. The fix is content-by-fetch — the payload carries an ID; the app retrieves the content over authenticated API.

### ⚠️ No Minimum Supported Version

Old clients from three years ago continue to call old API versions; the backend cannot retire endpoints. Technical debt compounds. The fix is the MSV policy with a 6-month rolling window: the app version supported today is the oldest version that can still authenticate.

### ⚠️ GraphQL Without Persisted Queries

The mobile app sends arbitrary GraphQL queries; the backend executes them at runtime. An attacker sends a complex nested query that costs server resources. The fix is persisted queries — the mobile app sends a query hash; the server resolves the hash to a pre-registered query.

---

## AI Augmentation Extensions

### AI-Assisted BFF Schema Design

LLM-based architecture tools ingest the mobile UI screens and the backend microservice catalogue, then propose the BFF schema that minimises round trips per screen. The architect ratifies; the typing compresses.

### AI-Assisted GraphQL Query Optimisation

LLM analysis of mobile GraphQL queries identifies over-fetching, suggests field deselection, and validates against persisted-query allowlists. The mobile client's payload shrinks measurably.

---

## References

1. [Sam Newman — Backend For Frontends Pattern](https://samnewman.io/patterns/architectural/bff/) — *samnewman.io*
2. [GraphQL Specification](https://spec.graphql.org/) — *spec.graphql.org*
3. [Relay Connection Spec — Pagination](https://relay.dev/graphql/connections.htm) — *relay.dev*
4. [Apollo Client — Android](https://www.apollographql.com/docs/kotlin/) — *apollographql.com*
5. [HTTP Caching — RFC 7234](https://datatracker.ietf.org/doc/html/rfc7234) — *IETF*
6. [APNs — Apple Push Notification Service](https://developer.apple.com/documentation/usernotifications) — *developer.apple.com*
7. [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging) — *firebase.google.com*
8. [gRPC Documentation](https://grpc.io/docs/) — *grpc.io*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/backend-integration/` | Aligned to BFF Pattern · RFC 7234 · OpenAPI 3.1 · gRPC*
