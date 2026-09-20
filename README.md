# SatQuery AI 🛰️🤖

**Grounded Multimodal Intelligence for Satellite Earth Observation Analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React_19_+_Vite-61DAFB.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Regression_Tests-29%2F29_PASS-success.svg)](docs/results/phase_9_demo_readiness_report.md)

---

## 📌 Executive Summary

**SatQuery AI** transforms heterogeneous Earth Observation questions into a controlled, evidence-producing analysis workflow. 

Rather than relying on an unconstrained, monolithic chatbot or fragile desktop GIS toolchains, SatQuery AI employs a **deterministic agent router** that validates incoming natural language queries and raster payloads, enforces strict parameter firewalls, and dispatches tasks to specialized computer vision and vision-language pipelines.

---

## 🚀 Key Capabilities

SatQuery AI provides native, unified support for four distinct Earth Observation analytical modalities:

| Capability | Specialist Model / Backbone | Input Modality | Primary Output Artifact | Confidence Metric Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **1. Satellite VQA** | Domain-Adapted VLM (3B) | 1 Optical Image + Natural Language Question | Structured Text Answer | `null` (uncalculated; never fabricated) |
| **2. Visual Grounding** | Open-Vocabulary Detector (Grounding DINO) | 1 Optical Image + Detection Prompt | Bounding Box Overlay PNG | Uncalibrated Detector Logit ($37.3\%$) |
| **3. Temporal Change** | Siamese Feature Differencer (ResNet-18) | 2 Co-Registered Images ($T_1, T_2$) | Binary Difference Mask & Heatmap PNG | Area Stability Margin ($97.4\%$ unchanged) |
| **4. Optical-SAR Fusion** | Dual-Stream Matrix Correlator | 1 Optical + 1 Microwave SAR Image | False-Color Fused Composite PNG | Pipeline Integrity Status ($100\%$ valid grid) |

---

## 🏛️ System Architecture

```text
               [ USER INTERFACE / API CLIENT ]
                             │  (Natural Language Query + 1 or 2 Satellite Images)
                             ▼
                 [ FASTAPI BACKEND GATEWAY ]
                             │
                             ▼
                  [ INPUT VALIDATION LAYER ]
              (MIME check, 15MB limit, PIL raster integrity)
                             │
                             ▼
                     [ AGENT ROUTER ]
          (Deterministic Regex Fast-Path + Semantic Fallback)
                             │
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
[ PARAMETER FIREWALL ]                  [ GPU EXECUTION LOCK ]
 (Strict Pydantic Validation)             (_GPU_EXECUTION_LOCK)
        │                                         │
        └────────────────────┬────────────────────┘
                             │
             [ MULTIMODAL SPECIALIST REGISTRY ]
   ┌───────────────────┬───────────────────┬───────────────────┐
   ▼                   ▼                   ▼                   ▼
 [ VQA ENGINE ]    [ GROUNDING ]       [ CHANGE DET. ]    [ OPTICAL-SAR ]
(3B Remote-Sensing  (Open-Vocabulary   (Siamese ResNet-18  (Radiometric Grid
  Autoregressive)     Detector)         Differencing)       Normalization)
   │                   │                   │                   │
   └───────────────────┴─────────┬─────────┴───────────────────┘
                                 │
                     [ EVIDENCE ARTIFACT BUILDER ]
               (Bounding Overlays, Change Masks, Composites)
                                 │
                   [ OBSERVABLE EXECUTION TRACE ]
               (Per-step telemetry, latencies, memory)
                                 │
                                 ▼
                     [ STRUCTURED API RESULT ]
```

---

## 🔒 Safe Agentic Engineering & Governance

1. **Immutable Tool Registry**: The router is constrained to an immutable registry of 4 tools (`vqa`, `visual_grounding`, `change_detection`, `optical_sar_analysis`). No arbitrary code or shell execution is permitted.
2. **Strict Parameter Firewall**: Model arguments are validated against Pydantic schemas, blocking prompt injections or malformed parameters.
3. **Sequential Execution Scheduling (`_GPU_EXECUTION_LOCK`)**: Heavy model calls are serialized to guarantee zero CUDA Out-Of-Memory (OOM) crashes on local 8 GB consumer GPUs.
4. **Observable Trace vs. Hidden Thought**: SatQuery AI records system-level execution telemetry (tool choice, latency, VRAM, artifact paths), not simulated chain-of-thought tokens.
5. **Strict Confidence Semantics**: Confidence metrics are never reported as empirical classification accuracy unless formally calibrated:
   - **VQA**: Explicitly `null`.
   - **Grounding**: Uncalibrated detector logit.
   - **Change Detection**: Area stability margin (fraction of scene unchanged).
   - **Optical-SAR**: Pipeline integrity confirmation status.

---

## 📊 Empirical Benchmark Results

SatQuery AI's specialist models were evaluated against genuine public benchmark slices ($N=20$, Seed 42). These results represent an **honest zero-shot baseline**, establishing pipeline reproducibility, latency feasibility, and identified improvement areas—**not claims of state-of-the-art accuracy**.

### 1. RSVQA-LR (Sentinel-2 Satellite VQA, $N=20$)
- **Exact Match (EM)**: **`35.0%`** (7 / 20 canonical matches)
- **Token F1**: **`0.2525`**
- **Mean Latency**: **`50.11 s`** (Median: `49.60 s`)
- **Process Reliability**: **`0 Failures / 0 OOM Events`** (100% completion)

### 2. LEVIR-CD (Building Change Detection, $N=20$)
- **Macro IoU**: **`0.0878`** | **Micro IoU**: **`0.1113`**
- **Macro F1**: **`0.1535`** | **Micro F1**: **`0.2002`**
- **Macro Precision**: **`0.1237`** | **Macro Recall**: **`0.6755`**
- **Mean Latency**: **`27.4 ms`** per pair

### 3. Automated Regression Suites
- **Failure & Security Suite** (`tests/test_failure_cases.py`): **`10 / 10 PASS (100%)`**
- **Agent Orchestration Suite** (`tests/test_agent_orchestration.py`): **`11 / 11 PASS (100%)`**
- **Live API Contract Suite** (`tests/test_api_contract.py`): **`8 / 8 PASS (100%)`**

---

## 🛠️ Quickstart Guide

### Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.0` or higher
- **GPU**: NVIDIA GPU with $\ge 8$ GB VRAM recommended (CPU execution supported with fallback)
- **Storage**: **25 GB free disk space recommended** (~12 GB active for PyTorch environment and 3B VLM weights cache, plus 13 GB operational buffer for dataset caching, inference tensor scratchpad, and visual evidence artifacts)

### 1. Clone the Repository
```bash
git clone https://github.com/bhuvaneshwarann-ma/SatQuery-AI.git
cd SatQuery-AI
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
*API and Swagger documentation will be available at:* [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
```bash
# Open a new terminal
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
*Web dashboard will be available at:* [http://localhost:5173](http://localhost:5173)

---

## 🎮 Interactive Presets in the UI

The web interface includes 4 one-click demo presets ready for evaluation:

1. **`Preset 1: VQA Coastal Terrain`**: Ingests Sentinel-2 coastal settlement imagery (`sample_satellite.jpg`) and extracts terrain classifications.
2. **`Preset 2: Grounding Maritime`**: Dispatches Grounding DINO to detect and draw bounding boxes around vessels in a port facility (`sample_satellite_port.jpg`).
3. **`Preset 3: Port Expansion Change`**: Compares a baseline port layout with a temporal pair (`sample_satellite_port_t2_synthetic.jpg`) to render change masks.
4. **`Preset 4: Maritime Optical-SAR`**: Ingests cloud-obscured optical imagery alongside radar backscatter (`sample_sentinel1_sar_mauritius.jpg`) to verify vessel returns.

---

## 📂 Project Structure

```text
SatQuery-AI/
├── ai/
│   ├── evaluation/            # Benchmark execution runners and test harnesses
│   │   ├── benchmark_runner.py
│   │   ├── benchmark_protocol.md
│   │   └── benchmark_schema.json
│   └── inference/             # Model wrappers and weight management
├── backend/
│   ├── app/
│   │   ├── agent/             # Intent router, tool registry, and firewalls
│   │   ├── api/               # FastAPI endpoints, schemas, and routes
│   │   ├── services/          # Specialist pipelines & GPU serialization lock
│   │   └── main.py            # Application entrypoint
│   └── requirements.txt
├── data/
│   ├── benchmarks/            # LEVIR-CD and RSVQA-LR sample manifests
│   ├── samples/               # Public test images for live demonstration
│   └── uploads/               # Isolated storage for inference payloads
├── docs/
│   ├── results/               # Authoritative evidence reports, defense matrices & slide decks
│   │   ├── final_ppt_content.md
│   │   ├── final_demo_runbook.md
│   │   ├── final_judge_qa.md
│   │   └── final_presentation_audit.md
│   └── architecture.md        # Technical design documentation
└── frontend/                  # React 19 + TypeScript + Vite analytics dashboard
    ├── src/
    │   ├── components/        # UI components (Header, AnalysisForm, ResultView)
    │   └── api/               # API client and telemetry parsers
    └── package.json
```

---

## 🧭 Technical Roadmap & Open Work

- **Requirement #5 (VLM Domain Fine-Tuning)**: Transparently classified as **`PARTIAL / OPEN`**. We evaluated an open-source remote-sensing domain-adapted checkpoint zero-shot. Custom QLoRA fine-tuning on Indian satellite imagery (e.g. ISRO Cartosat-2S) is planned with multi-GPU cluster compute.
- **Supervised Change Detection**: Integrating ChangeFormer / BIT heads to replace unsupervised Siamese feature differencing.
- **Probabilistic Calibration**: Implementing temperature scaling and Platt scaling on validation splits to produce formal probabilistic confidence intervals.
- **Inference Optimization**: Deploying 4-bit AWQ quantization and vLLM serving to reduce VQA latency from ~50s to $<3$s.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
