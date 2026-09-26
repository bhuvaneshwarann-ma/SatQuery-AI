# Grounding DINO Remote-Sensing Benchmark & Confidence Calibration Plan

**Document Status**: Formal Evaluation & Calibration Protocol  
**Repository State**: `IMPLEMENTED + PARTIALLY VALIDATED`  
**Current Finding**:
> *"Grounding DINO Swin-T operates zero-shot. While qualitative bounding boxes, annotated visual artifacts, and raw cross-attention logits (0.30 - 0.52) are logged, benchmarked localization accuracy (mAP@0.5) against a labeled remote-sensing ground truth benchmark is not currently established. Reported detector scores must be labeled 'uncalibrated detector confidence', never 'localization accuracy'."*

---

## 1. Objective: From Raw Logits to Calibrated Spatial Overlap

In standard object detection, model logits reflect cross-attention matching scores between text tokens and visual feature tokens. In remote sensing imagery—characterized by nadir viewpoints, dense object clustering, and high aspect-ratio variations—raw detector scores are frequently uncalibrated.

The objective of this calibration plan is:
$$\text{Raw Detector Score } s \in [0, 1] \xrightarrow{\text{Isotonic / Platt Scaling}} P(\text{IoU} \ge 0.50 \mid s)$$

This allows SatQuery AI to convert raw uncalibrated detector confidence into a statistically sound probability of true spatial localization.

---

## 2. Benchmark Datasets

### DIOR-RSVG (Remote Sensing Visual Grounding)
- **Scale**: 23,463 satellite images, 58,393 referring expressions, 20 object classes (airports, bridges, ships, storage tanks, harbor quays, expressways).
- **Source Sensors**: Google Earth optical RGB (0.5m to 30m spatial resolution).
- **Split**: 14,000 train expressions, 3,463 validation, 6,000 test expressions.

### Secondary Evaluation: DOTA-v1.5 (Dense Small-Object Detection)
- **Focus**: Oriented and horizontal bounding boxes for maritime vessels, shipping containers, and vehicles.
- **Tiling**: $1024 \times 1024$ px overlapping sub-patches with 200 px stride.

---

## 3. Evaluation Protocol & Metrics

### 1. Ground Truth Matching
A detected bounding box $\hat{B}_i$ matches a ground-truth annotation $B_j^*$ if and only if:
$$\text{IoU}(\hat{B}_i, B_j^*) = \frac{\text{Area}(\hat{B}_i \cap B_j^*)}{\text{Area}(\hat{B}_i \cup B_j^*)} \ge 0.50$$

### 2. Localization Metrics
- **mAP@0.50**: Mean Average Precision calculated across all 20 DIOR-RSVG object classes at IoU threshold $0.50$.
- **mAP@0.50:0.95**: COCO-style average precision across IoU thresholds from $0.50$ to $0.95$ with step $0.05$.
- **Precision / Recall Curves**: Evaluated at varying detector score cutoffs $\tau \in [0.10, 0.90]$.

### 3. Calibration Metrics (Expected Calibration Error)
Partition predictions into $M=10$ confidence bins $B_m \subset (0, 1]$:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{Accuracy}(B_m) - \text{Confidence}(B_m) \right|$$
where $\text{Accuracy}(B_m)$ is the fraction of detections in bin $m$ with $\text{IoU} \ge 0.50$, and $\text{Confidence}(B_m)$ is the mean detector score in bin $m$.

---

## 4. Calibration Methodology

1. **Temperature Scaling**:
   Learn a single scalar parameter $T > 0$ on the validation split:
   $$\hat{p}_i = \sigma(z_i / T)$$
   where $z_i$ is the pre-sigmoid logit of bounding box $i$.
2. **Isotonic Non-Parametric Regression**:
   Fit a piecewise non-decreasing step function mapping raw detector logits to empirical true positive frequencies:
   $$\hat{P}(\text{IoU} \ge 0.5) = f_{\text{iso}}(s_i)$$

---

## 5. Execution Commands (Once Benchmark Dataset is Mounted)

```bash
# 1. Download and extract DIOR-RSVG benchmark dataset
python scripts/download_dior_rsvg.py --data-dir data/benchmarks/dior_rsvg

# 2. Run zero-shot evaluation on DIOR-RSVG test split (6,000 queries)
python ai/evaluation/benchmark_grounding_dino.py \
    --dataset dior_rsvg \
    --data-dir data/benchmarks/dior_rsvg \
    --iou-threshold 0.50 \
    --output results/grounding_dino_dior_raw.json

# 3. Fit Isotonic Calibration model on validation split
python ai/evaluation/calibrate_grounding_scores.py \
    --input results/grounding_dino_dior_raw.json \
    --calibrator isotonic \
    --save-model training/checkpoints/grounding_calibrator.pkl

# 4. Generate Calibration Reliability Diagram and ECE Report
python ai/evaluation/plot_grounding_reliability.py \
    --raw-results results/grounding_dino_dior_raw.json \
    --calibrator training/checkpoints/grounding_calibrator.pkl \
    --output-plot docs/results/grounding_calibration_curve.png
```

---

## 6. Current Hackathon Disclosure

Until the above calibrated benchmark is executed:
> **"Grounding DINO confidence is an uncalibrated cross-attention detector score; it is not equivalent to benchmarked spatial localization accuracy."**
