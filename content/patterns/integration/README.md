# Integration Patterns

Architecture for the spaces between systems — the patterns for messaging styles, contracts, idempotency, and coordination that determine whether services compose into a product or merely accumulate alongside it.

**Section:** `patterns/` | **Subsection:** `integration/`
**Alignment:** Enterprise Integration Patterns | AsyncAPI | OpenAPI | CloudEvents

---

## What "integration patterns" actually means

A *call-it-and-hope* approach treats integration as plumbing: when service A needs something from service B, A makes a function-shaped call, B answers, A continues. When this works, it works invisibly. When it fails — and across hundreds of services, it fails constantly — every failure mode is an emergency someone has to invent the response to. The architecture has no opinion about how systems should communicate; communication just happens, and its consequences land in incident reviews.

An *integration-as-architecture* approach treats the spaces between systems as a first-class design surface. The choice of messaging style (synchronous request/response, asynchronous messaging, file transfer, shared state), the guarantees of each interaction (at-least-once, ordered, idempotent), and the coordination model (orchestrated workflow, choreographed events) are decisions made deliberately, documented explicitly, and propagated through every service that participates. Integration is not what services do *between* running their business logic; it *is* a substantial portion of their business logic, and pretending otherwise is the most common reason distributed systems are unmanageable.

The architectural shift is not "we use a message bus now." It is: **integration is the place where most distributed-systems failures live, and engineering it deliberately is what separates a coherent product from a federation of services that happen to share a customer.**

---

## Six principles

### 1. Choose the integration style based on coupling, not familiarity

The four canonical integration styles — file transfer, shared database, RPC (synchronous request/response), and messaging (asynchronous) — are not interchangeable. Each commits the participants to a different coupling profile. RPC couples in time: A waits for B to respond, A's failure mode includes B's failure modes. Messaging decouples in time: A drops a message and continues, B processes when available. Shared databases couple in schema, deployment, and operational responsibility. File transfers decouple in time and space but couple in format and timing windows. Choosing among these is a fundamental architectural commitment, not a "let's just use REST" reflex.

#### Architectural implications

- The default integration style for the system is named, with a written rationale.
- Each integration that deviates from the default is documented with the reason it deviates.
- The coupling profile of each style is understood by the team — not just "we picked sync because it's easier."
- Changing styles between services is treated as a real architectural change, not a refactor.

#### Quick test

> Pick your most recent service-to-service integration. Why was it implemented as a synchronous call rather than a message? If the answer is "we didn't think about it" or "that's how everyone does it here," the choice was made by default, not by design.

#### Reference

[Hohpe & Woolf, Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) — the integration styles chapter remains the canonical decomposition; everything since builds on it.

---

### 2. Idempotency is a contract, not an implementation detail

Networks fail. Messages get duplicated. Retries happen — they have to, because the alternative is silent data loss. Idempotency is what makes retries safe: an operation that produces the same effect whether it runs once or fifty times. Without idempotency, the choice is between "messages can be lost" and "messages can be processed multiple times with different cumulative effects." Both are usually unacceptable. Idempotency at the integration boundary is what makes both retries and replay possible — and it has to be specified as part of the contract, not hoped for in the implementation.

#### Architectural implications

- Every operation that crosses a system boundary is idempotent at the boundary by design, not by accident.
- Idempotency keys (request IDs, deduplication windows, version numbers) are part of the contract, declared and documented.
- The retention window for an idempotency key is matched to the maximum retry interval of the consumers using it.
- Operations that cannot themselves be idempotent (side-effecting external systems, third-party APIs) are wrapped by an idempotent envelope owned at your boundary.

#### Quick test

> What happens if your most-called API receives the same request twice in 10 seconds? If the answer is "two records get created" or "the second one fails with a 500," idempotency is not a property of the contract — and every retry policy across the system is loaded with risk that nobody is owning.

#### Reference

[Pat Helland, Idempotence is Not a Medical Condition](https://queue.acm.org/detail.cfm?id=2187821) — the foundational treatment, and still the clearest articulation of why this matters at scale.

---

### 3. Asynchronous communication is a different programming model, not an optimization

When teams move from synchronous calls to asynchronous messaging, the common framing is "we made it faster" or "we decoupled the systems." Both are true effects, but neither is the underlying change. The underlying change is that the programming model is different: error handling no longer flows through return values; ordering is no longer guaranteed by the call stack; observability moves from spans to message audit logs; the meaning of "the operation succeeded" requires a definition. Teams that adopt async without acknowledging the model shift import the rules of synchronous programming into a paradigm where they no longer hold — and discover, during incidents, that the rules they relied on no longer apply.

#### Architectural implications

- Error handling in async systems is designed (dead-letter queues, retry topologies, alerting), not inherited.
- Ordering guarantees (per-key, global, none) are explicit contracts in every async interaction.
- The boundary between "operation initiated" and "operation completed" is observable, with timestamps and status independently retrievable.
- Async interactions have idempotency, timeouts, and back-pressure handling at every step — not as nice-to-haves but as load-bearing structure.

#### Quick test

> In your most recent async workflow, what guarantees the eventual completion of a request — and how does the originator know it completed? If the answer is "the consumer logs success" or "we'd check the database," the model shift hasn't fully landed: there is no architecturally explicit completion contract.

#### Reference

[Pat Helland, Life Beyond Distributed Transactions](https://queue.acm.org/detail.cfm?id=3025012) — the long-form argument for why async changes everything, and why pretending otherwise is so consistently expensive.

---

### 4. Choreography and orchestration are different governance models

For a workflow that spans multiple services, two architectural choices exist. Orchestration: a central coordinator (workflow engine, state machine, dedicated service) knows the steps and tells each participant what to do, in order, with retries and rollback. Choreography: each participant knows the rules of engagement and reacts to events from others; no central coordinator exists. Both can produce correct, scalable systems. They differ in *who has visibility* into the workflow, *who can change it*, and *who is responsible when it breaks*. Picking unconsciously means picking the governance model unconsciously — and discovering it during the postmortem of the first cross-service incident.

#### Architectural implications

- For each multi-service workflow, the coordination model is named: orchestration, choreography, or explicit hybrid with documented boundaries.
- Orchestrated workflows have an obvious owner; choreographed workflows have a conscious agreement among the participating teams.
- The visibility of a workflow's current state is designed: orchestrators expose state directly; choreographies require event-trace tooling.
- Workflow changes follow the chosen model: orchestrator changes are made in one place; choreography changes require coordinated updates across services and explicit versioning.

#### Quick test

> Pick a workflow that spans three or more of your services. Who owns it, end to end? If the answer is "no single team — the participants own their parts," that is choreography. If the answer is "the workflow service" or "the X orchestration tool," that is orchestration. If the answer is "I don't know," the governance model is whatever happened by accident.

#### Reference

[Chris Richardson, Saga Pattern](https://microservices.io/patterns/data/saga.html) — the orchestration vs. choreography discussion in the saga implementation context, with concrete trade-offs.

---

### 5. Canonical data models are integration anti-patterns at scale; transform at boundaries

The canonical data model approach — define one Master Customer schema, one Master Order schema, force every system to use them at the integration boundary — is appealing because it sounds clean. In practice it produces a god-schema that grows to accommodate every integration's edge cases, becomes the slowest-changing piece of the architecture, and ages into "we can't change it because seventeen systems use it." The alternative is small, local transforms at each integration boundary: each integration defines what it needs in its own terms, and a transform layer maps between local models and partner models. This is more code, but the code is local, owned, and replaceable.

#### Architectural implications

- No single schema is forced as the universal contract across all integrations.
- Each integration boundary has its own transform layer, owned by the team that owns the integration.
- When two systems need to exchange data, they negotiate a contract bilateral to that integration — not a contribution to a global schema everyone else has to live with.
- The cost of N transforms across N integrations is accepted as the price of being able to change one integration without coordinating with all others.

#### Quick test

> If you needed to add a new field to one integration today, how many other integrations or teams would need to be involved? If the answer is "all of them, because the schema is shared," the canonical data model is producing exactly the coupling it was meant to prevent.

#### Reference

[Hohpe & Woolf, Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) — the Canonical Data Model pattern is described alongside the trade-offs that make it dangerous as systems and team counts grow.

---

### 6. The integration contract is the architecture; the transport is detail

Whether messages flow over REST, gRPC, Kafka, RabbitMQ, or HTTP/2 streams, the transport is largely interchangeable from an architectural standpoint. What matters is the contract: the messages exchanged, their semantics, the ordering guarantees, the idempotency rules, the failure modes, the versioning policy, the error model. Most teams arguing about integration are actually arguing about transport ("should we use Kafka or RabbitMQ?") when the architectural decisions live in the contract layer ("what messages, what guarantees, what failure handling?"). Get the contract right and the transport choice is replaceable; get the transport right and a poorly-designed contract still produces an unmanageable integration.

#### Architectural implications

- Integration contracts are documented as first-class artifacts (OpenAPI, AsyncAPI, Protobuf schemas), versioned, and reviewed alongside the code that implements them.
- Failure semantics (retry, dead-letter, timeout, backoff) are part of the contract, not assumed at the transport layer.
- Versioning strategy (additive change, deprecation cycles, breaking-change handling) is explicit per contract.
- Transport changes (e.g., REST to gRPC) are routine when the contract is well-defined; they are crisis-level when the contract was implicit in the transport.

#### Quick test

> If you needed to change the transport for your most-used integration tomorrow — REST to gRPC, or HTTP polling to WebSocket — how much would change in the consumer code? If the answer is "everything, because the contract is implicit in the HTTP semantics," the transport is doing the work the contract should be doing.

#### Reference

[AsyncAPI Specification](https://www.asyncapi.com/) and [OpenAPI Specification](https://www.openapis.org/) are the canonical contract definition languages for asynchronous and synchronous integration respectively. [CloudEvents](https://cloudevents.io/) provides a transport-neutral envelope for events.

---

## Architecture Diagram

The diagram below shows a canonical integration topology: a synchronous path through an API gateway with an OpenAPI contract, and an asynchronous path using the transactional outbox pattern, an event stream with an AsyncAPI contract, and idempotent consumers backed by a dead-letter queue for failed messages. Both paths are first-class, neither is a fallback for the other, and the contracts at each boundary are versioned alongside the code.

---

## Common pitfalls when adopting integration-pattern thinking

### ⚠️ The shared library masquerading as integration

A "client library" is shipped to every consumer of an API. To upgrade the API, every consumer must upgrade the library. To deploy a breaking change, every consumer must coordinate the deployment. The integration that should have been mediated by a contract is now mediated by a binary, and the deployment coupling that was supposedly removed by separating the services has been quietly reintroduced through their dependencies.

#### What to do instead

Boundaries are defined by contracts (OpenAPI, schema, message format), not by libraries. Generated client code is fine; required client libraries are not. The consumer should be free to consume the contract however they choose — including with a different language, framework, or version cadence than the producer.

---

### ⚠️ The chatty integration

A workflow that requires N+1 round-trips to complete one logical operation. Each round-trip is correct in isolation; together they multiply latency, multiply failure surface, multiply observability complexity. Often a symptom of a "let's just expose CRUD operations" approach, where the consumer must orchestrate the actual business operation themselves using your low-level building blocks.

#### What to do instead

Design the integration around the consumer's logical operation, not the producer's data model. Coarse-grained operations that match real use cases beat fine-grained CRUD that requires consumers to know your internals to do anything useful.

---

### ⚠️ Distributed transaction by accident

The pattern: service A writes to its database, service A calls service B, service B writes to its database. If the call to B fails, A has committed but B has not — the systems are now inconsistent. If A retries, B may double-process — the systems are now inconsistent in a different way. The team didn't intend to implement a distributed transaction; they implemented one accidentally and now own all its failure modes without any of its tooling.

#### What to do instead

Use the outbox pattern (write the message to your DB transactionally, deliver it asynchronously) or design the workflow as a saga with explicit compensation. Either way, the choice is conscious and the failure modes are designed in, not discovered during the first incident.

---

### ⚠️ Logs as message bus

Application logs are scraped by an aggregator, parsed for events of interest, and used to trigger downstream actions. This works until the log format changes (deployment), the volume increases (sampling), the aggregator falls behind (delays), or the parser misinterprets a new entry (silent bugs). What started as observability has become load-bearing infrastructure that nobody designed, nobody owns, and nobody can change without breaking something.

#### What to do instead

If service A needs to communicate with service B, that is an integration with a contract — design it as one. Logs are for human and machine inspection of system behavior, not for triggering business workflows; treating them otherwise produces brittle dependencies on what was meant to be a debugging surface.

---

### ⚠️ Polling that should be subscription

Service A asks service B for changes every minute. Service B has no changes 99% of the time. Service A's load on B is constant; B's actual work is intermittent. Multiply across hundreds of consumers and B is buried in pointless requests while delivering each consumer's update on an arbitrary delay. The consumers are doing the wrong thing, but the producer never told them what to do instead.

#### What to do instead

Push, don't poll. Webhooks, server-sent events, message subscriptions, change-data-capture streams — each turns "ask repeatedly" into "tell when there's news." If the producer doesn't expose a push mechanism, the producer is offloading their cost to consumers — and as the consumer count grows, they will eventually have to fix it under pressure.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | The default integration style across the system is named, with a documented rationale ‖ Without a default, every team picks differently and the consequences accumulate as architectural drift. Naming the default doesn't mean using it everywhere — it means deviations are conscious choices the team owns rather than accidents the team inherits. | ☐ |
| 2 | Every operation crossing a system boundary is idempotent at the boundary ‖ Network retries are not optional; they happen whether you designed for them or not. Idempotency at the boundary is what makes retries safe rather than data-corrupting; pushing it into "the application logic should handle it" is an organisational way of pushing the bug forward. | ☐ |
| 3 | Idempotency keys, retention windows, and conflict semantics are part of every contract ‖ "It's idempotent" without a key is not an idempotency commitment, it is a hope. Keys, retention windows, and what happens during overlap are the actual specification — without them, two implementations of the same contract can produce different behaviour and both will claim correctness. | ☐ |
| 4 | Failure semantics for each integration (retries, dead-letter, timeouts, back-pressure) are designed and documented ‖ Untreated failures are not failures that don't happen; they are failures whose handling is improvised at 2 AM. Designing them upfront is dramatically cheaper than improvising them during the incident that exposes the gap. | ☐ |
| 5 | Each multi-service workflow has a named coordination model: orchestration, choreography, or explicit hybrid ‖ Picking unconsciously means picking by accident, and accidents are surfaced by incidents. Both orchestration and choreography are valid; "we don't know what we have" is not — it is the absence of the architectural decision. | ☐ |
| 6 | Contract definitions (OpenAPI, AsyncAPI, schema) are first-class artifacts versioned with the code ‖ Contracts in tribal memory or "the JSON the API returns this week" are not contracts; they are surfaces that change without notification, and consumers discover the change through breakage. Formal contracts make change deliberate and reviewable. | ☐ |
| 7 | Backward and forward compatibility are explicit properties of every contract, tested in CI ‖ "Don't break consumers" without testing is hope. Contract tests in CI catch breakage before it ships, and they document the compatibility commitment as code rather than as a slogan that everyone interprets differently. | ☐ |
| 8 | No integration depends on a shared library that all consumers must upgrade in lockstep ‖ Required libraries replace contracts with deployment coupling. Generated clients and codified contracts are fine; required libraries are not, because they re-introduce the very coupling that separating services was meant to remove. | ☐ |
| 9 | Polling-based integrations have been audited and replaced with push where the producer can support it ‖ Polling moves cost to the wrong party (the consumer) and adds latency for the privilege. Push integrations require producer effort but are dramatically more efficient at scale, and the conversation about who pays the cost is itself an architectural conversation. | ☐ |
| 10 | Cross-service workflows have observable end-to-end traces, with correlation IDs propagated through every hop ‖ Without traces, debugging cross-service failures is forensic guesswork. Correlation IDs are cheap to add upfront, expensive to retrofit, and the difference between resolving an incident in fifteen minutes and resolving it in three hours. | ☐ |

---

## Related

[`principles/domain-specific`](../../principles/domain-specific) | [`principles/foundational`](../../principles/foundational) | [`principles/cloud-native`](../../principles/cloud-native) | [`patterns/data`](../data) | [`patterns/deployment`](../deployment) | [`anti-patterns/distributed-monolith`](../../anti-patterns/distributed-monolith)

---

## References

1. [Gregor Hohpe & Bobby Woolf — Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) — *enterpriseintegrationpatterns.com*
2. [Pat Helland — Idempotence is Not a Medical Condition](https://queue.acm.org/detail.cfm?id=2187821) — *ACM Queue*
3. [Pat Helland — Life Beyond Distributed Transactions](https://queue.acm.org/detail.cfm?id=3025012) — *ACM Queue*
4. [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html) — *microservices.io*
5. [AsyncAPI Specification](https://www.asyncapi.com/) — *asyncapi.com*
6. [OpenAPI Specification](https://www.openapis.org/) — *openapis.org*
7. [CloudEvents](https://cloudevents.io/) — *cloudevents.io*
8. [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html) — *martinfowler.com*
9. [Idempotence](https://en.wikipedia.org/wiki/Idempotence) — *Wikipedia*
10. [Message-Oriented Middleware](https://en.wikipedia.org/wiki/Message-oriented_middleware) — *Wikipedia*
