# SpaceNet-6 Multi-Modal (Optical + SAR) Quantitative Validation Plan

**Document Status**: Formal Evaluation Protocol  
**Repository State**: `IMPLEMENTED + NOT QUANTITATIVELY VALIDATED`  
**Current Finding**:
> *"DualStreamOpticalSARFusionNetwork is implemented with dual ResNet-18 encoders, cross-modal attention, and radiometric Pearson correlation ($r=0.428$). Task-level quantitative fusion validation and superiority on paired labeled benchmarks are not currently established."*

---

## 1. Motivation & Scientific Integrity

While the current `DualStreamOpticalSARFusionNetwork` successfully implements cross-modal tensor alignment and radiometric backscatter analysis, hackathon evaluation standards require a strict separation between **architectural implementation** and **empirical task validation**. 

Claims of "superior segmentation through multi-modal fusion" cannot be defended on stage without a rigorous, controlled ablation using identical architectures and identical paired labeled test sets.

This document defines the exact, reproducible experimental protocol to validate or refute multi-modal superiority on the **SpaceNet-6 (Multi-Sensor All-Weather Mapping)** benchmark.

---

## 2. Dataset Requirements

### SpaceNet-6 Specification
- **Area of Interest (AOI)**: Port of Rotterdam, Netherlands (approx. 120 km²).
- **Sensors**:
  1. **Optical**: Maxar WorldView-2 half-meter pan-sharpened RGB (0.5m GSD).
  2. **SAR**: Capella Space aerial X-band Synthetic Aperture Radar (quad-pol HH/HV/VH/VV, 0.5m GSD).
- **Target Ground Truth**: Vector building footprints (GeoJSON polygons) converted to binary raster masks ($512 \times 512$ px tiles).
- **Split Protocol**:
  - **Training**: 3,401 paired tiles (Rotterdam port industrial & urban sectors).
  - **Validation**: 600 tiles (geographically isolated to prevent spatial autocorrelation leakage).
  - **Test**: 813 tiles (blind benchmark partition).

---

## 3. Preprocessing & Data Harmonization

1. **Spatial Co-Registration**:
   - Re-project both optical and SAR rasters to UTM Zone 31N (`EPSG:32631`).
   - Resample both modalities to identical spatial grids ($512 \times 512$ px, 0.5m/pixel) using bilinear interpolation for optical and nearest-neighbor for ground truth masks.
2. **SAR Speckle Suppression & Radiometric Scaling**:
   - Convert linear backscatter intensity to decibel scale:
     $$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\text{intensity} + 10^{-6})$$
   - Apply Lee filter ($5 \times 5$ window) to suppress coherent speckle noise while preserving linear edge boundaries.
   - Min-max normalize dB range $[-25.0 \text{ dB}, 0.0 \text{ dB}]$ to $[0.0, 1.0]$.
3. **Optical Normalization**:
   - Clip surface reflectance outliers to 1st and 99th percentiles.
   - Standard ImageNet z-score normalization: $\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$.

---

## 4. Controlled 3-Arm Ablation Protocol

To prove whether optical+SAR fusion yields measurable task improvements over single-sensor baselines, all three models must use identical loss functions, learning rate schedules, and optimization hyper-parameters:

| Arm | Model Name | Architecture | Input Channels | Parameters |
| :--- | :--- | :--- | :--- | :--- |
| **Arm 1** | **Optical Only Baseline** | ResNet-18 + U-Net Decoder | 3 (RGB) | 14.3M |
| **Arm 2** | **SAR Only Baseline** | ResNet-18 + U-Net Decoder | 4 (HH, HV, VH, VV) | 14.3M |
| **Arm 3** | **Dual-Stream Fusion** | `DualStreamOpticalSARFusionNetwork` | 3 (Optical) + 4 (SAR) | 28.6M |

### Training Configuration
- **Loss Function**: Combined Binary Cross-Entropy + Soft Dice Loss:
  $$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCE}}(Y, \hat{Y}) + (1 - \text{Dice}(Y, \hat{Y}))$$
- **Optimizer**: AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay = $10^{-4}$).
- **Learning Rate**: $10^{-4}$ with cosine annealing schedule down to $10^{-6}$.
- **Batch Size**: 16 pairs per batch across 50 epochs.

---

## 5. Quantitative Evaluation Metrics

All models will be evaluated pixel-wise against human-annotated building footprints on the blind test split ($N=813$ tiles):

1. **Intersection over Union (IoU / Jaccard Index)**:
   $$\text{IoU} = \frac{|Y \cap \hat{Y}|}{|Y \cup \hat{Y}|}$$
2. **F1-Score (Dice Coefficient)**:
   $$\text{F1} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
3. **Cloud-Cover Robustness Slice**:
   - Evaluate specifically on tiles with $>40\%$ synthetic cloud occlusion:
     - Hypothesized outcome: Arm 1 (Optical) F1 degrades substantially; Arm 3 (Fusion) retains $\ge 85\%$ of cloud-free performance due to SAR penetration.

---

## 6. Execution Commands (Once SpaceNet-6 Archive is Mounted)

```bash
# 1. Download and unpack SpaceNet-6 Rotterdam dataset
python scripts/download_spacenet6.py --target-dir data/benchmarks/spacenet6

# 2. Run deterministic preprocessing and tiling
python ai/data/preprocess_spacenet6.py \
    --input-dir data/benchmarks/spacenet6 \
    --output-dir data/benchmarks/spacenet6_tiles \
    --tile-size 512

# 3. Train all three ablation arms under identical seeds
python ai/training/train_optical_sar_ablation.py --arm optical_only --seed 42
python ai/training/train_optical_sar_ablation.py --arm sar_only --seed 42
python ai/training/train_optical_sar_ablation.py --arm dual_stream --seed 42

# 4. Generate quantitative comparison matrix and markdown report
python ai/evaluation/evaluate_spacenet6_ablation.py \
    --checkpoints-dir training/checkpoints/spacenet6_ablation \
    --output results/spacenet6_ablation_results.csv
```

---

## 7. Current Hackathon Disclosure

Until the above 4-step protocol is executed with verified SpaceNet-6 checkpoints:
> **"Optical/SAR fusion is implemented in SatQuery AI; task-level superiority remains to be established."**
