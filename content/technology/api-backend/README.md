# API & Backend Technologies

**Scalable Server-Side Architecture — designing robust, performant services for modern applications.** The backend is where business logic lives, where state is owned, and where every promise made to a frontend or partner is either kept or broken. This page describes how we approach API design, backend stack selection, and the operational properties that make services trustworthy at scale.

**Section:** `technology/` | **Subsection:** `api-backend/`
**Alignment:** Spring Boot | Node.js | FastAPI | OpenAPI

---

## What "API & Backend" actually means

The backend is two architectural concerns wearing one name. The *API* is the contract — what consumers can do, what they can't, what they get when they ask, what they get when something fails. The *backend* is the implementation — the language, the framework, the data access, the integrations that fulfil the contract. Conflating them produces APIs whose shape was decided by the database schema, frameworks chosen by familiarity rather than fit, and a contract that breaks every time the implementation evolves.

Treating them separately — designing the API as a product whose lifecycle outlasts any backend implementation, choosing the stack as an engineering decision with five-year consequences — produces services that consumers can rely on and teams can evolve. Java/Spring, Node.js, Python, Go, .NET each have their place; the discipline is matching the choice to the workload, the team, and the integration profile.

---

## Six principles

### 1. The API is the product; design its lifecycle accordingly

Consumers — internal teams, external partners, mobile apps that ship to app stores — couple to API contracts. A breaking change in the contract requires every consumer to follow, which means the API's design quality and evolution discipline determine the speed at which the system as a whole can move. Treating the API as a first-class product with an owner, a contract, a versioning policy, and a deprecation cycle is what separates services that survive five years from services that everyone has to coordinate around forever.

#### Architectural implications

- API contracts are designed first (OpenAPI/AsyncAPI), reviewed before implementation, and treated as the integration commitment.
- Versioning policy is documented (URL versioning, header versioning, evolution semantics) and consumers know what to expect when versions change.
- Deprecation has a documented cycle — communicate, dual-run, sunset — measured in quarters or years, not weeks.
- Backward and forward compatibility are tested in CI; consumer-driven contract testing catches breakage before deployment, not in production.

#### Reference

[OpenAPI Specification](https://www.openapis.org/) — the de facto standard for describing REST APIs in machine-readable form, enabling contract-first design and automated tooling across the lifecycle.

---

### 2. Stack choice is a hiring decision as much as a technical one

Java/Spring, Node.js, Python, Go, and .NET each have engineering trade-offs (concurrency model, ecosystem maturity, performance ceiling, library breadth). They also have organisational consequences — the talent market in your region, the salaries those engineers command, the tools they expect, the patterns they bring. Picking a stack on technical merit alone, without weighing the hiring and operational consequences, leaves the architecture defensible on paper but undeliverable in practice. The right stack is the one where the technical fit and the team profile align.

#### Architectural implications

- Stack selection considers the hiring market in the geography the team operates from, not just the global engineering blogosphere.
- The stack matches the workload: Java/Spring for transaction-heavy enterprise, Node.js for I/O-heavy front-of-house, Python for data and AI, Go for performance-critical infrastructure.
- Polyglot is acceptable but bounded — the cost of operating N stacks grows non-linearly, and the boundary between them is itself an architectural concern.
- Migration plans exist for stacks that the team commits to; switching language costs as much as rewriting the service in most cases.

#### Reference

[Stack Overflow Developer Survey](https://survey.stackoverflow.co/) — annual global telemetry on language adoption, satisfaction, and salary that informs hiring-market decisions.

---

### 3. Stateless services scale; stateful services do not

A stateless service can be replicated, load-balanced, and replaced trivially because every instance is interchangeable. A stateful service has identity — instance N holds state instance M does not — and scaling it requires partitioning, replication, leader election, and a coordination story that is itself complex. The architectural pattern is to push state outward: into databases, caches, queues, and explicit stateful components designed for the property. The application services that orchestrate the work are stateless, and that statelessness is what enables them to scale horizontally without architectural drama.

#### Architectural implications

- Application servers hold no state across requests — sessions, in-flight transactions, and conversation context live in backing services with explicit consistency contracts.
- Configuration comes from the environment, not from instance-local files; instances are interchangeable in deployment, scaling, and replacement.
- Stateful components (databases, message brokers, search indexes) are designed for the state property they need — and the application architecture treats them as the only stateful elements.

#### Reference

[The Twelve-Factor App — III. Config and VI. Processes](https://12factor.net/) — the canonical articulation of stateless, environment-configured services that scale horizontally without coordination.

---

### 4. Contract-first beats code-first at the API boundary

An API contract — OpenAPI schema, gRPC proto, GraphQL SDL, AsyncAPI specification — is a declarative description of what an API offers and what consumers can rely on. *Contract-first* design starts with the schema, generates server stubs and client libraries from it, and treats the schema as the source of truth. *Code-first* design starts with handler code and produces a schema afterward, often via reflection or annotations. The two approaches produce visibly similar artefacts but very different evolutionary properties: contract-first APIs are reviewed before implementation, validated against versioned consumers in CI, and surfaced as documentation that is authoritative because it generated the implementation. Code-first APIs are reviewed at PR time, drift from documentation by the second commit, and produce schemas that are accurate today and stale tomorrow.

#### Architectural implications

- The schema (OpenAPI, gRPC proto, GraphQL SDL) is checked in alongside source code and is the artefact reviewed in design discussions, not the handler implementation.
- Server stubs, client libraries, mock servers, and documentation all generate from the schema; hand-written drift between schema and implementation is treated as a CI failure.
- Schema-level breaking changes (removed fields, narrowed types, renamed operations) are blocked at PR time, before they land in main, by automated diff checks against the published version.
- Consumer-driven contract tests verify that real consumers can still parse what the API returns — schema compliance is a regression-tested property, not a hope.

#### Reference

[OpenAPI Specification](https://www.openapis.org/) — the canonical schema language for HTTP APIs that makes contract-first design practical. [gRPC](https://grpc.io/) and [GraphQL](https://graphql.org/) provide the equivalents for binary RPC and graph-traversal APIs respectively, with the same contract-first discipline applied to their respective transports.

---

### 5. Observability is wired in from day one, not added at SLO time

The first time a team needs observability is during an incident, which is the worst time to discover the logs are unstructured, the traces are missing, the metrics don't include the dimensions the question requires. Wiring observability into services from the first commit — structured logging with request correlation, distributed traces across service boundaries, metrics with the right cardinality, semantic conventions for fields — is what turns "I think it's slow" into "the p99 of the auth endpoint regressed 3 days ago after deployment v2.4.1." The cost of doing this from day one is small; the cost of retrofitting it is enormous.

#### Architectural implications

- Logs are structured (JSON), include correlation IDs, and follow consistent semantic conventions across services.
- Distributed tracing (OpenTelemetry) instruments every service-to-service call by default, not as a special project.
- Metrics include sufficient cardinality (per-route, per-status, per-customer-tier) for the questions operations actually has to answer.
- Dashboards exist for the SLOs that matter (availability, latency, error rate per endpoint) and are reviewed weekly, not consulted only during incidents.

#### Reference

[OpenTelemetry](https://opentelemetry.io/) — the CNCF standard for distributed tracing, logs, and metrics with instrumentation libraries across every major language and framework.

---

### 6. Security is layered across the request path, not a single gate

Authentication at the edge, authorisation at the service, input validation at the handler, rate limiting at the gateway, secrets management at the runtime, audit logging at the data layer — each is a separate concern with its own threat model and its own enforcement point. Treating security as "we have an API gateway with auth" leaves every layer below the gateway depending on the gateway being correct, present, and not bypassed. Layered defence — where every component validates its inputs and authorises its callers — is what makes the system resilient to single-point failures in the security architecture.

#### Architectural implications

- AuthN at the edge is verified, but every internal call is also authenticated and authorised — services do not trust the gateway as a permission source.
- Input validation happens at the boundary of every component that processes external input, not just at the API surface.
- Secrets are managed by a dedicated service (Vault, cloud-native KMS), rotated, and never in source control or environment files committed to git.
- Audit logging captures authenticated actor, action, target, and outcome — the questions security and compliance actually need answers to.

#### Reference

[OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x00-introduction/) — the canonical industry catalogue of API-specific security risks, with practical guidance for each.

---

## Architecture Diagram

The diagram below shows the canonical backend topology: an API gateway handling edge concerns (authn, rate limiting, TLS); stateless service tiers behind the gateway with internal authn/authz; a backing-services layer (databases, caches, message brokers) holding state; observability instrumentation as a cross-cutting concern; secrets management and IAM as distinct services.

---

## Common pitfalls

### ⚠️ Database schema as the API contract

The API shape mirrors the database schema, exposing internal structure to consumers. Database refactors become breaking API changes; API consumers learn implementation details that should have been hidden.

#### What to do instead

API contracts are designed for consumer needs and use cases. The database schema is an implementation detail; consumers see resources and operations matched to their workflow, not tables and joins.

---

### ⚠️ Stack monoculture by default

Picking the same stack for every service because that's what the team knows. When a workload genuinely requires different characteristics (high I/O concurrency, ML serving, cryptographic performance), the wrong stack is paid for in operational complexity and engineering effort over years.

#### What to do instead

Match the stack to the workload, with explicit polyglot boundaries. The default is one stack for most things; the exceptions are deliberate and documented, not accidental.

---

### ⚠️ Sticky sessions as scaling

State held in application servers, with sticky load-balancer sessions to keep clients pinned to the same instance. Scaling horizontally becomes impossible because new instances can't serve in-flight sessions; deployment becomes painful because every restart sheds state.

#### What to do instead

Statelessness with explicit external state. Sessions in Redis, in-flight context in queues, durable state in databases. Application instances are interchangeable; deployment is routine.

---

### ⚠️ Observability as a sprint

A dedicated "observability sprint" added when the SLO conversation starts. The instrumentation is partial, the dimensions miss the questions that matter, and the team's instinct is to instrument by reaction rather than by design.

#### What to do instead

Observability is part of every service from the first commit. Logging conventions, trace propagation, and metric naming are standard library calls — not optional decoration.

---

### ⚠️ Authentication as the only security

The API gateway enforces authentication; everything behind it implicitly trusts the caller. A misconfigured gateway, a compromised internal service, or a misused service-account token bypasses the entire security model.

#### What to do instead

Layered authentication and authorisation. Every internal call is authenticated; every authorisation decision happens at the data or operation level it protects, not at the network edge.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | API contracts are documented in OpenAPI / AsyncAPI and reviewed before implementation ‖ Contract-first design forces the integration conversation upstream of code; the resulting API is shaped by consumer needs, not by whichever endpoint was easiest to expose. | ☐ |
| 2 | Versioning policy and deprecation cycles are documented and enforced ‖ Consumers know what to expect; deprecations follow announce-dual-run-sunset; the team's commitment to the contract is what makes external consumers willing to integrate. | ☐ |
| 3 | Stack selection is justified against workload, team, and hiring market ‖ The choice is defensible to a CTO joining in two years; polyglot is bounded and deliberate, not accidental; migration plans exist for stacks the team commits to. | ☐ |
| 4 | Application services hold no state across requests ‖ Sessions, in-flight transactions, and conversation context live in backing services; instances are interchangeable for deployment, scaling, and replacement. | ☐ |
| 5 | Idempotency is documented per mutation, with idempotency keys where required ‖ Consumers know which operations are safe to retry; idempotency keys are first-class contract elements; internal retry handlers assume duplicate delivery. | ☐ |
| 6 | Structured logging with correlation IDs is standard from day one ‖ Logs are JSON; correlation IDs propagate across service boundaries; semantic conventions are consistent across services so cross-service queries actually work. | ☐ |
| 7 | Distributed tracing instruments every service-to-service call by default ‖ OpenTelemetry instrumentation is a library default, not an opt-in; traces span the request lifecycle without per-team integration projects. | ☐ |
| 8 | Internal calls are authenticated and authorised, not gateway-trusted ‖ Service-to-service authn (mTLS, signed tokens) is the norm; authorisation decisions happen at the protected operation, not at the network edge. | ☐ |
| 9 | Secrets are managed by a dedicated service, rotated, never in version control ‖ Vault or cloud-native KMS; secrets are injected at runtime; rotation is automated; no secrets in committed environment files or container images. | ☐ |
| 10 | Audit logging captures actor, action, target, and outcome for security-relevant operations ‖ The questions security, compliance, and incident response need answers to are pre-answered by the audit log structure; the schema is treated as a public contract. | ☐ |

---

## Related

[`technology/ui-ux-cx`](../ui-ux-cx) | [`technology/databases`](../databases) | [`technology/cloud`](../cloud) | [`patterns/integration`](../../patterns/integration) | [`patterns/security`](../../patterns/security) | [`system-design/scalable`](../../system-design/scalable)

---

## References

1. [OpenAPI Specification](https://www.openapis.org/) — *openapis.org*
2. [Spring Boot](https://spring.io/projects/spring-boot) — *spring.io*
3. [Node.js](https://nodejs.org/) — *nodejs.org*
4. [FastAPI](https://fastapi.tiangolo.com/) — *tiangolo.com*
5. [The Twelve-Factor App](https://12factor.net/) — *12factor.net*
6. [Stripe — Designing robust APIs](https://stripe.com/blog/idempotency) — *stripe.com*
7. [OpenTelemetry](https://opentelemetry.io/) — *opentelemetry.io*
8. [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x00-introduction/) — *owasp.org*
9. [GraphQL](https://graphql.org/) — *graphql.org*
10. [gRPC](https://grpc.io/) — *grpc.io*
