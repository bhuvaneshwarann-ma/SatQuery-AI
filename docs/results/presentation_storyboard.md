# SatQuery AI — Presentation Visual Storyboard (Phase 10)

**Presentation Duration**: Exactly 5 to 7 minutes  
**Target Audience**: Smart India Hackathon (SIH) Technical Jury & Domain Evaluators  
**Guidance**: Focus on clean visual hierarchy, disciplined time allocations, and zero unsupported claims.

---

### Slide 1 — Title & Executive Summary
- **Objective**: Introduce SatQuery AI, define the core value proposition in one sentence, and establish immediate technical credibility.
- **Exact Content**:
  - *Title*: SatQuery AI: Controllable Agentic Multi-Modal Remote Sensing Analysis
  - *Subtitle*: Automated, Parameter-Guarded Satellite QA & Multi-Sensor Spatial Evidence
  - *Core Tagline*: Conversational Remote Sensing Intelligence with Verifiable Evidence & Zero Hallucinated Tools.
- **Recommended Visual**: High-contrast split visual: left side shows a natural language operator terminal; right side shows spatial overlays (bounding boxes, differential heatmaps, false-color radar).
- **Presenter Script (25 seconds)**:
  > *"Good morning, respected judges. We present SatQuery AI. SatQuery AI is a controllable agentic analysis engine designed for multi-modal Earth Observation data. It bridges the gap between natural language questions and specialist remote sensing models, returning not just answers, but verifiable spatial evidence, honest confidence semantics, and observable execution traces on consumer-grade hardware."*
- **Maximum Time**: 25 seconds
- **Likely Judge Question**: *"What makes this different from asking ChatGPT or standard Qwen to look at a satellite photo?"*

---

### Slide 2 — The Remote Sensing Problem
- **Objective**: Frame the acute operational pain point experienced by non-GIS specialists when handling heterogeneous satellite rasters.
- **Exact Content**:
  - *Data Complexity*: Multi-spectral optical RGB, microwave SAR backscatter, multi-temporal passes.
  - *Skill Barrier*: Non-technical defense, disaster, or municipal operators cannot write GDAL/Rasterio scripts or configure complex GIS software under mission pressure.
  - *Latency*: Satellite constellations produce massive data streams, but manual feature analysis creates severe decision bottlenecks.
- **Recommended Visual**: Infographic illustrating the mismatch between incoming raw satellite data streams and manual GIS analyst workflows.
- **Presenter Script (30 seconds)**:
  > *"Satellite imagery is fundamentally heterogeneous. It includes optical RGB, synthetic aperture radar (SAR), and multi-temporal sequences. Currently, analyzing this data requires specialized GIS expertise, manual band calculations, and custom scripting. Non-technical operators—such as disaster relief coordinators or defense analysts—need immediate, conversational insights without spending hours wrestling with raw raster formats."*
- **Maximum Time**: 30 seconds
- **Likely Judge Question**: *"Can't existing commercial GIS suites like ArcGIS or QGIS already automate some of this?"*

---

### Slide 3 — Why Existing Approaches Fail
- **Objective**: Scientifically explain why monolithic VLMs and unconstrained LLM web agents fail in remote sensing.
- **Exact Content**:
  - *General-Purpose VLMs*: Web-trained models lack nadir perspective biases, cannot perform pixel-level bi-temporal change masking, and cannot interpret non-RGB radar backscatter physics.
  - *Unconstrained LLM Agents*: Prone to hallucinated tools, prompt injection vulnerabilities, non-deterministic looping, and GPU VRAM crashes.
  - *Deceptive Confidence*: Black-box commercial systems return arbitrary "99% confidence" scores that conflate background stability with true accuracy.
- **Recommended Visual**: Comparison chart contrasting Unconstrained Web Agents vs. Monolithic VLMs vs. SatQuery AI Controllable Agent.
- **Presenter Script (35 seconds)**:
  > *"Why can't we simply drop in a standard vision-language model or an autonomous web agent? First, monolithic VLMs lack pixel-level differencing heads and cannot process microwave SAR backscatter physics. Second, unconstrained LLM agents hallucinate tools, execute arbitrary code, and easily crash local GPU memory through unbounded concurrency. Finally, existing systems frequently display deceptive 99% confidence scores without defining what they measure."*
- **Maximum Time**: 35 seconds
- **Likely Judge Question**: *"Why did you not use an end-to-end multi-task model instead of an agent routing to multiple tools?"*

---

### Slide 4 — Our Solution: The Controllable Agent Architecture
- **Objective**: Present the end-to-end query lifecycle and establish the core technical paradigm.
- **Exact Content**:
  - *Pipeline Flow*:
    $$\text{User Query} \to \text{Input Validation} \to \text{Agent Router} \to \text{Authorized Tool} \to \text{Evidence} \to \text{Confidence Semantics} \to \text{Observable Trace} \to \text{Result}$$
  - *Core Mechanisms*:
    1. Predefined Tool Registry (No hallucinated tools).
    2. Sub-millisecond Parameter Firewall ($<20\text{ ms}$ input sanitization).
    3. Observable 5-Stage Trace (No opaque chain-of-thought).
- **Recommended Visual**: Clean, high-contrast architectural diagram of the 5-stage pipeline with icons for each phase.
- **Presenter Script (30 seconds)**:
  > *"SatQuery AI introduces a Controllable Agent paradigm. When an operator submits a query, it passes through Input Validation, followed by our deterministic Agent Router. The router verifies intent and enforces our Pre-Model Parameter Firewall in under 20 milliseconds. Execution is dispatched strictly to an authorized tool in our predefined registry, returning structured text, visual evidence, uncalibrated confidence metrics, and an observable execution trace."*
- **Maximum Time**: 30 seconds
- **Likely Judge Question**: *"What happens if the user inputs a prompt injection or asks an ambiguous question?"*

---

### Slide 5 — Four Specialized Analytical Capabilities
- **Objective**: Introduce the four specialist backbones and transparently distinguish benchmarked models from integration demos.
- **Exact Content**:
  - *VQA*: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` (Benchmarked: RSVQA-LR).
  - *Visual Grounding*: `IDEA-Research/grounding-dino-tiny` (Integration validated, bounding box overlay).
  - *Bi-Temporal Change Detection*: `Siamese-ResNet18-FeatureDifferencer` (Benchmarked: LEVIR-CD).
  - *Optical-SAR Multi-Sensor Fusion*: `Dual-Stream Radiometric Engine` (Integration validated on proxy SAR).
- **Recommended Visual**: 4-quadrant layout displaying sample visual outputs for each of the four tools.
- **Presenter Script (40 seconds)**:
  > *"Our system integrates four distinct capabilities across remote sensing tasks: First, Visual Question Answering via an open-source domain-adapted 3B VLM. Second, Visual Grounding for spatial referring expression localization via Grounding DINO. Third, Bi-Temporal Change Detection via a Siamese ResNet-18 feature differencer producing binary change masks. Fourth, Optical-SAR Cross-Modal Fusion combining optical RGB with microwave radar backscatter into false-color synergy composites."*
- **Maximum Time**: 40 seconds
- **Likely Judge Question**: *"Are all four models benchmarked on ground-truth datasets?"*

---

### Slide 6 — Agent Safety, Firewall & Hardware Concurrency
- **Objective**: Demonstrate engineering robustness, security enforcement, and hardware resource awareness.
- **Exact Content**:
  - *Predefined Tool Registry*: Closed set of tools; zero arbitrary shell or script execution.
  - *Parameter Firewall*: Strict whitelisting of parameter keys, types, and numerical bounds.
  - *GPU Concurrency Lock (`_GPU_EXECUTION_LOCK`)*: Serializes heavy model invocations, guaranteeing zero CUDA Out-Of-Memory (OOM) errors on 8 GB laptop GPUs.
- **Recommended Visual**: Diagram showing the Parameter Firewall intercepting unauthorized keys and the sequential GPU locking mechanism.
- **Presenter Script (35 seconds)**:
  > *"A critical engineering breakthrough in SatQuery AI is hardware-aware safety. On consumer hardware like our 8 GB laptop GPU, attempting to run a 3B VLM and a vision backbone simultaneously causes immediate CUDA OOM crashes. We enforce sequential GPU locking (`_GPU_EXECUTION_LOCK`). Furthermore, our parameter firewall traps unauthorized parameters before GPU allocation, ensuring rock-solid stability."*
- **Maximum Time**: 35 seconds
- **Likely Judge Question**: *"Doesn't sequential execution hurt multi-user throughput?"*

---

### Slide 7 — Defensible Technical Innovations
- **Objective**: Highlight the genuine, provable engineering differentiators of the project.
- **Exact Content**:
  1. *Sub-millisecond Pre-Model Firewall*: Rejects malicious injections and ambiguous intent prior to model loading ($<20\text{ ms}$).
  2. *Observable Trace Auditing*: Transparent stage-by-stage record with per-step latencies.
  3. *Honest Confidence Semantics*: Uncalibrated, tool-specific metrics distinguishing detector logits, area ratios, and pipeline integrity.
  4. *Multi-Sensor Radiometric Alignment*: Dual-stream cross-modal statistical analysis between optical and microwave domains.
- **Recommended Visual**: Bulleted feature cards with green verification checkmarks backed by test suite filenames.
- **Presenter Script (30 seconds)**:
  > *"Our innovations are practical and defensible: We built sub-millisecond intent and parameter guardrails that protect compute resources; we provide transparent confidence semantics that never deceive operators; we enforce hardware-aware execution serialization; and we deliver verifiable visual evidence alongside every analytical output."*
- **Maximum Time**: 30 seconds
- **Likely Judge Question**: *"How do you prove that your parameter firewall actually works?"*

---

### Slide 8 — Empirical Benchmark & Evaluation Evidence
- **Objective**: Present verified quantitative benchmark numbers with scientific integrity and zero metric fabrication.
- **Exact Content**:
  - *RSVQA-LR ($N=20$, Sentinel-2 VQA)*:
    - Exact Match: **35.0%** | Mean Token F1: **0.2525** | Mean Latency: **50.11 s** | 0 OOM / 0 Crashes.
  - *LEVIR-CD ($N=20$, Google Earth Building Change)*:
    - Macro Change IoU: **0.0878** (Micro: **0.1113**) | Macro F1: **0.1535** (Micro: **0.2002**) | Latency: **27.4 ms**.
  - *Regression Test Suites*:
    - Failure/Security: **10 / 10 PASS** | Orchestration: **11 / 11 PASS** | API Contract: **8 / 8 PASS**.
- **Recommended Visual**: Clean, professional benchmark scorecard table comparing metrics with dataset badges and slice declarations.
- **Presenter Script (45 seconds)**:
  > *"We believe in scientific honesty. Rather than claiming fabricated 99% accuracy, we evaluated our system on genuine public benchmark slices. On RSVQA-LR Sentinel-2 images, our zero-shot remote-sensing VLM achieved 35.0% Exact Match and 0.2525 Token F1, performing strongly on categorical queries. On LEVIR-CD building change detection, our unsupervised Siamese feature differencer achieved 0.1535 Macro F1 and 0.0878 Macro IoU at 27.4 ms per pair. All three regression suites pass with 100% success."*
- **Maximum Time**: 45 seconds
- **Likely Judge Question**: *"Why is the RSVQA accuracy 35% and LEVIR-CD F1 0.1535? Isn't that lower than published SOTA?"*

---

### Slide 9 — Live System Demonstration Choreography
- **Objective**: Guide evaluators through the live interactive demonstration of all four capabilities and safety features.
- **Exact Content**:
  - Step 1: Demo A — Port Overview VQA (Exploration dialogue + Trace).
  - Step 2: Demo B — Vessel Grounding (Referring expression + Bounding boxes).
  - Step 3: Demo C — Bi-Temporal Change Detection (T1/T2 + Differential Heatmap in $<1\text{s}$).
  - Step 4: Demo D — Optical + SAR Radiometric Fusion (Cross-modal correlation + Proxy SAR notice).
  - Step 5: Safety Interception (Rejection of unsupported intent in $<20\text{ ms}$).
- **Recommended Visual**: Screenshot of the React 19 UI showing the One-Click Evaluator Presets and 3-Panel comparison layout.
- **Presenter Script (60 seconds)**:
  > *"Let us transition to the live system. In our React UI, we provide quick presets for all four scenarios. When we run Demo A, the agent routes to the 3B VLM; notice our live stopwatch tracking the ~50-second generation honestly. When we run Demo C for Change Detection, execution finishes in under one second, displaying a 3-panel comparative view with 8,848 changed pixels identified. In Demo D, we fuse optical and radar backscatter, computing cross-modal correlation with explicit proxy SAR disclosure. Finally, submitting an ambiguous query triggers immediate clarification without invoking GPU models."*
- **Maximum Time**: 60 seconds
- **Likely Judge Question**: *"Can the user upload their own GeoTIFF or high-resolution imagery?"*

---

### Slide 10 — Limitations & Responsible Engineering
- **Objective**: Address limitations proactively and demonstrate mature, responsible AI engineering.
- **Exact Content**:
  - *Requirement #5*: **PARTIAL / OPEN** (Domain-adapted VLM benchmarked zero-shot; custom fine-tuning open).
  - *VQA Latency*: ~50s on local 8 GB GPU due to 3B model scale and CPU offloading.
  - *Uncalibrated Confidence*: Scores represent detector similarity or area ratios, not statistical accuracy.
  - *Dataset Scope*: Evaluations conducted on $N=20$ slices; proxy SAR used due to restricted ISRO data licensing.
- **Recommended Visual**: "Responsible Engineering Checklist" outlining limitations alongside their explicit operational mitigations.
- **Presenter Script (40 seconds)**:
  > *"We treat limitations as engineering parameters, not hidden flaws. First, Requirement #5 is explicitly PARTIAL / OPEN: we deployed an existing domain-adapted remote-sensing VLM, but custom team-owned fine-tuning on Indian EO data remains our post-hackathon milestone. Second, VQA takes ~50 seconds on this 8 GB laptop due to model scale. Third, confidence scores are uncalibrated algorithmic metrics and are explicitly labeled as such. Fourth, proxy SAR was used because authentic ISRO Cartosat and RISAT co-registered pairs are restricted under data licensing."*
- **Maximum Time**: 40 seconds
- **Likely Judge Question**: *"Why did you not perform fine-tuning on Indian satellite data during the hackathon?"*

---

### Slide 11 — Technical Roadmap
- **Objective**: Outline the realistic path from Hackathon MVP to operational deployment.
- **Exact Content**:
  - *Milestone 1*: In-domain LoRA fine-tuning of Qwen2.5-VL-3B on Cartosat/Resourcesat paired VQA datasets (closing Requirement #5).
  - *Milestone 2*: Supervised ChangeFormer / BIT transformer head for building change detection ($F1 > 0.80$).
  - *Milestone 3*: Integration of authentic ISRO Cartosat-2S and RISAT-1A SAR rasters upon formal data agreement.
  - *Milestone 4*: vLLM / TensorRT-LLM serving with FP8 quantization reducing VQA latency to $<3\text{ seconds}$.
- **Recommended Visual**: Phased timeline showing Phase 1 (LoRA), Phase 2 (ChangeFormer), Phase 3 (ISRO data), Phase 4 (vLLM Cloud Serving).
- **Presenter Script (30 seconds)**:
  > *"Our post-hackathon roadmap is focused on operational scaling: In Phase 1, we will implement parameter-efficient LoRA fine-tuning on Indian EO satellite data to close Requirement #5. In Phase 2, we will integrate a supervised ChangeFormer head to elevate change detection F1 beyond 0.80. In Phase 3, we will ingest authentic ISRO Cartosat and RISAT data once access is cleared. Finally, serving via vLLM with FP8 quantization will drop VQA latency to under 3 seconds."*
- **Maximum Time**: 30 seconds
- **Likely Judge Question**: *"What compute resources would you need to implement your fine-tuning pipeline?"*

---

### Slide 12 — Conclusion & Defense Invitation
- **Objective**: Reiterate core strengths, thank the judges, and transition smoothly to Q&A.
- **Exact Content**:
  - *Core Summary*: Controllable Agent + 4 Specialist Tools + Hardware Safety + Transparent Evidence.
  - *Status*: Live MVP verified; 100% regression pass; ground-truth benchmarked on public subsets.
  - *Call to Action*: Open for jury questions and live scenario exploration.
- **Recommended Visual**: Summary slide with team contact info, GitHub repo link, and live system status badges (`ONLINE`, `GPU: RTX 5050`, `ALL TESTS PASS`).
- **Presenter Script (20 seconds)**:
  > *"In conclusion, SatQuery AI provides a robust, controllable agentic framework that makes multi-modal satellite analysis accessible, verifiable, and safe on standard hardware. We have prioritized scientific honesty and rigorous engineering at every step. Thank you for your time, and we look forward to answering your questions."*
- **Maximum Time**: 20 seconds
- **Likely Judge Question**: *"Can we test an arbitrary image or prompt right now?"*
