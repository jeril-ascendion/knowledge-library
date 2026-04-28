# Scalable Systems

Architecture for systems that absorb growth — more users, more data, more traffic, more concurrent operations — without rewriting from the foundations every time the load doubles. Scalability is not a feature added at the end; it is a set of decisions made early about where bottlenecks are allowed to form, how they are detected, and what is done when they do.

**Section:** `system-design/` | **Subsection:** `scalable/`
**Alignment:** CAP Theorem | Reactive Manifesto | Twelve-Factor App | Site Reliability Engineering

---

## What "scalable" actually means

A *scale-by-default* approach assumes the cloud will handle scale: add more instances, increase the database size, configure autoscaling, raise the rate limits. This works until it does not — and the moment it stops working is rarely a gradual slowdown. It is a sudden cliff, where adding more instances no longer helps because the bottleneck has moved to a place autoscaling cannot reach: a database connection pool, a downstream rate limit, a synchronisation primitive, a network egress quota. The team that scaled by default discovers the bottleneck for the first time when the system is on fire.

A *scale-by-design* approach treats scalability as a property of the architecture, not the infrastructure. Bottlenecks are identified before they are encountered. Caches, queues, partitioning strategies, and async paths are placed deliberately at the points where load would otherwise concentrate. The trade-offs each pattern accepts (eventual consistency, complexity, operational overhead) are evaluated against the load profile they are meant to handle. Capacity is forecast and planned, not discovered when the alert fires.

The architectural shift is not "we use a cloud autoscaler." It is: **scale is a property the architecture either has or does not have, and adding it after the fact is harder, more expensive, and slower than designing for it from the start — but designing for scale that never materialises is also expensive, so the discipline is matching the architecture to the actual growth profile rather than to the imagined one.**

---

## Six principles

### 1. Scale by removing bottlenecks, not by adding hardware

The instinctive response to a slow system is to add hardware: more CPU, more memory, more instances, a bigger database. This works only when the bottleneck is the hardware that was added — which, in mature systems, it usually is not. Bottlenecks live at synchronisation points: database locks, connection pools, downstream services with their own limits, single-threaded code paths, shared caches, network egress. Adding hardware *amplifies* the load arriving at the bottleneck without making the bottleneck wider. The first discipline of scalable systems is to identify the actual constraint — the resource whose saturation determines throughput — and address it. Until that resource is no longer the constraint, every other optimisation is wasted effort.

#### Architectural implications

- Capacity work begins with measurement: where is time actually spent under load, what resource saturates first, what does the queue look like at that resource.
- Adding hardware is one option among many — alongside caching, partitioning, async paths, batching, removing work entirely — and is chosen because it addresses the actual constraint, not because it is the easiest dial to turn.
- The team has explicit awareness of where the next bottleneck will appear after the current one is fixed; addressing one bottleneck without knowing the next leads to short-lived wins.
- The Theory of Constraints applies: throughput is determined by the slowest step; speeding up any step that is not the slowest does not improve throughput at all.

#### Quick test

> Pick a recent scaling effort in your system. What was the actual bottleneck, and how did the team know? If the answer is "we tried adding more instances and it got better," the bottleneck happened to be at the layer that was scaled — but the team has not built the muscle to identify the next one before it bites.

#### Reference

[Brendan Gregg — Systems Performance](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) — the canonical treatment of identifying the actual bottleneck through measurement rather than speculation, with the USE method (Utilisation, Saturation, Errors) as the practical entry point.

---

### 2. Vertical scale is finite; horizontal scale needs design

Vertical scaling — making a single machine larger — is the simplest scaling pattern and the first to fail. Single machines have hard limits: the largest available CPU, the largest available memory, the maximum NIC throughput, the operating system's overhead. These limits arrive sooner than expected, and the cost curve approaches infinity well before the limit. Horizontal scaling — adding more machines — has higher ceiling but requires architectural decisions vertical scaling does not: how is state partitioned across instances, how is work distributed, how do instances coordinate without becoming a bottleneck themselves. Systems that scale vertically until they cannot, then attempt to scale horizontally as an emergency, discover that the architecture they relied on does not support what they now need.

#### Architectural implications

- Stateless services scale horizontally trivially; stateful services require explicit partitioning, replication, or both.
- Partition keys are chosen deliberately to distribute load evenly; bad partition keys produce hot shards that re-create the original bottleneck at smaller scale.
- Coordination overhead at scale (consensus, locking, leader election) is recognised as a scaling boundary; designs that avoid coordination scale further than designs that require it.
- Vertical scale is a temporary measure for stateful components, not a strategy — the path to horizontal scale is mapped before the vertical limit is reached.

#### Quick test

> Pick a stateful component in your system. What is its current size, what is the largest size available from your provider, and what is the architectural plan when that limit arrives? If the plan is "we'll figure it out then," the system has a hard ceiling that the team has chosen not to see yet.

#### Reference

The [Twelve-Factor App](https://12factor.net/) — the foundational reference for stateless service design that makes horizontal scaling viable; statelessness is the precondition that turns "add more instances" from a hopeful action into an architectural pattern.

---

### 3. Caching is invalidation; the rest is detail

Phil Karlton's old line — "there are only two hard things in computer science: cache invalidation and naming things" — is sometimes treated as a joke. It is not. Caching trades correctness (freshness) for performance (latency, load reduction), and the trade is governed by invalidation: when does the cache return stale data, when does it return correct data, who decides, what happens when the decision is wrong. A cache without an invalidation strategy is a bug accumulator. A cache with the wrong invalidation strategy is worse than no cache, because it produces wrong answers fast. The architectural decision in caching is not "should we cache" — it is "what is our staleness contract, and how is it enforced." Until that question is answered, the cache is a bet on the cost of being wrong being lower than the cost of being slow, made without consulting either cost.

#### Architectural implications

- Each cache has a documented staleness contract: how stale can the data be before it is incorrect, who can read stale data, who must always read fresh.
- The invalidation mechanism (TTL, event-based, write-through, manual purge) is chosen to enforce the staleness contract — not chosen for ease of implementation.
- Cache stampede protection (singleflight, request coalescing, jittered expiry) is part of the design at any meaningful scale; without it, the moment a hot cache entry expires, the upstream is overwhelmed by simultaneous reloads.
- The behaviour when the cache is unavailable, partitioned, or evicted is designed — not assumed to be "things are slower" when in practice it can be "things are broken."

#### Quick test

> Pick a cache in your system. What is its staleness contract — that is, what is the maximum acceptable age of data it returns, and what determines when an entry is invalidated? If the answer is "we have a TTL of 5 minutes," that is the mechanism but not the contract; the contract is what the rest of the system is allowed to assume about freshness, which is a different question.

#### Reference

[Caching strategies — AWS Architecture Blog](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/welcome.html) — a practical treatment of the cache patterns (read-through, write-through, write-behind, cache-aside) and the freshness/correctness trade-offs each accepts.

---

### 4. The CAP theorem is a budget, not a choice

The CAP theorem says that a distributed system cannot simultaneously provide consistency, availability, and partition tolerance — it can have any two but not all three. In practice, partition tolerance is mandatory (networks partition; the only choice is what to do when they do), so the real question is whether to sacrifice consistency or availability during a partition. Most popular discussions of CAP treat this as a one-time architectural decision (CP system or AP system) — but the actual practice is finer. Different operations in the same system have different needs. A bank balance read may need strict consistency; a feed of recent activity may tolerate eventual consistency. Treating CAP as a budget — different parts of the system spend C and A differently, deliberately, with awareness — produces architectures that fit the domain rather than that fit the database.

#### Architectural implications

- Each operation in the system has a documented consistency requirement (strict, eventual, monotonic, session, etc.) chosen against the domain's actual need.
- Partition behaviour is documented per operation: what does the system do during a network partition, which operations continue, which are rejected, which return potentially stale data.
- Mixed-consistency architectures are designed deliberately: strongly-consistent stores for the operations that need them, eventually-consistent stores for the operations that can absorb the trade-off.
- The cost of strict consistency at scale (latency, throughput limits, partition behaviour) is visible in capacity planning, not absorbed silently into the architecture.

#### Quick test

> Pick an operation in your system that reads data. What consistency does it actually provide, and is that consistency enough for the domain? If the operation reads from a cache or replica without knowing how stale the answer might be, the consistency contract is whatever happens to be true today — which is not a contract.

#### Reference

[Eric Brewer — CAP Twelve Years Later: How the "Rules" Have Changed](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/) — the original author's revisit of CAP, clarifying that the "two of three" framing is too coarse and that real systems navigate the trade-offs at finer granularity.

---

### 5. Backpressure is a system property; design for graceful slowdown

When a producer generates work faster than consumers can process it, something has to give. Without explicit backpressure handling, the something is usually memory: queues grow without bound until the consumer process runs out of memory and dies, taking the work in flight with it. With explicit backpressure, the producer is signalled to slow down, drop work according to policy, or queue with bounded capacity. The architecture either has backpressure designed in — flow control, bounded queues, drop policies, slow-producer signalling — or it has unbounded queues that work until they don't. Unlike many architectural choices, this one is invisible at low load: a system without backpressure looks identical to a system with backpressure when the load is far below capacity. The difference appears only when load matches or exceeds capacity, at which point it determines whether the system slows down gracefully or collapses entirely.

#### Architectural implications

- All inter-component queues have explicit bounds and policies for what happens when the bound is reached (drop oldest, drop newest, reject, block).
- Producers receive backpressure signals from consumers and have explicit logic for what to do (slow down, shed load, escalate) — not just "send and hope."
- The end-to-end flow control story is documented: which components can push back, which must accept work unconditionally, where the boundary is between "the system slows down" and "the system rejects requests."
- Load shedding policies are designed: which requests are dropped first, which are protected, what users see when their requests are shed.

#### Quick test

> Pick the busiest internal queue in your system. What is its maximum size, what happens when it reaches that size, and what does the producer of work into that queue see when it does? If the answer is "we have a queue but no explicit limit," the system has been working because it has not yet been pushed past its limit.

#### Reference

[The Reactive Manifesto](https://www.reactivemanifesto.org/) — the explicit articulation that elastic, resilient, message-driven systems must use non-blocking back-pressure as a first-class property of their inter-component contracts.

---

### 6. Capacity planning is a forecasting discipline, not a one-time exercise

Scale is not a state — it is a trajectory. The system that handles current load with margin will, given sustained growth, eventually run out of margin. The system that "scales infinitely" because it is on Kubernetes still has billing limits, database connection limits, third-party API quotas, and team operational capacity. Capacity planning — projecting load growth, identifying the next constraint that will saturate, planning for its mitigation, and tracking actuals against forecasts — is what turns scaling from reactive (the alert fired, what now) to proactive (we expect to hit this limit in Q3, and the work to address it is in the roadmap). Without this discipline, the team scales by responding to incidents, which is more expensive than scaling by forecast and produces worse outcomes for everyone involved.

#### Architectural implications

- Load growth (users, requests, data volume, concurrent operations) is measured and trended; the team knows what next quarter looks like, not just what last quarter looked like.
- Resource utilisation is tracked against capacity, with alerts at planning-relevant thresholds (60–70%) rather than crisis-relevant thresholds (95%+).
- Each major component has a documented next-bottleneck — the resource that would saturate first under continued growth — and a plan for addressing it before it does.
- Quotas, limits, and allocations from upstream services (cloud provider, third parties, internal platforms) are tracked as constraints, not assumed to be infinite.

#### Quick test

> Pick a system you operate. What is the projected load 6 months from now, what is the resource that would saturate first under that load, and what is the plan for addressing it? If those questions cannot be answered, capacity planning is happening reactively — which is to say, it is not happening, and the team will rediscover the limits expensively.

#### Reference

[Site Reliability Engineering — Capacity Planning](https://sre.google/sre-book/software-engineering-in-sre/) — Chapter 18 covers the forecasting and resource-modelling discipline that distinguishes proactive scaling from incident-driven reaction; the treatment is platform-agnostic and applies regardless of which provider or technology stack is used.

---

## Architecture Diagram

The diagram below shows a canonical scalable topology: stateless application tier behind a load balancer; bounded queues between asynchronous stages; a partitioned data tier with read replicas for read scaling; a cache layer with explicit invalidation; rate limiting at the edge; capacity headroom on every tier with monitoring at planning-relevant thresholds.

---

## Common pitfalls when adopting scalability thinking

### ⚠️ Premature scaling

Designing for ten million users on day one when the actual load is ten. The architectural complexity (sharding, queues, multi-region, eventual consistency) is paid up front in development time, operational overhead, and bug surface area — and amortised against load that may never arrive. The system is hard to operate and slow to evolve while waiting for the demand it was built for.

#### What to do instead

Match architectural complexity to actual or imminent load. Start simpler than you think you need; design with awareness of where complexity will be added when load arrives; refactor toward complexity in response to evidence rather than imagination.

---

### ⚠️ The hot shard

Partitioning by a key that is not evenly distributed: tenant ID where one tenant has 80% of the traffic, user ID where active users are concentrated, geographic region where one region dominates. The partitioning *technique* is correct but the partitioning *key* is wrong, and the hot shard becomes the bottleneck the partitioning was supposed to eliminate.

#### What to do instead

Partition keys are chosen against actual data distribution, not against what feels natural. Distribution is measured before partitioning is committed to. Where distribution is uneven, secondary partitioning, salting, or different patterns are used.

---

### ⚠️ Cache as correctness layer

Using a cache to "fix" a slow query, then discovering that consumers are relying on cached data being current. The cache became part of the correctness contract without anyone deciding it should be. When the cache misses or is purged, behaviour subtly changes in ways the rest of the system did not anticipate.

#### What to do instead

Caches are performance optimisations, not correctness mechanisms. Staleness contracts are explicit; consumers know how fresh the data is allowed to be; the system works correctly with the cache absent (just slower).

---

### ⚠️ Unbounded queues

Queues with no maximum size, accepted as "we'll set a limit later." Under sustained overload, the queue grows until the process runs out of memory, at which point the queue is dumped — losing every message in it — and the system restarts to face the same overload that filled the queue in the first place.

#### What to do instead

Every queue has an explicit bound and an explicit policy for what happens at the bound. The policy is chosen deliberately (drop oldest, drop newest, reject, block) based on what the domain can tolerate.

---

### ⚠️ Capacity discovered at saturation

The first time the team learns about a capacity limit is when the alert fires at 95% utilisation. By then, the response is reactive: emergency provisioning, panicked refactoring, customer-visible degradation. The team's capacity planning consists of waiting for problems to surface and then addressing them.

#### What to do instead

Capacity is forecast quarterly, tracked against actuals, and alerted at planning thresholds (60–70% utilisation, growth trajectory exceeding plan) — not crisis thresholds. The work to address the next bottleneck is in the roadmap before the bottleneck arrives.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Bottleneck identification is data-driven, using measurement of actual resource saturation under load ‖ Adding hardware to the wrong resource is expensive theatre. The team knows where time is actually spent under load, where queues form, and which resource saturates first — and addresses that resource specifically. | ☐ |
| 2 | Stateless services are the default; stateful components have a documented horizontal-scale path ‖ Vertical scale ends; horizontal scale needs design. The path from "this component is currently vertical-scaled" to "this component scales horizontally" is mapped before the vertical limit is reached. | ☐ |
| 3 | Each cache has a documented staleness contract and explicit invalidation strategy ‖ Caches without contracts become hidden correctness mechanisms. Explicit staleness contracts let downstream consumers reason about freshness; explicit invalidation strategies make the contract enforceable rather than aspirational. | ☐ |
| 4 | Partitioning keys are chosen against measured data distribution, not assumed distribution ‖ Hot shards arise from partitioning keys that seem reasonable but distribute unevenly in practice. Measuring distribution before committing to a partition strategy prevents the bottleneck from re-forming at a smaller scale than the original. | ☐ |
| 5 | Each operation has a documented consistency requirement matched against domain need ‖ One-size-fits-all consistency (everything strict, or everything eventual) leaves money on the table or correctness on the floor. Per-operation consistency lets the architecture spend the CAP budget where the domain actually requires the spend. | ☐ |
| 6 | Inter-component queues have explicit bounds and explicit overflow policies ‖ Unbounded queues are time bombs. Bounded queues with documented overflow behaviour (drop, reject, block) make the system's behaviour under sustained overload predictable rather than catastrophic. | ☐ |
| 7 | Backpressure flows end-to-end through the system, not just at the edges ‖ When one component cannot keep up, that signal must propagate to the producers feeding it. End-to-end backpressure prevents the failure mode where the front door accepts work the backend cannot complete, accumulating broken promises. | ☐ |
| 8 | Capacity utilisation is alerted at planning thresholds, not crisis thresholds ‖ Alerts at 95% utilisation are crisis alerts; alerts at 60–70% are planning alerts. The latter give the team time to address growth before it becomes an incident; the former are notifications that the incident has begun. | ☐ |
| 9 | Load growth is measured, trended, and used as input to roadmap planning ‖ Capacity work in the next quarter's roadmap should be based on the load expected next quarter, not on what was painful last quarter. The forecast is updated as actuals come in and informs prioritisation, not just operational vigilance. | ☐ |
| 10 | Quotas, limits, and allocations from upstream dependencies are tracked as constraints ‖ Cloud providers have limits. Third-party APIs have rate limits. Internal platforms have allocations. The architecture treats each of these as a real constraint to be planned around — not as theoretically infinite resources that can be assumed away. | ☐ |

---

## Related

[`principles/cloud-native`](../../principles/cloud-native) | [`principles/foundational`](../../principles/foundational) | [`patterns/data`](../../patterns/data) | [`patterns/integration`](../../patterns/integration) | [`system-design/event-driven`](../event-driven) | [`system-design/ha-dr`](../ha-dr)

---

## References

1. [Eric Brewer — CAP Twelve Years Later](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/) — *InfoQ*
2. [The Reactive Manifesto](https://www.reactivemanifesto.org/) — *reactivemanifesto.org*
3. [The Twelve-Factor App](https://12factor.net/) — *12factor.net*
4. [Brendan Gregg — Systems Performance](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) — *brendangregg.com*
5. [Google SRE Book — Capacity Planning](https://sre.google/sre-book/software-engineering-in-sre/) — *sre.google*
6. [AWS — Database Caching Strategies using Redis](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/welcome.html) — *AWS*
7. [Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — *dataintensive.net*
8. [Little's Law](https://en.wikipedia.org/wiki/Little%27s_law) — *Wikipedia*
9. [Theory of Constraints](https://en.wikipedia.org/wiki/Theory_of_constraints) — *Wikipedia*
10. [Amdahl's Law](https://en.wikipedia.org/wiki/Amdahl%27s_law) — *Wikipedia*
