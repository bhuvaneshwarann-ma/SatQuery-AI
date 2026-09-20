# API Specification — SatQuery AI

## 1. Document Overview
This document specifies the RESTful application programming interface (API) contracts for **SatQuery AI**, covering asset ingestion, agentic query submission, evidence retrieval, and execution trace inspection.

---

## 2. API Design Principles
* **Predictable REST Conventions**: Standard HTTP verbs and status codes (`200 OK`, `400 Bad Request`, `422 Unprocessable Entity`, `500 Internal Error`).
* **Observable Response Payloads**: Analytical responses return answers, visual evidence, confidence metrics, and execution traces in a structured JSON envelope.
* **Strict Input Validation**: Image dimensions, missing modality tags, and temporal pairing errors return clear diagnostic codes.

---

## 3. Endpoints

### 3.1 Health & Service Status
* **`GET /api/v1/health`**
  - **Purpose**: Verify backend service and model readiness.
  - **Response (200 OK)**:
    ```json
    {
      "status": "healthy",
      "models_ready": true,
      "version": "1.0.0"
    }
    ```

### 3.2 Asset Ingestion
* **`POST /api/v1/assets/upload`**
  - **Purpose**: Upload and validate single or paired imagery.
  - **Content-Type**: `multipart/form-data`
  - **Form Fields**:
    - `file`: Binary image file (GeoTIFF, PNG, JPEG).
    - `modality`: Optional string (`optical`, `sar`).
    - `timestamp`: Optional ISO-8601 string (for bi-temporal sequences).
  - **Response (201 Created)**:
    ```json
    {
      "asset_id": "ast_98432a10",
      "filename": "mumbai_port_2024.png",
      "dimensions": {"width": 1024, "height": 1024, "channels": 3},
      "modality": "optical",
      "status": "validated"
    }
    ```

### 3.3 Query Execution (Agentic Dispatch)
* **`POST /api/v1/query`**
  - **Purpose**: Submit an analytical natural language query against one or more assets.
  - **Content-Type**: `application/json`
  - **Request Body**:
    ```json
    {
      "query": "Locate all cargo vessels docked at the pier.",
      "asset_ids": ["ast_98432a10"],
      "session_id": "ses_01"
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "query_id": "qry_8831b",
      "answer": "Identified 4 cargo vessels berthed along the eastern pier.",
      "confidence": 0.92,
      "detected_intent": "visual_grounding",
      "selected_pipeline": "rs_object_grounding",
      "visual_evidence": [
        {
          "type": "bounding_box",
          "label": "cargo_vessel",
          "box_2d": [120, 340, 260, 480],
          "confidence": 0.94
        }
      ],
      "execution_trace": [
        {"step": "input_validation", "status": "passed", "latency_ms": 12},
        {"step": "intent_classification", "intent": "visual_grounding", "latency_ms": 45},
        {"step": "model_inference", "model": "rs_grounding_head", "latency_ms": 320},
        {"step": "evidence_assembly", "status": "completed", "latency_ms": 18}
      ],
      "total_latency_ms": 395
    }
    ```

### 3.4 Bi-Temporal & Optical-SAR Analysis
* **`POST /api/v1/query/paired`**
  - **Purpose**: Execute bi-temporal change detection or optical-SAR fusion queries.
  - **Content-Type**: `application/json`
  - **Request Body**:
    ```json
    {
      "query": "Identify new construction between T1 and T2.",
      "primary_asset_id": "ast_t1_2023",
      "secondary_asset_id": "ast_t2_2024",
      "analysis_type": "bi_temporal_change"
    }
    ```

### 3.5 Trace & Audit Log Retrieval
* **`GET /api/v1/traces/{query_id}`**
  - **Purpose**: Inspect the granular reasoning and execution log for a past query.

---

## 4. Error Responses & Diagnostic Schema
When validation fails or an unrecoverable error occurs, the API returns a structured error object:
```json
{
  "error": {
    "code": "INVALID_IMAGE_PAIR",
    "message": "Bi-temporal analysis requires exactly two registered assets.",
    "details": {
      "provided_asset_count": 1,
      "required_asset_count": 2
    }
  }
}
```

---

## 5. Open Technical Decisions (To Be Finalized)
* Choice of backend web framework (e.g., FastAPI vs. Flask / Node.js).
* Streaming / Server-Sent Events (SSE) support for real-time progress updates on long-running multi-image tasks.
