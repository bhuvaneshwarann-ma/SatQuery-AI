# SatQuery AI — Evaluation Asset Inventory (Phase 8B)

This inventory records all data assets, benchmark files, validation artifacts, and evaluation scripts currently present in the SatQuery AI repository. It strictly documents modality, provenance, ground-truth availability, and authentic evaluation status without assumptions or fabricated metrics.

---

## 1. Imagery & Sensor Assets (`data/samples/`)

| Asset Name | Modality | Sensor / Source | Status | Resolution / Dimensions | Ground Truth Available? | Intended Evaluation Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sample_satellite_port.jpg` | Optical RGB | NASA Earth Observatory (Landsat 9 OLI-2, Rio Grande, Brazil) | **Real** Satellite Asset | 720 × 480 px (JPEG) | **No** (Qualitative visual evidence only; no paired reference QA annotations or bounding box ground-truth labels) | VQA real-scene description, Grounding spatial localization pipeline test, Change Detection T1 baseline, Optical-SAR optical baseline. |
| `sample_satellite_port_t2_synthetic.jpg` | Optical RGB | Synthetic derivation from `sample_satellite_port.jpg` | **Controlled Synthetic** | 720 × 480 px (JPEG) | **Deterministic delta** (Synthetic pixel modifications; not an operational multi-pass ground-truth dataset) | Bi-temporal change detection pipeline verification, differential feature extraction, spatial mask generation. |
| `sample_satellite_port_proxy_sar.png` | Microwave Radar Backscatter (Simulated) | Physically modeled synthetic radar backscatter | **Proxy SAR** | 720 × 480 px (PNG) | **No** (Simulated backscatter with synthetic coherent speckle and corner reflection) | Optical-SAR multi-sensor ingestion, cross-modal Pearson correlation analysis, radiometric normalization testing. |
| `sample_sentinel1_sar_mauritius.jpg` | Spaceborne SAR (C-band Radar) | ESA Copernicus Sentinel-1 IW (Mauritius scene) | **Real** Spaceborne SAR | 720 × 480 px (JPEG) | **No** (Unregistered geographic reference; not co-registered with `sample_satellite_port.jpg`) | Non-coregistered spaceborne SAR reference asset; demonstrates genuine radar texture and speckle characteristics. |

---

## 2. Evaluation Scripts & Suites (`ai/evaluation/`)

| Script File | Target Capability | Evaluation Scope | Ground-Truth Dependent? | Metrics Reported |
| :--- | :--- | :--- | :--- | :--- |
| `test_vlm_loading.py` | VQA (AdaptLLM Qwen2.5-VL-3B) | Hardware loading & BF16 CPU offload | No | Load time, memory residency, CUDA memory allocation. |
| `test_real_satellite_vqa.py` | VQA (AdaptLLM Qwen2.5-VL-3B) | Domain vocabulary & inference execution | No | Response latency, domain vocabulary alignment, memory stability. |
| `test_grounding.py` | Grounding (Grounding DINO Tiny) | Coordinate box detection across 5 prompts | No | Detection count, confidence score range, execution latency. |
| `test_change_detection.py` | Change Detection (Siamese ResNet18) | Differential distance feature differencing | No (Synthetic test) | Changed pixel count, change area percentage, inference latency. |
| `test_optical_sar.py` | Optical-SAR (Dual-Stream Engine) | Cross-modal statistical correlation | No (Proxy SAR) | Optical stats, SAR backscatter stats, Pearson $r$, radar anomaly count. |
| `test_vqa_execution.py` | VQA Execution Integration | ToolResult schema & error contracts | No | Execution status, latency, error contract compliance. |
| `test_grounding_execution.py` | Grounding Execution Integration | ToolResult schema & box evidence contract | No | Execution status, bounding box payload structure, confidence. |
| `test_change_execution.py` | Change Detection Execution Integration | ToolResult schema & heatmap artifact | No | Execution status, changed pixel payload, synthetic note check. |
| `test_optical_sar_execution.py` | Optical-SAR Execution Integration | ToolResult schema & synergy overlay | No | Execution status, optical/SAR stats, proxy classification check. |
| `test_agent_router.py` | Deterministic Agent Router | Intent classification & parameter firewall | Yes (Unit test fixtures) | 12 / 12 test assertions (routing status, parameter sanitation). |
| `test_agent_orchestration.py` | End-to-End Orchestrator | Complete 5-stage pipeline across 4 tools | No | 11 / 11 test scenarios, latency, observable trace completeness. |
| `test_backend_api.py` | FastAPI HTTP/Multipart API | Live endpoint validation (Tests A–E, Health) | No | HTTP status codes, structured JSON contract compliance. |
| `test_api_contract.py` | Production MVP API Hardening | Full 8-test API contract & VRAM telemetry | No | 8 / 8 tests passed, latency per tool, VRAM progression. |

---

## 3. Evidence Artifacts & Documentation (`docs/results/`)

| Artifact Path | Producing Engine | Content / Modality | Intended Demonstration Use |
| :--- | :--- | :--- | :--- |
| `grounding_execution_artifact.jpg` | `IDEA-Research/grounding-dino-tiny` | Optical RGB with coordinate bounding box overlay | Visual spatial evidence for visual grounding queries. |
| `change_detection_execution_artifact.jpg` | `Siamese-ResNet18-FeatureDifferencer` | 3-panel composite (T1, T2, Differential Mask) | Visual evidence of temporal changes between T1 and T2. |
| `optical_sar_execution_artifact.jpg` | `Dual-Stream Cross-Modal Engine` | 3-panel composite (Optical, SAR Backscatter, Synergy) | Multi-sensor visual evidence highlighting radar-dominant echoes. |
| `real_satellite_vqa_results.md` | Phase 3D Evaluation | VQA hardware observations, questions, answers | Documentation of VLM performance on Landsat 9 optical raster. |
| `grounding_validation_results.md` | Phase 3E Evaluation | Detection counts, confidence scores, VRAM stats | Documentation of zero-shot object detection capabilities. |
| `change_detection_validation_results.md` | Phase 3F Evaluation | Changed pixel metrics, synthetic pair limitation | Quantitative differencing report with synthetic data caveats. |
| `optical_sar_validation_results.md` | Phase 3G Evaluation | Radiometric stats, Pearson $r$, proxy caveats | Statistical evaluation with explicit proxy SAR disclosure. |

---

## 4. Ground-Truth & Benchmark Summary

* **Public Benchmark Datasets Currently Downloaded**: **None** (RSVQA, VRSBench, LEVIR-CD, and SEN1-2 are referenced in architecture specifications but have not been downloaded to conserve local storage and avoid non-reproducible bandwidth dependencies).
* **Current Evaluation Status**: **Integration & Algorithmic Pipeline Validation** across all 4 specialist tools is 100% verified. Formal benchmark accuracy scores (e.g. mAP@IoU, F1 score, Top-1 accuracy) are **pending ingestion of annotated ground-truth benchmark datasets**.
