# Structural Patterns

Architecture for the internal shape of systems — the patterns for layers, cores, extension points, and composition that determine what can change cheaply, what is expensive to reverse, and what becomes the system's permanent geometry.

**Section:** `patterns/` | **Subsection:** `structural/`
**Alignment:** GoF Design Patterns | Pattern-Oriented Software Architecture | Hexagonal Architecture | Clean Architecture

---

## What "structural patterns" actually means

A *structure-by-default* approach assumes the structure of a system emerges from how it gets built — which usually means it inherits the shape of the framework, the expectations of the team, or the historical accidents of which file was created first. The result is a system whose structural decisions were never made consciously, which means they cannot be defended consciously, which means they erode whenever deadline pressure or new requirements arrive.

A *structure-as-architecture* approach treats the internal shape of a system — its layers, its core, its extension points, its composition strategy — as a deliberate decision recorded alongside other architectural choices. Whether a system is layered, hexagonal, microkernel, pipes-and-filters, or some named hybrid is something the team chose, can articulate, and can defend. The patterns are not academic — they are named shapes that have been tried, refined, and named precisely so that teams can reach for them by name rather than reinventing them under pressure.

The architectural shift is not "we organised the folders." It is: **structural patterns are the named shapes for how systems compose; picking deliberately means picking from a vocabulary of trade-offs that other teams have already paid for, instead of inventing your trade-offs in production.**

---

## Six principles

### 1. Pick a structural pattern deliberately, or one will pick you

Every system has a structure. The only question is whether the structure was chosen or whether it accumulated by accident — through framework conventions, deadline pressure, the order files happened to be created in, or which engineer was hired first. Systems with chosen structures have known trade-offs the team can defend and revisit. Systems with accumulated structures have unknown trade-offs the team only discovers when the structure breaks under a load it was never designed to bear.

#### Architectural implications

- Each major capability has a documented structural pattern (layered, hexagonal, microkernel, pipes-and-filters, plugin) chosen at design time, not assumed by default.
- The trade-offs of the chosen pattern are documented alongside the choice — what it gives up to gain what it gives.
- When the structure starts to feel wrong, the response is to revisit the pattern choice deliberately, not to add layers of compensating mechanism on top of the wrong shape.
- Pattern shifts (e.g., from layered to hexagonal during modernisation) are first-class architectural changes, planned and tracked, not refactoring side-effects.

#### Quick test

> Pick your most central service. What structural pattern is it built around? If the answer is "well, it's organised into folders for controllers, services, and models," that is a framework convention, not a structural pattern. The folders are there; the architectural commitment is not.

#### Reference

[Mark Richards, Software Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/) — the canonical short summary of the major architectural patterns, their forces, and their trade-offs.

---

### 2. The application core should be testable without its infrastructure

The hexagonal architecture insight, also known as ports-and-adapters, is that the application's core domain logic should run in a unit test — without a database, without a network, without a UI, without anything that requires infrastructure. Everything that touches the outside world (database drivers, HTTP frameworks, message brokers, file systems) is an adapter that the core uses through a port — an interface owned by the core. The core depends only on its own ports; the adapters depend on the core. The architectural property this delivers is enormous: the core can be reasoned about, tested, and refactored without infrastructure changing under it. Most "we can't test that" code is code where the core has been entangled with its adapters.

#### Architectural implications

- The core domain logic depends on its own interfaces (ports), not on framework or infrastructure types.
- Adapters (database access, HTTP handlers, external API clients) implement those ports and are wired up at the application's edge.
- Unit tests for the core run without spinning up infrastructure — no database, no embedded server, no message broker, no mock that fills in for a real system.
- Switching infrastructure (Postgres to MySQL, REST to gRPC, Kafka to RabbitMQ) is a matter of writing new adapters, not rewriting the core.

#### Quick test

> Pick the most central piece of business logic in your system. Could you run its tests with the database, network, and message broker all unavailable? If the answer is "no, because the logic calls into them directly," the core has been infected by its infrastructure — and that infection compounds with every change.

#### Reference

[Alistair Cockburn, Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_%28software%29) — the original formulation, and still the clearest articulation of the testability property.

---

### 3. Layers encode a dependency policy, not abstraction levels

Layered architecture is widely misunderstood as "high-level on top, low-level on bottom." That framing is wrong. The layered pattern's actual content is a *dependency policy*: code in layer N may call into code in layer N&minus;1, but never the reverse. The "levels" metaphor confuses people into thinking layers are about abstraction quality; they are about the direction of allowed dependencies. Reverse-direction dependencies (lower layer reaching back into higher layer) violate the pattern even when the code looks fine, because they break the substitutability and reasoning guarantees the layers were designed to provide. When teams say layered architecture failed them, they almost always mean the layering was a folder structure, not an enforced dependency policy.

#### Architectural implications

- Each layer's allowed dependencies are documented and enforced — typically by linting, module visibility rules, or build-system boundaries.
- Cross-layer calls in the wrong direction are detected automatically, not in code review.
- "Skip-level" calls (layer 3 calling layer 1 directly, bypassing layer 2) are also policy violations and either explicitly allowed or explicitly forbidden — never silently tolerated.
- When a layer becomes leaky — frequently bypassed, frequently extended, frequently mocked in tests — the response is to revisit the layering, not to add a new helper layer that compounds the mess.

#### Quick test

> Pick the lowest layer of your system (database access, infrastructure clients). Can it import or reference anything from higher layers? If yes, the layering is a folder convention, not a dependency policy. If no, but you have never seen the policy enforced or articulated — it is still a folder convention; the policy has not yet been tested against an actual violation.

#### Reference

[Multitier Architecture](https://en.wikipedia.org/wiki/Multitier_architecture) — Wikipedia's article remains the clearest correction of the abstraction-level misconception, and traces the pattern to its 1990s origins in three-tier client/server architecture.

---

### 4. Plugin points are architectural commitments — they outlast every plugin

The microkernel pattern (also called plugin architecture) is for systems where the variability is the point — extensions, modules, custom workflows that different users or contexts need to inject. The architectural commitment is the *shape* of the extension surface: what data is passed across, what guarantees the kernel makes about ordering and lifecycle, what plugins can and cannot affect. Once that surface is established and external plugins exist against it, changing the surface is incredibly expensive — every plugin must be updated. So the surface decision must be made deliberately, *before* the first plugin exists, by people who understand what kinds of extension are likely to be needed in five years. Adding extension points later, once you "need extensibility," produces the wrong surface and locks you into it.

#### Architectural implications

- Plugin contracts are defined as first-class architectural artifacts, versioned, and maintained with backward compatibility commitments.
- The kernel boundary is conceptually a public API even when plugins are internal — the ergonomics matter and the lock-in is real.
- Plugin lifecycle (install, activate, deactivate, uninstall) is part of the kernel design, not retrofitted when the first plugin failure happens.
- Extension is preferred over modification — the kernel's stability is what makes plugins viable, and weakening it for one plugin's convenience costs every other plugin.

#### Quick test

> Pick a feature in your most extensible system that was added by extension. Could it have been added without modifying the kernel? If yes, the extension surface is doing its job. If the kernel had to change to accommodate the extension, the surface needs revisiting — that path will be required again.

#### Reference

[Microkernel Architecture](https://en.wikipedia.org/wiki/Microkernel) — the broader plugin architecture literature; Eclipse's plugin system and the Linux kernel's loadable module system remain canonical examples in widely different domains.

---

### 5. Linear data flow deserves linear structure

Some workflows ARE pipelines: extract data, validate it, transform it, enrich it, write it. Implementing such workflows as request-response chains or shared mutable state produces complexity for no benefit. The pipes-and-filters pattern matches the linear data shape with a linear architectural shape: independent stages connected by pipes, each stage transforming its input and emitting output, with no shared state between stages. The properties this delivers — independent failability of each stage, easy reordering, observable intermediate state, parallelisability — are exactly what the workflow's shape was already calling for. The cost of fighting the data's shape with a different structure is paid every time the pipeline changes, which it always does.

#### Architectural implications

- Workflows that are inherently linear are structured as pipelines, not as request-response chains or shared-state machines.
- Each pipeline stage is independently failable and observable — the input and output of each stage are visible, not opaque to the rest of the system.
- Stages have no shared state; coordination happens only through the data flowing between them via the pipes.
- The pipeline's stages are reorderable and replaceable as long as they implement the same input/output contract — which is what the contract is for.

#### Quick test

> Pick a workflow in your system that processes data through multiple stages. If you wanted to insert a new validation step, what would it cost? In a pipeline-shaped architecture, it is a new stage between two existing stages. If the answer is "we'd need to refactor several services," the workflow is shaped wrong for what it actually is.

#### Reference

[Pipeline (software)](https://en.wikipedia.org/wiki/Pipeline_%28software%29) — formalised by Doug McIlroy at Bell Labs in the 1960s; the Unix philosophy is its most successful enduring example, and forty years later still the cleanest demonstration of why matching structure to flow shape matters.

---

### 6. Composition over hierarchy at every scale

At every scale — objects, modules, services, systems — composition (combining peers through explicit contracts) tends to age better than deep hierarchy (extending one tower of behaviour). A system composed of peer modules with explicit interfaces can be re-composed when needs change; a system organised as a single inheritance hierarchy can only be extended in the directions the hierarchy already permits, and refactoring the hierarchy requires touching everything. This principle scales: it applied to GoF-era class design, it applies to modular monoliths, it applies to microservice topologies, and (by Conway's Law) it applies to organisational structure that produces all of the above. The single-tower approach is locally easier to start; it is universally harder to grow.

#### Architectural implications

- New behaviour is added by composing existing modules with new ones, not by extending a base class or framework type that was never designed to receive that extension.
- The system's main components are peers connected by explicit contracts, not a hierarchy of "parent" and "child" modules where the parent imposes structure on every descendant.
- Inheritance and "framework provides, application extends" patterns are reserved for cases where the hierarchy is genuinely stable — typically rare in line-of-business code.
- When teams reach for a "BaseService" that all services extend, the question is whether that's truly stable or whether composition would handle it better — usually the latter.

#### Quick test

> Pick the deepest inheritance chain in your most central code. Trace it from leaf to root. How many of the intermediate classes have multiple direct subclasses, and how often does adding new behaviour require touching multiple levels? If the answer is "rarely multiple subclasses, often multiple levels touched," the hierarchy is doing the wrong job — composition would localise the change.

#### Reference

[Gamma, Helm, Johnson, Vlissides — Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) — the GoF book's "favour composition over inheritance" rule remains the most durable advice in the entire patterns canon, and the most consistently confirmed at every scale of system design since 1994.

---

## Architecture Diagram

The diagram below shows the canonical structural-patterns view of an application: the core domain at the centre (independent of infrastructure), surrounded by ports it owns, with adapters at the edge connecting to infrastructure. The same shape supports layered, hexagonal, and microkernel interpretations depending on which dependency policies are enforced — which is the page's central insight that the *named pattern* is the policy, not the shape.

---

## Common pitfalls when adopting structural-pattern thinking

### ⚠️ Patterns by name, not by force

Adopting a pattern because it is named (microservices! event-driven! hexagonal!) without understanding the problem it solves. The pattern's value comes from the trade-offs it embodies; adopting the trade-offs without the problem produces costs without benefits. Pattern names are not magic; they're shorthand for a set of constraints that the team has now signed up for whether they understand them or not.

#### What to do instead

Start with the forces — what is hard about this system right now, what does it need to support, what kinds of change are likely. Then look for the named pattern that addresses those forces. The pattern's name is the *answer*, not the *question*.

---

### ⚠️ The accidental layered architecture

Folders called "controllers," "services," "models" because the framework set them up that way, with no enforced dependency policy. Looks like layered architecture from a distance. Has none of the substitutability, testability, or reasoning guarantees that layered architecture is supposed to deliver, because nothing prevents layers from depending on each other in any direction.

#### What to do instead

If layering matters, enforce it by tooling — module visibility rules, dependency-direction linters, build-system boundaries that make wrong-direction imports fail to compile. Layering as folder structure is a comforting illusion that does no architectural work.

---

### ⚠️ The framework as architecture

Treating the framework's structural conventions as the system's architecture. When the framework changes (or you migrate to a different one), the architecture has to be re-discovered and rebuilt — because it lived in someone else's code, not in yours. Framework upgrades become rewrites; framework migrations become death marches.

#### What to do instead

The structural pattern lives in your design documents and your enforcement tooling, separate from any framework. Frameworks come and go; architecture should outlast at least three of them.

---

### ⚠️ The "we'll make it pluggable later" plugin

Designing for extensibility that does not yet have a use case. The extension points end up matching no actual extension need, the surface reflects guesses rather than experience, and the first real plugin requires changing the kernel — which then breaks all the imaginary plugins that motivated the surface in the first place.

#### What to do instead

Resist the urge to over-design extension surfaces. Build for current needs, refactor toward extensibility when the second use case arrives, and treat the surface as conscious technical debt until the third use case confirms its shape.

---

### ⚠️ Inheritance as the default for "shared behaviour"

Putting common code in a parent class because that's how the language teaches you to share. By the third subclass, the parent has split-personality conditional logic ("if this subclass do X, otherwise do Y") and changing it touches every subclass. The hierarchy that started as "DRY" has become the most coupled, most fragile part of the system.

#### What to do instead

Default to composition. Shared behaviour goes in a separate module that interested parties depend on explicitly — not a base class that imposes a contract on every descendant. Inheritance is appropriate only when the hierarchy is genuinely stable and the relationship is genuinely "is-a," which in line-of-business code is rare.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Each major capability's structural pattern is named in its design document ‖ Without a named pattern, every team member has a different mental model of how the system is structured. Naming the pattern (layered, hexagonal, microkernel, pipes-and-filters) creates shared vocabulary and makes departures from the chosen pattern visible rather than invisible. | ☐ |
| 2 | The application core has unit tests that run without infrastructure ‖ The hexagonal property: if the core can't be tested without DB, network, and UI, the core has been entangled with its adapters and refactoring becomes a multi-system project that nobody starts because nobody can finish. | ☐ |
| 3 | Layer dependencies are enforced by tooling, not by code review ‖ Code review catches violations sometimes; tooling catches them every time. Module visibility, build-system boundaries, or dependency-direction linters turn the layering policy into structure rather than into hope. | ☐ |
| 4 | Plugin and extension contracts are versioned and reviewed alongside code ‖ Plugin surfaces are public API even when "internal." Versioning them and reviewing changes prevents the kernel from drifting in ways that break extensions and forces every kernel change to consider its downstream impact. | ☐ |
| 5 | New behaviour is preferentially added by composition, not inheritance extension ‖ The "extends BaseService" reflex usually creates split-personality classes that nobody can maintain. Composition keeps changes local; inheritance distributes them across the hierarchy and amplifies their cost. | ☐ |
| 6 | Linear workflows are structured as pipelines with independent stages ‖ Pipelines match data flow shape; request-response chains for inherently linear workflows produce coordination complexity for no benefit. Match structure to flow, not the other way around. | ☐ |
| 7 | Framework conventions are recognised as conventions, not as the architecture ‖ Frameworks come and go; architecture should outlast them. Documenting the structural pattern separately from the framework prevents a framework migration from becoming a re-architecture project nobody asked for. | ☐ |
| 8 | Pattern departures (mixing patterns, hybrid structures) are documented with reasons ‖ Hybrid structures (layered + hexagonal, microkernel + microservices) are common and often correct, but the departure should be deliberate — "we mix these because X" rather than accidental. The departure documents what to keep watching when the shape evolves. | ☐ |
| 9 | The system's structural pattern is articulable by team members who didn't design it ‖ If only the original designer can describe the structure, the structure exists in tribal memory and will erode the moment that person leaves. Tested by asking new team members what pattern the system uses. | ☐ |
| 10 | Refactors are evaluated against whether they preserve or violate the structural pattern ‖ Refactoring as cleanup easily violates the original structure if the structure isn't named. Articulating the pattern makes it possible to refactor without eroding the architecture; without articulation, every cleanup is also a quiet vote for "no architecture." | ☐ |

---

## Related

[`principles/foundational`](../../principles/foundational) | [`principles/domain-specific`](../../principles/domain-specific) | [`patterns/data`](../data) | [`patterns/integration`](../integration) | [`patterns/security`](../security) | [`patterns/deployment`](../deployment)

---

## References

1. [Gamma, Helm, Johnson, Vlissides — Design Patterns (GoF)](https://en.wikipedia.org/wiki/Design_Patterns) — *Wikipedia*
2. [Buschmann et al. — Pattern-Oriented Software Architecture (POSA)](https://en.wikipedia.org/wiki/Pattern-Oriented_Software_Architecture) — *Wikipedia*
3. [Mark Richards — Software Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/) — *O'Reilly*
4. [Mark Richards & Neal Ford — Fundamentals of Software Architecture](https://www.oreilly.com/library/view/fundamentals-of-software/9781492043447/) — *O'Reilly*
5. [Alistair Cockburn — Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_%28software%29) — *Wikipedia*
6. [Microkernel Architecture](https://en.wikipedia.org/wiki/Microkernel) — *Wikipedia*
7. [Pipeline (software)](https://en.wikipedia.org/wiki/Pipeline_%28software%29) — *Wikipedia*
8. [Multitier Architecture](https://en.wikipedia.org/wiki/Multitier_architecture) — *Wikipedia*
9. [Composition over Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) — *Wikipedia*
10. [SOLID Principles](https://en.wikipedia.org/wiki/SOLID) — *Wikipedia*
