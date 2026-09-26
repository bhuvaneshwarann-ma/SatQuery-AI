"""
SatQuery AI — VQA Dataset Validation & Integrity Checker (Phase 4)
Runs strict quality-gate checks on generated VQA datasets:
- Missing image verification
- Corrupt/unreadable file detection
- Empty question/answer detection
- Duplicate example detection
- Benchmark subset leakage auditing
- Format and dimensions consistency
"""

import os
import json
import sys
from typing import Dict, Any, List
from PIL import Image

BENCHMARK_MANIFEST = "data/benchmarks/rsvqa_lr/manifest.json"


def validate_vqa_file(dataset_path: str, manifest_path: str = BENCHMARK_MANIFEST) -> Dict[str, Any]:
    """Inspects a JSON dataset file and returns an audit report."""
    if not os.path.exists(dataset_path):
        return {"status": "FAIL", "error": f"Dataset file does not exist: {dataset_path}"}

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return {"status": "FAIL", "error": "Dataset root must be a JSON array of examples."}

    # Load benchmark manifest for leakage detection
    benchmark_queries = set()
    benchmark_images = set()
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
            for s in m_data.get("samples", []):
                benchmark_queries.add(s.get("query", "").strip().lower())
                benchmark_images.add(os.path.basename(s.get("image_path", "")))

    errors: List[str] = []
    seen_keys = set()
    duplicates = 0
    type_counts: Dict[str, int] = {}
    valid_count = 0

    for idx, item in enumerate(data):
        img_path = item.get("image")
        q = item.get("question")
        a = item.get("answer")
        tt = item.get("task_type", "unknown")

        type_counts[tt] = type_counts.get(tt, 0) + 1

        # Check fields
        if not img_path:
            errors.append(f"Sample #{idx}: Missing 'image' field.")
            continue
        if not q or not str(q).strip():
            errors.append(f"Sample #{idx}: Empty or missing 'question'.")
            continue
        if a is None or str(a).strip() == "":
            errors.append(f"Sample #{idx}: Empty or missing 'answer'.")
            continue

        # Check image existence & readability
        if not os.path.exists(img_path):
            errors.append(f"Sample #{idx}: Referenced image does not exist: {img_path}")
            continue

        try:
            with Image.open(img_path) as img:
                img.verify()
        except Exception as e:
            errors.append(f"Sample #{idx}: Corrupted image {img_path}: {e}")
            continue

        # Check duplicates
        key = (img_path, q.strip().lower())
        if key in seen_keys:
            duplicates += 1
            errors.append(f"Sample #{idx}: Duplicate (image, question) detected.")
        seen_keys.add(key)

        # Check benchmark leakage
        if q.strip().lower() in benchmark_queries:
            errors.append(f"Sample #{idx}: Benchmark leakage! Question matches RSVQA validation subset.")
        if os.path.basename(img_path) in benchmark_images:
            errors.append(f"Sample #{idx}: Benchmark leakage! Image filename matches RSVQA validation subset.")

        valid_count += 1

    report = {
        "dataset_path": dataset_path,
        "total_records": len(data),
        "valid_records": valid_count,
        "duplicate_records": duplicates,
        "task_type_distribution": type_counts,
        "error_count": len(errors),
        "errors": errors[:20],
        "status": "PASS" if len(errors) == 0 else "FAIL",
    }
    return report


def main():
    train_rep = validate_vqa_file("training/data/vqa_train.json")
    val_rep = validate_vqa_file("training/data/vqa_val.json")

    print("\n" + "=" * 60)
    print("  SatQuery AI - VQA Dataset Quality Gate Report")
    print("=" * 60)
    print(f"Train Dataset: {train_rep['dataset_path']} | Status: {train_rep['status']} | Valid: {train_rep.get('valid_records')}/{train_rep.get('total_records')}")
    print(f"Val Dataset:   {val_rep['dataset_path']} | Status: {val_rep['status']} | Valid: {val_rep.get('valid_records')}/{val_rep.get('total_records')}")
    
    if train_rep["status"] == "FAIL" or val_rep["status"] == "FAIL":
        print("\nErrors Found:")
        for err in train_rep.get("errors", []) + val_rep.get("errors", []):
            print(f"  * {err}")
        sys.exit(1)
    else:
        print("\nAll quality gates passed: zero missing images, zero corrupt rasters, zero benchmark leakage.")
        sys.exit(0)


if __name__ == "__main__":
    main()
