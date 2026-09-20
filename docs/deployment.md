# Deployment & Infrastructure Plan — SatQuery AI

## 1. Document Overview
This document specifies the deployment architecture, runtime environments, hardware prerequisites, containerization, and demonstration-day operational procedures for **SatQuery AI**.

---

## 2. Target Deployment Environments

### 2.1 Local Demonstration Setup (Primary for Hackathon)
* **Target OS**: Windows 11 / Linux (Ubuntu 22.04 LTS).
* **Hardware Profile**: Minimum 16 GB System RAM, NVIDIA GPU with $\ge 8$ GB VRAM (CUDA-enabled) recommended for local model acceleration, and $\ge 25$ GB free disk storage (~12 GB active footprint + 13 GB operational buffer for weights, caching, and tensor scratchpads).
* **CPU-Only Fallback**: Quantized execution mode enabled if discrete GPU is not present.
* **Purpose**: Self-contained local demonstration without external internet or third-party API dependencies.

### 2.2 Cloud / Staging Environment (Secondary)
* Containerized service deployment (Docker / Docker Compose).
* GPU-accelerated cloud instance (e.g., T4/A10G or similar).
* Scalable object storage for raster assets if deployed as a public endpoint.

---

## 3. Deployment Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│   (Web UI: Uploads, Bounding Boxes, Traces, Change Viewer)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / WebSocket
┌──────────────────────────────▼──────────────────────────────┐
│                    SatQuery Backend Gateway                  │
│   (Input Validation, Asset Manager, Agentic Task Router)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Model Execution Services                   │
│  - Remote-Sensing VLM Pipeline                              │
│  - Object Grounding Head                                     │
│  - Bi-Temporal Difference Engine                            │
│  - Optical-SAR Multi-Modal Fusion Engine                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      Local Storage                          │
│  - Cached Model Weights (`models/`)                         │
│  - Ingested Raster Assets (`storage/uploads/`)               │
│  - Generated Evidence Masks (`storage/evidence/`)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Dependencies & Prerequisites (Planned)
* **Python Runtime**: Python 3.10+ (to be confirmed).
* **Deep Learning Runtime**: PyTorch with CUDA support (or ONNX Runtime for CPU/accelerated inference).
* **Geospatial & Vision Libraries**: OpenCV, Pillow, Rasterio/GDAL (as needed for GeoTIFF handling).
* **Frontend**: Lightweight modern web client with high-aesthetic visual evidence rendering.

---

## 5. Demonstration Day Fail-Safe & Reliability Plan
* **Local Offline Bundle**: Pre-cache all required model checkpoints and demonstration satellite scenes to guarantee operation in low/no connectivity hackathon venues.
* **Pre-Baked Showcase Scenarios**: Pre-validated assets representing each core capability (single VQA, grounding, bi-temporal, optical-SAR) ready for instant, deterministic demonstration.
* **Graceful Degradation**: Fallback to CPU-optimized quantized models if GPU VRAM limits are approached.

---

## 6. Open Decisions (To Be Finalized)
* Containerization tooling (Docker Compose vs. direct Python virtual environment for hackathon judging simplicity).
* Cloud hosting provider if remote access is required by evaluators.
