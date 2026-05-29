# Offline-First Architecture

The architectural commitment to treat the network as an enhancement, not a requirement — local SQLite as the single source of truth, optimistic UI, conflict resolution strategies, delta sync, and background reconciliation when the device reconnects.

**Section:** `technology/mobile/` | **Subsection:** `offline-first/`
**Alignment:** Local-First Software (Ink & Switch) | CAP Theorem | Material Design Offline Patterns | Apple Sync Guidance
**Audience:** Mobile Engineers · Mobile Architects · Data Engineers

---

## Overview

Most mobile apps treat the network as a precondition. The user opens the app; the app fetches; the spinner spins; if the network is poor, the user waits; if the network is absent, the user sees an error. This works in San Francisco and fails everywhere else — in a subway tunnel, on a rural Philippines highway, in an elevator in a Manila high-rise where LTE signal drops to 0.5 bars. Apps that work only with reliable connectivity are apps that exclude users in markets where reliable connectivity is the exception.

Offline-first is the opposite architectural stance: the app's source of truth is the local SQLite database; the UI always reads from the local database, never directly from a network response; network calls write through to the local database first, then propagate to the UI through the Repository's observable interface; user actions are queued and reconciled when the network returns. The pattern was named in Ink & Switch's "Local-First Software" essay (Kleppmann et al., 2019) and codified for mobile in Google's offline-first guidance and Apple's CloudKit synchronisation patterns.

The architectural shift is not "we cache the API responses." It is: **the local SQLite database is the single source of truth for what the UI displays; every write happens locally first; the network is a background reconciliation channel; user actions never block on connectivity; and conflict resolution is a named, documented architectural decision per data type — not an exception thrown at the user.**

---

## Core Principles

### 1. The local database is the source of truth for the UI

The UI reads from Room (`Flow<T>`) or SwiftData (`@Query`); the Repository writes to the local database on every successful network response; the UI updates because the local database changed, not because the network returned. This is the single most-important offline-first principle and the one most-often abandoned under deadline pressure.

### 2. Writes are optimistic

A user action that produces a write (mark-as-read, edit, transfer) is reflected in the UI immediately, persisted to the local database immediately, queued for network propagation, and reconciled when the server responds. If the server rejects, the local change is rolled back and the user is told why.

### 3. Connectivity is an enhancement signal, not a precondition

The Connectivity Manager (Android `ConnectivityManager`, iOS `NWPathMonitor`) reports network state for UI affordances ("Working offline — changes will sync when you reconnect") and triggers background sync. It does not gate user actions.

### 4. Conflict resolution strategy is named per data type

Scalar value updates: last-write-wins with a server-authoritative timestamp. Structured profile updates: field-level merge. Collaborative documents: CRDT or operational-transform if the use case warrants. User-uploaded content: user-decides UI when the conflict is real. The strategy is documented per data type in the API contract; the mobile code reflects the documented choice.

### 5. Delta sync minimises bandwidth

Sync requests carry the last-known-server-timestamp. The server returns only records changed since. On low-bandwidth connections (emerging markets, roaming), the delta is the difference between a usable app and a 30-second sync.

### 6. Background reconciliation honours platform constraints

WorkManager on Android and BGTaskScheduler / BGAppRefreshTask on iOS schedule background sync with the OS — the OS decides when to run based on battery, network, and user activity. Foreground services for sync are anti-patterns on modern Android; long-running iOS background tasks are not permitted at all.

---

## Architecture Deep-Dive

**Repository as the Reconciliation Point**

The Repository is where offline-first becomes concrete. The Repository's API exposes `Flow<T>` (Android) or `AsyncStream<T>` (iOS) reading from the local database. A `refresh()` method triggers network fetch, writes the response to the local database, and lets the Flow emit naturally:

```kotlin
class TransactionRepository @Inject constructor(
    private val api: TransactionApi,
    private val dao: TransactionDao,
    private val syncWatermark: SyncWatermarkStore,
) {
    fun observe(): Flow<List<Transaction>> = dao.observeAll()

    suspend fun refresh() {
        val since = syncWatermark.get("transactions")
        val delta = api.getTransactions(since = since)
        dao.upsertAll(delta.items.map { it.toEntity() })
        syncWatermark.set("transactions", delta.serverTimestamp)
    }

    suspend fun markRead(id: String) {
        // Optimistic: update local immediately
        dao.updateReadFlag(id, true)
        // Queue for server propagation
        outboxQueue.enqueue(MarkReadCommand(id))
    }
}
```

The UI observes `repository.observe()` and updates automatically when `dao.upsertAll()` writes. The `refresh()` call is triggered by the ViewModel's pull-to-refresh and by a background WorkManager job. The `markRead` call updates the UI in the same frame as the user's tap; the outbox handles network propagation.

**The Outbox Pattern for Pending Writes**

Pending writes are persisted in an Outbox table with status (`pending`, `in_flight`, `failed`, `applied`), retry count, and idempotency key. A background worker drains the Outbox:

```kotlin
class OutboxWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val outboxDao: OutboxDao,
    private val api: ApiClient,
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        outboxDao.observePending().first().forEach { command ->
            try {
                api.execute(command.toRequest(), idempotencyKey = command.id)
                outboxDao.markApplied(command.id)
            } catch (e: HttpException) {
                if (e.code() in 400..499) outboxDao.markFailed(command.id, e.message)
                else throw e // retry on 5xx / network errors
            }
        }
        return Result.success()
    }
}
```

Idempotency keys are critical: the server must deduplicate retried requests by key. Without them, a network blip during the original request and the retry both succeed produces a double-charged transaction.

**Conflict Resolution Strategies**

- **Last-write-wins**: Simple scalar fields (notification preferences, dark-mode flag). Server's authoritative timestamp wins; client's pending write loses if the server timestamp is newer. The user does not see the conflict; the local write is silently overwritten on next sync.
- **Field-level merge**: Structured records like user profiles where name, phone, and address can be independently updated. The merge is performed server-side using JSON Merge Patch (RFC 7396) or a custom field-versioning scheme.
- **CRDT (conflict-free replicated data type)**: Collaborative editing, presence indicators, shared lists. Yjs and Automerge are the production-grade JavaScript / Rust CRDT libraries; mobile-native CRDTs (Yrs for Swift, automerge-rs for Kotlin via JNI) are emerging.
- **User-decides**: Cases where the conflict has semantic weight — the user edited a document, the server has a newer version edited by someone else. The UI presents both versions and asks the user to merge or pick.

**Delta Sync with Timestamp Watermarks**

The client stores the last successful sync timestamp per resource collection. The next sync request sends `?since=2026-05-29T08:15:30Z`. The server returns only records changed after that timestamp plus a new `server_timestamp` field in the response, which becomes the new watermark. The client must trust the server's timestamp authority — clock skew between client and server breaks the sync if the client uses its own clock.

For deletes, the server returns tombstones (records with `deleted_at` set); the client applies the deletion locally and continues forward. Soft-delete on both sides preserves the sync model.

**Background Sync — Platform Constraints**

Android's WorkManager schedules work with constraints (`requiresNetwork`, `requiresBatteryNotLow`, `requiresCharging`). The OS schedules work opportunistically. Foreground services are only appropriate for user-initiated long-running tasks (a music player, an active GPS recording) and are not permitted for routine background sync since Android 12's foreground-service-type restrictions.

iOS's BGAppRefreshTask runs in opportunistic short windows (typically under 30 seconds) when the OS predicts the user will open the app soon. BGProcessingTask is for longer-running work (up to several minutes) and only runs while the device is on power. Neither task is permitted to run for arbitrary durations or at deterministic intervals — apps that need predictable sync must accept the OS's opportunistic schedule or trigger sync on app foreground.

Silent push notifications (APNs `content-available: 1`, FCM data-only) wake the app briefly for sync; the OS rate-limits silent pushes aggressively to prevent abuse. Treat silent push as a hint, not a guarantee.

**Connectivity Monitoring**

Android `ConnectivityManager.registerDefaultNetworkCallback`; iOS `NWPathMonitor`. Both report connectivity state changes. The Repository starts a sync on reconnection from offline; the UI shows the "syncing…" indicator briefly. On loss of connectivity, the UI shows an unobtrusive "offline" affordance and continues to function on local data.

---

## Implementation Guide

### Step 1: Make the local database the UI's source of truth

Refactor any ViewModel that observes API responses directly. The ViewModel observes the Repository's `Flow` / `AsyncStream`; the Repository writes to the local database on every API response.

### Step 2: Implement the Outbox pattern for writes

Every user action that produces a write is queued in the Outbox table. The UI updates optimistically; the worker drains the Outbox; idempotency keys are generated per command.

### Step 3: Negotiate delta-sync semantics with the API team

The mobile client and the backend agree on the `since` parameter convention, the `server_timestamp` response field, and the tombstone format for deletes. The API contract is documented and versioned.

### Step 4: Choose and document conflict resolution per data type

For each resource: last-write-wins, field merge, CRDT, or user-decides. The ADR lives in the mobile architecture documentation; the API contract reflects the choice.

### Step 5: Wire background sync per platform

WorkManager on Android with appropriate constraints; BGAppRefreshTask on iOS. Reconciliation on app foreground if background opportunities have been infrequent.

### Step 6: Add connectivity affordances to the UI

A persistent offline banner (subtle), inline "pending sync" indicators on records with queued writes, and clear messaging when a write fails permanently. The user understands the app's state.

---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Local-source-of-truth audit | Mobile Architect | No ViewModel observes API directly; all UI reads from Repository Flow | Required |
| Outbox pattern in place | Mobile Engineering Lead | Pending-writes table, idempotency keys, retry policy documented | Required |
| Delta sync contract agreed with API team | Mobile + API Architects | `since` parameter, `server_timestamp`, tombstone semantics in API spec | Required |
| Conflict resolution ADR per data type | Mobile Architect | Strategy named, rationale documented, user-decides UI specified where used | Required |
| Background sync per platform | Mobile Engineering Lead | WorkManager / BGAppRefreshTask configured with measured success rate | Required |
| Offline UX affordances ratified | UX + Mobile Architect | Banner, pending indicators, error messages documented and consistent | Required |

---

## Security Considerations

- Local database storage of sensitive data (account balances, transaction history) requires encryption: SQLCipher for Room on Android, SwiftData with file-protection class `complete` on iOS. The encryption key derives from a Keychain-backed master key.
- The Outbox contains pending mutations; if the device is compromised before sync, those mutations are readable. Sensitive Outbox commands (transfers, password changes) include encrypted payloads where the server holds the decryption key.
- Tombstones in the local database persist deletion intent; ensure that "delete" actions in the UI translate to tombstones, not to physical row removal, so concurrent edits on other devices can be reconciled.
- Conflict-resolution UI must avoid leaking the server's "winning" version when it contains information the user should not see (e.g., last-edited-by on a shared document when the editor's identity should be hidden).

---

## Performance Considerations

- Local-write latency under 16 ms (one frame) so the UI does not stutter on optimistic update; Room with proper indices and write-ahead logging achieves this on tier-2 devices.
- Sync payload under 100 KB per delta on typical sessions; pagination and `since` semantics keep the payload bounded.
- Background sync battery budget under 1 percent per day on a Pixel 6a measured with Battery Historian; over-eager WorkManager scheduling is the most common offline-first battery regression.
- WAL (write-ahead logging) enabled on the SQLite database for concurrent read/write performance; checkpoint frequency tuned per app workload.
- Outbox worker batch size: process up to 50 commands per invocation, with exponential backoff on 5xx errors.

---

## Anti-Patterns to Avoid

### ⚠️ The ViewModel Observing the API Directly

Engineers wire the ViewModel to a `Flow` produced by Retrofit's suspend function plus `flow { emit(api.get()) }`. The UI breaks when offline. The fix is the Repository's `dao.observeAll()` flow as the only thing the ViewModel observes; refresh() is a separate concern.

### ⚠️ Blocking the UI on Network for Reads

A list screen shows a spinner until the API responds, even though local data exists. The fix is the local-first read: show local data immediately; refresh in the background; update when the network returns.

### ⚠️ Forgetting Idempotency Keys

The Outbox retries a transfer; the network blip masked an earlier success; the server processes both. The user is charged twice. The fix is the per-command idempotency key generated client-side and respected by the server.

### ⚠️ Last-Write-Wins for Everything

The team applies last-write-wins to user profiles because it is simple. A user edits their phone number on one device while another device edits their address; both fields persisted on different devices; the second sync overwrites the first device's change. The fix is field-level merge for structured records, last-write-wins only for genuinely scalar fields.

### ⚠️ Foreground Service for Sync

The team uses a foreground service to "guarantee" sync timing. The user sees the permanent notification, complains, the app gets one-star reviews about battery and intrusion. The fix is WorkManager / BGAppRefreshTask and acceptance that the OS decides when sync runs.

---

## AI Augmentation Extensions

### AI-Assisted Sync Contract Design

LLM-based architecture assistants ingest the API specification and the mobile data model, then generate a candidate delta-sync contract including `since` semantics, tombstone format, and per-resource conflict-resolution recommendations. The team reviews and ratifies.

### AI-Assisted Conflict Resolution UI Generation

When a data type requires user-decides conflict resolution, AI coding assistants generate the side-by-side merge UI from the data shape, with appropriate affordances for each field type. The design-system team approves the output.

---

## References

1. [Local-First Software — Ink & Switch](https://www.inkandswitch.com/local-first/) — *inkandswitch.com*
2. [Android — Build an offline-first app](https://developer.android.com/topic/architecture/data-layer/offline-first) — *developer.android.com*
3. [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager) — *developer.android.com*
4. [Background Tasks — Apple Developer](https://developer.apple.com/documentation/backgroundtasks) — *developer.apple.com*
5. [JSON Merge Patch — RFC 7396](https://datatracker.ietf.org/doc/html/rfc7396) — *IETF*
6. [Automerge — Local-first CRDTs](https://automerge.org/) — *automerge.org*
7. [Yjs — CRDT for shared editing](https://yjs.dev/) — *yjs.dev*
8. [SQLCipher Documentation](https://www.zetetic.net/sqlcipher/) — *zetetic.net*

---

*Last updated: 2026 | Maintained by: Ascendion Solutions Architecture Practice*
*Section: `technology/mobile/offline-first/` | Aligned to Local-First Software · CAP · Android Offline Guidance*
