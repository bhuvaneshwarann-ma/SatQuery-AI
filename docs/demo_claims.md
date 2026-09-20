# SatQuery AI — Demo-Safe Claims & Evaluation Boundaries

This document defines the strict communication boundaries for **SatQuery AI** during the Smart India Hackathon (SIH) jury evaluations, pitch presentations, and technical demonstrations.

---

## 1. Supported Claims (Fully Verified by Code & Reproducible Tests)

The following claims are completely backed by working code, automated test suites, and live demonstrations:

* **Controlled Agentic Orchestration**: Autonomous, deterministic intent parsing maps natural language questions to specialist tools (`VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`) without unconstrained LLM loops or hallucinated tool calls.
* **Predefined Tool Registry & Parameter Firewall**: Sub-millisecond parameter sanitation strictly enforces permitted types, numerical ranges, and allowed keys before any specialist model is loaded or executed.
* **Observable Execution Tracing**: Every analysis pass produces a strictly observable 5-stage pipeline trace (`INPUT_VALIDATION` → `ROUTER` → `TOOL_EXECUTION` → `EVIDENCE` → `RESULT_COMPOSITION`) detailing model names, latencies, and output references for auditability.
* **Visual Spatial Evidence Generation**:
  * Coordinate bounding boxes with spatial overlays (`docs/results/grounding_execution_artifact.jpg`).
  * Bi-temporal differential heatmaps and binary change masks (`docs/results/change_detection_execution_artifact.jpg`).
  * Cross-modal 3-panel synergy composites (`docs/results/optical_sar_execution_artifact.jpg`).
* **Four Distinct Multi-Modal Capabilities**:
  1. *Visual Question Answering*: Remote-sensing scene interpretation via `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`.
  2. *Zero-Shot Grounding*: Spatial object detection via `IDEA-Research/grounding-dino-tiny`.
  3. *Bi-Temporal Differencing*: Fast feature extraction via `Siamese-ResNet18-FeatureDifferencer`.
  4. *Optical + Microwave Correlation*: Dual-stream radiometric profiling and Pearson correlation coefficient analysis.
* **GPU-Aware Concurrency Serialization**: Safe execution scheduling via backend `asyncio.Lock` ensures zero CUDA Out-Of-Memory crashes on local 8 GB consumer GPUs.
* **Robust Input Validation & Ambiguity Detection**: Immediate rejection of corrupted images, forbidden extensions, missing required pair assets, or vague requests (`"process this"`) with human-readable diagnostic error codes.

---

## 2. Qualified Claims (Must Include Required Context / Caveats)

The following claims are technically valid but **must always be accompanied by their specific qualification**:

* **Bi-Temporal Change Detection Feasibility**:
  * *Required Qualification*: Evaluated on a **controlled synthetic temporal delta pair** (`sample_satellite_port_t2_synthetic.jpg` derived from Landsat 9 optical baseline) to prove feature differencing mechanics; operational accuracy benchmarks against authentic multi-date satellite passes (e.g. LEVIR-CD) are pending.
* **Optical + SAR Multi-Sensor Ingestion**:
  * *Required Qualification*: Evaluated using a **physically modeled synthetic radar backscatter proxy** (`sample_satellite_port_proxy_sar.png`) simulating specular absorption, corner reflection, and coherent speckle; genuine co-registered spaceborne SAR validation (e.g. Sentinel-1 GRD paired with Sentinel-2 L2A) is pending.
* **Confidence Scores**:
  * *Required Qualification*: Confidence values represent **uncalibrated algorithmic detector or area-stability scores** (e.g. Grounding DINO cross-attention similarity or Siamese background stability ratio); they are **not** statistical classification accuracy or ground-truth probabilities.
* **Single-Scene Resolution Scope**:
  * *Required Qualification*: Visual reasoning operates within a calibrated token budget ($512 \times 28 \times 28$ tokens); gigapixel Earth observation mosaics require spatial tile chipping for sub-pixel object identification.

---

## 3. Unsupported Claims (Strictly Prohibited)

The pitch team, presentation slides, and demonstration scripts must **NEVER** state:

* ❌ **"Our AI is 95% (or 98%) accurate."**
  * *Reason*: Conflates background area stability or integration tests with scientific classification accuracy. No formal benchmark evaluation has been computed yet.
* ❌ **"State-of-the-Art (SOTA) remote sensing accuracy across all Earth Observation domains."**
  * *Reason*: The models are open-source pre-trained specialists adapted for remote sensing; claims of universal SOTA require comprehensive benchmark publication across global benchmarks.
* ❌ **"Validated on authentic spaceborne ISRO / RISAT / Sentinel-1 co-registered SAR imagery."**
  * *Reason*: Optical-SAR evaluation currently uses simulated proxy radar data. While authentic Sentinel-1 imagery is cached as a reference texture, co-registered paired evaluation is pending.
* ❌ **"Pixel-accurate real-world disaster damage assessment ready for deployment."**
  * *Reason*: Change detection has only been verified on a controlled synthetic port infrastructure pair.
* ❌ **"Real-time simultaneous parallel model execution."**
  * *Reason*: The models are serialized on the local 8 GB GPU to respect physical VRAM constraints.
