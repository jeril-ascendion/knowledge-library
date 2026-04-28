# Edge AI Systems

Architecture for AI systems that run *where the data is* — on phones, vehicles, sensors, browsers, and embedded devices — under constraints that do not exist in the cloud, with lifecycles that the cloud's deployment patterns do not address.

**Section:** `system-design/` | **Subsection:** `edge-ai/`
**Alignment:** ONNX | TensorFlow Lite | Federated Learning | Edge Computing

---

## What "edge AI" actually means

A *cloud-by-default* approach to AI assumes inference happens in a datacentre: the device collects data, sends it to a service, the service runs the model, the result comes back. This works for many problems and breaks down for many more — when latency requirements are sub-100ms, when the data is too sensitive to leave the device, when the device has no reliable connection, when the volume of data is too large to ship, when the cost per inference at cloud scale exceeds what the workload can pay.

An *edge AI* approach treats inference at the edge as a first-class architectural option, with its own constraints and patterns. Models are compressed to fit edge hardware. Their lifecycle differs from cloud models — they are deployed over the air, run on devices that fragment by hardware generation, and update on schedules the user (not the platform) controls. The split between what runs at the edge and what runs in the cloud is a planned division of labour, not a fallback when the network is bad.

The architectural shift is not "we run a model on the device." It is: **edge AI is its own architectural problem with its own constraints, lifecycle, and governance — and treating it as "cloud AI but smaller" produces systems that are slow at the edge, fragile in the field, and accidental in their privacy posture.**

---

## Six principles

### 1. Inference belongs where the data lives

The default architectural reflex — collect data here, ship it to the model there — is often wrong for edge. When the data is high-volume (video frames, sensor streams), high-rate (real-time control signals), or high-sensitivity (biometrics, location), shipping it to a cloud model imposes latency, bandwidth, and privacy costs that may exceed the value of the inference itself. The alternative is to bring the model to the data: deploy compressed models to the edge, run inference locally, ship only what is necessary back to the cloud (aggregates, anomalies, training signal). The architectural insight is that data location and inference location are independent decisions, and choosing them separately is what makes edge AI viable.

#### Architectural implications

- Inference location is a per-capability decision, not a system-wide default — different capabilities run at the edge, in the cloud, or in hybrid configurations based on their actual constraints.
- Data flow is designed to ship the minimum necessary upstream — inferences, summaries, anomalies — rather than raw input.
- Privacy commitments (data does not leave the device) are enforced architecturally, not stated in policy documents that the implementation can quietly violate.
- Hybrid topologies (edge inference + cloud training, edge filtering + cloud heavy lifting) are deliberate designs with documented data flows, not accidents of which engineer built which half first.

#### Quick test

> Pick the most data-intensive AI capability in your system. Where does the inference run, and how much raw data leaves the device? If raw video, audio, or sensor streams flow to the cloud just so a model can run on it, ask whether the same model could run on the device — and what the latency, bandwidth, and privacy gains would be if it did.

#### Reference

[Edge Computing](https://en.wikipedia.org/wiki/Edge_computing) — the broader paradigm of which edge AI is the inference-specific case. The architectural argument predates AI by decades; ML simply made it more consequential.

---

### 2. Model size is an architectural decision, not a hyperparameter

Whether a model fits on the target device, runs within the latency budget, and stays within thermal limits is determined by its size, its architecture, and the precision of its weights — choices that are made jointly, not selected by a researcher and accepted by an engineer downstream. Quantisation (reducing weights to 8-bit, 4-bit, even 2-bit), distillation (training a small student from a large teacher), pruning (removing weights that contribute least), and architecture search (choosing model topology for the target hardware) are not optimisations applied to a finished model — they are architectural commitments that shape what is deployable. The team that treats compression as a post-processing step ends up with models the hardware cannot run.

#### Architectural implications

- Model compression strategy is decided alongside model selection, not after training.
- Accuracy/size trade-offs are evaluated against deployment constraints, not against research benchmarks that no real device matches.
- The compressed model's accuracy is the relevant accuracy, not the original full-precision model's — and is benchmarked on real device hardware, not in the cloud.
- Hardware-specific optimisations (NPU instructions, GPU kernels, vendor compilers) are part of the deployment pipeline, with measurable impact on latency and power.

#### Quick test

> Pick the largest model targeted for an edge device in your system. What is its compressed size, its compressed accuracy, and its measured latency on the target hardware? If those numbers come from the cloud or from a desktop GPU, the compressed model has not been evaluated where it will actually run.

#### Reference

[ONNX](https://onnx.ai/) provides a portable model representation that supports runtime compression and hardware-specific optimisation; [TensorFlow Lite](https://www.tensorflow.org/lite) is the canonical reference for the on-device deployment pipeline including post-training quantisation.

---

### 3. Edge models have a different lifecycle than cloud models

Cloud models are deployed by the platform team, run on infrastructure the platform team controls, and updated whenever the platform team chooses. Edge models are deployed *to* devices the platform team does not control, run on hardware that fragments across generations, and update on schedules the user controls — when the device has connectivity, power, and consent. The deployment patterns from the cloud world do not transfer: there is no "rolling deployment" across devices that turn off; there is no "instant rollback" when the rollback channel is the same intermittent connection that delivered the buggy model in the first place. Edge model lifecycle is its own discipline.

#### Architectural implications

- Over-the-air model updates have explicit policies for partial rollout, A/B testing, rollback, and version skew between models and the apps that call them.
- Device fragmentation (hardware generations, OS versions, accelerator availability) is a first-class deployment concern, not "an issue we'll handle later".
- Models on devices that have not connected in months, years, or ever are part of the supported population — the architecture either accommodates them or explicitly cuts them off.
- Telemetry from edge models (accuracy in the field, drift detection, failure modes) flows back to the platform via mechanisms designed for partial connectivity and bandwidth limits.

#### Quick test

> Pick an edge model in production. If you discovered a critical bug in it right now, how long until you could roll it back across all installed devices? If the answer is "we'd push an update and hope," the rollback story is aspirational. If the answer involves "fleet management" tooling that you trust, the lifecycle has been engineered.

#### Reference

The [Federated Learning](https://en.wikipedia.org/wiki/Federated_learning) literature provides one mature pattern for the lifecycle problem; the broader treatment lives in mobile platform documentation and the OTA update systems built on top of it.

---

### 4. Latency-bound problems demand edge or are not real-time problems

If the latency budget for a decision is 50 milliseconds, the round trip to a cloud datacentre — typically 50–200ms in the best case, more under load or congestion — has already consumed the budget before the model has run. Real-time perception (autonomous driving, AR overlays, gesture recognition), real-time interaction (voice assistants, low-latency translation, gameplay), and real-time control (robotics, manufacturing, medical instruments) all live in latency regimes where cloud inference is structurally impossible. The architectural choice is not "edge or cloud, whichever is more convenient" — it is "edge, or accept that this is not a real-time problem after all". Pretending otherwise produces systems that pass demos and fail in production.

#### Architectural implications

- The latency budget for each AI-driven decision is documented and known, not assumed.
- Latency budgets that fall below cloud round-trip time are recognised as edge requirements, not as cloud SLOs to be optimised toward.
- "Hybrid" architectures (edge for low-latency, cloud for occasional heavy lifting) are designed around the latency boundary, with edge providing the time-critical path.
- Apparent real-time performance that depends on perfect connectivity is treated as a fragile illusion — it works in the demo, fails the first time the user is on a train.

#### Quick test

> Pick an AI capability described as "real-time" in your system. What is its actual latency budget, and what does it do when the network round-trip exceeds that budget? If the answer is "it gets slow," the real-time claim is marketing rather than architecture.

#### Reference

The latency hierarchy is well documented; [Peter Norvig's classic latency numbers](https://norvig.com/21-days.html#answers) remain the canonical illustration of why network round-trips are an order of magnitude more expensive than anything happening on-device.

---

### 5. Federated and on-device learning are governance models, not just techniques

Federated learning lets devices contribute to a shared model without raw data ever leaving the device — gradients or model updates flow up; raw data does not. On-device learning takes this further: the model adapts to the user without any updates flowing anywhere. Both are described in technical terms ("we federate" / "we learn on-device") but the architectural commitment they make is governance, not algorithm: who has access to what, who can change the model, who is responsible when the model misbehaves, what the user has consented to. Adopting these techniques without taking the governance seriously produces systems that claim privacy benefits the architecture does not actually provide.

#### Architectural implications

- The data that does and does not leave the device is documented, enforced architecturally, and verifiable by audit.
- Gradient privacy (preventing reconstruction of training data from gradients) is treated as a real threat model, with mitigations like differential privacy or secure aggregation chosen explicitly rather than implied.
- The lifecycle of the federated/on-device model — who can read it, who can replace it, what happens on device transfer or wipe — is part of the design.
- User consent for the data flows, retraining, and personalisation involved is part of the architecture, not a checkbox during onboarding.

#### Quick test

> Pick the federated or on-device learning system you operate. What exactly leaves each device, what could in principle be reconstructed from what leaves, and what are the documented mitigations? If those answers are not crisp, the privacy claim rests on the technique's name rather than on what the architecture actually guarantees.

#### Reference

[Federated Learning](https://en.wikipedia.org/wiki/Federated_learning) — both the algorithmic foundation and the literature on its privacy limitations, and the techniques (DP, SecAgg) that strengthen them.

---

### 6. The edge/cloud split is a planned division of labour, not an accident

Most edge AI systems are hybrids: some inference on-device, some in the cloud, some training on aggregated data, some adaptation per-user, some logic switching between modes based on connectivity. The split between what happens where determines the system's latency, privacy, cost, and operability. Letting the split emerge from "what's easiest to build first" produces systems where the boundary between edge and cloud lives in the heads of the original engineers, drifts with every change, and turns into a coordination disaster when the team grows. Naming the split deliberately — what runs at the edge, what runs in the cloud, when does it sync, what happens when it cannot — turns hybrid AI from accidental to architectural.

#### Architectural implications

- The on-device behaviour, cloud-side behaviour, and synchronisation logic are designed and documented as a single system, not as separate concerns owned by separate teams.
- Offline behaviour is a first-class design decision: which capabilities degrade gracefully, which stop, which queue for later sync.
- Sync semantics (when does the device push results, when does it pull updates, what conflicts can arise) are explicit in the contract between edge and cloud.
- Cost, latency, and privacy implications of the split are evaluated jointly — moving work between edge and cloud changes all three at once, in ways that benefit one and may compromise another.

#### Quick test

> Pick a hybrid AI capability in your system. Without looking at code, can you describe what runs at the edge, what runs in the cloud, when they sync, and what happens during a 24-hour offline period? If the description requires reading code, the split is implicit and will diverge as the system evolves.

#### Reference

The [Edge Computing](https://en.wikipedia.org/wiki/Edge_computing) literature treats the division of labour as the central design problem; for AI specifically, the on-device-vs-cloud split has become the defining architectural question of mobile and IoT product design.

---

## Architecture Diagram

The diagram below shows a canonical edge AI topology: edge devices running compressed inference locally; a sync channel carrying telemetry, anomalies, and federated updates upstream; a cloud-side aggregator producing the next generation of models; OTA deployment back down to devices. The split between what runs where is named and bidirectional — neither side is a fallback for the other.

---

## Common pitfalls when adopting edge AI

### ⚠️ Treating edge as "cloud, but smaller"

The instinct to take a cloud architecture and shrink it for edge ignores that edge has fundamentally different constraints — power, thermal, intermittent connectivity, device fragmentation, no central control plane. Architectures that work in the cloud often produce edge systems that drain batteries, overheat, fail offline, and cannot be updated reliably.

#### What to do instead

Design for edge constraints from the beginning. Power and thermal budgets, offline behaviour, OTA reliability, and device fragmentation are first-class architectural concerns — not problems to solve after the cloud architecture has been ported.

---

### ⚠️ Static models forever

Edge models are deployed and forgotten — the assumption being that a model trained once and shipped will continue to work. Models drift: real-world data shifts, user behaviour changes, the model encounters distributions it was never trained on. Without lifecycle management, the models silently degrade until the user-facing accuracy drops below what the architecture's quality bars demand.

#### What to do instead

Edge models have a lifecycle: drift detection, retraining cadence, update deployment, rollback paths. The lifecycle infrastructure costs real engineering — that cost is the price of edge AI being a sustained capability rather than a launch event.

---

### ⚠️ Underestimating compression trade-offs

Quantising a 32-bit model to 8-bit and assuming accuracy will be "close enough" without measuring on the target hardware. Real-world quantisation often produces accuracy drops in specific input distributions (rare classes, edge cases, adversarial inputs) that benchmark accuracy does not reveal — and these are exactly the cases that matter in production.

#### What to do instead

Measure compressed accuracy on the target hardware against the same data slices you care about in production. Treat compression-induced accuracy drops in critical slices as bugs, not as expected trade-offs to accept.

---

### ⚠️ Ignoring battery and thermal cost

Inference is computational work; computation costs energy and produces heat. Edge AI systems that run inference continuously can drain a phone battery in hours, throttle the device thermally, and produce a worse user experience than cloud inference would have despite the latency win.

#### What to do instead

Power and thermal budgets are explicit constraints. Batch inference, run on schedule rather than continuously, exploit hardware accelerators (NPUs, DSPs) that are far more power-efficient than CPU/GPU paths, and measure the cost in milliwatt-hours, not just in latency.

---

### ⚠️ Federated learning as black box

Adopting federated learning because it sounds private, without understanding what gradients can leak about the data they were computed from. Without differential privacy, secure aggregation, or other explicit mitigations, federated learning provides weaker privacy guarantees than the marketing implies — and the gap is invisible until a researcher demonstrates a reconstruction attack.

#### What to do instead

Treat federated privacy as a real threat model. Document what the architecture protects against and what it does not. Apply DP, SecAgg, or both where the threat model demands them — and audit the resulting privacy guarantees rather than claiming them.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Inference location for each AI capability is a documented decision with named trade-offs ‖ Cloud-by-default and edge-by-default are both wrong as universal rules. The decision is per-capability, based on latency, bandwidth, privacy, cost, and operability — and the rationale is recorded so the choice can be revisited deliberately when the trade-offs change. | ☐ |
| 2 | Model compression strategy is chosen alongside model architecture, not after training ‖ The compressed model is the actual deployment artefact. Treating compression as post-processing produces models that don't fit, don't run, or don't perform — discovered late, when the cost of changing direction is highest. | ☐ |
| 3 | Compressed model accuracy is measured on target device hardware, on real production data slices ‖ Cloud benchmarks lie about edge accuracy. The accuracy that matters is the accuracy on the hardware the user owns, on the data slices that matter to the product — not aggregate scores on synthetic test sets evaluated in a datacentre. | ☐ |
| 4 | OTA model deployment supports staged rollout, rollback, and version skew with the calling app ‖ Edge devices are not a Kubernetes cluster. Updates reach them on the user's schedule, fail in user-specific ways, and run alongside app versions that may be older or newer. The deployment system handles all of these as routine, not as exceptions. | ☐ |
| 5 | Device fragmentation (hardware generation, OS, accelerator) is a first-class deployment concern ‖ The deployment matrix is real. Treating it as "we'll figure it out per device" means the team will figure it out under pressure during incidents. Treating it as a designed system means the matrix is enumerated, tested, and budgeted for. | ☐ |
| 6 | Telemetry from edge models flows back via mechanisms designed for partial connectivity ‖ Edge models drift; you only know they drifted if telemetry returns. The telemetry pipeline is explicit, sample-rated, bandwidth-aware, and survives long offline periods rather than failing silently when devices are out of contact. | ☐ |
| 7 | Latency budgets for AI capabilities are documented and known, not assumed ‖ "Real-time" without a number is not a requirement, it is a vibe. Documented latency budgets force the architectural choice between edge and cloud to be made deliberately rather than discovered when the demo fails on stage. | ☐ |
| 8 | Privacy claims about on-device or federated processing are verifiable by audit ‖ Architectural claims about data locality and privacy must be enforceable, not aspirational. Logs, network audits, or instrumentation that prove the claim — not merely a statement in the privacy policy that the data stays on-device. | ☐ |
| 9 | Power and thermal cost of inference is measured and budgeted ‖ Battery drain and device heat are user-visible failure modes that bypass every other quality bar. Measuring them in milliwatt-hours or thermal headroom turns the constraint into an engineering target rather than a customer complaint that arrives weeks after launch. | ☐ |
| 10 | The edge/cloud split is documented for each capability — including offline behaviour ‖ Hybrid systems where the boundary lives only in the original author's head become impossible to evolve safely. Explicit boundary documentation, including what runs offline and how state reconciles when connectivity returns, is the architecture itself rather than a description of it. | ☐ |

---

## Related

[`principles/ai-native`](../../principles/ai-native) | [`principles/cloud-native`](../../principles/cloud-native) | [`principles/foundational`](../../principles/foundational) | [`patterns/data`](../../patterns/data) | [`patterns/deployment`](../../patterns/deployment) | [`patterns/security`](../../patterns/security)

---

## References

1. [ONNX — Open Neural Network Exchange](https://onnx.ai/) — *onnx.ai*
2. [TensorFlow Lite](https://www.tensorflow.org/lite) — *tensorflow.org*
3. [Federated Learning](https://en.wikipedia.org/wiki/Federated_learning) — *Wikipedia*
4. [Edge Computing](https://en.wikipedia.org/wiki/Edge_computing) — *Wikipedia*
5. [Apple Core ML](https://developer.apple.com/documentation/coreml) — *developer.apple.com*
6. [Differential Privacy](https://en.wikipedia.org/wiki/Differential_privacy) — *Wikipedia*
7. [Quantization in machine learning](https://en.wikipedia.org/wiki/Quantization_%28signal_processing%29) — *Wikipedia*
8. [Knowledge Distillation](https://en.wikipedia.org/wiki/Knowledge_distillation) — *Wikipedia*
9. [Peter Norvig — Latency numbers every programmer should know](https://norvig.com/21-days.html#answers) — *norvig.com*
10. [ETSI Multi-access Edge Computing (MEC)](https://www.etsi.org/technologies/multi-access-edge-computing) — *etsi.org*
