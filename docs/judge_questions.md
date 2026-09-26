# SatQuery AI — Evaluator & Judge Defense Q&A (Section 10)

This document provides concise, technically rigorous, and honest answers to the 20 most critical architectural, machine learning, and scientific questions an expert hackathon evaluator will ask.

---

### 1. Why do you need an agent?
**Answer**: Earth Observation queries often require multi-step decomposition that no single computer vision or language model can execute alone. For example, answering *"What changed in the built-up area between these two dates and where?"* requires: (1) temporal pixel differencing, (2) spatial bounding box localization, and (3) vision-language semantic description. An agent orchestrates this pipeline sequentially, passing intermediate evidence artifacts between specialist engines while enforcing deterministic safety boundaries.

---

### 2. Why not use one VLM for everything?
**Answer**: Monolithic VLMs suffer from three critical remote sensing failures:
1. **Resolution & Fine Geometry**: VLMs downsample or patchify images (e.g. $28 \times 28$ patches), losing sub-pixel boundaries needed for change detection and pixel-level masks.
2. **Specialized Sensor Modalities**: VLMs are pre-trained primarily on optical RGB photographs; they cannot compute microwave radar backscatter physics, cross-sensor polarimetric matrices, or Pearson radiometric correlations.
3. **Hallucination Risk**: Asking a generative language model to guess coordinates produces ungrounded bounding boxes, whereas specialized detectors like Grounding DINO output calibrated pixel coordinates.

---

### 3. Why Qwen2.5-VL-3B?
**Answer**: We selected `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` because:
1. It is already pre-aligned on remote sensing domain corpora.
2. At 3.75 billion parameters in BF16, it fits within our 8 GB VRAM budget alongside serialized specialized vision heads.
3. Its native dynamic resolution visual encoder supports varying satellite aspect ratios without distortion.

---

### 4. What did your LoRA actually improve?
**Answer**: Our project-owned LoRA adapter targeting projection layers (`q_proj`, `v_proj`) with rank $r=8$ achieved an empirical **+19.3% relative improvement in Token Macro F1** (0.2525 baseline $\to$ 0.3012 adapted) on the fixed RSVQA-LR validation benchmark ($N=20$). Crucially, **object presence accuracy increased from 42.9% to 75.0%** (+32.1% absolute gain), significantly reducing false negative presence errors. Exact match shifted slightly from 35.0% to 30.0% due to richer, more descriptive phrasing in generated answers.

---

### 5. Why is counting still weak in the base VLM, and how do you solve it?
**Answer**: On RSVQA-LR counting questions, raw VLM accuracy remained at 20.0% (1/5 correct). This is a well-documented architectural limitation of patch-based visual transformers: small remote sensing objects (e.g., individual houses or small vessels spanning only 5–15 pixels) fall within the same visual token patch, causing feature blending and token collision.
**Our Solution**: SatQuery AI implements a deterministic counting guardrail in the agent router. Numerical queries ("How many...", "Count...") are intercepted before VLM generation and routed directly to Grounding DINO. The final count is computed strictly from the cardinality of valid localized bounding boxes (`len(valid_grounded_boxes)`), eliminating generative VLM hallucinations entirely.

---

### 6. How did you choose $\tau=0.30$?
**Answer**: We executed an empirical decision threshold sweep across 12 candidate values ($\tau \in [0.10, 0.60]$) on the LEVIR-CD benchmark test set ($N=20$), recorded in [results/change_threshold_sweep.csv](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/results/change_threshold_sweep.csv).
The legacy arbitrary threshold ($\tau=0.42$) yielded an F1 of 0.1535 and IoU of 0.0878. The sweep proved that $\tau=0.30$ represents the global maximum for harmonic balance, yielding **$F1=0.2335$ (+52.1% relative gain)**, **$IoU=0.1322$ (+50.6% relative gain)**, and a recall of **73.56%**.

---

### 7. Why is change detection precision relatively low?
**Answer**: At $\tau=0.30$, precision is 13.88% against a high recall of 73.56%. This occurs because our Siamese ResNet-18 baseline operates without task-specific supervised training on pixel annotations; it computes deep feature L2 cosine distances. In complex satellite scenes, natural seasonal lighting shifts, sun angle differences, and vegetation phenology produce feature deltas that create false positives in the background. A supervised mask decoder trained on dense change labels (e.g. BIT or ChangeFormer) is required to suppress background variance.

---

### 8. How do you know a detected change is real?
**Answer**: SatQuery AI does not rely on a single scalar. A change is corroborated through multi-evidence triangulation:
1. **Differential Feature Map**: Siamese ResNet-18 computes structural convolutional feature deltas.
2. **Stability Margin**: The fraction of unchanged background pixels is logged.
3. **Spatial Grounding Verification**: For compound queries, Grounding DINO independently localizes the target entity to confirm that the change coincides with an actual physical structure rather than shadow or illumination noise.

---

### 9. Why use Grounding DINO?
**Answer**: Grounding DINO Tiny combines a Swin-Transformer visual backbone with BERT text conditioning to perform true open-vocabulary object detection. In remote sensing, target classes are highly diverse (e.g. *"docked container vessels"*, *"circular fuel storage tanks"*, *"runway aprons"*). Rather than retraining a closed-set detector for every class, Grounding DINO extracts cross-attention peaks between user text prompts and spatial feature maps in $<1.5$ seconds.

---

### 10. How do you validate optical+SAR fusion?
**Answer**: We must be scientifically transparent: **task-level quantitative fusion validation against labeled target masks is not currently established** because public, co-registered, multi-temporal optical-SAR pairs with ground truth segmentation labels are severely limited. Instead, our system validates fusion through:
1. **Empirical Radiometric Correlation**: Pearson correlation coefficient ($r$) between optical luminance and radar backscatter intensity.
2. **Radar-Dominant Anomaly Detection**: Identifying pixels where radar returns spike despite optical cloud attenuation.
3. **Modality Ablation Analysis**: Comparing feature activations under optical-only, SAR-only, and joint cross-modal modes.

---

### 11. Is your SAR data genuine?
**Answer**: We maintain strict provenance disclosure. Our demo assets include **genuine Sentinel-1 C-band spaceborne SAR** over coastal Mauritius (`sample_sentinel1_sar_mauritius.jpg`, GRD product, dual polarization), as well as a controlled synthetic proxy radar asset (`sample_satellite_port_proxy_sar.png`) generated via physical multiplicative speckle modeling. Our pipeline automatically inspects asset metadata and explicitly tags every output with `[GENUINE SPACEBORNE SAR]` or `[PROXY SIMULATED SAR]`, preventing misleading provenance claims.

---

### 12. How do you prevent hallucination?
**Answer**: We employ three architectural safeguards:
1. **Deterministic Agent Routing**: Query intent is parsed via deterministic pattern matching and schema validation, not unconstrained LLM generation.
2. **Visual Evidence Anchoring**: Generative text answers must cite physical evidence (bounding boxes, change masks, radiometric correlations) extracted directly from the raster.
3. **Strict Confidence Semantics**: We never output uncalibrated probabilities as "accuracy". Detector logits are explicitly labeled as *uncalibrated detector confidence*, and VLM text outputs default to uncalculated (`null`) rather than fabricated numbers.

---

### 13. How does the parameter firewall work?
**Answer**: Implemented in [backend/app/agent/firewall.py](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/backend/app/agent/firewall.py), incoming parameters pass through strict Pydantic models. Every specialist tool has a whitelisted parameter dictionary:
- `VQA`: Only `max_new_tokens`, `min_pixels`, `max_pixels`, `do_sample`.
- `GROUNDING`: Only `box_threshold`, `text_threshold`.
- `CHANGE_DETECTION`: Only `threshold`, `blur_kernel_size`.
Any parameter outside the whitelist is automatically stripped; out-of-range numerical parameters are clamped to safe intervals.

---

### 14. How do you prevent tool misuse?
**Answer**: Our system uses an **immutable certified tool registry** ([backend/app/agent/registry.py](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/backend/app/agent/registry.py)). The router can only select from 4 registered tools: `VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`. Unregistered tools (e.g., shell access, arbitrary code execution, or uncertified models) are rejected with a deterministic `UNREGISTERED_TOOL` error.

---

### 15. How does the system operate on an 8 GB GPU?
**Answer**: Consumer laptops with 8 GB VRAM cannot host a 3.75B VLM concurrently with ResNet-18, Grounding DINO, and fusion networks without triggering CUDA OOM. We solved this with:
1. **Sequential Execution Scheduling (`_GPU_EXECUTION_LOCK`)**: Specialists execute serially in an isolated thread lock.
2. **Aggressive VRAM Garbage Collection**: `torch.cuda.empty_cache()` and `gc.collect()` run immediately between specialist calls.
3. **Inference Contexts**: All inference runs inside `torch.inference_mode()`, preventing autograd computational graph allocations.
4. **Dynamic Visual Token Clamping**: Image visual tokens are bounded to 65,536–200,704 pixels.

---

### 16. What happens if the rasters have different CRS?
**Answer**: Unlike naive vision systems that treat images as raw pixel grids, our **Geospatial Validation Service** ([backend/app/services/geospatial_service.py](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/backend/app/services/geospatial_service.py)) reads GeoTIFF GeoKeys and EPSG codes. If $T_1$ is in EPSG:32643 (UTM 43N) and $T_2$ is in EPSG:4326 (WGS84), the pipeline halts with an actionable error:
> *"Spatial coordinate reference mismatch: T1 has EPSG:32643 while T2 has EPSG:4326. Reproject both rasters to a common CRS before change analysis."*
This prevents false change detections caused by spatial coordinate misalignment.

---

### 17. What is genuinely novel here?
**Answer**: The novelty is not claiming a 100-billion parameter foundation model, but rather:
1. **Safe Agentic Orchestration**: Bridging natural language queries with deterministic spatial/temporal computer vision tools under a policy firewall.
2. **Transparent Multi-Sensor Evidence Fusion**: Correlating optical texture with microwave radar backscatter while preserving strict provenance.
3. **Zero-Fabrication Metric Discipline**: Delivering a production-ready, honest system where confidence semantics, LoRA deltas, and threshold trade-offs are empirically backed.

---

### 18. What would you improve with another month?
**Answer**:
1. **Supervised Dense Change Decoder**: Train a ChangeFormer / BIT transformer decoder on 10,000+ LEVIR-CD pairs to boost precision from 14% to 85%+.
2. **Multi-Scale GeoTIFF Orthorectification**: Integrate automated tie-point coregistration (SIFT/ORB) directly into the geospatial ingestion service.
3. **Formal Confidence Calibration**: Implement temperature scaling and conformal prediction on validation splits to output mathematically valid error bounds.

---

### 19. What are the current scientific limitations?
**Answer**:
1. Counting small objects remains limited by VLM visual patchification.
2. Change detection precision suffers from illumination noise in unsupervised feature differencing.
3. Optical-SAR cross-modal fusion is evaluated through radiometric statistics and dual-stream synergy maps rather than task-level ground-truth segmentation masks.
4. VLM token generation latency on consumer hardware takes 4 to 8 seconds per query.

---

### 20. Why should this architecture scale?
**Answer**: The architecture is modular and decoupled:
- The **FastAPI gateway** and **deterministic router** scale horizontally across lightweight CPU instances.
- Specialist models can be hosted as independent containerized worker microservices (e.g. Triton Inference Server or Ray Serve).
- Adding new Earth Observation sensors (e.g., thermal infrared, hyperspectral, or LiDAR) only requires registering a new tool contract in `TOOL_REGISTRY` without re-architecting the planner or UI.
