# SatQuery AI — Evaluator Technical FAQ (Phase 9)

**Document Purpose**: Direct, authoritative answers to critical evaluator and jury questions regarding system architecture, agent design, confidence semantics, benchmark findings, hardware constraints, and scientific limitations.

---

### Q1: Why is this system "agentic"?
**Answer**: SatQuery AI is agentic because it autonomously:
1. Translates unstructured natural language queries from non-technical users into structured operational goals.
2. Dynamically decides which specialized model or analytical tool (`VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`) is best suited to satisfy the query.
3. Automatically maps inputs, validates parameters against a firewall, orchestrates execution, and composes multi-modal outputs (text, bounding boxes, heatmaps, telemetry).
Unlike unconstrained LLM loops, SatQuery AI implements a **controllable agent paradigm**: its action space is strictly bounded by a typed, pre-registered tool schema to eliminate hallucinations and arbitrary code execution.

---

### Q2: Why not simply use one unified VLM for everything?
**Answer**: Modern VLMs (such as Qwen2.5-VL) are powerful vision-language generalists, but remote sensing demands specialized computational capabilities that general VLMs cannot perform natively:
1. **Pixel-Level Bi-Temporal Change Detection**: Autoregressive VLMs lack spatial differencing heads to generate exact $256 \times 256$ binary change masks across two co-registered temporal passes. Siamese deep feature differencers execute this in $<30\text{ ms}$.
2. **Radar Microwave Backscatter Physics**: General VLMs are trained predominantly on visible RGB spectra and lack inductive biases for SAR speckle, dielectric constants, and radar cross-sections.
3. **Latency & Compute**: Running a 3B VLM for every single spatial query consumes ~50 seconds per query on 8 GB GPUs. Routing grounding queries to `grounding-dino-tiny` takes ~8 seconds, and change detection takes $<1\text{ second}$. A multi-specialist architecture optimizes both accuracy and latency.

---

### Q3: How is tool selection controlled and deterministic?
**Answer**: The Agent Router (`backend/app/agent/router.py`) uses a rule-guided, semantic pattern matcher with keyword-intent scoring. It evaluates query verbs (e.g. *"detect changes"*, *"locate ships"*, *"what is shown"*), required input assets (single image vs T1/T2 pair vs optical+SAR), and optional user task hints. If the query is ambiguous (e.g. *"process this"*), the router refuses to guess and returns `NEEDS_CLARIFICATION` in $<20\text{ ms}$.

---

### Q4: How do you prevent arbitrary or malicious tool execution?
**Answer**: SatQuery AI employs three layers of pre-model defense:
1. **Predefined Tool Registry**: The agent can only dispatch to tools explicitly registered in `backend/app/agent/registry.py`. Unregistered requests (e.g., shell commands or external scripts) are rejected immediately with `UNREGISTERED_TOOL`.
2. **Pre-Model Parameter Firewall**: Every tool defines a whitelist of allowed parameters, valid types, and numerical ranges (e.g., `threshold` between `0.1` and `0.9`). Unauthorized keys (such as injection attacks) are rejected in $<20\text{ ms}$ before any GPU model is loaded.
3. **Input Validation**: Uploaded binaries are verified for raster integrity via PIL/Rasterio before invoking neural networks.

---

### Q5: What does "confidence" actually mean in your system?
**Answer**: Confidence in SatQuery AI is **strictly uncalibrated** and has distinct semantic meanings per tool:
- **VQA**: Confidence is explicitly `null` / unavailable. Autoregressive token decoding produces natural language; we refuse to fabricate an uncalibrated scalar percentage.
- **Visual Grounding**: Reflects the post-processed cross-attention logit similarity ($37.3\%$) from the Swin Transformer backbone. It is **uncalibrated** and does **not** represent spatial localization accuracy or Intersection-over-Union (IoU).
- **Change Detection**: Represents the **heuristic area stability margin** (the proportion of the scene remaining unchanged, e.g. $97.4\%$). It does **not** represent classification F1-score or precision.
- **Optical-SAR**: Represents a **pipeline integrity indicator** ($1.0$ on valid matrix dimension matching and Pearson $r$ correlation). It does **not** measure target classification probability.
*We strictly prohibit calling these heuristic values "model accuracy" or "calibrated probabilities".*

---

### Q6: What empirical benchmark evidence do you have?
**Answer**: We evaluated SatQuery AI on genuine public remote-sensing benchmark slices (Seed 42) with zero metric fabrication:
1. **LEVIR-CD ($N=20$ building change pairs, $256 \times 256$ px)**:
   - **Macro Change IoU**: `0.0878` (Micro IoU: `0.1113`)
   - **Macro F1-Score**: `0.1535` (Micro F1: `0.2002`)
   - **Macro Precision**: `0.1237` | **Macro Recall**: `0.6755`
   - **Mean Latency**: `27.4 ms` per pair
2. **RSVQA-LR ($N=20$ Sentinel-2 low-resolution VQA samples)**:
   - **Exact Match (EM)**: `35.0%` (7 / 20 canonical answers matched)
   - **Mean Token F1**: `0.2525`
   - **Mean Latency**: `50.11 s` (Median: `49.60 s`)
   - **Failures / OOM Events**: `0 / 20` (100% completion rate)
3. **Automated Regression**: 10/10 failure tests PASS, 11/11 orchestration tests PASS, 8/8 live API contract tests PASS.

---

### Q7: Why is VQA latency ~50 seconds?
**Answer**: The VQA backbone is `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`, a full 3-Billion-parameter vision-language model. On our local target evaluation machine (an NVIDIA GeForce RTX 5050 Laptop GPU with ~8 GB VRAM), the model allocates ~6.2 GB of VRAM with CPU offloading. Autoregressive text generation requires multiple sequential forward passes per token. We prioritized deploying a genuine domain-adapted remote-sensing VLM on consumer hardware over a lightweight toy model, and we display live elapsed time honestly in the UI.

---

### Q8: Why is Requirement #5 (VLM Adaptation / Fine-Tuning) marked PARTIAL / OPEN?
**Answer**: Scientific honesty is our top priority. We successfully integrated and benchmarked an open-source domain-adapted remote-sensing VLM (`remote-sensing-Qwen2.5-VL-3B-Instruct`) zero-shot on RSVQA-LR. However, **custom team-owned fine-tuning, training scripts, LoRA adapter weights, and parameter updates on Indian EO satellite data (Cartosat/Resourcesat) have not yet been performed**. Rather than fabricating a toy training loss curve, we transparently classify Requirement #5 as **PARTIAL / OPEN** and document it as an active post-hackathon development milestone.

---

### Q9: Why did you use proxy SAR for Optical-SAR testing?
**Answer**: Authentic spaceborne multi-sensor co-registered imagery (e.g. ISRO Cartosat-2S optical fused with RISAT-1A SAR) is restricted under institutional data licensing agreements and requires formal institutional clearances. To validate our dual-stream ingestion pipeline, radiometric normalization algorithms, and Pearson cross-modal correlation mathematics, we tested with physically modeled radar backscatter proxies (`proxy_sar`) reflecting corner reflection, surface roughness, and dielectric contrast. We explicitly label this proxy in the UI and never claim authentic ISRO data evaluation.

---

### Q10: What happens if a user submits invalid or malicious input?
**Answer**: The system rejects invalid inputs in $<20\text{ ms}$ at Stage 1 (`INPUT_VALIDATION`) or Stage 2 (`ROUTER`) before invoking heavy GPU models:
- Corrupted or non-image binaries: Rejected with `INVALID_IMAGE` (4.1–6.8 ms).
- Missing secondary images (e.g. Change Detection without T2): Rejected with `INVALID_INPUT` (24 ms).
- Parameter injection attacks (e.g. unauthorized flags): Trapped by the parameter firewall and stripped with `INVALID_PARAMETER` (0.65–3.5 ms).
- Ambiguous queries (e.g. *"process this"*): Returns `NEEDS_CLARIFICATION` with suggestions.
In all cases, GPU memory remains untouched and zero crashes occur.

---

### Q11: How would SatQuery AI scale beyond a single local GPU in production?
**Answer**: The architecture is already decoupled for horizontal cloud scaling:
1. **Asynchronous Task Workers**: FastAPI can dispatch requests to a Celery/RabbitMQ job queue with dedicated GPU worker pools.
2. **Model Specialization by Worker**: Heavy 3B VLM workers can run on dedicated A10G/A100 instances, while lightweight ResNet/DINO tasks run on high-throughput T4 or CPU nodes.
3. **vLLM / TensorRT-LLM Serving**: Serving Qwen2.5-VL via vLLM with PagedAttention and FP8 quantization would reduce VQA latency from ~50s to $<3\text{s}$.
4. **Tile Chipping for Large Rasters**: Large gigapixel satellite mosaics can be chipped into $512 \times 512$ sliding windows with spatial indexing (PostGIS).

---

### Q12: What would you improve after the hackathon?
**Answer**:
1. **In-Domain LoRA Fine-Tuning (Requirement #5)**: Implement parameter-efficient LoRA fine-tuning on Indian EO datasets (Cartosat-2S / Resourcesat-2) to improve fine-grained numeric counting and regional land-use classification.
2. **In-Domain Change Segmentation Head**: Replace unsupervised ResNet-18 feature differencing with a supervised ChangeFormer or BIT (Bitemporal Image Transformer) trained on LEVIR-CD+ to boost change F1 score from 0.1535 to $>0.80$.
3. **Authentic ISRO Multi-Sensor Ingestion**: Ingest genuine co-registered Cartosat-2S and RISAT-1A SAR datasets once institutional data access is finalized.
4. **Model Quantization**: Quantize Qwen2.5-VL-3B to AWQ / INT4 to achieve sub-10-second response times on 8 GB consumer laptop GPUs.
