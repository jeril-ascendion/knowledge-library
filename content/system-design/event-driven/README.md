# Event-Driven Systems

Architecture for systems organised around events — facts about things that happened, propagated through subscribers who never need to know each other, ordered or partitioned in ways that the architecture chooses deliberately.

**Section:** `system-design/` | **Subsection:** `event-driven/`
**Alignment:** Event Sourcing | CQRS Pattern | Apache Kafka | CloudEvents

---

## What "event-driven" actually means

A *request-driven* approach treats system communication as a sequence of calls: A asks B to do something, B does it, A continues. The structure of the system mirrors the structure of the calls — a directed graph of who calls whom, with timing assumptions baked in at every edge. When the system grows beyond a handful of services, this structure becomes its own problem: every change to one service ripples through everyone who calls it, every new feature requires a coordination meeting, every outage cascades along the call graph.

An *event-driven* approach inverts the relationship. Instead of services calling each other, services emit events — facts about things that happened in their own domain — and other services subscribe to the events they care about. The producer does not know who consumes; consumers do not know each other. The system's structure is encoded in what events exist, what they mean, and what order they preserve — not in who calls whom. This shift has wide-ranging consequences: time becomes a first-class domain concept, replay becomes a real capability, schema evolution becomes a continuous discipline, and the failure modes shift from "service A is down" to "the event log is unavailable" — a different problem with different mitigations.

The architectural shift is not "we added Kafka." It is: **events become the system's primary architectural unit, and the structure of the system is encoded in the event vocabulary, the event log, and the contracts between producers and consumers — not in the call graph.**

---

## Six principles

### 1. An event is a fact about the past, not a request for the future

The semantic difference between an event and a command is the foundation of the entire pattern. A command says "do this" — it asks the receiver to perform an action that may succeed or fail. An event says "this happened" — it reports a fact that is already true and cannot be undone. This is not pedantry. It changes who is responsible for what, what failure modes exist, and how the system evolves. Producers of events make assertions about their own domain; consumers decide what to do about them. Producers of commands ask consumers to take action; consumers may refuse, may fail, may double-execute. Treating events and commands interchangeably — naming events as if they were commands ("DoThing"), naming commands as if they were events ("ThingDone") — is the most common way to lose the value of event-driven architecture before you've started.

#### Architectural implications

- Event names describe what happened, in past tense, in the producer's domain language: `OrderPlaced`, `PaymentReceived`, `InventoryReserved`, not `PlaceOrder` or `ReceivePayment`.
- An event is immutable once published; correcting a fact means publishing a new event (`OrderCorrected`, `PaymentReversed`), not editing the original.
- Producers commit to the truth of their events — when an event is published, the fact is real in the producer's domain.
- Consumers decide what to do with each event independently; the producer is not asking, just reporting.

#### Quick test

> Pick a recently-added event in your system. Read its name aloud. Does it describe a fact about the past, or does it sound like a command? If it sounds like a command, the system is using events as RPC and giving up most of the architectural benefits while paying all the costs.

#### Reference

[Martin Fowler, What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html) — the canonical taxonomy that separates event notification, event-carried state transfer, event sourcing, and CQRS as distinct patterns with distinct trade-offs.

---

### 2. The event log can be the source of truth; projections are views derived from it

In event sourcing, the system's state is not stored as the current values of fields — it is stored as the sequence of events that produced those values. The current state is a derived view; the events are the truth. This inverts the traditional database relationship: rows in tables are projections of events, not the canonical record. The architectural property this delivers is profound. The full history of every change is intrinsic, not a feature added on. New views (read models) can be built by replaying the events through different projection logic. Bugs in projections can be fixed by re-running them; bugs in events themselves require compensating events because facts cannot be retroactively unmade. The trade-off is real complexity: the team must think about events, projections, and replay as first-class concerns, and not every system warrants this. But for systems where audit, reconstruction, or temporal queries matter, the alternative architectures are quietly more expensive than they appear.

#### Architectural implications

- The event log is durable, append-only, and treated as the system of record — backups, replication, and disaster recovery centre on it.
- Projections (read models, materialised views, search indexes, dashboards) are derived from the event log and can be rebuilt by replaying it.
- Schema evolution for events is a careful, additive discipline because old events live forever and must remain replayable.
- The team has explicit policies on event retention, log compaction, snapshotting, and projection rebuild — these are operational decisions with architectural consequences.

#### Quick test

> Pick the most central piece of state in your system. Could you reconstruct it from a log of all the events that ever changed it? In an event-sourced system, the answer is yes by design. In other systems, the answer is "we'd need to dig through audit logs and infer," which is not the same property.

#### Reference

[Martin Fowler, Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) and [Greg Young's CQRS Documents](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation) — the canonical discussion of event sourcing and its relationship to CQRS, including the costs that make it unsuitable for many systems and the benefits that make it essential for some.

---

### 3. Ordering is an architectural property — choose it deliberately

Events have order in the producer's mind ("the customer was created before the order was placed"). Whether that order is preserved across the system, across consumers, across replays — is an architectural decision with concrete trade-offs. Global total order is the strongest guarantee and the most expensive to provide; it requires a single sequencer through which all events flow, which becomes the system's bottleneck. Per-key order (events for a given customer or order are ordered relative to each other, but not relative to events for other customers) is the common compromise — sufficient for most domain logic, much cheaper to scale. No order at all is the cheapest and is appropriate for events where independent processing is the only requirement. Choosing among these is not an implementation detail; it determines which kinds of bugs your consumers will see and which kinds of guarantees your domain logic can rely on.

#### Architectural implications

- Each event stream's ordering guarantee is documented as part of the contract: total, per-key, or unordered.
- Partitioning keys are chosen deliberately based on the consistency boundaries the domain requires (typically the aggregate identifier).
- Consumers are written to handle the ordering guarantee they are actually given — assuming total order when only per-key order exists is a recipe for race conditions.
- Cross-partition ordering questions ("what happened first across all partitions") are recognised as expensive and avoided where possible, or solved through explicit aggregation steps.

#### Quick test

> Pick an event stream in your system. What ordering does it guarantee, and does every consumer that depends on order know what guarantee it has? If a consumer assumes more order than is guaranteed, the bug exists already; it just hasn't manifested yet.

#### Reference

[Apache Kafka — Documentation](https://kafka.apache.org/documentation/) — the canonical reference for partition-keyed ordering and the trade-offs between per-partition and global ordering at scale.

---

### 4. Replay is a capability, not an emergency procedure

In a request-driven system, "what would happen if we ran yesterday's transactions through today's code?" is a question without a good answer — yesterday's transactions are gone. In an event-driven system, the question is routine: pick the event log, choose a starting point, run it through the projection or consumer logic, observe the result. Replay enables debugging (reproduce a production issue locally), schema evolution (rebuild a projection with a new shape), backfill (a new consumer joins and processes historical events), and recovery (rebuild a corrupted read model). The architectural commitment to making replay routine — rather than emergency-only — multiplies the value of every other property of the system.

#### Architectural implications

- Consumers are designed to be idempotent — replaying the same events produces the same effect, regardless of how many times.
- The event log retains events long enough to support replay for the longest legitimate use case (which is usually longer than people initially estimate).
- Replay tooling (point-in-time replay, partition-scoped replay, dry-run mode) is part of the platform, not improvised under pressure.
- New consumers can join and replay from the beginning of history, or from a defined offset, without coordinating with existing consumers.

#### Quick test

> Pick a consumer in your event-driven system. If you had to backfill a new field in its read model from historical events, what would that look like? If the answer is "we'd write a one-off script and pray," replay is not actually a capability the architecture provides — it is an aspirational property dressed up as engineering.

#### Reference

[Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — Chapter 11 ("Stream Processing") covers replay, retention, and the operational discipline that makes them work as routine rather than as emergency.

---

### 5. Producers don't know consumers; consumers don't know each other

The decoupling event-driven architecture provides is not just temporal (producers don't wait for consumers) — it is structural: producers do not know who consumes their events, and consumers do not know who produced them or what other consumers exist. This decoupling is the source of the architecture's evolutionary power. New consumers can be added without changing producers. Producers can change implementation without coordinating with consumers (as long as the contract holds). The cost is real: when a consumer breaks, the producer cannot help diagnose; when a producer changes a contract, every consumer is affected without the producer knowing about most of them. The decoupling is what makes event-driven powerful and what makes it operationally different from request-driven systems.

#### Architectural implications

- Producer and consumer teams interact through the event contract (schema, semantics, ordering guarantees), not through direct coordination on every change.
- Backward and forward compatibility of events is a producer responsibility, tested in CI, treated as a public API guarantee.
- Discovery of who consumes which events is a platform capability — without it, producers cannot reason about the impact of contract changes.
- Operational visibility (per-consumer lag, error rates, replay status) is provided by the platform, not by ad-hoc tooling each consumer team invents.

#### Quick test

> Pick a producer in your event-driven system. Without asking the producer team, can you determine which consumers depend on its events and which fields they actually use? If not, the decoupling has eliminated the conversation but kept the dependency invisible — which produces the worst of both worlds.

#### Reference

[CloudEvents Specification](https://cloudevents.io/) — the CNCF specification for transport-neutral event envelopes, designed precisely so that producers and consumers can be decoupled across runtimes, languages, and platforms while still sharing a contract.

---

### 6. Time is a domain concept in event-driven systems

In request-driven systems, time is mostly an operational concern: how long did the request take, was it within SLO, did it time out. In event-driven systems, time becomes a domain concept — events have timestamps, but those timestamps may be when the event happened, when it was published, when it was received, or when it was processed, and these times are different in ways that affect correctness. Stream processing systems must handle late-arriving events (an event from yesterday arrives today because the device was offline), out-of-order events within a window, watermarks that decide when a window is "done," and reprocessing semantics when historical data changes. None of this exists in a request-driven world; all of it must be designed deliberately in an event-driven one.

#### Architectural implications

- Each event has explicit timestamps with documented semantics (event time vs. processing time vs. ingestion time).
- Windowed computations are designed with explicit late-arrival policies — what counts as "in window," how long after a window closes can a late event still be incorporated, and what happens if it arrives after that.
- Watermarks (the system's belief about how far event time has progressed) are first-class and observable, not buried in stream-processor configuration.
- Reprocessing semantics (idempotency under replay, convergence after corrections) are tested as part of the system's correctness, not as edge cases.

#### Quick test

> Pick a windowed computation in your stream-processing system (any rolling aggregate, any per-period summary). What happens to an event whose timestamp falls in yesterday's window but which arrives today? If the answer is "it would be in today's window because that's when we received it," the system has confused processing time for event time — a category of bug that produces silently wrong analytics.

#### Reference

[Tyler Akidau et al. — The Dataflow Model](https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/) — the foundational paper introducing the unified treatment of event time, processing time, and watermarks that informs every modern stream processor.

---

## Architecture Diagram

The diagram below shows the canonical event-driven topology: producers emit immutable events into an ordered event log; the log is the durable source of truth; projections derive read models for query access; independent consumers process events for their own purposes without coordinating with each other; replay is routine, with consumers able to start from any offset.

---

## Common pitfalls when adopting event-driven thinking

### ⚠️ Events as RPC in disguise

Naming events as if they were commands (`SendEmail`, `ChargeCustomer`) and treating them as fire-and-forget remote procedure calls. The producer expects a specific consumer to act on the event in a specific way; the architecture has the cost of asynchrony without any of the decoupling benefits.

#### What to do instead

Events are facts, named in past tense. If a producer needs a specific action to happen, that's a command (sent to a specific recipient with success/failure semantics) — not an event. Using the right primitive for the right semantics keeps the architecture honest.

---

### ⚠️ Schema evolution by accident

Adding fields to events without thinking about consumers; removing or renaming fields and discovering the breakage in production. Events live forever in the log; consumers may be running old code, new code, or replaying historical data. Casual schema changes break all three.

#### What to do instead

Treat event schemas as versioned public APIs. Additive changes only; new fields optional with sensible defaults; deprecation cycles for breaking changes; CI tests that verify backward and forward compatibility.

---

### ⚠️ The unbounded retention assumption

Designing the system as if events are kept forever, then discovering retention costs at scale and quietly truncating the log — which silently breaks replay, breaks backfill, breaks debugging, and breaks any consumer that assumed history was still there.

#### What to do instead

Retention is an explicit architectural decision. Some streams retain forever (event-sourced sources of truth), some retain for a defined window (operational signals), some are compacted (latest-value-per-key snapshots). The retention policy is part of the contract, not an operational adjustment.

---

### ⚠️ Eventual consistency by hope

Adopting event-driven architecture and assuming consumers will catch up "fast enough." Without backpressure handling, lag monitoring, and explicit consistency contracts with consumers, "eventual" can mean minutes, hours, or longer — and the rest of the system silently becomes broken in ways the team only discovers when a customer notices.

#### What to do instead

Lag is a measured property with explicit SLOs per consumer. Backpressure is handled architecturally. Consumers that fall behind raise alerts; consumers that fall too far behind have escalation paths (replay, backfill, manual intervention) that the team has practised.

---

### ⚠️ Time confusion

Treating processing time as event time and producing analytics that drift on outage days, double-count after replays, or miss late-arriving data entirely. Time semantics are not optional for windowed computation — they are the difference between correct and silently wrong.

#### What to do instead

Distinguish event time, ingestion time, processing time. Use event time for domain semantics; document watermarks and late-arrival policies; test that windowed analytics produce stable results under replay and out-of-order arrivals.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Events are named in past tense and describe facts in the producer's domain ‖ Naming reflects semantics. Events named like commands (DoThing, SendEmail) reveal that the architecture is using events as remote calls — collecting all the cost of asynchrony with none of the decoupling benefits the pattern was supposed to deliver. | ☐ |
| 2 | Each event stream's ordering guarantee is documented as part of the contract ‖ Total, per-key, or unordered are different commitments with different costs. Without a documented guarantee, every consumer is making an assumption — usually a wrong one — and the resulting bugs are hard to find and harder to reproduce. | ☐ |
| 3 | Event schemas are versioned and tested for backward and forward compatibility in CI ‖ Schemas evolve; the question is whether the evolution is safe. CI tests that verify a new event version can still be read by old consumers, and old events can still be read by new consumers, are what makes evolution routine rather than risky. | ☐ |
| 4 | Consumers are idempotent — replaying the same events produces the same effect ‖ Replay is a feature only if consumers handle it correctly. Without idempotency, every replay is a potential corruption event; with it, replay becomes a tool for debugging, schema migration, and recovery. | ☐ |
| 5 | Retention policy per stream is documented and enforced ‖ Some streams must retain forever; some have legal retention limits; some are operationally bounded. Without explicit policy, retention is whatever happened by default, and the team will discover the gap when replay fails on a real incident. | ☐ |
| 6 | Consumer lag is measured per consumer with documented SLOs ‖ Eventual consistency without lag bounds is just "consistent eventually, value of eventually unclear." SLOs make the consistency contract real and detectable when it breaks. | ☐ |
| 7 | Replay tooling exists and is exercised regularly, not improvised under pressure ‖ Replay during an incident is the first time any tool is used at scale; if that tool was written under pressure, it will fail under pressure. Routine exercise (rebuilding read models, backfilling new consumers) keeps the tooling and the team practised. | ☐ |
| 8 | Time semantics (event time vs. processing time) are explicit in stream-processing logic ‖ Time confusion produces silently wrong analytics. Explicit timestamps, documented watermarks, and tested late-arrival behaviour separate correct stream processing from "we hope the average lines up." | ☐ |
| 9 | A discoverable registry of producers, consumers, and event schemas exists ‖ Decoupling without discovery means producers cannot assess the impact of changes, and consumers cannot find the events they need. The platform's discovery layer is what makes decoupling productive rather than chaotic. | ☐ |
| 10 | Backpressure and overload handling are designed, not assumed ‖ When consumers cannot keep up, something has to give. Designed backpressure (slow producers, drop with policy, queue with limits) keeps the system predictable; un-designed backpressure produces cascading failures and surprise outages. | ☐ |

---

## Related

[`patterns/integration`](../../patterns/integration) | [`patterns/data`](../../patterns/data) | [`principles/cloud-native`](../../principles/cloud-native) | [`principles/foundational`](../../principles/foundational) | [`patterns/deployment`](../../patterns/deployment) | [`anti-patterns/distributed-monolith`](../../anti-patterns/distributed-monolith)

---

## References

1. [Martin Fowler — What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html) — *martinfowler.com*
2. [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) — *martinfowler.com*
3. [Martin Fowler — CQRS](https://martinfowler.com/bliki/CQRS.html) — *martinfowler.com*
4. [Apache Kafka — Documentation](https://kafka.apache.org/documentation/) — *kafka.apache.org*
5. [CloudEvents Specification](https://cloudevents.io/) — *cloudevents.io*
6. [Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — *dataintensive.net*
7. [Tyler Akidau et al. — The Dataflow Model](https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/) — *Google Research*
8. [Greg Young — CQRS Documents](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation) — *Wikipedia*
9. [Apache Pulsar](https://pulsar.apache.org/) — *pulsar.apache.org*
10. [AsyncAPI Specification](https://www.asyncapi.com/) — *asyncapi.com*
