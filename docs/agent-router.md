# Agent Router & Predefined Tool Registry Specification — SatQuery AI (Phase 4)

## 1. Overview & Architectural Role
The **Agent Router** serves as the deterministic orchestrator and security boundary in SatQuery AI. It translates natural language user queries and multi-sensor input envelopes into strictly governed tool invocations.

In contrast to open-ended LLM agents that execute arbitrary code, explore file systems, or invoke unbounded external APIs, SatQuery AI implements a **Bounded Deterministic Router**. The router evaluates queries against a closed, predefined catalog of certified specialist AI tools, validates input asset requirements, sanitizes user parameters against strict schemas, and emits observable execution trace telemetry without storing hidden chain-of-thought.

---

## 2. Predefined Tool Registry
The system registry (`backend/app/agent/registry.py`) defines exactly four certified remote-sensing tools:

| Tool Name | Capability Description | Model / Underlying Engine | Required Inputs | Primary Output | Evidence Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`VQA`** | Remote-sensing visual question answering, counting, and scene captioning | `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` | `image_path` | Natural language text | Visual token attention |
| **`GROUNDING`** | Open-vocabulary object localization & bounding box coordinate regression | `IDEA-Research/grounding-dino-tiny` | `image_path` | Coordinate boxes $[x_1, y_1, x_2, y_2]$ | Annotated bounding box overlays |
| **`CHANGE_DETECTION`** | Bi-temporal differential change understanding between timestamps T1 and T2 | `Siamese-ResNet18-FeatureDifferencer` | `image_path`, `second_image_path` | Binary change mask ($H \times W$) | Differential heatmap mask composite |
| **`OPTICAL_SAR`** | Cross-modal analysis fusing optical reflectance with radar microwave backscatter | Dual-stream multi-sensor statistics engine | `optical_image_path`, `sar_image_path` | Cross-modal statistics & correlation ($r$) | Optical-SAR synergy overlay |

### Permitted Parameter Enforcement
User requests cannot pass arbitrary configuration variables to underlying models. Parameters are strictly validated against tool-specific schemas:
* **`VQA`**: `max_new_tokens` ($16 - 256$), `do_sample` (`False` only), `min_pixels` ($200,704$), `max_pixels` ($401,408$).
* **`GROUNDING`**: `box_threshold` ($0.10 - 0.90$), `text_threshold` ($0.10 - 0.90$).
* **`CHANGE_DETECTION`**: `threshold` ($0.10 - 0.90$).
* **`OPTICAL_SAR`**: `high_scatter_threshold` ($100.0 - 250.0$ DN).

Any unrecognized parameter is filtered out with an explicit warning; out-of-range numeric parameters are clamped to authorized safety boundaries.

---

## 3. Deterministic Routing Rules
The router evaluates user queries using hierarchical domain-specific pattern matching:

1. **Optical-SAR Rule**:
   - Triggers when queries contain microwave/radar keywords (`sar`, `radar`, `backscatter`, `microwave`, `optical and sar`, `through clouds`, `all-weather`).
   - Mapped Tool: **`OPTICAL_SAR`**.
2. **Bi-Temporal Change Rule**:
   - Triggers when queries contain temporal differential keywords (`changed`, `difference`, `diff`, `between these images`, `between t1 and t2`, `before and after`, `new construction`, `loss`, `expansion`).
   - Mapped Tool: **`CHANGE_DETECTION`**.
3. **Visual Grounding Rule**:
   - Triggers when queries request object localization or spatial coordinates (`locate`, `find`, `detect`, `where is`, `where are`, `point out`, `bounding box`, `coordinates of`, `pinpoint`).
   - Mapped Tool: **`GROUNDING`**.
4. **General Remote-Sensing VQA Rule**:
   - Triggers for qualitative, descriptive, and counting questions (`what is`, `what are`, `describe`, `caption`, `overview`, `how many`, `count`, `is there`, `land cover`, `environment`).
   - Mapped Tool: **`VQA`**.

---

## 4. Input Validation & Prerequisite Enforcement
Before a tool is scheduled for execution, the router strictly enforces prerequisite input asset availability:

| Selected Tool | Mandatory Input Assets | Rejection Error if Missing |
| :--- | :--- | :--- |
| **`VQA`** | `image_path` | `INVALID_INPUT`: *"VQA requires a valid 'image_path'."* |
| **`GROUNDING`** | `image_path` | `INVALID_INPUT`: *"Grounding requires a valid 'image_path' to localize objects."* |
| **`CHANGE_DETECTION`** | `image_path` (T1) and `second_image_path` (T2) | `INVALID_INPUT`: *"Change Detection requires baseline image T1 and post-event image T2."* |
| **`OPTICAL_SAR`** | `optical_image_path` (or `image_path`) and `sar_image_path` | `INVALID_INPUT`: *"Optical-SAR analysis requires an optical image and a SAR radar image."* |

Inference forward passes are **never** attempted if prerequisite assets are missing.

---

## 5. Ambiguity Handling & Guardrails
If incoming query text lacks sufficient operational signal (e.g., `"process this"`, `"run"`, `"analyze"`, `"hello"`, `"test"`), the router rejects automated selection and issues a structured **`NEEDS_CLARIFICATION`** response:
* Status: `NEEDS_CLARIFICATION`
* Selected Tool: `None`
* Clarification Prompt: *"Please specify your objective: (1) Answer question (VQA), (2) Locate objects (Grounding), (3) Compare bi-temporal changes, or (4) Analyze Optical+SAR."*

If a user submits an explicit task override requesting an unregistered tool (e.g., `task="CUSTOM_SHELL_EXECUTION"`), the router immediately aborts with **`UNREGISTERED_TOOL`** status, blocking arbitrary execution.

---

## 6. GPU Model Resource Policy
Given the **8.0 GB GDDR7** VRAM budget of the local NVIDIA GeForce RTX 5050 Laptop GPU:
1. **Single-Heavy-Model Residency**: The 3B VLM (`AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`) consumes $\sim 6.2$ GB in bfloat16. It is classified as `HEAVY_VLM` and **must never be loaded concurrently** in GPU memory alongside another heavy or medium model.
2. **On-Demand Loading & Explicit Eviction**: Specialist models (`GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`) are loaded on-demand. When switching to or from the VLM, the active model is evicted from GPU memory, calling `torch.cuda.empty_cache()` and garbage collection before loading the next model.
3. **Sequential Pipeline Execution**: Multi-step workflows (e.g. Grounding $\to$ VQA description) run sequentially in discrete phases rather than via parallel multi-threading on the GPU.

---

## 7. Observable Execution Trace Telemetry
Every transaction produces an observable trace entry structured as follows:

```json
{
  "step": "ROUTER",
  "selected_task": "GROUNDING",
  "selected_tool": "GROUNDING",
  "model": "IDEA-Research/grounding-dino-tiny",
  "permitted_parameters": {
    "box_threshold": 0.35,
    "text_threshold": 0.25
  },
  "input_references": ["data/samples/sample_satellite_port.jpg"],
  "status": "ROUTED",
  "latency_ms": 1.45,
  "output_reference": "tool_selection_01",
  "evidence_reference": "annotated_bounding_box_overlay"
}
```

*Policy Note*: The execution trace contains only observable data fields (selected tool, validated parameters, file paths, latencies, and execution status). Hidden model reasoning and chain-of-thought remain completely unexposed.

---

## 8. Concrete Routing Examples

```
Input:  query="Where are the ships and vessels?", image_path="sample_port.jpg"
Result: Tool=GROUNDING | Status=ROUTED | Params={"box_threshold": 0.30, "text_threshold": 0.25}

Input:  query="What changed between these two dates?", image_path="t1.jpg", second_image_path="t2.jpg"
Result: Tool=CHANGE_DETECTION | Status=ROUTED | Params={"threshold": 0.40}

Input:  query="What changed between these two dates?", image_path="t1.jpg", second_image_path=None
Result: Tool=CHANGE_DETECTION | Status=INVALID_INPUT | Error="Missing post-event image T2"

Input:  query="analyze this", image_path="sample_port.jpg"
Result: Tool=None | Status=NEEDS_CLARIFICATION | Prompt="Please specify your objective..."

Input:  query="Run system diagnostics", task="SHELL_EXECUTION", image_path="sample_port.jpg"
Result: Tool=None | Status=UNREGISTERED_TOOL | Error="Unregistered tool 'SHELL_EXECUTION'"
```
