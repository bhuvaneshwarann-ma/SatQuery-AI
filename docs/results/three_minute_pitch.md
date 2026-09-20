# SatQuery AI — 3-Minute Emergency Pitch (Phase 10)

**Target Delivery Time**: Exactly 3 Minutes (180 Seconds)  
**Tone**: Confident, technically precise, scientifically honest, and authoritative.  
**Governing Rule**: Use only claims fully supported by the authoritative evidence in [`demo_claims_matrix.md`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/demo_claims_matrix.md).

---

### [0:00 – 0:20] The Hook (20 Seconds)

> *"Respected Evaluators, when natural disasters strike or border security incidents occur, satellite constellations downlink gigabytes of Earth Observation imagery every hour. 
> Yet decision-makers—such as relief coordinators or defense commanders—cannot extract critical answers because current tools demand specialized GIS software, manual band calculations, and custom Python scripting. 
> We built **SatQuery AI**: a controllable agentic engine that turns conversational English queries into verifiable multi-modal satellite intelligence on standard hardware."*

---

### [0:20 – 0:50] The Problem & Why Existing AI Fails (30 Seconds)

> *"Why can't we simply ask a general-purpose LLM or standard vision model? 
> First, general VLMs are trained on web photos; they lack remote-sensing nadir perspective biases, cannot compute pixel-level bi-temporal change masks, and cannot parse non-RGB microwave radar backscatter physics. 
> Second, unconstrained autonomous web agents hallucinate tools, execute arbitrary code, and easily crash local GPU memory through unbounded concurrency. 
> Third, existing black-box prototypes return deceptive '99% confidence' numbers without defining what they measure."*

---

### [0:50 – 1:20] The Solution & The Four Specialist Capabilities (30 Seconds)

> *"SatQuery AI introduces a **Controllable Agent Paradigm**. Rather than forcing one monolithic model to do everything, our system routes queries across four specialized, allowlisted remote-sensing engines:
> 
> 1. **Visual Question Answering**: Natural language scene interpretation using `remote-sensing-Qwen2.5-VL-3B`.
> 2. **Visual Grounding**: Open-vocabulary spatial object localization using `Grounding DINO Tiny`.
> 3. **Bi-Temporal Change Detection**: Sub-second differential change mapping using `Siamese ResNet-18`.
> 4. **Optical-SAR Cross-Modal Fusion**: Dual-stream radiometric correlation fusing optical RGB and microwave radar backscatter.
> 
> Every response delivers not just text, but visual spatial overlays, honest confidence semantics, and an observable audit trace."*

---

### [1:20 – 1:50] Architecture & The Agentic Mechanism (30 Seconds)

> *"Under the hood, our architecture enforces safety before execution. 
> When a query arrives at our FastAPI backend, it passes through **Input Validation**, verifying raster integrity in 4 milliseconds. 
> Next, our deterministic **Agent Router** inspects intent and enforces our **Pre-Model Parameter Firewall** in under 20 milliseconds, rejecting unauthorized parameters before invoking heavy models. 
> To guarantee zero CUDA Out-Of-Memory crashes on our 8 GB laptop GPU, we enforce sequential hardware locking (`_GPU_EXECUTION_LOCK`). The result is a 100% crash-free, predictable execution pipeline."*

---

### [1:50 – 2:30] Live Demonstration & Visual Evidence (40 Seconds)

> *"In our live React interface, an evaluator can test all four workflows in one click:
> 
> - Running **Change Detection** completes in under one second, rendering a 3-panel comparative layout with 8,848 changed pixels highlighted and an area stability margin of 97.4%.
> - Running **Optical-SAR Fusion** ingests dual-sensor rasters, calculating a Pearson correlation of 0.574 and displaying a false-color radiometric synergy map.
> - Running **Visual Grounding** localizes maritime vessels with bounding boxes and an uncalibrated detector logit of 37.3%.
> - Running **VQA** provides in-depth port infrastructure dialogue with full 5-stage execution trace auditing.
> - And if an operator enters an ambiguous prompt like 'calculate trajectory', the router returns immediate clarification in 6 milliseconds without touching the GPU."*

---

### [2:30 – 2:50] Evaluation Evidence & Scientific Honesty (20 Seconds)

> *"We stand behind verified, reproducible public benchmark evidence (Seed 42):
> 
> - On **RSVQA-LR** Sentinel-2 imagery, our zero-shot VLM achieved **35.0% Exact Match** and **0.2525 Token F1** with zero OOM crashes.
> - On **LEVIR-CD** building change detection, our Siamese feature differencer achieved **0.1535 Macro F1** and **0.0878 Macro IoU** at **27.4 ms** per pair.
> - Our automated regression suites pass **100%** across 10 failure tests, 11 orchestration tests, and 8 live API contract tests.
> - And we are completely transparent: **Requirement #5 (custom fine-tuning on Indian EO data) explicitly remains PARTIAL / OPEN** as our post-hackathon milestone."*

---

### [2:50 – 3:00] Closing (10 Seconds)

> *"SatQuery AI proves that multi-modal satellite intelligence can be conversational, observable, and hardware-safe without sacrificing scientific honesty. 
> Thank you, and we look forward to your questions."*
