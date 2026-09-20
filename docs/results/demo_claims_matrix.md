# SatQuery AI — Demo Claims Matrix

**Document Purpose**: Definitive reference establishing which technical and performance claims are fully supported by code and benchmarks, which claims require scientific qualifications, and which claims are strictly prohibited during pitch presentations and jury evaluations.

---

## 1. Supported Claims (100% Backed by Code & Empirical Evidence)

The team may state the following without hesitation, as they are proven by working code, automated test suites, and empirical benchmark outputs:

| Claim | Verification Evidence | Key Numbers / Facts |
| :--- | :--- | :--- |
| **Autonomous, Controlled Agentic Orchestration** | `backend/app/agent/router.py`<br>`ai/evaluation/test_agent_orchestration.py` | 11/11 tests pass. Sub-millisecond routing maps user intent to specialist models with zero prompt injections or unconstrained LLM loops. |
| **Four Multi-Modal Specialist Capabilities** | `backend/app/agent/registry.py`<br>`backend/app/services/orchestration_service.py` | Supports VQA, Visual Grounding, Bi-Temporal Change Detection, and Optical-SAR Multi-Sensor Fusion under one unified API. |
| **Predefined Tool Registry & Parameter Firewall** | `ai/evaluation/test_failure_cases.py` (Test 9, 10)<br>`backend/app/agent/registry.py` | 10/10 failure tests pass. Parameters are strictly validated against whitelisted types and numerical ranges in $<20\text{ ms}$ before invoking heavy models. |
| **Observable Execution Tracing** | FastAPI `/api/analyze` response envelope<br>React UI Trace Component | Returns a structured 5-stage execution trace (`INPUT_VALIDATION` → `ROUTER` → `TOOL_EXECUTION` → `EVIDENCE` → `RESULT_COMPOSITION`) with per-step latency and status. |
| **Visual Spatial Evidence Delivery** | Generated image files in `docs/results/` | Provides visual bounding box annotations (`grounding_execution_artifact.jpg`), 3-panel change heatmaps (`change_detection_execution_artifact.jpg`), and optical-SAR synergy maps (`optical_sar_execution_artifact.jpg`). |
| **Reproducible Public Benchmark Evaluations** | `docs/results/benchmark_levir_cd_report.md`<br>`docs/results/benchmark_rsvqa_report.md` | Executed on public datasets with seed 42: LEVIR-CD ($N=20$) and RSVQA-LR ($N=20$) with zero metric fabrication. |
| **Hardware-Safe GPU Concurrency** | `_GPU_EXECUTION_LOCK` in backend orchestration | Serialized execution prevents concurrent heavy model allocation, guaranteeing 0 CUDA OOM crashes on 8 GB consumer laptop GPUs. |

---

## 2. Qualified Claims (Must State the Required Scientific Caveat)

The following claims are technically valid but **must always be communicated with their specific scientific qualification**:

| Qualified Claim | Required Caveat / Scientific Boundary | Documented Baseline |
| :--- | :--- | :--- |
| **"SatQuery AI achieves 35.0% Exact Match on RSVQA-LR."** | Evaluated on an **$N=20$ Sentinel-2 sample slice** (Seed 42) using `remote-sensing-Qwen2.5-VL-3B-Instruct`. High performance on categorical and boolean queries; granular numeric counting remains challenging without in-domain fine-tuning. | 35.0% EM (7/20), 0.2525 Mean Token F1, 50.11s mean latency. |
| **"SatQuery AI detects structural changes between multi-temporal passes."** | Evaluated on **$N=20$ LEVIR-CD pairs** using an **unsupervised Siamese-ResNet18 feature distance differencer** at threshold $\tau=0.42$. It is not an end-to-end supervised change detection segmentation head and does not imply generalized real-world temporal change accuracy beyond this subset. | 0.0878 Macro IoU, 0.1535 Macro F1, 27.4 ms mean latency. |
| **"SatQuery AI fuses Optical and Microwave SAR satellite data."** | Current cross-modal validation uses a **physically modeled synthetic radar backscatter proxy** (`proxy_sar`) reflecting corner reflection and surface roughness. Authentic spaceborne Cartosat-2S and RISAT-1A co-registered pairs remain restricted under ISRO/SAC institutional data licensing. | Pearson $r = 0.574$, Radar backscatter anomaly density = 28,276 px. |
| **"Confidence scores represent uncalibrated algorithmic metrics."** | Confidence scores are strictly **uncalibrated heuristic metrics** with distinct per-tool definitions: (1) **VQA**: confidence is unavailable/`null`; (2) **Grounding**: detector cross-attention logit score; NOT calibrated and NOT localization accuracy; (3) **Change Detection**: heuristic background area stability margin, NOT equivalent to F1/IoU; (4) **Optical-SAR**: pipeline integrity completion indicator, NOT target prediction accuracy. | Grounding score $\approx 0.37$, Change confidence $\approx 0.97$, VQA is `null`, Optical-SAR is `1.0`. |
| **"Sub-second change detection and cross-modal processing."** | ResNet-18 and Radiometric correlation engines run in $<0.6\text{s}$, but **VQA reasoning takes ~50 seconds** per sample due to the 3-Billion-parameter VLM autoregressive decoding budget on consumer hardware. | Change detection: 27.4 ms - 0.59 s; VQA: 50.11 s. |

---

## 3. Unsupported Claims (Strictly Prohibited During Presentation)

The pitch team, presentation slides, and demonstration scripts must **NEVER** make the following claims:

| Prohibited Claim | Why It Is Prohibited | Proper Scientific Substitute |
| :--- | :--- | :--- |
| ❌ *"Our AI achieves 95% (or 98%) accuracy."* | Conflates background area stability or integration tests with scientific classification accuracy. Our actual measured VQA accuracy on RSVQA-LR is **35.0% EM**, and change detection is **0.1535 Macro F1**. | *"We evaluated our baseline on genuine benchmark subsets, achieving 35.0% EM on RSVQA-LR and 0.1535 F1 on LEVIR-CD without fine-tuning."* |
| ❌ *"State-of-the-Art (SOTA) remote sensing AI."* | We have not published competitive comparative benchmarks against all leading remote sensing research models across full multi-gigabyte benchmark corpuses. | *"SatQuery AI provides a robust, agentic architecture integrating validated open-source remote-sensing specialist models."* |
| ❌ *"Calibrated confidence scores or posterior probability values."* | No statistical calibration experiments (e.g. Platt scaling, temperature scaling, Expected Calibration Error) have been conducted. Confidence values are purely uncalibrated heuristic scores. | *"SatQuery AI returns transparent, uncalibrated heuristic scores distinguishing detector logits, area margins, and pipeline integrity."* |
| ❌ *"Custom-adapted or fine-tuned remote sensing VLM."* | The team deployed an existing open-source checkpoint (`remote-sensing-Qwen2.5-VL-3B-Instruct`). Team-owned fine-tuning, custom LoRA adaptation, or weight training on Indian EO data was not performed (Requirement #5 remains PARTIAL / OPEN). | *"We evaluated an existing domain-adapted remote sensing VLM zero-shot; custom fine-tuning on Indian satellite data is our next roadmap milestone."* |
| ❌ *"Production-ready operational disaster-damage assessment system."* | SatQuery AI is a functional, architecturally hardened engineering prototype/MVP, not an operationally certified emergency dispatch or disaster damage quantification platform. | *"SatQuery AI provides an operational MVP demonstrating automated multi-modal analysis with verifiable visual evidence."* |
| ❌ *"Universal real-world temporal change accuracy beyond the benchmark."* | Change detection was evaluated solely on an $N=20$ subset of LEVIR-CD using an unsupervised distance metric. It does not generalize unconditionally to all global or Indian terrain changes. | *"Our change detection engine was benchmarked on an N=20 slice of LEVIR-CD building pairs with full metric transparency."* |
| ❌ *"Validated on authentic ISRO Cartosat-2S and RISAT-1A operational satellite data."* | While data access procedures have been documented, authentic ISRO SAC data has not been ingested; synthetic dual-sensor proxies were used for integration validation. | *"Our cross-modal engine was validated on dual-sensor radiometric proxies while official ISRO/SAC data access is being formalized."* |
| ❌ *"Real-time concurrent multi-model parallel inference."* | Models are intentionally serialized via GPU locking to prevent memory exhaustion on local 8 GB hardware. | *"SatQuery AI incorporates GPU-aware serialization ensuring zero OOM errors on consumer-grade laptop GPUs."* |
