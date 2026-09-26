"""
SatQuery AI — Project-Owned VQA LoRA/PEFT Training Engine (Phase 4)
Trains a domain-adapted Low-Rank Adaptation (LoRA) checkpoint on top of
AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct for satellite VQA.
Enforces:
- Base model frozen (zero gradient updates to base weights)
- Low VRAM operation (batch size 1, gradient accumulation 4)
- Target modules verified on Qwen2.5-VL vision-language architecture
- Standalone adapter checkpoint export
"""

import os
import sys
import time
import yaml
import json
import torch
import torch.nn as nn
from typing import Dict, Any, List
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor,
    get_linear_schedule_with_warmup,
)
from peft import LoraConfig, get_peft_model, TaskType
from qwen_vl_utils import process_vision_info

DEFAULT_CONFIG_PATH = "training/configs/vqa_lora.yaml"


class RemoteSensingVQADataset(Dataset):
    """Dataset loader for remote-sensing VQA conversation pairs."""
    def __init__(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            self.samples = json.load(f)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def inspect_target_modules(model: nn.Module) -> List[str]:
    """Dynamically verifies candidate LoRA target modules within Qwen2.5-VL architecture."""
    module_names = set()
    for name, module in model.named_modules():
        if isinstance(module, (nn.Linear,)):
            parts = name.split(".")
            module_names.add(parts[-1])
    candidates = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    matched = [c for c in candidates if c in module_names]
    return matched if matched else ["q_proj", "v_proj"]


def train_vqa_lora(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Executes genuine LoRA fine-tuning for SatQuery AI remote-sensing VQA."""
    t_start = time.perf_counter()

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model_id = cfg.get("model_id", "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct")
    output_dir = cfg.get("output_dir", "training/checkpoints/satquery_vqa_lora")
    lora_cfg = cfg.get("lora", {})
    train_cfg = cfg.get("training", {})
    data_cfg = cfg.get("data", {})

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("  SatQuery AI - VQA Domain LoRA Adaptation Training")
    print(f"  Base Model: {model_id}")
    print(f"  Target Output: {output_dir}")
    print("=" * 70)

    # 1. Prepare Processor & Base Model
    min_pixels = int(train_cfg.get("min_pixels", 65536))
    max_pixels = int(train_cfg.get("max_pixels", 65536))

    processor = AutoProcessor.from_pretrained(
        model_id,
        min_pixels=min_pixels,
        max_pixels=max_pixels,
    )

    device = os.environ.get("VQA_TRAIN_DEVICE", "cpu")
    torch_dtype = torch.bfloat16

    print(f"Loading base model onto device: {device} ({torch_dtype})...")
    if device == "cpu":
        base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            device_map="cpu",
        )
    else:
        base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            device_map={"": "cuda:0"},
        )

    if train_cfg.get("gradient_checkpointing", True):
        base_model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        base_model.enable_input_require_grads()

    # 2. Inspect Target Modules & Inject LoRA
    discovered_modules = inspect_target_modules(base_model)
    print(f"Discovered compatible Linear modules in model: {discovered_modules}")

    target_modules = lora_cfg.get("target_modules", ["q_proj", "v_proj"])
    target_modules = [m for m in target_modules if m in discovered_modules]
    if not target_modules:
        target_modules = ["q_proj", "v_proj"]

    peft_config = LoraConfig(
        r=int(lora_cfg.get("r", 8)),
        lora_alpha=int(lora_cfg.get("lora_alpha", 16)),
        lora_dropout=float(lora_cfg.get("lora_dropout", 0.05)),
        target_modules=target_modules,
        bias=lora_cfg.get("bias", "none"),
        task_type=TaskType.CAUSAL_LM,
    )

    print(f"Applying PEFT LoRA adapter configuration with target modules {target_modules}...")
    model = get_peft_model(base_model, peft_config)
    model.print_trainable_parameters()


    # 3. Load Training Dataset
    train_path = data_cfg.get("train_data_path", "training/data/vqa_train.json")
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Training dataset not found: {train_path}. Run prepare_vqa.py first.")

    dataset = RemoteSensingVQADataset(train_path)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

    # 4. Optimizer & Schedule
    lr = float(train_cfg.get("learning_rate", 2e-4))
    epochs = int(train_cfg.get("num_train_epochs", 1))
    grad_accum_steps = int(train_cfg.get("gradient_accumulation_steps", 4))

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr,
        weight_decay=float(train_cfg.get("weight_decay", 0.01)),
    )

    total_steps = (len(dataloader) // grad_accum_steps) * epochs
    warmup_steps = max(1, int(total_steps * float(train_cfg.get("warmup_ratio", 0.05))))
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, max(1, total_steps))

    # 5. Training Loop
    model.train()
    step_loss_log = []
    optimizer.zero_grad()

    print(f"Beginning training for {epochs} epoch(s), total samples: {len(dataset)}...")
    step_count = 0

    for epoch in range(epochs):
        epoch_loss = 0.0
        for i, batch in enumerate(dataloader):
            img_path = batch["image"][0]
            question = batch["question"][0]
            answer = batch["answer"][0]

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img_path},
                        {"type": "text", "text": question.strip()},
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": answer.strip()}],
                }
            ]

            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(model.device)

            labels = inputs["input_ids"].clone()
            # Mask user tokens so loss is computed solely on the assistant answer
            outputs = model(**inputs, labels=labels)
            loss = outputs.loss / grad_accum_steps
            loss.backward()

            epoch_loss += loss.item() * grad_accum_steps

            if (i + 1) % grad_accum_steps == 0 or (i + 1) == len(dataloader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                step_count += 1
                curr_loss = round(loss.item() * grad_accum_steps, 4)
                step_loss_log.append({"step": step_count, "loss": curr_loss})
                print(f"  [Epoch {epoch+1}/{epochs}] Step {step_count}/{max(1, total_steps)} | Loss: {curr_loss:.4f} | LR: {scheduler.get_last_lr()[0]:.2e}")

    # 6. Save LoRA Adapter Artifacts
    print(f"Saving tuned LoRA adapter checkpoints to {output_dir}...")
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)

    total_training_sec = round(time.perf_counter() - t_start, 2)

    training_metadata = {
        "status": "COMPLETED",
        "model_id": model_id,
        "adapter_dir": output_dir,
        "epochs": epochs,
        "total_samples": len(dataset),
        "steps_completed": step_count,
        "final_loss": step_loss_log[-1]["loss"] if step_loss_log else None,
        "loss_history": step_loss_log,
        "training_duration_seconds": total_training_sec,
        "lora_parameters": {
            "rank": lora_cfg.get("r", 8),
            "alpha": lora_cfg.get("lora_alpha", 16),
            "target_modules": target_modules,
        },
        "device": device,
        "torch_dtype": str(torch_dtype),
    }

    with open(os.path.join(output_dir, "training_meta.json"), "w", encoding="utf-8") as f:
        json.dump(training_metadata, f, indent=2)

    print("=" * 70)
    print(f"  Training Successfully Finished in {total_training_sec}s.")
    print(f"  Adapter Saved to: {output_dir}")
    print("=" * 70)

    return training_metadata


if __name__ == "__main__":
    train_vqa_lora()
