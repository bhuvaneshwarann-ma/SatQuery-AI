# Database & Storage Specification — SatQuery AI

## 1. Document Overview
This document specifies the data storage requirements, metadata models, caching strategies, and persistence architecture for **SatQuery AI**.

---

## 2. Storage Principles & Requirements
* **Lightweight Footprint**: For the hackathon MVP, data persistence must be simple to deploy, reliable, and require minimal operational overhead.
* **Asset & Metadata Separation**: Raw raster and image files are stored in object/file storage, while structured metadata, query logs, and traces are maintained in relational or document stores.
* **Auditability & Traceability**: Every analytical query, router decision, generated visual evidence, and confidence score must be persistable for evaluator review.

---

## 3. Conceptual Entities & Data Models

### 3.1 Image Asset (`assets`)
* `asset_id`: Unique identifier (UUID).
* `file_path`: Path / URI to stored image on disk.
* `modality`: Enum (`OPTICAL_RGB`, `OPTICAL_MULTISPECTRAL`, `SAR_GRD`).
* `dimensions`: Image height, width, and number of channels.
* `spatial_metadata`: Ground Sampling Distance (GSD), projection info, or timestamp if available.
* `created_at`: Ingestion timestamp.

### 3.2 Analytical Session (`sessions`)
* `session_id`: Unique identifier (UUID).
* `user_or_evaluator_tag`: Identifier for demo or session context.
* `active_asset_ids`: Array of asset IDs bound to the current session (single, bi-temporal, or paired).
* `created_at`: Creation timestamp.

### 3.3 Query & Execution Trace Record (`query_records`)
* `query_id`: Unique identifier (UUID).
* `session_id`: Foreign key reference to session.
* `prompt_text`: Raw user query string.
* `detected_intent`: Classified task category (VQA, Grounding, Change, Optical-SAR).
* `selected_pipeline`: Name of the routed model pipeline.
* `answer_text`: Generated natural language response.
* `confidence_score`: Normalized numerical score ($0.0 - 1.0$).
* `execution_trace`: JSON-structured log of intermediate routing and execution stages.
* `latency_ms`: Total execution time in milliseconds.
* `created_at`: Execution timestamp.

### 3.4 Visual Evidence Record (`visual_evidence`)
* `evidence_id`: Unique identifier (UUID).
* `query_id`: Foreign key reference to query record.
* `evidence_type`: Enum (`BOUNDING_BOX`, `CHANGE_MASK`, `HEATMAP`, `SEGMENTATION`).
* `data_payload`: Bounding box coordinates $[x_{min}, y_{min}, x_{max}, y_{max}]$ or URI to generated overlay raster/mask.
* `confidence`: Confidence score associated with specific visual feature.

---

## 4. Storage Architecture
* **File Storage**: Local directory (`storage/uploads/` and `storage/evidence/`) holding ingested images and rendered overlay artifacts.
* **Metadata Store**: Lightweight embedded or relational database (e.g., SQLite for MVP local execution, or PostgreSQL if multi-user persistence is configured).
* **In-Memory Cache**: Volatile caching for fast access to recent session states and pre-computed embeddings.

---

## 5. Open Technical Decisions (To Be Finalized)
* Embedded database (SQLite) vs. client-server database (PostgreSQL) for hackathon demo portability.
* Retention policies for uploaded raster imagery and temporary visual evidence masks.
