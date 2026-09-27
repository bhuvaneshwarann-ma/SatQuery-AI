# SatQuery AI — Comprehensive Repository Audit Report (Phase 1)

**Audit Date**: September 2026  
**Auditor**: Lead AI Systems & Remote-Sensing Engineer  
**Target System**: SatQuery AI (Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries)  
**Host Environment**: Windows 11 x64, Python 3.12.10, PyTorch 2.14.0+cu130, NVIDIA GeForce RTX 5050 Laptop GPU (8 GB GDDR7 VRAM)

---

## 1. Executive Summary

SatQuery AI has a solid, well-architected foundational codebase featuring a deterministic agent router, 4 core specialist remote-sensing execution pipelines (VQA, Grounding, Change Detection, Optical+SAR), a FastAPI backend with GPU serialization locks, and a React 19 + TypeScript + Vite frontend.

However, against the rigorous requirements of the problem statement and evaluator expectations, several critical gaps and areas of technical debt were identified:
1. **Agent Planning**: Current routing is single-stage/single-tool. Complex queries requiring multi-stage reasoning (e.g. change detection + target grounding + descriptive change summary) lack a structured planner, multi-tool plan decomposition, and multi-specialist evidence fusion.
2. **VQA Adaptation (Critical)**: The system currently directly references the base pre-trained checkpoint `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` without project-owned PEFT/LoRA adapter weights or a reproducible training pipeline.
3. **Change Detection Optimization**: The Siamese ResNet-18 feature differencer suffers from high false-positive rates at default thresholds. It lacks a threshold sweep curve on genuine benchmark data (`LEVIR-CD`) and a trainable/refined decoder head.
4. **Optical + SAR Science**: While the current tool extracts cross-modal correlation ($r$) and backscatter anomalies, it relies solely on Pearson correlation rather than deep dual-stream feature fusion and does not provide an ablation across modalities.
5. **Geospatial & Format Validation**: Current validation checks standard image formats (JPEG/PNG dimensions) and basic TIFF readability, but lacks GeoTIFF coordinate reference system (CRS), affine transform, bounding box, spatial resolution, and co-registration compatibility checks.
6. **Reproducibility & Dependencies**: The root directory lacks a consolidated `requirements.txt` and `.env.example`, and relies on ad-hoc local configurations.

---

## 2. Current Architecture & Component Inventory

### 2.1 System Architecture Overview

```
                                  [USER]
                                     │
                             [Vite React 19 UI]
                        (Port 5173 / REST API Client)
                                     │
                                     ▼
                            [FastAPI Backend]
                     (Main /routes /services /agent)
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
         [Deterministic Agent Router]       [_GPU_EXECUTION_LOCK]
         ├── Intent Classification         (Serialized GPU access)
         ├── Asset Validation                         │
         └── Parameter Firewall                       ▼
                    │                     [Specialist Model Pipeline]
                    └────────────────────►├── 1. VQA (Qwen2.5-VL-3B)
                                          ├── 2. Grounding (Grounding DINO)
                                          ├── 3. Change (Siamese ResNet18)
                                          └── 4. Optical+SAR (Dual Matrix)
                                                      │
                                                      ▼
                                          [Confidence & Evidence Engine]
                                          ├── Multi-type confidence
                                          ├── Visual evidence artifacts
                                          └── JSON Execution Trace
```

### 2.2 Entry Points & Directory Structure

| Path | Purpose | Current State |
| :--- | :--- | :--- |
| `backend/app/main.py` | FastAPI application entry point, CORS, static mounts | Working |
| `backend/app/api/routes.py` | `/api/health`, `/api/tools`, `/api/analyze` endpoints | Working |
| `backend/app/agent/router.py` | Regex/keyword deterministic intent classification | Working (single-tool only) |
| `backend/app/agent/registry.py` | Certified tool schema & parameter whitelist firewall | Working |
| `backend/app/services/orchestration_service.py` | End-to-end execution, trace generation | Working (single-tool execution) |
| `backend/app/services/confidence_service.py` | Confidence scoring heuristics & evidence extraction | Working |
| `ai/inference/vqa.py` | Qwen2.5-VL-3B-Instruct executor | Working, lacks LoRA adapter integration |
| `ai/inference/grounding.py` | Grounding DINO Tiny executor | Working |
| `ai/inference/change_detection.py` | Siamese ResNet18 Euclidean feature differencer | Working baseline, high false positives |
| `ai/inference/optical_sar.py` | Optical + SAR statistics & proxy SAR classification | Working, needs joint fusion upgrade |
| `data/benchmarks/rsvqa_lr/` | 20-sample validation split of RSVQA-LR | Ingested, baseline evaluated |
| `data/benchmarks/levir_cd/` | 20-sample test split of LEVIR-CD (T1, T2, label) | Ingested, baseline evaluated |
| `data/samples/` | Sample Landsat-9, proxy SAR, synthetic T2 imagery | Ingested |
| `frontend/` | React 19 + TypeScript + Vite app shell & views | Working, builds cleanly |

---

## 3. Detailed Component Analysis & Technical Debt

### 3.1 Agent & Orchestration
- **Strengths**: Strict deterministic parameter firewall prevents injection of malicious parameters. Execution is serialized with `_GPU_EXECUTION_LOCK` to respect 8 GB VRAM.
- **Weaknesses / Missing**:
  - Only maps query to a single tool.
  - Does not support compound/multi-tool queries (e.g., "Find built-up areas and detect what changed between T1 and T2").
  - Lacks structured task plan output (`intent`, `target`, `requires_temporal_pair`, `plan`: `[{tool, purpose}]`).
  - Lacks evidence fusion across sequential tool outputs.

### 3.2 VQA Adaptation
- **Strengths**: Isolated executor, on-demand loading, GPU cleanup in `finally` blocks, token generation bounding.
- **Weaknesses / Missing**:
  - No fine-tuning or adaptation code exists in the repository.
  - Model weights used are upstream `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`.
  - Lack of LoRA training script, dataset preparation script, adapter validation script, and before/after evaluation report.

### 3.3 Change Detection
- **Strengths**: Clean Siamese feature extraction using pre-trained ResNet18, composite visual artifact generator.
- **Weaknesses / Missing**:
  - Baseline LEVIR-CD results show Precision ≈ 0.1237, Recall ≈ 0.6755, F1 ≈ 0.1535, IoU ≈ 0.0878 at default threshold 0.42.
  - No threshold sweep has been systematically executed or documented as a CSV curve.
  - Lacks a trained/refined decoder head to suppress spatial noise.

### 3.4 Grounding
- **Strengths**: IDEA-Research/grounding-dino-tiny runs in ~0.36s warm, outputs bounding boxes and visual artifacts.
- **Weaknesses / Missing**:
  - Detector confidence must be explicitly distinguished from ground-truth probability of correctness.
  - Missing quantitative localization evaluation on remote sensing datasets.

### 3.5 Optical + SAR Analysis
- **Strengths**: Differentiates `spaceborne_sar` vs `proxy_sar` vs `unverified_sar`. Generates 3-panel composite.
- **Weaknesses / Missing**:
  - Statistical analysis relies heavily on Pearson correlation ($r$) between optical luminance and radar backscatter.
  - Lacks a deep joint cross-modal fusion network that extracts shared multimodal representations.
  - Lacks ablation metrics (Optical Only vs SAR Only vs Joint Optical+SAR).

### 3.6 Geospatial & Input Validation
- **Strengths**: Checks image file existence, corrupt byte detection via PIL verify, dimension equality for pairs.
- **Weaknesses / Missing**:
  - No GeoTIFF tag inspection (CRS EPSG code, geotransform, spatial resolution, bounding box bounds).
  - Does not check if T1 and T2 or Optical and SAR actually overlap geographically (assumes equal pixel dimensions equals geographic alignment).
  - Lacks actionable error messages when geospatial projections or bounding boxes differ.

---

## 4. Problem-Statement Compliance Matrix (Pre-Upgrade Audit)

| Requirement | Implementation State | Evidence / Gaps | Audit Status |
| :--- | :--- | :--- | :--- |
| **1. Single-image VQA** | `ai/inference/vqa.py` | Qwen2.5-VL-3B works, but unadapted base model | **PARTIAL** |
| **2. Single-image Grounding** | `ai/inference/grounding.py` | Grounding DINO Tiny detects ships/ports with boxes | **IMPLEMENTED** |
| **3. Bi-temporal Change** | `ai/inference/change_detection.py` | Siamese ResNet18 baseline working, high false positives | **PARTIAL** |
| **4. Optical + SAR Paired** | `ai/inference/optical_sar.py` | Correlation & backscatter anomalies, needs deep fusion | **PARTIAL** |
| **5. Agentic Orchestration** | `backend/app/agent/router.py` | Single-tool router works; lacks multi-tool planner | **PARTIAL** |
| **6. Project-Owned VLM Adaptation** | None | No PEFT/LoRA training code, config, or weights | **NOT IMPLEMENTED** |
| **7. Geospatial Validation** | Basic PIL dimension check | No CRS, bounds, affine, resolution, or footprint check | **PARTIAL** |
| **8. Visual Evidence** | Execution composite images | Saved to `docs/results/`, displayed in UI | **IMPLEMENTED** |
| **9. Confidence Reporting** | `confidence_service.py` | Multi-category confidence (heuristic/logit/status) | **IMPLEMENTED** |
| **10. Auditable Execution Summary** | Execution trace in JSON | Visible in API response and UI drawer | **IMPLEMENTED** |
| **11. Downloadable Results** | UI export / Static artifacts | Static files served at `/api/artifacts` | **IMPLEMENTED** |

---

## 5. Upgrade Action Plan & Target Deliverables

### Phase A: Geospatial Input Validation & Format Engine
- Create `backend/app/services/geospatial_service.py`:
  - GeoTIFF parsing: CRS, GeoKeys, ModelTiepoint, ModelPixelScale, Affine Transform, bounding box.
  - Multi-raster compatibility checker: CRS matching, spatial footprint intersection, resolution ratio check.
  - Preview generation: Contrast-stretched, normalized RGB/false-color previews from multispectral rasters.
  - Clear, actionable error messages for incompatible geospatial inputs.

### Phase B: Advanced Multi-Tool Agent Planner & Policy Firewall
- Upgrade `backend/app/agent/schemas.py` and `router.py`:
  - Support multi-stage query classification (e.g. `CHANGE_ANALYSIS`, `TARGETED_CHANGE`).
  - Generate structured task plans conforming to the target schema:
    `{ "intent": ..., "target": ..., "requires_temporal_pair": ..., "requires_spatial_evidence": ..., "plan": [...] }`
  - Implement deterministic policy engine verifying tool dependencies and parameter safety.
  - Sequential execution with intermediate evidence propagation and final cross-tool evidence fusion.

### Phase C: VQA PEFT/LoRA Adaptation Engine
- Build `training/` pipeline:
  - `training/data/prepare_vqa.py`: Remote-sensing VQA dataset preprocessing with balanced categories (counting, presence, spatial, comparison, land_cover), benchmark non-leakage verification.
  - `training/data/validate_vqa.py`: Data integrity, image validation, format normalization.
  - `training/configs/vqa_lora.yaml`: LoRA config (rank=8, alpha=16, dropout=0.05, target_modules for Qwen2.5-VL).
  - `training/train_vqa_lora.py`: PyTorch + PEFT training script with gradient accumulation, BF16/FP16, frozen vision encoder/base LLM, separate adapter weight saving.
  - `training/evaluate_vqa.py`: Side-by-side evaluation against RSVQA-LR benchmark subset.
  - Generate `results/vqa_before_after.json` and `results/vqa_before_after.md`.

### Phase D: Change Detection Refinement & Threshold Sweep
- Implement `ai/evaluation/sweep_change_thresholds.py`:
  - Run sweep across thresholds [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50] on LEVIR-CD test subset.
  - Calculate Precision, Recall, F1, and IoU per threshold.
  - Save `results/change_threshold_sweep.csv`.
- Implement lightweight change refinement decoder head in `ai/inference/change_detection.py` to suppress false positive background clutter.

### Phase E: Optical + SAR Joint Fusion & Modality Ablation
- Upgrade `ai/inference/optical_sar.py`:
  - Dual-stream deep feature extractor (Optical stream + SAR stream).
  - Cross-modal attention / joint fusion head.
  - Empirical ablation pipeline: Optical Only vs SAR Only vs Joint Optical+SAR.
  - Transparent data classification: spaceborne SAR vs proxy SAR vs unverified SAR.

### Phase F: End-to-End Testing, Documentation & Reproducibility
- Create `requirements.txt` and `.env.example`.
- Implement comprehensive automated test suites covering all validation, routing, agent multi-tool planning, model smoke tests, and end-to-end flows.
- Generate `COMPLIANCE_MATRIX.md`, `EVALUATION_REPORT.md`, and `FINAL_STATUS.md`.

---

## 6. Files to be Created or Modified

### Files to Create:
- `AUDIT_REPORT.md` (This document)
- `requirements.txt`
- `.env.example`
- `backend/app/services/geospatial_service.py`
- `training/data/prepare_vqa.py`
- `training/data/validate_vqa.py`
- `training/configs/vqa_lora.yaml`
- `training/train_vqa_lora.py`
- `training/evaluate_vqa.py`
- `training/README.md`
- `ai/evaluation/sweep_change_thresholds.py`
- `results/change_threshold_sweep.csv`
- `results/vqa_before_after.json`
- `results/vqa_before_after.md`
- `COMPLIANCE_MATRIX.md`
- `EVALUATION_REPORT.md`
- `FINAL_STATUS.md`

### Files to Modify:
- `backend/app/agent/schemas.py` (Structured task plan, execution trace)
- `backend/app/agent/router.py` (Multi-tool planning, intent classification)
- `backend/app/services/orchestration_service.py` (Multi-stage execution & evidence fusion)
- `backend/app/api/routes.py` (Geospatial validation integration, plan telemetry)
- `ai/inference/vqa.py` (LoRA adapter loading support)
- `ai/inference/change_detection.py` (Optimal thresholding & refinement decoder)
- `ai/inference/optical_sar.py` (Joint deep feature fusion & ablation support)
- `frontend/src/pages/AnalysisPage.tsx` & components (Plan visualization, multi-tool stages)
