# Integration Patterns

> **Section:** `patterns/` | **Subsection:** `integration/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Enterprise Integration Patterns: message broker, saga, choreography, orchestration.

This document is part of the **Architecture & Design Patterns** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Loose Coupling via Messaging

Services communicate via messages wherever the response is not time-critical. This eliminates runtime dependency — the consumer does not need to be running when the producer sends.

### 2. Idempotency at Every Consumer

Message consumers must produce the same result if the same message is received twice. Use idempotency keys, processed-event tables, or naturally idempotent operations.

### 3. Contract-First Integration

Define the message schema or API contract before building either side. Use schema registries and API design tools. This prevents incompatible changes from reaching production.

### 4. Failure Isolation

A failure in one integration path must not propagate to other services. Circuit breakers stop cascading synchronous failures. Dead letter queues contain asynchronous failure storms.

### 5. Observability of Integration Points

Every message published, consumed, delayed, or failed must be observable. Integration points are where most distributed system mysteries live — instrument them exhaustively.


---

## Implementation Guide

**Step 1: Map Your Integration Topology**

Draw every service-to-service communication in your system: direction, protocol, synchronous or async, schema format. Color-code synchronous calls red. Review: are any critical paths all-red? Those are your availability risks.

**Step 2: Classify by Communication Need**

For each integration: does the caller need an immediate response? If yes — synchronous REST or gRPC. If no — async messaging (Kafka, SQS). If bulk — batch file. If real-time stream — Kafka or Kinesis.

**Step 3: Design Idempotency into Every Consumer**

Before writing consumer code, answer: 'What happens if this message is delivered twice?' If the answer is 'bad things,' implement idempotency: generate a deterministic ID from the event payload and use it as an upsert key.

**Step 4: Implement Dead Letter Queues Everywhere**

Every queue or Kafka topic must have a DLQ. Configure alert thresholds: any message in the DLQ within 5 minutes triggers a PagerDuty alert. DLQs without alerts are debugging black holes.

**Step 5: Register All Schemas**

Every event schema goes into a schema registry (Confluent, AWS Glue, Azure Schema Registry). Set compatibility rules: BACKWARD for consumer-initiated changes, FORWARD for producer-initiated changes. Block deployments that break schema compatibility.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Integration Topology Documented | Solution Architect | Synchronous/async classification for all integrations complete | Required |
| Schema Registry Populated | Integration Architect | All event schemas registered with compatibility rules set | Required |
| DLQ + Alerting Configured | Platform / DevOps | DLQ alert firing within 5 minutes of first failed message | Required |
| Idempotency Tests in CI | QA Lead | Duplicate-message delivery tests passing in CI pipeline | Required |
| Contract Tests for All Consumers | QA Lead | Pact or Spring Cloud Contract tests registered for all consumers | Required |


---

## Recommended Patterns

### Saga Pattern (Choreography)

Each service listens for events and reacts independently. No central coordinator. Order Service publishes OrderCreated → Payment Service listens and publishes PaymentProcessed → Inventory Service listens. Failure triggers compensating events. Highly decoupled but complex to trace.

### Saga Pattern (Orchestration)

A dedicated Saga Orchestrator (Step Functions, Temporal, Camunda) drives the workflow step by step, calling each service and handling failures with compensating calls. More visible and controllable than choreography.

### Outbox Pattern

Write the business record AND the event to your own database in a single ACID transaction. A CDC connector (Debezium, AWS DMS) reads the outbox table and publishes to the message bus. Guarantees at-least-once delivery without distributed transactions.

### Event-Carried State Transfer

Events carry the full data payload consumers need. Order events carry the full order: customer ID, name, items, address. Consumers never need to call back to the source. Eliminates synchronous lookup dependencies.

### Claim Check

Large payloads (PDFs, images, large JSON) are stored in object storage. The message carries a reference token. Consumers redeem the token to fetch the payload. Keeps the message bus fast and lean.

### Consumer-Driven Contract Testing

Consumers define the contract they need from a provider. Tools like Pact verify that the provider satisfies every registered consumer contract before deployment. Prevents integration regressions in CI/CD.


---

## Anti-Patterns to Avoid

### ⚠️ Synchronous Chain of Death

Service A → B → C → D all synchronous. Each call adds latency. Any failure propagates up the entire chain. The system's availability is the product of each service's availability: 99.9%^4 = 99.6%. Resolution: identify the longest synchronous chains and introduce async messaging at appropriate boundaries.

### ⚠️ Integration via Shared Database

Multiple services reading and writing to the same database tables as the integration mechanism. Schema changes break all consumers simultaneously. Deployment of one service can corrupt another's data. This is the most dangerous integration anti-pattern and the hardest to remediate.

### ⚠️ Phantom Events

Events that trigger notifications without meaningful payload — just an entity ID. Every consumer must then call back to the source service to get the data they need. Creates synchronous coupling inside async workflows. Use Event-Carried State Transfer instead.


---

## AI Augmentation Extensions

### AI Schema Evolution Impact Analysis

LLM agents analyze all registered consumer contracts when a new event schema is proposed. They generate a full impact report: which consumers are affected, what migration steps are required, and whether backward compatibility is maintained.

> **Note:** Always validate AI-generated impact analysis against actual consumer codebases. LLMs may miss dynamic consumers or unconventional schema usage patterns.

### Intelligent DLQ Triage Agent

An AI agent monitors DLQ message patterns, classifies failures by root cause (schema mismatch, network timeout, business rule violation, poison pill), and generates remediation playbooks for each category.

> **Note:** Require human approval before AI agents replay DLQ messages in production. Automated replay of incorrect messages can propagate data corruption.


---

## Related Sections

[`patterns/data`](../patterns/data) | [`system-design/event-driven`](../system-design/event-driven) | [`observability/traces`](../observability/traces) | [`anti-patterns/shared-db-context`](../anti-patterns/shared-db-context)

---

## References

1. [Enterprise Integration Patterns — Hohpe & Woolf](https://www.enterpriseintegrationpatterns.com/) — *enterpriseintegrationpatterns.com*
2. [Building Event-Driven Microservices — Adam Bellemare](https://www.oreilly.com/library/view/building-event-driven-microservices/9781492057888/) — *O'Reilly*
3. [Designing Data-Intensive Applications — Kleppmann](https://dataintensive.net/) — *dataintensive.net*
4. [Kafka: The Definitive Guide — Shapira et al.](https://www.confluent.io/resources/kafka-the-definitive-guide/) — *Confluent*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `patterns/integration/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
