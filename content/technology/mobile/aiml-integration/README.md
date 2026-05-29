# AI/ML Integration Considerations

> **Section:** `technology/mobile/aiml-integration/`
> **Alignment:** Google ML Kit | Apple Core ML | TensorFlow Lite | On-Device Privacy | NIST AI Risk Framework
> **Audience:** Mobile Architects · AI/ML Engineers · Solutions Architects · Privacy Officers

AI and ML capabilities are increasingly expected in mobile applications — document scanning with OCR, personalised recommendations, real-time translation, biometric verification, and anomaly detection. The architectural decision that defines the integration approach is: on-device inference versus cloud inference. Each has distinct implications for latency, privacy, cost, model update cadence, and functionality scope.

## Overview

On-device inference processes data locally without network round-trips. Cloud inference sends data to a server for processing. The choice is not binary — many applications use on-device for latency-sensitive features and cloud for complex models that cannot fit in device memory. The architectural principle: minimise the data that leaves the device for AI/ML processing, especially when that data contains PII, biometrics, or health information.

## On-Device Inference

### Apple Core ML
Core ML runs trained models on Apple Neural Engine (ANE) — available on A11 Bionic and later, delivering 15-38 TOPS depending on chip generation. Models converted to `.mlmodel` format using `coremltools` Python library from PyTorch, TensorFlow, or ONNX source. Core ML Compiler optimises the model for the target hardware at build time. Privacy benefit: no data leaves the device. Latency: sub-100ms for most models on ANE. Limitation: model size constrained by device storage and memory.

Use cases: document OCR (Vision framework), face detection and recognition (Vision + Core ML), language detection (Natural Language framework), on-device text generation (Apple Intelligence on A17 Pro and M-series), personalised recommendations (Create ML trained on-device with private user data).

### TensorFlow Lite and Google ML Kit
TensorFlow Lite converts TensorFlow models to `.tflite` format, optimised for mobile inference through quantisation (reducing model precision from float32 to int8 — 4× size reduction with minimal accuracy loss). GPU delegate for hardware acceleration on Qualcomm Adreno and ARM Mali GPUs. NNAPI delegate for Qualcomm, MediaTek, and Samsung NPUs on Android.

Google ML Kit provides pre-built, optimised on-device models: text recognition (Latin and Chinese scripts), face detection, barcode scanning, pose estimation, object detection, language identification, translation. Zero model management — ML Kit handles model downloads and updates. For custom models, ML Kit's Custom Models API hosts and serves `.tflite` models with OTA updates.

### Gemini Nano (On-Device LLM)
Google Gemini Nano runs locally on Pixel 8+ and select Android 14+ devices via Android AICore. Provides summarisation, smart reply, and proofreading capabilities without network access. Access via Android Gemini SDK with capability checking (not all devices have Gemini Nano).

Apple Intelligence provides on-device foundation model inference on iPhone 15 Pro (A17 Pro) and iPhone 16 series, iPad Pro with M-series chips. Privacy-preserving: user context processed on device for most features; complex requests routed to Private Cloud Compute with cryptographic guarantees.

## Cloud Inference

Cloud inference is appropriate for: models too large for device memory (>100MB for mobile), frequent model updates required without app releases, complex reasoning requiring large LLM context windows, and features where network latency is acceptable (non-real-time analysis).

Architecture pattern: requests processed at the BFF layer — the mobile app sends a structured request, the BFF calls the ML service, returns a structured response. The mobile app never communicates directly with the ML inference endpoint. This maintains the BFF as the single integration boundary and enables model changes without mobile app releases.

## Privacy Considerations for Mobile AI

On-device AI is the privacy-preferred architecture. Data used for inference is never transmitted. Data cannot be intercepted in transit. PDPA Philippines, GDPR, and HIPAA all favour on-device processing for sensitive data categories.

When cloud inference is required for regulated data (PHI, financial records, biometrics): data minimisation (send only the minimum required for inference, not the full record), encryption in transit (TLS 1.3), transient processing (no persistent storage of inference inputs on cloud infrastructure), explicit user consent.

## Anti-Patterns to Avoid

> **⚠ Sending Raw Biometrics to Cloud for Verification** — Transmitting facial images or fingerprint data to a cloud API for identity verification. Creates a biometric data repository that is a high-value breach target and may violate biometric data regulations.
> **CORRECT:** On-device biometric verification using platform APIs (Face ID/Touch ID on iOS, BiometricPrompt on Android). Biometrics never leave the device. The platform's secure enclave handles comparison.

> **⚠ Blocking UI for Model Inference** — Running a TensorFlow Lite model inference on the main thread, producing UI lag during document scanning or image classification.
> **CORRECT:** Inference runs on a background thread (Dispatchers.Default on Android, background Task on iOS). Results published to the UI through StateFlow/ObservableObject when complete.

## References

1. Apple — Core ML Documentation. developer.apple.com/documentation/coreml
2. Google — ML Kit. developers.google.com/ml-kit
3. TensorFlow — TensorFlow Lite. tensorflow.org/lite
4. Google — Android AICore (Gemini Nano). developer.android.com/ml/gemini-nano
5. NIST — AI Risk Management Framework. nist.gov/system/files/documents/2023/01/26/AI RMF 1.0.pdf
