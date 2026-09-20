# SatQuery AI — Mock Evaluator Technical Review (Phase 10)

**Review Role**: Senior Defense & Remote Sensing Technical Evaluator (Smart India Hackathon)  
**Evaluation Scope**: Full architectural review, AI model rigor, benchmark reproducibility, security firewall, data provenance, and jury defensibility.  
**Review Policy**: Highly skeptical inspection. Zero tolerance for ungrounded claims, unverified metrics, fake confidence, or unacknowledged limitations.

---

## 1. Problem Significance & Domain Clarity

* **Evaluator Assessment**:
  The core problem addressed by SatQuery AI—enabling non-GIS personnel (e.g. disaster coordinators, defense duty officers) to interact conversationally with complex multi-modal satellite imagery—is of high operational significance. The distinction between raw multi-spectral raster processing and rapid decision intelligence is well-articulated.
* **Skeptical Observation**:
  The team must avoid generalizing this system as an all-purpose geospatial engine. Remote sensing spans hundreds of specialized sub-problems (hyperspectral unmixing, digital elevation modeling, bathymetry). SatQuery AI is specifically scoped to four distinct tasks (`VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`). The problem boundary is defensible only when kept within these four defined workflows.

---

## 2. Architectural Necessity: Agent Router vs. Monolithic VLM

* **Evaluator Assessment**:
  A primary trap in hackathons is claiming a general-purpose LLM or VLM can solve every domain task. SatQuery AI successfully avoids this fallacy by articulating why a single VLM is computationally and mathematically inadequate:
  1. Monolithic generative VLMs generate text tokens, not dense pixel-level binary change masks across multi-temporal raster grids.
  2. Monolithic VLMs lack inductive biases for non-RGB microwave SAR backscatter physics, speckle patterns, and dielectric contrast.
  3. Routing every spatial query to a 3B VLM incurs severe latency (~50s per sample) and memory overhead. Routing to a lightweight Siamese ResNet (27.4 ms) or Grounding DINO (8s) optimizes compute and latency.
* **Skeptical Observation**:
  The router is fundamentally deterministic and rule-guided. While this is an asset for security and predictability (preventing prompt injections and hallucinated actions), the team must not claim "emergent autonomous cognitive agent reasoning." It is a controllable, schema-bounded agent orchestrator.

---

## 3. Tool Registry, Parameter Firewall & Input Validation

* **Evaluator Assessment**:
  The pre-model security engineering is among the strongest components of the submission:
  - **Tool Registry (`backend/app/agent/registry.py`)**: Actions are strictly bounded by an immutable catalog. Unregistered tools (such as shell commands) are rejected immediately.
  - **Parameter Firewall**: Strips unpermitted parameters and enforces strict type and range constraints (e.g. `threshold` between `0.1` and `0.9`) in $<20\text{ ms}$ before GPU allocation.
  - **Input Validation**: Corrupted rasters, non-image binaries, and missing secondary images are caught in 4 to 25 ms, protecting neural network backbones from crash loops.
* **Skeptical Observation**:
  The parameter firewall is verified by automated test suites (`test_failure_cases.py` 10/10 PASS). The team must continue emphasizing that these rejections happen *before* invoking GPU models, which is a genuine architectural strength.

---

## 4. AI Contribution & Requirement #5 Status

* **Evaluator Assessment**:
  The team's handling of **SIH Problem Requirement #5 (Remote-Sensing VLM Adaptation / Fine-Tuning)** was inspected with particular scrutiny:
  - The team integrated and evaluated `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`, an open-source domain-adapted checkpoint, zero-shot on RSVQA-LR.
  - The team **does NOT claim to have performed custom fine-tuning, training runs, or LoRA parameter updates**.
  - Requirement #5 is transparently declared as **`PARTIAL / OPEN`** across all matrices, presentation slides, and reports.
* **Evaluator Verdict**:
  This demonstrates exceptional scientific honesty. In hackathon environments, teams frequently fabricate toy loss curves or claim "fine-tuning" after running a few gradient steps on unverified data. SatQuery AI's transparent admission that custom fine-tuning on Indian EO data is an open roadmap milestone protects them from fatal jury exposure.

---

## 5. Empirical Benchmark Results & Statistical Credibility

* **Evaluator Assessment**:
  The quantitative performance numbers reported across the documentation match the verified JSON benchmark outputs identically:
  - **RSVQA-LR ($N=20$, Sentinel-2 VQA)**:
    - Exact Match: **`35.0%`** (7 / 20 canonical matches)
    - Mean Token F1: **`0.2525`**
    - Mean Latency: **`50.11 s`** (Median: **`49.60 s`**)
    - Failures / OOM Events: **`0 / 20`** (100% completion rate)
  - **LEVIR-CD ($N=20$, Google Earth Building Change Detection)**:
    - Macro Change IoU: **`0.0878`** (Micro IoU: **`0.1113`**)
    - Macro F1-Score: **`0.1535`** (Micro F1-Score: **`0.2002`**)
    - Macro Precision: **`0.1237`** | Macro Recall: **`0.6755`**
    - Mean Latency: **`27.4 ms`** per pair
* **Evaluator Verdict on Performance Magnitude & Evidence Role**:
  - *Primary Evidence Role*: The benchmarks provide empirical evidence of (1) **reproducibility** (deterministic seed 42 under schema validation), (2) **baseline capability** (functional execution on public remote-sensing datasets), (3) **latency and hardware feasibility** (operating stably within 8 GB VRAM without OOM crashes), and (4) **identified improvement areas** (clarifying where in-domain adaptation is required). It is explicitly **NOT evidence of state-of-the-art accuracy**.
  - *RSVQA-LR (35.0% EM, 0.2525 Token F1)*: Represents an un-fine-tuned zero-shot baseline on low-resolution 10m Sentinel-2 imagery where fine-grained structure counting presents expected difficulty without domain-specific instruction tuning.
  - *LEVIR-CD (0.1535 Macro F1, 0.0878 Macro IoU)*: Reflects unsupervised deep feature differencing on ImageNet weights without building change supervision. While Macro Recall reached 0.6755, Macro Precision was only 0.1237, showing sensitivity to background texture and illumination variation. Recall alone must never be conflated with overall change detection accuracy.
  - *Sample Size ($N=20$)*: Acknowledged as a reproducible evaluation slice (Seed 42) designed for local GPU budget constraints; not a claim of full-corpus evaluation.


---

## 6. Confidence Semantics Audit

* **Evaluator Assessment**:
  The system's confidence definitions strictly adhere to the audited semantics:
  - **VQA**: Explicitly `null` / unavailable. No token probabilities are fabricated.
  - **Visual Grounding**: Heuristic detector logit ($37.3\%$) from Swin Transformer cross-attention; explicitly labeled as **uncalibrated** and **NOT localization accuracy or IoU**.
  - **Change Detection**: Area stability margin ($97.4\%$); explicitly labeled as the **proportion of unchanged scene area**, **NOT classification F1 or IoU**.
  - **Optical-SAR**: Pipeline integrity indicator ($100\%$); explicitly labeled as confirming **matrix grid matching and correlation calculation**, **NOT target classification accuracy**.
* **Evaluator Verdict**:
  No deceptive claims of "calibrated probabilities" or "95% accuracy" exist. The UI and documentation explicitly caveat all metrics.

---

## 7. Data Provenance & Limitations Disclosure

* **Evaluator Assessment**:
  - **Change Detection Demo Asset**: Transparently disclosed as a *controlled synthetic temporal pair* (`sample_satellite_port_t2_synthetic.jpg`) for reliable integration testing; ground-truth benchmarks were executed on real LEVIR-CD pairs.
  - **Optical-SAR Demo Asset**: Explicitly classified as *proxy SAR* (`sample_sentinel1_sar_mauritius.jpg`), simulating radar backscatter physics. Authentic ISRO Cartosat-2S and RISAT-1A co-registered pairs are properly documented as restricted under institutional licensing agreements.
  - **Zero Unsupported Operational Claims**: No claims of operational disaster damage assessment or production readiness are made.

---

## 8. Hardware & Concurrency Boundaries

* **Evaluator Assessment**:
  - **Local Hardware Profile**: NVIDIA GeForce RTX 5050 Laptop GPU (~8 GB VRAM).
  - **Execution Serialization**: Heavy model executions are guarded by `_GPU_EXECUTION_LOCK`. Attempting concurrent 3B VLM and computer vision passes would trigger immediate CUDA OOM; sequential execution guarantees 100% crash-free stability.
  - **Latency Transparency**: VQA latency (~50s) is displayed with an active elapsed stopwatch in the UI rather than being hidden or masked.

---

## 9. Final Evaluator Acceptance Determination

All four required review and defense artifacts have been created and verified:
1. `docs/results/mock_evaluator_review.md` (Current authoritative evaluation review)
2. `docs/results/judge_attack_questions.md` (28 probing evaluator attack questions across 10 categories)
3. `docs/results/judge_answer_sheet.md` (13 detailed defense scripts with 10s spoken answers and follow-ups)
4. `docs/results/final_risk_register.md` (10-point prioritized risk matrix with concrete mitigations)

All four documents are completely consistent with verified empirical benchmark outputs, maintain Requirement #5 as PARTIAL / OPEN, preserve exact confidence semantics, disclose all data proxies honestly, and contain zero prohibited claims.

---

MOCK_EVALUATOR_REVIEW_RESULT=PASS
