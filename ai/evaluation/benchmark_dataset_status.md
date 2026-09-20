# SatQuery AI — Benchmark Dataset Status (Phase 8C)

This document records the availability, characteristics, and operational fit of candidate remote-sensing benchmark datasets evaluated for SatQuery AI.

---

## 1. Local Availability & Pipeline Readiness Matrix

| Dataset | Local? | Task | Modality | Labels | Size | Download Needed? | Fits Current Pipeline? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSVQA** (LR & HR) | **No** | Visual Question Answering (VQA) | Optical RGB (Sentinel-2 10m & Aerial 0.15m) | Question-Answer pairs (presence, count, area, comparison) | ~1.5 GB (LR) / ~12 GB (HR) | Yes (Mini-subset of 20–50 QA pairs recommended) | **Yes (Direct fit for VQA)**: Ingests single optical raster + question text → text answer. |
| **VRSBench** | **No** | Dual-Task: VQA & Visual Grounding | High-Res Optical (Google Earth / aerial, sub-meter) | QA text pairs + Referring Expression bounding boxes $[x_1, y_1, x_2, y_2]$ | ~15 GB (Full) / ~80 MB (Mini subset) | Yes (Mini-subset of 20–50 samples recommended) | **Yes (Direct fit for VQA & GROUNDING)**: Directly supports Grounding DINO box evaluation and VLM question answering. |
| **CDVQA** | **No** | Change Detection VQA | Bi-Temporal Optical Pairs (T1, T2) | Questions about temporal deltas + change descriptions + change masks | ~6 GB (Full) | Yes (Mini-subset recommended for Phase 9) | **Yes (Direct fit for CHANGE_DETECTION & VQA)**: Bridges bi-temporal feature extraction with natural-language change reasoning. |
| **LEVIR-CD / WHU-CD** | **No** | Bi-Temporal Change Detection | Multi-temporal Optical Satellite / Aerial | Pixel-level binary change masks (changed vs. unchanged) | ~850 MB (LEVIR-CD mini) / ~1.2 GB | Yes (Subset of 20–50 pairs needed for F1/IoU) | **Yes (Direct fit for CHANGE_DETECTION)**: Siamese ResNet18 can directly output predicted change mask to compare with ground-truth mask. |
| **BigEarthNet-MM** (v2.0) | **No** | Multi-Label Scene Classification & Cross-Modal Pretraining | Paired Sentinel-2 (12 bands) + Sentinel-1 (VV/VH SAR) | Multi-label CORINE Land Cover (CLC) categories (19/43 classes) | ~120 GB (Full) / ~1.2 GB (1K patch subset) | **No** (Full download strictly prohibited; mini-patch optional) | **Partial fit for OPTICAL_SAR**: Provides genuine paired Sentinel-1/Sentinel-2 rasters for correlation, but lacks natural language QA and bounding boxes. |
| **SEN1-2** | **No** | Optical-SAR Data Fusion & Cross-Modal Translation | Paired Sentinel-1 SAR (VV) + Sentinel-2 Optical (RGB) | Co-registered spatial image pairs (4 seasons, 282,384 pairs) | ~35 GB (Full) / ~150 MB (Mini-split) | Yes (Mini-subset of 20–50 pairs recommended for genuine SAR) | **Yes (Direct fit for OPTICAL_SAR)**: Genuine spaceborne Sentinel-1/2 co-registered pairs to replace proxy SAR. |
| **ISRO/SAC Cartosat-2S + RISAT SAR** | **No** | Dual-Sensor High-Res Surveillance | Cartosat-2S Pan/MS (0.65m) + RISAT-1A / EOS-04 C-band SAR | Level-1/2 geocoded rasters (no pre-packaged task labels) | ~2–10 GB per raw scene | Requires ISRO Bhoonidhi portal credentials | **Requires preprocessing**: Full scenes must be orthorectified, co-registered, and chipped to $512 \times 512$ patches before inference. |

---

## 2. Official Access & Download Path Discovery

| Dataset | Official Source / Repository | Access Requirements | Recommended Ingestion Strategy |
| :--- | :--- | :--- | :--- |
| **RSVQA** | Sylvain Lobry / Univ. of Geneva (Zenodo / HuggingFace: `RSVQA`) | Open Access (Creative Commons) | Fetch a lightweight validated 25-sample test slice via HuggingFace Hub streaming (zero large tarball download). |
| **VRSBench** | Lingxuan Meng et al. / CVPR 2024 (`VRSBench` HuggingFace/GitHub) | Open Access (Academic License) | Download a deterministic mini-split of 20 image-question-box pairs (~25 MB total) for dual VQA and Grounding evaluation. |
| **LEVIR-CD** | Beihang University (LEVIR-CD via IEEE / GitHub) | Open Access | Download 25 co-registered pre/post flood/construction pairs with ground-truth binary PNG masks (~30 MB). |
| **SEN1-2** | TU Munich (Prof. Xiao Xiang Zhu, IEEE Dataport / MediaTUM) | Open Access (Registration required for full bulk) | Download a 20-pair co-registered patch sample (Spring/Summer urban & port scenes) (~15 MB). |
| **ISRO Cartosat + RISAT** | ISRO Bhoonidhi Data Portal (`bhoonidhi.nrsc.gov.in`) | Free user registration with manual CAPTCHA / OTP | Manual procurement only; do not automate download in automated CI/CD pipelines. |

---

## 3. Storage & Bandwidth Impact Summary

* **Bulk Download Policy**: Downloading full benchmark corpuses (BigEarthNet 120 GB, RSVQA 14 GB, VRSBench 15 GB, SEN1-2 35 GB) is **strictly prohibited** in this local development environment.
* **Prescribed Approach**: Standardized **mini-evaluation splits** of 20–50 samples per task (~100 MB total across all 4 capabilities) will provide 100% reproducible statistical benchmark validation while preserving storage and GPU evaluation feasibility.
