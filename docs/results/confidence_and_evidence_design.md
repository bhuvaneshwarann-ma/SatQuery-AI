# SatQuery AI: Evidence Strength Heuristic & Visual Evidence Design

## 1. Executive Summary & Core Paradigm

SatQuery AI provides an **Evidence Strength Heuristic** layer designed to replace opaque or missing confidence indicators (`Confidence: Unavailable / Null`) with scientifically defensible, verifiable assessments of evidence grounding.

> [!IMPORTANT]
> **Mandatory Scientific Disclosure Statement:**
> "SatQuery AI currently provides model-derived, uncalibrated evidence-strength semantics. These values communicate the strength and consistency of available visual evidence and uncertainty signals; they are not statistical probabilities of answer correctness."

### Key Conceptual Guarantees
1. **Uncalibrated Heuristic**: Confidence levels (`LOW`, `MEDIUM`, `HIGH`) and numerical scores ($[0.0, 1.0]$) represent the strength, completeness, and consistency of observable image evidence corroborating the model's claims. They are **not** Bayesian posterior probabilities, conformal prediction sets, or calibrated accuracy predictors.
2. **No Length Bias**: Verbose answers are not rewarded. The heuristic explicitly inspects semantic claims against resolved visual signals; an unsupported long response receives no bonus.
3. **No Resolution Conflation**: Raw sensor grid dimensions ($512\times 512$) do not imply high confidence. Resolution is treated strictly as an information ceiling ($S_{\text{res}} \in [0.7, 1.0]$), while low or compressed resolutions impose degradation penalties.
4. **Transparent Categorization**: Every prediction is paired with its constituent sub-signals, detected hedge terms, and active ceiling constraints.

---

## 2. Confidence Architecture & Trace Flow

The confidence and visual evidence pipeline is integrated directly into SatQuery AI's strict 6-stage orchestration flow:

```text
User Query + Satellite Image(s)
              ↓
  [1] INPUT_VALIDATION        (Schema integrity, file existence, parameter firewall)
              ↓
  [2] ROUTER                  (Rule-based specialist tool dispatch)
              ↓
  [3] TOOL_EXECUTION          (VLM / Grounding / Siamese / Optical-SAR execution)
              ↓
  [4] EVIDENCE                (Spatial bbox extraction, heatmaps, cross-modal stats)
              ↓
  [5] CONFIDENCE              (Signal calculation, ceiling enforcement, uncalibrated level)
              ↓
  [6] RESULT_COMPOSITION      (Structured response packaging with zero CoT token leakage)
```

No chain-of-thought tokens or reasoning traces are exposed to external callers, strictly complying with the API contract.

---

## 3. VQA Evidence Strength Heuristic Formula

For Visual Question Answering, the uncalibrated score $S_{\text{raw}}$ is evaluated as a transparent weighted sum of five orthogonal signals:

$$S_{\text{raw}} = 0.30 \cdot S_{\text{avail}} + 0.30 \cdot S_{\text{cons}} + 0.15 \cdot S_{\text{spec}} + 0.15 \cdot S_{\text{suff}} + 0.10 \cdot S_{\text{ambig}}$$

### Constituent Signals
| Signal | Weight | Description | Evaluation Logic |
| :--- | :---: | :--- | :--- |
| **Evidence Availability ($S_{\text{avail}}$)** | 30% | Volume and resolution of observable visual signals. | Ratio of non-empty dynamic semantic categories identified in the scene (scaled by category confidence). |
| **Answer/Evidence Consistency ($S_{\text{cons}}$)** | 30% | Corroboration between generated text and image evidence. | Verified presence of dynamic visual features mentioned in the answer; penalized if claims lack corresponding image features. |
| **Query Specificity ($S_{\text{spec}}$)** | 15% | Semantic precision of the user's analytical question. | High for targeted queries (e.g. "Identify cargo vessels in the bay"), low for broad queries (e.g. "What is here?"). |
| **Visual Detail Sufficiency ($S_{\text{suff}}$)** | 15% | Suitability of sensor resolution and image area. | Resolution sufficiency baseline ($1.0$ for $\ge 512\times 512$, penalizing down to $0.4$ for degraded/tiny assets). |
| **Ambiguity Factor ($S_{\text{ambig}}$)** | 10% | Absence of hedge terms and speculative language. | $1.0$ when clear and decisive; drops to $0.20$ if hedge phrases ("appears to possibly", "cannot be determined", "not clearly visible") are present. |

### Discrete Level Mapping
- **`HIGH`**: $S \ge 0.70$ — Clear specific query, multi-feature visual corroboration, decisive language.
- **`MEDIUM`**: $0.40 \le S < 0.70$ — Partial feature availability, moderately broad query, or minor visual hedging.
- **`LOW`**: $0.00 \le S < 0.40$ — Weak evidence, severe visual ambiguity, or speculative/contradicted claims.

---

## 4. Hard Uncertainty Ceilings

To prevent hallucinated confidence and overconfident outputs, three hard ceilings override the weighted sum:

```text
       ┌─────────────────────────────────────────────────────────┐
       │                 Raw Score: S_raw                        │
       └──────────────────────────┬──────────────────────────────┘
                                  │
      Is answer contradictory? ───┼─► YES ──► S = min(S_raw, 0.20) [Hard LOW]
                                  │
     Are visual features empty? ──┼─► YES ──► S = min(S_raw, 0.35) [Hard LOW]
                                  │
    Severe ambiguity or hedges? ──┼─► YES ──► S = min(S_raw, 0.65) [Cap at MEDIUM]
                                  │
                                  ▼
                         Final Score: S_final
```

1. **Direct Contradiction Ceiling**: If the model claims an object is present when visual signals explicitly contradict it (or vice-versa), $S \le 0.20$ (`LOW`).
2. **Zero Visual Evidence Ceiling**: If no observable features can be resolved from the scene, $S \le 0.35$ (`LOW`).
3. **High Ambiguity / Severe Hedge Ceiling**: If substantial uncertainty qualifiers or high query ambiguity are present, $S \le 0.65$ (`MEDIUM` maximum).

---

## 5. Dynamic Visual Evidence Extraction

The evidence extraction system does **not** rely on hardcoded static categories (e.g., fixed assumptions of water or ships). Instead, it dynamically derives visual features and localized regions from the image content:

- **Scene Clustering & Segment Decomposition**: Dynamic color, texture, and intensity clustering partition the scene into observable regions.
- **Dynamic Semantic Labelling**: Visual descriptors (e.g. `dark_water_body`, `high_reflectance_structures`, `vegetation_canopy`, `linear_infrastructure`) are derived contextually from spectral characteristics.
- **Rich Visual Evidence Cards**: Each resolved feature is exported with:
  - `feature_name`: Dynamic semantic descriptor
  - `presence_status`: Detected / Potential / Hedged
  - `salience_score`: Relative prominence in the scene ($[0.0, 1.0]$)
  - `description`: Grounded visual summary of the region

---

## 6. Multi-Tool Confidence Semantics

SatQuery AI's specialist tools implement tool-appropriate, scientifically accurate confidence semantics:

### A. Visual Grounding (Grounding DINO)
- **Metric**: Detector Cross-Attention Logit (Peak / Mean Score).
- **Semantics**: `Detector score — uncalibrated`.
- **Constraint**: Strictly documented as cross-modal matching logits from the detector, **not** spatial localization precision, intersection-over-union (IoU), or ground-truth accuracy.

### B. Change Detection (Siamese ResNet-18)
- **Metric**: Area Stability Margin ($1.0 - \text{Change Ratio}$).
- **Semantics**: `Change evidence confidence: model-derived heuristic`.
- **Constraint**: Synthetic temporal pairs are explicitly flagged with:
  `Controlled synthetic temporal pair — not an operational accuracy benchmark.`

### C. Optical-SAR Cross-Modal Analysis
- **Metric**: Sensor Pipeline Integrity Status & Backscatter Matrix Correlation.
- **Semantics**: Evaluates cross-modal grid alignment, dynamic range, and Pearson $r$ correlation.
- **Constraint**: Mandatory classification stamp:
  `DATA CLASSIFICATION: PROXY SAR — confirms dimensional alignment and matrix correlation; NOT target detection accuracy.`

---

## 7. Frontend User Experience Architecture

The frontend (`frontend/src/components/ResultView.tsx` & `index.css`) renders the evidence layer with full scientific transparency:

1. **Confidence Metric Card**:
   - Distinct badges for `HIGH` (emerald), `MEDIUM` (amber), and `LOW` (rose).
   - Prominent uncalibrated badge: `Model-derived, Uncalibrated`.
   - Explanatory subtitle and active ceiling notice when capped.
2. **Scene Interpretation & Context**:
   - Natural language description summarizing the observable scene.
3. **Dynamic Visual Evidence Grid**:
   - Responsive cards displaying each resolved feature, salience bar, and presence badge.
