# SatQuery AI — Curated Demo Asset Manifest (Phase 9)

**Document Purpose**: Definitive registry of verified sample assets curated for live evaluator demonstrations, including modality, scientific provenance, expected demo queries, generated spatial artifacts, and explicit limitations.

---

## Curated Demo Assets Registry

| Asset File | Modality | Purpose & Journey | Expected Demo Query | Provenance & Classification | Associated Evidence Artifact | Documented Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`sample_satellite_port.jpg`**<br>(63,292 bytes, $512 \times 512$ px) | Optical RGB (Visible Spectrum) | **Demo A (VQA)**<br>**Demo B (Grounding)**<br>Baseline for Demo C & D | • *"What type of maritime port or facility is shown in this satellite image?"*<br>• *"Locate the ships in this satellite image."* | **Public Optical Satellite Imagery**<br>(Commercial high-resolution harbor/coastline acquisition) | • [`grounding_execution_artifact.jpg`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/grounding_execution_artifact.jpg)<br>• `vqa_spatial_metadata` | Single static optical capture; lack of multi-spectral bands limits atmospheric haze correction. |
| **`sample_satellite_port_t2_synthetic.jpg`**<br>(120,756 bytes, $512 \times 512$ px) | Optical RGB (Perturbed Temporal) | **Demo C (Bi-Temporal Change Detection)** (Timestamp T2) | *"Identify differences and what changed between these two images"* | **Controlled Synthetic Temporal Pair**<br>(Controlled spatial modifications simulating vessel departures and dock alterations) | [`change_detection_execution_artifact.jpg`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/change_detection_execution_artifact.jpg)<br>(3-Panel composite: T1, T2, and differential heatmap) | Controlled synthetic temporal pair used for integration verification; does not measure real-world multi-year building change detection accuracy. |
| **`sample_sentinel1_sar_mauritius.jpg`**<br>(168,735 bytes, $512 \times 512$ px) | Microwave SAR (Synthetic Aperture Radar) | **Demo D (Optical + SAR Multi-Sensor Fusion)** (SAR Channel) | *"Analyze optical and SAR radar cross-modal backscatter imagery"* | **Synthetic Radar Backscatter Proxy (`proxy_sar`)**<br>(Simulates radar backscatter, dielectric corner reflection from metal vessels, and sea clutter) | [`optical_sar_execution_artifact.jpg`](file:///c:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/docs/results/optical_sar_execution_artifact.jpg)<br>(3-Panel composite: Optical, SAR backscatter, Radiometric synergy overlay) | Proxy SAR data; authentic ISRO/SAC Cartosat-2S and RISAT-1A co-registered spaceborne SAR pairs remain restricted under institutional data licensing. |
| **`sample_satellite_port_proxy_sar.png`**<br>(326,484 bytes, $512 \times 512$ px) | Synthetic Microwave SAR Intensity | **Demo D Alternative** (High-dynamic-range proxy SAR) | *"Perform dual-sensor radiometric fusion on optical and radar imagery"* | **Synthetic Radar Backscatter Proxy (`proxy_sar`)**<br>(Derived via physically modeled corner reflection simulation) | `optical_sar_execution_artifact.jpg` | Synthetic proxy; must never be represented as authentic spaceborne radar data. |

---

## Demo Presets Configuration

The React frontend UI (`frontend/src/components/AnalysisForm.tsx`) incorporates one-click quick presets referencing these assets directly from `/samples/`:

1. **Preset A (Single-Image VQA)**:
   - Primary: `sample_satellite_port.jpg`
   - Task: `VQA`
   - Query: *"What type of maritime port or facility is shown in this satellite image?"*
   - Expected Output: Natural language explanation of harbor, coastline, and maritime facilities via `remote-sensing-Qwen2.5-VL-3B-Instruct`.
2. **Preset B (Visual Grounding)**:
   - Primary: `sample_satellite_port.jpg`
   - Task: `GROUNDING`
   - Query: *"Locate the ships in this satellite image."*
   - Expected Output: Bounding box detection on vessel coordinates `[209.8, 2.15, 701.95, 432.29]` with uncalibrated detector score $\approx 0.3732$.
3. **Preset C (Bi-Temporal Change Detection)**:
   - Primary (T1): `sample_satellite_port.jpg`
   - Secondary (T2): `sample_satellite_port_t2_synthetic.jpg`
   - Task: `CHANGE_DETECTION`
   - Query: *"Identify differences and what changed between these two images"*
   - Expected Output: 8,848 changed pixels ($2.56\%$), area stability margin $97.4\%$, and 3-panel differential heatmap.
4. **Preset D (Optical + SAR Cross-Modal Fusion)**:
   - Primary (Optical): `sample_satellite_port.jpg`
   - SAR Channel: `sample_sentinel1_sar_mauritius.jpg`
   - Task: `OPTICAL_SAR`
   - Query: *"Analyze optical and SAR radar cross-modal backscatter imagery"*
   - Expected Output: Pearson $r = 0.574$, 28,276 radar-dominant anomalies, and 3-panel false-color synergy composite.
5. **Preset E (Safety & Parameter Firewall Test)**:
   - Primary: `sample_satellite_port.jpg`
   - Task: `AUTO`
   - Query: *"calculate orbital trajectory"*
   - Expected Output: Pre-model clarification prompt (`NEEDS_CLARIFICATION`) in $<25\text{ ms}$ without invoking heavy models or crashing GPU.
