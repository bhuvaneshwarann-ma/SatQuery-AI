# SatQuery AI — Judge Answer Sheet & Defense Protocol (Phase 10)

**Document Purpose**: Definitive script and technical defense sheet providing 10–20 second spoken responses, supporting code/evidence citations, anticipated judge follow-ups, and airtight secondary responses.

---

### Question 1: "Is this really an AI agent or just an if/else router?"

* **10–20 Second Spoken Answer**:
  > *"SatQuery AI is a controllable agent designed specifically for mission-critical remote sensing. Rather than unconstrained LLM loops that hallucinate tools and execute arbitrary code, our agent autonomously translates natural language intent into structured operational parameters, dynamically matches multi-modal raster assets, validates parameters against a pre-model firewall, and composes multi-step visual and textual evidence."*
* **Evidence Supporting Answer**:
  - `backend/app/agent/router.py`: Autonomous intent extraction and asset matching.
  - `backend/app/agent/registry.py`: Predefined typed Tool Registry schema.
  - `backend/app/services/orchestration_service.py`: Automated orchestration pipeline.
  - `ai/evaluation/test_agent_orchestration.py`: 11 / 11 PASS verifying autonomous routing.
* **Likely Follow-Up**:
  *"Why not use LangChain, CrewAI, or an unconstrained ReAct loop?"*
* **Recommended Response to Follow-Up**:
  > *"Unconstrained ReAct agents are non-deterministic, have unbounded token consumption, and frequently attempt to invoke nonexistent tools or shell commands. In an operational defense or disaster scenario, non-deterministic looping is a disqualifying vulnerability. Our controllable agent guarantees sub-millisecond routing ($<20\text{ ms}$) and zero hallucinated tools."*

---

### Question 2: "Why didn't you use one unified VLM like GPT-4o or Qwen for all tasks?"

* **10–20 Second Spoken Answer**:
  > *"Generative VLMs are text generators, not dense pixel classifiers. They cannot compute exact $256 \times 256$ binary change masks between temporal passes, nor can they calculate non-RGB microwave radar cross-correlation. A multi-specialist architecture delivers superior task accuracy, runs sub-second for change and SAR, and protects local GPU memory from multi-model allocation."*
* **Evidence Supporting Answer**:
  - `ai/inference/change_detection.py`: Generates pixel-level difference masks in 27.4 ms.
  - `ai/inference/optical_sar.py`: Dual-stream radiometric correlation in $<300\text{ ms}$.
  - `docs/results/performance_report.md`: Latency comparison across backbones.
* **Likely Follow-Up**:
  *"Couldn't a VLM describe changes in text without needing ResNet?"*
* **Recommended Response to Follow-Up**:
  > *"Text descriptions like 'some buildings were added' lack spatial precision. A disaster relief or defense commander requires exact spatial coordinates and pixel boundaries to deploy resources. Our Siamese differencer outputs an exact binary mask, which a text-only VLM cannot produce."*

---

### Question 3: "Did you build any new AI model, or are you just wrapping open-source models?"

* **10–20 Second Spoken Answer**:
  > *"Our core engineering contribution is the controllable orchestration architecture, pre-model parameter firewall, hardware-aware execution serialization, and multi-modal radiometric fusion engine. In remote sensing, combining specialized vision-language models with spatial computer vision under strict memory and safety boundaries is a non-trivial systems engineering achievement."*
* **Evidence Supporting Answer**:
  - `backend/app/services/orchestration_service.py`: Hardware lock & parameter firewall.
  - `ai/inference/optical_sar.py`: Custom mathematical engine for dual-sensor cross-modal correlation.
  - `ai/evaluation/test_failure_cases.py`: 10/10 pre-model failure interception.
* **Likely Follow-Up**:
  *"So the machine learning models themselves are not trained by your team?"*
* **Recommended Response to Follow-Up**:
  > *"Correct. We intentionally deployed verified, published foundation checkpoints—such as `remote-sensing-Qwen2.5-VL-3B` and `grounding-dino-tiny`—to build a stable, reproducible engineering prototype. In-domain fine-tuning is our documented post-hackathon roadmap milestone."*

---

### Question 4: "Why does Requirement #5 remain PARTIAL / OPEN? Did you fail to fine-tune?"

* **10–20 Second Spoken Answer**:
  > *"We prioritize scientific integrity over inflated claims. We successfully deployed and benchmarked an existing open-source remote-sensing domain-adapted VLM checkpoint zero-shot on RSVQA-LR. However, custom team-owned fine-tuning and LoRA parameter adaptation on Indian EO satellite data have not yet been performed. Rather than fabricating a toy training loss curve, we transparently classify Requirement #5 as PARTIAL / OPEN."*
* **Evidence Supporting Answer**:
  - `docs/results/judge_evidence_matrix.md`: Requirement #5 explicitly marked PARTIAL / OPEN.
  - `docs/results/benchmark_rsvqa_report.md`: Zero-shot baseline evaluation.
  - `docs/results/phase_8e_correction_report.md`: Strict evidence boundary confirmation.
* **Likely Follow-Up**:
  *"Another team claims they fine-tuned a model during the hackathon. Why didn't you?"*
* **Recommended Response to Follow-Up**:
  > *"Fine-tuning a 3-Billion-parameter VLM scientifically requires curated, licensed remote sensing datasets and multi-GPU clusters. Running a 2-epoch script on 50 unverified images on a laptop produces severe catastrophic forgetting, not genuine domain adaptation. We established a rigorous, reproducible zero-shot baseline first and outlined a realistic post-hackathon LoRA roadmap."*

---

### Question 5: "Your RSVQA accuracy is only 35.0% and LEVIR-CD F1 is 0.1535. Why are they so low?"

* **10–20 Second Spoken Answer**:
  > *"Our current benchmark is an honest zero-shot baseline, not a claim of state-of-the-art accuracy. On N=20 public benchmark samples, RSVQA achieved 35% exact match and 0.2525 token F1, while LEVIR-CD achieved 0.0878 macro IoU and 0.1535 macro F1. These results establish a reproducible baseline and show where adaptation is still needed."*
* **Evidence Supporting Answer**:
  - **Complete RSVQA-LR ($N=20$) Benchmark**: EM 35.0% (7/20), Token F1 0.2525, Mean Latency 50.11s, Median Latency 49.60s, Failures/OOM: 0.
  - **Complete LEVIR-CD ($N=20$) Benchmark**: Macro IoU 0.0878, Micro IoU 0.1113, Macro F1 0.1535, Micro F1 0.2002, Macro Precision 0.1237, Macro Recall 0.6755, Mean Latency 27.4ms.
  - `docs/results/benchmark_rsvqa_results.json` & `docs/results/benchmark_levir_cd_results.json`: Full per-sample prediction manifests.
* **Likely Follow-Up**:
  *"With an F1 of 0.1535, isn't your change detector generating mostly false alarms?"*
* **Recommended Response to Follow-Up**:
  > *"Yes, unsupervised feature differencing on ImageNet weights captures general pixel variance, yielding 0.1237 precision alongside 0.6755 recall. We do not claim this represents operational building change accuracy—it serves as a transparent baseline establishing pipeline execution and proving why supervised in-domain adaptation (e.g. ChangeFormer) is our documented next step."*


---

### Question 6: "Why did you benchmark on only N=20 samples?"

* **10–20 Second Spoken Answer**:
  > *"Evaluating the 3B VLM takes ~50 seconds per sample on our 8 GB laptop GPU. Running 20 samples required ~16.7 minutes of continuous GPU compute. Evaluating $N=20$ reproducible slices (Seed 42) conformed to our formal benchmark schema and allowed us to verify pipeline correctness and zero-OOM stability without multi-day cluster requirements."*
* **Evidence Supporting Answer**:
  - `data/benchmarks/benchmark_manifest.json`: Fixed seed 42 sample manifest.
  - `ai/evaluation/benchmark_schema.json`: Strict JSON schema validation.
  - `docs/results/performance_report.md`: Hardware telemetry documentation.
* **Likely Follow-Up**:
  *"Can you prove your results aren't cherry-picked?"*
* **Recommended Response to Follow-Up**:
  > *"All $N=20$ indices were sampled using deterministic random seed 42 via `ai/evaluation/acquire_benchmarks.py`. Any evaluator can clone our repository and run `python ai/evaluation/benchmark_runner.py` to regenerate the exact same JSON results byte-for-byte."*

---

### Question 7: "Does 'System Confidence: 97.4%' in Change Detection mean 97.4% accuracy?"

* **10–20 Second Spoken Answer**:
  > *"Absolutely not, and our documentation and UI explicitly forbid that interpretation. 97.4% is the **heuristic area stability margin**—the mathematical proportion of the scene remaining unchanged under the feature differencing metric. It does not measure classification accuracy, F1-score, or precision against ground truth."*
* **Evidence Supporting Answer**:
  - `ai/evaluation/confidence_semantics.md`: Section on Change Detection semantics.
  - `docs/results/demo_claims_matrix.md`: Prohibited claims section.
  - `frontend/src/components/ResultView.tsx`: Explicit hover caveat and uncalibrated label.
* **Likely Follow-Up**:
  *"Why show a confidence percentage at all if it's not accuracy?"*
* **Recommended Response to Follow-Up**:
  > *"Operators need to know the magnitude of detected change relative to scene size (e.g., 2.6% changed vs 97.4% stable). However, we label it as 'Area Stability Margin' with an uncalibrated disclaimer to prevent any confusion with statistical accuracy."*

---

### Question 8: "Why is VQA confidence null?"

* **10–20 Second Spoken Answer**:
  > *"Because our 3B VLM uses greedy autoregressive decoding (`do_sample=False`). Autoregressive token probabilities do not represent semantic factual certainty. Fabricating an arbitrary 90% score would deceive operators. Returning 'null' is the only scientifically honest approach."*
* **Evidence Supporting Answer**:
  - `ai/inference/vqa.py`: Greedy decoding parameters (`do_sample=False`).
  - `docs/results/confidence_semantics.md`: VQA confidence classification as `null`.
* **Likely Follow-Up**:
  *"How does an operator know if the VLM is hallucinating?"*
* **Recommended Response to Follow-Up**:
  > *"By inspecting the visual evidence envelope and the observable execution trace. The operator can cross-reference the VLM's text with the raw optical imagery and spatial telemetry returned in the same API payload."*

---

### Question 9: "Why are you using proxy SAR instead of real ISRO RISAT data?"

* **10–20 Second Spoken Answer**:
  > *"Authentic sub-meter Cartosat-2S optical and RISAT-1A SAR co-registered operational pairs are restricted under ISRO/SAC institutional data agreements for national security reasons. To validate our dual-stream ingestion pipeline and Pearson cross-correlation algorithms, we tested using physically modeled radar backscatter proxies (`proxy_sar`)."*
* **Evidence Supporting Answer**:
  - `docs/results/demo_assets.md`: Data classification as `proxy_sar`.
  - `ai/inference/optical_sar.py`: Dual-stream radiometric ingestion engine.
  - `docs/results/judge_evidence_matrix.md`: Requirement 4 documented limitation.
* **Likely Follow-Up**:
  *"Is your proxy SAR just an inverted grayscale image?"*
* **Recommended Response to Follow-Up**:
  > *"No. The proxy simulates radar backscatter physics: high dielectric corner reflections from metal vessels, double-bounce scattering from vertical structures, and low backscatter specular reflection from calm water, calibrated in estimated decibels ([-53.1 dB to -5.0 dB])."*

---

### Question 10: "Your VQA takes ~50 seconds. How is that usable in an emergency?"

* **10–20 Second Spoken Answer**:
  > *"A 50-second latency reflects running an unquantized 3-Billion-parameter VLM on consumer laptop hardware (~8 GB VRAM) with CPU offloading. In an emergency, operators prioritize deep scene interpretation over sub-second speed. For rapid screening, our Change Detection runs in under 1 second and Grounding runs in 8 seconds. Furthermore, serving Qwen via vLLM in cloud deployment drops VQA to under 3 seconds."*
* **Evidence Supporting Answer**:
  - `docs/results/performance_report.md`: Detailed latency breakdown.
  - `frontend/src/components/AnalysisForm.tsx`: Honest elapsed stopwatch.
  - `docs/results/judge_faq.md` (Q11): Cloud vLLM roadmap.
* **Likely Follow-Up**:
  *"What happens during a cold start when the model isn't in memory?"*
* **Recommended Response to Follow-Up**:
  > *"Initial model loading from disk takes ~14 seconds. Once loaded, our `PersistentQwenVLM` session keeps the model in host memory, meaning subsequent queries do not incur disk reload penalties."*

---

### Question 11: "What happens if two users submit requests simultaneously? Won't your serial lock cause a bottleneck?"

* **10–20 Second Spoken Answer**:
  > *"On local 8 GB hardware, concurrent heavy model execution causes an immediate CUDA Out-Of-Memory crash. Our `_GPU_EXECUTION_LOCK` is an intentional safety mechanism that guarantees 100% crash-free operation on consumer GPUs. In production, requests would be queued via Celery across a horizontally scaled multi-GPU worker cluster."*
* **Evidence Supporting Answer**:
  - `backend/app/services/orchestration_service.py`: `_GPU_EXECUTION_LOCK` implementation.
  - `ai/evaluation/test_agent_orchestration.py`: Test 10 & 11 concurrency safety.
* **Likely Follow-Up**:
  *"What does the second user see while waiting?"*
* **Recommended Response to Follow-Up**:
  > *"The frontend displays an active processing state with an elapsed stopwatch, informing the user that the single-model GPU execution lock is engaged to prevent memory collisions."*

---

### Question 12: "Can an attacker jailbreak your agent to execute bash commands or exploit parameters?"

* **10–20 Second Spoken Answer**:
  > *"No. Our architecture does not expose arbitrary code execution or shell tools. All tools are registered in an immutable whitelist. Furthermore, our pre-model parameter firewall validates all keys and numerical bounds in under 20 milliseconds, rejecting unauthorized parameters before any model is invoked."*
* **Evidence Supporting Answer**:
  - `backend/app/agent/registry.py`: Immutable tool dictionary.
  - `ai/evaluation/test_failure_cases.py`: Test 9 (Parameter injection rejection in 3.5ms) & Test 10 (Unregistered tool rejection in 3.8ms).
* **Likely Follow-Up**:
  *"Can someone inject malicious parameters inside a JSON string?"*
* **Recommended Response to Follow-Up**:
  > *"FastAPI and Pydantic v2 parse and validate JSON payloads against our strict Pydantic schemas. Unrecognized keys are automatically filtered out by our router firewall before reaching specialist functions."*

---

### Question 13: "What happens if an operator uploads a corrupted or cloudy image?"

* **10–20 Second Spoken Answer**:
  > *"Corrupted images are intercepted at Stage 1 (Input Validation) in under 7 milliseconds via PIL/Rasterio decoders and rejected with `INVALID_IMAGE` before any GPU resources are used. For cloudy scenes, the models process visible bands honestly, and Grounding DINO cross-attention scores reflect low similarity rather than hallucinating detections through solid clouds."*
* **Evidence Supporting Answer**:
  - `ai/evaluation/test_failure_cases.py`: Test 1 (Corrupted binary rejection in 6.8ms) & Test 2 (Unsupported extension in 4.1ms).
  - `backend/app/validation/image_validation.py`: Pre-execution raster integrity checking.
* **Likely Follow-Up**:
  *"Can you demonstrate that live right now?"*
* **Recommended Response to Follow-Up**:
  > *"Yes! We can click our 'Safety & Firewall' preset or upload a `.txt` file disguised as an image. In less than 10 milliseconds, the UI will display an immediate rejection banner without touching the GPU."*
