# SatQuery AI — Evaluation Matrix (Phase 8B)

This evaluation matrix strictly categorizes the verification status of **SatQuery AI** across three decoupled tiers:
1. **Category A: Integration Validation** (End-to-end software pipeline, contracts, schemas, API endpoints, and hardware stability)
2. **Category B: Model / Algorithm Evaluation** (Functional capability, algorithmic output sanity, and resource footprint on local GPU)
3. **Category C: Dataset-Backed Benchmark Evaluation** (Statistical evaluation against verified ground-truth reference labels)

---

## Evaluation Matrix by Tier

### Category A: Integration Validation

| Capability | Current Asset | Validation Scope | Contract Metric | Status | Evaluation Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VQA** | `sample_satellite_port.jpg` | HTTP multipart upload → InputValidator → AgentRouter → `run_vqa` → ToolResult → Observable Trace → UI | HTTP 200, 5-stage trace (`INPUT_VALIDATION`, `ROUTER`, `TOOL_EXECUTION`, `EVIDENCE`, `RESULT_COMPOSITION`) | **PASS** | Validated via `test_agent_orchestration.py`, `test_backend_api.py`, `test_api_contract.py` |
| **Grounding** | `sample_satellite_port.jpg` | HTTP multipart upload → Router parameter firewall → `run_grounding` → spatial bounding boxes → artifact save | HTTP 200, non-empty bounding box list, confidence score, annotated JPEG artifact at `/api/artifacts/` | **PASS** | Validated via `test_grounding_execution.py`, `test_api_contract.py` |
| **Change Detection** | T1: `sample_satellite_port.jpg`<br>T2: `sample_satellite_port_t2_synthetic.jpg` | Bi-temporal image pairing → Siamese ResNet18 forward pass → feature differencing → heatmap mask | HTTP 200, changed pixels $>0$, change percentage, synthetic evaluation caveat preserved in metadata | **PASS** | Validated via `test_change_execution.py`, `test_api_contract.py` |
| **Optical-SAR** | Optical: `sample_satellite_port.jpg`<br>SAR: `sample_satellite_port_proxy_sar.png` | Dual-stream multi-sensor ingestion → radiometric normalization → Pearson $r$ correlation → synergy composite | HTTP 200, optical/SAR stats, cross-modal $r \in [-1, 1]$, `proxy_sar` data classification preserved | **PASS** | Validated via `test_optical_sar_execution.py`, `test_api_contract.py` |
| **Parameter Firewall** | Query + Injection Payload | Injection of unauthorized parameters (e.g. `unauthorized_key`) | Status `INVALID_INPUT`, `error_type="INVALID_PARAMETER"`, sub-millisecond rejection, 0 model execution | **PASS** | Validated via `test_agent_orchestration.py` (Test 10), `test_api_contract.py` (Test 5) |
| **Intent Ambiguity** | Ambiguous Query (`"process this"`, `"calculate orbital trajectory"`) | Deterministic intent classification under domain keyword rules | Status `NEEDS_CLARIFICATION`, clarification prompt returned, 0 model execution | **PASS** | Validated via `test_backend_api.py` (Test B), `test_api_contract.py` (Test 6) |

---

### Category B: Model / Algorithm Evaluation (Functional & Local GPU Footprint)

| Capability | Model / Engine | Input Assets | Functional Metric | Measured Performance | Demonstrated Capability | Known Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VQA** | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | `sample_satellite_port.jpg` | Domain terminology alignment & scene description completeness | Latency: ~27–49s (cold/resident)<br>VRAM: ~6.2 GB allocated (BF16 CPU offload active) | Accurately identifies natural harbor, coastal waterways, jetties, ships, and sediment plumes without hallucinating urban skylines. | Visual token budget downscales high-res scenes; cannot detect sub-pixel targets; sequential execution required on 8 GB GPU. |
| **Grounding** | `IDEA-Research/grounding-dino-tiny` | `sample_satellite_port.jpg` | Spatial coordinate bounding box localization for zero-shot text prompts | Latency: 0.36–9.3s<br>VRAM: ~660 MB allocated (tensors evicted after pass) | Detects target ships with tight pixel bounding coordinates `[ymin, xmin, ymax, xmax]` and renders bounding box overlay. | Confidence is a detector heuristic score, not verified IoU accuracy against human annotations; sensitive to threshold tuning. |
| **Change Detection** | `Siamese-ResNet18-FeatureDifferencer` | T1 + T2 Synthetic | Multi-scale feature distance thresholding and binary mask segmentation | Latency: 0.35–0.68s<br>VRAM: ~12 MB allocated | Isolates newly constructed dock infrastructure and localized modifications while rejecting unchanged ocean/land backgrounds. | Evaluated on controlled synthetic temporal pair; real multi-date seasonal illumination and coregistration variance not tested. |
| **Optical-SAR** | `Dual-Stream Cross-Modal Engine` | Optical RGB + Proxy SAR | Radiometric intensity profiling & cross-sensor Pearson correlation ($r$) | Latency: 0.28–0.51s<br>VRAM: ~10 MB allocated | Identifies 40,910 high-backscatter radar returns (11.84% of scene) and 28,276 radar-dominant anomalies with $r = 0.574$. | SAR asset is a physically modeled synthetic proxy simulating backscatter; authentic spaceborne Sentinel-1 coregistration pending. |

---

### Category C: Dataset-Backed Benchmark Evaluation (Statistical Accuracy)

| Capability | Target Benchmark Dataset | Required Labels / Ground Truth | Standard Scientific Metrics | Current Benchmark Status | Operational Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VQA** | RSVQA / VRSBench | Triplet: (Satellite Image, Natural Language Question, Ground-Truth Reference Answer) | Top-1 Accuracy (%), BLEU-4, METEOR, ROUGE-L, CIDEr | **Pending Ground-Truth Dataset** | Integration validated; quantitative benchmark accuracy pending local ingestion of verified remote-sensing QA benchmark corpus. |
| **Grounding** | DIOR-RSVG / RSVG | Pair: (Satellite Image, Referring Text Expression) + Ground-Truth Bounding Box Coordinates $[x_1, y_1, x_2, y_2]$ | $\text{IoU} \ge 0.5$ Success Rate, Mean IoU (mIoU), Average Precision (AP@50) | **Pipeline Validation Only** | Integration validated; precision/recall benchmark pending ground-truth labeled spatial dataset. Do not treat detector confidence as IoU accuracy. |
| **Change Detection** | LEVIR-CD / WHU-CD / Siam-CD | Triplet: (T1 Optical Image, T2 Optical Image, Pixel-Level Binary Change Mask) | Precision, Recall, F1-Score, Change IoU, Overall Accuracy (OA) | **Pending Labeled Bi-Temporal Imagery** | Integration validated on synthetic pair; quantitative operational accuracy pending ingestion of authentic labeled multi-pass dataset. |
| **Optical-SAR** | SEN1-2 / QXS-SAROPT | Co-registered Pair: (Sentinel-2 L2A Optical, Sentinel-1 GRD SAR) + Coregistration Metadata | Mutual Information (MI), Structural Similarity Index (SSIM), Normalized Cross-Correlation (NCC) | **Pending Genuine Co-Registered Imagery** | Pipeline integration verified with proxy SAR; genuine multi-sensor cross-modal evaluation pending co-registered spaceborne dataset. |
