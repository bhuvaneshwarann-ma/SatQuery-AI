# SatQuery AI — RSVQA-LR Benchmark Evaluation Report (Phase 8D)

**Execution Date**: 2026-09-20T04:12:50.207492+00:00  
**Evaluator**: `ai/evaluation/benchmark_runner.py`  
**Dataset**: RSVQA-LR (dmarsili/RSVQA-LR-2k validation split)  
**Model**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` (3 Billion parameters)  
**Visual Budget**: `min_pixels=200704`, `max_pixels=401408`  
**Precision**: `bfloat16` with dynamic CPU offload  
**Resume Checkpointing**: Active (`data/benchmarks/rsvqa_lr/checkpoint.json`)

---

## 1. Executive Statistical Summary

| Metric | Result | Description |
| :--- | :--- | :--- |
| **Exact Match (EM) Accuracy** | **35.0%** (7/20) | Normalized prediction exactly matches canonical ground truth |
| **Mean Token F1 Score** | **0.2525** | Macro token-level precision/recall harmonic mean |
| **Total Inferences Evaluated** | **20** | 20 passed, 0 failed |
| **Mean Sample Latency** | **50.11 s** | Average end-to-end pipeline time per sample |
| **Median Sample Latency** | **49.60 s** | Median end-to-end pipeline time per sample |
| **Total Benchmark Duration** | **1002.22 s** (16.7 min) | Total wall-clock evaluation session |

---

## 2. Hardware & Environment Telemetry

- **GPU Device**: NVIDIA GeForce RTX 5050 Laptop GPU
- **Total VRAM**: 8150.56 MB
- **Free VRAM**: 7070.00 MB
- **PyTorch Version**: `2.14.0+cu130`
- **Inference Mode**: Sequential, batch size = 1, `PersistentQwenVLM` loaded once

---

## 3. Per-Sample Detailed Evaluation Results

| Sample ID | Question | Ground Truth | Normalized Pred Candidate | Exact Match | Token F1 | Latency (s) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rsvqa_lr_val_0001` | Is it a rural or an urban area | `rural` | `rural` | YES | 1.00 | 43.6s | SUCCESS |
| `rsvqa_lr_val_0002` | What is the number of commercial buildings? | `5` | `there are 0 commercial buildin` | NO | 0.00 | 51.9s | SUCCESS |
| `rsvqa_lr_val_0003` | How many farmlands are there? | `62` | `10` | NO | 0.00 | 46.7s | SUCCESS |
| `rsvqa_lr_val_0004` | What is the number of buildings? | `104` | `10` | NO | 0.00 | 48.3s | SUCCESS |
| `rsvqa_lr_val_0005` | How many small buildings are there? | `100` | `2` | NO | 0.00 | 42.1s | SUCCESS |
| `rsvqa_lr_val_0006` | Are there less farmlands than water areas? | `no` | `no` | YES | 1.00 | 57.4s | SUCCESS |
| `rsvqa_lr_val_0007` | What is the number of residential buildings next to a  farmland in the image? | `98` | `2` | NO | 0.00 | 51.5s | SUCCESS |
| `rsvqa_lr_val_0008` | Is the number of commercial buildings equal to the number of grass areas? | `no` | `image provided does not contai` | YES | 0.02 | 58.9s | SUCCESS |
| `rsvqa_lr_val_0009` | Is there a circular water area? | `no` | `no` | YES | 1.00 | 45.7s | SUCCESS |
| `rsvqa_lr_val_0010` | Are there less forests than commercial buildings? | `no` | `image provided does not contai` | NO | 0.00 | 64.0s | SUCCESS |
| `rsvqa_lr_val_0011` | Is the number of water areas equal to the number of large roads? | `no` | `image provided does not contai` | YES | 0.03 | 58.8s | SUCCESS |
| `rsvqa_lr_val_0012` | What is the amount of medium water areas? | `4` | `there are 10 medium water area` | NO | 0.00 | 58.2s | SUCCESS |
| `rsvqa_lr_val_0013` | Is a large building present? | `no` | `no` | YES | 1.00 | 41.4s | SUCCESS |
| `rsvqa_lr_val_0014` | What is the number of water areas on the left of a  commercial building? | `10` | `2` | NO | 0.00 | 42.5s | SUCCESS |
| `rsvqa_lr_val_0015` | Is a circular building present in the image? | `no` | `yes` | NO | 0.00 | 44.1s | SUCCESS |
| `rsvqa_lr_val_0016` | Are there more water areas than residential buildings in the image? | `no` | `yes` | NO | 0.00 | 46.7s | SUCCESS |
| `rsvqa_lr_val_0017` | Is the number of circular residential buildings equal to the number of commercial buildings? | `no` | `it is not possible to determin` | NO | 0.00 | 63.2s | SUCCESS |
| `rsvqa_lr_val_0018` | Is the number of buildings equal to the number of forests? | `no` | `no` | YES | 1.00 | 54.4s | SUCCESS |
| `rsvqa_lr_val_0019` | What is the amount of rectangular buildings in the image? | `65` | `10` | NO | 0.00 | 50.9s | SUCCESS |
| `rsvqa_lr_val_0020` | What is the amount of medium farmlands? | `0` | `amount of medium farmlands can` | NO | 0.00 | 31.9s | SUCCESS |

---

## 4. Scientific Claim Firewall & Limitations

1. **Answer Formats**:
   - The VLM model generates conversational explanatory text, whereas RSVQA-LR labels are strict single-token strings (`rural`, `5`, `no`).
   - Normalization extracts candidate tokens and evaluates both direct match and token-level F1.
2. **Numeric Counting Task**:
   - Counting small objects in low-resolution (10m Sentinel-2) imagery is notoriously challenging for general VLMs without fine-tuning on RSVQA counts.
3. **Reproducibility**:
   - Seed 42, deterministic sequential inference on first 20 validation samples.
