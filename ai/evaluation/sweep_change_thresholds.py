"""
SatQuery AI — LEVIR-CD Change Detection Threshold Sweep (Phase 5)
Performs systematic threshold sensitivity analysis across multiple candidate distance thresholds
(0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
on the genuine LEVIR-CD benchmark test subset (N=20 pairs).
Computes:
- Precision
- Recall
- F1 Score
- Intersection over Union (IoU)
- Total Changed Pixels vs Ground Truth
Saves empirical curve to results/change_threshold_sweep.csv.
"""

import os
import sys
import csv
import time
import json
from typing import Dict, Any, List
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as T

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai.inference.change_detection import SiameseResNetChangeDetector

MANIFEST_PATH = "data/benchmarks/levir_cd/manifest.json"
OUTPUT_CSV = "results/change_threshold_sweep.csv"
CANDIDATE_THRESHOLDS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.42, 0.45, 0.50, 0.55, 0.60]


def run_threshold_sweep(
    manifest_path: str = MANIFEST_PATH,
    output_csv: str = OUTPUT_CSV,
    thresholds: List[float] = CANDIDATE_THRESHOLDS,
) -> List[Dict[str, Any]]:
    """Runs threshold evaluation on LEVIR-CD test subset."""
    print("=" * 70)
    print("  SatQuery AI - LEVIR-CD Change Detection Threshold Sensitivity Sweep")
    print("=" * 70)

    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"LEVIR-CD manifest not found: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    samples = manifest.get("samples", [])
    print(f"Loaded {len(samples)} LEVIR-CD test pairs.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Executing feature extraction on device: {device}...")

    model = SiameseResNetChangeDetector(pretrained=True).to(device)
    model.eval()

    transform = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Pre-compute distance maps for all samples once to make sweep fast and deterministic
    cached_distance_maps = []
    cached_gt_masks = []

    t0_extract = time.perf_counter()
    for s in samples:
        t1_path = os.path.join(PROJECT_ROOT, s["image_path"])
        t2_path = os.path.join(PROJECT_ROOT, s["second_image_path"])
        lbl_path = os.path.join(PROJECT_ROOT, s["label_path"])

        t1_img = Image.open(t1_path).convert("RGB")
        t2_img = Image.open(t2_path).convert("RGB")
        lbl_img = Image.open(lbl_path).convert("L")

        gt_mask = (np.array(lbl_img) > 128).astype(np.uint8)

        t1_t = transform(t1_img).unsqueeze(0).to(device)
        t2_t = transform(t2_img).unsqueeze(0).to(device)

        with torch.inference_mode():
            dist_map = model(t1_t, t2_t)

        dist_np = dist_map.squeeze().cpu().numpy()
        d_min, d_max = dist_np.min(), dist_np.max()
        norm_dist = (dist_np - d_min) / (d_max - d_min + 1e-8)

        cached_distance_maps.append(norm_dist)
        cached_gt_masks.append(gt_mask)

    extract_sec = round(time.perf_counter() - t0_extract, 2)
    print(f"Computed normalized differential distance maps for all {len(samples)} pairs in {extract_sec}s.")

    sweep_results = []
    total_pixels_all = sum(m.size for m in cached_gt_masks)
    total_gt_changed_all = sum(int(np.sum(m)) for m in cached_gt_masks)

    print("\n--- Running Sweep Across Thresholds ---")
    for th in thresholds:
        tp_total = 0
        fp_total = 0
        fn_total = 0
        tn_total = 0
        pred_changed_total = 0

        for norm_dist, gt_mask in zip(cached_distance_maps, cached_gt_masks):
            pred_mask = (norm_dist >= th).astype(np.uint8)
            pred_changed = int(np.sum(pred_mask))
            pred_changed_total += pred_changed

            tp = int(np.sum((pred_mask == 1) & (gt_mask == 1)))
            fp = int(np.sum((pred_mask == 1) & (gt_mask == 0)))
            fn = int(np.sum((pred_mask == 0) & (gt_mask == 1)))
            tn = int(np.sum((pred_mask == 0) & (gt_mask == 0)))

            tp_total += tp
            fp_total += fp
            fn_total += fn
            tn_total += tn

        p = round(tp_total / (tp_total + fp_total), 4) if (tp_total + fp_total) > 0 else 0.0
        r = round(tp_total / (tp_total + fn_total), 4) if (tp_total + fn_total) > 0 else 1.0
        f1 = round(2 * (p * r) / (p + r), 4) if (p + r) > 0 else 0.0
        iou = round(tp_total / (tp_total + fp_total + fn_total), 4) if (tp_total + fp_total + fn_total) > 0 else 0.0
        pct_changed = round((pred_changed_total / total_pixels_all) * 100.0, 2)

        sweep_results.append({
            "threshold": th,
            "precision": p,
            "recall": r,
            "f1_score": f1,
            "iou": iou,
            "pred_changed_pixels": pred_changed_total,
            "gt_changed_pixels": total_gt_changed_all,
            "pred_changed_pct": pct_changed,
            "tp": tp_total,
            "fp": fp_total,
            "fn": fn_total,
            "tn": tn_total,
        })
        print(f"Threshold: {th:.2f} | Precision: {p:.4f} | Recall: {r:.4f} | F1: {f1:.4f} | IoU: {iou:.4f} | Pred Changed: {pct_changed:.2f}%")

    # Export to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    fieldnames = [
        "threshold", "precision", "recall", "f1_score", "iou",
        "pred_changed_pixels", "gt_changed_pixels", "pred_changed_pct",
        "tp", "fp", "fn", "tn"
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sweep_results:
            writer.writerow(row)

    # Find optimal threshold by F1
    best_row = max(sweep_results, key=lambda x: x["f1_score"])
    print("=" * 70)
    print(f"Sweep Completed! Results saved to {output_csv}")
    print(f"Optimal Threshold by F1: {best_row['threshold']:.2f}")
    print(f"  * Precision: {best_row['precision']:.4f}")
    print(f"  * Recall:    {best_row['recall']:.4f}")
    print(f"  * F1 Score:  {best_row['f1_score']:.4f}")
    print(f"  * IoU:       {best_row['iou']:.4f}")
    print("=" * 70)

    return sweep_results


if __name__ == "__main__":
    run_threshold_sweep()
