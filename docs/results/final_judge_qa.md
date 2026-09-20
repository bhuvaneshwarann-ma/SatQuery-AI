# SatQuery AI — Final Evaluator Q&A Sheet (Phase 11)

**Document Purpose**: The 15 most rigorous evaluator attack questions, paired with concise (10–20 second) spoken responses, supporting evidence links, predicted evaluator follow-ups, and punchy one-sentence follow-up rebuttals.

---

### Question 1: "Why is this system called 'agentic' if you have fixed tools?"
* **10–20 Second Spoken Answer**:
  > *"It is an agent because it dynamically interprets arbitrary, unstructured user queries, autonomously plans the appropriate specialist workflow, validates parameters against a schema firewall, executes the specialist model, and synthesizes structured visual evidence with audit telemetry. Having an immutable tool registry is not a lack of agency—it is responsible engineering that prevents hallucinated execution."*
* **Evidence Reference**: `backend/app/agent/registry.py` & `backend/app/services/orchestration_service.py`
* **Likely Follow-Up**: *"Can it chain multiple tools sequentially, like grounding and then VQA?"*
* **One-Sentence Response**: *"Yes, our orchestrator architecture is designed for multi-step tool graphs, but we intentionally exposed discrete single-turn specialist pipelines in our MVP to guarantee predictable latency and zero memory leaks on consumer hardware."*

---

### Question 2: "Why not just use a single large Vision-Language Model like GPT-4o or Qwen2.5-VL for everything?"
* **10–20 Second Spoken Answer**:
  > *"Because general VLMs cannot natively localize bounding coordinates with millimeter accuracy, cannot ingest microwave SAR complex matrices, and cannot compute exact pixel-level bi-temporal feature differencing. Earth observation requires specialized computer vision heads alongside language reasoning—a modular agent architecture outperforms a monolithic model on domain-specific tasks."*
* **Evidence Reference**: `docs/results/sixty_second_technical_explanation.md`
* **Likely Follow-Up**: *"Newer VLMs output bounding boxes in text tokens. Why isn't that enough?"*
* **One-Sentence Response**: *"Text-token bounding boxes from general VLMs suffer from high coordinate jitter and cannot match the sub-pixel precision of dedicated cross-attention detector heads like Grounding DINO."*

---

### Question 3: "What did your team actually build versus just downloading open-source models?"
* **10–20 Second Spoken Answer**:
  > *"We engineered the end-to-end operational platform: the deterministic agent router and tool firewall, the dual-stream Optical-SAR normalization pipeline, the Siamese feature differencing engine, the visual evidence generator, the GPU serialization scheduler, the FastAPI backend, the React analytical dashboard, and the reproducible evaluation harness."*
* **Evidence Reference**: `backend/app/services/` & `frontend/src/components/`
* **Likely Follow-Up**: *"Isn't the intelligence just the weights of Qwen and ResNet?"*
* **One-Sentence Response**: *"Model weights are inert without an orchestrated system that validates multimodal inputs, schedules GPU execution, enforces confidence semantics, and generates auditable visual evidence."*

---

### Question 4: "What is Requirement #5, and why is it marked PARTIAL / OPEN?"
* **10–20 Second Spoken Answer**:
  > *"Requirement #5 calls for fine-tuning a vision-language model on remote sensing data. We deployed and benchmarked an existing open-source remote-sensing domain-adapted checkpoint zero-shot. However, custom team-owned fine-tuning and LoRA parameter training on Indian satellite data have not yet been executed. We refuse to fabricate toy training curves, so we transparently classify Requirement #5 as PARTIAL / OPEN."*
* **Evidence Reference**: `docs/results/judge_evidence_matrix.md` (Requirement #5)
* **Likely Follow-Up**: *"Why didn't you quickly fine-tune it with LoRA during the hackathon?"*
* **One-Sentence Response**: *"Rushing a 2-epoch LoRA script on 50 uncurated images on a laptop produces catastrophic forgetting and false claims; establishing a rigorous zero-shot baseline first was the scientifically sound engineering decision."*

---

### Question 5: "Your benchmark scores are low—35% Exact Match on RSVQA and 0.1535 F1 on LEVIR-CD. Why?"
* **10–20 Second Spoken Answer**:
  > *"Our current benchmark is an honest zero-shot baseline, not a claim of state-of-the-art accuracy. On N=20 public benchmark samples, RSVQA achieved 35% exact match and 0.2525 token F1, while LEVIR-CD achieved 0.0878 macro IoU and 0.1535 macro F1. These results establish a reproducible baseline and show where adaptation is still needed."*
* **Evidence Reference**: `docs/results/satquery_ai_evaluation_report.md` & `ai/evaluation/benchmark_runner.py`
* **Likely Follow-Up**: *"Doesn't a 0.1535 F1 mean your change detector generates mostly false alarms?"*
* **One-Sentence Response**: *"Yes, unsupervised feature differencing on ImageNet weights captures textural variance, yielding 0.1237 precision alongside 0.6755 recall—which quantitatively proves why supervised in-domain adaptation is our documented next milestone."*

---

### Question 6: "Why did you benchmark on only N=20 samples instead of the full dataset?"
* **10–20 Second Spoken Answer**:
  > *"At ~50 seconds per sample for 3B VLM autoregressive decoding, evaluating 20 samples required ~17 minutes of continuous GPU execution on our 8 GB hardware. The N=20 slices with fixed Seed 42 provide a scientifically verifiable, 100% reproducible baseline proving pipeline correctness without requiring multi-day cloud cluster runs."*
* **Evidence Reference**: `data/benchmarks/benchmark_manifest.json` & `ai/evaluation/benchmark_protocol.md`
* **Likely Follow-Up**: *"Did you cherry-pick those 20 samples to look good?"*
* **One-Sentence Response**: *"No, samples were selected via fixed deterministic pseudo-random seeding (Seed 42) directly from public validation splits, as proven by our reproducible benchmark generation script."*

---

### Question 7: "Why did you use proxy SAR data instead of real ISRO RISAT imagery?"
* **10–20 Second Spoken Answer**:
  > *"Authentic sub-meter ISRO Cartosat-2S and RISAT SAR data is restricted under institutional access agreements that were not available during this phase. We therefore validated our dual-stream ingestion mathematics and correlation algorithms using physically modeled radar backscatter proxies and public Sentinel-1 microwave data."*
* **Evidence Reference**: `docs/results/demo_assets.md` & `ai/evaluation/test_optical_sar.py`
* **Likely Follow-Up**: *"Will your mathematical correlation pipeline work on genuine RISAT data?"*
* **One-Sentence Response**: *"Yes, our pipeline ingests normalized floating-point decibel backscatter matrices, which is the standard physical data format of calibrated Level-1 RISAT and Sentinel-1 SLC/GRD products."*

---

### Question 8: "Why does the change detection demo use a synthetic temporal pair?"
* **10–20 Second Spoken Answer**:
  > *"The demo asset uses a controlled synthetic pair so that live evaluators can visually inspect clear, isolated structural changes without seasonal crop or atmospheric noise during a 45-second demo. However, our actual scientific benchmarking was executed on 20 genuine, real-world Google Earth temporal pairs from the LEVIR-CD benchmark."*
* **Evidence Reference**: `data/benchmarks/levir_cd/` & `docs/results/demo_assets.md`
* **Likely Follow-Up**: *"Is the synthetic pair easier than real images?"*
* **One-Sentence Response**: *"Yes, which is precisely why we explicitly disclose it as a demonstration asset and evaluate our true algorithm against the difficult, noisy public LEVIR-CD benchmark."*

---

### Question 9: "What does 'confidence' actually mean across your system? Are these calibrated probabilities?"
* **10–20 Second Spoken Answer**:
  > *"No, none of our confidence metrics are calibrated classification probabilities, and we explicitly disclaim this to the user. VQA confidence is strictly null; Grounding score is an uncalibrated detector logit; Change confidence is an area stability margin representing unchanged pixels; and Optical-SAR confidence is a pipeline matrix integrity indicator."*
* **Evidence Reference**: `docs/results/confidence_semantics.md` & `backend/app/schemas/response_schema.py`
* **Likely Follow-Up**: *"If an evaluator sees 97.4% on Change Detection, won't they assume it means 97.4% accuracy?"*
* **One-Sentence Response**: *"Not in our system, because the UI displays an explicit label 'Area Stability Margin (Uncalibrated)' with a hover tooltip defining it as the percentage of scene pixels unchanged."*

---

### Question 10: "Why is VQA latency so high (~50 seconds)?"
* **10–20 Second Spoken Answer**:
  > *"Running an unquantized 3-Billion-parameter vision-language model with CPU memory offloading on an 8 GB consumer laptop GPU takes approximately 50 seconds for full autoregressive token decoding. We display live elapsed time transparently. In production, serving the model via vLLM with AWQ 4-bit quantization on dedicated cloud GPUs drops latency to under 3 seconds."*
* **Evidence Reference**: `docs/results/performance_report.md`
* **Likely Follow-Up**: *"Why not run a much smaller 500M parameter model instead?"*
* **One-Sentence Response**: *"Sub-1B parameter VLMs suffer severe spatial hallucination on complex multi-spectral remote sensing imagery, making 3B the empirical sweet spot for baseline semantic reasoning."*

---

### Question 11: "What happens when multiple users send queries concurrently to your API?"
* **10–20 Second Spoken Answer**:
  > *"On our local 8 GB GPU, concurrent execution of multiple heavy vision models causes an immediate CUDA Out-Of-Memory crash. Our `_GPU_EXECUTION_LOCK` serializes access to the GPU, queuing requests safely. In cloud deployment, this lock is replaced by an asynchronous Celery task queue distributing jobs across horizontally scaled GPU worker pools."*
* **Evidence Reference**: `backend/app/services/orchestration_service.py` (`_GPU_EXECUTION_LOCK`)
* **Likely Follow-Up**: *"Doesn't serialization create a massive user bottleneck?"*
* **One-Sentence Response**: *"On a single 8 GB laptop, predictable serialization is vastly superior to crashing the server; horizontal worker pooling is the standard production solution."*

---

### Question 12: "How do you prevent prompt injection or tool escape through user queries?"
* **10–20 Second Spoken Answer**:
  > *"First, our agent router cannot execute arbitrary Python, bash, or SQL commands; it can only select an enum key from an immutable registry of 4 tools. Second, all extracted parameters are validated through strict Pydantic schemas that reject unexpected fields or malformed payloads before any specialist model is invoked."*
* **Evidence Reference**: `backend/app/agent/registry.py` & `backend/app/schemas/`
* **Likely Follow-Up**: *"What if the user passes an adversarial prompt to the VLM?"*
* **One-Sentence Response**: *"The VLM executes in an isolated inference context without system tool access or external network capabilities, preventing any prompt injection from breaking out of the model container."*

---

### Question 13: "What happens if the router classifies the user's intent incorrectly?"
* **10–20 Second Spoken Answer**:
  > *"Our router uses a deterministic rule-anchored classifier with regex priority, achieving 100% accuracy on our 11 orchestration test cases. If a query is ambiguous, the router falls back to VQA as the most capable conversational pipeline, and the UI provides a manual mode override allowing the analyst to explicitly select any specialist tool."*
* **Evidence Reference**: `backend/app/agent/router.py` & `tests/test_agent_orchestration.py`
* **Likely Follow-Up**: *"Can the user override the router manually in the frontend?"*
* **One-Sentence Response**: *"Yes, the frontend header contains a dedicated mode selector allowing analysts to bypass automatic routing and force any specific specialist pipeline."*

---

### Question 14: "What is genuinely innovative about your architecture compared to existing solutions?"
* **10–20 Second Spoken Answer**:
  > *"The innovation is the controlled, hardware-aware multimodal agent architecture that enforces strict parameter firewalls, guarantees zero CUDA OOM crashes via execution locking, pairs every answer with inspectable raster evidence, and enforces rigorous semantic honesty rather than fabricating uncalibrated confidence percentages."*
* **Evidence Reference**: `docs/results/mock_evaluator_review.md` (Sections 3, 4, and 7)
* **Likely Follow-Up**: *"Is this an AI innovation or a software engineering innovation?"*
* **One-Sentence Response**: *"It is an applied AI systems engineering breakthrough—bridging the gap between raw, unstable foundation models and reliable, auditable Earth observation operations."*

---

### Question 15: "If your team had 3 more months and a compute grant, what would you build next?"
* **10–20 Second Spoken Answer**:
  > *"We would execute four prioritized milestones: first, QLoRA fine-tuning of our 3B VLM on Indian EO datasets to close Requirement #5; second, integration of supervised ChangeFormer to elevate change detection F1 above 0.85; third, evaluation on authentic co-registered Cartosat-2S and RISAT data; and fourth, formal confidence calibration via temperature scaling."*
* **Evidence Reference**: `docs/results/final_ppt_content.md` (Slide 11 Roadmap)
* **Likely Follow-Up**: *"Which of those four is the highest technical priority?"*
* **One-Sentence Response**: *"Supervised fine-tuning on Indian remote sensing data, because domain-adapted visual tokens are the foundational prerequisite for higher downstream accuracy."*
