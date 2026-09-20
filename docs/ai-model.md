# AI Model & Adaptation Specification — SatQuery AI

## 1. Document Overview & Hardware Environment

This document specifies the AI model stack, adaptation strategies, specialist vision heads, model registry contracts, inference memory policies, and validation procedures for **SatQuery AI**.

### Target Hardware Environment
* **GPU**: NVIDIA GeForce RTX 5050 Laptop GPU
* **Expected VRAM**: 8 GB GDDR7
* **Compute Policy**: Maximum operational VRAM ceiling targeted at **6.5 GB – 7.0 GB** to preserve OS display overhead and prevent sudden Out-Of-Memory (OOM) aborts.
* **Driver & Framework Verification**: CUDA runtime, cuDNN, and PyTorch builds will **not** be hard-coded until verified directly against the physical machine during the runtime setup phase.

---

## 2. Remote-Sensing VQA & Captioning Engine

### 2.1 Primary Model: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Hugging Face Identifier**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Base Architecture**: Qwen2.5-VL-3B-Instruct (Vision-Language Transformer featuring dynamic resolution vision encoder and causal language decoder).
* **Remote-Sensing Adaptation**: Domain-specific instruction tuning and continuous pre-training on overhead Earth Observation (EO) corpora, aerial scene reasoning, and remote-sensing question-answering pairs.
* **Supported Tasks**:
  1. Single-image remote-sensing Visual Question Answering (VQA) — counting, spatial layouts, presence verification.
  2. Overhead scene description and land-cover / land-use (LULC) captioning.
* **Expected Inference Role**: Serves as the primary conversational and analytical reasoning core for single-image queries.
* **GPU / Memory Considerations**:
  - Parameter Count: ~3 Billion.
  - Native 16-bit (`bfloat16`/`float16`): Requires ~6.0 – 6.5 GB VRAM.
  - Quantized 4-bit (NF4 / AWQ / bitsandbytes): Requires ~2.5 – 3.2 GB VRAM, fitting comfortably within the 8 GB budget alongside image feature tokens.
* **Input / Output Format**:
  - *Input*: Preprocessed optical RGB image tensor ($3 \times H \times W$, normalized) + structured domain instruction prompt.
  - *Output*: Natural language text response + generated token log-probabilities (used by the Confidence Estimator).
* **Why Selected for MVP**:
  - 3B size is the sweet spot for modern reasoning performance on consumer/laptop GPUs with 8 GB VRAM.
  - Native remote-sensing domain tuning avoids generic vision hallucinations on nadir/overhead perspectives.
  - Supports dynamic input aspect ratios without forced square warping.
* **Known Limitations**:
  - Lacks pixel-level coordinate heads for fine-grained bounding box regression (delegated to Grounding DINO).
  - Sub-pixel objects ($< 10$ px) can be lost during patch visual tokenization.
  - May hallucinate if asked to identify features beyond the optical Ground Sampling Distance (GSD).

### 2.2 Backup / Reference Model: `MBZUAI/geochat-7B`
* **Hugging Face Identifier**: `MBZUAI/geochat-7B`
* **Base Architecture**: LLaVA-1.5 / Vicuna-7B backbone adapted for geospatial conversation.
* **Why NOT the Primary Local Model for RTX 5050 8 GB**:
  - 7B parameter footprint requires ~14–16 GB in 16-bit precision, or ~5.5–6.5 GB in 4-bit quantization.
  - In an 8 GB VRAM laptop environment, 4-bit 7B leaves virtually zero headroom for visual tokens, KV cache, and operating system framebuffers, posing acute OOM risk.
  - Based on older LLaVA-1.5 architecture with fixed $336 \times 336$ or $448 \times 448$ CLIP tile resolution, inferior to modern dynamic-resolution vision encoders.
* **Fallback Evaluation Trigger**: Retained as a reference benchmark or cloud-hosted fallback if local 4-bit evaluation of the 3B model shows deficiencies in specific regional Indian terrain terminology.

---

## 3. Text-Guided Visual Grounding Engine

### 3.1 Primary Model: Grounding DINO (Swin-T Variant)
* **Official Repository**: `IDEA-Research/GroundingDINO` (GitHub)
* **Checkpoint Identity**: `groundingdino_swint_ogc.pth` (Swin-Transformer Tiny backbone, OGC pre-trained)
* **Input**:
  - Preprocessed RGB image tensor ($3 \times H \times W$).
  - Natural language phrase query (e.g., `"cargo ship . oil storage tank . aircraft . bridge ."`).
* **Output**:
  - Normalized 2D bounding boxes $[x_{min}, y_{min}, x_{max}, y_{max}] \in [0.0, 1.0]$.
  - Associated text phrase tokens and predicted detection logits.
* **Role in SatQuery**: Primary visual localization engine for identifying target infrastructure and geographic objects requested in natural language.
* **Memory Considerations**:
  - Parameter Count: ~172 Million.
  - VRAM Consumption: ~800 MB – 1.2 GB in evaluation mode.
  - Extremely lightweight; can reside in VRAM concurrently or load/unload within milliseconds.
* **Confidence & Threshold Parameters (Exposed via Registry)**:
  - `box_threshold`: Minimum bounding box detection score (default: `0.35`, range: `0.10 – 0.90`).
  - `text_threshold`: Minimum cross-modal text-image alignment score (default: `0.25`, range: `0.10 – 0.90`).

---

## 4. Segmentation & Visual Evidence Engine

### 4.1 Primary Model: Segment Anything Model (SAM) — ViT-B Variant
* **Official Repository**: `facebookresearch/segment-anything` (GitHub)
* **Checkpoint Identity**: `sam_vit_b_01ec64.pth`
* **Input**:
  - Base RGB image tensor ($1024 \times 1024$ embedding space).
  - Spatial prompts: 2D bounding boxes $[x_{min}, y_{min}, x_{max}, y_{max}]$ provided directly by Grounding DINO.
* **Output**:
  - High-resolution binary segmentation mask ($H \times W$, boolean/uint8).
  - Predicted mask IoU confidence score (stability score).
* **Role After Grounding DINO**:
  - Grounding DINO yields rectangular bounds; SAM ViT-B refines these into exact pixel-level contours for verifiable visual evidence (e.g., precise ship hull outlines, storage tank perimeters).
* **Why ViT-B is Preferred Over ViT-L / ViT-H for MVP**:
  - ViT-B (~91M parameters, ~375 MB file) requires ~1.5 GB – 2.0 GB VRAM.
  - ViT-H (~636M parameters, ~2.5 GB file) requires $> 6.5$ GB VRAM, which would consume the entire RTX 5050 budget by itself.
  - ViT-B achieves near-identical boundary delineation for man-made overhead infrastructure when guided by high-quality box prompts.

---

## 5. Bi-Temporal Change Detection Engine

### 5.1 Primary Model: BIT-CD (Bitemporal Image Transformer for Change Detection)
* **Official Repository**: `justchenhao/BIT_CD` (GitHub / Chen & Shi, 2021)
* **Model Architecture**:
  - Dual-stream Siamese CNN backbone (ResNet-18) for high-resolution spatial feature extraction across timestamps $T_1$ and $T_2$.
  - Bitemporal Image Transformer (BIT) encoder-decoder modeling spatiotemporal context and differential token correlations.
  - Lightweight prediction head producing differential change maps.
* **Expected Inputs**: Two registered optical images: Image $T_1$ and Image $T_2$ ($3 \times H \times W$ each).
* **Expected Outputs**: Binary change probability map / mask ($1 \times H \times W$) where pixel value $\ge 0.5$ denotes significant semantic change.
* **Pretrained Checkpoint Situation**: Community and author checkpoints trained on standard benchmarks: `LEVIR-CD`, `WHU-CD`, and `SYSU-CD`.
* **Known Legacy Dependency Constraints**:
  - Original implementation was authored against legacy PyTorch 1.7 – 1.9 and torchvision 0.8 – 0.10.
  - May invoke deprecated tensor operations (`torch.meshgrid` indexing syntax, older autograd conventions).
* **Compatibility Risk with Modern Python / PyTorch**: **HIGH**. Running legacy code directly on modern Python 3.10+ with modern PyTorch on next-gen hardware poses import, compilation, and CUDA kernel risks.
* **Fallback Plan**:
  - *Fallback A (Modernized BIT-CD)*: Refactor the compact BIT architecture into clean, modern PyTorch 2.x code utilizing `torch.nn.TransformerEncoder` without legacy package dependencies.
  - *Fallback B (Siamese Difference U-Net)*: Utilize a clean Siamese ResNet/U-Net difference architecture pre-trained on LEVIR-CD from modern segmentation libraries (e.g., `segmentation_models_pytorch` or `ChangeFormer`).
* **Critical Rule**: **Do not claim compatibility until the environment and checkpoints are physically tested.**

---

## 6. Optical + SAR Paired Analysis Engine

### 6.1 Primary Baseline: Dual-Stream U-Net / Lightweight Optical-SAR Fusion
* **Separate Optical and SAR Branches**:
  - *Optical Stream*: Ingests 3-channel RGB optical imagery ($3 \times H \times W$).
  - *SAR Stream*: Ingests 1-channel or 2-channel calibrated Synthetic Aperture Radar backscatter (e.g., Sentinel-1 GRD VV/VH amplitudes, normalized to decibel scale $\text{dB} \in [-30.0, 0.0]$).
* **Feature Fusion Concept**:
  - Mid-level feature fusion: Multi-scale convolutional feature maps from optical and SAR encoders are concatenated and passed through cross-attention fusion blocks.
  - Allows radar surface roughness and metallic specular bounce signatures to penetrate optical cloud cover or shadow occlusions.
* **Expected Inputs**: Co-registered Optical image ($3 \times H \times W$) + SAR amplitude tensor ($C_{SAR} \times H \times W$).
* **Expected Outputs**:
  - Binary/multiclass feature mask (e.g., water boundary delineation, vessel detection under clouds, permanent road corridors).
  - Cross-modal agreement index (percentage consistency between optical and radar signatures).
* **Evidence Visualization**:
  - Color-coded overlay displaying SAR high-backscatter signatures mapped directly over the optical base layer, highlighting structures invisible in optical RGB.
* **Why Lightweight Fusion is Preferred for Hackathon MVP**:
  - Small model size (~15M – 25M parameters), consuming $< 1.0$ GB VRAM.
  - Fast forward pass ($< 200$ ms), ideal for interactive hackathon evaluations.
  - Transparent mathematical formulation (backscatter contrast + spectral reflectance) easily explained to jury.
* **Reference Literature**: Schmitt et al. (SEN1-2 dataset); SpaceNet 6 Multi-Sensor All-Weather Mapping benchmark.
* **License & Implementation Risks Requiring Verification**:
  - Open-source weights for dual-stream optical-SAR fusion often use research-only licenses.
  - Radiometric calibration differences between SAR sensors (e.g., TerraSAR-X vs. Sentinel-1) require strict input normalization.

---

## 7. BigEarthNet Adaptation Strategy

### 7.1 Dataset Overview & Role
* **BigEarthNet v2.0**: The premier multi-modal Earth Observation benchmark comprising paired Sentinel-2 (multispectral) and Sentinel-1 (dual-pol SAR) tiles covering diverse land-cover categories across Europe.
* **Sentinel-1 / Sentinel-2 Relationship**: Provides spatially co-registered, temporally proximate optical and microwave observations of identical geographic footprints.
* **Role in SatQuery**: Provides the domain grounding for tuning the Optical-SAR fusion head and aligning remote-sensing visual representations.

### 7.2 Hackathon Dataset Scope Constraint
* **Total Dataset Size**: $> 100$ GB compressed (~590,000 paired image patches).
* **Decision**: **We will NOT download the entire BigEarthNet dataset for the hackathon.**
* **Proposed Development Subset**: A curated, lightweight development package consisting of **500 to 1,000 paired patches** representing 4 key evaluation categories:
  1. Maritime Ports & Coastal Water (vessel & water boundary verification).
  2. Dense Urban Infrastructure (building footprints under varying conditions).
  3. Agricultural & Rural Basins (vegetation & soil moisture backscatter).
  4. Inland Water Reservoirs & River Basins (flood and drainage tracking).

### 7.3 PEFT / LoRA Adaptation Strategy
* Base visual backbone weights are frozen.
* Low-Rank Adaptation (LoRA) matrices ($r=8$ or $r=16$, $\alpha=16$) are injected into projection layers.
* Only the adapter parameters ($\sim 0.5\% - 1.5\%$ of total weights) are tuned.
* **Hardware Constraints on RTX 5050 (8 GB)**:
  - Batch size: $\le 4$ with gradient accumulation steps ($= 4$).
  - Mixed Precision: `torch.cuda.amp.autocast(dtype=torch.bfloat16)`.
  - Patch Dimension: Standardized to $256 \times 256$ or $512 \times 512$ patches.
* **Success Criteria for Proving Adaptation**:
  - Stable cross-entropy loss convergence on the 1,000-patch validation set.
  - Statistically significant improvement in land-use classification accuracy over zero-shot base models on the evaluation subset.
  - *No synthetic or unverified metrics will be published.*

---

## 8. Agent Router Specification

### 8.1 Architecture: Deterministic Guardrailed Router
The Agent Router is designed as a **deterministic, rule-and-intent router** rather than an autonomous unconstrained LLM agent.

```
Incoming Request (Query Text + Asset Metadata)
                    │
                    ▼
       [Input Asset Constraint Guard]
       ├── Asset Count = 1 ──> Allowed: {rs_vqa, captioning, grounding}
       ├── Asset Count = 2 (Temporal) ──> Allowed: {temporal_change}
       └── Asset Count = 2 (Optical + SAR) ──> Allowed: {optical_sar}
                    │
                    ▼
       [Intent Classification Engine]
       ├── Matches Localization Patterns ("find", "locate", "detect", "where") ──> grounding
       ├── Matches Scene Patterns ("describe", "overview", "caption") ──────────> captioning
       ├── Matches Change Patterns ("difference", "changed", "before and after") ──> temporal_change
       ├── Matches Multi-Sensor Patterns ("radar", "sar", "through clouds") ────> optical_sar
       └── General / Numerical / Relational Questions ──────────────────────────> rs_vqa
                    │
                    ▼
       [Registry Schema Validation]
       ├── Validate tool exists in Model Registry
       └── Validate parameters within bounded range
                    │
                    ▼
       [Dispatch to Specialist AI Tool]
```

### 8.2 Supported Task Types & Registry Mapping
| Task Type | Registry `model_id` | Primary Trigger Criteria |
| :--- | :--- | :--- |
| `SINGLE_VQA` | `rs_vqa` | Single image + analytical, counting, or attribute query |
| `SCENE_CAPTIONING` | `captioning` | Single image + broad scene summary or description query |
| `VISUAL_GROUNDING` | `grounding` + `segmentation` | Single image + target object localization query |
| `BI_TEMPORAL_CHANGE`| `temporal_change` | Registered $T_1, T_2$ pair + change detection query |
| `OPTICAL_SAR` | `optical_sar` | Co-registered Optical and SAR pair + cross-sensor query |

### 8.3 Permitted Parameters & Validation Before Execution
* `box_threshold`: float $\in [0.10, 0.90]$
* `text_threshold`: float $\in [0.10, 0.90]$
* `max_tokens`: int $\in [32, 512]$
* `temperature`: float $\in [0.0, 0.7]$ (strict bounds to minimize linguistic hallucination)
* Any parameter submitted outside permitted ranges is rejected before model invocation.

### 8.4 Fallback Behavior
* If the user query is ambiguous, the router selects `rs_vqa` with a low-certainty flag and prompts the user for clarification.
* If query intent conflicts with input assets (e.g., change query requested on 1 image), the router aborts with diagnostic error `INPUT_PAIRING_REQUIRED`.

### 8.5 Observable Trace Fields
Every execution produces a structured log containing:
* `trace_id`: UUID
* `timestamp`: ISO-8601
* `input_assets`: `[{"asset_id": ..., "modality": ..., "dimensions": ...}]`
* `detected_intent`: TaskEnum
* `selected_tool`: Tool ID
* `permitted_parameters`: Key-value map
* `stage_latencies_ms`: Breakdown of validation, routing, inference, and evidence generation
* `confidence_summary`: Calibrated metric
* `status`: `SUCCESS` or `FAILED`

---

## 9. Predefined Model Registry Schema

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class TaskType(str, Enum):
    RS_VQA = "rs_vqa"
    CAPTIONING = "captioning"
    GROUNDING = "grounding"
    SEGMENTATION = "segmentation"
    TEMPORAL_CHANGE = "temporal_change"
    OPTICAL_SAR = "optical_sar"

class ModalityType(str, Enum):
    OPTICAL_RGB = "optical_rgb"
    OPTICAL_MULTISPECTRAL = "optical_multispectral"
    SAR_GRD = "sar_grd"
    DUAL_TEMPORAL = "dual_temporal"
    OPTICAL_SAR_PAIR = "optical_sar_pair"

class ModelStatus(str, Enum):
    REGISTERED_UNVERIFIED = "registered_unverified"
    VERIFIED_READY = "verified_ready"
    FALLBACK = "fallback"

class ModelRegistryEntry(BaseModel):
    model_id: str
    task: TaskType
    modality: ModalityType
    input_types: List[str]
    output_types: List[str]
    checkpoint: str
    version: str
    permitted_parameters: Dict[str, Dict[str, Any]]
    resource_requirements: Dict[str, Any]
    confidence_fields: List[str]
    evidence_fields: List[str]
    status: ModelStatus
```

### Predefined Model Registry Catalog
| `model_id` | Task | Modality | Checkpoint Reference | Permitted Parameters | Resource Target | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rs_vqa` | `RS_VQA` | `OPTICAL_RGB` | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | `max_tokens` ($32-512$), `temperature` ($0.0-0.5$) | $\le 3.5$ GB VRAM (4-bit) | `REGISTERED_UNVERIFIED` |
| `captioning` | `CAPTIONING` | `OPTICAL_RGB` | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | `max_tokens` ($64-256$), `temperature` ($0.0-0.7$) | $\le 3.5$ GB VRAM (4-bit) | `REGISTERED_UNVERIFIED` |
| `grounding` | `GROUNDING` | `OPTICAL_RGB` | `groundingdino_swint_ogc.pth` | `box_threshold` ($0.1-0.9$), `text_threshold` ($0.1-0.9$) | $\le 1.2$ GB VRAM | `REGISTERED_UNVERIFIED` |
| `segmentation` | `SEGMENTATION` | `OPTICAL_RGB` | `sam_vit_b_01ec64.pth` | `multimask_output` (bool) | $\le 2.0$ GB VRAM | `REGISTERED_UNVERIFIED` |
| `temporal_change` | `TEMPORAL_CHANGE` | `DUAL_TEMPORAL`| `bit_cd_levir.pth` (or modern fallback) | `threshold` ($0.3-0.7$) | $\le 1.5$ GB VRAM | `REGISTERED_UNVERIFIED` |
| `optical_sar` | `OPTICAL_SAR` | `OPTICAL_SAR_PAIR`| `dualstream_fusion_baseline.pth` | `fusion_weight` ($0.1-0.9$) | $\le 1.0$ GB VRAM | `REGISTERED_UNVERIFIED` |

---

## 10. Memory & GPU Management Policy

### 10.1 Practical VRAM Target
* **Available Hardware**: 8.0 GB GDDR7 (GeForce RTX 5050 Laptop).
* **Operational Ceiling**: **6.5 GB**. Any single inference pipeline must not allocate more than 6.5 GB of peak GPU memory.

### 10.2 Sequential Execution (One Heavy Model at a Time)
* SatQuery AI executes specialist models **sequentially, never concurrently**.
* When executing a Grounding $\to$ Segmentation sequence:
  1. Load Grounding DINO in memory ($\sim 1.2$ GB).
  2. Compute bounding boxes and output tensor to CPU memory.
  3. Load SAM ViT-B ($\sim 2.0$ GB) to compute segmentation masks.
  4. Grounding DINO + SAM ViT-B together peak at $\le 3.5$ GB, well within limits.
* When switching to/from the 3B VLM:
  - If VRAM is constrained, explicitly invoke `torch.cuda.empty_cache()` and Python `gc.collect()`.

### 10.3 Precision & Quantization Policy
* **VLM**: Evaluated with 4-bit NormalFloat (NF4) or AWQ quantization to reduce parameter weight memory from 6.2 GB to ~3.0 GB.
* **Grounding DINO & SAM**: Evaluated in native `float16` or `bfloat16`.
* **BIT-CD & Fusion Head**: Evaluated in `float16` or `float32`.

### 10.4 Image Tiling & Resizing Strategy
* **Input Resolution Cap**: Full images larger than $1024 \times 1024$ pixels are downscaled or tiled into $512 \times 512$ patches to prevent activation tensor blowup.
* High-resolution GeoTIFFs are ingested via sliding-window inference with 15% overlap.

### 10.5 OOM Guardrail & Warm-Up Strategy
* **OOM Interceptor**: Wrap all model forward passes in a `try...except torch.cuda.OutOfMemoryError` handler. On trigger:
  1. Call `torch.cuda.empty_cache()`.
  2. Automatically downscale input image by 50%.
  3. Rerun forward pass or fall back to CPU execution.
* **Warm-Up Pass**: On system initialization, execute a dummy single-tensor pass through active models to compile execution graphs and initialize CUDA memory buffers before user queries are accepted.

---

## 11. Model Validation Plan

| Model | Task | Checkpoint | VRAM Risk | Dependency Risk | License Risk | Verification Method | Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AdaptLLM-Qwen2.5-VL-3B** | RS VQA & Captioning | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | Medium (3-6 GB) | Low (Hugging Face `transformers`) | Low (Apache 2.0 / Open) | Single forward pass on 1024x1024 overhead image in 4-bit | GeoChat-7B (quantized) or API |
| **Grounding DINO-T** | Visual Grounding | `groundingdino_swint_ogc.pth` | Low (~1.2 GB) | Medium (CUDA C++ operator compilation) | Low (Apache 2.0) | Verify forward pass with 5 text labels on DOTA sample | Hugging Face Transformers native implementation |
| **SAM ViT-B** | Visual Evidence Segmentation | `sam_vit_b_01ec64.pth` | Low (~2.0 GB) | Low (Pure PyTorch) | Low (Apache 2.0) | Verify box-prompted mask generation on test tile | Direct Bounding Box evidence (skip mask) |
| **BIT-CD** | Bi-temporal Change | `bit_cd_levir.pth` | Low (~1.5 GB) | **High** (Legacy PyTorch 1.x codebase) | Low (Research Open Source) | Standalone Python 3.10+ execution script testing pair inference | Modernized PyTorch 2.x BIT or Siamese Diff U-Net |
| **Dual-Stream Fusion** | Optical-SAR Analysis | `dualstream_fusion_baseline.pth` | Low (<1.0 GB) | Low (Custom PyTorch module) | Low (MIT / Academic) | Verify joint forward pass on paired optical-SAR sample | Feature-difference SAR backscatter thresholding |

---

## 12. Problem Statement Coverage Matrix

| PS Mandatory Capability | SatQuery Architectural Component | Primary AI Model | Visual Evidence Artifact | Confidence Information | Observable Trace Fields |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Single-Image VQA** | RS VQA Engine | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | Visual attention map / scene highlight | Linguistic token certainty score | `intent: SINGLE_VQA`, model latency, token confidence |
| **2. Single-Image Capability (Grounding / Captioning)** | Grounding & Captioning Engine | `Grounding DINO-T` + `SAM ViT-B` / `AdaptLLM-3B` | 2D Bounding Boxes & pixel-level contour masks | Box detection score & mask stability IoU | `intent: VISUAL_GROUNDING`, detected targets, box coordinates |
| **3. Bi-Temporal Change Understanding** | Change Detection Engine | `BIT-CD` (or Modernized Siamese Fallback) | Color-coded difference heatmap & binary change mask | Change segmentation probability | `intent: BI_TEMPORAL_CHANGE`, dual image validation, change % |
| **4. Optical-SAR Paired Analysis** | Cross-Modal Fusion Engine | Dual-Stream Optical-SAR Fusion Baseline | SAR backscatter overlay on optical scene | Multi-sensor cross-modal agreement index | `intent: OPTICAL_SAR`, radar channel status, feature synergy |
| **5. Remote-Sensing Adaptation** | Domain Adaptation Layer | `AdaptLLM` + BigEarthNet LoRA Adapters | Domain-tuned visual features | Calibrated domain uncertainty score | LoRA adapter status, GSD parameter alignment |
| **6. Agentic Task/Model Selection** | Deterministic Agent Router | Guardrailed Intent Engine + Model Registry | Dynamic pipeline execution path | Task routing confidence | `selected_tool`, permitted parameters, routing justification |
| **7. Input Compatibility Validation** | Ingestion & Validation Gateway | Deterministic Tensor Validator | Diagnostic validation status report | Pre-inference validity check ($1.0$ or $0.0$) | Format check, dimension check, pair alignment status |
| **8. Visual Evidence** | Evidence Builder | `EvidenceBuilder` (OpenCV, NumPy) | Overlaid canvas layers (boxes, masks, heatmaps) | Feature-level confidence scores | Evidence layer count, coordinate payloads, render time |
| **9. Confidence Information** | Confidence Estimator | Statistical Calibrator | Normalized certainty badge ($0.0 - 1.0$) | Calibrated multi-modal score | Raw model logit, threshold flag, uncertainty advisory |
| **10. Observable Execution Trace** | Trace Engine | Structured Audit Logger | Step-by-step audit drawer on UI | Per-stage status and latency counters | Complete audit JSON envelope |

---

## 13. AI Architecture Risks & Mitigations

| Risk | Technical Implication | Mitigation Strategy |
| :--- | :--- | :--- |
| **RTX 5050 VRAM Limitations (8 GB)** | Exceeding 8 GB triggers immediate CUDA OOM crashes during inference. | Enforce 4-bit quantization for VLM, sequential tool execution, and $1024 \times 1024$ image tiling. |
| **Next-Gen GPU / CUDA / PyTorch Compatibility** | GeForce RTX 50-series (Blackwell architecture) requires cutting-edge CUDA and PyTorch builds. Older binaries will fail to initialize. | Verify physical GPU compute capability first; do not lock CUDA versions prematurely; provide CPU fallback mode. |
| **Legacy BIT-CD Dependencies** | Original 2021 codebase relies on deprecated PyTorch functions that fail on modern Python 3.10+. | Modernize the architecture into pure PyTorch 2.x or switch to modern Siamese Difference baseline. |
| **VLM Hallucination on Low-GSD Rasters** | Model answers questions about objects smaller than the spatial resolution allows. | Prompt templates inject GSD constraints; confidence $< 0.40$ triggers an explicit uncertainty warning. |
| **Grounding False Positives in Cluttered Scenes** | Grounding DINO may trigger false positives on visual clutter resembling target infrastructure. | Pair Grounding DINO with SAM mask verification; enforce high `box_threshold` ($\ge 0.35$). |
| **SAR-Optical Spatial Misalignment** | Differences in viewing geometry (SAR side-looking vs. optical nadir) create false change signals. | Restrict MVP evaluations to pre-registered, orthorectified image pairs. |
| **Insufficient Training Data during Hackathon** | Lack of labeled remote-sensing data impairs from-scratch training. | Rely on zero-shot/few-shot pre-trained models; adapt only small LoRA layers on curated subsets. |
| **Dataset & Checkpoint Licensing** | Incompatible research-only licenses may violate hackathon presentation guidelines. | Enforce Apache 2.0 / MIT / Open-access licenses across all registered checkpoints. |
| **Inference Latency Exceeding Demo Tolerances** | Multi-second model load times degrade live evaluator experience. | Keep models warm in memory; use lightweight backbones (Swin-T, ViT-B, 3B VLM). |
| **Model Download Size & Venue Network Bottlenecks** | Multi-gigabyte model downloads during hackathon will fail over venue Wi-Fi. | Download and cache all verified weights locally prior to the competition. |

---

## 14. Phase 3 Model Decision

### Summary of Decisions
* **Primary Models**:
  - RS VQA & Captioning: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
  - Visual Grounding: `Grounding DINO-T` (`groundingdino_swint_ogc.pth`)
  - Visual Evidence Segmentation: `SAM ViT-B` (`sam_vit_b_01ec64.pth`)
* **Backup Models**:
  - `MBZUAI/geochat-7B` (held as reference/cloud fallback; not primary due to 8 GB VRAM budget).
* **Models Requiring Compatibility Testing**:
  - `BIT-CD` (requires PyTorch 2.x compatibility test; fallback to Modernized Siamese Diff U-Net if legacy issues arise).
  - `Grounding DINO-T` (requires verification of C++/CUDA operator build on the RTX 5050).
* **Models Requiring Adaptation**:
  - Dual-Stream Optical-SAR Fusion Baseline (adaptation on 1,000-patch BigEarthNet development subset).
* **Models that Must NOT Be Downloaded Yet**:
  - Large 7B+ models (`geochat-7B`, `Qwen2.5-VL-7B`).
  - SAM ViT-Large / ViT-Huge (`sam_vit_l`, `sam_vit_h`).
  - Full BigEarthNet v2.0 dataset (100+ GB download strictly prohibited).
  - Any model checkpoint before local environment verification in Phase 4.

---

## 15. VLM Hardware Validation

### 15.1 Physical Environment Baseline
* **GPU**: NVIDIA GeForce RTX 5050 Laptop GPU
* **Total VRAM**: ~8,151 MB (~8.0 GB GDDR7)
* **Initial Free VRAM (Idle)**: ~7,070 MB
* **Hardware BF16 Compute Support**: `True` (native bfloat16 accelerated)
* **Host Python Environment**: Windows, Python 3.12 (`.venv`), PyTorch CUDA build

### 15.2 Validation Protocol (`ai/evaluation/test_vlm_loading.py`)
To prevent unverified assumptions regarding VRAM limits, a controlled hardware feasibility test script has been created at `ai/evaluation/test_vlm_loading.py`.

* **Target Checkpoint**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Loading Configuration**:
  - `Qwen2_5_VLForConditionalGeneration` with `torch_dtype="auto"` and `device_map="auto"`
  - `AutoProcessor` configured with a conservative visual token budget:
    - `min_pixels = 256 * 28 * 28` (~200,704 px)
    - `max_pixels = 512 * 28 * 28` (~401,408 px)
  - FlashAttention is disabled for this baseline feasibility phase.
* **Controlled Inference Pass**:
  - Ingests a programmatically generated, temporary synthetic remote-sensing tile.
  - Submits the standardized domain prompt: *"What objects or land-cover features are visible in this image?"*
  - Generates a short answer constrained to `max_new_tokens = 64`.

### 15.3 Memory Profiling & Feasibility Assessment
* **Approximate VRAM Footprint**:
  - Unquantized 16-bit parameter weights require ~6.0 – 6.5 GB. Given ~7,070 MB free at idle, running 16-bit unquantized operates near the critical memory boundary.
  - If dynamic activation buffers exceed the remaining ~500–1,000 MB during forward pass generation, CUDA Out-Of-Memory (`torch.cuda.OutOfMemoryError`) will occur.
* **OOM & Offloading Policy**:
  - The validation script traps CUDA OOM exceptions explicitly (`VLM_GPU_OOM`), documents the exact stage where failure occurred, and triggers garbage collection to restore VRAM stability.
  - If unquantized loading triggers OOM or excessive CPU offload, the model will transition to a 4-bit / 8-bit quantized loading strategy before pipeline integration.
* **Full-GPU Deployment Verdict**:
  - **Status**: Subject to live verification via `python ai/evaluation/test_vlm_loading.py`.
  - Full-GPU deployment is deemed feasible **only if** total allocated + reserved memory during both loading and generation remains strictly below **7.0 GB** without triggering CPU offloading.

> [!IMPORTANT]
> A successful model load and single forward pass indicates only hardware feasibility on this local machine. It does **not** prove that the model is production-ready for arbitrary high-resolution multi-spectral satellite rasters or concurrent multi-tool workflows.

---

## 16. VLM Real Satellite Validation

### 16.1 Validation Scope & Purpose (Phase 3D)
To evaluate the remote-sensing conversational and visual reasoning capabilities of `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` on authentic Earth Observation data (rather than synthetic patterns), a real satellite image VQA evaluation protocol is implemented via [`ai/evaluation/test_real_satellite_vqa.py`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/ai/evaluation/test_real_satellite_vqa.py).

### 16.2 Real Satellite Test Asset
* **Asset Location**: `data/samples/sample_satellite_port.jpg`
* **Source**: NASA Earth Observatory (Image Record 152192: *Sediments and Ships in Rio Grande*)
* **Mission / Sensor**: Landsat 9 Operational Land Imager-2 (OLI-2), natural color composite
* **Dimensions**: $720 \times 480$ pixels (JPEG, 62 KB)
* **Licensing**: Public Domain (USGS / NASA Earth Observatory open data policy)
* **Geographic / Semantic Features**: Coastal maritime inlet, channel breakwaters / jetties, turbid sediment plumes, deep coastal water, sandy barrier islands, and adjacent urban port infrastructure.

### 16.3 Evaluation Questions
Four sequential domain queries are posed to the resident model without reloading weights:
1. *"What type of land cover or environment is visible in this satellite image?"*
2. *"What major objects or structures are visible?"*
3. *"Are there signs of roads, buildings, vegetation, water, or bare land? Describe only what is visually supported."*
4. *"Give a concise scene description of this satellite image."*

### 16.4 Execution & Hardware Policy
* **Loading**: `Qwen2_5_VLForConditionalGeneration` with `device_map="auto"`, `torch_dtype="auto"`.
* **Visual Tokens**: `min_pixels = 256 * 28 * 28`, `max_pixels = 512 * 28 * 28`.
* **Generation Constraint**: `max_new_tokens = 100`, greedy decoding (`do_sample = False`).
* **VRAM Monitoring**: Explicit pre- and post-inference memory profiling per question.
* **Results Reference**: Complete answers, latencies, and memory metrics are cataloged in [`docs/results/real_satellite_vqa_results.md`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/real_satellite_vqa_results.md).

---

## 17. VQA Tool Integration (Phase 5A)

### 17.1 Concrete Executor Architecture
The remote-sensing VQA capability validated in Phase 3 is wrapped in a dedicated, isolated execution module: [`ai/inference/vqa.py`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/ai/inference/vqa.py).

* **Model Checkpoint**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Calling Contract**: `run_vqa(image_path: str, query: str, permitted_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
* **Service Integration**: Connected to [`backend/app/services/analysis_service.py`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/backend/app/services/analysis_service.py) behind the `AgentRouter`.
* **Execution Flow**: `AnalysisRequest` $\to$ Input Validation $\to$ `AgentRouter` (`VQA`) $\to$ `run_vqa` $\to$ `ToolResult` + `ExecutionTraceEntry`.

### 17.2 Resource Policy & Evidence Constraints
* **On-Demand Residency**: The VLM is loaded dynamically and purged from GPU memory in a deterministic `finally` block, releasing VRAM back to $\sim 7.0$ GB idle.
* **Evidence Strategy**: Returns factual metadata (file reference, native dimensions, query, and latencies). No fabricated bounding boxes or masks are generated.
* **Confidence Handling**: Confidence is strictly returned as `null` (`None`) until the formal confidence calibration pipeline is activated.
* **Full Specification**: See [`docs/model-execution.md`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/model-execution.md) for full telemetry schemas, error handling matrices, and observable trace details.

---
*End of AI Model Specification.*
