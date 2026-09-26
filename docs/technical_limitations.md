# SatQuery AI — Technical & Scientific Limitations

**Document Status**: Official Limitations Disclosure  
**Last Updated**: 2026-09-26  
**Audience**: Technical Evaluators, Academic Judges, System Architects

---

## 1. Visual Question Answering (VLM) Limitations

### Small-Object Counting Deficits
- **Empirical Measurement**: Both baseline Qwen2.5-VL-7B and LoRA-adapted checkpoints achieve only **20.0% accuracy** on small-object counting probes (e.g. ship and building counting on RSVQA-LR).
- **Underlying Cause**: Modern vision-language transformers tokenize images into discrete visual patches (e.g. $14 \times 14$ or $28 \times 28$ pixels). Dense, sub-pixel or small aerial targets (such as small fishing boats or shipping containers) collapse into identical or adjacent token patches, causing the self-attention mechanism to lose individual spatial identity.
- **Architectural Defense**: SatQuery AI prevents VLM counting hallucinations by intercepting numerical count queries via a pre-routing regex guardrail (`COUNT_PATTERNS`) and routing them to Grounding DINO, deriving the count strictly from `len(valid_bounding_boxes)`.

### Inference Latency on 8 GB Consumer Hardware
- **Measurement**: Qwen2.5-VL parameter generation requires **300–560 seconds** wall-clock per query when executing on consumer hardware with 8 GB VRAM.
- **Underlying Cause**: Due to the 8.29B parameter footprint, approximately 35% of model layers must be offloaded from VRAM to host system RAM and disk buffers via `accelerate`. Each token autoregressive decoding step incurs PCIe bus transfer latency.
- **Production Roadmap**: In operational environments, inference would be deployed on dedicated multi-GPU instances (e.g. NVIDIA A100/H100 with tensor parallelism) or 4-bit quantized AWQ/GPTQ kernels, reducing latency to $<2$ seconds.

---

## 2. Change Detection Limitations

### Precision Ceiling on Unsupervised Differencing
- **Empirical Measurement**: Evaluated across 20 co-registered LEVIR-CD pairs, the calibrated threshold $\tau=0.30$ achieves:
  - Recall: `73.56%`
  - F1-Score: `0.2335`
  - IoU: `0.1322`
  - **Precision: `13.88%`**
- **Underlying Cause**: The change detection engine relies on Siamese ResNet-18 Euclidean feature differencing without supervised segmentation head fine-tuning on building masks. Consequently, subtle variations in sun illumination angle, seasonal vegetation phenology, and surface moisture generate non-zero Euclidean distances that produce false positive clusters.
- **Architectural Defense**: Change detection output is explicitly treated as a high-recall candidate proposal mask. In complex workflows, the agent chains Change Detection into Grounding and VQA to corroborate candidate changed regions before issuing qualitative assertions.

---

## 3. Visual Grounding Limitations

### Uncalibrated Cross-Attention Logits
- **Empirical Measurement**: Raw detector confidence scores range between `0.30` and `0.52`.
- **Underlying Cause**: Grounding DINO outputs cross-attention similarity scores between visual feature tokens and text prompt tokens. These scores do not undergo post-hoc calibration (e.g. Platt scaling or Isotonic regression) against labeled ground truth remote-sensing datasets (such as DIOR-RSVG or DOTA).
- **Architectural Defense**: SatQuery AI explicitly labels all grounding scores as `"Model confidence — uncalibrated (cross-attention logit)"` and strictly forbids reporting them as `"Localization accuracy"`. A complete calibration plan is documented in `docs/grounding_validation_plan.md`.

---

## 4. Multi-Modal Optical + SAR Limitations

### Prototype Status & Absence of Task-Level Ablation
- **Empirical Measurement**: DualStreamOpticalSARFusionNetwork computes cross-sensor statistics and achieves a radiometric Pearson correlation $r = 0.428$ on aligned test pairs.
- **Limitation**: The model is an **architectural prototype**. It has not been trained or evaluated on a paired labeled benchmark (such as SpaceNet-6 building footprints). Therefore, no quantitative claim can be made that optical+SAR fusion outperforms optical-only or SAR-only models in segmentation or classification accuracy.
- **Architectural Defense**: The system transparently reports: *"Multimodal optical/SAR processing is implemented, but task-level superiority has not been quantitatively established."* A controlled 3-arm ablation protocol is documented in `docs/optical_sar_validation_plan.md`.

---

## 5. Geospatial Processing Limitations

### Scope of Current Validation
- **Implemented & Verified**:
  - Raster grid dimension equality ($W_1 = W_2, H_1 = H_2$)
  - Multi-spectral channel requirements (RGB 3-channel vs. SAR 1-channel)
  - GDAL/Rasterio GeoTIFF coordinate reference system (CRS/EPSG) parsing
  - File existence and format integrity.
- **Current Operational Gaps**:
  - **Sub-Pixel Co-Registration**: The system assumes rasters are co-registered prior to ingestion; it does not perform automated tie-point matching or affine warp alignment.
  - **Sensor Resolution Discrepancy**: Rasters with identical pixel dimensions but differing ground sampling distances (GSD, e.g. 10m Sentinel-2 vs. 0.5m WorldView) are not resampled automatically.
  - **Temporal Timestamp Validation**: Sensor acquisition dates are parsed from metadata strings when available, but automated satellite orbital catalog cross-referencing is not currently integrated.
