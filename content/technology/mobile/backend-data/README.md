# Backend Integration & Data Architecture

> **Section:** `technology/mobile/backend-data/`
> **Alignment:** Richardson Maturity Model | RFC 7636 PKCE | GraphQL Foundation | gRPC | IETF RFC 8030 Push
> **Audience:** Mobile Architects · Backend Engineers · API Designers · Integration Specialists

The mobile-backend boundary is where most production incidents originate. Write the contract deliberately and most of them go away.

---

## The Backend for Frontend Pattern

Mobile cannot share an API with web because the constraints are different in kind, not degree. Mobile returns from background expecting fresh data with one network request; web can comfortably make twelve parallel requests because the user is staring at the screen. Mobile is on cellular with 100-300 ms round-trip time; web is on fibre with 5-15 ms. Mobile battery penalises every wakeup measurable in mAh; web has unlimited power. Mobile clients ship across five platform versions, four screen sizes, and three release vintages simultaneously; web is one current build.

The **Backend for Frontend** (BFF) pattern, articulated by Sam Newman, answers all four constraints. The mobile BFF aggregates calls to multiple downstream microservices into a single mobile-optimised response; applies field selection so the payload is 40 to 70 percent smaller than a generic REST API would return; handles mobile-specific authentication (PKCE token exchange, refresh-token rotation); and provides mobile-appropriate error detail (the user-facing message, not the stack trace). The BFF is owned by the mobile team — the team that knows what the mobile client actually needs — and is deployed alongside the mobile release cadence rather than the backend microservice cadence.

**GraphQL as a natural BFF**. Field selection is built into the query language; subscriptions handle real-time without the connection-management ceremony WebSocket requires; the strong schema enables generated type-safe clients (Apollo Kotlin, Apollo iOS) where every field access is compile-time checked. Persisted queries — the mobile app submits a query hash rather than the query text — eliminate query-complexity attacks and bound the runtime cost the server pays.

**REST BFF best practices**. **Cursor-based pagination** (`?cursor=eyJpZCI6MTIzfQ&limit=20`) survives concurrent inserts and deletes — offset pagination breaks when items are inserted or deleted during pagination, producing duplicates and gaps. **Batch endpoints** for related resources reduce N+1 round trips on screens that show many related items. **Conditional requests** with `ETag` and `If-None-Match` let the CDN serve 304 Not Modified without hitting origin for unchanged resources — substantial bandwidth saving on stable data. **Brotli compression** is 20 to 26 percent smaller than gzip on JSON payloads and is supported on every modern mobile HTTP client.

---

## Offline-First Architecture

**Single source of truth**. Room database on Android or SwiftData on iOS is the only source the UI reads from — never from a network response directly. All network data is written to the local database first; the UI observes the database via `Flow<T>` on Android or `@Query` on iOS; the UI updates because the local database changed, not because the network returned. This is the single most important offline-first principle and the one most often abandoned under deadline pressure.

The **Repository decides cache strategy**. Cache-first for reference data (product catalogue, configuration, FAQ entries) — serve from cache instantly, refresh in background. Network-first for user-generated content with explicit recency requirements (transaction history, message feed) — fetch fresh, fall back to cache on network failure. The strategy is documented per resource in the API contract, not invented per screen.

**Optimistic updates**. A user action that produces a write — mark-as-read, edit, transfer initiate — is reflected in the UI immediately, persisted to the local database immediately, queued for network propagation through an Outbox table, and reconciled when the server responds. If the server rejects (validation failure, insufficient balance), the local change is rolled back and the user is told why. The architectural payoff is the perceived performance: the UI responds in the same frame as the user's tap.

**Conflict resolution per data type**. Last-write-wins with server timestamp for scalar user preferences (notification settings, dark-mode flag) — simple, no UI required, the user does not notice. Field-level merge for structured records like user profiles, where name, phone, and address can be independently updated — implemented server-side via JSON Merge Patch (RFC 7396) or field-versioning. User-decides modal for collaborative data with semantic value on both sides — the user edited a document, another device has a newer edit, the UI presents both versions for the user to merge or pick.

**Delta sync** via timestamp watermarks. The mobile client stores the last-known-server-timestamp per collection in DataStore (Android) or UserDefaults (iOS); the next sync request sends `?since=2026-05-29T08:15:30Z`; the server returns only records modified after that timestamp plus a new `server_timestamp` field in the response that becomes the new watermark. **Tombstones** (records with `deleted_at` set) handle deletes — the client applies the deletion locally and continues forward. The bandwidth saving on stable data is the difference between a usable app on a tier-three device and an unusable one.

**CRDTs for collaborative features**. **Operation-based CRDT** for chat messages where order matters but conflicts are rare — each message is an operation appended in causal order. **State-based CRDT** for presence indicators and shared metadata — the state merges associatively, commutatively, and idempotently. Production-grade libraries: **Automerge** and **Yjs** (JavaScript), `automerge-rs` via JNI on Android, Yjs Swift bindings on iOS.

---

## Real-Time Data

**WebSocket** is the workhorse for bidirectional real-time on mobile. **OkHttp WebSocket** on Android with automatic reconnection and exponential backoff (`OkHttpClient.newWebSocket(request, listener)` plus a wrapper that handles `onFailure`); **URLSessionWebSocketTask** on iOS for the equivalent. The connection consumes battery — keep it open only while the screen is on or while sensitive flows require fresh data; close on background and reopen on foreground.

**gRPC** bidirectional streaming for high-frequency structured data — Protobuf binary encoding is three to ten times more compact than equivalent JSON, the connection multiplexes streams over a single HTTP/2 session, and the strong schema enables compile-time-safe clients on both sides. Use cases that justify gRPC's complexity: live location tracking, real-time market data, in-app chat at scale. **Streaming response** patterns: server-streaming for one-direction live feeds, bidirectional streaming for conversational protocols. Limitations: corporate proxies sometimes break HTTP/2 trailers; debugging is weaker than REST; the toolchain is heavier.

**Server-Sent Events** (SSE) for server-to-client only streams — simpler than WebSocket when bidirectional is not needed, plain HTTP so traverses all proxies cleanly, easy to integrate. The right answer for notification feeds, status dashboards, and any "push update to a screen the user is watching" use case.

**Firebase Realtime Database** and **Firestore** for document sync with offline support built in. Firestore's offline-first model handles the cache-and-reconcile work the team would otherwise build by hand. Cost scales with operations — careful query design matters.

---

## Push Notifications

**APNs** (Apple Push Notification Service) and **FCM** (Firebase Cloud Messaging) are the platform-native push channels. The mobile app obtains a device token at registration via `FirebaseMessaging.getInstance().token` (Android) or `UIApplication.shared.registerForRemoteNotifications()` (iOS). The app sends the device token to your backend on each launch; the backend stores it and sends pushes via APNs HTTP/2 API or FCM REST.

**Critical rule: never put sensitive data in a push payload**. APNs and FCM are infrastructure you do not control — payloads transit Apple's and Google's servers and reside on the device's notification UI where any sibling notification widget can read them. The payload contains a **notification ID** only; the app, on opening the notification, fetches the actual content from your authenticated API. Account balances, transaction amounts, names, account numbers, OTPs — never in push.

**Silent pushes** for background data sync. iOS `content-available: 1` in the APNs payload wakes the app for a brief background-fetch window; FCM `data` payload without notification field does the equivalent on Android. iOS aggressively rate-limits silent pushes (a few per hour typical, much less under heavy battery use); treat as a hint not a guarantee. Android delivers more reliably but is subject to Doze mode constraints.

**Token rotation**. The device token changes when the app reinstalls, when the user restores a device backup, when push permission is enabled or disabled, and unpredictably on server-side rotation. Handle the `410 Gone` response from APNs by removing the stale token from your database immediately — continuing to push to a 410 token is rate-limited by APNs and risks delivery degradation for your other tokens.

---

## Anti-Patterns

### 1. Sharing the Web API with Mobile

The team has one REST API for web and mobile. The web's needs dominate; mobile payloads bloat; users on tier-two devices and weak networks suffer. The fix is the mobile BFF.

### 2. Offset Pagination on Mobile Lists

`?offset=20&limit=20` works in tests; in production the list grows during pagination and users see duplicates and gaps. The fix is cursor pagination from day one.

### 3. Sensitive Data in Push Payloads

Push notifications carry account balances and transaction amounts "for richer notifications." Apple, Google, and any local app on the device with the right permission can read them. The fix is content-by-fetch — the payload carries an ID, the app fetches the content through authenticated API.

### 4. ViewModel Observing the API Directly

The team wires the ViewModel to a `Flow` produced by Retrofit's `flow { emit(api.get()) }`. The UI breaks when offline. The fix is the Repository's `dao.observeAll()` flow as the only thing the ViewModel observes; `refresh()` is a separate concern.

### 5. Forgetting Idempotency Keys

The Outbox retries a transfer; the network blip masked an earlier success; the server processes both. The user is charged twice. The fix is the per-command idempotency key generated client-side and respected server-side.

---

## References

1. [Sam Newman — BFF Pattern](https://samnewman.io/patterns/architectural/bff/) — *samnewman.io*
2. [GraphQL Specification](https://spec.graphql.org/) — *spec.graphql.org*
3. [Relay Connection Spec — Pagination](https://relay.dev/graphql/connections.htm) — *relay.dev*
4. [HTTP Caching — RFC 7234](https://datatracker.ietf.org/doc/html/rfc7234) — *IETF*
5. [JSON Merge Patch — RFC 7396](https://datatracker.ietf.org/doc/html/rfc7396) — *IETF*
6. [Automerge CRDTs](https://automerge.org/) — *automerge.org*
7. [APNs Documentation](https://developer.apple.com/documentation/usernotifications) — *developer.apple.com*
8. [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging) — *firebase.google.com*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/backend-data/` | Aligned to Richardson · RFC 7636 · GraphQL · gRPC · IETF RFC 8030*
