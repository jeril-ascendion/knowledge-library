# Offline and Reliability Strategy

> **Section:** `technology/mobile/offline-reliability/`
> **Alignment:** CAP Theorem | Offline First Manifesto | Google WorkManager | Apple BGTaskScheduler
> **Audience:** Mobile Architects · Backend Engineers · Mobile Engineers

Mobile applications operate on networks that are fundamentally unreliable. Cellular connectivity drops in underground car parks, building basements, rural areas, and during handover between towers. Satellite connectivity has latency that makes synchronous request-response impractical. Designing a mobile application that degrades gracefully under network loss — rather than presenting an error screen — is an architectural decision, not an implementation detail.

## Overview

The offline-first philosophy inverts the default assumption: instead of designing for network availability and handling offline as an exception, design for offline operation and treat network connectivity as an enhancement. The local database is the single source of truth. The UI reads from the local database exclusively. Network access writes to the local database, which propagates to the UI through reactive observation.

## Offline Architecture Components

### Local Database as Single Source of Truth
Room (Android) or SwiftData/Core Data (iOS) serves as the authoritative data store. Every network response is written to the local database before the UI sees it. The UI never reads from a network response directly — it observes the local database through reactive queries. This pattern ensures: the UI is always consistent with the local database, network failures produce no UI regression (cached data remains visible), and resuming from the background shows instant content while a refresh occurs in the background.

### Repository Cache Strategy
The Repository decides which cache strategy applies to each data type:
- **Cache-first (stale-while-revalidate):** Return cached data immediately, fetch network update in background. Best for reference data (product catalogues, configuration, user profiles). User sees content instantly.
- **Network-first with cache fallback:** Try network first, fall back to cache only on failure. Best for user-generated content (transactions, orders) where freshness matters.
- **Cache-only:** Return cached data, never fetch. For computed data that is expensive to regenerate but changes infrequently.

### Delta Sync Protocol
All collection endpoints support a `since` query parameter accepting an ISO 8601 timestamp or opaque cursor. The mobile Repository stores the watermark of the last successful sync. Subsequent sync requests fetch only records modified after the watermark. Deleted records appear as tombstones (id + deletedAt) for a minimum of 30 days — the Repository removes them from the local database and the UI.

### Conflict Resolution
When optimistic updates are used (write to local database immediately on user action, sync to server in background), network rejection requires rollback. Conflict resolution strategies: last-write-wins with server timestamp for simple scalar values; merge strategy comparing field-level changes for structured objects; user-resolution modal for collaborative data where both changes have business value.

### Background Sync
Android: WorkManager guarantees execution of sync tasks even after process death and device restart. Constraints: network available, battery not critical. Exponential backoff on failure. iOS: BGProcessingTask for longer sync operations (up to 30 minutes when plugged in); BGAppRefreshTask for lightweight updates (up to 30 seconds). Both honour system scheduling — do not use `UIBackgroundModes: fetch` as it is deprecated in favour of BGTaskScheduler.

## Reliability Design Patterns

### Circuit Breaker
Prevent retry storms against an unavailable backend. After N consecutive failures, the circuit opens and fast-fails all subsequent requests for a configurable period. The circuit enters half-open state after the timeout, sending one probe request. If the probe succeeds, the circuit closes. Implemented in the Repository layer using a state machine backed by in-memory state or Object Store v2.

### Retry with Exponential Backoff and Jitter
Transient errors (connection timeout, HTTP 503) are retried. Permanent errors (HTTP 400, 401, 404) are not retried — they are error states requiring user action. Retry formula: `delay = min(base * 2^attempt + random(0, base), maxDelay)`. Base: 1 second. Max: 60 seconds. Jitter prevents thundering herd: multiple client instances failing simultaneously recover at different times rather than synchronised retry storms.

## Anti-Patterns to Avoid

> **⚠ Network Calls Blocking the UI Thread** — `runBlocking { api.getAccount() }` on the main thread. Produces ANR (Application Not Responding) on Android, hangs the UI on iOS. Detected by StrictMode in development.
> **CORRECT:** All network operations on Dispatchers.IO (Android) or a background Task (iOS). UI thread is reserved exclusively for rendering.

> **⚠ No Offline State** — App shows a blank error screen when network is unavailable instead of cached content with a staleness indicator.
> **CORRECT:** All screens implement the offline-first pattern. Stale data is shown with a timestamp of last successful sync. A reconnection banner appears when network returns and a sync is in progress.

## References

1. Hood, Chet and Strazzullo, Luciano — Offline-First Apps with Android. Google I/O 2022.
2. Google — WorkManager Documentation. developer.android.com/topic/libraries/architecture/workmanager
3. Apple — Background Tasks Framework. developer.apple.com/documentation/backgroundtasks
4. Nygard, Michael — Release It! Design and Deploy Production-Ready Software. 2nd Ed. Pragmatic Bookshelf, 2018.
