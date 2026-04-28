# Databases

**Data Persistence Strategies — navigating relational, NoSQL, and vector-based storage architectures.** Data is the asset clients trust us with, and the choices we make about where it lives, how it's shaped, and how it evolves outlive every application that touches it. This page describes how we approach the database landscape — relational, document, key-value, graph, time-series, vector, and the data warehouse — and how to match the store to the workload.

**Section:** `technology/` | **Subsection:** `databases/`
**Alignment:** PostgreSQL | MongoDB | Apache Kafka | Pinecone

---

## What "databases" actually means

The database is no longer one thing. Twenty years ago, "the database" meant a relational database, with a schema, with SQL. Today, a single application typically uses four or five distinct stores — relational for transactional truth, key-value for sessions, search index for full-text, document store for flexible schemas, message broker for event streams, vector store for embeddings, time-series for telemetry, graph for relationship traversal, data warehouse for analytics. Pretending one store fits all workloads forces every workload into the same shape, which is wrong for most of them. Choosing the right store per workload — *polyglot persistence* — is the architectural commitment that makes modern data platforms work.

The cost is real: more stores mean more operational surface, more skills, more integration. The discipline is choosing deliberately, bounding the polyglot, and treating the integration between stores as architecturally significant.

---

## Six principles

### 1. Database choices outlive the applications that use them

Most architectural decisions are revisable. A framework can be replaced over a year. A microservice can be rewritten. An infrastructure provider can be changed. But the database — once it holds production data, with schemas evolved over years, with operational tooling built around it, with a team that knows its quirks — is the architectural decision that sticks. Migrating from PostgreSQL to MongoDB, from Cassandra to a relational store, from one cloud's managed service to another, is multi-quarter work that disrupts the team and risks the data. The implication is that database choices deserve a longer evaluation horizon than other architectural decisions, and the criteria should weight long-term operability and team familiarity more heavily than short-term feature fit.

#### Architectural implications

- New database adoption is treated as a multi-year commitment, not a per-feature choice; the team that picks Cassandra for one feature is committing to operating it for the foreseeable life of the data.
- The operational cost (backups, upgrades, monitoring, capacity planning, security patching, expertise) of each new store class is a budget item evaluated over a 3–5 year horizon, not against the immediate use case.
- Migration cost and risk are factored into every "is this the right database" conversation; the right database for the next 3 years may not be the right database for today's narrow requirement.
- Database expertise is built deliberately — through training, deliberate practice, and hiring — not assumed because the technology is "popular" in the broader market.

#### Reference

[Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — the canonical reference for the long-horizon thinking that database choices require, including the migration patterns and operational properties that distinguish stores in practice.

---

### 2. Schema evolution is a continuous discipline, not a deployment event

The database schema is the longest-lived artefact in any application — the code changes monthly, the team changes annually, the schema changes daily and persists for years. A schema migration that requires downtime, a rollback that loses data, a column rename that breaks every consumer — these are operational events that interrupt every release. The mature alternative is an evolution discipline: additive changes only, dual-running readers and writers during transitions, contraction phases that remove deprecated columns long after no consumer reads them. Done well, the schema evolves continuously and invisibly; done poorly, every schema change is a coordination event the whole organisation feels.

#### Architectural implications

- Migrations are additive by default — new columns are nullable, new tables coexist with old, deprecated columns are removed in a separate phase.
- Online schema-change tools (gh-ost, pt-online-schema-change) are available and exercised; long-blocking ALTER TABLE is treated as a production incident.
- The application is decoupled from schema details by repository or DAO patterns — schema changes do not ripple through every layer of the codebase.

#### Reference

[Martin Kleppmann — Designing Data-Intensive Applications, Chapter 4](https://dataintensive.net/) — the canonical treatment of evolvability of data, including backward and forward compatibility patterns that scale to systems with many independently-deployed consumers.

---

### 3. Vectors are an index, not magic — apply the same operational discipline

Vector databases (Pinecone, Weaviate, Milvus, pgvector) are not magic — they are indexes over high-dimensional embedding spaces, with the same lifecycle concerns as any other index. The embeddings need to come from somewhere (which model, with which dimensions, normalised how), they need to stay current (when the source data changes, the embedding must too), they need to be tuned for retrieval (the right ANN algorithm, the right recall/latency trade-off). Treating "we put it in Pinecone" as the architecture, without thinking about the embedding lifecycle, produces semantic search that quietly degrades as the source data drifts, and the team only notices when a customer reports irrelevant results.

#### Architectural implications

- The embedding model is a versioned dependency — when it changes, the entire index is rebuilt; running mixed-version embeddings produces meaningless similarity scores.
- Embeddings are kept current — when source records change, embeddings are recomputed; stale embeddings are detected, not assumed away.
- ANN tuning (HNSW parameters, IVF parameters, recall-vs-latency trade-off) is documented and matched against the use case; defaults rarely match production needs.
- The path from a search query to source records is traceable — vectors are the *index*, not the source of truth.

#### Reference

[Pinecone — Vector Database Guide](https://www.pinecone.io/learn/vector-database/) — a practical industry treatment of vector indexing, ANN trade-offs, and the lifecycle considerations that distinguish working from failing semantic search.

---

### 4. Time-series is a structural pattern, not just a workload

Time-series workloads (metrics, telemetry, IoT, financial ticks) have specific structural properties — high write throughput, append-only, queries that aggregate by time window, retention that decreases for older data, compression that exploits temporal locality. General-purpose databases handle these workloads, but at significant cost: storage that grows unbounded, queries that slow down as data accumulates, expensive aggregations that re-scan months of data. Purpose-built time-series databases (InfluxDB, TimescaleDB, ClickHouse) optimise for the structural pattern: chunked storage, automatic downsampling, retention policies, columnar compression. Choosing the time-series structure deliberately — even when the data volume seems small — is what prevents the painful migration two years later when it isn't.

#### Architectural implications

- Time-series workloads use time-series stores or extensions (TimescaleDB on Postgres, ClickHouse, InfluxDB) — not general tables that happen to have a timestamp column.
- Retention policy is explicit and enforced: high-resolution data for X days, downsampled to Y resolution after that, expired entirely after Z.
- Aggregation queries hit pre-computed rollups, not raw data; the cost of dashboard rendering is bounded.

#### Reference

[TimescaleDB — Time-series data architecture](https://www.timescale.com/learn/time-series-databases) — an industry treatment of why general-purpose stores fail at time-series workloads and what the structural pattern actually requires.

---

### 5. Graph problems hide in relational data; recognising them is the architecture

Some queries — multi-hop relationship traversals, shortest path, community detection, recursive ancestry — get exponentially harder in relational form because each hop is a join, and three hops produce a query that scans most of the database. Graph databases (Neo4j, Amazon Neptune, ArangoDB) optimise for these traversals natively; what takes minutes in SQL takes milliseconds in a graph store. The architectural insight is to recognise the graph workload before forcing it into relational form — fraud detection, recommendation engines, organisational hierarchies, supply-chain dependencies, social networks all have graph DNA that's expensive to fight.

#### Architectural implications

- Workloads with traversal depth ≥ 3 are evaluated for graph database fit before being implemented in SQL.
- Graph stores are integrated alongside transactional databases — typically as projections of the relational truth, kept current by event-driven sync.
- Graph queries are written in graph query languages (Cypher, Gremlin) by engineers who understand the model — not as SQL emulation in graph form.

#### Reference

[Neo4j — Graph Database Concepts](https://neo4j.com/developer/graph-database/) — the canonical introduction to graph data modelling, query patterns, and the workloads where graph stores fundamentally outperform relational alternatives.

---

### 6. The data warehouse is yesterday's truth; treat the path with care

Operational databases (the OLTP path) hold today's truth — the current balance, the in-flight transaction, the latest customer record. The data warehouse (the OLAP path) holds yesterday's truth, organised for analysis — historical patterns, aggregations, longitudinal cohorts. They are different stores for different questions, with different freshness, different cardinality, and different workloads. Modern lake-house architectures (Databricks, Snowflake, Microsoft Fabric) blur the boundary, but the principle remains: the operational path optimises for transaction throughput, the analytical path optimises for retrospective query, and the pipeline that moves data between them is its own architectural concern with its own SLOs.

#### Architectural implications

- The OLTP and OLAP paths are separate stores with separate optimisation; they share data through a deliberate ETL/ELT pipeline, not by direct query.
- The freshness of the analytical path is documented and known — daily, hourly, near-real-time — and consumers of analytics know what window they're seeing.
- The pipeline between them is observable, monitored, and recovered like any other production system; broken ETL is an incident, not a back-of-the-week chore.
- The lake-house pattern (Snowflake, Databricks, Fabric) is evaluated for new analytics workloads against the cost of operating separate OLTP/OLAP stores.

#### Reference

[Bill Inmon — Building the Data Warehouse](https://en.wikipedia.org/wiki/Bill_Inmon) — the foundational text that defined the OLTP/OLAP distinction; modern lake-house architectures (Snowflake, Databricks, [Microsoft Fabric](https://www.microsoft.com/en-us/microsoft-fabric)) are the contemporary evolution.

---

## Architecture Diagram

The diagram below shows a canonical polyglot data architecture: an operational tier with relational and document stores; a key-value cache for hot data; a search index for full-text; a vector store for semantic retrieval; a message broker carrying changes between stores; a data warehouse for analytics fed by a deliberate ETL/ELT pipeline.

---

## Common pitfalls

### ⚠️ One database for everything

Forcing every workload into the relational database the team started with. Sessions, full-text search, time-series telemetry, and analytical queries all live in Postgres because "we already have Postgres." Each workload underperforms; the database becomes a bottleneck no amount of vertical scaling can fix.

#### What to do instead

Polyglot by deliberate choice. Each workload uses the store whose engineering matches its access pattern; the integration cost is paid in exchange for proper performance characteristics.

---

### ⚠️ Schema migration as a release event

Schema changes coupled to deployments, requiring downtime, requiring all consumers to upgrade simultaneously. Releases become coordination exercises; the team avoids schema work because the cost is so high.

#### What to do instead

Continuous additive evolution. Online schema change tools, dual-run periods, contraction phases. Schema changes happen weekly or daily, invisibly, without ceremony.

---

### ⚠️ Vector store as semantic magic

Embeddings stored in a vector database without lifecycle thinking — when the embedding model is upgraded, when source records change, when the index needs to be rebuilt. Search quietly degrades as the index drifts from the source of truth.

#### What to do instead

Treat embeddings as a versioned, lifecycle-managed dependency. Re-embed on source changes, rebuild on model upgrades, monitor for drift, audit relevance regularly.

---

### ⚠️ Time-series in a general table

High-throughput time-series data in a normalised relational table with a timestamp column. Storage grows unbounded, queries slow as data accumulates, retention is manual and unreliable.

#### What to do instead

Use time-series stores (TimescaleDB, ClickHouse, InfluxDB) for time-series workloads. Retention, downsampling, and chunked storage come built in; storage and query performance stay predictable.

---

### ⚠️ Direct OLAP queries against OLTP

Reporting, BI dashboards, and analytical queries hitting the operational database directly. Long-running queries lock tables, degrade transaction throughput, and produce stale dashboards anyway because the data hasn't been shaped for analysis.

#### What to do instead

A deliberate ETL/ELT pipeline to a separate analytical store. The OLTP path stays fast for transactions; the OLAP path is shaped for the questions analysts actually ask.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Each major data domain has a documented store choice with the access-pattern rationale ‖ Polyglot is deliberate, not accidental; the choice survives review by an engineer who didn't make it; the rationale is current to the workload as it exists today, not as it was when the system launched. | ☐ |
| 2 | Schema migrations are additive; online schema-change tools are exercised regularly ‖ ALTER TABLE downtime is rare and avoidable; dual-run windows let consumers migrate at their own pace; contraction phases remove deprecated columns long after no consumer reads them. | ☐ |
| 3 | Embedding lifecycles are managed: model versioning, re-embedding on source change, drift monitoring ‖ Vectors are an index over a source of truth; the index stays current; embedding-model upgrades trigger documented rebuild procedures; no mixed-version embeddings in production. | ☐ |
| 4 | Time-series workloads use purpose-built stores or extensions ‖ Retention, downsampling, and chunked storage come from the platform, not from custom cleanup jobs; query performance stays bounded as data accumulates. | ☐ |
| 5 | Workloads with traversal depth ≥ 3 are evaluated for graph fit before SQL ‖ Multi-hop queries, recursive traversals, fraud-pattern detection, supply-chain analysis — these are recognised as graph problems and routed to graph stores or extensions. | ☐ |
| 6 | OLTP and OLAP paths are separate, with a deliberate ETL/ELT pipeline between them ‖ Reporting does not hit production; the pipeline has SLOs and is monitored; analytical freshness is documented and known to consumers. | ☐ |
| 7 | Backups are tested by restore, not just by completion ‖ Backup integrity is verified through routine restore drills to a separate environment; the team has actually done this, not just configured it. | ☐ |
| 8 | Read replicas are used for read scaling but never assumed for write durability ‖ Async replication has lag; the team knows the lag bounds; replicas are not used for transactions that require read-your-writes consistency. | ☐ |
| 9 | Connection pooling is configured per service, sized against the database's connection limit ‖ Connection-limit exhaustion is a common outage cause; explicit pool sizing per service prevents one runaway service from starving the rest. | ☐ |
| 10 | Cross-store consistency contracts are documented and tested ‖ When data flows from Postgres to Elasticsearch, from Postgres to a warehouse, from event streams to read models — the consistency window, the failure modes, the reconciliation strategy are explicit. | ☐ |

---

## Related

[`technology/api-backend`](../api-backend) | [`technology/cloud`](../cloud) | [`patterns/data`](../../patterns/data) | [`patterns/integration`](../../patterns/integration) | [`system-design/event-driven`](../../system-design/event-driven) | [`system-design/scalable`](../../system-design/scalable)

---

## References

1. [PostgreSQL](https://www.postgresql.org/) — *postgresql.org*
2. [MongoDB](https://www.mongodb.com/) — *mongodb.com*
3. [Redis](https://redis.io/) — *redis.io*
4. [Apache Cassandra](https://cassandra.apache.org/) — *cassandra.apache.org*
5. [Elasticsearch](https://www.elastic.co/elasticsearch) — *elastic.co*
6. [Neo4j](https://neo4j.com/) — *neo4j.com*
7. [Pinecone — Vector Database Guide](https://www.pinecone.io/learn/vector-database/) — *pinecone.io*
8. [Snowflake](https://www.snowflake.com/) — *snowflake.com*
9. [Martin Fowler — Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html) — *martinfowler.com*
10. [Martin Kleppmann — Designing Data-Intensive Applications](https://dataintensive.net/) — *dataintensive.net*
