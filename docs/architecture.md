# System Architecture Specification — SatQuery AI

## 1. Executive Summary & Architectural Mission
**SatQuery AI** is an intelligent, multi-modal Earth Observation (EO) and Remote Sensing (RS) analytical system designed for the **Smart India Hackathon (SIH)**. The platform enables natural language interaction over satellite and aerial imagery, combining multi-sensor cross-reasoning, agentic tool orchestration, grounded visual evidence, and transparent execution traces.

Generic Vision-Language Models (VLMs) fail when confronted with satellite imagery due to nadir/overhead perspectives, varying Ground Sampling Distances (GSD), multi-spectral bands, and radar backscatter complexities. Furthermore, black-box AI generates hallucinations without verifiable visual evidence or quantifiable confidence.

To solve this, **SatQuery AI rejects the single-monolithic-generic-VLM anti-pattern** and instead implements a **Modular Specialist AI Architecture**. An intelligent, bounded agent router interprets user queries, validates spatial-temporal input constraints, and dispatches requests to dedicated, domain-adapted specialist tools (VQA, Grounding/Captioning, Bi-temporal Change, Optical-SAR). Every inference produces an observable execution trace, calibrated confidence metrics, and verifiable visual overlays (bounding boxes, difference heatmaps, masks) without exposing unsafe internal chains of thought.

---

## 2. Core Architectural Principles & Decisions

1. **Specialist Tools over Monolithic VLMs**: Individual remote-sensing tasks (e.g., SAR speckle analysis vs. high-resolution optical object detection vs. bi-temporal differential change) possess vastly different mathematical and feature properties. We isolate these into modular specialist tools rather than burdening a single multi-modal LLM with all capabilities.
2. **Controlled, Bounded Agentic Dispatch**: The system utilizes a deterministic, registry-constrained agent router. The router parses user intent and image metadata, selecting only from a strictly governed **Predefined Tool Registry**. Unrestricted tool calling, arbitrary code execution, and unconstrained agent loops are strictly prohibited.
3. **Observable Execution Trace (Auditability)**: Hackathon evaluators and operational field officers require transparency. The system generates an end-to-end execution trace recording: input validation status, detected query intent, routed specialist tool, permitted parameters, stage latencies, confidence metrics, and generated visual evidence. Raw, hidden LLM chain-of-thought (CoT) is kept private to prevent prompt injection and hallucinations, exposing only the structured execution trace.
4. **Synchronous, Lean MVP**: Avoid premature distributed complexity (no Kafka, Celery, Kubernetes, microservice meshes). The initial architecture is a clean, modular monolith with synchronous request/response contracts suited for local GPU testing and resilient live hackathon judging.
5. **Separation of Binary Rasters and Relational Metadata**: Heavy satellite raster binaries (GeoTIFF/PNG/JPEG) and generated overlay masks are stored strictly on filesystem/object storage. Relational database engines (PostgreSQL) store only image metadata, spatial properties, session states, and query traces.
6. **Zero Unverified Model Checkpoints**: Concrete weights and checkpoints remain deferred to Phase 3 (AI/Model Selection). Architecture specifies strictly modular interfaces, input/output tensor contracts, and adapter slots.

---

## 3. High-Level System Architecture

The end-to-end system follows a deterministic pipeline from user interaction to visual result composition:

```
User
  │
  ▼
React Frontend (TypeScript + Vite)
  │
  ▼  [HTTP REST / Multipart Upload]
FastAPI Backend Gateway
  │
  ▼
Input Compatibility Validator
  │
  ▼
Analysis Manager (Pipeline Orchestrator)
  │
  ▼
Agent Router (Intent Parser & Guardrail)
  │
  ▼
Predefined Model / Tool Registry
  │
  ├───────────────────┬───────────────────┬───────────────────┬───────────────────┐
  ▼                   ▼                   ▼                   ▼                   ▼
Specialist Tool 1:   Specialist Tool 2:  Specialist Tool 3:  Specialist Tool 4:  Specialist Tool 5:
RS VQA Engine       Visual Grounding    Scene Captioning    Bi-Temporal Change  Optical-SAR Paired
(Overhead VLM)      (Bounding Boxes)    (Contextual Desc)   (Diff Mask Engine)  (Cross-Modal Fusion)
  │                   │                   │                   │                   │
  └───────────────────┴───────────────────┼───────────────────┴───────────────────┘
                                          │
                                          ▼
                                   Evidence Builder
                         (Bounding Boxes, Heatmaps, Masks)
                                          │
                                          ▼
                                 Confidence Estimator
                       (Calibrated Detection & VQA Scores)
                                          │
                                          ▼
                                Observable Execution Trace
                      (Step Latencies, Tool Decisions, Stages)
                                          │
                                          ▼
                                   Result Composer
                       (Synthesized JSON Response Envelope)
                                          │
                                          ▼
                          React Frontend (Visual Evidence UI)
```

---

## 4. Component Deep Dive: Roles, I/O, Dependencies & Failures

### 4.1 React Frontend
* **Why It Exists**: Provides an intuitive, responsive interface for non-GIS domain experts (disaster responders, urban analysts, evaluators) to upload satellite images, query them in natural language, toggle visual evidence layers, and inspect the observable execution trace.
* **Responsibilities**:
  - Drag-and-drop ingestion supporting single-image, bi-temporal ($T_1, T_2$), and optical-SAR multi-sensor uploads.
  - Interactive canvas rendering visual overlays (color-coded bounding boxes, segmentation masks, change heatmaps) aligned with source pixels.
  - Collapsible/expandable execution trace drawer displaying step-by-step agent decisions, stage latencies, and confidence.
  - Session history and query input management.
* **Input**: User interactions (image uploads, natural language query text, layer toggle clicks).
* **Output**: HTTP REST requests (`multipart/form-data`, `application/json`).
* **Dependencies**: Web browser runtime, FastAPI backend endpoints.
* **Failure Modes**: Network timeout, malformed image rendering in canvas, browser memory exhaustion on ultra-large rasters (mitigated by image pre-scaling and client-side dimension checks).

### 4.2 FastAPI Backend Gateway
* **Why It Exists**: Serves as the high-throughput, asynchronous-ready API gateway and boundary layer between the presentation tier and the internal Python AI inference runtime.
* **Responsibilities**:
  - Request ingestion, deserialization, rate limiting, and CORS handling.
  - Routing multipart file streams to local disk/object storage.
  - Dispatching validated payloads to the Analysis Manager.
  - Serializing consolidated results into clean JSON envelopes.
* **Input**: Incoming HTTP requests from frontend.
* **Output**: HTTP responses (JSON payloads, binary image masks/evidence).
* **Dependencies**: Python standard runtime, Pydantic, Uvicorn, Local File Storage.
* **Failure Modes**: Request deserialization errors, unhandled internal exceptions, thread pool starvation under heavy concurrent requests (handled via centralized exception handlers).

### 4.3 Input Compatibility Validator
* **Why It Exists**: Remote-sensing models fail catastrophically or produce silent hallucinations if fed incompatible formats, mismatched spatial resolutions, missing sensor bands, or single images when paired images are required.
* **Responsibilities**:
  - Validate image format (PNG, JPEG, GeoTIFF) and file integrity.
  - Validate tensor shapes, channels ($C \ge 1$), aspect ratios, and minimum resolution thresholds ($H, W \ge 256$).
  - Enforce strict pairing rules:
    - *Bi-temporal*: Exactly two images ($T_1, T_2$) with matching dimensions and compatible coordinate frames.
    - *Optical-SAR*: Explicit sensor modality tagging (Optical RGB/Multispectral and SAR GRD).
  - Reject invalid inputs before invoking expensive GPU pipelines.
* **Input**: Raw uploaded file references, metadata tags, and query string.
* **Output**: `ValidationResult(is_valid: bool, error_code: str, normalized_tensors: dict)`.
* **Dependencies**: Pillow, OpenCV, NumPy, Rasterio (for GeoTIFF metadata).
* **Failure Modes**: Corrupted file headers, dimension mismatches, unsupported color depths (produces HTTP 422 with actionable diagnostic messages).

### 4.4 Analysis Manager (Pipeline Orchestrator)
* **Why It Exists**: Acts as the central transaction controller managing the end-to-end analytical workflow, lifecycle of the request, session state, and assembly of final results.
* **Responsibilities**:
  - Coordinate the sequential handoff from Validator $\to$ Agent Router $\to$ Model Registry $\to$ Specialist Tool $\to$ Evidence Builder $\to$ Confidence Estimator $\to$ Result Composer.
  - Collect timing metrics for each step to feed the Observable Execution Trace.
  - Ensure transaction isolation across queries.
* **Input**: Validated image identifiers and user query text.
* **Output**: Consolidated `AnalysisResponse` object.
* **Dependencies**: Input Validator, Agent Router, Result Composer.
* **Failure Modes**: Unhandled tool execution failure, pipeline timeout (catches tool exceptions and triggers graceful degradation path).

### 4.5 Agent Router (Intent Parser & Guardrail)
* **Why It Exists**: End users do not know which computer vision model to configure. The Agent Router autonomously deconstructs the user's natural language query, checks the available image inputs, and selects the optimal specialist tool.
* **Responsibilities**:
  - Parse query semantics and classify task intent into one of 5 supported tasks:
    1. `SINGLE_VQA`: Descriptive, counting, or spatial relationship queries.
    2. `VISUAL_GROUNDING`: Queries demanding target localization ("locate", "find", "detect", "where is").
    3. `SCENE_CAPTIONING`: Contextual scene overview and land-use summarization.
    4. `BI_TEMPORAL_CHANGE`: Comparative analysis between two timestamps.
    5. `OPTICAL_SAR_ANALYSIS`: Cross-modal reasoning involving radar backscatter.
  - Cross-check classified intent against uploaded assets (e.g., prevent routing to bi-temporal change if only one image was uploaded).
  - Select tool parameters strictly permitted by the Predefined Registry schema.
* **Input**: User query text, input metadata (asset count, sensor types).
* **Output**: `RoutingDecision(task_type: TaskEnum, tool_id: str, permitted_params: dict, routing_reasoning: str)`.
* **Dependencies**: NLP intent classification engine / lightweight domain classifier, Predefined Tool Registry.
* **Failure Modes**: Ambiguous user query (e.g., "Analyze this"), conflict between query and assets (falls back to default safe VQA/captioning or prompts user for clarification).

### 4.6 Predefined Model/Tool Registry
* **Why It Exists**: Prevents unrestricted agent behaviors and protects against runtime model loading failures by enforcing a strict catalog of certified specialist AI tools.
* **Responsibilities**:
  - Maintain a registry of available tools, their supported input shapes, parameter constraints, and required GPU/CPU memory footprints.
  - Validate requested parameters against strict schemas.
  - Route execution calls directly to registered Python callable wrappers.
* **Input**: Tool ID and parameter dictionary from Agent Router.
* **Output**: Verified execution handle and validated parameters.
* **Dependencies**: Python callable registry.
* **Failure Modes**: Invocation of unregistered tool ID (immediately blocked and logged as a routing anomaly).

### 4.7 Specialist AI Tools

#### A. Remote-Sensing VQA Engine
* **Purpose**: Performs natural language reasoning over overhead imagery, answering questions about infrastructure, counts, spatial layouts, and land use.
* **Design**: Domain-adapted vision-language inference module employing remote-sensing prompt templates and nadir-perspective feature projection.
* **Input**: Normalized optical image tensor, formatted prompt.
* **Output**: Natural language text answer, visual attention/activation coordinates.

#### B. Text-Guided Visual Grounding Engine
* **Purpose**: Locates specific objects or geographical features referred to in the text query (e.g., "Find all storage tanks", "Locate cargo vessels").
* **Design**: Open-vocabulary / referring expression grounding head producing precise 2D bounding boxes $[x_{min}, y_{min}, x_{max}, y_{max}]$ normalized to $[0, 1000]$ or $[0.0, 1.0]$.
* **Input**: Image tensor, target text phrase.
* **Output**: Array of detection boxes, category labels, box-level confidence scores.

#### C. Remote-Sensing Scene Captioning Engine
* **Purpose**: Generates holistic, domain-rich scene descriptions, identifying overall land cover (urban, maritime, agricultural, forest, barren) and spatial layout.
* **Design**: Lightweight vision encoder with descriptive captioning decoder adapted for remote sensing.
* **Input**: Image tensor.
* **Output**: Comprehensive natural language descriptive summary.

#### D. Bi-Temporal Change Understanding Engine
* **Purpose**: Compares two registered satellite scenes taken at Time $T_1$ and Time $T_2$ to isolate new construction, deforestation, flood inundation, or demolition.
* **Design**: Dual-stream / Siamese visual feature extractor computing differential correlation maps and generating a visual change mask + textual change summary.
* **Input**: Registered image pair $(I_{T1}, I_{T2})$, optional query focus.
* **Output**: Binary/multi-class change mask raster, quantitative change statistics (e.g., % area changed), natural language change commentary.

#### E. Optical-SAR Paired Analysis Engine
* **Purpose**: Jointly analyzes optical imagery with Synthetic Aperture Radar (SAR) to penetrate cloud cover, evaluate surface roughness, and isolate metallic/specular reflections.
* **Design**: Cross-modal feature alignment network pairing optical spectral bands with SAR backscatter (VV/VH polarization).
* **Input**: Co-registered Optical and SAR image pair $(I_{Opt}, I_{SAR})$, user query.
* **Output**: Cross-modal synthesized natural language answer, SAR-derived feature highlight mask (e.g., water boundary or ship detection under clouds).

### 4.8 Evidence Builder
* **Why It Exists**: Eliminates AI hallucination by creating concrete visual proof backing every linguistic assertion.
* **Responsibilities**:
  - Transform raw model output coordinates into styled bounding box overlays with class tags.
  - Convert differential change arrays into color-coded raster heatmaps/masks (e.g., Green = Vegetation Loss, Red = New Construction, Blue = Flood Inundation).
  - Export evidence artifacts as lightweight overlay PNGs or standardized GeoJSON/JSON vectors.
* **Input**: Raw bounding boxes, attention heatmaps, segmentation/change arrays.
* **Output**: `VisualEvidenceArtifact(type: str, overlay_url: str, geojson_data: dict, metadata: dict)`.
* **Dependencies**: OpenCV, NumPy, Matplotlib/Pillow.
* **Failure Modes**: Empty detection sets (produces empty evidence layer with explicit note rather than crashing).

### 4.9 Confidence Estimator
* **Why It Exists**: Decision-makers must know whether an AI output can be trusted or requires human verification.
* **Responsibilities**:
  - Calibrate and normalize raw model outputs into a standard $0.0 - 1.0$ confidence score.
  - Grounding confidence: Aggregated detection probability across predicted bounding boxes.
  - VQA / Text confidence: Normalized likelihood estimation combining token probabilities and semantic certainty indicators.
  - Apply threshold logic: If confidence $< 0.40$, trigger an uncertainty advisory flag.
* **Input**: Raw logits, detection confidence scores, token likelihoods.
* **Output**: `ConfidenceScore(overall: float, metric_type: str, uncertainty_flag: bool)`.
* **Dependencies**: NumPy, statistical calibration functions.
* **Failure Modes**: Model does not emit raw logits (falls back to heuristic entropy estimation).

### 4.10 Observable Execution Trace Engine
* **Why It Exists**: Hackathon judges and auditors must verify that SatQuery AI operates through a genuine, observable agentic pipeline rather than hard-coded responses.
* **Responsibilities**:
  - Capture timestamps and execution status for every pipeline stage:
    1. Input Validation (`PASS / FAIL`, dimensions, detected sensor).
    2. Intent Classification (`DETECTED_TASK`, confidence, reasoning).
    3. Tool Registry Dispatch (`SELECTED_TOOL`, permitted parameters).
    4. Model Inference (`EXECUTION_TIME_MS`, memory usage).
    5. Evidence Generation (`EVIDENCE_COUNT`, layer types).
    6. Confidence Calculation (`SCORE`, threshold status).
  - Format the trace into a clean, human-readable audit log.
  - Strip any raw internal chain-of-thought to prevent leakage of ungrounded intermediate LLM reasoning.
* **Input**: Stage events, metrics, parameter dictionaries.
* **Output**: `ExecutionTrace(trace_id: str, steps: list[TraceStep], total_latency_ms: float)`.
* **Dependencies**: Python logging, timing decorators.
* **Failure Modes**: Partial stage failure (records failure state in trace for transparency before aborting).

### 4.11 Result Composer
* **Why It Exists**: Assembles disparate model outputs, evidence artifacts, confidence scores, and execution logs into a unified, contract-compliant JSON response.
* **Responsibilities**:
  - Aggregate:
    - Natural language answer / report.
    - Visual evidence URLs and coordinates.
    - Confidence score and advisory notes.
    - Structured execution trace.
  - Persist metadata into PostgreSQL database.
* **Input**: Outputs from all prior stages.
* **Output**: Final `QueryResponseEnvelope` sent to frontend.
* **Dependencies**: Database client, Pydantic schemas.
* **Failure Modes**: Database persistence failure (still returns response to user while logging DB write error).

---

## 5. Architectural ASCII Diagrams

### A. Overall Architecture
```
+-----------------------------------------------------------------------------------+
|                                 USER / CLIENT                                     |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼ [HTTP REST / WebSocket]
+-----------------------------------------------------------------------------------+
|                        REACT FRONTEND (TypeScript + Vite)                        |
|  [Image Upload Canvas]  [Query Chat Input]  [Visual Evidence Layer]  [Trace Drawer]|
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼ [REST API /multipart]
+-----------------------------------------------------------------------------------+
|                                 FASTAPI BACKEND                                   |
|  ┌─────────────────────────────────────────────────────────────────────────────┐  |
|  │ 1. Ingestion & Validation Gateway                                           │  |
|  │    ├── Image Format & Integrity Checks (PNG, JPEG, GeoTIFF)                 │  |
|  │    └── Multi-Image Registration / Modality Pair Validation                  │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 2. Analysis Manager (Pipeline Orchestrator)                                 │  |
|  │    ├── Session Lifecycle & Latency Profiling                                │  |
|  │    └── State Management                                                     │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 3. Agent Router (Intent Parser & Guardrail)                                 │  |
|  │    ├── Query Intent Deconstruction                                          │  |
|  │    └── Strict Dispatch to Predefined Registry Only                          │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 4. Predefined Model / Tool Registry                                         │  |
|  │    ├── Parameter Validation (Bounded Schema)                                │  |
|  │    └── Dispatch to Modular Specialist AI Tools                              │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 5. Modular Specialist AI Tools (Python Inference Layer)                    │  |
|  │    ├─ [Tool 1: RS VQA] ───────────────────> Overhead VLM Inference         │  |
|  │    ├─ [Tool 2: Visual Grounding] ─────────> Bounding Box Coordinates       │  |
|  │    ├─ [Tool 3: Scene Captioning] ─────────> Holistic Land-Use Summary      │  |
|  │    ├─ [Tool 4: Bi-Temporal Change] ───────> Difference Mask & Change Rep   │  |
|  │    └─ [Tool 5: Optical-SAR Cross-Modal] ──> Cloud-Penetrating Synergy Rep  │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 6. Evidence Builder                                                         │  |
|  │    ├── Bounding Box Coordinate Overlays                                     │  |
|  │    └── Difference Heatmaps & Segmentation Masks                             │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 7. Confidence Estimator                                                     │  |
|  │    └── Calibrated Certainty Score Calculation (0.0 - 1.0)                   │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 8. Observable Execution Trace Engine                                        │  |
|  │    └── Step-by-Step Audit Log (Intent -> Tool -> Latency -> Evidence)      │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │
|  ┌──────────────────────────────────────▼──────────────────────────────────────┐  |
|  │ 9. Result Composer                                                          │  |
|  │    └── Structured JSON Assembly & Metadata Persistence                      │  |
|  └─────────────────────────────────────────────────────────────────────────────┘  |
+-----------------------------------------┬────────────────────────────────---------+
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
+---------------------------------------+   +---------------------------------------+
|          LOCAL FILE STORAGE           |   |          POSTGRESQL DATABASE          |
|  - Source Satellite Images            |   |  - Image Metadata & Asset IDs         |
|  - Cached Model Checkpoints           |   |  - Query Logs & Confidence Scores     |
|  - Generated Visual Evidence Masks    |   |  - Serialized Execution Traces        |
+---------------------------------------+   +---------------------------------------+
```

---

### B. Single-Image VQA Flow
```
[User Image + Query: "How many storage tanks are present?"]
                           │
                           ▼
               [Input Compatibility Validator]
                ├── Checks: Format OK, 1 Image
                └── Image Tensor Normalized
                           │
                           ▼
                    [Agent Router]
                ├── Intent: SINGLE_VQA
                └── Dispatches: Tool 'rs_vqa_engine'
                           │
                           ▼
              [Specialist Tool: RS VQA]
                ├── Domain Prompt: "Overhead Remote Sensing Analysis..."
                ├── Nadir-Adapted Feature Extraction
                └── Output: "There are 8 oil storage tanks in the northern sector."
                           │
                           ▼
                 [Confidence Estimator]
                └── Logit calibration -> 0.88 Confidence
                           │
                           ▼
                  [Execution Trace]
                └── Step 1: Validated (12ms) -> Step 2: VQA Model (450ms)
                           │
                           ▼
                   [Result Composer] ───> [Frontend Display]
```

---

### C. Grounding / Captioning Flow
```
[User Image + Query: "Locate all cargo vessels along the dock"]
                           │
                           ▼
               [Input Compatibility Validator]
                           │
                           ▼
                    [Agent Router]
                ├── Keyword Check: "Locate" / "Find" -> VISUAL_GROUNDING
                └── Tool Selected: 'rs_grounding_head'
                           │
                           ▼
        [Specialist Tool: Visual Grounding Head]
                ├── Feature Matching on Text Query: "cargo vessels"
                └── Output: Coordinates [[x1, y1, x2, y2], ...]
                           │
                           ▼
                   [Evidence Builder]
                └── Renders 2D bounding boxes with label tags
                           │
                           ▼
                 [Confidence Estimator]
                └── Detection confidence per box (Mean: 0.93)
                           │
                           ▼
                  [Execution Trace]
                └── Logs grounding parameters, box count, latencies
                           │
                           ▼
                   [Result Composer] ───> [Frontend Box Overlay]
```

---

### D. Bi-Temporal Change Flow
```
[User Images: T1 (2023) + T2 (2024) + Query: "What changed?"]
                           │
                           ▼
               [Input Compatibility Validator]
                ├── Checks: Exactly 2 images present
                ├── Verifies: Dimensions Match (W1=W2, H1=H2)
                └── Asserts: Registered Spatial Frames
                           │
                           ▼
                    [Agent Router]
                ├── Intent: BI_TEMPORAL_CHANGE
                └── Tool Selected: 'rs_change_engine'
                           │
                           ▼
        [Specialist Tool: Bi-Temporal Change Engine]
                ├── Siamese Feature Extraction (T1 & T2)
                ├── Difference Correlation Computation
                └── Output: Binary change array + textual diff summary
                           │
                           ▼
                   [Evidence Builder]
                └── Generates color-coded Difference Heatmap / Mask
                           │
                           ▼
                 [Confidence Estimator]
                └── Spatial segmentation certainty score: 0.86
                           │
                           ▼
                  [Execution Trace]
                └── Records dual-tensor validation, model latency (720ms)
                           │
                           ▼
                   [Result Composer] ───> [Frontend Split/Diff Viewer]
```

---

### E. Optical-SAR Flow
```
[User Images: Optical RGB + SAR GRD + Query: "Detect ships through clouds"]
                               │
                               ▼
                   [Input Validator]
                ├── Verifies: 1 Optical + 1 SAR image
                └── Checks: Polarization/Channel tagging
                               │
                               ▼
                        [Agent Router]
                ├── Intent: OPTICAL_SAR_ANALYSIS
                └── Tool Selected: 'rs_optical_sar_fuser'
                               │
                               ▼
        [Specialist Tool: Optical-SAR Analysis Engine]
                ├── Optical stream: Identifies cloud-occluded zones
                ├── SAR stream: Extracts high-backscatter radar targets
                └── Synergistic Output: Pinpoints metallic hulls beneath cloud deck
                               │
                               ▼
                       [Evidence Builder]
                └── Renders SAR backscatter highlight overlay on optical base
                               │
                               ▼
                     [Confidence Estimator]
                └── Multi-sensor agreement metric: 0.91
                               │
                               ▼
                      [Execution Trace]
                └── Records cross-modal alignment and tool trace
                               │
                               ▼
                       [Result Composer] ───> [Frontend Cloud/Radar View]
```

---

### F. Agent Routing Flow
```
[Incoming Request: Query String + Image Metadata Envelope]
                           │
                           ▼
              [Query Intent Normalization]
               (Strip whitespace, tokenize, extract spatial keywords)
                           │
                           ▼
         [Asset Constraint Check]
         ├── Asset Count = 1?  ──> Can route to: VQA, Grounding, Captioning
         ├── Asset Count = 2 & Temporal? ──> Can route to: Bi-Temporal Change
         └── Asset Count = 2 & Multi-Sensor? ──> Can route to: Optical-SAR
                           │
                           ▼
          [Does Query Demand Grounding?]
          ("find", "locate", "detect", "where are", "draw box")
                 │                    │
                YES                   NO
                 │                    │
                 ▼                    ▼
     [Route: VISUAL_GROUNDING]  [Does Query Ask for Change?]
                                 ("difference", "new buildings", "before vs after")
                                        │                    │
                                       YES                   NO
                                        │                    │
                                        ▼                    ▼
                           [Route: BI_TEMPORAL_CHANGE] [Does Input Include SAR?]
                                                             │            │
                                                            YES           NO
                                                             │            │
                                                             ▼            ▼
                                                [Route: OPTICAL_SAR]  [Route: SINGLE_VQA]
                           │
                           ▼
        [Validate Selected Tool against Predefined Registry]
         ├── Is Tool ID registered? YES
         └── Are parameters within bounded limits? YES
                           │
                           ▼
        [Emit RoutingDecision + Append to Execution Trace]
```

---

### G. Input Validation Flow
```
[Raw Uploaded Files & Metadata]
                │
                ▼
    [1. File Extension & MIME Check]
    ├── Allowed: .png, .jpg, .jpeg, .tif, .tiff
    └── Failed? ──> Terminate (HTTP 415 Unsupported Media Type)
                │
                ▼
    [2. File Integrity & Header Inspection]
    ├── Attempt open via Pillow / OpenCV / Rasterio
    └── Corrupted file? ──> Terminate (HTTP 422 Corrupted File)
                │
                ▼
    [3. Dimension & Channel Thresholds]
    ├── Width >= 256, Height >= 256
    ├── Channels >= 1 (Grayscale/SAR) or == 3 (RGB)
    └── Out of bounds? ──> Terminate (HTTP 422 Invalid Dimensions)
                │
                ▼
    [4. Multi-Image Modality / Pair Verification]
    ├── If Bi-temporal: Is count == 2 AND Dimensions identical?
    ├── If Optical-SAR: Is exactly 1 Optical AND 1 SAR tagged?
    └── Violation? ──> Terminate (HTTP 422 Pairing Mismatch)
                │
                ▼
    [Validation Passed: Construct Normalized Tensor Handles]
```

---

### H. Execution Trace Flow
```
[Request Initiated]
        │
        ├──> [Event: VALIDATION_START] ──────> Timer Start
        ├──> [Event: VALIDATION_DONE] ───────> Record Status: "PASSED", Latency: 14ms
        │
        ├──> [Event: ROUTING_START] ─────────> Intent Parser
        ├──> [Event: ROUTING_DONE] ──────────> Record Tool: "rs_grounding", Latency: 32ms
        │
        ├──> [Event: INFERENCE_START] ───────> Model Dispatch
        ├──> [Event: INFERENCE_DONE] ────────> Record Output Status: "SUCCESS", Latency: 420ms
        │
        ├──> [Event: EVIDENCE_GEN_DONE] ─────> Record Evidence: "4 Bounding Boxes", Latency: 18ms
        ├──> [Event: CONFIDENCE_DONE] ───────> Record Score: 0.92, Latency: 2ms
        │
        ▼
[Trace Engine Sanitization]
 ├── Remove any internal model chain-of-thought
 ├── Assemble clean timeline: [Validation -> Router -> Inference -> Evidence -> Confidence]
 └── Embed in JSON payload `execution_trace`
```

---

### I. Frontend-Backend-AI Flow
```
+--------------------+        +--------------------+        +--------------------+
|  React Frontend    |        |  FastAPI Backend   |        |  AI Inference Core |
+--------------------+        +--------------------+        +--------------------+
          │                              │                             │
          │ 1. POST /api/v1/query        │                             │
          │    (Multipart Image + Query) │                             │
          │─────────────────────────────>│                             │
          │                              │ 2. Validate & Store File    │
          │                              │    (Save to disk/storage)   │
          │                              │                             │
          │                              │ 3. Dispatch to Orchestrator │
          │                              │────────────────────────────>│
          │                              │                             │ 4. Route Tool
          │                              │                             │ 5. Execute Model
          │                              │                             │ 6. Build Evidence
          │                              │                             │ 7. Calibrate Conf.
          │                              │ 8. Return Analysis Payload  │
          │                              │<────────────────────────────│
          │                              │                             │
          │                              │ 9. Write Audit to DB        │
          │ 10. Return 200 OK + JSON     │                             │
          │<─────────────────────────────│                             │
          │                              │                             │
          │ 11. Render Answer + Overlays │                             │
          │     + Execution Trace Drawer │                             │
```

---

### J. Storage / Database Relationship
```
+---------------------------------------------------------------------------------+
|                               POSTGRESQL DATABASE                               |
|                                                                                 |
|  +---------------------+        +--------------------+        +--------------+  |
|  |     assets          |        |   query_records    |        |   sessions   |  |
|  +---------------------+        +--------------------+        +--------------+  |
|  | PK asset_id (UUID)  |◄───┐   | PK query_id (UUID) |        | PK id (UUID) |  |
|  |    filename         |    │   | FK session_id      |───────>|    user_tag  |  |
|  |    file_path (URI)  |──┐ │   |    user_query      |        |    created_at|  |
|  |    modality         |  │ │   |    detected_intent |        +--------------+  |
|  |    dimensions       |  │ │   |    selected_tool   |                          |
|  |    created_at       |  │ │   |    answer_text     |                          |
|  +---------------------+  │ │   |    confidence      |                          |
|                           │ │   |    execution_trace |                          |
|                           │ │   |    total_latency_ms|                          |
|                           │ │   |    created_at      |                          |
|                           │ │   +---------┬----------+                          |
|                           │ │             │                                     |
|                           │ │             ▼                                     |
|                           │ │   +---------------------+                         |
|                           │ │   |   visual_evidence   |                         |
|                           │ │   +---------------------+                         |
|                           │ │   | PK evidence_id(UUID)|                         |
|                           │ └───| FK asset_id         |                         |
|                           │     | FK query_id         |                         |
|                           │     |    evidence_type    |                         |
|                           │     |    overlay_path     |──┐                      |
|                           │     |    data_payload     |  │                      |
|                           │     |    confidence       |  │                      |
|                           │     +---------------------+  │                      |
+---------------------------│------------------------------│----------------------+
                            │                              │
                            ▼                              ▼
+---------------------------------------------------------------------------------+
|                       LOCAL FILESYSTEM / OBJECT STORAGE                         |
|                                                                                 |
|   storage/uploads/                              storage/evidence/               |
|   ├── ast_8f12.png (Original Optical)           ├── ev_33a1.png (Difference)   |
|   ├── ast_9b44.tif (Original SAR)               └── ev_77b2.png (Mask Overlay) |
+---------------------------------------------------------------------------------+
```

---

## 6. Subsystem Architectures

### 6.1 Backend Architecture
* **Framework**: FastAPI (Python 3.10+), running under Uvicorn ASGI server.
* **Structure**: Clean Layered Architecture:
  - `api/`: Route definitions, API versioning (`/api/v1`), request/response schemas (Pydantic v2).
  - `core/`: Config settings, security middlewares, centralized error handling.
  - `validation/`: Ingestion checks, raster integrity, multi-image pair validators.
  - `orchestration/`: Analysis Manager, Agent Router, Predefined Tool Registry.
  - `services/`: Concrete specialist tool wrappers (VQA, Grounding, Change, Optical-SAR).
  - `storage/`: File persistence handlers, database repositories.
* **Concurrency Model**: Synchronous/blocking GPU inference calls are wrapped in thread-pool workers (`run_in_threadpool`) to prevent blocking FastAPI’s asynchronous event loop.

### 6.2 Frontend Architecture
* **Framework**: React 18+ with TypeScript, bundled via Vite.
* **Styling**: Tailored, modern Vanilla CSS with dark mode aesthetics, glassmorphism panels, and clear typographic contrast for operational readouts.
* **Key Components**:
  - `ImageCanvas`: Multi-layer HTML5 Canvas / SVG overlay engine that handles pan, zoom, and pixel-accurate rendering of bounding boxes and change heatmaps.
  - `ModeSelector`: Pre-sets upload zones for Single Image, Bi-Temporal ($T_1, T_2$), or Optical-SAR.
  - `TraceDrawer`: Slide-out or expandable audit panel showing live execution stages, latency counters, and confidence gauges.
  - `EvidencePanel`: Layer toggle list allowing users to turn specific detection categories or difference masks on/off over the base raster.
* **State Management**: React Context or lightweight Zustand store managing active session, uploaded assets, and query history.

### 6.3 AI Service Architecture
* **Modular Specialist Pattern**: AI pipelines operate as isolated, self-contained Python modules adhering to a standard `SpecialistTool` interface:
  ```python
  class BaseSpecialistTool(ABC):
      @abstractmethod
      def validate_input(self, payload: ToolInput) -> bool: ...
      
      @abstractmethod
      def execute(self, payload: ToolInput) -> ToolOutput: ...
  ```
* **Memory Management**: Models remain loaded in memory if VRAM permits, or dynamically execute with PyTorch `no_grad()` inference mode and periodic cache garbage collection (`torch.cuda.empty_cache()`).
* **Hardware Adaptation**: Automatic device targeting (`cuda` if available, falling back to `cpu` with quantized weights).

### 6.4 Storage Architecture
* **Raster Storage**: Images are saved with content-addressed or UUID-prefixed filenames in `storage/uploads/`.
* **Evidence Storage**: Generated visual masks, bounding box GeoJSON, and difference overlays are written to `storage/evidence/`.
* **Database Responsibility**: PostgreSQL (or SQLite in self-contained local mode) is responsible strictly for:
  - Tracking image asset metadata (dimensions, GSD, sensor type, filepath).
  - Preserving session history.
  - Recording query logs, confidence metrics, and serialized JSON execution traces.
  - Binary imagery is never stored in relational column fields (`BYTEA`/`BLOB` avoided).

---

## 7. Operational & Development Architectures

### 7.1 Local Development Architecture
* **Runtime**: Single Windows/Linux developer machine with NVIDIA GPU.
* **Backend**: FastAPI started via `uvicorn backend.main:app --reload --port 8000`.
* **Frontend**: React Vite dev server via `npm run dev -- --port 3000`.
* **Storage**: Local filesystem directories (`./storage/uploads`, `./storage/evidence`).
* **Database**: Local PostgreSQL instance or zero-config fallback to SQLite (`satquery.db`) to ensure zero-friction onboarding during hackathon hacking.
* **Model Storage**: Pre-downloaded weights cached in local directory (`./models/cache`).

### 7.2 Future Deployment Architecture
* **Containerization**: Multi-stage Dockerfiles for Frontend (Nginx alpine serving static assets) and Backend (CUDA-enabled Python base).
* **Composition**: `docker-compose.yml` linking Frontend, FastAPI Backend Gateway, and PostgreSQL.
* **Object Storage**: Seamless substitution of local storage with AWS S3, MinIO, or Google Cloud Storage via standard storage abstraction interfaces.
* **Scaling**: Horizontal scaling of FastAPI gateway; AI inference service deployed on dedicated GPU worker nodes.

---

## 8. Team Ownership (6-Person SIH Allocation)

| Role | Primary Ownership Areas | Key Deliverables |
| :--- | :--- | :--- |
| **Member 1: System Architect & AI Lead** | - AI Model Strategy & VLM Adaptation<br>- Predefined Tool Registry Design<br>- GPU Resource & Inference Optimization | - Remote-Sensing VQA Pipeline<br>- Model loading & inference wrappers<br>- Confidence scoring calibration |
| **Member 2: Computer Vision Specialist** | - Visual Grounding / Localization Head<br>- Bi-Temporal Change Detection Engine<br>- Optical-SAR Cross-Modal Fusion | - Bounding box localization tool<br>- Differential change masking tool<br>- SAR backscatter integration tool |
| **Member 3: Backend & Orchestration Engineer** | - FastAPI Gateway & Middleware<br>- Analysis Manager & Agent Router<br>- Input Compatibility Validator | - REST endpoints & schemas<br>- Task classification & routing logic<br>- Observable Execution Trace engine |
| **Member 4: Frontend & UX Engineer** | - React + TypeScript Application<br>- Interactive Image Canvas & Overlays<br>- Layer toggles & Trace Drawer | - High-aesthetic UI dashboard<br>- Bounding box/mask canvas renderer<br>- Observable trace audit UI |
| **Member 5: Data & Evidence Engineer** | - Benchmark Datasets (Optical & SAR)<br>- Evidence Builder (Masks, Heatmaps)<br>- Storage & PostgreSQL Database | - Curated demonstration imagery<br>- Pixel-accurate overlay generators<br>- DB schema & storage handlers |
| **Member 6: QA, Integration & Evaluator Lead** | - End-to-End Integration Testing<br>- Fail-Safe Demo Package Preparation<br>- Evaluator Script & Benchmark Validation | - Test suite (unit, integration, load)<br>- Demo showcase scenarios<br>- Hackathon presentation materials |

---

## 9. Architecture Decision Record (ADR)

### ADR-01: React + TypeScript Frontend
* **Context**: Need a responsive, rock-solid UI for rendering complex visual evidence (bounding boxes, masks) and execution traces.
* **Decision**: Adopt React 18 with TypeScript.
* **Reasoning**: TypeScript provides compile-time safety for API contracts. React’s component model allows seamless isolation of the interactive canvas, chat drawer, and trace logs.

### ADR-02: FastAPI Backend
* **Context**: Need a high-performance Python API gateway that interfaces natively with deep learning frameworks.
* **Decision**: Adopt FastAPI with Uvicorn.
* **Reasoning**: FastAPI offers native async support, automatic OpenAPI/Swagger documentation, and Pydantic v2 data validation, allowing rapid and error-free API development during hackathons.

### ADR-03: Python AI Layer
* **Context**: Deep learning models for remote sensing, vision-language processing, and image arrays require standard ecosystem tooling.
* **Decision**: Keep the AI service layer in native Python using PyTorch, OpenCV, and Pillow.
* **Reasoning**: All major remote-sensing models, vision-language backbones, and image manipulation libraries are Python-first.

### ADR-04: PostgreSQL (with SQLite Local Fallback)
* **Context**: Need persistent tracking of asset metadata, query logs, confidence scores, and execution traces.
* **Decision**: Use PostgreSQL for standard production deployment, with transparent configuration fallback to SQLite for zero-setup local hackathon environments.
* **Reasoning**: Relational structure suits audit logs and asset records. Providing SQLite fallback eliminates database connection roadblocks during live hackathon demos.

### ADR-05: Local / Object File Storage (No Binary Blobs in DB)
* **Context**: Satellite imagery rasters range from multi-megabyte PNGs to high-resolution GeoTIFFs.
* **Decision**: Store all image binaries and generated masks on filesystem/object storage; store only string URI/path references in the database.
* **Reasoning**: Storing large raster blobs in relational databases degrades query performance, inflates backup sizes, and complicates image streaming.

### ADR-06: Predefined Model Registry
* **Context**: The agent router needs access to specialist capabilities.
* **Decision**: Enforce a closed, predefined Model/Tool Registry.
* **Reasoning**: Eliminates runtime discovery failures, prevents unconstrained tool hallucinations, and guarantees that every callable tool has known hardware requirements.

### ADR-07: Controlled Agent Router (No Unrestricted Tool Calling)
* **Context**: Autonomous LLM agents with unrestricted tool access frequently enter infinite loops or execute unsafe operations.
* **Decision**: Implement a bounded router that only classifies intent and dispatches to registered tools with validated parameters.
* **Reasoning**: Ensures deterministic, bounded execution, rapid response times, and eliminates prompt injection risks.

### ADR-08: Synchronous MVP Architecture
* **Context**: Need to decide between asynchronous message queues (RabbitMQ/Celery) vs. direct synchronous request/response.
* **Decision**: Build the initial MVP with synchronous request/response execution.
* **Reasoning**: For an interactive hackathon demo with target latencies of 3–8 seconds, synchronous execution eliminates message queue failures, worker coordination bugs, and unnecessary infrastructure overhead.

### ADR-09: No RAG (Retrieval-Augmented Generation) Initially
* **Context**: Consideration of whether to add text document RAG to the core platform.
* **Decision**: Exclude RAG from the initial MVP.
* **Reasoning**: The problem statement requires image-to-text visual question answering, grounding, and change detection on satellite imagery, not document search. Adding text RAG would consume compute without addressing core remote-sensing requirements.

### ADR-10: No Vector Database Initially
* **Context**: Consideration of vector databases (e.g., Milvus, Chroma, Pinecone) for the core pipeline.
* **Decision**: Exclude vector databases from the initial image-analysis pipeline.
* **Reasoning**: The core workflow is direct inference over uploaded satellite rasters (VQA, Grounding, Change, Optical-SAR). Embedding-based retrieval is unnecessary for single-query multi-sensor analysis.

### ADR-11: No Unnecessary Microservices
* **Context**: Architectural topology selection (microservices vs. modular monolith).
* **Decision**: Implement a modular monolith backend.
* **Reasoning**: Microservices introduce network overhead, serialization latency, distributed failure points, and deployment friction. A modular monolith provides clean code separation while running reliably in a single process.

---

## 10. Architecture Risks & Mitigations

| Risk | Why It Matters | Mitigation Strategy |
| :--- | :--- | :--- |
| **GPU / VRAM Uncertainty (e.g., RTX 3050 VRAM configuration not yet verified)** | An RTX 3050 may have 4 GB or 6 GB VRAM. Large VLMs or multi-stream change models will crash with Out-Of-Memory (CUDA OOM) errors during inference. | 1. Implement dynamic CPU/GPU device selection.<br>2. Select models supporting 4-bit/8-bit quantization.<br>3. Enforce raster tiling/downscaling on ingestion ($1024 \times 1024$ max).<br>4. Run sequential single-tool inference rather than parallel model invocations. |
| **Optical-SAR Spatial Misalignment** | Optical and SAR images over the same scene often have different projections, pixel scales, and viewing geometries, leading to false cross-modal correlations. | Enforce pre-registered demonstration pairs for MVP. Include spatial dimension and aspect ratio compatibility checks in the Input Validator. |
| **Agent Routing Misclassification** | If the router misclassifies a change query as single-image VQA, the entire analysis fails. | Implement dual intent heuristics: combine lightweight semantic classification with strict input constraints (e.g., if 2 images uploaded with change keywords, force `BI_TEMPORAL_CHANGE`). |
| **Inference Latency Exceeding Hackathon Demo Tolerances** | Long wait times ($> 15$ seconds) lose evaluator attention and risk live demo timeouts. | Cache model weights in memory; employ optimized PyTorch inference modes (`torch.inference_mode()`); utilize lightweight backbones for real-time responsiveness. |
| **Hallucination on Low-Resolution Imagery** | Generic models hallucinate fine-grained objects (e.g., cars, small boats) on low GSD imagery where they are mathematically invisible. | Incorporate resolution awareness into prompt templates and enforce confidence thresholds ($\tau < 0.40$) that trigger uncertainty warnings. |

---

## 11. Phase 2 Definition of Done Checklist

- [x] **Mandatory Capabilities Represented**: Single-image VQA, Visual Grounding / Captioning, Bi-temporal Change, Optical-SAR paired analysis, RS VLM adaptation, agentic selection, input validation, visual evidence, confidence information, and observable execution trace are all fully represented in the architecture.
- [x] **Component Responsibilities Defined**: Every component across frontend, backend, validation, routing, inference, evidence, confidence, and trace has explicit inputs, outputs, dependencies, and failure modes.
- [x] **Data Flows Documented**: End-to-end data flows, AI inference flows, and multi-sensor paths are completely documented.
- [x] **Agent Routing Documented**: Deterministic, bounded routing logic and Predefined Tool Registry guardrails are established.
- [x] **Validation Documented**: Format, dimension, channel, and multi-image pairing validation rules are defined.
- [x] **Visual Evidence Documented**: Generation of bounding boxes, difference heatmaps, and masks is specified.
- [x] **Execution Trace Documented**: Observable trace schema, stage timings, and separation from hidden LLM reasoning are detailed.
- [x] **Team Ownership Documented**: 6-person SIH team role breakdown is allocated.
- [x] **No Unverified Model Claims**: Exact weights and checkpoints remain deferred to Phase 3 (AI/Model Selection).
- [x] **ASCII Diagrams Included**: All 10 required architectural diagrams (A through J) are present.
- [x] **ADR Included**: Architectural decisions and rationales (Frontend, Backend, AI layer, Storage, DB, Agent, Synchronous design, No RAG, No Vector DB, No Microservices) are documented.
- [x] **GPU/VRAM Risk Addressed**: RTX 3050 VRAM uncertainty is analyzed with concrete mitigation steps.

---
*End of Phase 2 System Architecture Specification. Awaiting explicit instruction before proceeding to Phase 3.*
