# Foundational Principles

> **Section:** `principles/` | **Subsection:** `foundational/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Base axioms of sound architecture: separation of concerns, single responsibility, least privilege, and design for failure.

This document is part of the **Architecture Principles** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Separation of Concerns

Each component has one bounded responsibility. Payment processing does not send emails. Authentication does not transform data. Crossing concerns creates hidden coupling that surfaces as incidents.

### 2. Dependency Inversion Principle

High-level policy (business logic) must not depend on low-level detail (database, HTTP). Both depend on an abstraction. Swapping the database should not require changing business rules.

### 3. Design for Failure

Assume every external call will eventually fail. Implement timeouts on every outbound call, circuit breakers for cascading failure prevention, retries with exponential backoff, and graceful degradation paths.

### 4. Least Privilege

Every process, service account, and user receives only the minimum permissions to perform its specific function. Scope credentials to schemas, not databases. Scope IAM roles to actions, not wildcards.

### 5. Explicit Over Implicit

Make dependencies, configuration, side effects, and failure modes visible. Hidden conventions are future production incidents waiting to happen.

### 6. Open/Closed Principle

Software entities should be open for extension (add new behavior) but closed for modification (don't change existing behavior). Achieved via interfaces, plugins, and strategy patterns.


---

## Implementation Guide

**Step 1: Audit Your Current Principle Adherence**

Walk through each active system and score it against each principle on a 1–5 scale. Document violations as architectural debt items with estimated remediation effort. This baseline is your starting point.

**Step 2: Create Traceable Architecture Decisions**

Every significant design decision should reference the principle(s) that justify it. 'We chose an async messaging pattern because Design for Failure requires decoupling caller and callee.' Traceability turns principles from posters into guardrails.

**Step 3: Encode Principles as Automated Tests**

Use ArchUnit (Java), NetArchTest (.NET), or Dependency Cruiser (JavaScript) to write automated tests that fail CI builds when dependency directions are inverted or when a module exceeds its bounded responsibility.

**Step 4: Establish a Principle Tension Resolution Matrix**

Principles can conflict. DRY (Don't Repeat Yourself) vs. Team Autonomy. Least Privilege vs. Developer Productivity. Document your organization's precedence rules so teams resolve conflicts consistently.

**Step 5: Run Principle Reviews at Architecture Gates**

At each ARB review, the submitting architect must demonstrate how each principle applies to their design. Non-application must be explicitly justified, not silently omitted.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Principle Traceability Audit | EA Lead | Every ADR references at least one principle with justification | Required |
| Automated Dependency Tests in CI | Tech Lead | ArchUnit/NetArchTest rules passing on every build | Required |
| Principle Tension Register | Architecture Board | Conflict resolution rules documented and published | Required |
| Quarterly Principle Review | CTO / EA | Principle set reviewed for organizational relevance | Periodic |


---

## Recommended Patterns

### Layered Architecture

Horizontal layers — presentation, application, domain, infrastructure — each calling only the layer below. Enforces SoC at the code structure level. Dependency direction: always downward.

### Hexagonal Architecture (Ports & Adapters)

The domain core defines ports (interfaces). Adapters implement them for specific technology (REST adapter, Kafka adapter, PostgreSQL adapter). The domain has zero infrastructure imports. Swap adapters freely without touching business logic.

### SOLID Applied at Service Level

SOLID principles apply not just at the class level but at the service boundary level. Each microservice = Single Responsibility. Service contracts = Open/Closed. Service interfaces = Interface Segregation. Service dependencies = Dependency Inversion.


---

## Anti-Patterns to Avoid

### ⚠️ God Class / God Service

A class or service that accumulates all responsibilities over time. Symptoms: 3,000-line classes, services with 50+ endpoints, deployment that requires coordinating 8 teams. Resolution: apply SoC aggressively.

### ⚠️ Implicit Global State

Shared mutable global configuration, thread-local context, or ambient authentication state that services read without declaring the dependency. Makes reasoning about behavior impossible and testing a nightmare.

### ⚠️ Principle Theater

Architecture documents filled with principle references that bear no relationship to the actual design decisions made. Principles cited as decoration rather than applied as constraints.


---

## AI Augmentation Extensions

### Principle-Aware Architecture Review Agent

An LLM agent ingests the principle inventory and evaluates submitted ADRs for principle alignment, flagging violations, suggesting remediation, and generating a scored compliance report.

> **Note:** Configure the review agent to weight principles by your organization's priority (security > performance for fintech; availability > consistency for social media).

### RAG-Based Principle Lookup

Embed all principles into a vector store. Architects query: 'Which principle should govern how I design this caching layer?' and receive cited, evidence-based answers from the library.

> **Note:** Chunk at the principle level, not the document level, for higher retrieval precision. Each principle should be its own embedding unit.


---

## Related Sections

[`patterns/structural`](../patterns/structural) | [`adrs/platform`](../adrs/platform) | [`governance/review-templates`](../governance/review-templates) | [`scorecards/principles`](../scorecards/principles)

---

## References

1. [Clean Architecture — Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) — *Amazon*
2. [Patterns of Enterprise Application Architecture — Fowler](https://martinfowler.com/books/eaa.html) — *martinfowler.com*
3. [Building Evolutionary Architectures — Ford, Parsons, Kua](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/) — *O'Reilly*
4. [Domain-Driven Design — Evans](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215) — *Amazon*
5. [Site Reliability Engineering — Google](https://sre.google/sre-book/table-of-contents/) — *sre.google*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `principles/foundational/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
