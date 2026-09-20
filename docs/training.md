# Training & Adaptation Strategy — SatQuery AI

## 1. Document Overview
This document outlines the training, adaptation, fine-tuning, and prompt-engineering strategies for **SatQuery AI**'s remote-sensing vision and vision-language components.

---

## 2. Adaptation Objectives
* **Overhead Domain Transfer**: Align general vision-language capabilities with remote-sensing nadir viewing angles, multi-spectral band variations, and small-scale visual features.
* **Efficient Compute Footprint**: Prioritize parameter-efficient adaptation (LoRA, prefix tuning, instruction tuning) over full pre-training to operate within hackathon compute limits.
* **Cross-Modal Grounding**: Bridge textual referring expressions to accurate pixel-level and bounding-box coordinates.

---

## 3. Dataset Requirements & Benchmarks

### 3.1 Remote-Sensing VQA Datasets
* Candidate benchmarks: RSVQA (LR/HR), RSIVQA, or curated domain QA pairs covering counting, presence, and spatial relationship questions.

### 3.2 Visual Grounding & Object Detection Datasets
* Datasets featuring oriented or horizontal bounding boxes for aerial targets (DOTA, DIOR, FAIR1M).
* Classes of interest: Storage tanks, cargo ships, aircraft, bridges, harbors, solar arrays.

### 3.3 Bi-Temporal Change Detection Datasets
* Paired remote-sensing change datasets (LEVIR-CD, WHU-CD, SYSU-CD) containing pre/post registered scenes and change masks.

### 3.4 Optical-SAR Multi-Sensor Datasets
* Co-registered optical and SAR imagery (e.g., SEN1-2 dataset, SpaceNet 6) for cross-sensor feature correlation.

---

## 4. Fine-Tuning & Adaptation Methodologies

### 4.1 Parameter-Efficient Fine-Tuning (PEFT / LoRA)
* Freeze base vision transformer and language decoder backbones.
* Inject low-rank adapter (LoRA) matrices into attention projection layers to learn remote-sensing vocabulary and spatial tokens.

### 4.2 Instruction Tuning & Prompt Formatting
* Construct structured instruction prompts containing:
  - System role (Earth Observation specialist).
  - Spatial resolution context (GSD).
  - Explicit output constraint (coordinate brackets, confidence, visual evidence tag).

### 4.3 Change Detection Head Adaptation
* Training lightweight difference-decoder modules on paired feature vectors to predict binary and semantic change masks.

---

## 5. Evaluation Metrics & Benchmarks
* **VQA Evaluation**: Accuracy, BLEU, ROUGE-L, CIDEr.
* **Grounding & Detection**: Mean Average Precision ($mAP_{50}$, $mAP_{50:95}$), Average Recall ($AR$).
* **Change Detection**: Intersection over Union ($IoU$), F1-Score, Overall Accuracy ($OA$).
* **Confidence Calibration**: Expected Calibration Error ($ECE$).

---

## 6. Open Decisions (To Be Finalized)
* Selection of target parameter count (e.g., lightweight ~3B/7B VLM vs. modular vision-encoder + LLM).
* Finalization of training execution environment (local GPU vs. cloud compute instances).
