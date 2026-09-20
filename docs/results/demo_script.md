# SatQuery AI — Evaluator Demonstration Script (Phase 9)

**Target Presentation Window**: 5 to 7 minutes (Smart India Hackathon Jury Pitch)  
**System Location**: React UI at `http://127.0.0.1:5173` | FastAPI Backend at `http://127.0.0.1:8000`  
**Execution Profile**: Live Single-GPU Execution on NVIDIA GeForce RTX 5050 Laptop (~8 GB VRAM)  
**Governing Authority**: Strictly constrained to claims defined in [`docs/results/demo_claims_matrix.md`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/demo_claims_matrix.md)

---

### Opening — 20 Seconds: What SatQuery AI Is

> *"Respected Evaluators, Earth Observation analysis today is fragmented. Analysts must switch between manual GIS software, brittle pipelines, or unconstrained LLMs that hallucinate tools and leak memory.*
> 
> ***SatQuery AI is a controllable agentic analysis engine for multi-modal remote sensing.***
> *Instead of an unconstrained LLM loop, SatQuery AI pairs a sub-millisecond intent router with four specialized remote-sensing model backbones under an enforced parameter firewall, generating observable execution traces and verifiable spatial visual evidence on consumer hardware."*

---

### Demo 1 — Single-Image VQA (Visual Question Answering)

**1. User Action**:
- In the UI, click **`Demo A: VQA`** under the Evaluator Quick Presets bar.
- *What Happens*:
  - Automatically populates the Primary Image with `sample_satellite_port.jpg` (commercial optical satellite harbor scene).
  - Sets query: *"What type of maritime port or facility is shown in this satellite image?"*
  - Sets Mode: `VQA`.
- Click **Run Satellite Analysis**.

**2. Observable Execution State**:
- Point out the **Live Elapsed Stopwatch** and hardware notice:
  - *"Notice the hardware lock status. Our backend enforces sequential GPU locking (`_GPU_EXECUTION_LOCK`). Because our VQA backbone is `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`, autoregressive generation takes ~50 seconds on this 8 GB laptop GPU. Rather than hiding this latency, we provide honest real-time feedback."*

**3. System Response & Evidence**:
- Once complete, direct attention to:
  - **Analytical Assessment**: Comprehensive description identifying the harbor breakwaters, coastline, and maritime facilities.
  - **Confidence Semantics**: Highlight the **Unavailable / Null** confidence badge:
    *"Notice we do not fabricate a fake 99% accuracy score. Autoregressive language generation produces natural language dialogue; no token probability is fabricated."*
  - **Observable Execution Trace**: Expand the 5-stage trace drawer:
    `INPUT_VALIDATION (4.8ms)` → `ROUTER (12.3ms)` → `TOOL_EXECUTION (50.2s)` → `EVIDENCE (3.1ms)` → `RESULT_COMPOSITION (0.9ms)`.

---

### Demo 2 — Bi-Temporal Change Detection

**1. User Action**:
- Click **`Demo C: Change`** under Evaluator Quick Presets.
- *What Happens*:
  - Populates Baseline T1 with `sample_satellite_port.jpg`.
  - Populates Post-Event T2 with `sample_satellite_port_t2_synthetic.jpg`.
  - Sets query: *"Identify differences and what changed between these two images"*.
- Click **Run Satellite Analysis**.

**2. System Response & Evidence (Sub-Second Execution)**:
- Execution finishes in $<1\text{ second}$ (~500 ms).
- Direct attention to:
  - **3-Panel Comparative Layout**: Shows T1 Baseline, T2 Post-Event, and the generated **Differential Change Heatmap** artifact (`change_detection_execution_artifact.jpg`).
  - **Quantitative Metrics Table**: Displays 8,848 changed pixels ($2.56\%$) at Euclidean feature distance threshold $\tau=0.42$.
  - **Confidence Semantics**: Highlight the **Area Stability Margin (97.4%)**:
    *"Notice the transparent definition: 97.4% is the proportion of unchanged background area, NOT a claim of 97% classification F1 or IoU."*
  - **Evaluation Disclaimer**: Point to the disclaimer:
    *"This demo utilizes a controlled synthetic temporal pair for integration verification; our empirical benchmark on LEVIR-CD achieved 0.1535 Macro F1 and 0.0878 Macro IoU without in-domain fine-tuning."*

---

### Demo 3 — Optical + SAR Cross-Modal Radiometric Fusion

**1. User Action**:
- Click **`Demo D: Optical+SAR`** under Evaluator Quick Presets.
- *What Happens*:
  - Populates Optical Sensor with `sample_satellite_port.jpg`.
  - Populates SAR Microwave Radar with `sample_sentinel1_sar_mauritius.jpg`.
  - Sets query: *"Analyze optical and SAR radar cross-modal backscatter imagery"*.
- Click **Run Satellite Analysis**.

**2. System Response & Multi-Sensor Telemetry**:
- Execution completes in $<300\text{ ms}$.
- Direct attention to:
  - **Multi-Sensor 3-Panel Ingestion**: Optical RGB alongside microwave SAR backscatter and the resulting **Radiometric Synergy Composite** (`optical_sar_execution_artifact.jpg`).
  - **Dual-Stream Radiometric Statistics**: Optical Mean=78.67, SAR Mean=79.96, Cross-Modal Pearson correlation $r=0.574$, and 28,276 radar-dominant anomaly pixels.
  - **Pipeline Integrity Metric**: Confirms matrix dimension matching and radiometric normalization (100% completion status; not target prediction accuracy).
  - **Data Classification Notice**:
    *"We explicitly label this asset as `proxy_sar`. Authentic ISRO/SAC Cartosat-2S and RISAT-1A co-registered spaceborne pairs remain restricted under institutional data licensing; our dual-stream ingestion math is verified on physically modeled radar backscatter proxies."*

---

### Optional Step — Visual Grounding Referring Expression Localization

**1. User Action**:
- Click **`Demo B: Grounding`**.
- Sets query: *"Locate the ships in this satellite image."*
- Click **Run Satellite Analysis**.

**2. System Response & Bounding Boxes**:
- Finishes in ~8 seconds via `IDEA-Research/grounding-dino-tiny`.
- Direct attention to:
  - **Annotated Bounding Box Overlay**: Renders tight bounding box overlay around harbor vessels (`grounding_execution_artifact.jpg`).
  - **Detector Logit Score**: Displays uncalibrated cross-attention score ($37.3\%$) with explicit caveat:
    *"This score indicates cross-attention feature similarity from the Swin Transformer backbone; it is NOT calibrated and does NOT represent spatial localization accuracy or IoU."*

---

### Demo 4 (Safety Test) — Parameter Firewall & Ambiguity Interception

**1. User Action**:
- Click **`Safety & Firewall`** preset (or enter *"calculate orbital trajectory"*).
- Click **Run Satellite Analysis**.

**2. System Response**:
- Direct attention to the immediate ($<20\text{ ms}$) rejection banner:
  *"Notice the immediate response: status `NEEDS_CLARIFICATION`. The agent router detected ambiguous/unsupported intent and provided clarification prompts without invoking heavy GPU models, protecting VRAM."*
- Mention that malicious parameter injections (e.g. `unauthorized_key`) are similarly trapped and stripped at the pre-model firewall.

---

### Closing — 45 Seconds: Rigorous Engineering & Roadmap

> *"To summarize what you have seen today in SatQuery AI:
> 
> 1. **Controllable Agentic Routing**: Autonomous tool selection strictly bounded within an allowlisted Tool Registry and sub-millisecond parameter firewall.
> 2. **Evidence-First Architecture**: Every query returns structured text, spatial visual artifacts, and an observable execution trace.
> 3. **Hardware-Safe Serialization**: Zero CUDA OOM crashes on consumer laptop hardware through GPU locking.
> 4. **Empirical Public Benchmarking**: Evaluated on genuine public benchmark slices—35.0% EM on RSVQA-LR and 0.1535 Macro F1 on LEVIR-CD.
> 5. **Scientific Honesty on Requirement #5**: While we successfully integrated and benchmarked an open-source remote-sensing VLM checkpoint, **Requirement #5 (custom team-owned fine-tuning on Indian EO data) explicitly remains PARTIAL / OPEN** as our post-hackathon milestone.
> 
> *Thank you. We welcome your questions."*
