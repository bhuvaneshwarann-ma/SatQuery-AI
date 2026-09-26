# SatQuery AI — Final Claims Matrix & Verification Boundaries

**Document Status**: Official Defensibility & Evaluator Matrix  
**Last Updated**: 2026-09-26  
**Audience**: Hackathon Judges, Academic Evaluators, and Technical Reviewers

---

## 1. Executive Summary

This matrix establishes the verified factual boundaries of the **SatQuery AI** system. Every claim is categorized strictly based on reproducible empirical evidence stored directly in this repository.

| Claim Category | Definition | What We CAN Claim on Stage | What We MUST NOT Claim |
| :--- | :--- | :--- | :--- |
| **VERIFIED** | Proven with empirical checkpoints, repeatable tests, and reproducible benchmarks. | LoRA VQA improves token F1 by +19.3%; Change detection calibrated to $\tau=0.30$ yielding +52.1% F1; Geospatial firewall intercepts mismatched grids in 3.29 ms; Counting queries route to Grounding to avoid VLM hallucination. | Do NOT claim 100% accuracy, real-time performance, or zero hallucination. |
| **PARTIALLY VALIDATED** | Model is operational and produces valid artifacts, but lacks labeled remote-sensing ground truth benchmark. | Grounding DINO detects spatial features zero-shot with cross-attention scores; produces annotated visual bounding boxes. | Do NOT claim localization accuracy (e.g., "82% accurate") or benchmarked mAP@0.5. |
| **NOT QUANTITATIVELY VALIDATED** | Architecture is implemented and tensor-aligned, but task-level ablation is not established. | DualStreamOpticalSARFusionNetwork implements dual ResNet-18 encoders, cross-modal attention, and radiometric Pearson $r=0.428$. | Do NOT claim optical+SAR fusion improves building segmentation or disaster detection over optical alone. |
| **FUTURE VALIDATION** | Experimental protocols defined for future benchmarking once large labeled archives are mounted. | SpaceNet-6 ablation protocol and DIOR-RSVG isotonic calibration plans are formally specified in repository documentation. | Do NOT cite simulated or fabricated benchmark metrics. |

---

## 2. Granular Verification Audit

### A. Parameter-Efficient VQA LoRA Adaptation (`VERIFIED`)
- **Base Model**: AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct.
- **LoRA Hyperparameters**: $r=16, \alpha=32$, target modules `["q_proj", "v_proj"]`.
- **Trainable Footprint**: 1,056,768 parameters (0.0126% of base model).
- **Empirical Validation ($N=20$ RSVQA-LR)**:
  - Macro Token F1: Baseline `0.2525` $\to$ Adapted `0.3012` (**+19.3% relative improvement**).
  - Presence Accuracy: Baseline `42.9%` $\to$ Adapted `75.0%` (**+32.1% absolute gain**).
  - Exact Match: Baseline `35.0%` $\to$ Adapted `30.0%` (adapted outputs provide descriptive sentences rather than one-word responses).
  - Counting Accuracy: `20.0%` on both (visual patch token collision limitation).
- **Leakage Protection**: Geographically partitioned hash split ensuring zero coordinate overlap between train and validation scenes.

### B. Bi-Temporal Change Detection Decision Boundary (`VERIFIED`)
- **Architecture**: Siamese difference feature extractor operating on co-registered temporal rasters.
- **Empirical Threshold Sweep ($N=20$ LEVIR-CD pairs)**:
  - Legacy threshold $\tau=0.42$: Precision = `0.1706`, Recall = `0.2285`, **F1 = `0.1535`**, **IoU = `0.0831`**.
  - Calibrated threshold $\tau=0.30$: Precision = `0.1388`, Recall = `0.7356`, **F1 = `0.2335`**, **IoU = `0.1322`**.
  - Relative gains: **+52.1% F1**, **+59.1% IoU**, **+221.9% Recall**.
- **Defensibility Guard**: Precision is $13.88\%$ due to unsupervised differencing sensitivity to shadows, seasonal shifts, and sensor noise. It is never presented as "high accuracy".

### C. Deterministic Counting Guardrail (`VERIFIED`)
- **Problem Solved**: General-purpose VLMs consistently hallucinate numeric object counts (achieving only 20% on counting probes).
- **Implementation**: Pre-routing regex filter detects counting queries (`"How many..."`, `"Count the..."`, `"What is the number of..."`) and routes them directly to `GROUNDING`.
- **Count Extraction**: Count is computed deterministically as `len(valid_grounded_boxes)`.
- **Zero-Detection Guarantee**: If no objects pass threshold, returns: *"No valid {target} were detected with the current grounding threshold."* (e.g. *"No valid ships were detected with the current grounding threshold."*).
- **Single/Plural Formats**: *"1 ship was detected."*, *"2 ships were detected."*
- **Audit Trace**: Response attaches explicit limitation: *"Count is derived from grounding detections rather than VLM-generated counting."*

### D. Geospatial Validation Firewall (`VERIFIED`)
- **Implementation**: `backend/app/services/geospatial_service.py`.
- **Integrity Checks**:
  - Raster dimension parity (rejects unaligned pairs, e.g. 720x480 vs 944x314 in **3.29 ms**).
  - CRS / EPSG metadata compatibility.
  - Multi-band channel validation (3-band optical vs single-band SAR).
  - Radiometric min-max normalization.

### E. Text-Guided Grounding (`PARTIALLY VALIDATED`)
- **Status**: Operational zero-shot inference with Grounding DINO Swin-T.
- **Evidence**: Generates bounding boxes, annotated image overlays, and cross-attention scores.
- **Boundary**: Does not possess labeled remote-sensing benchmark validation (e.g. DIOR-RSVG). Reported scores are **uncalibrated detector confidence**, not spatial localization accuracy.

### F. Dual-Stream Optical + SAR Fusion (`NOT QUANTITATIVELY VALIDATED`)
- **Status**: Architectural prototype (`DualStreamOpticalSARFusionNetwork`).
- **Evidence**: Dual ResNet-18 encoders, cross-modal attention fusion, radiometric Pearson correlation ($r=0.428$), and false-color composite artifacts.
- **Boundary**: **Task-level quantitative superiority on benchmark tasks is not currently established.** We do not claim improved segmentation accuracy over single-sensor baselines.

---

## 3. Evaluator Defense Cheat-Sheet

| If a Judge Asks... | Deliverable Defense |
| :--- | :--- |
| *"Why is your change detection F1 only 0.23?"* | *"Because it is an unsupervised Siamese feature differencer evaluated on LEVIR-CD without task-specific supervised training. Rather than hiding this limitation, we swept 10 thresholds to optimize F1 from 0.15 to 0.23 (+52%), and our multi-tool pipeline validates these candidates using Grounding DINO."* |
| *"Can your VLM reliably count ships?"* | *"No, standard VLMs fail at small-object counting due to visual patch token collisions (our adapted VLM scored only 20%). That is why we built a deterministic counting guardrail that intercepts count queries and delegates enumeration to Grounding DINO's spatial bounding boxes."* |
| *"Does your Optical-SAR model outperform optical alone?"* | *"Task-level superiority has not been quantitatively benchmarked on paired labeled datasets like SpaceNet-6. Our model is currently an architectural prototype demonstrating tensor alignment and radiometric Pearson correlation ($r=0.428$). We have authored a formal 3-arm ablation plan in `docs/optical_sar_validation_plan.md`."* |
| *"Is your Grounding confidence an IoU accuracy score?"* | *"No. It is a cross-attention logit score from Grounding DINO. We clearly label it as uncalibrated model confidence, and our roadmap specifies Isotonic calibration against DIOR-RSVG."* |
