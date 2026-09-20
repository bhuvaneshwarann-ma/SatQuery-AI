# SatQuery AI — Scientific Benchmark Evaluation Protocol (Phase 8C)

This document specifies the exact, reproducible experimental protocol for evaluating **SatQuery AI** across standard Earth Observation benchmark datasets. Any teammate or external researcher can reproduce identical benchmark evaluations by following these procedures.

---

## 1. Experimental Environment & Hardware Specifications

* **Operating System**: Windows 11 64-bit
* **GPU**: NVIDIA GeForce RTX 5050 Laptop GPU (8,150.56 MB GDDR7)
* **CUDA Driver**: 13.0 (CUDA UMD 13.3)
* **PyTorch Version**: `2.14.0+cu130`
* **Python Version**: `3.12` (in `.venv`)
* **Concurrency Policy**: Sequential inference via `_GPU_EXECUTION_LOCK` (batch size = 1)
* **Random Seed**: Fixed at `seed = 42` for all pseudo-random sample selections and dataset splits.

---

## 2. Capability Specifications & Protocol

### A. Visual Question Answering (VQA)
* **Target Dataset**: RSVQA-LR / VRSBench VQA subset
* **Evaluator Script**: `ai/evaluation/benchmark_runner.py --task VQA`
* **Recommended Evaluation Subset**: $N = 25$ image-question pairs
* **Input Preprocessing**:
  * Image RGB converted, dynamic aspect ratio preservation.
  * Visual token budget: `min_pixels = 200,704`, `max_pixels = 401,408`.
* **Model Configuration**:
  * Checkpoint: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
  * Precision: `bfloat16` with automatic CPU offload (`device_map="auto"`)
  * Decoding: Greedy search (`do_sample=False`, `max_new_tokens=100`)
* **Evaluation Metrics**:
  * Categorical Exact Match (EM): $\text{Accuracy} = \frac{N_{\text{exact}}}{N_{\text{total}}}$
  * Token-level macro F1 score
* **Runtime Expectation**: $\approx 15\text{s} - 25\text{s}$ per sample ($\approx 6 - 10\text{ minutes}$ for $N=25$).

---

### B. Visual Grounding (Spatial Object Localization)
* **Target Dataset**: DIOR-RSVG / VRSBench Grounding subset
* **Evaluator Script**: `ai/evaluation/benchmark_runner.py --task GROUNDING`
* **Recommended Evaluation Subset**: $N = 25$ referring-expression queries
* **Input Preprocessing**:
  * Normalization: ImageNet standard mean & std dev.
  * Dot-termination appended to text prompt (e.g. `"${query}."`).
* **Model Configuration**:
  * Checkpoint: `IDEA-Research/grounding-dino-tiny`
  * Detection Thresholds: `box_threshold = 0.35`, `text_threshold = 0.25`
  * Post-Processing: Tensor deletion and `torch.cuda.empty_cache()` after each pass.
* **Evaluation Metrics**:
  * Intersection-over-Union (IoU) between predicted box $[y_1, x_1, y_2, x_2]$ and ground truth box.
  * Success Rate at IoU $\ge 0.50$ ($\text{Acc}@0.5$).
  * Mean IoU ($\text{mIoU}$).
* **Runtime Expectation**: $\approx 0.4\text{s}$ per sample ($\approx 10\text{ seconds}$ for $N=25$).

---

### C. Bi-Temporal Change Detection
* **Target Dataset**: LEVIR-CD mini-split / WHU-CD
* **Evaluator Script**: `ai/evaluation/benchmark_runner.py --task CHANGE_DETECTION`
* **Recommended Evaluation Subset**: $N = 25$ bi-temporal image pairs (T1, T2)
* **Input Preprocessing**:
  * Paired spatial cropping ($512 \times 512$ px or $720 \times 480$ px matching).
  * ImageNet normalization applied independently to T1 and T2 tensors.
* **Model Configuration**:
  * Architecture: `Siamese-ResNet18-FeatureDifferencer`
  * Differencing Threshold: Euclidean distance threshold $\tau = 0.40$.
* **Evaluation Metrics**:
  * Pixel Precision: $\frac{TP}{TP + FP}$
  * Pixel Recall: $\frac{TP}{TP + FN}$
  * Pixel F1-Score: $\frac{2 \cdot P \cdot R}{P + R}$
  * Change IoU: $\frac{TP}{TP + FP + FN}$
* **Runtime Expectation**: $\approx 0.5\text{s}$ per pair ($\approx 12\text{ seconds}$ for $N=25$).

---

### D. Optical-SAR Multi-Sensor Fusion
* **Target Dataset**: SEN1-2 (Summer urban & coastal subset)
* **Evaluator Script**: `ai/evaluation/benchmark_runner.py --task OPTICAL_SAR`
* **Recommended Evaluation Subset**: $N = 25$ co-registered Sentinel-1 / Sentinel-2 pairs
* **Input Preprocessing**:
  * Verify identical raster spatial bounds and pixel grid alignment.
  * Optical: Luminance transformation $Y = 0.299R + 0.587G + 0.114B$.
  * SAR: Single-channel amplitude conversion and dB scaling estimation.
* **Model Configuration**:
  * Engine: `Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine`
  * High-Scatter Threshold: $\tau_{\text{SAR}} = 180.0$ DN.
* **Evaluation Metrics**:
  * Cross-modal Pearson correlation coefficient ($r$).
  * Radar anomaly density (percentage of microwave reflectors in low-optical reflectance regions).
* **Runtime Expectation**: $\approx 0.3\text{s}$ per pair ($\approx 7.5\text{ seconds}$ for $N=25$).

---

## 3. Reproduction Command Line

To execute a benchmark evaluation:

```bash
# Example 1: VQA Dry-Run Verification (Schema & Pipeline check)
.venv\Scripts\python ai\evaluation\benchmark_runner.py --task VQA --dry-run --subset-size 10

# Example 2: Grounding Benchmark Evaluation (Once dataset slice is loaded)
.venv\Scripts\python ai\evaluation\benchmark_runner.py --task GROUNDING --dataset-name VRSBench_Mini --dataset-root data/benchmarks/vrsbench_mini --subset-size 25 --seed 42

# Example 3: Change Detection Benchmark Evaluation
.venv\Scripts\python ai\evaluation\benchmark_runner.py --task CHANGE_DETECTION --dataset-name LEVIR_CD_Mini --dataset-root data/benchmarks/levir_cd_mini --subset-size 25 --seed 42
```

---

## 4. Known Evaluation Protocol Limitations

1. **Sequential Execution Mandatory**: On local 8 GB GPUs, attempting parallel batch inference with the 3B VLM will immediately trigger CUDA OOM.
2. **Ground-Truth Data Ingestion Policy**: Bulk downloading $>10\text{ GB}$ datasets is restricted; always use pre-filtered mini-splits ($N=20-50$).
3. **Sensor GSD Differences**: High-resolution datasets (e.g. aerial $0.15\text{m}$) cannot be directly compared against medium-resolution sensors (Landsat $30\text{m}$) without accounting for Ground Sampling Distance (GSD).
