# SatQuery AI — Confidence Semantics Audit (Phase 8B)

This document formalizes the exact technical and mathematical semantics of the `confidence` field across all SatQuery AI analytical tools and API endpoints. 

> [!WARNING]
> **Strict Evaluation Rule**: No confidence value returned by SatQuery AI may be labeled as "accuracy", "ground-truth probability", or "classification precision" in judge demonstrations, frontend views, or technical reports. Every confidence metric represents a specific algorithmic or pipeline artifact as detailed below.

---

## Tool-by-Tool Confidence Semantics

| Tool / Pipeline | Confidence Value Range | Underlying Calculation / Source | Semantic Classification | What It Truly Measures | What It Does NOT Measure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VQA**<br>(`AdaptLLM Qwen2.5-VL-3B`) | `null` (`None`) | Greedy autoregressive token generation (`do_sample=False`, `max_new_tokens=100`). No token sequence probability aggregation is performed. | **Unsupported / Null** | Honest absence of arbitrary confidence score. The VLM outputs natural-language answers without fabricating an ungrounded certainty metric. | Does NOT measure correctness, factual truthfulness, or hallucination-free certainty. |
| **GROUNDING**<br>(`Grounding DINO Tiny`) | `[0.0, 1.0]` (typically `0.35`–`0.85`) | Post-processed sigmoid activation of cross-attention logit between language tokens and visual box proposal queries (`det["scores"]`). | **Detector Heuristic Score (Uncalibrated)** | Relative feature similarity between the text prompt (e.g. *"ships"*) and the spatial image region proposed by the Swin Transformer backbone. | Does NOT measure Intersection-over-Union (IoU), spatial accuracy, or bounding box correctness against human ground truth. |
| **CHANGE_DETECTION**<br>(`Siamese ResNet18`) | `[0.0, 1.0]` (e.g. `0.9744`) | Heuristic scene consistency score: $\text{conf} = 1.0 - \frac{\text{changed\_pixels}}{\text{total\_pixels}}$ at Euclidean feature distance threshold $\tau = 0.40$. | **Heuristic Area Margin Score** | The proportion of the scene remaining stable / unchanged under the Siamese differential feature distance metric. | Does NOT measure F1-score, pixel classification accuracy, precision, or recall against actual historical changes. |
| **OPTICAL_SAR**<br>(`Dual-Stream Engine`) | `1.0` | Discrete execution completion indicator ($1.0$ on valid multi-sensor matrix computation, `null` on error). | **Pipeline Integrity Status** | Confirms that dual-sensor rasters were successfully matched in pixel grid dimensions, radiometrically normalized, and Pearson $r$ correlation computed without numeric divergence. | Does NOT measure probability that radar backscatter echoes correspond to genuine physical vessels or land targets. |

---

## Frontend & Reporting Guidelines

1. **User Interface Label**: In [`frontend/src/components/ResultView.tsx`](file:///C:/Users/BHUVANESHWARAN%20N/Downloads/SatQuery-AI/frontend/src/components/ResultView.tsx), all confidence metrics are displayed under the explicit label:
   ```
   System Confidence: [XX.X]% (model estimate)
   ```
2. **Hover Caveat**: The UI tooltip explicitly instructs judges:
   *"System/model algorithmic confidence score; does not guarantee ground-truth accuracy."*
3. **No Fake Numbers**: If a model does not provide a native scalar probability (e.g. VQA), the system strictly renders `null` and omits the confidence pill rather than generating a random or hardcoded percentage.
4. **Presentation Prohibitions**: Presenters and pitch decks must never state:
   - *"The AI is 97% accurate"* (conflating Change Detection background stability with classification accuracy).
   - *"The model detected ships with 100% certainty"* (conflating Optical-SAR matrix completion status with target probability).
