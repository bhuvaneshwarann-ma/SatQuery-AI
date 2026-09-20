# SatQuery AI — Phase 8D Controlled Benchmark Execution Summary

**Execution Timestamp**: 2026-09-20T04:12:50.207492+00:00  
**Status**: COMPLETE  
**Integrity Verification**: PASS (100% genuine public benchmark data, 0 fabricated numbers)

---

## 1. Multi-Task Quantitative Benchmark Results

| Capability | Benchmark Dataset | Sample Size (N) | Primary Metric | Primary Score | Secondary Metric | Secondary Score | Mean Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Change Detection** | **LEVIR-CD** (test mini) | 20 pairs | **Change IoU (Macro)** | **0.0878** | **F1-Score (Macro)** | **0.1535** | **27.4 ms** |
| **Visual QA** | **RSVQA-LR** (val mini) | 20 samples | **Exact Match Accuracy** | **35.0%** | **Mean Token F1** | **0.2525** | **50.1 s** |

### Additional Benchmark Aggregates:
- **LEVIR-CD**:
  - Precision (Macro): `0.1237` | Recall (Macro): `0.6755`
  - Precision (Micro): `0.1415` | Recall (Micro): `0.3422`
  - Total Pixels Evaluated: `1,310,720` pixels
- **RSVQA-LR**:
  - Exact Matches: `7 / 20`
  - Total VLM Evaluation Runtime: `1002.2 s` (16.7 min)

---

## 2. Hardware & Resource Telemetry

- **Target Hardware**: NVIDIA GeForce RTX 5050 Laptop GPU
- **Total VRAM**: 8150.56 MB
- **Free VRAM After Execution**: 7070.00 MB
- **Concurrency**: Strictly sequential execution (batch size = 1) under `_GPU_EXECUTION_LOCK`.

---

## 3. Scientific Integrity & Claim Firewall

1. **Integration Validation $\ne$ Benchmark Accuracy**:
   - Previous integration test passes verified that specialist pipelines executed without crashing and returned structured envelopes.
   - The Phase 8D benchmarks above represent genuine statistical performance evaluated against ground-truth public annotations.
2. **Confidence Semantics**:
   - Confidence values returned by specialist endpoints represent heuristic algorithmic scores, not calibrated classification probabilities.
3. **No Fabricated Data**:
   - Every metric was calculated from actual model predictions against labeled ground-truth files stored under `data/benchmarks/`.
