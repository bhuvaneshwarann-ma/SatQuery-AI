# SatQuery AI — Phase 8E Evidence Correction Report

**Evaluation Date**: 2026-09-20  
**Audit Purpose**: Focused correction of confidence terminology, preservation of Requirement #5 status boundaries, alignment of evaluator readiness semantics, audit of demo claims, and regression verification.

---

## 1. Issues Identified During Audit

1. **Premature Calibration Claims on Requirement #9**:
   - *Previous Text*: Referred to "Calibrated task-specific confidence metrics", implying statistical calibration experiments (e.g., Platt scaling, temperature scaling, Expected Calibration Error) had been conducted.
   - *Reality*: No calibration experiments were performed. Confidence outputs are uncalibrated heuristic scores (detector cross-attention, area ratios, discrete pipeline integrity).
2. **Ambiguity on Requirement #5 (Remote-Sensing VLM Adaptation / Fine-Tuning)**:
   - *Risk*: Evaluators could misunderstand the integration and zero-shot benchmark evaluation of an open-source domain-adapted checkpoint (`remote-sensing-Qwen2.5-VL-3B-Instruct`) as team-owned fine-tuning or in-domain parameter adaptation on Indian EO satellite data.
   - *Correction*: Requirement #5 must be explicitly preserved as **PARTIAL / OPEN**, clearly documenting that custom fine-tuning evidence is missing.
3. **Evaluator Readiness Semantics**:
   - *Risk*: A superficial reading of `EVALUATOR_READINESS_RESULT=PASS` could suggest that all 10 SIH problem requirements are 100% satisfied and closed.
   - *Correction*: Redefined `EVALUATOR_READINESS_RESULT=PASS` to certify that the **technical evidence package and verification process are evaluator-ready**, with Requirement #5 explicitly declared as **PARTIAL / OPEN**.
4. **Demo Claims Boundary Gaps**:
   - *Issue*: `demo_claims_matrix.md` required explicit clauses prohibiting claims of calibrated confidence, custom VLM fine-tuning, operational disaster-damage quantification, and universal temporal change generalization beyond the tested slice.

---

## 2. Files Modified

1. **`docs/results/judge_evidence_matrix.md`**:
   - Corrected Requirement #9 status to `VERIFIED & STANDARDIZED (Strictly uncalibrated; calibration experiments NOT performed)`.
   - Updated Requirement #9 limitation with explicit per-tool uncalibrated semantics.
   - Reaffirmed Requirement #5 status as `PARTIAL / OPEN (Domain-adapted pre-trained checkpoint benchmarked; custom team fine-tuning NOT performed)`.
   - Updated Evaluation Summary and defined `EVALUATOR_READINESS_RESULT=PASS` boundary conditions.
2. **`docs/results/demo_claims_matrix.md`**:
   - Updated Section 2 to delineate per-tool uncalibrated confidence semantics.
   - Expanded Section 3 (Prohibited Claims) with explicit prohibitions against calibration claims, custom fine-tuning claims, operational disaster-damage assessment claims, and generalized real-world temporal change accuracy claims.
3. **`docs/results/satquery_ai_evaluation_report.md`**:
   - Replaced "Calibrated Confidence Semantics" in Executive Summary with "Transparent Confidence Semantics", affirming all scores are strictly uncalibrated.
   - Added explicit evaluator readiness definition callout in Section 1.
   - Expanded Section 9 (Limitations) item 5 with per-tool uncalibrated confidence semantics and item 6 detailing Requirement #5 PARTIAL / OPEN status.
4. **`docs/results/evaluator_one_page.md`**:
   - Updated status header to reflect evaluator readiness with Requirement #5 remaining PARTIAL / OPEN.
   - Updated Section 7 (Limitations) items 2 and 5 to explicitly detail missing custom fine-tuning and uncalibrated per-tool confidence definitions.
5. **`docs/results/confidence_semantics.md`**:
   - Created synchronized reference copy in `docs/results/` confirming tool-by-tool uncalibrated metrics and prohibited presentation statements.

---

## 3. Exact Terminology Corrections

The following standardized technical definitions are now enforced across all documentation and presentations:

| Modality / Tool | Former Terminology | Corrected & Authoritative Terminology | Permitted Presentation Statement |
| :--- | :--- | :--- | :--- |
| **VQA** (`Qwen2.5-VL-3B`) | Calibrated confidence | **Confidence Unavailable / `null`** | *"VQA outputs natural language responses; no token confidence is fabricated."* |
| **Grounding** (`Grounding DINO`) | Calibrated confidence | **Uncalibrated Detector Heuristic Score** (cross-attention similarity); NOT calibrated and NOT localization accuracy or IoU. | *"Confidence score indicates cross-attention feature similarity, not localization accuracy."* |
| **Change Detection** (`Siamese-ResNet18`) | Calibrated confidence | **Heuristic Area Stability Margin** (unmodified area proportion); NOT equivalent to F1 or IoU. | *"Confidence score indicates the proportion of unchanged background area, not change detection F1/IoU."* |
| **Optical-SAR** (`Dual-Stream Engine`) | Calibrated confidence | **Pipeline Integrity Status** ($1.0$ discrete completion indicator); NOT target prediction accuracy. | *"Confidence confirms successful dual-sensor radiometric alignment, not target classification accuracy."* |

---

## 4. Status of Requirement #5 (Remote-Sensing VLM Adaptation / Fine-Tuning)

- **Official Status**: **`PARTIAL / OPEN`**
- **What is Verified**:
  - Successfully integrated open-source domain-adapted remote-sensing VLM checkpoint (`AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`).
  - Benchmarked zero-shot on genuine Sentinel-2 low-resolution pairs (RSVQA-LR $N=20$), achieving 35.0% Exact Match and 0.2525 Token F1 under 8 GB VRAM.
- **What is Open / Missing**:
  - Custom team-owned fine-tuning, training scripts, LoRA adapter weights, and parameter adaptation on Indian EO satellite data (e.g. Cartosat-2S / Resourcesat) have **not** been performed.
  - No adaptation loss curves, fine-tuned checkpoints, or comparative pre/post adaptation benchmarks exist.
  - Formally scheduled as a post-hackathon roadmap milestone.

---

## 5. Benchmark Numbers Audit

All reported benchmark figures match ground-truth JSON outputs identically:

- **RSVQA-LR ($N=20$, Sentinel-2 VQA)**:
  - Exact Match (EM): **35.0%** (7 / 20)
  - Mean Token F1: **0.2525**
  - Mean Latency: **50.11 s**
  - Median Latency: **49.60 s**
  - Failures / OOM Events: **0**
- **LEVIR-CD ($N=20$, Google Earth Building Change Detection)**:
  - Macro Change IoU: **0.0878**
  - Micro Change IoU: **0.1113**
  - Macro F1-Score: **0.1535**
  - Micro F1-Score: **0.2002**
  - Macro Precision: **0.1237**
  - Macro Recall: **0.6755**
  - Mean Latency: **27.4 ms**

---

## 6. Regression Results

All regression suites executed without modifications to core inference code:

1. `test_failure_cases.py`: **10 / 10 PASS** (input validation, parameter firewall, corrupt image handling)
2. `test_agent_orchestration.py`: **11 / 11 PASS** (`AGENT_ORCHESTRATION_TEST_RESULT=PASS`)
3. `test_api_contract.py`: **8 / 8 PASS** (`API_CONTRACT_TEST_RESULT=PASS`)

---

## 7. Remaining Open Risks & Mitigations

1. **VQA Latency**: 3B VLM autoregressive decoding takes ~50s per query on 8 GB laptop GPU.  
   *Mitigation*: UI displays live loading indicator and execution trace stage timer.
2. **Optical-SAR Satellite Data Licensing**: Authentic Cartosat-2S + RISAT-1A co-registered rasters remain restricted under ISRO/SAC data agreements.  
   *Mitigation*: Transparently disclosed that a physically modeled radar backscatter proxy (`proxy_sar`) was evaluated for dual-stream radiometric fusion.
3. **Change Detection Domain Transfer**: ResNet-18 feature differencing threshold ($\tau=0.42$) was calibrated on building footprints in LEVIR-CD and may require retuning for flooded or agricultural terrain.  
   *Mitigation*: Documented as an unsupervised baseline with documented margin semantics.

---

EVIDENCE_CORRECTION_RESULT=PASS
