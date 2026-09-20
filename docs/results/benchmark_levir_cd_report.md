# SatQuery AI — LEVIR-CD Benchmark Evaluation Report (Phase 8D)

**Execution Date**: 2026-09-20T03:48:21.850439+00:00  
**Evaluator**: `ai/evaluation/benchmark_runner.py`  
**Dataset**: LEVIR-CD (Cropped-256 test split)  
**Model**: `Siamese-ResNet18-FeatureDifferencer` (Pretrained ResNet18)  
**Positive Class Definition**: Pixel value $>128$ in ground-truth binary change mask (1 = Building Change, 0 = No Change).  
**Differential Threshold**: $\tau = 0.42$

---

## 1. Executive Statistical Summary

| Metric | Macro Average (Per Sample) | Micro Average (All Pixels) | Notes |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.1237** | **0.1415** | $\frac{TP}{TP + FP}$ |
| **Recall** | **0.6755** | **0.3422** | $\frac{TP}{TP + FN}$ |
| **F1-Score** | **0.1535** | **0.2002** | Harmonic mean of Precision & Recall |
| **Change IoU** | **0.0878** | **0.1113** | $\frac{TP}{TP + FP + FN}$ |

- **Total Evaluated Image Pairs**: 20 (100% completed, 0 failures)
- **Total Pixels Evaluated**: 1,310,720 pixels
- **Confusion Matrix Totals**:
  - True Positives ($TP$): 43,061
  - False Positives ($FP$): 261,177
  - False Negatives ($FN$): 82,757
  - True Negatives ($TN$): 923,725
- **Mean Latency**: 27.39 ms / pair
- **Median Latency**: 8.82 ms / pair
- **Total Benchmark Duration**: 0.56 s

---

## 2. Hardware & Environment Telemetry

- **GPU Device**: NVIDIA GeForce RTX 5050 Laptop GPU
- **Total VRAM**: 8150.56 MB
- **Free VRAM**: 7020.00 MB
- **PyTorch Version**: `2.14.0+cu130`
- **Inference Mode**: `torch.inference_mode()`, batch size = 1

---

## 3. Per-Sample Detailed Evaluation Results

| Sample ID | Changed Pixels (Pred) | Changed Pixels (GT) | Precision | Recall | F1-Score | IoU | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `levir_cd_test_0001` | 10,085 | 0 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 373.9 |
| `levir_cd_test_0002` | 7,547 | 447 | 0.0592 | 1.0000 | 0.1118 | 0.0592 | 10.9 |
| `levir_cd_test_0003` | 8,264 | 16,089 | 0.2216 | 0.1138 | 0.1504 | 0.0813 | 9.5 |
| `levir_cd_test_0004` | 11,332 | 20,416 | 0.3015 | 0.1674 | 0.2153 | 0.1206 | 8.7 |
| `levir_cd_test_0005` | 11,566 | 7,219 | 0.1632 | 0.2615 | 0.2010 | 0.1117 | 8.4 |
| `levir_cd_test_0006` | 14,889 | 18,886 | 0.2492 | 0.1965 | 0.2197 | 0.1234 | 7.9 |
| `levir_cd_test_0007` | 29,380 | 18,843 | 0.2554 | 0.3982 | 0.3112 | 0.1843 | 14.3 |
| `levir_cd_test_0008` | 21,415 | 15,523 | 0.2205 | 0.3042 | 0.2557 | 0.1466 | 9.0 |
| `levir_cd_test_0009` | 16,151 | 0 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 8.2 |
| `levir_cd_test_0010` | 1,793 | 0 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 9.1 |
| `levir_cd_test_0011` | 8,144 | 1,131 | 0.1224 | 0.8815 | 0.2150 | 0.1204 | 9.8 |
| `levir_cd_test_0012` | 15,118 | 0 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 8.6 |
| `levir_cd_test_0013` | 11,994 | 2,134 | 0.1698 | 0.9545 | 0.2883 | 0.1685 | 7.9 |
| `levir_cd_test_0014` | 38,172 | 11,766 | 0.2285 | 0.7414 | 0.3493 | 0.2116 | 9.6 |
| `levir_cd_test_0015` | 18,640 | 219 | 0.0091 | 0.7717 | 0.0180 | 0.0090 | 8.2 |
| `levir_cd_test_0016` | 20,643 | 6,170 | 0.1915 | 0.6408 | 0.2949 | 0.1730 | 7.3 |
| `levir_cd_test_0017` | 24,592 | 0 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 9.4 |
| `levir_cd_test_0018` | 10,132 | 211 | 0.0208 | 1.0000 | 0.0408 | 0.0208 | 8.3 |
| `levir_cd_test_0019` | 10,126 | 1,154 | 0.0666 | 0.5841 | 0.1196 | 0.0635 | 8.2 |
| `levir_cd_test_0020` | 14,255 | 5,610 | 0.1947 | 0.4948 | 0.2794 | 0.1624 | 10.5 |

---

## 4. Scientific Claim Firewall & Limitations

1. **Unsupervised vs Supervised Differencing**:
   - The current specialist uses a Siamese deep feature differencer on ImageNet-pretrained ResNet-18 features without task-specific fine-tuning on LEVIR-CD.
   - The reported F1-score ({macro_f1:.4f} macro) reflects zero-shot unsupervised feature distance differencing under fixed threshold $\tau={threshold:.2f}$, NOT a fine-tuned change detection network.
2. **Confidence Semantics**:
   - Model confidence is computed as the complement of changed pixel area and does NOT equate to statistical classification accuracy.
3. **No Claim of SOTA**:
   - These results establish an honest, reproducible quantitative baseline for the SatQuery AI engine on genuine remote sensing benchmark data.
