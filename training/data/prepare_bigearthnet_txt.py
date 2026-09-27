"""Prepare a bounded, scene-grouped BigEarthNet.txt adapter manifest.

BigEarthNet.txt supplies text annotations and Sentinel patch identifiers; the
paired Sentinel-1/Sentinel-2 image archive must be provisioned separately.
This command records that provenance instead of silently substituting RGB files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def prepare(metadata_path: str, image_root: str, output: str, split: str, limit: int):
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("Install pandas/pyarrow to read BigEarthNet.txt parquet metadata.") from exc
    frame = pd.read_parquet(metadata_path)
    frame = frame[frame["split"].astype(str).str.lower() == split.lower()]
    rows, seen = [], set()
    for _, item in frame.iterrows():
        patch = str(item["patch_id"])
        if patch in seen:
            continue
        seen.add(patch)
        s1 = Path(image_root) / "S1" / f"{item['s1_name']}.tif"
        s2 = Path(image_root) / "S2" / f"{patch}.tif"
        rows.append({"image": str(s2), "second_image": str(s1),
                     "question": str(item["input"]), "answer": str(item["output"]),
                     "scene_group": patch, "source": "BigEarthNet.txt",
                     "annotation_type": str(item.get("type", "unknown"))})
        if len(rows) >= limit:
            break
    if not rows:
        raise RuntimeError("No rows found; verify metadata path and split name.")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"output": output, "samples": len(rows), "split": split,
                      "image_root": str(Path(image_root).resolve()),
                      "note": "Both S1 and S2 files must exist before training."}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata")
    parser.add_argument("image_root")
    parser.add_argument("--output", default="training/data/bigearthnet_txt_train.json")
    parser.add_argument("--split", default="train")
    parser.add_argument("--limit", type=int, default=800)
    args = parser.parse_args()
    prepare(args.metadata, args.image_root, args.output, args.split, args.limit)
