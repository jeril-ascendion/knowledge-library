# Data Patterns

Architecture for systems where data outlives the applications that created it — the patterns for ownership, evolution, consistency, and lineage that keep data debuggable, evolvable, and trusted across years and stores.

**Section:** `patterns/` | **Subsection:** `data/`
**Alignment:** Domain-Driven Design | CQRS Pattern | Event Sourcing | Polyglot Persistence

---

## What "data patterns" actually means

A *data-as-app-state* approach treats persistence as something the application does. The app owns the database schema, the app team handles migrations, and "data architecture" means whatever ORM the team picked. When a second application needs the same data, the simplest path is granting it database access — and the architecture's first major mistake has been made.

A *data-architecture* approach treats data as a first-class concern with its own architecture, separate from the applications that read or write it. Each persistent fact has a named owner. Each consumer accesses through a defined contract, not through a shared database connection. The data has shape (schema), consistency rules (transactional or eventual), classification (master, reference, transactional, analytical), and history (lineage). All of these are architectural decisions that survive across applications, refactors, and platform changes.

The architectural shift is not "we use a fancier database." It is: **data outlives the applications that created it; design accordingly.**

---

## Six principles

### 1. Each fact has one authoritative owner — the source of truth, by name

A data fact without a named owner is a data fact that will eventually be inconsistent. Multiple writers create irreconcilable state. When two systems both believe they are authoritative for a customer's email address, eventually one of them is wrong, and there is no architectural authority to resolve the conflict. The first data architecture decision is naming the source of truth for every persistent concept — *who* writes it, *who* propagates it, *who* arbitrates when they disagree.

#### Architectural implications

- Every persistent data class (customer, order, product, account) has exactly one owning team and one writeable store of record.
- Other systems read through replicas, projections, or events — they never write directly to the source.
- The authority to change source-of-truth ownership is explicit, documented, and tracked alongside other architectural decisions.
- "Master data management" is not a separate function; it is the discipline every domain team practices for the data they own.

#### Quick test

> For your most-debated piece of data — the one where two systems regularly disagree — name the system that is supposed to be authoritative. If the answer is "we sync them periodically," there is no source of truth, only two opinions and a sync job that loses every race.

#### Reference

The principle predates the relational database. It is documented across [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/) (Fowler) and [Designing Data-Intensive Applications](https://dataintensive.net/) (Kleppmann), and forms the basis of every master-data-management discipline.

---

### 2. The aggregate is the consistency boundary; across aggregates, consistency is eventual

Domain-Driven Design's most operationally consequential idea is that transactions span exactly one aggregate. Within the aggregate, invariants hold strongly: an order's total equals the sum of its line items, a balance never goes below zero, an entity's ID is unique. Across aggregates, consistency is eventual — and it is *designed for*, not assumed. Most database performance crises and most distributed-systems consistency disasters trace back to teams not making this choice deliberately.

#### Architectural implications

- Aggregate boundaries are documented explicitly, not implied by directory layout or table prefixes.
- A single transaction modifies exactly one aggregate; cross-aggregate operations propagate via events.
- Eventual consistency between aggregates is a designed property with defined SLOs, not an accident.
- Database constraints reflect aggregate invariants — not the union of every relationship in the system.

#### Quick test

> Pick a database transaction in your system that involves more than one table. Do those tables belong to the same aggregate? If they belong to different aggregates, you have either an aggregate boundary in the wrong place or a transaction that will eventually break under contention.

#### Reference

[Eric Evans, Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design) introduced the aggregate concept. [Vaughn Vernon's Implementing DDD samples](https://github.com/VaughnVernon/IDDD_Samples) show its operational consequences in working code.

---

### 3. Reads and writes are different problems; their models can diverge

The shape that's good for writes — normalised, transactionally consistent, easily validated — is rarely the shape that's good for reads — denormalised, fast to scan, joinable across patterns. A single model serving both compromises both: queries get slow, writes get complex, every optimisation creates a new tax somewhere else. CQRS (Command Query Responsibility Segregation) is the named pattern; the underlying principle is older. Splitting read and write models isn't always required, but the architecture must allow it when it becomes required.

#### Architectural implications

- Read access patterns and write access patterns for each capability are analysed separately, not assumed to share a model.
- The write model optimises for invariants and validation; read models optimise for query performance and shape.
- Read models are derived from the write model through projections — they are not separate sources of truth.
- Switching between "single shared model" and "separated read/write models" is an architectural option that can be exercised per capability when access patterns warrant it.

#### Quick test

> Is your most complex query running on the same schema that handles your highest-volume writes? If yes, every query optimisation compromises every write, and vice versa. The teams owning writes and the teams owning reads are paying each other's tax with every change.

#### Reference

[Martin Fowler, CQRS](https://martinfowler.com/bliki/CQRS.html). [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) is a related but distinct pattern that often appears alongside CQRS — the event log becomes the write model, and projections become the read models.

---

### 4. Schema is forever — design for additive change, not migration

Schemas change. Pretending otherwise is the most common, most expensive mistake in data architecture. Migrations of running systems are expensive, risky, and frequently require coordinated downtime. Additive change — adding optional fields, new tables, new event types — is cheap when the system is designed for it. The cost of designing for evolution is paid once; the cost of not designing for it is paid every quarter, in migration projects nobody enjoys.

#### Architectural implications

- New fields are added as optional or nullable; consumers handle their absence gracefully.
- Breaking changes (renames, removed fields, type changes) are deprecated through versioning cycles, not done in place.
- Schema validation rejects unknown fields at the producer; tolerates them at the consumer (Postel's law applied to data).
- Forward and backward compatibility are explicit properties of every published schema, tested in CI as part of every change.

#### Quick test

> Add a new optional field to the most central entity in your system. How many places must change before the system runs again? If the answer is "every consumer," the architecture has not been designed for schema evolution — every change will hurt, and many will be deferred until they hurt more.

#### Reference

[Martin Kleppmann, Designing Data-Intensive Applications](https://dataintensive.net/), Chapter 4 ("Encoding and Evolution"), is the modern reference. Apache Avro and Protocol Buffers codify the practice in their schema systems; their compatibility rules are worth reading even if you use neither.

---

### 5. Choose the store for the access pattern, not the other way around

One database type serving everything is one database type compromising everything. Relational stores excel at transactional consistency and complex joins; columnar stores excel at analytics; document stores excel at flexible-schema reads; search engines excel at text and faceted queries; graph stores excel at multi-hop relationships; key-value stores excel at simple, high-throughput access. Polyglot persistence is choosing each based on its access patterns, paying the cost of operational complexity deliberately rather than accidentally.

#### Architectural implications

- Each capability's access pattern (read shape, write shape, scale, latency budget) is analysed before the store is chosen.
- Store choices are recorded in ADRs naming the rejected alternatives, not just the selected one.
- The operational cost of each store (backups, monitoring, scaling, on-call expertise) is accepted as a known investment.
- Adding a new store type requires both an architectural justification and an operational plan, signed by the team that will own it on-call.

#### Quick test

> List the data stores in your production system. For each one beyond the first, name the access pattern that justifies its presence. If the honest answer for any of them is "we wanted to try it," that store has no business case — and probably no engineer who can debug it under pressure.

#### Reference

[Martin Fowler, Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html). [Designing Data-Intensive Applications](https://dataintensive.net/) provides the operational depth on each store family and how to reason about the choice.

---

### 6. Data lineage is architecture, not metadata

Where did this fact come from? What did it look like yesterday? Who changed it? When? Without answers to these, every incident becomes forensic guesswork — and every regulatory inquiry becomes a panic. Data lineage and provenance are not an audit feature added before a compliance review; they are properties the architecture either has or doesn't, designed in from the start or absent thereafter.

#### Architectural implications

- Every data flow that crosses a system boundary records its source, transformation, and timestamp as first-class metadata.
- Lineage metadata is queryable through the same tools that query the data itself — not buried in pipeline configuration or tribal knowledge.
- Schema changes, ETL jobs, and data corrections are first-class events with their own audit trail, not background activities.
- PII, secrets, and regulated data are tagged at the schema level, with classification flowing through every transformation downstream.

#### Quick test

> Pick a metric on your most important dashboard. Trace it back to source records — through every transformation, every join, every filter — without asking another engineer. How long does it take? If the answer is "we'd have to read code," lineage isn't part of the architecture; it lives in the heads of three people who are too busy to write it down.

#### Reference

[OpenLineage](https://openlineage.io/) is the emerging open standard for cross-platform lineage. The discipline pre-dates it: Pat Helland's work on data architecture has shaped the conversation for decades and remains essential reading.

---

## Architecture Diagram

The diagram below shows the canonical write-side / read-side data architecture: an aggregate root holds the source of truth in a transactional store; events propagate every change through a stream; multiple read-side projections (search, analytical, cache) serve different access patterns; lineage captures every flow that crosses a boundary.

---

## Common pitfalls when adopting data-architecture thinking

### ⚠️ The shared database

Multiple services writing to the same tables, on the theory that "data should be one database." The fastest path to a distributed monolith — every schema change couples every service that touches it, and "we'll just coordinate" doesn't survive five teams. The cure looks like more work; the disease *is* more work, paid in slow incidents.

#### What to do instead

Each service owns its tables; cross-service access is through APIs, events, or read-only replicas — never through shared write access. Treat the database as an internal implementation detail of the owning service, not as a public integration surface.

---

### ⚠️ Eventual consistency by default

Choosing eventual consistency reflexively because someone said "scale," then accepting all the resulting complexity in the application layer — order ID lookups that sometimes fail, balances that briefly disagree, customers seeing yesterday's price. Eventual consistency is a real architectural choice with real costs; accepting it for capabilities that don't need it imports those costs for no benefit.

#### What to do instead

Classify each capability by its consistency needs. Strong consistency where invariants must hold (charges, inventory commits, identity assignments). Eventual where it's acceptable (analytics, recommendations, search indexes). Hybrid where it makes sense (write-strong, read-eventual). The choice is per-capability, not per-system.

---

### ⚠️ The grand schema migration

Big-bang schema changes that require coordinated downtime — usually because the schema was designed for the past and never evolved. Each migration becomes its own project, with stakeholders, project managers, and a date that slips. Three or four of these and the team will avoid changing the schema at all, which means the schema lies about reality forever.

#### What to do instead

Online schema evolution as a routine practice — add fields without breaking consumers, backfill in batches, rename through deprecation cycles. Tooling (gh-ost, pt-online-schema-change, online migration libraries) makes this routine; additive-change discipline keeps it safe.

---

### ⚠️ Lineage as compliance afterthought

Treating data lineage as a feature to add when regulators ask, rather than a property the architecture should have from day one. The cost of retrofitting lineage across an existing system is roughly equivalent to rewriting it; the cost of designing it in from the start is closer to free.

#### What to do instead

Capture lineage at every cross-boundary data flow from the start. The cost is small per pipeline; the cost of having it later when an incident or audit demands it is enormous. Treat lineage like observability — engineered in, not bolted on.

---

### ⚠️ Polyglot persistence for resume value

Adding new data store types because they're interesting, not because the access pattern requires them. The result is operational complexity nobody owns: a Cassandra cluster nobody patches, an Elasticsearch deployment three engineers know how to debug, a graph database whose schema lives in one person's head and disappears when they leave.

#### What to do instead

Each new store added must answer "what access pattern requires this that the existing stores cannot serve?" — and have an explicit owner accepting operational responsibility before deployment. Resume-driven persistence is a real failure mode; name it in design review when you see it.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Every persistent data class has a named, documented owner team ‖ Without an owner, every schema change is a multi-team negotiation. With one, change is routine. Look at your data catalogue (or wiki, or Slack channel where data questions land) — for each major data class, a single team should be the unambiguous answer to "who owns this?" | ☐ |
| 2 | Aggregate boundaries are explicit and reviewed alongside the database schema ‖ Aggregate boundaries are not implied by table names. They define what transactions are atomic versus eventually consistent. If aggregates are not documented explicitly, any new schema change will accidentally violate one and nobody will notice until an incident exposes the inconsistency. | ☐ |
| 3 | Schema migrations are routine, automated, and run online — no downtime ‖ Migrations as one-off projects with dedicated downtime windows are the surface symptom of brittle data architecture. Online migration tools and additive-change discipline turn migrations into low-risk routine changes the team runs every Tuesday without ceremony. | ☐ |
| 4 | Read access patterns and write access patterns are analysed separately for each major capability ‖ A single shared model serving both reads and writes is a series of compromises, both for query performance and for write integrity. Separating them when needed is an option that requires architectural design, not a refactor under pressure during a performance incident. | ☐ |
| 5 | Data classification is documented (transactional / reference / master / analytical) with rules for each ‖ The handling rules differ by classification — transactional needs ACID, reference data can be cached, analytical can be batch, master data needs cross-system propagation. Without classification, the same rules get applied to all, and nothing fits. | ☐ |
| 6 | The data store choice for each capability is recorded in an ADR naming rejected alternatives ‖ "We use Postgres for everything" might be the right answer, but it should be a documented choice, not a default. ADRs that name the alternatives considered (and why rejected) prevent the choice from being relitigated every six months when a new senior engineer joins. | ☐ |
| 7 | Cross-store consistency is an intentional design choice — not implicit ‖ When data flows across stores, the consistency model must be chosen: strong, eventual, causal. Eventual is the default in distributed systems, but "default" doesn't mean "free" — application code has to handle it. Choosing forces the team to think about failure modes; not choosing means they will think about them during an incident instead. | ☐ |
| 8 | Lineage and provenance are captured for every data flow that crosses a system boundary ‖ Without lineage, debugging cross-system data issues is forensic archaeology. With it, the team can answer "where did this fact come from" in seconds. The cost of retrofitting lineage across an existing system is large; the cost of designing it in is small. | ☐ |
| 9 | PII, secrets, and regulated data are tagged at the schema level, enforced by tooling at write time ‖ Policy alone doesn't prevent regulated data leaking into logs, analytics tables, or developer environments. Schema-level tagging plus automated enforcement (linters, masking-on-export, policy-as-code) makes the right thing the easy thing — and the wrong thing harder than the right one. | ☐ |
| 10 | Backfill, rollback, and disaster-recovery procedures are tested under production-like load ‖ Untested DR is theatre. The team must have actually backfilled, rolled back, and recovered, on a system close enough to production, recently enough that the procedure still applies. If DR has not been exercised this quarter, assume it will fail when it matters most. | ☐ |

---

## Related

[`principles/foundational`](../../principles/foundational) | [`principles/domain-specific`](../../principles/domain-specific) | [`principles/cloud-native`](../../principles/cloud-native) | [`patterns/integration`](../../patterns/integration) | [`patterns/distributed`](../../patterns/distributed) | [`anti-patterns/shared-db-context`](../../anti-patterns/shared-db-context)

---

## References

1. [Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — *dataintensive.net*
2. [Martin Fowler — Patterns of Enterprise Application Architecture Catalog](https://martinfowler.com/eaaCatalog/) — *martinfowler.com*
3. [Martin Fowler — CQRS](https://martinfowler.com/bliki/CQRS.html) — *martinfowler.com*
4. [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) — *martinfowler.com*
5. [Martin Fowler — Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html) — *martinfowler.com*
6. [Eric Evans — Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design) — *Wikipedia*
7. [Vaughn Vernon — Implementing Domain-Driven Design Samples](https://github.com/VaughnVernon/IDDD_Samples) — *GitHub*
8. [ACID Properties](https://en.wikipedia.org/wiki/ACID) — *Wikipedia*
9. [Eventual Consistency](https://en.wikipedia.org/wiki/Eventual_consistency) — *Wikipedia*
10. [OpenLineage — Data Lineage Standard](https://openlineage.io/) — *openlineage.io*
