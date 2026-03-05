# Data Modeling

> **Section:** `data/` | **Subsection:** `modeling/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Conceptual, logical, and physical data modeling. ERD conventions, normalization, and dimensional modeling.

This document is part of the **Data Architecture** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Model the Business Domain, Not the Technology

The data model should reflect how the business thinks about its data — not how the database stores it most efficiently. Start with the business entities and relationships; optimize for the technology second.

### 2. Each Fact in One Place (Normalization)

In OLTP systems, every fact should be stored exactly once. If customer address is stored in both the Customer table and the Order table, updating one without the other creates inconsistency. Normalize until you have a consistency problem; then denormalize selectively.

### 3. Design for Query Patterns in NoSQL

In NoSQL systems (DynamoDB, Cassandra), model data to answer your specific query patterns efficiently. General-purpose schemas on NoSQL systems produce expensive, slow queries. Know your top 5 access patterns before designing the schema.

### 4. Events are Immutable; State is Derived

In event-sourced systems, past events are facts that cannot be changed. Current state is a projection derived from replaying events. This distinction preserves the integrity of the historical record and is required for PCI DSS and BSP audit trail compliance.

### 5. Schema Evolution is a First-Class Concern

Plan for how the schema will change before deploying it. Additive changes are always safe. Breaking changes require multi-stage migrations. Event schemas must be versioned. Design with evolution in mind from day one.


---

## Implementation Guide

**Step 1: Identify the Domain Entities and Boundaries**

Work with business stakeholders to enumerate all entities, their key attributes, and the relationships between them. Use event storming or domain storytelling to discover entities through business processes rather than database tables.

**Step 2: Apply Normalization to OLTP Schemas**

Walk through 1NF (atomic attributes), 2NF (no partial dependencies), and 3NF (no transitive dependencies) for all relational tables. Document any intentional denormalization with the query performance justification.

**Step 3: Design the Write Model (Transactions)**

Identify the transactional boundaries: what operations must be atomic? Each transaction boundary maps to either a single table mutation, a multi-table transaction within one service, or a saga across services. Never span a transaction across service boundaries.

**Step 4: Design the Read Models (Query Optimization)**

For reporting and analytics use cases, design denormalized read models (star schemas, materialized views, Elasticsearch indexes) separately from the normalized write model. This is the CQRS principle applied to data modeling.

**Step 5: Define Data Retention and Archival Strategy**

For each entity: what is the retention period? (BSP: 5 years minimum for transaction records.) How are records archived? How are deletion requests handled (GDPR/DPA right to erasure)? Design retention into the schema from the start.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| ER Diagram Reviewed by Domain Experts | Data Architect | Business stakeholders have validated entity definitions and relationships | Required |
| Normalization Documented | Data Architect | Normalization level stated with justifications for any denormalization | Required |
| Migration Plan Defined | Data Engineer | Schema migration approach documented for all planned changes | Required |
| Retention Policy Aligned to BSP/DPA | Compliance Architect | Retention periods defined per entity aligned to regulatory requirements | Required |


---

## Recommended Patterns

### Star Schema (Data Warehouse)

A central Fact table (transactions, events) surrounded by Dimension tables (customer, product, time, location). Highly denormalized for fast analytical queries. The Kimball methodology for dimensional modeling.

### Event Sourcing Store

An append-only event log is the primary data store. Current state is derived by replaying events. Enables complete audit trails, temporal queries ('what was the balance on 2024-01-15?'), and multiple independent read projections from the same event stream.

### Polyglot Persistence

Use the right database technology for each access pattern: PostgreSQL for transactional data requiring ACID guarantees; DynamoDB for high-throughput key-value access; Elasticsearch for full-text search; Redis for caching; TimescaleDB for time-series metrics.


---

## Anti-Patterns to Avoid

### ⚠️ God Table

A single database table with 200+ columns, used by every service in the system to store anything vaguely related to the central entity. Modifications require coordinating every team. Queries return enormous row payloads. The hardest technical debt to escape.

### ⚠️ EAV (Entity-Attribute-Value) Overuse

Storing all attributes as rows in a generic (entity_id, attribute_name, attribute_value) table to achieve 'schema flexibility.' Makes SQL queries unmaintainable, destroys query performance, and loses type safety. Use JSONB columns or document databases for genuinely dynamic attributes.


---

## AI Augmentation Extensions

### AI-Assisted ER Generation

LLM agents translate business domain descriptions into draft ER diagrams with entity definitions, relationships, and cardinality constraints. Dramatically accelerates the initial modeling phase for new domains.

> **Note:** AI-generated ER models require validation by a data architect. LLMs may miss domain-specific constraints, regulatory requirements, and cardinality edge cases.

### Schema Drift Detection

Automated monitoring compares deployed database schemas against the version-controlled schema definitions. Deviations (manually applied changes, ORM-driven schema drift) trigger alerts and generate remediation migrations.

> **Note:** Run schema drift detection in every environment — staging and production. Manual schema changes in production that bypass version control are a critical audit finding.


---

## Related Sections

[`data/integration`](../data/integration) | [`data/governance`](../data/governance) | [`patterns/data`](../patterns/data) | [`ddd/aggregates`](../ddd/aggregates) | [`compliance/bsp-afasa`](../compliance/bsp-afasa)

---

## References

1. [Designing Data-Intensive Applications — Kleppmann](https://dataintensive.net/) — *dataintensive.net*
2. [The Data Warehouse Toolkit — Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/) — *Kimball Group*
3. [CQRS Documents — Greg Young](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf) — *cqrs.files.wordpress.com*
4. [Domain-Driven Design — Evans](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215) — *Amazon*
5. [Fundamentals of Data Engineering — Reis & Housley](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/) — *O'Reilly*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `data/modeling/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
