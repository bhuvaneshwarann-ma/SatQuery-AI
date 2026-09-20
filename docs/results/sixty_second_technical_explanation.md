# SatQuery AI — 60-Second Technical Walkthrough (Phase 10)

**Question**: *"What technically happens after an operator clicks 'Run Satellite Analysis'?"*  
**Target Duration**: 60 Seconds  
**Audience**: Mixed Technical & Non-Technical Evaluators  
**Key Principle**: Concrete step-by-step clarity without buzzwords.

---

### The 60-Second Technical Answer

> *"When you click 'Run Satellite Analysis' in the SatQuery AI interface, your request undergoes a deterministic five-stage pipeline:
> 
> 1. **Stage 1 — Input Validation (4 ms)**: 
>    FastAPI receives the multipart upload. Image decoders verify the binary header, raster dimensions, and file extensions before any neural network is touched. Corrupted files are rejected immediately.
> 
> 2. **Stage 2 — Agent Router & Parameter Firewall (12 ms)**: 
>    Our deterministic router inspects your natural language query and asset count to determine intent (`VQA`, `GROUNDING`, `CHANGE_DETECTION`, or `OPTICAL_SAR`). Simultaneously, our parameter firewall checks all options against a whitelist, stripping injection attempts before GPU allocation.
> 
> 3. **Stage 3 — Hardware-Locked Tool Execution**: 
>    The system acquires our sequential GPU lock (`_GPU_EXECUTION_LOCK`). This guarantees that our 3B VLM and computer vision models never compete for VRAM, eliminating CUDA Out-Of-Memory crashes. The selected backbone executes its forward pass on the GPU.
> 
> 4. **Stage 4 — Spatial Evidence Synthesis (3 ms)**: 
>    The specialist engine renders physical visual artifacts—such as tight bounding boxes, 3-panel differential heatmaps, or false-color radiometric synergy composites—and saves them to disk.
> 
> 5. **Stage 5 — Result Composition & Trace Delivery (1 ms)**: 
>    The backend synthesizes the answer text, uncalibrated confidence semantics, and an observable audit trace showing the exact latency of each step, delivering an auditable response to your screen.
> 
> *The entire process is transparent, secure, and observable from start to finish."*
