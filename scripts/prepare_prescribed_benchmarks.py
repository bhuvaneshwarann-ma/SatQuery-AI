"""Build honest local manifests for the prescribed evaluation inputs.

This utility never invents labels or treats a proxy image as prescribed data.
It scans data supplied by the user/downloaded from the official source and
creates manifests consumed by ``prescribed_benchmark_runner.py``.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {path} ({len(payload.get('samples', []))} samples)")


def build_cdvqa(root: Path, output: Path) -> None:
    images = sorted([p for p in root.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}])
    if not images:
        raise SystemExit("CDVQA image directory is empty; download the official CDVQA test images first.")
    # CDVQA releases commonly use *_A/*_B, before/after, or T1/T2 naming.
    groups: dict[str, dict[str, Path]] = {}
    for image in images:
        stem = image.stem
        match = re.match(r"(.+?)(?:[_-](?:a|b|t1|t2|before|after))$", stem, re.I)
        if not match:
            continue
        key = match.group(1)
        side = stem[len(key):].lower()
        groups.setdefault(key, {})["second" if side.endswith(("b", "t2", "after")) else "primary"] = image
    samples = []
    for index, (key, pair) in enumerate(sorted(groups.items())):
        if "primary" not in pair or "second" not in pair:
            continue
        samples.append({"sample_id": f"cdvqa-{index + 1:05d}",
                        "image_path": _rel(pair["primary"]),
                        "second_image_path": _rel(pair["second"]),
                        "query": "What changed between these two observations?",
                        "ground_truth": None,
                        "annotation_required": True})
    if not samples:
        raise SystemExit("CDVQA images were found but no T1/T2 pairs could be inferred from filenames.")
    _write(output, {"dataset_name": "CDVQA", "source_url": "https://github.com/YZHJessica/CDVQA",
                    "task": "CDVQA", "split": "test", "samples": samples,
                    "limitations": ["Populate ground_truth and change_direction from the official test annotations before scoring."]})


def build_sen12(root: Path, output: Path) -> None:
    rasters = sorted([p for p in root.rglob("*") if p.suffix.lower() in {".tif", ".tiff"}])
    if not rasters:
        raise SystemExit("SEN1-2 directory is empty; provide the official paired Sentinel-1/2 rasters first.")
    groups: dict[str, dict[str, Path]] = {}
    for raster in rasters:
        lower = raster.stem.lower()
        sensor = "sar" if re.search(r"(?:^|[_-])(?:s1|sar)(?:[_-]|$)", lower) else "optical" if re.search(r"(?:^|[_-])(?:s2|optical)(?:[_-]|$)", lower) else None
        if not sensor:
            continue
        key = re.sub(r"(?:^|[_-])(?:s1|s2|sar|optical)(?:[_-]|$)", "_", lower).strip("_-")
        groups.setdefault(key, {})[sensor] = raster
    samples = []
    for index, (key, pair) in enumerate(sorted(groups.items())):
        if "optical" not in pair or "sar" not in pair:
            continue
        samples.append({"sample_id": f"sen1-2-{index + 1:05d}",
                        "optical_image_path": _rel(pair["optical"]),
                        "sar_image_path": _rel(pair["sar"]),
                        "query": "Compare the optical and SAR observations for built-up and water-covered regions.",
                        "sensor_metadata": {"optical_sensor": "Sentinel-2", "sar_sensor": "Sentinel-1"},
                        "reference_regions": None})
    if not samples:
        raise SystemExit("No Sentinel-1/Sentinel-2 filename pairs were inferred.")
    _write(output, {"dataset_name": "SEN1-2", "source_url": "https://github.com/isstncu/s1s2",
                    "task": "SEN1_2", "split": "test", "samples": samples,
                    "limitations": ["Populate reference_regions and baseline predictions before reporting class F1."]})


def build_isro(root: Path, output: Path) -> None:
    optical = sorted([p for p in root.rglob("*") if p.suffix.lower() in {".tif", ".tiff"} and re.search(r"cartosat|optical", p.stem, re.I)])
    sar = sorted([p for p in root.rglob("*") if p.suffix.lower() in {".tif", ".tiff"} and re.search(r"risat|sar", p.stem, re.I)])
    if not optical or not sar:
        raise SystemExit("ISRO root must contain labelled Cartosat/optical and RISAT/SAR GeoTIFFs supplied by the authorised data owner.")
    samples = []
    for index, (optical_path, sar_path) in enumerate(zip(optical, sar)):
        samples.append({"sample_id": f"isro-pair-{index + 1:04d}", "optical_image_path": _rel(optical_path),
                        "sar_image_path": _rel(sar_path), "sensor_metadata": {"optical_sensor": "Cartosat-2S", "sar_sensor": "RISAT"}})
    _write(output, {"dataset_name": "ISRO/SAC Cartosat-2S + RISAT", "source_url": "https://bhoonidhi.nrsc.gov.in/",
                    "task": "ISRO", "mode": "readiness", "split": "representative_pairs", "samples": samples,
                    "limitations": ["The hidden ISRO judging labels are not included; this manifest validates compatibility only."]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdvqa-root", type=Path)
    parser.add_argument("--sen1-2-root", type=Path)
    parser.add_argument("--isro-root", type=Path)
    args = parser.parse_args()
    if args.cdvqa_root:
        build_cdvqa(args.cdvqa_root, ROOT / "data/benchmarks/cdvqa/manifest.json")
    if args.sen1_2_root:
        build_sen12(args.sen1_2_root, ROOT / "data/benchmarks/sen1_2/manifest.json")
    if args.isro_root:
        build_isro(args.isro_root, ROOT / "data/benchmarks/isro/manifest.json")
    if not any((args.cdvqa_root, args.sen1_2_root, args.isro_root)):
        parser.error("provide at least one dataset root")
