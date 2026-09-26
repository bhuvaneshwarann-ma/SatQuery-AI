# SatQuery AI — Project-Owned VQA LoRA Adaptation Engine

This directory provides the end-to-end training and evaluation pipeline for adapting `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` on domain-specific remote-sensing visual question answering.

---

## 1. Directory Structure

```text
training/
├── configs/
│   └── vqa_lora.yaml         # Training hyperparameters, LoRA target modules, and optimizer config
├── data/
│   ├── prepare_vqa.py        # Dataset preprocessing, task-type categorization, and leakage check
│   ├── validate_vqa.py       # Quality gate validation script
│   ├── vqa_train.json        # Normalized training split (isolated from benchmark)
│   └── vqa_val.json          # Normalized validation split
├── checkpoints/
│   └── satquery_vqa_lora/    # Standalone PEFT LoRA adapter weights (.safetensors, adapter_config.json)
├── train_vqa_lora.py         # PyTorch + PEFT training script with GPU/CPU offload & frozen backbone
├── evaluate_vqa.py           # Side-by-side benchmark comparison against RSVQA-LR subset
└── README.md                 # This documentation
```

---

## 2. Adaptation Workflow

### Step 1: Preprocess and Validate Dataset
Normalizes question-answer pairs across 6 distinct remote sensing task types:
`counting`, `object_presence`, `spatial_relation`, `comparison`, `scene`, `land_cover`.
Enforces non-leakage against the fixed 20-sample RSVQA-LR validation benchmark.

```bash
python training/data/prepare_vqa.py
python training/data/validate_vqa.py
```

### Step 2: Execute LoRA Fine-Tuning
Trains a Low-Rank Adaptation adapter with frozen base model weights:
- **Base Model**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
- **Target Modules**: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
- **LoRA Rank $r$**: 8
- **LoRA Alpha $\alpha$**: 16
- **Dropout**: 0.05
- **Batch Size**: 1 (Gradient Accumulation: 4)
- **Optimizer**: AdamW ($\text{LR}=2\times 10^{-4}$)

```bash
python training/train_vqa_lora.py
```

### Step 3: Run Comparative Benchmark Evaluation
Executes the adapted model on the SAME 20 RSVQA-LR validation samples and generates comparative reports:

```bash
python training/evaluate_vqa.py
```

Generates:
- `results/vqa_before_after.json`
- `results/vqa_before_after.md`
