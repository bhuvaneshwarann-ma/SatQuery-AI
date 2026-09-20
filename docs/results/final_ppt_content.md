# SatQuery AI — Final Presentation Deck (Slide Content)

**Title**: SatQuery AI — Grounded Multimodal Intelligence for Satellite Earth Observation  
**Target Duration**: 10–12 Slides (~6 Minutes Spoken Delivery)  
**Tone**: Rigorous, Technically Grounded, Engineering-First, Scientifically Honest  

---

## Slide 1 — Title & Identity

* **Headline**: **SatQuery AI**
* **Sub-headline**: Grounded Multimodal Intelligence for Earth Observation Analysis
* **Core Value Proposition**: *Turning heterogeneous satellite questions into a controlled, evidence-producing analysis workflow.*
* **Project Metadata**:
  - Smart India Hackathon (SIH) — Space Technology & Earth Observation Domain
  - Team: SatQuery AI Engineering Team
  - Target Architecture: Decoupled Agent Router + Multimodal Specialist Model Registry
  - Hardware Profile: Local Laptop GPU (NVIDIA RTX 3050 / 8 GB VRAM) + Cloud-Ready Architecture

---

## Slide 2 — The Problem: Fragmented Earth Observation Analysis

* **Headline**: Earth Observation Analysis Is Severely Fragmented
* **The Operational Bottleneck**:
  - Analysts must extract actionable insights across completely different task modalities:
    1. **Semantic Understanding**: *"What terrain type is visible in this scene?"* (VQA)
    2. **Spatial Localization**: *"Where are the maritime vessels in this coastal area?"* (Visual Grounding)
    3. **Temporal Differencing**: *"What structural changes occurred between 2021 and 2024?"* (Bi-temporal Change)
    4. **Cross-Modal Correlation**: *"Are these radar reflections genuine ships despite cloud cover?"* (Optical-SAR)
  - Current workflows require analysts to manually switch between disconnected desktop GIS packages, separate vision APIs, and custom Python scripts.
* **The Core Challenge**: It is not just that "satellite AI is hard"—it is that query intents, image formats, spatial coordinates, and analytical models are completely fractured across toolchains.

---

## Slide 3 — Why One Model Is Not Enough

* **Headline**: A Single General-Purpose Model Cannot Solve Earth Observation
* **Technical Incompatibilities Across Modalities**:
  - **Vision-Language Models (VLMs)**: Excel at autoregressive semantic reasoning over single optical images, but lack pixel-level bounding coordinates, cannot ingest SAR complex matrices, and cannot perform exact bi-temporal pixel differencing.
  - **Zero-Shot Object Detectors**: Excel at open-vocabulary spatial localization (bounding boxes), but cannot answer free-form queries or reason about temporal change.
  - **Bi-Temporal Differencers**: Require paired, co-registered image tensors passed through twin feature extraction backbones; single-image architectures cannot compute feature distance.
  - **SAR Cross-Modal Processors**: SAR data represents microwave backscatter (dB, roughness, dielectric properties) requiring radiometric alignment and physical speckle modeling, fundamentally incompatible with RGB color space assumptions.
* **The Engineering Conclusion**: Real-world EO analysis demands a **specialized model registry coordinated by a deterministic, safety-bounded router**—not an unconstrained monolithic chatbot.

---

## Slide 4 — System Architecture: The Controlled Workflow

* **Headline**: SatQuery AI Controlled Agent Architecture
* **The End-to-End Pipeline Flow**:
  ```text
  [ USER REQUEST ] (Natural Language Query + 1 or 2 Satellite Images)
         │
         ▼
  [ INPUT VALIDATION ] (MIME inspection, 15MB limit, PIL raster integrity)
         │
         ▼
  [ AGENT ROUTER ] (Strict Tool Classifier + Schema Firewall)
         │
         ▼
  [ SPECIALIST EXECUTION ] (Sequential GPU Execution Lock: 1 Model at a Time)
         ├── VQA: Domain-Adapted 3B VLM (Autoregressive Semantic Reasoning)
         ├── Grounding: Open-Vocabulary Object Detector (Cross-Attention Localization)
         ├── Change Detection: Unsupervised Siamese Feature Differencing (ResNet-18)
         └── Optical-SAR: Dual-Stream Radiometric Normalization & Spatial Correlation
         │
         ▼
  [ EVIDENCE BUILDER ] (Annotated Overlays, Change Masks, Feature Distance Maps)
         │
         ▼
  [ CONFIDENCE SEMANTICS ] (Task-Specific Semantic Boundaries; Never Inflated)
         │
         ▼
  [ OBSERVABLE EXECUTION TRACE ] (Step-by-step telemetry logged to UI & API)
         │
         ▼
  [ STRUCTURED API RESULT ] (Answer, Visual Evidence Artifacts, Execution Metrics)
  ```
* **Key Architecture Principle**: Router parameters are allowlisted; models cannot execute arbitrary code; all execution steps generate verifiable visual evidence.

---

## Slide 5 — Four Specialist Capabilities

* **Headline**: Four Distinct Modalities, One Unified Interface
* **Capability Matrix**:

| Capability | Model / Engine | Input Assets | Output Artifact | Primary Metric Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **1. Satellite VQA** | Domain-Adapted VLM (3B) | 1 Optical Image + Question | Structured Text Answer | Confidence: `null` (uncalculated; never fabricated) |
| **2. Visual Grounding** | Open-Vocabulary Detector | 1 Optical Image + Target Prompt | Bounding Box Overlay PNG | Score: Uncalibrated detector logit ($37.3\%$) |
| **3. Temporal Change** | Siamese Feature Differencer | 2 Co-registered Images ($T_1, T_2$) | Binary Mask & Heatmap PNG | Margin: Area stability ($97.4\%$ unchanged scene) |
| **4. Optical-SAR** | Dual-Stream Matrix Correlator | 1 Optical + 1 SAR Image | False-Color Composite PNG | Status: Pipeline integrity ($100\%$ grid correlation) |

* **Visual Evidence Anchor**: Every specialist workflow outputs both quantitative data and an inspectable raster overlay artifact.

---

## Slide 6 — Agentic Engineering: Safety, Routing & Telemetry

* **Headline**: Safe Agentic Engineering Under Hardware Constraints
* **Concrete Engineering Protections**:
  - **Immutable Tool Registry**: Router can only choose from 4 registered tools (`vqa`, `visual_grounding`, `change_detection`, `optical_sar_analysis`). No arbitrary shell or code execution.
  - **Parameter Firewall**: Tool parameters are strictly validated via Pydantic schemas. Unrecognized or out-of-bounds parameters are rejected before model invocation.
  - **Hardware-Aware Serialization (`_GPU_EXECUTION_LOCK`)**: 8 GB consumer VRAM cannot hold multiple heavy vision models simultaneously. Our sequential lock guarantees zero CUDA Out-Of-Memory (OOM) crashes across back-to-back queries.
  - **Observable Trace vs. Hidden Thought**: SatQuery AI exposes an **observable execution trace** (input inspection, tool dispatch, runtime latency, VRAM allocation, output serialization)—not fake internal "chain-of-thought" tokens.

---

## Slide 7 — Technical Innovation: Pragmatic System Engineering

* **Headline**: Engineering Innovation Over Buzzwords
* **What We Built**:
  1. **Deterministic Intent Classification**: Hybrid router combining regex-anchored fast-path routing with semantic fallback, guaranteeing $<5\text{ms}$ dispatch without hallucinated tool names.
  2. **Specialist Image Processors**: Native support for single-image optical queries, bi-temporal differential pairs, and optical-SAR multi-sensor arrays.
  3. **Visual Evidence Pipeline**: Dynamic generation of color-coded bounding boxes, binary difference masks, and RGB-SAR fused false-color composites.
  4. **Strict Semantics Firewall**: Enforces that heuristic margins, detector logits, and pipeline status flags are never reported to the user as "classification accuracy".
  5. **Production Regression Hardening**: Fully automated regression test suites verifying 10 failure/security modes, 11 agent orchestration paths, and 8 live API contracts.

---

## Slide 8 — Empirical Evaluation: Honest Zero-Shot Baselines

* **Headline**: Empirical Benchmark Results on Public Datasets
* **Verbatim Technical Stance**:
  > *"Our current benchmark is an honest zero-shot baseline, not a claim of state-of-the-art accuracy. On N=20 public benchmark samples, RSVQA achieved 35% exact match and 0.2525 token F1, while LEVIR-CD achieved 0.0878 macro IoU and 0.1535 macro F1. These results establish a reproducible baseline and show where adaptation is still needed."*

* **Verified Benchmark Scorecard**:

| Benchmark | Test Slices | Primary Metrics | Latency & Reliability | Scientific Finding |
| :--- | :--- | :--- | :--- | :--- |
| **RSVQA-LR**<br>*(Sentinel-2 VQA)* | $N=20$<br>(Seed 42) | Exact Match: **`35.0%`** (7/20)<br>Token F1: **`0.2525`** | Mean: **`50.11s`** (Median: 49.60s)<br>Failures / OOM: **`0 / 20`** | Reliable on presence/booleans; fine-grained numeric counting on 10m pixels requires in-domain tuning. |
| **LEVIR-CD**<br>*(Google Earth CD)* | $N=20$<br>(Seed 42) | Macro IoU: **`0.0878`**<br>Macro F1: **`0.1535`**<br>Precision: **`0.1237`**<br>Recall: **`0.6755`** | Mean: **`27.4 ms`** per pair<br>Failures / OOM: **`0 / 20`** | Unsupervised differencing captures general pixel variance; high recall ($0.6755$) with low precision ($0.1237$) shows clear need for supervised heads. |

* **What Benchmarks Prove**: Reproducibility, pipeline capability, latency feasibility, and identified improvement areas—**NOT SOTA performance**.

---

## Slide 9 — Live System Demonstration

* **Headline**: Live Demonstration of the Four User Journeys
* **Demonstrated Scenarios**:
  - **Demo A — Satellite VQA**:
    - *Image*: Sentinel-2 coastal settlement (`sample_satellite.jpg`)
    - *Query*: *"Describe the primary terrain and visible structures in this scene."*
    - *Result*: Semantic terrain description; confidence explicitly `null`; elapsed timer displayed.
  - **Demo B — Visual Grounding**:
    - *Image*: Port facility (`sample_satellite_port.jpg`)
    - *Query*: *"Detect and localize ships docked along the berths."*
    - *Result*: Bounding box overlays (`[342, 60, 480, 210]`); detector logit $37.3\%$.
  - **Demo C — Temporal Change Detection**:
    - *Images*: Controlled synthetic temporal pair (`port_t1.jpg`, `port_t2_synthetic.jpg`)
    - *Query*: *"Highlight all new construction and land alterations between these two dates."*
    - *Result*: Binary change mask + difference heatmap; area stability margin $97.4\%$.
  - **Demo D — Optical-SAR Fusion**:
    - *Images*: Optical scene + physically modeled proxy SAR (`mauritius_optical.jpg`, `mauritius_sar.jpg`)
    - *Query*: *"Correlate radar backscatter with optical features to verify maritime targets."*
    - *Result*: False-color fused composite; pipeline correlation integrity $100\%$.

---

## Slide 10 — Honest Engineering Boundaries & Disclosures

* **Headline**: Transparent Governance & Known Boundaries
* **Direct Disclosures to Evaluators**:
  - **Requirement #5 Status**: Strictly **`PARTIAL / OPEN`**. We evaluated an open-source domain-adapted VLM checkpoint zero-shot. Custom team-owned fine-tuning and LoRA parameter adaptation on Indian EO data have not yet been performed.
  - **Confidence Values**: Strictly uncalibrated scores. VQA confidence is `null`. Grounding score is an uncalibrated detector logit. Change confidence is an area stability margin ($97.4\%$ unchanged). Optical-SAR confidence is a pipeline integrity check ($1.0$).
  - **Demo Assets**: The bi-temporal change demo uses a controlled synthetic pair to ensure noise-free live execution; the Optical-SAR demo uses physically modeled proxy SAR due to institutional licensing restrictions on sub-meter ISRO data.
  - **Evaluation Scope**: Benchmark subsets ($N=20$, Seed 42) were selected to respect local 8 GB VRAM compute limits (~17 minutes per run).

---

## Slide 11 — Post-Hackathon Technical Roadmap

* **Headline**: Path from Hackathon Prototype to Operational Deployment
* **Prioritized Milestones**:
  1. **Team-Owned Remote-Sensing VLM Adaptation**: Implement QLoRA parameter-efficient fine-tuning on domain-specific datasets (RSVQA / BigEarthNet) using dedicated multi-GPU compute.
  2. **Authentic Co-Registered Optical-SAR Benchmarking**: Ingest verified Sentinel-1/Sentinel-2 and ISRO Cartosat/RISAT data through institutional partnerships.
  3. **Supervised Change Detection Head**: Replace unsupervised ResNet differencing with a supervised ChangeFormer / BIT head to elevate F1 from 0.1535 toward operational thresholds.
  4. **Empirical Confidence Calibration**: Implement temperature scaling and Platt scaling on validation splits to produce calibrated probabilistic confidence intervals.
  5. **Inference Latency Optimization**: Deploy VLM via vLLM with AWQ 4-bit quantization and TensorRT-LLM, cutting VQA generation from ~50s to $<3$s.

---

## Slide 12 — Conclusion: Grounded Multimodal Intelligence

* **Headline**: SatQuery AI: Predictable, Auditable Earth Observation
* **Core Takeaway**:
  - *"SatQuery AI turns heterogeneous satellite questions into a controlled, evidence-producing analysis workflow."*
* **Summary of Delivered System**:
  - **4 Analytical Modalities**: VQA, Grounding, Bi-temporal Change, Optical-SAR.
  - **Safety & Robustness**: Schema-validated parameter firewall, GPU serialization lock, zero crash track record.
  - **Scientific Integrity**: Complete, honest benchmark baselines on public datasets without metric inflation or cherry-picking.
  - **Auditability**: Observable execution telemetry and inspectable visual evidence artifacts on every run.
* **Q&A Readiness**: Live system ready on `localhost:5173` (Frontend) and `localhost:8000` (FastAPI). All logs, manifests, and test suites available for inspection.
