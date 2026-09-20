# SatQuery AI — Hardware & Model Execution Performance Report (Phase 8B)

This performance report documents measured execution latency, memory footprint, cold vs. warm residency behavior, and hardware scheduling constraints for SatQuery AI running on the production MVP evaluation platform.

---

## 1. Evaluation Hardware Profile

* **Host System**: Windows 11 64-bit
* **GPU**: NVIDIA GeForce RTX 5050 Laptop GPU
* **Total Physical VRAM**: 8,150.56 MB (~8 GB GDDR7)
* **Compute Capability**: Blackwell Architecture (CUDA 13.0, PyTorch 2.14.0+cu130)
* **BF16 Tensor Core Support**: Native (Hardware accelerated)
* **Host Memory (RAM)**: 16 GB DDR5 System Memory
* **Storage**: NVMe PCIe Gen4 SSD

---

## 2. Latency Benchmarks by Analytical Capability

All values are derived from reproducible tests (`test_api_contract.py` and `test_real_satellite_vqa.py`) executed on `sample_satellite_port.jpg` (720 × 480 px).

| Capability | Model / Engine | Cold-Start Latency (First Invocation) | Warm Inference Latency (Resident Model) | Latency Characterization |
| :--- | :--- | :--- | :--- | :--- |
| **VQA** | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | **45.78 s – 49.04 s**<br>(includes HuggingFace model weight loading & CPU offload dispatch) | **5.58 s – 27.18 s**<br>(resident model forward pass; duration varies with generated token length) | **Heavyweight VLM**<br>Greedy decoding generation (100 tokens max); bound by autoregressive token generation & GPU memory bandwidth. |
| **GROUNDING** | `IDEA-Research/grounding-dino-tiny` | **8.46 s – 9.32 s**<br>(includes on-demand PyTorch model load & Swin-T initialization) | **0.36 s – 0.50 s**<br>(pure forward pass on resident weights) | **Lightweight Fast Detector**<br>Single-stage zero-shot Swin-T forward pass followed by bounding box threshold filtering. |
| **CHANGE_DETECTION** | `Siamese-ResNet18-FeatureDifferencer` | **0.54 s – 0.68 s**<br>(includes model initialization & T1/T2 tensor allocation) | **0.34 s – 0.35 s**<br>(pure Siamese feature differencing pass) | **Ultra-Fast Siamese Embedder**<br>Dual-stream feature extraction at layer 4 followed by Euclidean distance computation. |
| **OPTICAL_SAR** | `Dual-Stream Cross-Modal Statistics Engine` | **0.28 s – 0.31 s**<br>(initial tensor conversion & CUDA transfer) | **0.07 s – 0.12 s**<br>(GPU parallel luminance & backscatter calculation) | **Real-Time Mathematical Engine**<br>Vectorized PyTorch statistical moments, Pearson correlation coefficient, and corner-reflection filtering. |

---

## 3. GPU VRAM Consumption & Memory Footprint

| Pipeline Phase | Free VRAM (MB) | Allocated VRAM (MB) | GPU Memory Description |
| :--- | :--- | :--- | :--- |
| **Clean Baseline (Idle FastAPI Server)** | **7,070.0 MB** | 0.0 MB | Clean CUDA context; only FastAPI server and driver buffers active. |
| **During Qwen2.5-VL-3B Execution** | **236.0 – 278.0 MB** | ~6,174.8 MB | Model weights loaded in BF16. Layers 29–35 and final norm offloaded to CPU to stay strictly within 8 GB GDDR7 budget. |
| **After Grounding Execution** | **838.0 – 858.0 MB** | ~660.0 MB | Grounding DINO loaded on demand; tensors deleted and `torch.cuda.empty_cache()` invoked upon completion. |
| **After Change Detection Execution** | **888.0 MB** | ~11.8 MB | Siamese ResNet18 consumes negligible GPU memory (<15 MB); stable headroom maintained. |
| **After Optical-SAR Execution** | **886.0 MB** | ~9.9 MB | Pure tensor statistical reduction; consumes <10 MB GPU memory. |
| **Post-Pipeline Stable State** | **886.0 MB** | Stable | Server remains responsive with ~886 MB headroom available for subsequent fast tool calls. |

---

## 4. Hardware Scheduling & Architectural Constraints

### 1. Sequential GPU Execution Lock
Because the 3B Vision-Language Model allocates ~6.2 GB of the available ~8.15 GB VRAM, **concurrent model residency is strictly impossible** on an 8 GB consumer GPU without triggering a fatal CUDA Out-of-Memory (`cudaErrorMemoryAllocation`) crash.
* **Architecture Implementation**: All tool invocations passing through `backend/app/api/routes.py` are wrapped under an `asyncio.Lock()` (`_GPU_EXECUTION_LOCK`).
* **Operational Implication**: Requests are serialized in a FIFO queue. If a VQA request is running, subsequent Grounding or Change Detection calls await its completion safely before executing.

### 2. Cold-Start vs. Warm Inference Trade-off
* In standard production servers, heavy models remain resident in memory.
* For the lightweight tools (`GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`), executing on-demand with explicit post-execution tensor cleanup (`del model`, `torch.cuda.empty_cache()`, `gc.collect()`) guarantees that memory is never permanently leaked.
* The first VQA call on a freshly started server incurs a ~45s cold-start penalty; subsequent scene queries execute in ~5–27 seconds.

### 3. Visual Token Budget Constraints
To guarantee stable GPU residency during VQA, conservative pixel limits are enforced:
* `min_pixels = 200,704` (equivalent to $256 \times 28 \times 28$ visual tokens)
* `max_pixels = 401,408` (equivalent to $512 \times 28 \times 28$ visual tokens)
* Extremely large satellite scenes (e.g., $10,000 \times 10,000$ gigapixel mosaics) must be tiled or chipped prior to VLM ingestion.
