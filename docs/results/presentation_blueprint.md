# SatQuery AI — Presentation Architecture Blueprint (Phase 10)

**Target Competition**: Smart India Hackathon (SIH) — Multi-Modal Remote Sensing & Satellite Analysis  
**Format**: 10–12 Slides Executive & Technical Evaluation Pitch  
**Governing Authority**: Strictly aligned with [`demo_claims_matrix.md`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/demo_claims_matrix.md) and empirical benchmark outputs.

---

## Slide 1 — Title & Executive Value Proposition

* **Slide Title**: SatQuery AI — Controllable Agentic Multi-Modal Remote Sensing Analysis
* **Subtitle**: Automated, Parameter-Guarded Satellite Question Answering & Multi-Sensor Spatial Evidence
* **Key Visual**: Dual-panel graphic showing a non-technical natural language query on the left, passing through an agentic router, and producing spatial bounding boxes, bi-temporal heatmaps, and false-color radar composites on the right.
* **Core Value Statement**: *"Bridging the gap between natural language operational queries and specialist Earth Observation models through controlled, observable agentic orchestration."*

---

## Slide 2 — The Operational Remote Sensing Problem

* **Slide Title**: The Remote Sensing Analysis Bottleneck
* **Operational Challenges**:
  1. **Heterogeneous Sensor Formats**: Analysts must interpret multi-spectral optical RGB, microwave SAR radar backscatter, and multi-temporal satellite passes.
  2. **High Domain Specialization**: Non-technical defense, disaster, or civil operators cannot operate complex GIS software or write Python raster workflows under time pressure.
  3. **Data Overload vs. Human Bandwidth**: Satellite constellations downlink gigabytes of imagery hourly, but manual feature identification creates severe decision latency.
* **Key Takeaway**: Non-specialist operators need a conversational interface that delivers transparent, verifiable evidence without requiring manual GIS pipeline engineering.

---

## Slide 3 — Why Existing AI Approaches Are Insufficient

* **Slide Title**: Limitations of General-Purpose LLMs & Monolithic VLMs
* **Architectural Shortcomings**:
  1. **Monolithic General-Purpose VLMs**:
     - Generic vision-language models (e.g., standard Qwen/LLaVA) are trained primarily on consumer web photos; they lack remote-sensing inductive biases (e.g., top-down nadir perspective, non-RGB microwave radar backscatter).
     - Standard VLMs cannot compute exact pixel-level bi-temporal change masks or calculate SAR cross-correlation.
  2. **Unconstrained Autonomous LLM Agents**:
     - Web-style autonomous agents loop open-endedly, hallucinate tools, execute arbitrary code, and crash GPU VRAM via unbounded concurrency.
  3. **Black-Box "Accuracy" Illusions**:
     - Commercial black boxes return scalar percentages without semantic definition, leading operators to conflate detector heuristics with factual certainty.

---

## Slide 4 — Our Solution: The Controllable Agent Paradigm

* **Slide Title**: SatQuery AI Architecture — Evidence-First Multi-Modal Pipeline
* **Visual Pipeline**:
  $$\text{User Query} \longrightarrow \text{Input Validation} \longrightarrow \text{Agent Router} \longrightarrow \text{Authorized Specialist Tool} \longrightarrow \text{Spatial Evidence} \longrightarrow \text{Confidence Semantics} \longrightarrow \text{Observable Trace} \longrightarrow \text{Unified Result}$$
* **Core Principles**:
  - **Deterministic Action Space**: Bounded strictly within an allowlisted Tool Registry (`VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`).
  - **Pre-Model Parameter Firewall**: Sanitizes inputs in $<20\text{ ms}$ before invoking heavy GPU neural networks.
  - **Observable Execution Audit**: Every step generates an immutable execution record with per-stage latency telemetry.

---

## Slide 5 — Four Specialist Analytical Capabilities

* **Slide Title**: Modular Specialist Engines Across Remote Sensing Tasks
* **Capability Matrix**:

| Capability | Model / Engine Checkpoint | Validation Level | Output Spatial Evidence | Documented Limitation |
| :--- | :--- | :--- | :--- | :--- |
| **1. Visual Question Answering (VQA)** | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | **Ground-Truth Benchmarked** (RSVQA-LR $N=20$) | Spatial metadata & structured natural dialogue | Latency ~50s on 8 GB GPU; granular counting challenging |
| **2. Visual Grounding** | `IDEA-Research/grounding-dino-tiny` | **Integration Validated** (Contract & Box overlay) | Annotated bounding box visual overlay (`.jpg`) | Cross-attention score; NOT calibrated localization IoU |
| **3. Bi-Temporal Change Detection** | `Siamese-ResNet18-FeatureDifferencer` | **Ground-Truth Benchmarked** (LEVIR-CD $N=20$) | 3-panel differential heatmap composite (`.jpg`) | Unsupervised feature differencing; not in-domain trained head |
| **4. Optical-SAR Multi-Sensor Fusion** | `Dual-Stream Radiometric Correlation Engine` | **Integration Validated** (Proxy SAR evaluated) | 3-panel radiometric synergy composite (`.jpg`) | Evaluated on proxy SAR; authentic ISRO/SAC data restricted |

---

## Slide 6 — Agentic System Architecture & Safety Control

* **Slide Title**: Safety-First Agent Orchestration: Protecting Memory & Execution
* **Architecture Diagram**:
  - **React 19 Dark UI**: Client layer; handles multipart asset bundling and live telemetry display.
  - **FastAPI Backend Gateway**: Pydantic v2 input validation, CORS, error interceptors.
  - **Agent Router**: Sub-millisecond intent extraction mapping verbs and asset types to registered tools.
  - **Parameter Firewall**: Type and range validation preventing injection attacks before GPU allocation.
  - **Hardware Serialization Lock (`_GPU_EXECUTION_LOCK`)**: Enforces single-model sequential execution, guaranteeing zero CUDA Out-Of-Memory (OOM) crashes on consumer 8 GB laptop GPUs.

---

## Slide 7 — Defensible Technical Innovations

* **Slide Title**: Defensible Technical Differentiators
* **Core Innovations**:
  1. **Pre-Model Intent & Parameter Guardrails**: Sub-millisecond rejection of ambiguous or unpermitted inputs, preventing GPU memory exhaustion and denial-of-service.
  2. **Transparent Confidence Semantics**: Complete elimination of deceptive accuracy claims; tool-by-tool separation between detector logits, area margins, and pipeline integrity.
  3. **Hardware-Aware Concurrency Scheduling**: Dynamic execution serialization enabling full 3B VLM reasoning alongside computer vision models within consumer laptop VRAM budgets (~8 GB).
  4. **Multi-Modal Evidence Generation**: Outputs human-verifiable visual spatial artifacts alongside natural language text answers for immediate operational auditability.

---

## Slide 8 — Empirical Benchmark & Evaluation Evidence

* **Slide Title**: Measured Benchmark Results on Public Datasets (Seed 42)
* **Performance Overview**:

| Benchmark Corpus | Task Modality | Evaluated Slice | Primary Metric | Secondary Metric | Mean Sample Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RSVQA-LR** (Sentinel-2) | Visual Question Answering | Exactly $N=20$ scene pairs | **35.0% Exact Match** (7 / 20) | **0.2525 Token F1** | **50.11 s** (0 OOM / 0 crashes) |
| **LEVIR-CD** (Google Earth) | Building Change Detection | Exactly $N=20$ temporal pairs | **0.0878 Macro IoU** (0.1113 Micro) | **0.1535 Macro F1** (0.2002 Micro) | **27.4 ms** (Sub-second batch) |

* **Automated System Regressions**:
  - Failure & Security Robustness Suite: **10 / 10 PASS (100%)**
  - Agent Orchestration Integration Suite: **11 / 11 PASS (100%)**
  - Live FastAPI API Contract Suite: **8 / 8 PASS (100%)**
* *Boundary Note: Results reflect small reproducible slices ($N=20$) establishing honest baselines without fine-tuning; no claims of universal SOTA or full-dataset dominance.*

---

## Slide 9 — Live System Demonstration Choreography

* **Slide Title**: Live System Demonstration Sequence
* **Choreographed Evaluator Flow**:
  1. **Demo A (Single-Image VQA)**: Upload optical harbor scene $\to$ ask facility query $\to$ observe live elapsed stopwatch $\to$ verify natural language answer, null confidence semantics, and 5-stage execution trace.
  2. **Demo B (Visual Grounding)**: Referring expression query (*"Locate the ships"*) $\to$ display bounding box overlay and uncalibrated detector score ($37.3\%$).
  3. **Demo C (Bi-Temporal Change Detection)**: Upload T1 and T2 $\to$ sub-second execution $\to$ display 3-panel comparative layout and area stability margin ($97.4\%$).
  4. **Demo D (Optical-SAR Multi-Sensor Fusion)**: Upload Optical + SAR $\to$ cross-modal correlation ($r=0.574$) $\to$ display false-color synergy composite and proxy SAR classification.
  5. **Safety Test (Firewall & Ambiguity)**: Submit *"calculate orbital trajectory"* $\to$ immediate pre-model rejection (`NEEDS_CLARIFICATION`) in $<20\text{ ms}$.

---

## Slide 10 — Scientific Limitations & Responsible Engineering

* **Slide Title**: Transparent Engineering Boundaries & Limitations
* **Explicit Disclosures**:
  1. **Requirement #5 (PARTIAL / OPEN)**: Deployed and benchmarked an open-source remote-sensing VLM checkpoint zero-shot; custom team-owned fine-tuning on Indian EO data was not performed and remains an open roadmap item.
  2. **Hardware & VQA Latency**: Autoregressive decoding of the 3B VLM takes ~50s on local 8 GB laptop GPUs due to CPU offloading and memory bandwidth constraints.
  3. **Uncalibrated Confidence**: Output confidence metrics represent algorithmic artifacts (detector cross-attention logits, area margins, pipeline integrity) and must never be interpreted as statistical classification accuracy.
  4. **Benchmark Scale**: Evaluated on $N=20$ public subsets (Seed 42) to operate within local compute limits.
  5. **Proxy SAR Ingestion**: Tested using a physically modeled radar backscatter proxy; authentic spaceborne Cartosat-2S and RISAT-1A pairs require restricted ISRO/SAC data licensing.

---

## Slide 11 — Roadmap & Future Enhancements

* **Slide Title**: Technical Roadmap: Scaling Beyond Hackathon MVP
* **Phased Milestones**:
  - **Phase 1: In-Domain LoRA Fine-Tuning (Requirement #5)**: Fine-tune Qwen2.5-VL-3B on Indian satellite imagery (Cartosat/Resourcesat paired VQA datasets) to enhance numeric counting and regional land-use understanding.
  - **Phase 2: Supervised Change Detection Transformer**: Integrate an in-domain fine-tuned ChangeFormer / BIT head to advance change detection F1 beyond unsupervised feature differencing.
  - **Phase 3: Formal ISRO/SAC Data Access**: Ingest authentic co-registered Cartosat-2S optical and RISAT-1A SAR imagery once institutional licensing is granted.
  - **Phase 4: High-Throughput Cloud Serving**: Deploy via vLLM with FP8 quantization and Celery worker pools, reducing VQA latency to $<3\text{ seconds}$.

---

## Slide 12 — Conclusion & Defense Invitation

* **Slide Title**: SatQuery AI — Controllable, Honest, and Observable
* **Key Takeaways**:
  - Real, functioning agentic architecture running live on consumer hardware.
  - Pre-model safety firewall, observable trace auditing, and verifiable spatial evidence.
  - Complete scientific transparency: exact measured benchmark numbers and honest limitation boundaries.
* **Closing Prompt**: *"Thank you. We welcome your technical questions."*
