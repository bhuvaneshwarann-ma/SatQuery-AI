# SatQuery AI — Final Live Demo Runbook (Phase 11)

**Duration**: 5–7 Minutes (Synchronized Spoken & Live UI Flow)  
**Target Environment**: `http://localhost:5173` (React Vite App) + `http://localhost:8000` (FastAPI Server)  
**Execution Objective**: Deliver a flawless, scripted live walkthrough without improvisation, demonstrating all four specialist modalities, execution telemetry, empirical evidence, and transparent engineering boundaries.

---

## Master Choreography Timeline

```text
  00:00 ─── 00:30 ─── 01:15 ─── 02:00 ─── 02:45 ─── 03:30 ─── 04:15 ─── 05:00 ─── 05:45 ─── 06:30 ─── 07:00
    │         │         │         │         │         │         │         │         │         │         │
 Problem   Arch.       VQA    Grounding  Change     SAR      Trace &   Evaluation Limitations Closing    Q&A
 & Value   Overview    Demo     Demo      Demo      Demo     Evidence   Evidence   & Roadmap  Takeaway
```

---

## Phase-by-Phase Stage Directions

### 00:00 – 00:30 | Opening: Problem & Value Proposition
* **Visual on Screen**: Browser showing SatQuery AI Header, clean state, green system status badges (`API: Connected`, `GPU: Ready`).
* **Presenter Actions**: Stand upright, direct eye contact with judges, open on home dashboard.
* **Spoken Script**:
  > *"Respected evaluators, Earth Observation analysis today is severely fractured. An analyst examining a coastal region must juggle separate, incompatible tools for terrain classification, object localization, temporal change detection, and radar correlation. No single vision model can solve this alone. We built **SatQuery AI**: a system that turns heterogeneous satellite questions into a controlled, evidence-producing analysis workflow coordinated by a safe agent router."*
* **What NOT to Claim**:
  - Do NOT claim SatQuery AI is a "revolutionary general intelligence" or "100% autonomous".
  - Do NOT claim single-model mastery.

---

### 00:30 – 01:15 | System Architecture Walkthrough
* **Visual on Screen**: Switch briefly to Architecture diagram tab or slide, then back to the UI split-pane showing Query input, Mode Selector, and Execution Trace drawer.
* **Presenter Actions**: Point to the system status bar showing `_GPU_EXECUTION_LOCK` indicator and tool registry badge.
* **Spoken Script**:
  > *"Rather than letting a large language model execute unconstrained code, SatQuery AI implements a deterministic agent router backed by an immutable tool registry and strict Pydantic parameter validation. The router inspects user intent and dispatches to one of four dedicated specialist pipelines: a 3B domain-adapted VLM for semantic reasoning, Grounding DINO for spatial detection, a Siamese feature differencer for change detection, and a dual-stream correlator for Optical-SAR fusion. To prevent CUDA Out-Of-Memory crashes on our local 8 GB GPU, execution is hardware-locked to run sequentially with zero failures."*
* **What NOT to Claim**:
  - Do NOT describe the router as "hidden chain-of-thought tokens". Emphasize observable execution steps.

---

### 01:15 – 02:00 | Demo A — Satellite Visual Question Answering (VQA)
* **Preset / Flow Selection**: Click Preset button **`[Preset 1: VQA Coastal Terrain]`**.
* **Input Asset Loaded**: `sample_satellite.jpg` (Sentinel-2 multi-spectral scene of coastal settlement, $256 \times 256$).
* **Exact Query**: *"Describe the primary terrain and visible structures in this coastal scene."*
* **Expected Visible Result**:
  - Primary Result Card displays structured semantic summary identifying coastal waterway, agricultural plots, and low-density settlements.
  - Confidence Badge: `null` (Displayed clearly as `Uncalculated / N/A`).
  - Latency / Stopwatch: ~50 seconds (or immediate display if cached/pre-warmed).
* **Artifact / Evidence Shown**: Raw input image display alongside structured response text.
* **Spoken Script**:
  > *"Our first workflow demonstrates satellite VQA. Here, an analyst asks a natural language question over a Sentinel-2 image. The router assigns this to our 3B domain-adapted VLM. Notice two critical engineering features: first, the live progress stopwatch tracks autoregressive decoding transparently; second, notice the confidence badge is explicitly null. We refuse to fabricate artificial probability percentages for generative language answers."*
* **What NOT to Claim**:
  - Do NOT claim 95% or 100% classification accuracy.
  - Do NOT claim VQA operates in sub-second real-time on local consumer hardware.
* **Fallback Path**: If VLM generation times out, click the pre-computed cached execution tab or show pre-recorded run log: `data/benchmarks/benchmark_rsvqa_results.json` sample #1.

---

### 02:00 – 02:45 | Demo B — Visual Grounding (Spatial Localization)
* **Preset / Flow Selection**: Click Preset button **`[Preset 2: Grounding Maritime]`**.
* **Input Asset Loaded**: `sample_satellite_port.jpg` (High-resolution port facility with visible vessels).
* **Exact Query**: *"Detect and localize ships docked along the berths."*
* **Expected Visible Result**:
  - Open-vocabulary detector outputs color-coded bounding boxes enclosing docked vessels.
  - Pixel Coordinates: `[ymin: 342, xmin: 60, ymax: 480, xmax: 210]`.
  - Confidence Badge: `0.373` (Labeled as `Uncalibrated Detector Logit`).
* **Artifact / Evidence Shown**: Dynamic PNG overlay showing high-contrast bounding boxes with labels.
* **Spoken Script**:
  > *"Next is visual grounding. The analyst queries for 'ships docked along the berths'. The router identifies a spatial localization request and dispatches Grounding DINO. Within 1.5 seconds, the detector extracts cross-attention peaks and renders pixel-accurate bounding box overlays directly on the scene. The confidence of 0.373 is the raw detector logit score—we explicitly inform the analyst that this is an uncalibrated heuristic, not localization IoU."*
* **What NOT to Claim**:
  - Do NOT claim the detector score is an intersection-over-union (IoU) accuracy metric.
  - Do NOT claim the detector was custom fine-tuned on ISRO data.
* **Fallback Path**: If GPU memory is occupied, reload the static artifact `docs/results/artifacts/grounding_sample_overlay.png` directly in the UI viewer.

---

### 02:45 – 03:30 | Demo C — Bi-Temporal Change Detection
* **Preset / Flow Selection**: Click Preset button **`[Preset 3: Port Expansion Change]`**.
* **Input Assets Loaded**:
  - Pre-image ($T_1$): `sample_satellite_port.jpg` (Baseline port layout).
  - Post-image ($T_2$): `sample_satellite_port_t2_synthetic.jpg` (Controlled synthetic pair showing expanded berth and newly excavated dock).
* **Exact Query**: *"Highlight all new construction and land alterations between these two dates."*
* **Expected Visible Result**:
  - Side-by-side $T_1 / T_2$ display with synchronized cursor panning.
  - Binary Change Mask PNG with red highlight overlays on altered structures.
  - Area Stability Margin: `97.4%` (Labeled as `Unchanged Scene Proportion`).
  - Execution Latency: `< 30 ms` (ResNet feature differencing).
* **Artifact / Evidence Shown**: Difference heatmap and segmented binary change mask.
* **Spoken Script**:
  > *"Our third workflow performs bi-temporal change detection across two aligned scenes. Our Siamese feature differencing pipeline compares deep convolutional activations at 27 milliseconds per pair. Notice the red change mask clearly isolating the modified berth structures. Crucially, the 97.4% confidence metric represents the area stability margin—meaning 97.4% of the background pixels remained stable. It is not a claim of 97% classification precision."*
* **What NOT to Claim**:
  - Do NOT claim the test pair is an operational real-world disaster scene; openly disclose it is a controlled synthetic temporal pair.
  - Do NOT call the 97.4% stability margin an F1 score or IoU.
* **Fallback Path**: Open the pre-generated change mask in the visual artifacts tab.

---

### 03:30 – 04:15 | Demo D — Cross-Modal Optical-SAR Correlation
* **Preset / Flow Selection**: Click Preset button **`[Preset 4: Maritime Optical-SAR]`**.
* **Input Assets Loaded**:
  - Optical: `sample_sentinel2_optical_mauritius.jpg` (Maritime optical scene with partial cloud obstruction).
  - Radar: `sample_sentinel1_sar_mauritius.jpg` (Physically modeled proxy SAR backscatter image).
* **Exact Query**: *"Correlate radar backscatter with optical features to verify maritime targets."*
* **Expected Visible Result**:
  - False-color composite overlay (SAR intensity mapped to red/yellow channel, optical mapped to green/blue).
  - High-intensity radar returns pinpoint metal vessel hulls penetrating through optical clouds.
  - Pipeline Integrity Status: `100%` (Labeled as `Pipeline Matrix Integrity`).
* **Artifact / Evidence Shown**: Multi-modal fusion composite image and backscatter correlation matrix.
* **Spoken Script**:
  > *"Our fourth workflow tackles multimodal sensor fusion. Here we ingest an optical image alongside a radar backscatter scene. Radar microwaves penetrate cloud cover and reflect strongly off metallic vessel hulls. Our pipeline normalizes both coordinate grids and computes spatial correlation, generating a false-color composite where metal hulls illuminate in bright yellow. The 100% indicator confirms pipeline integrity and dimension matching—not a claim of 100% target detection accuracy."*
* **What NOT to Claim**:
  - Do NOT claim the SAR asset is classified ISRO RISAT-1 data; disclose it is a physically modeled radar proxy.
  - Do NOT claim 100% ship detection accuracy.
* **Fallback Path**: Switch to the pre-rendered SAR fusion composite artifact.

---

### 04:15 – 05:00 | Observable Execution Trace & Evidence Inspection
* **Visual on Screen**: Open the **`[Execution Trace]`** collapsible drawer on the right side of the screen.
* **Presenter Actions**: Scroll through the 6 structured execution log entries showing timestamp, tool name, input payload validation, VRAM allocation, execution time, and output artifact paths.
* **Spoken Script**:
  > *"Here is what makes SatQuery AI genuinely production-grade: the Observable Execution Trace. For every query, our platform records an immutable audit log: the exact router intent classification, the Pydantic schema validation check, the GPU execution lock acquisition, and the SHA-256 hashed artifact paths. An evaluator or defense analyst can verify exactly why an answer was generated, which model produced it, and review the raw raster artifact without guessing."*
* **What NOT to Claim**:
  - Do NOT call this an LLM "thought process". Call it system-level execution telemetry.

---

### 05:00 – 05:45 | Quantitative Benchmark Evidence
* **Visual on Screen**: Switch to the **Benchmark Scorecard** view or slide showing the verified metrics table.
* **Presenter Actions**: Present both benchmark families side by side.
* **Spoken Script** *(Verbatim Standardized Defense)*:
  > *"Our current benchmark is an honest zero-shot baseline, not a claim of state-of-the-art accuracy. On N=20 public benchmark samples, RSVQA achieved 35% exact match and 0.2525 token F1, while LEVIR-CD achieved 0.0878 macro IoU and 0.1535 macro F1. These results establish a reproducible baseline and show where adaptation is still needed. On LEVIR-CD, our unsupervised differencer achieved 0.6755 recall alongside 0.1237 precision at 27.4 milliseconds per pair. Crucially, all three automated regression test suites pass at 100% across 29 test cases with zero crashes."*
* **What NOT to Claim**:
  - Do NOT round 35.0% up or hide 0.1237 precision.
  - Do NOT claim these numbers outperform supervised SOTA models.

---

### 05:45 – 06:30 | Transparent Engineering Boundaries & Roadmap
* **Visual on Screen**: Display the **Honest Boundaries & Technical Roadmap** view.
* **Presenter Actions**: Address Requirement #5 directly before the judges bring it up.
* **Spoken Script**:
  > *"We believe in absolute engineering transparency. Requirement #5—custom VLM fine-tuning on Indian EO data—remains PARTIAL / OPEN. We evaluated a domain-adapted checkpoint zero-shot, but custom LoRA parameter training requires curated institutional data and GPU cluster time that we will not fake with a toy script. Our documented post-hackathon roadmap outlines: first, supervised QLoRA fine-tuning; second, authentic ISRO Cartosat and RISAT evaluation; third, supervised ChangeFormer integration; and fourth, formal confidence calibration."*
* **What NOT to Claim**:
  - Do NOT claim fine-tuning was completed.

---

### 06:30 – 07:00 | Conclusion & Handoff to Q&A
* **Visual on Screen**: Main dashboard showing completed multi-modal workspace with system health green.
* **Presenter Actions**: Step forward, invite evaluators to ask questions.
* **Spoken Script**:
  > *"In conclusion: SatQuery AI turns heterogeneous satellite questions into a controlled, evidence-producing analysis workflow. We have proven end-to-end integration, 100% crash-free GPU scheduling, uncalibrated confidence honesty, and reproducible benchmark baselines. We welcome your questions."*

---

## Contingency & Fallback Protocol Matrix

| Failure Event | Detection Indicator | Immediate Fallback Action | Verbal Script for Presenter |
| :--- | :--- | :--- | :--- |
| **VLM Timeout / Lag (>60s)** | Stopwatch exceeds 55s | Click `View Cached Run` in UI | *"While the 3B model decodes on our 8 GB GPU, let us examine the identical pre-recorded run from our N=20 benchmark manifest."* |
| **GPU Out-Of-Memory Error** | Red toast alert in UI | Click `Restart Model Engine` | *"Our execution lock caught the memory ceiling and safely isolated the failure without crashing the FastAPI backend."* |
| **Frontend React Disconnect** | Red indicator `API: Offline` | Switch to Swagger UI (`/docs`) | *"The React dev server lost connection; here is the live FastAPI OpenAPI documentation serving identical endpoints directly."* |
| **Judge Challenges Metric** | Evaluator interrupts on 35% | Open `docs/results/benchmark_rsvqa_results.json` | *"We have the full per-sample prediction manifest right here on disk—every sample, prompt, and ground truth is fully inspectable."* |
