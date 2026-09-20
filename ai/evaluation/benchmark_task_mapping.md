# SatQuery AI — Benchmark Task-to-Dataset Mapping (Phase 8C)

This document establishes the precise mapping between the four specialized analytical pipelines of **SatQuery AI** and target scientific benchmark datasets. Every mapping specifies the matching rationale, available ground-truth annotation format, mathematical evaluation metrics, and dataset-level constraints.

---

## 1. Visual Question Answering (VQA)

### Primary Target Benchmark: **RSVQA-HR / VRSBench (VQA Subset)**
* **Specialist Engine**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Task Rationale**: Evaluates the model's natural language comprehension, domain-specific visual reasoning, and spatial object counting against standardized remote sensing queries.
* **Ground-Truth Data Structure**:
  ```json
  {
    "image_id": "rsvqa_sample_1042",
    "image_path": "images/1042.tif",
    "question": "Are there any water bodies visible in this coastal area?",
    "ground_truth_answers": ["yes"],
    "question_type": "presence"
  }
  ```
* **Supported Evaluation Metrics**:
  * **Exact Match (EM) Accuracy**: $\text{Acc}_{\text{EM}} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\hat{y}_i \equiv y_i)$ (for categorical/boolean questions like "yes/no", counting numbers).
  * **Token F1 Score**: Harmonic mean of precision and recall over lowercased prediction tokens.
  * **BLEU-4 / ROUGE-L**: N-gram overlap metrics for descriptive/qualitative answers.
* **Dataset Fit Justification**: RSVQA contains explicit remote-sensing categories (presence, comparison, counting) directly within Landsat/Sentinel GSD bounds.

---

## 2. Visual Grounding (Spatial Object Localization)

### Primary Target Benchmark: **DIOR-RSVG / VRSBench (Grounding Subset)**
* **Specialist Engine**: `IDEA-Research/grounding-dino-tiny`
* **Task Rationale**: Evaluates the ability of zero-shot language-guided detectors to output tight, pixel-accurate bounding box coordinates for natural language referring expressions (e.g. *"ships docked at pier"*, *"oil storage tanks"*).
* **Ground-Truth Data Structure**:
  ```json
  {
    "image_id": "vrsbench_g_0482",
    "image_path": "images/0482.jpg",
    "query": "the large cargo vessel near the harbor entrance",
    "target_class": "ship",
    "ground_truth_boxes": [
      [145.0, 210.0, 312.0, 480.0]
    ]
  }
  ```
* **Supported Evaluation Metrics**:
  * **Intersection-over-Union (IoU)**: $\text{IoU}(B_{\text{pred}}, B_{\text{gt}}) = \frac{\text{Area}(B_{\text{pred}} \cap B_{\text{gt}})}{\text{Area}(B_{\text{pred}} \cup B_{\text{gt}})}$.
  * **Accuracy@IoU ($\text{Acc}@0.5$)**: Percentage of queries where the top-predicted bounding box achieves $\text{IoU} \ge 0.50$ against the ground-truth box.
  * **Mean IoU (mIoU)**: Average IoU across all evaluation query instances.
* **Dataset Fit Justification**: DIOR-RSVG and VRSBench provide human-annotated bounding boxes precisely matching Grounding DINO's output coordinate format `[ymin, xmin, ymax, xmax]`.

---

## 3. Bi-Temporal Change Detection

### Primary Target Benchmark: **LEVIR-CD / WHU-CD**
* **Specialist Engine**: `Siamese-ResNet18-FeatureDifferencer`
* **Task Rationale**: Evaluates feature differencing accuracy between pre-event (T1) and post-event (T2) satellite passes over urban expansion, disaster damage, or infrastructure modifications.
* **Ground-Truth Data Structure**:
  ```json
  {
    "pair_id": "levir_pair_0055",
    "t1_image_path": "A/0055.png",
    "t2_image_path": "B/0055.png",
    "ground_truth_mask_path": "label/0055.png",
    "mask_format": "1-channel binary raster (0 = Unchanged, 255 = Changed)"
  }
  ```
* **Supported Evaluation Metrics**:
  * **Pixel Precision**: $\text{Precision} = \frac{TP}{TP + FP}$
  * **Pixel Recall**: $\text{Recall} = \frac{TP}{TP + FN}$
  * **F1-Score**: $F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
  * **Change Intersection-over-Union (Change IoU)**: $\text{IoU}_{\text{change}} = \frac{TP}{TP + FP + FN}$
* **Dataset Fit Justification**: Replaces the current controlled synthetic pair (`sample_satellite_port_t2_synthetic.jpg`) with authentic multi-date passes possessing verified binary pixel change masks.

---

## 4. Optical + SAR Cross-Modal Analysis

### Primary Target Benchmark: **SEN1-2 (Summer / Urban Subsets)**
* **Specialist Engine**: `Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine`
* **Task Rationale**: Evaluates dual-modality co-registration validation, joint radiometric profiling, and microwave-optical structural correlation on authentic spaceborne imagery.
* **Ground-Truth Data Structure**:
  ```json
  {
    "pair_id": "sen12_summer_urban_s2_0412",
    "optical_path": "s2/0412.png",
    "sar_path": "s1/0412.png",
    "optical_sensor": "Sentinel-2 MSI (Level-1C/2A)",
    "sar_sensor": "Sentinel-1 C-SAR (IW mode, VV polarization)",
    "co_registered": true,
    "spatial_resolution": "10 meters/pixel"
  }
  ```
* **Supported Evaluation Metrics**:
  * **Cross-Modal Pearson Correlation ($r$)**: Mathematical correlation between optical luminance and radar backscatter intensity.
  * **Normalized Mutual Information (NMI)**: Information-theoretic overlap measuring joint entropy between multi-modal sensors.
  * **Radar Anomaly Ratio**: Proportion of high-backscatter microwave echoes exceeding the scene threshold $\tau$ in cloud-covered or low-reflectance zones.
* **Dataset Fit Justification**: Directly replaces the synthetic proxy SAR (`sample_satellite_port_proxy_sar.png`) with true co-registered Sentinel-1 and Sentinel-2 orbital acquisitions.

---

## 5. Summary of Prohibited Task Mismatches

To maintain evaluation integrity, the following dataset-to-task mismatches are explicitly rejected:
1. **Do NOT force BigEarthNet into VQA or Grounding**: BigEarthNet only contains whole-scene multi-label tags (e.g. *"Coniferous forest"*, *"Inland waters"*). It does not contain natural language questions or localized bounding boxes.
2. **Do NOT force Single-Date Optical Datasets into Change Detection**: Datasets like DOTA or UC Merced lack temporal pairing; synthetically altering single images is acceptable only for pipeline integration smoke testing, not for operational change benchmark claims.
3. **Do NOT force Non-Co-registered SAR Images into Joint Correlation**: Running cross-modal correlation on unrelated geographic regions (e.g. Rio Grande optical with Mauritius SAR) is mathematically invalid and produces meaningless statistics.
