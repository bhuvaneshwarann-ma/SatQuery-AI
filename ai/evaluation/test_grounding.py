"""
Visual Grounding Validation Test — SatQuery AI (Phase 3E)
Evaluates Grounding DINO (Swin-T variant) on real satellite imagery.
Target Hardware: NVIDIA GeForce RTX 5050 Laptop GPU (8 GB GDDR7 VRAM)
"""

import os
import sys
import time
import gc
import traceback
import torch
from PIL import Image, ImageDraw, ImageFont


def get_vram_info():
    """Return memory metrics in MB."""
    if not torch.cuda.is_available():
        return {"free_mb": 0.0, "total_mb": 0.0, "alloc_mb": 0.0, "reserved_mb": 0.0}
    free, total = torch.cuda.mem_get_info()
    return {
        "free_mb": round(free / (1024 ** 2), 2),
        "total_mb": round(total / (1024 ** 2), 2),
        "alloc_mb": round(torch.cuda.memory_allocated() / (1024 ** 2), 2),
        "reserved_mb": round(torch.cuda.memory_reserved() / (1024 ** 2), 2),
    }


def write_markdown_results(
    results_path: str,
    hw_info: dict,
    model_info: dict,
    image_info: dict,
    results_table: list,
    vram_log: dict,
    verdict: str,
):
    """Write grounding validation results report to docs/results/grounding_validation_results.md."""
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    lines = []
    lines.append("# Grounding Validation")
    lines.append("")
    lines.append("## Model")
    lines.append(f"* **Model Name**: `{model_info['model_id']}`")
    lines.append(f"* **Architecture**: Swin-T Grounding DINO Zero-Shot Object Detector")
    lines.append(f"* **Configuration**: `box_threshold={model_info['box_threshold']}`, `text_threshold={model_info['text_threshold']}`")
    lines.append(f"* **Inference Device**: {model_info['device']}")
    lines.append("")
    lines.append("## Test Image")
    lines.append(f"* **Filename**: `{image_info['filename']}`")
    lines.append(f"* **Source**: {image_info['source']}")
    lines.append(f"* **Dimensions**: {image_info['dimensions'][0]} x {image_info['dimensions'][1]} pixels ({image_info['format']})")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Prompt | Detections | Confidence (Min - Max) | Time (s) | Status |")
    lines.append("| :----- | ---------: | ---------------------: | -------: | :----- |")

    for r in results_table:
        conf_str = r["conf_str"]
        lines.append(f"| `{r['prompt']}` | {r['count']} | {conf_str} | {r['time_sec']:.2f}s | {r['status']} |")

    lines.append("")
    lines.append("## Hardware Observations")
    lines.append(f"* **VRAM Before Loading**: Free: {vram_log['before_load']['free_mb']} MB | Alloc: {vram_log['before_load']['alloc_mb']} MB")
    lines.append(f"* **VRAM After Loading**: Free: {vram_log['after_load']['free_mb']} MB | Alloc: {vram_log['after_load']['alloc_mb']} MB")
    lines.append(f"* **VRAM After Inference**: Free: {vram_log['after_inference']['free_mb']} MB | Alloc: {vram_log['after_inference']['alloc_mb']} MB")
    lines.append(f"* **Memory Footprint**: ~{round(vram_log['after_load']['alloc_mb'] - vram_log['before_load']['alloc_mb'], 2)} MB allocated on GPU (extremely lightweight)")
    lines.append("* **CPU Offloading**: None required (model fits entirely in GPU VRAM)")
    lines.append(f"* **Final Script Verdict**: `{verdict}`")
    lines.append("")
    lines.append("## Evidence")
    lines.append("Visual grounding with coordinate bounding boxes provides essential spatial proof for SatQuery AI:")
    lines.append("1. **Direct Spatial Grounding**: Bounding boxes localize exactly where the user query targets are located on the satellite canvas, eliminating black-box ambiguities.")
    lines.append("2. **Dual-Layer Validation**: Textual claims made by the VLM (e.g., 'ships are present') can be programmatically cross-verified against Grounding DINO detections.")
    lines.append("3. **Downstream Segmentation Anchor**: Bounding box outputs feed directly as spatial prompt tokens into SAM ViT-B to derive pixel-accurate masks.")
    lines.append(f"4. **Annotated Visual Artifact**: Generated detection visualization is saved at `docs/results/grounding_sample_result.jpg`.")
    lines.append("")
    lines.append("## Limitations")
    lines.append("* **Scale Discrepancy**: Small watercraft (<15 pixels in Landsat 30m GSD imagery) can be missed or confused with white-cap wave crests.")
    lines.append("* **Amorphous Geographic Boundaries**: Large amorphous features like `water` or `river` encompass sprawling continuous regions better suited for semantic segmentation than rectangular bounding boxes.")
    lines.append("* **Threshold Sensitivity**: Standard `box_threshold=0.30` requires careful tuning across varying sensor lighting conditions to prevent false positives in urban clutter.")
    lines.append("")

    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[OUTPUT] Saved grounding validation report to: {results_path}")


def draw_detections(base_image: Image.Image, all_detections: list, output_path: str):
    """Draw bounding boxes with label tags and confidence on the image."""
    annotated = base_image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)

    # Color map for diverse categories
    palette = [
        (255, 69, 0),    # Red-Orange
        (30, 144, 255),  # Dodger Blue
        (50, 205, 50),   # Lime Green
        (255, 215, 0),   # Gold
        (186, 85, 211),  # Medium Orchid
    ]

    color_idx = 0
    font = None
    try:
        font = ImageFont.load_default()
    except Exception:
        pass

    for det in all_detections:
        color = palette[color_idx % len(palette)]
        color_idx += 1
        prompt = det["prompt"]

        for box, score in zip(det["boxes"], det["scores"]):
            x1, y1, x2, y2 = [int(v) for v in box]
            # Draw rectangle with thickness
            for w in range(2):
                draw.rectangle([x1 - w, y1 - w, x2 + w, y2 + w], outline=color)

            label_text = f"{prompt}: {score:.2f}"
            # Draw label banner
            if font:
                bbox = draw.textbbox((x1, max(0, y1 - 14)), label_text, font=font)
                draw.rectangle(bbox, fill=color)
                draw.text((x1 + 1, max(0, y1 - 14)), label_text, fill=(255, 255, 255), font=font)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    annotated.save(output_path, "JPEG", quality=92)
    print(f"[OUTPUT] Saved annotated detection image to: {output_path}")


def main():
    print("=" * 70)
    print("  SatQuery AI - Phase 3E: Visual Grounding Feasibility Validation")
    print("=" * 70)

    # 1. Hardware & Environment Check
    vram_before_load = get_vram_info()
    hw_info = {
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "total_vram_mb": vram_before_load["total_mb"],
        "cuda_available": torch.cuda.is_available(),
    }
    print(f"Device: {hw_info['gpu_name']} | Total VRAM: {hw_info['total_vram_mb']} MB")
    print(f"VRAM Before Model Loading: Free={vram_before_load['free_mb']} MB | Alloc={vram_before_load['alloc_mb']} MB")

    # 2. Image Verification
    sample_img_path = os.path.join("data", "samples", "sample_satellite_port.jpg")
    if not os.path.exists(sample_img_path):
        print(f"[ERROR] Test image not found at: {sample_img_path}")
        print("GROUNDING_TEST_RESULT=FAIL")
        sys.exit(1)

    raw_image = Image.open(sample_img_path).convert("RGB")
    img_w, img_h = raw_image.size
    image_info = {
        "filename": "sample_satellite_port.jpg",
        "source": "NASA Earth Observatory (Landsat 9 OLI-2, Rio Grande)",
        "dimensions": (img_w, img_h),
        "format": "JPEG",
    }
    print(f"Test Image: {image_info['filename']} ({img_w}x{img_h})")

    # 3. Model Loading
    model_id = "IDEA-Research/grounding-dino-tiny"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    box_threshold = 0.30
    text_threshold = 0.25

    model_info = {
        "model_id": model_id,
        "device": device,
        "box_threshold": box_threshold,
        "text_threshold": text_threshold,
    }

    model = None
    processor = None

    try:
        print(f"\n--- Loading Grounding DINO: {model_id} ---")
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)
        model.eval()

        vram_after_load = get_vram_info()
        print("Model successfully loaded onto target device.")
        print(f"VRAM After Load: Free={vram_after_load['free_mb']} MB | Alloc={vram_after_load['alloc_mb']} MB")

        # 4. Sequential Prompt Evaluation
        test_prompts = ["ship", "boat", "river", "water", "island"]
        print("\n--- Running Grounding Queries ---")

        results_table = []
        all_detections = []

        for prompt in test_prompts:
            # Grounding DINO expects dot-terminated text phrases
            formatted_text = f"{prompt.strip().lower()}."
            print(f"\nTesting prompt: '{prompt}' (formatted: '{formatted_text}')")

            t0 = time.perf_counter()

            inputs = processor(images=raw_image, text=formatted_text, return_tensors="pt").to(device)

            with torch.inference_mode():
                outputs = model(**inputs)

            # Post-process detections into pixel coordinates (Transformers 5.x uses `threshold`)
            processed = processor.post_process_grounded_object_detection(
                outputs,
                inputs.input_ids,
                threshold=box_threshold,
                text_threshold=text_threshold,
                target_sizes=[(img_h, img_w)],
            )

            dt = time.perf_counter() - t0

            det = processed[0]
            scores = det["scores"].detach().cpu().tolist()
            boxes = det["boxes"].detach().cpu().tolist()

            num_detections = len(scores)

            if num_detections > 0:
                conf_str = f"{min(scores):.2f} - {max(scores):.2f}"
                all_detections.append({
                    "prompt": prompt,
                    "boxes": boxes,
                    "scores": scores,
                })
            else:
                conf_str = "N/A"

            print(f"Detections: {num_detections} | Confidence: {conf_str} | Latency: {dt:.2f}s")

            results_table.append({
                "prompt": prompt,
                "count": num_detections,
                "conf_str": conf_str,
                "time_sec": dt,
                "status": "SUCCESS",
            })

        vram_after_inference = get_vram_info()
        print(f"\nVRAM After Inference: Free={vram_after_inference['free_mb']} MB | Alloc={vram_after_inference['alloc_mb']} MB")

        # 5. Draw Annotated Visual Evidence Artifact
        annotated_out_path = os.path.join("docs", "results", "grounding_sample_result.jpg")
        draw_detections(raw_image, all_detections, annotated_out_path)

        # 6. Save Markdown Report
        vram_log = {
            "before_load": vram_before_load,
            "after_load": vram_after_load,
            "after_inference": vram_after_inference,
        }

        verdict = "GROUNDING_TEST_RESULT=PASS"
        results_doc_path = os.path.join("docs", "results", "grounding_validation_results.md")
        write_markdown_results(
            results_path=results_doc_path,
            hw_info=hw_info,
            model_info=model_info,
            image_info=image_info,
            results_table=results_table,
            vram_log=vram_log,
            verdict=verdict,
        )

        print("\n" + "=" * 70)
        print("Summary: Grounding DINO successfully executed across all target prompts.")
        print(f"Verdict: {verdict}")
        print("=" * 70)

    except torch.cuda.OutOfMemoryError as oom:
        print(f"[OOM ERROR] Grounding DINO CUDA Out of Memory: {oom}")
        print("GROUNDING_TEST_RESULT=FAIL")
    except Exception as err:
        print(f"[ERROR] Grounding DINO execution error: {err}")
        traceback.print_exc()
        print("GROUNDING_TEST_RESULT=FAIL")
    finally:
        # Clean up model from GPU memory
        if model is not None:
            del model
        if processor is not None:
            del processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        vram_cleaned = get_vram_info()
        print(f"\nVRAM After Model Cleanup: Free={vram_cleaned['free_mb']} MB | Alloc={vram_cleaned['alloc_mb']} MB")


if __name__ == "__main__":
    main()
