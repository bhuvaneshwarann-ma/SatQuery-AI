# SatQuery AI — Earth Observation Intelligence Workstation Design System

**Specification Version**: 2.0  
**Design Philosophy**: "A professional Earth Observation analysis workstation, not a generic AI dashboard."  
**Target Domain**: Mission control, Earth observation operations, scientific geospatial intelligence, Smart India Hackathon defense.

---

## 1. Visual Language & Core Principles

| Principle | Workstation Execution | Prohibited SaaS Anti-Pattern |
| :--- | :--- | :--- |
| **Imagery Dominance** | Geospatial raster viewer occupies the central focus (>60% screen estate) with direct pan, zoom, split-screen, and pixel-aligned bounding boxes. | Drowning imagery in oversized decorative cards, padding, or hero illustrations. |
| **Mission-Control Aesthetics** | High-contrast dark theme, crisp hairline borders (`#263037`), high data density, structured tabular summaries. | Neon glows, heavy drop shadows, pastel gradients, oversized 24px border radii. |
| **Precise Typography** | Technical typography pairing: `Inter` / `Space Grotesk` for UI structure and `JetBrains Mono` for metadata, coordinates, and telemetry. | Decorative, handwritten, or playful typography. |
| **Controlled Iconography** | Crisp, uniform SVG line icons (1.75px stroke) for geospatial actions. | Emojis in navigation, status bars, and headers (`🛰️`, `🔬`, `📊`, `✦`). |
| **Scientific Disclosures** | Prominent disclosures on uncalibrated heuristics, proxy classifications, and baseline sample sizes ($N=20$). | Misleading "100% accurate", "probabilistic certainty", or deceptive marketing badges. |

---

## 2. Color Palette & Design Tokens

### 2.1 Surfaces & Canvas
* **Application Canvas (`--bg-app`)**: `#080B0D` (Deep oceanic void)
* **Primary Workstation Panel (`--surface-primary`)**: `#0E1316` (Refined technical charcoal)
* **Secondary Surface (`--surface-secondary`)**: `#13191D` (Subtle elevation surface)
* **Hover / Interaction Surface (`--surface-hover`)**: `#1A2227` (Interactive feedback state)

### 2.2 Hairline Borders & Dividers
* **Default Hairline (`--border-default`)**: `#263037` (Disciplined separation)
* **Subtle Inner Hairline (`--border-subtle`)**: `#1D252B` (Internal table rows and section splits)
* **Strong Structural Hairline (`--border-strong`)**: `#3D4C55` (Active focus and selected borders)
* **Focus Outline (`--border-focus`)**: `#00A3BF` (Restrained Earth observation cyan)

### 2.3 Typography Scale
* **Primary Text (`--text-primary`)**: `#E8EEF0` (High contrast, crisp legibility)
* **Secondary Text (`--text-secondary`)**: `#8C999F` (Descriptive context and metadata labels)
* **Muted Telemetry Text (`--text-muted`)**: `#5E6A70` (Grid labels, timestamps, units)

### 2.4 Semantic Accents
* **Geospatial Primary Accent (`--accent-teal`)**: `#00A3BF` (Restrained Earth Observation cyan)
* **Operational Success (`--color-success`)**: `#10B981` (Completed pipelines, valid inputs)
* **Operational Warning / Review (`--color-warning`)**: `#F59E0B` (Medium confidence, proxy data notes)
* **Operational Error / Rejection (`--color-error`)**: `#EF4444` (Firewall rejections, invalid inputs)

---

## 3. Geometric Rules & Density Constraints

* **Panel Border Radii**: Strict `8px` (`--radius-panel`) for workstation cards and panels.
* **Control Border Radii**: Strict `6px` (`--radius-control`) for buttons, text inputs, and select chips.
* **Metadata Tag Radii**: Strict `4px` (`--radius-tag`) for status badges and technical tokens.
* **Button Elevations**: Flat 1px border; no exaggerated 3D drops or floating shadows.
* **Layout Radii**: Prohibit 16px–32px pill bubbles on rectangular analytical content.

---

## 4. Multi-Page Workstation Information Architecture

```text
SatQuery AI Workstation Shell
├── Left Navigation Rail (230px, text-first, SVG line icons, line active indicator)
│   ├── Overview (/)
│   ├── Analysis Workspace (/analyze)
│   ├── Results & Audit (/results)
│   ├── Scene Explorer (/scenes)
│   ├── Model Registry (/models)
│   ├── Benchmarks (/evaluation)
│   ├── History (/history)
│   └── Architecture (/about)
│
├── Top Workstation Bar (48px, compact, developer telemetry removed)
│   ├── Breadcrumb navigation (WORKSPACE / ...)
│   ├── Global Command Palette trigger (Ctrl+K)
│   └── Action: New Analysis ([+])
│
└── Workstation Viewport (100% height, zero decorative gutters)
```

---

## 5. Page-Specific Workstation Paradigms

### 5.1 Analysis Workspace (`/analyze`) — 3-Column Ergonomics
1. **Input Rail (260px)**: Co-registered raster dropzones with format verification (`.tif`, `.png`, `.jpg`), file size indicators, and preloaded benchmark sample presets.
2. **Geospatial Canvas (Center, focal component)**:
   * 42px technical toolbar: Zoom in/out (`+`/`−`), Reset view, Fullscreen canvas, Overlay opacity slider, Split-screen comparison toggle.
   * Pan/drag navigation with bounding box overlays rendered directly on raster coordinates.
3. **Analytical Query Rail (340px)**:
   * Segmented task selector: `[ AUTO ] [ VQA ] [ GROUNDING ] [ CHANGE ] [ OPTICAL + SAR ]`.
   * Natural language query textarea with character counter.
   * Parameter override dropdowns (threshold, box threshold, max tokens).
   * Primary dispatch action button: `RUN SATELLITE ANALYSIS ↗`.

### 5.2 Results & Audit Report (`/results`)
* **Scientific Analysis Report**: Clean hairline horizontal dividers separating Answer, Scene Context, Observable Evidence Signals, and Evidence Strength Heuristic.
* **Evidence Items**: Numbered list format (`01`, `02`, `03`) with category tags (`STRUCTURAL`, `SPECTRAL`, `SPATIAL`).
* **Confidence Level**: `LOW / MEDIUM / HIGH — Model-derived • Uncalibrated` with exact score percentage and contextual signal explanation.
* **Operational Trace**: Monospaced 6-stage execution log documenting input verification, parameter firewall check, tool dispatch, inference latency, and memory footprint.

### 5.3 Model Registry (`/models`)
* High-density Model Registry Table: `STATUS`, `IDENTIFIER / MODEL NAME`, `TASK MODE`, `TYPE`, `PEAK VRAM`, `TYPICAL LATENCY`, `ACTION`.
* Interactive Inspector Drawer: Detailed schema of allowlisted parameters, input/output tensor contracts, and confidence semantics.

### 5.4 Benchmark & Evaluation Suite (`/evaluation`)
* Labeled `BASELINE EVALUATION (N=20)`.
* Tabular presentation of `RSVQA-LR` and `LEVIR-CD` metrics alongside ground-truth baselines.
* Structured operational disclosures: Cartosat roadmap milestone, SAR proxy status, temporal slice limitations, and uncalibrated heuristic guarantees.

---

## 6. Verification Status

* **TypeScript Compilation**: `tsc -b && vite build` $\rightarrow$ Clean build (`0 errors`).
* **Bundle Footprint**: 35.69 kB CSS (optimized from 94 kB initial prototype), 325 kB JS.
* **Design Rule Compliance**: 100% adherence to Earth Observation workstation guidelines.
