# Product Requirements Document (PRD) — SatQuery AI

## 1. Product Overview
**SatQuery AI** is an intelligent, multi-modal Earth Observation (EO) and Remote Sensing (RS) analytical assistant developed for the **Smart India Hackathon (SIH)**. The platform bridges the gap between complex satellite imagery (high-resolution optical and Synthetic Aperture Radar / SAR) and end users by providing natural language interaction, agentic task orchestration, verifiable visual evidence, and transparent execution traces.

Unlike generic Vision-Language Models (VLMs) that struggle with nadir/overhead perspectives, multi-sensor cross-matching, and non-RGB characteristics, SatQuery AI is tailored for remote-sensing semantics, bi-temporal change reasoning, and multi-sensor (Optical + SAR) analytical queries.

---

## 2. Problem Statement
Satellite and aerial imagery volumes are exploding due to public earth observation missions (e.g., Sentinel, Landsat, ISRO Cartosat/EOS series) and commercial constellations. However:
1. **High Domain Barrier**: Non-GIS experts (disaster response teams, urban planners, agricultural officers, defense analysts) cannot easily query raw satellite imagery without specialized GIS software and manual visual interpretation.
2. **Generic VLM Failures**: Standard multi-modal LLMs lack domain adaptation for satellite overhead perspectives, complex multi-spectral bands, scale variations, and SAR microwave characteristics (speckle, backscatter, polarization).
3. **Black-Box Outputs**: Existing AI tools often produce hallucinations or ungrounded claims without verifiable visual localization (bounding boxes, heatmaps, masks), confidence measures, or observable reasoning chains.
4. **Complex Multi-Sensor & Temporal Demands**: Crucial applications require analyzing temporal changes (T1 vs. T2) or cross-referencing cloud-penetrating SAR with optical data, which single-image generic models cannot handle natively.

---

## 3. Product Vision
To deliver an open, reliable, and agent-driven Remote Sensing Query Engine that empowers decision-makers to ask complex analytical questions in plain natural language, instantly receiving accurate answers backed by localized visual evidence, quantified confidence scores, and an observable execution trace.

---

## 4. Target Users
* **Disaster Management Authorities & First Responders** (NDRF, SDMA): Rapid damage assessment, flood extent mapping, landslide localization.
* **Urban & Regional Planners**: Monitoring unauthorized construction, encroached water bodies, infrastructure progress.
* **Agricultural & Environmental Analysts**: Crop condition checks, deforestation monitoring, water reservoir depletion tracking.
* **Defense & Maritime Surveillance Evaluators**: Port vessel activity, airfield monitoring, change detection in border infrastructure.
* **Hackathon Evaluators & Domain Researchers**: Assessing technical rigor, modular design, AI safety, and explainability in EO workflows.

---

## 5. User Personas

### Persona A: Rajesh Kumar — Disaster Response Officer
* **Background**: Field coordinator during monsoon flooding events.
* **Goal**: Needs immediate answers on submerged bridges, flooded road arteries, and affected settlements using post-flood optical and cloud-piercing SAR imagery.
* **Pain Points**: Cloud cover blinds optical satellites; lacks time to manually run QGIS workflows or decipher raw SAR backscatter.
* **Expectations from SatQuery AI**: Can upload pre- and post-flood images or SAR tiles, ask "Which road segments are inundated?", and receive a pinpointed visual overlay with high confidence.

### Persona B: Ananya Sharma — Urban Infrastructure Analyst
* **Background**: Municipal planning consultant tracking illegal encroachments and land-use changes.
* **Goal**: Detect bi-temporal changes between 2023 and 2024 satellite passes over urban peripheries.
* **Pain Points**: Comparing two multi-gigabyte rasters by eye is exhausting and prone to human oversight.
* **Expectations from SatQuery AI**: Ask "What new structures were erected between Image T1 and Image T2?", receiving highlighted visual diffs and quantified structural counts.

### Persona C: SIH Hackathon Jury / Technical Evaluator
* **Background**: Remote sensing scientist and AI systems evaluator.
* **Goal**: Verify if the system actually understands RS characteristics, avoids hallucinations, selects appropriate specialized models, and exposes clear execution traces rather than acting as a static API wrapper.
* **Expectations from SatQuery AI**: Transparent step-by-step pipeline view (intent classification -> modality validation -> model routing -> evidence generation -> answer synthesis) with calibrated confidence metrics.

---

## 6. Core User Journeys

### Journey 1: Single-Image VQA & Object Grounding
1. User uploads a high-resolution satellite/aerial image.
2. User enters a query (e.g., *"How many cargo vessels are berthed at the western docks, and what are their locations?"*).
3. The system validates image dimensions, channels, and metadata.
4. The Agentic Router recognizes the dual intent: numerical counting/VQA + visual object grounding.
5. The system invokes the RS-adapted VLM and object localization tool.
6. The user receives:
   - A direct, natural language answer.
   - Bounding boxes / heatmaps highlighting the identified vessels.
   - Confidence score and step-by-step agent execution trace.

### Journey 2: Bi-Temporal Change Detection
1. User uploads two registered satellite images of the same AOI (Area of Interest) captured at Time $T_1$ and Time $T_2$.
2. User asks: *"Identify newly cleared forest areas and infrastructure expansion between these dates."*
3. System verifies spatial alignment, resolution compatibility, and temporal ordering ($T_1 < T_2$).
4. Router activates the Bi-Temporal Change Understanding pipeline.
5. Visual change heatmaps/masks are generated alongside a natural language summary quantifying the extent and nature of change.
6. User inspects the side-by-side comparison with synchronized pan-zoom and execution logs.

### Journey 3: Optical-SAR Cross-Modal Analysis
1. User supplies a cloudy optical image and a corresponding SAR image (e.g., Sentinel-1 GRD or equivalent).
2. User asks: *"Verify industrial facility activity and water boundary beneath cloud cover."*
3. Input validation confirms paired Optical + SAR inputs.
4. Router schedules cross-modal feature alignment (SAR backscatter analysis for surface roughness/water delineation + optical context where cloud-free).
5. User receives a synthesized response revealing obscured structures with visual evidence derived from the SAR modality.

---

## 7. Core Use Cases
* **UC-01: Single-Image Remote-Sensing VQA**: Answering descriptive, counting, spatial relationship, and attribute questions on aerial and satellite imagery.
* **UC-02: Single-Image Visual Grounding / Object Localization**: Detecting, categorizing, and locating specific targets (aircraft, ships, storage tanks, bridges, buildings) with coordinate bounding boxes.
* **UC-03: Bi-Temporal Change Understanding**: Identifying semantic additions, demolitions, land-use shifts, and environmental variations between two timestamps.
* **UC-04: Optical-SAR Paired Analysis**: Fusing or co-analyzing complementary optical spectrum and Synthetic Aperture Radar data for all-weather, day-and-night observation.
* **UC-05: Agentic Query Deconstruction & Tool Routing**: Parsing multi-step user queries into deterministic execution graphs with specialized model dispatch.
* **UC-06: Visual Evidence & Transparency**: Generating overlaid spatial evidence (heatmaps, bounding boxes, segmentation contours) paired with natural language outputs.
* **UC-07: Observable Audit & Execution Trace**: Displaying the internal decisions, intermediate tool outputs, execution time, and confidence at each pipeline stage.

---

## 8. Functional Requirements

### FR-1: Ingestion & Input Validation
* **FR-1.1**: The system must accept standard geospatial and computer vision image formats (GeoTIFF, PNG, JPEG).
* **FR-1.2**: The system must validate input dimensions, aspect ratio, minimum resolution, channel count, and file integrity before dispatching to models.
* **FR-1.3**: For multi-image tasks, the system must enforce input pairing rules:
  - Bi-temporal: Exactly two images ($T_1$, $T_2$) covering the same scene.
  - Optical-SAR: Modality tagging for Optical and SAR inputs.
* **FR-1.4**: If invalid or corrupted inputs are detected, the system must abort gracefully with human-readable diagnostic error messages.

### FR-2: Agentic Task & Model Selection
* **FR-2.1**: The system must parse the user query and uploaded assets to deduce the task category:
  - Single-image VQA
  - Single-image Visual Grounding / Target Detection
  - Bi-temporal Change Detection
  - Optical-SAR Multi-Sensor Query
* **FR-2.2**: The router must dynamically construct an execution plan selecting the appropriate specialized models, preprocessing steps, and post-processors.
* **FR-2.3**: The router must support fallback handling if an initial model output falls below minimum confidence thresholds.

### FR-3: Remote-Sensing VLM Adaptation & Single-Image Capabilities
* **FR-3.1**: Support remote-sensing visual question answering for overhead perspectives, fine-grained objects, and land-use categories.
* **FR-3.2**: Provide at least one dedicated single-image grounding / localization capability outputting spatial coordinates ($[x_{min}, y_{min}, x_{max}, y_{max}]$ or segmentation polygon).
* **FR-3.3**: Support domain-specific prompts encoding nadir viewing geometry, ground sampling distance (GSD), and scale invariance.

### FR-4: Bi-Temporal & Multi-Sensor Understanding
* **FR-4.1**: Compute change features between registered $T_1$ and $T_2$ images to isolate newly appeared, modified, or vanished features.
* **FR-4.2**: Extract complementary signals from SAR inputs (polarization intensity, backscatter contrast) to validate optical observations or compensate for cloud/illumination deficits.
* **FR-4.3**: Produce paired descriptive change reports detailing the qualitative and quantitative nature of observed shifts.

### FR-5: Visual Evidence & Explanations
* **FR-5.1**: For every analytical assertion where spatial localization is relevant, the system must render visual evidence (color-coded bounding boxes, difference overlays, or attention heatmaps).
* **FR-5.2**: The system must maintain pixel-level coordinate alignment between the input image and the generated visual overlays.
* **FR-5.3**: Users must be able to toggle individual evidence layers on and off over the base image.

### FR-6: Confidence Information & Observable Trace
* **FR-6.1**: The system must calculate and display an explicit confidence metric for model outputs (e.g., detection score, linguistic certainty score).
* **FR-6.2**: The system must provide an observable execution trace documenting:
  - Query interpretation & selected sub-tasks.
  - Model / tool selected and execution parameters.
  - Processing latencies per pipeline step.
  - Warnings, fallback triggers, or data anomalies encountered.

---

## 9. Non-Functional Requirements

### NFR-1: Performance & Latency
* Interactive inference response target: $\le 5$ seconds for single-image VQA/grounding queries (on standard GPU inference hardware).
* Multi-image / Bi-temporal / Optical-SAR pipeline target: $\le 10$ seconds per analysis.

### NFR-2: Reliability & Error Handling
* 100% graceful handling of out-of-distribution queries, malformed images, and unsupported format requests without unhandled system crashes.
* Clear explanatory messages when confidence is too low to produce a definitive answer (preventing silent hallucinations).

### NFR-3: Usability & Interpretability
* UI must clearly delineate natural language commentary from strict visual evidence.
* Execution trace must be collapsible for casual users and expandable for evaluators/auditors.

### NFR-4: Modularity & Extensibility
* Decoupled architecture allowing vision encoders, VLM backbones, and grounding heads to be swapped or upgraded without refactoring the orchestration layer.

---

## 10. AI Requirements
* **Domain Adaptation**: Adaptation strategies (fine-tuning, LoRA adapters, domain prompt templates, or specialized RS visual backbones) suited to overhead nadir imagery.
* **Scale & Resolution Sensitivity**: Ability to handle varying Ground Sample Distances (GSD) without losing small-object signatures (e.g., small vehicles, shipping containers).
* **Cross-Modal Grounding**: Linking textual queries directly to 2D image coordinates.
* **Hallucination Suppression**: Rejection or disclaimer when a requested object or condition is not discernible due to resolution or sensor limitations.
* **Confidence Calibration**: Outputting normalized confidence intervals ($0.0 - 1.0$ or percentage) rather than uncalibrated raw softmax scores.

---

## 11. Data Requirements
* **Supported Sensor Modalities**:
  - Optical RGB / Multispectral imagery (simulated or real from Sentinel-2, Landsat-8/9, PlanetScope, aerial orthophotos).
  - Synthetic Aperture Radar (SAR) imagery (Sentinel-1 GRD, VV/VH polarizations).
* **Temporal Datasets**: Registered pairs ($T_1, T_2$) across seasonal changes, urban expansion, and disaster scenarios.
* **Sample / Benchmark Imagery**: Curated demonstration datasets for SIH evaluation representing real Indian and global geography (ports, agricultural basins, flooded rivers, urban periphery).
* **Data Privacy & Licensing**: Compliance with open-access government and satellite data licenses (Copernicus Open Access Hub, USGS, OpenAerialMap).

---

## 12. Feature Priorities (MoSCoW Framework)

| Priority | Feature | Description |
| :--- | :--- | :--- |
| **Must Have** | Single-image RS VQA | Natural language QA on satellite/aerial imagery |
| **Must Have** | Single-image Visual Grounding | Target localization with bounding boxes |
| **Must Have** | Bi-temporal Change Understanding | Comparing $T_1$ vs. $T_2$ images with visual difference evidence |
| **Must Have** | Optical-SAR Paired Analysis | Joint multi-sensor analysis exploiting SAR penetration/roughness |
| **Must Have** | Agentic Task/Model Selection | Autonomous query routing and pipeline construction |
| **Must Have** | Input Validation & Diagnostics | Pre-inference dimension, modality, and format verification |
| **Must Have** | Visual Evidence Generation | Overlays, bounding boxes, and highlight masks on source images |
| **Must Have** | Confidence Information | Normalized certainty score accompanying answers |
| **Must Have** | Observable Execution Trace | Step-by-step pipeline view for evaluator transparency |
| **Should Have** | Interactive Evidence Layer Toggle | Turning visual overlays on/off in UI |
| **Should Have** | Multi-Turn Context Follow-Up | Asking follow-up queries on previously uploaded scenes |
| **Could Have** | GeoTIFF CRS/Coordinate Extraction | Displaying real-world latitude/longitude alongside pixel coordinates |
| **Could Have** | PDF / Analytical Report Export | Downloading a summary brief with visual evidence for field teams |
| **Won't Have (MVP)** | Full GIS Raster Pipeline | Large-scale tile servers, petabyte raster streaming |
| **Won't Have (MVP)** | Real-time Satellite Constellation Ingestion | Live orbit satellite direct-downlink streaming |

---

## 13. MVP Scope
The SatQuery AI Minimum Viable Product (MVP) delivers a unified, runnable system containing:
1. **Core AI Pipelines**:
   - Single-Image VQA engine adapted for remote sensing.
   - Single-Image Visual Grounding tool (bounding box prediction for target objects).
   - Bi-Temporal Change Detection engine generating differential change descriptions and highlight masks.
   - Optical-SAR paired analysis module addressing cross-modal queries.
2. **Orchestration Layer**:
   - Agentic router that evaluates user query intent and attached assets to trigger the appropriate tool chain.
   - Guardrails and input validators for image integrity and format checks.
3. **Observability & Evidence Module**:
   - Visual evidence renderer (bounding boxes, change masks).
   - Confidence scoring estimator.
   - Transparent step-by-step execution trace log.
4. **Demonstration Scenarios**: Pre-validated datasets covering each of the core use cases to ensure reliable demonstration during hackathon judging.

---

## 14. Out of Scope (For Hackathon MVP)
* Production-scale distributed raster storage and multi-terabyte tile management (e.g., custom PostGIS/GeoServer cluster).
* Direct tasking or live real-time API integrations with active commercial satellite constellations.
* Training massive multi-billion parameter foundation models from scratch (pre-trained base weights with domain adaptation/adapters will be utilized).
* User management, role-based access control, and enterprise billing/metering systems.

---

## 15. Success Metrics
* **Routing Accuracy**: $\ge 95\%$ correct automated task dispatch on benchmark queries across the 4 core modalities.
* **Grounded Answer Rate**: $100\%$ of localization and change queries accompanied by valid visual bounding boxes or masks.
* **Latency Profile**: Single-image pipeline execution $\le 5$s; multi-image execution $\le 10$s on standard benchmark evaluation environments.
* **Hallucination Suppression**: System declines to answer or flags low confidence ($< 0.4$) on ambiguous, out-of-resolution, or non-visible features.
* **Evaluator Usability Score**: Positive assessment from hackathon jury on reasoning transparency and visual evidence clarity.

---

## 16. Acceptance Criteria
1. **AC-1 (Single-Image VQA)**: When given a valid satellite image and an analytical query, the system answers accurately in natural language with a confidence score.
2. **AC-2 (Single-Image Grounding)**: When asked to locate specific objects (e.g., "Find all storage tanks"), the system returns bounding box coordinates displayed visually on the image.
3. **AC-3 (Bi-Temporal Change)**: When provided with registered $T_1$ and $T_2$ images, the system detects differences, provides a descriptive change report, and highlights changed zones.
4. **AC-4 (Optical-SAR Pairing)**: When given paired Optical and SAR scenes, the system performs cross-sensor reasoning (e.g., assessing structures obscured by optical clouds).
5. **AC-5 (Agentic Routing)**: The system dynamically selects models/tools without requiring the user to manually configure the backend pipeline.
6. **AC-6 (Input Validation)**: Mismatched dimensions, single-image inputs submitted for bi-temporal queries, or corrupt files produce explicit, helpful error responses.
7. **AC-7 (Observable Trace)**: Every query execution displays an expandable execution trace showing query classification, tool invocation, processing time, and confidence.

---

## 17. Evaluator Perspective (Smart India Hackathon Focus)
Hackathon evaluators will judge SatQuery AI on:
* **Technical Innovation & Depth**: Meaningful remote-sensing adaptation and cross-modality (Optical + SAR) rather than a trivial wrapper around generic vision APIs.
* **Real-World Feasibility**: Practical utility for disaster management, national infrastructure monitoring, and environmental governance in India.
* **Explainability & Trust**: Verifiable bounding boxes, change maps, and visible reasoning traces that allow human-in-the-loop verification.
* **Architectural Cleanliness**: Clear separation of concerns between input validation, agentic routing, specialized model pipelines, and presentation layers.
* **Robustness During Live Demos**: Deterministic fallback mechanisms, swift inference, and resilient handling of unexpected user inputs.

---

## 18. Risks and Constraints

| Risk / Constraint | Severity | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Compute / GPU Limitations during Hackathon** | High | Slow inference or OOM on large rasters | Use quantized models, pre-tiled patches, and efficient inference backbones. |
| **Optical-SAR Misalignment** | Medium | Inaccurate cross-modal reasoning | Require pre-registered image pairs or include standard registration checks. |
| **Resolution Mismatch (Low GSD vs. Fine Object Queries)** | High | Hallucinated detections of invisible objects | Implement input resolution checks; reject queries asking for objects smaller than the sensor GSD. |
| **Model Hallucination in Complex Scenes** | High | False intelligence delivered to decision-makers | Enforce confidence thresholding; visual evidence must align with textual claims. |
| **Demo Day Network / API Latency** | Medium | Demo failure or unacceptable wait times | Package self-contained local fallback datasets and pre-cached demonstration scenarios. |
