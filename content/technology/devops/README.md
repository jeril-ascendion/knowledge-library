# DevOps

**DevOps & SRE Excellence — streamlining delivery via automation, IaC, and observability.** DevOps is the operational backbone of modern delivery: the difference between an engineering team that ships weekly and a team that doesn't. This page describes how we approach pipelines, infrastructure as code, GitOps, observability, and the supply-chain security that has become non-negotiable.

**Section:** `technology/` | **Subsection:** `devops/`
**Alignment:** GitHub Actions | Terraform | OpenTelemetry | SLSA

---

## What "DevOps" actually means

DevOps started as a cultural movement against the dev-vs-ops wall and matured into an engineering discipline with specific patterns. The discipline has four pillars: continuous delivery (the pipeline), infrastructure as code (the platform), observability (the visibility), and supply-chain security (the trust). Each pillar has its own tooling, its own maturity progression, and its own way of failing when neglected. A team that does CI/CD well but treats infrastructure as a manual process pays for the imbalance in unreliable environments; a team that has perfect infrastructure but no observability ships fast and is blind in production.

Doing DevOps well means investing in all four pillars, with the discipline to keep them current as the team and the system grow. The tools change every two years; the principles do not.

---

## Six principles

### 1. Pipelines are code; treat their reliability with the same rigor

A CI/CD pipeline is the gate between every code change and production. When the pipeline is flaky, every team is slowed; when it is unreliable, releases happen with bypassed gates that come back as production incidents. Treating the pipeline as a first-class engineering artefact — versioned, reviewed, tested, and operated — is the difference between fast delivery and fast theatrical delivery. Pipelines defined in YAML in the repo, with tests for the pipeline itself, with explicit ownership, with monitoring that flags flake rates, are what separate teams that ship reliably from teams that ship occasionally.

#### Architectural implications

- Pipelines are defined in the repository (GitHub Actions workflows, GitLab CI, Argo Workflows) and versioned alongside the code they build.
- Pipeline failures are diagnosed and fixed, not retried until they pass; flake rates are tracked as a quality metric.
- Pipeline performance (build time, test time) is measured; regressions are addressed because slow pipelines silently encourage workflow shortcuts.

#### Reference

[GitHub Actions Documentation](https://docs.github.com/en/actions) — the reference for pipeline-as-code patterns now widely adopted across the industry.

---

### 2. Infrastructure as code or no infrastructure

Infrastructure that exists outside of code drifts. The team that "documented the production setup" two years ago has documentation that no longer matches reality, and the only way to know what's actually running is to look. Infrastructure as code (Terraform, Pulumi, AWS CDK, Bicep) makes the desired state explicit and auditable; the running state is verified to match the code; changes are reviewed as code changes are reviewed. The discipline scales — a team of three can hold the running state in their heads; a team of thirty cannot, and the team that didn't adopt IaC at five engineers regrets it at fifty.

#### Architectural implications

- All infrastructure (network, compute, identity, data services) is defined in Terraform/Pulumi/CDK; manual changes are treated as incidents to be reverted.
- Drift detection runs continuously; deviations between code and reality are surfaced and reconciled.
- Modules are reusable across environments — dev, staging, production differ in size and configuration, not in shape.

#### Reference

[Terraform](https://www.terraform.io/) — the de facto standard for cloud-agnostic infrastructure as code, with a rich provider ecosystem and well-developed patterns for managing state, modules, and drift.

---

### 3. GitOps makes the desired state visible

The natural extension of IaC is GitOps: the git repository is not just the source of code, it is the source of truth for the desired state of the running system. A controller (Argo CD, Flux) continuously reconciles the running state to the repository state. Deployments happen by merging to a branch; rollbacks happen by reverting commits; the audit trail of what's running is the git log of the deployment branch. The mental model is declarative — describe what should be running, let the controller make it so — instead of imperative — run a deployment script and hope.

#### Architectural implications

- Production state lives in a git repository; controllers continuously reconcile running clusters to that state.
- Deployments are pull requests; rollbacks are revert commits; the change log of production is the git log.
- Drift detection is structural — the controller flags any difference between desired and actual state, not just changes initiated through the controller.

#### Reference

[OpenGitOps Principles](https://opengitops.dev/) — the formal articulation of GitOps as a discipline (declarative, versioned, automatically pulled, continuously reconciled).

---

### 4. Observability is one question, not three pillars

The "three pillars of observability" — logs, metrics, traces — is a useful taxonomy and a misleading framing. The pillars suggest three separate systems with three separate tools; the actual question observability answers is one: *what is happening in this system right now, and why?* Modern observability platforms (OpenTelemetry-instrumented stacks, Honeycomb, Grafana Tempo, Datadog) treat the three signals as facets of a single underlying telemetry stream. The discipline is not "we have logs, metrics, and traces" — it is "we can ask any question about production behaviour and get an answer in seconds."

#### Architectural implications

- Telemetry is collected with OpenTelemetry, the vendor-neutral standard, allowing the backend to be swapped without re-instrumenting.
- High-cardinality dimensions (per-customer, per-route, per-version) are first-class — observability without high cardinality answers only the easy questions.
- The team's instinct in an incident is to *query* observability data, not to grep logs. The infrastructure that makes that possible is what makes the difference.

#### Reference

[Charity Majors et al. — Observability Engineering](https://www.honeycomb.io/blog/observability-101-terminology-and-concepts) — the canonical treatment of observability as a discipline distinct from monitoring, with high-cardinality, high-dimensionality telemetry as the differentiator.

---

### 5. Security shifts left; compliance shifts everywhere

"Shift left" — finding security issues earlier in the lifecycle — has become a phrase that hides the work it entails. The actual discipline includes static analysis (SAST) integrated into CI, software composition analysis (SCA) scanning for vulnerable dependencies, secrets scanning preventing credentials from entering the repo, dynamic analysis (DAST) of running applications, infrastructure scanning before apply, and supply-chain attestation (SLSA) verifying that what's deployed is what was built. Compliance — SOC 2, ISO 27001, HIPAA, PCI — used to be a once-a-year audit; modern compliance is continuous, with controls that are evidenced automatically rather than reconstructed annually.

#### Architectural implications

- SAST, SCA, and secrets scanning run on every PR; security findings are addressed before merge, not deferred.
- Container images are scanned for vulnerabilities; signed at build; verified at deploy; the chain of custody is auditable.
- SLSA provenance is generated for build artefacts; the deployment system verifies provenance before running production workloads.
- Compliance controls are encoded as policy-as-code (OPA, Sentinel) and evaluated continuously, not assembled for audit.

#### Reference

[SLSA Framework](https://slsa.dev/) — the industry standard for supply-chain integrity, originating at Google and adopted across the cloud-native ecosystem.

---

### 6. Continuous deployment is a product capability, not an engineering nicety

Small batches reduce risk. The empirical evidence is overwhelming — teams that deploy daily have lower change-failure rates and shorter mean-time-to-restore than teams that deploy quarterly. This isn't because daily deployment is magic; it's because daily deployment forces every engineering practice the prior principles describe: reliable pipelines, IaC, observability, and security automation. Treating continuous deployment as a target — an explicit product capability, with the engineering investment to support it — is what aligns the rest of the practices around a measurable goal. Without that target, "we should improve our pipelines" is a wish; with it, the gap between current state and target is concrete and can be closed.

#### Architectural implications

- Deploy frequency, change-failure rate, lead time, and mean-time-to-restore (the DORA metrics) are measured and visible.
- The team has documented goals for each metric and reviews progress quarterly; gaps drive engineering investment.
- Feature flags decouple deploy from release — code can be deployed inert and activated separately, removing the pressure to perfect every deploy.

#### Reference

[DORA — Accelerate State of DevOps](https://dora.dev/) — the multi-year, peer-reviewed research showing that continuous-delivery practices correlate with both engineering quality and organisational performance.

---

## Architecture Diagram

The diagram below shows a canonical DevOps architecture: a CI pipeline triggered by code changes, building artefacts and generating provenance; a CD pipeline (or GitOps controller) deploying to environments; IaC managing the underlying infrastructure; observability collecting telemetry across the stack; policy-as-code enforcing compliance continuously.

---

## Common pitfalls

### ⚠️ Pipeline as a one-off script

The CI/CD pipeline started as a build script someone wrote, with no tests, no review, no monitoring. When it breaks, no one knows why; when it's slow, no one investigates; flake is normalised. The pipeline is the most-run code in the system and the least-engineered.

#### What to do instead

The pipeline is engineering work with engineering discipline — versioned in the repo, reviewed in PRs, monitored for flake and duration, owned by a named team.

---

### ⚠️ IaC for new things, manual for old

Greenfield projects use Terraform; legacy infrastructure is "too risky" to migrate, so it stays manual. The two halves diverge in operational characteristics, the manual half consumes disproportionate time, and the team gets the worst of both worlds.

#### What to do instead

A migration plan that brings legacy infrastructure into IaC over quarters. Drift detection covers the entire estate; the manual exception is documented and time-bounded.

---

### ⚠️ Observability as logs

A logging system is treated as the entire observability story. Metrics are bolted on later for SLOs; tracing is "for when we have time." Investigating production issues means greping through logs across services with correlation IDs that may or may not exist.

#### What to do instead

OpenTelemetry from day one — logs, metrics, traces as a single instrumented stream. The cost of doing this from the start is small; the cost of retrofitting is large.

---

### ⚠️ Security as a gate, not a stream

Security is the audit at the end of the cycle. Findings arrive late; fixing them disrupts release plans; the team's instinct is to negotiate severity rather than fix.

#### What to do instead

Security in the pipeline — SAST, SCA, secrets scanning, supply-chain attestation. Findings appear at PR time, when the cost of fixing is lowest. The audit becomes a verification of what's already done.

---

### ⚠️ Continuous deployment without continuous testing

The team adopts continuous deployment because it sounds modern, without the test coverage, observability, or feature-flagging that make it safe. Every deployment is a roll of the dice; production incidents trace back to deployments; the team retreats to release windows.

#### What to do instead

Continuous deployment is the *result* of the prior practices, not a starting point. Build the safety nets — tests, observability, feature flags, fast rollback — and continuous deployment becomes the natural mode rather than a bet.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Pipelines are versioned, reviewed, and operated as engineering artefacts ‖ Pipeline-as-code in the repo; tests for the pipeline itself; flake rates and duration tracked; pipeline incidents diagnosed not retried-until-green. | ☐ |
| 2 | All infrastructure is defined in IaC (Terraform / Pulumi / CDK) ‖ Manual infrastructure changes are exceptions, documented and reverted; drift detection runs continuously; environments differ in size and config, not shape. | ☐ |
| 3 | Production state is reconciled from git via a GitOps controller ‖ Argo CD or Flux watches the deployment branch; merges trigger reconciliation; the git log is the audit trail of what's running. | ☐ |
| 4 | OpenTelemetry instrumentation is the standard, not an opt-in ‖ Logs, metrics, and traces are correlated by trace ID; high-cardinality dimensions are first-class; the team queries telemetry to answer questions. | ☐ |
| 5 | DORA metrics (deploy frequency, lead time, change-failure rate, MTTR) are measured and visible ‖ Numbers are real, not aspirational; goals are documented; quarterly reviews drive engineering investment. | ☐ |
| 6 | SAST, SCA, and secrets scanning run on every PR ‖ Findings address before merge; the security team and engineering team see the same data; the conversation is "fix" not "negotiate severity." | ☐ |
| 7 | Container images are signed at build, scanned for vulnerabilities, and verified at deploy ‖ The chain of custody from source to running container is auditable; SLSA provenance is generated and verified. | ☐ |
| 8 | Compliance controls are encoded as policy-as-code (OPA / Sentinel) ‖ Continuous evaluation rather than annual reconstruction; drift between intended controls and effective controls is detected. | ☐ |
| 9 | Feature flags decouple deploy from release for risky changes ‖ Code can deploy inert and activate separately; rollback is a flag toggle, not a redeploy; the deploy-vs-release distinction is operationally real. | ☐ |
| 10 | Incident response is exercised, not just documented ‖ Runbooks are current; on-call rotations are sustainable; postmortems happen for every meaningful incident and the actions are tracked to closure. | ☐ |

---

## Related

[`technology/cloud`](../cloud) | [`technology/api-backend`](../api-backend) | [`patterns/deployment`](../../patterns/deployment) | [`patterns/security`](../../patterns/security) | [`principles/cloud-native`](../../principles/cloud-native) | [`system-design/ha-dr`](../../system-design/ha-dr)

---

## References

1. [GitHub Actions](https://docs.github.com/en/actions) — *github.com*
2. [Terraform](https://www.terraform.io/) — *terraform.io*
3. [Argo CD](https://argo-cd.readthedocs.io/) — *argo-cd.readthedocs.io*
4. [Flux CD](https://fluxcd.io/) — *fluxcd.io*
5. [OpenTelemetry](https://opentelemetry.io/) — *opentelemetry.io*
6. [OpenGitOps Principles](https://opengitops.dev/) — *opengitops.dev*
7. [SLSA Framework](https://slsa.dev/) — *slsa.dev*
8. [DORA — Accelerate State of DevOps](https://dora.dev/) — *dora.dev*
9. [Prometheus](https://prometheus.io/) — *prometheus.io*
10. [Grafana](https://grafana.com/) — *grafana.com*
