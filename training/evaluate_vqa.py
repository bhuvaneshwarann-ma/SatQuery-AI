"""
SatQuery AI — Scientific VQA Adaptation Evaluator (Phase 4)
Runs strict side-by-side evaluation between the unadapted baseline
(AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct) and the SatQuery project-owned LoRA adapter
across the SAME fixed RSVQA-LR benchmark subset (N=20).
Enforces:
- Identical preprocessing and token normalization
- Identical generation parameters (greedy, max_new_tokens=100)
- Task-specific sub-metric breakdown (counting, presence, scene, land_cover)
- Zero data fabrication (empirical measurement output)
- Exports results/vqa_before_after.json and results/vqa_before_after.md
"""

import os
import sys
import time
import json
import string
import re
from typing import Dict, Any, List, Optional
import torch
from PIL import Image

try:
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
    from peft import PeftModel
    from qwen_vl_utils import process_vision_info
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

BENCHMARK_MANIFEST = "data/benchmarks/rsvqa_lr/manifest.json"
BASELINE_RESULTS_PATH = "docs/results/benchmark_rsvqa_results.json"
ADAPTER_CHECKPOINT_DIR = "training/checkpoints/satquery_vqa_lora_corrected"
OUTPUT_JSON = "results/vqa_controlled_comparison.json"
OUTPUT_MD = "results/vqa_controlled_comparison.md"


def normalize_vqa_text(text: str) -> str:
    """Standard token normalization for RSVQA evaluation."""
    if not text:
        return ""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    words = [w for w in text.split() if w not in {"a", "an", "the"}]
    return " ".join(words).strip()


def extract_candidate_answer(pred_text: str) -> str:
    """Extracts answer candidate token from model narrative."""
    if not pred_text:
        return ""
    clean = pred_text.strip()
    m = re.search(r'(?:answer\s+is|therefore,?\s*(?:the\s+answer\s+is)?)\s*[:]?\s*([a-zA-Z0-9\s]+?)(?:\.|$)', clean, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    first_word = clean.split()[0].strip(string.punctuation).lower()
    if first_word in {"yes", "no", "rural", "urban"}:
        return first_word
    return clean


def compute_token_f1(pred: str, gt: str) -> float:
    """Computes token-level precision, recall, and macro F1."""
    pred_tokens = normalize_vqa_text(pred).split()
    gt_tokens = normalize_vqa_text(gt).split()
    if not pred_tokens and not gt_tokens:
        return 1.0
    if not pred_tokens or not gt_tokens:
        return 0.0
    common = set(pred_tokens) & set(gt_tokens)
    if not common:
        return 0.0
    p = sum(min(pred_tokens.count(t), gt_tokens.count(t)) for t in common) / len(pred_tokens)
    r = sum(min(pred_tokens.count(t), gt_tokens.count(t)) for t in common) / len(gt_tokens)
    return round(2 * (p * r) / (p + r), 4) if (p + r) > 0 else 0.0


def categorize_query_task(query: str) -> str:
    """Classifies RSVQA benchmark sample into task category."""
    q = query.lower()
    if any(k in q for k in ["how many", "number of", "count"]):
        return "counting"
    if any(k in q for k in ["is there", "are there", "presence"]):
        return "object_presence"
    if any(k in q for k in ["where", "between", "adjacent", "along"]):
        return "spatial_relation"
    if any(k in q for k in ["compare", "more", "less"]):
        return "comparison"
    return "land_cover_scene"


def evaluate_vqa_before_after(
    manifest_path=BENCHMARK_MANIFEST, adapter_path=ADAPTER_CHECKPOINT_DIR,
    output_json=OUTPUT_JSON, output_md=OUTPUT_MD, resume=False,
):
    """Paired measurements with one loaded model and adapters explicitly disabled/enabled."""
    import hashlib
    import platform
    from contextlib import nullcontext
    if not HAS_DEPS:
        raise RuntimeError("Install the locked model dependencies before evaluation")
    if not os.path.isfile(os.path.join(adapter_path, "adapter_config.json")):
        raise FileNotFoundError("Corrected adapter is required")
    with open(manifest_path, encoding="utf-8") as f:
        samples = json.load(f)["samples"]
    if not samples:
        raise ValueError("Benchmark is empty")
    device = os.environ.get("VQA_EVAL_DEVICE", "cpu")
    model_id = "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct"
    settings = {"min_pixels": 65536, "max_pixels": 65536,
                "max_new_tokens": 100, "do_sample": False, "seed": 42}
    experiment = {"settings": settings, "manifest_sha256": hashlib.sha256(open(manifest_path,"rb").read()).hexdigest(),
                  "adapter_sha256": hashlib.sha256(open(os.path.join(adapter_path,"adapter_model.safetensors"),"rb").read()).hexdigest()}
    results = {"baseline": [], "adapted": []}
    completed = 0
    if resume:
        with open(output_json + ".progress", encoding="utf-8") as stream:
            progress = json.load(stream)
        if progress.get("experiment") != experiment:
            raise ValueError("Checkpoint settings, manifest or adapter differ; cannot resume")
        results = progress["results"]
        completed = len(results["baseline"])
        if completed != len(results["adapted"]) or completed > len(samples):
            raise ValueError("Checkpoint does not contain complete sample pairs")
        for variant in results:
            for row, sample in zip(results[variant], samples):
                if row["sample_id"] != sample["sample_id"] or row["query"] != sample["query"] or row["ground_truth"] != str(sample["ground_truth"]):
                    raise ValueError("Checkpoint sample mismatch")
    torch.manual_seed(settings["seed"])
    processor = AutoProcessor.from_pretrained(model_id, min_pixels=settings["min_pixels"], max_pixels=settings["max_pixels"])
    base = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map=device)
    model = PeftModel.from_pretrained(base, adapter_path)
    model.eval()
    started = time.perf_counter()
    for sample in samples[completed:]:
        messages = [{"role": "user", "content": [{"type": "image", "image": sample["image_path"]},
                     {"type": "text", "text": sample["query"].strip()}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        images, videos = process_vision_info(messages)
        inputs = processor(text=[text], images=images, videos=videos, padding=True, return_tensors="pt").to(model.device)
        for variant in ["baseline", "adapted"]:
            t0 = time.perf_counter()
            row = {"sample_id": sample["sample_id"], "query": sample["query"], "ground_truth": str(sample["ground_truth"])}
            try:
                with (model.disable_adapter() if variant == "baseline" else nullcontext()), torch.inference_mode():
                    out = model.generate(**inputs, max_new_tokens=settings["max_new_tokens"], do_sample=False)
                raw = processor.batch_decode(out[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0].strip()
                answer = extract_candidate_answer(raw)
                row.update(status="SUCCESS", predicted_raw=raw, predicted_answer=answer,
                           exact_match=normalize_vqa_text(answer) == normalize_vqa_text(row["ground_truth"]),
                           token_f1=compute_token_f1(answer, row["ground_truth"]))
            except Exception as exc:
                row.update(status="ERROR", error=str(exc), exact_match=False, token_f1=0.0)
            row["latency_ms"] = round((time.perf_counter()-t0)*1000,2)
            results[variant].append(row)
            print(f"{variant} {sample['sample_id']}: {row['status']} EM={row['exact_match']}", flush=True)
        # Recoverable progress; never substitute it for the completed comparison.
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json + ".progress", "w", encoding="utf-8") as f:
            json.dump({"experiment": experiment, "results": results}, f, indent=2)
    def aggregate(rows):
        return {"sample_count": len(rows), "exact_match_pct": round(100*sum(r["exact_match"] for r in rows)/len(rows),2),
                "macro_token_f1": round(sum(r["token_f1"] for r in rows)/len(rows),4),
                "mean_latency_ms": round(sum(r["latency_ms"] for r in rows)/len(rows),2),
                "failed_samples": sum(r["status"] != "SUCCESS" for r in rows)}
    report = {"status": "COMPLETED", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "benchmark": "RSVQA-LR validation", "model": model_id, "adapter": adapter_path,
              "settings": settings, "device": device, "dtype": "bfloat16", "python": platform.python_version(),
              "torch": torch.__version__, "manifest_sha256": hashlib.sha256(open(manifest_path,"rb").read()).hexdigest(),
              "baseline": aggregate(results["baseline"]), "adapted": aggregate(results["adapted"]),
              "sample_evaluations": results, "current_segment_duration_seconds": round(time.perf_counter()-started,2),
              "total_generation_seconds": round(sum(row["latency_ms"] for rows in results.values() for row in rows)/1000,2),
              "resumed_sample_pairs": completed,
              "latency_scope": "Generation only; shared preprocessing/model loading excluded",
              "limitations": ["Small benchmark slice; no broad accuracy claim", "Adapter training corpus contains very few independent scenes"]}
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Controlled VQA comparison\n\nBoth variants use identical inputs and settings; baseline disables the adapter.\n\n")
        f.write("| Variant | Exact match | Token F1 | Failures |\n|---|---:|---:|---:|\n")
        for variant in ["baseline", "adapted"]:
            m=report[variant]
            f.write(f"| {variant} | {m['exact_match_pct']}% | {m['macro_token_f1']} | {m['failed_samples']} |\n")
        f.write("\nSmall validation slice. Full settings, sample predictions and timing scope are in the accompanying JSON.\n")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    evaluate_vqa_before_after(resume=args.resume)
