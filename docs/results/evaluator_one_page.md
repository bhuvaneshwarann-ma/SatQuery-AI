# SatQuery AI — Executive Evaluator Brief

**System**: SatQuery AI (Smart India Hackathon Technical Evidence Package)  
**Target Hardware**: NVIDIA GeForce RTX 5050 Laptop GPU (~8 GB VRAM)  
**Status**: Technical evidence package is evaluator-ready, with Requirement #5 explicitly remaining PARTIAL / OPEN

---

### 1. What is SatQuery AI?
**SatQuery AI** is an agentic Earth Observation (EO) analysis engine. It allows non-technical users, defense analysts, and disaster management personnel to ask questions in plain English about satellite imagery, automatically routing queries to specialist vision-language and computer vision models to generate structured answers, visual evidence, and transparent execution traces.

### 2. Why is it Different?
Traditional remote sensing pipelines require manual tool selection, specialized GIS software, or unconstrained LLM agents that hallucinate tools and execute arbitrary code. **SatQuery AI is built on a "Controllable Agent" paradigm**:
- **Zero Hallucinated Tools**: Operates strictly within a predefined, allowlisted Tool Registry.
- **Pre-Model Parameter Firewall**: Sanitizes all input parameters in $<20\text{ ms}$, rejecting injections before invoking GPU models.
- **Hardware-Aware Concurrency**: Uses serial execution locking (`_GPU_EXECUTION_LOCK`) to guarantee zero CUDA Out-Of-Memory (OOM) crashes on 8 GB consumer laptop GPUs.

### 3. How Does the Agent Work?
The query lifecycle follows an authoritative, single-direction pipeline:
1. **User / React UI**: Submits image(s) and natural language query to FastAPI `/api/analyze`.
2. **Input Validation**: Verifies raster integrity, file types, and asset existence.
3. **Agent Router**: Parses analytical intent and verifies whitelisted parameters against the Predefined Tool Registry.
4. **Specialist Execution**: Dispatches to the selected model backbone under serialized GPU locking.
5. **Evidence & Trace**: Compiles visual spatial artifacts, uncalibrated algorithmic confidence, and an observable 5-stage execution trace into a unified response envelope.

### 4. What Four Tasks Can it Perform?
1. **Visual Question Answering (VQA)**: Remote-sensing scene interpretation via `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`.
2. **Visual Grounding**: Object localization from referring expressions via `IDEA-Research/grounding-dino-tiny`.
3. **Bi-Temporal Change Detection**: Automated building/land change detection via `Siamese-ResNet18-FeatureDifferencer`.
4. **Optical-SAR Multi-Sensor Fusion**: Dual-stream radiometric correlation fusing optical RGB and microwave radar backscatter.

### 5. What Evidence Do We Have?
- **Automated Regression Suites**: 100% PASS across 10 Failure/Security Tests (`test_failure_cases.py`), 11 Orchestration Tests (`test_agent_orchestration.py`), and 8 Live API Contract Tests (`test_api_contract.py`).
- **Visual Spatial Artifacts**: Actual rendered JPEG overlays in `docs/results/` for Grounding (`grounding_execution_artifact.jpg`), Change Detection (`change_detection_execution_artifact.jpg`), and Optical-SAR (`optical_sar_execution_artifact.jpg`).
- **Auditability**: Observable execution trace with per-stage latencies returned in every response envelope.

### 6. What Are the Measured Benchmark Results?
Evaluated on genuine public benchmark slices (Seed 42) with zero metric fabrication:
- **RSVQA-LR ($N=20$, Sentinel-2 VQA)**:
  - **Exact Match Accuracy**: **35.0%** (7 / 20 canonical matches) | **Mean Token F1**: **0.2525**
  - **Mean Latency**: **50.11 s** per sample (Autoregressive 3B VLM decoding) | **Failures / OOM**: **0**
- **LEVIR-CD ($N=20$, Google Earth Change Detection)**:
  - **Change IoU (Macro)**: **0.0878** (Micro IoU: **0.1113**) | **F1-Score (Macro)**: **0.1535** (Micro F1: **0.2002**)
  - **Precision (Macro)**: **0.1237** | **Recall (Macro)**: **0.6755** | **Mean Latency**: **27.4 ms**

### 7. What Are the Current Limitations?
1. **Benchmark Scale**: Quantitative evaluations were executed on $N=20$ reproducible slices to accommodate 8 GB local VRAM. Full-corpus training sweeps remain future roadmap items.
2. **Missing Custom Fine-Tuning (Requirement #5 PARTIAL / OPEN)**: Evaluated an existing open-source domain-adapted checkpoint zero-shot; custom team-owned fine-tuning, training runs, and LoRA adaptation on Indian EO satellite data have not been performed and remain an active roadmap milestone.
3. **Change Detection**: The 0.1535 F1 on LEVIR-CD reflects unsupervised deep feature differencing, not an in-domain trained change segmentation head.
4. **Optical-SAR Data**: Uses a physically modeled radar backscatter proxy (`proxy_sar`) because authentic Cartosat-2S and RISAT-1A co-registered pairs require restricted ISRO/SAC licensing.
5. **Confidence Semantics (Uncalibrated)**: Algorithmic scores are uncalibrated and distinct per tool: VQA confidence is null; Grounding is a detector logit (not calibrated, not localization accuracy); Change Detection is a heuristic area stability margin (not F1/IoU); Optical-SAR is pipeline integrity (not target prediction accuracy). Calibration was not performed.

### 8. What Should the Live Demo Show?
1. **Multi-Modal Upload**: Uploading satellite imagery in the React web UI (`http://127.0.0.1:5173`).
2. **Agentic Routing**: Asking natural queries across different tasks (e.g. *"What is the land use?"* vs *"Locate ships"* vs *"Detect changes"*).
3. **Observable Execution Trace**: Expanding the execution trace drawer in the UI to demonstrate the 5-stage pipeline with live latencies.
4. **Visual Spatial Evidence**: Viewing generated bounding boxes, change heatmaps, and optical-SAR synergy maps.
5. **Firewall Resilience**: Submitting an ambiguous query (`"process this"`) or malicious parameter to demonstrate graceful rejection without GPU crashing.
