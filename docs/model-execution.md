# Model Execution Specification — SatQuery AI (Phase 5)

## 1. Overview & Architecture
This document specifies the concrete model execution pipeline for SatQuery AI, detailing how the high-level routing decisions from the **Agent Router** are dispatched to isolated, on-demand specialist model executors.

In **Phase 5A**, the **Remote-Sensing VQA** pipeline is connected end-to-end to the verified Earth Observation Vision-Language Model: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`.

```
User Request (AnalysisRequest)
            │
            ▼
[Input Validation Gateway]
            │
            ▼
     [Agent Router] ── (Status: ROUTED, Tool: VQA)
            │
            ▼
  [AnalysisService]
            │
            ▼
[VQA Executor: ai/inference/vqa.py]
  ├── Validates file presence & image integrity
  ├── Loads Qwen2.5-VL-3B on demand (BF16 + auto CPU offload)
  ├── Executes forward pass with conservative token limits
  ├── Formulates factual evidence metadata
  └── Releases model & flushes CUDA cache in finally block
            │
            ▼
   [ToolResult + Observable Trace]
```

---

## 2. Remote-Sensing VQA Executor (`ai/inference/vqa.py`)

### 2.1 Model Profile
* **Checkpoint Identifier**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Architecture**: Qwen2.5-VL-3B-Instruct with dynamic visual token resolution.
* **Loading Policy**: On-demand instantiation with `device_map="auto"` and `torch_dtype="auto"`.
* **Visual Token Budget**: `min_pixels = 200,704` ($256 \times 28 \times 28$), `max_pixels = 401,408` ($512 \times 28 \times 28$).
* **Acceleration**: FlashAttention is disabled; uses standard PyTorch attention mechanisms compatible with Windows and CUDA.

### 2.2 Input / Output Contract
* **Function Signature**:
  ```python
  run_vqa(image_path: str, query: str, permitted_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
  ```
* **Return Payload Schema**:
  ```json
  {
    "status": "SUCCESS",
    "tool": "VQA",
    "model": "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
    "answer": "The satellite image shows a coastal port area with visible navigation breakwaters, shipping channels, and coastal sandbars.",
    "confidence": null,
    "latency_ms": 6840.5,
    "evidence": [
      {
        "type": "vqa_spatial_metadata",
        "image_reference": "data/samples/sample_satellite_port.jpg",
        "dimensions": {"width": 720, "height": 480},
        "query": "What major objects or structures are visibly present?",
        "model": "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
        "latency_ms": 6840.5
      }
    ],
    "metadata": {
      "max_new_tokens": 100,
      "tokens_generated": 34,
      "visual_token_bounds": "200704-401408"
    }
  }
  ```

---

## 3. Evidence Generation & Transparency
* **Factual Evidence Only**: In strict adherence to SatQuery AI design principles, the VQA executor generates **factual metadata evidence** (source file reference, native pixel dimensions, user query string, and timing profiles).
* **Zero Hallucinated Evidence**: The system **does not** fabricate bounding boxes, segmentation masks, or heatmaps that the VLM was not mathematically trained to output. Fine-grained spatial coordinate evidence is reserved exclusively for the `GROUNDING` tool.

---

## 4. Confidence Limitation Policy
* **Current Status**: Confidence is set to **`null`** (`None`) for Phase 5A VQA execution.
* **Policy Rationale**: Raw token softmax scores from generative VLMs are notoriously uncalibrated and misleading. Inventing arbitrary confidence percentages is strictly forbidden. Formal calibrated uncertainty scoring will be introduced during the dedicated Confidence Calibration phase.

---

## 5. GPU Resource Management & Cleanup Policy
* **Single-Heavy-Model Residency**: The RTX 5050 Laptop GPU has **8.0 GB GDDR7** VRAM. In unquantized bfloat16, Qwen2.5-VL-3B consumes $\sim 6.2$ GB (with layers 29–35 offloaded to system RAM).
* **Guaranteed Memory Release**: In `ai/inference/vqa.py`, all model instances, processor handles, and CUDA tensors are purged in a deterministic `finally` block:
  ```python
  finally:
      if inputs is not None:
          del inputs
      if model is not None:
          del model
      if processor is not None:
          del processor
      if torch.cuda.is_available():
          torch.cuda.empty_cache()
      gc.collect()
  ```
* This ensures that upon completion of a VQA query, available VRAM returns to $\sim 7.0$ GB idle, leaving the GPU clear for downstream tools (e.g. Grounding DINO or Change Detection).

---

## 6. Observable Execution Trace Telemetry
Every analysis request coordinated through `AnalysisService.analyze()` automatically appends observable trace entries without recording private LLM chain-of-thought:

```json
[
  {
    "step": "ROUTER",
    "selected_task": "VQA",
    "selected_tool": "VQA",
    "model": "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
    "permitted_parameters": {"max_new_tokens": 100, "do_sample": false},
    "input_references": ["image_path"],
    "status": "ROUTED",
    "latency_ms": 1.25,
    "output_reference": "routing_decision:ROUTED",
    "evidence_reference": null
  },
  {
    "step": "TOOL_EXECUTION",
    "selected_task": "VQA",
    "selected_tool": "VQA",
    "model": "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
    "permitted_parameters": {"max_new_tokens": 100, "do_sample": false},
    "input_references": ["data/samples/sample_satellite_port.jpg"],
    "status": "SUCCESS",
    "latency_ms": 6840.5,
    "output_reference": "vqa_text_output",
    "evidence_reference": "vqa_spatial_metadata"
  }
]
```

---

## 7. Error Handling & Graceful Degradation
The VQA execution service traps all error cases and emits structured error payloads without crashing the host process:
* **Missing Image**: Returns `status="ERROR"` with error type `FILE_NOT_FOUND`.
* **Corrupted Image**: Traps Pillow verification errors and returns `UNREADABLE_IMAGE`.
* **Empty Query**: Caught during input validation, returning `VALIDATION_ERROR`.
* **CUDA OOM**: Traps `torch.cuda.OutOfMemoryError`, triggers emergency GPU cleanup, and returns `CUDA_OOM`.
