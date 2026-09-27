"""Reproducible evaluators for the SIH-prescribed benchmark manifest formats.

The runner intentionally refuses to fabricate scores: a missing image, answer,
box or label is recorded as SKIPPED/ERROR and the aggregate becomes unavailable.
Each sample may contain relative paths under the repository root or absolute paths.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import string
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _path(value: str | None) -> str | None:
    if not value:
        return None
    candidate = Path(value)
    return str(candidate if candidate.is_absolute() else ROOT / candidate)


def normalize(text: Any) -> str:
    value = "" if text is None else str(text).lower()
    value = value.translate(str.maketrans("", "", string.punctuation))
    return " ".join(w for w in value.split() if w not in {"a", "an", "the"})


def token_f1(prediction: Any, reference: Any) -> float:
    predicted, expected = normalize(prediction).split(), normalize(reference).split()
    if not predicted and not expected:
        return 1.0
    if not predicted or not expected:
        return 0.0
    overlap = sum(min(predicted.count(token), expected.count(token)) for token in set(predicted) & set(expected))
    precision, recall = overlap / len(predicted), overlap / len(expected)
    return round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0


def best_token_f1(prediction: Any, references: Any) -> float:
    """Score against datasets that publish one or more accepted answers."""
    values = references if isinstance(references, list) else [references]
    return max((token_f1(prediction, value) for value in values), default=0.0)


def box_iou(left: Any, right: Any) -> float:
    """IoU for [x1, y1, x2, y2] boxes; malformed boxes score zero."""
    try:
        ax1, ay1, ax2, ay2 = [float(v) for v in left]
        bx1, by1, bx2, by2 = [float(v) for v in right]
        ix1, iy1, ix2, iy2 = max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
        union = area_a + area_b - inter
        return round(inter / union, 4) if union else 0.0
    except (TypeError, ValueError):
        return 0.0


def _boxes_from_result(result: dict[str, Any]) -> list[list[float]]:
    evidence = result.get("evidence") or {}
    candidates = evidence.get("bounding_boxes") or result.get("bounding_boxes") or []
    if isinstance(evidence, list):
        candidates = evidence[0].get("bounding_boxes", []) if evidence else []
    return [box for box in candidates if isinstance(box, (list, tuple)) and len(box) == 4]


def _pair_readiness(primary: str, second: str, sample: dict[str, Any], task: str) -> dict[str, Any]:
    """Validate real-pair compatibility before any model is executed.

    This is deliberately a readiness gate, not an accuracy claim. Manifests can
    run with ``mode: readiness`` when hidden labels are unavailable.
    """
    result: dict[str, Any] = {"status": "READY", "checks": [], "warnings": []}
    if not second:
        return {"status": "BLOCKED", "checks": [], "warnings": ["A paired optical/SAR input is required."]}
    for label, path in (("optical", primary), ("sar", second)):
        suffix = Path(path).suffix.lower()
        if suffix not in {".tif", ".tiff"}:
            result["warnings"].append(f"{label} input is {suffix or 'extensionless'}; GeoTIFF is required for strict {task} readiness.")
        try:
            with Image.open(path) as image:
                result["checks"].append({"modality": label, "size": list(image.size), "bands": image.getbands(), "format": image.format})
        except Exception as error:
            result["status"] = "BLOCKED"
            result["warnings"].append(f"{label} image unreadable: {error}")
    sizes = [tuple(item["size"]) for item in result["checks"]]
    if len(sizes) == 2 and sizes[0] != sizes[1]:
        result["status"] = "BLOCKED"
        result["warnings"].append("Optical and SAR rasters do not share a pixel grid size.")
    metadata = sample.get("sensor_metadata") or {}
    if task == "ISRO" and not {"optical_sensor", "sar_sensor"}.issubset(metadata):
        result["status"] = "BLOCKED"
        result["warnings"].append("ISRO readiness requires optical_sensor and sar_sensor metadata in the manifest.")
    result["declared_sensor_metadata"] = metadata
    return result


def direction(text: str) -> str | None:
    clean = normalize(text)
    for candidate in ("increased", "decreased", "unchanged"):
        if re.search(rf"\b{candidate}\b", clean):
            return candidate
    return None


def load_manifest(path: str) -> dict[str, Any]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest.get("samples"), list):
        raise ValueError("Manifest must contain a samples array.")
    return manifest


def _valid_image(path: str | None) -> bool:
    if not path or not os.path.isfile(path):
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def evaluate(manifest_path: str, output_path: str, limit: int | None = None) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    task = str(manifest.get("task", "VRSBENCH")).upper()
    samples = manifest["samples"][:limit] if limit else manifest["samples"]
    rows: list[dict[str, Any]] = []
    for sample in samples:
        sample_id = sample.get("sample_id", f"sample-{len(rows)+1}")
        started = time.perf_counter()
        row = {"sample_id": sample_id, "status": "SKIPPED", "query": sample.get("query", ""),
               "input_references": [], "sample_metrics": {}}
        primary = _path(sample.get("image_path") or sample.get("optical_image_path"))
        second = _path(sample.get("second_image_path") or sample.get("sar_image_path"))
        row["input_references"] = [path for path in (primary, second) if path]
        if not _valid_image(primary) or (second and not _valid_image(second)):
            row["reason"] = "Required image is missing or unreadable."
            row["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            rows.append(row)
            continue
        try:
            if task in {"VRSBENCH", "RSVQA", "CDVQA"}:
                from backend.app.agent.schemas import AnalysisRequest
                from backend.app.services.orchestration_service import execute_agent_request
                request = AnalysisRequest(query=sample.get("query", "Describe this image."), image_path=primary,
                    second_image_path=second if task == "CDVQA" else None,
                    sar_image_path=second if task == "OPTICAL_SAR" else None)
                result = execute_agent_request(request).to_dict()
                prediction = result.get("answer", "")
                reference = sample.get("ground_truth", sample.get("answer"))
                if reference is None:
                    row["reason"] = "Reference answer is missing."
                else:
                    row.update(status="SUCCESS", prediction=prediction, ground_truth=reference)
                    row["sample_metrics"] = {"exact_match": any(normalize(prediction) == normalize(value) for value in (reference if isinstance(reference, list) else [reference])),
                                              "token_f1": best_token_f1(prediction, reference)}
                    if task == "CDVQA" and sample.get("change_direction"):
                        row["sample_metrics"]["direction_match"] = direction(prediction) == direction(sample["change_direction"])
                    if task == "VRSBENCH" and sample.get("ground_truth_box") is not None:
                        predicted_boxes = _boxes_from_result(result)
                        reference_boxes = sample["ground_truth_box"]
                        if reference_boxes and isinstance(reference_boxes[0], (int, float)):
                            reference_boxes = [reference_boxes]
                        pair_scores = [max((box_iou(predicted, expected) for predicted in predicted_boxes), default=0.0) for expected in reference_boxes]
                        row["sample_metrics"].update({"grounding_box_iou": round(_mean(pair_scores), 4) if pair_scores else 0.0,
                                                       "grounding_recall_at_50": round(_mean([float(score >= 0.5) for score in pair_scores]), 4) if pair_scores else 0.0,
                                                       "predicted_box_count": len(predicted_boxes)})
            elif task in {"OPTICAL_SAR", "SEN1_2", "ISRO"}:
                readiness = _pair_readiness(primary, second, sample, task)
                row["pair_readiness"] = readiness
                if readiness["status"] != "READY":
                    row["reason"] = "Pair compatibility gate failed."
                    row["status"] = "BLOCKED" if str(manifest.get("mode", "accuracy")).lower() == "readiness" else "SKIPPED"
                elif str(manifest.get("mode", "accuracy")).lower() == "readiness":
                    row.update(status="SUCCESS", prediction="pair-compatible", ground_truth=None,
                               sample_metrics={"pair_compatibility": True})
                else:
                    # This path measures all three requested engineering baselines only
                    # when the manifest supplies reference class regions. It never treats
                    # correlation or threshold pixels as class accuracy.
                    references = sample.get("reference_regions")
                    if not isinstance(references, list):
                        row["reason"] = "Reference regions are required for optical-only/SAR-only/combined comparison."
                    else:
                        from ai.inference.optical_sar import run_optical_sar
                        from ai.inference.grounding import run_grounding
                        optical = run_grounding(primary, "buildings. water.", {})
                        sar = run_optical_sar(primary, second, sample.get("query", ""), {})
                        # Region-level class labels are evaluated only if the manifest
                        # provides predictions from the three registered baselines.
                        predictions = {name: sample.get(f"{name}_prediction") for name in ("optical_only", "sar_only", "combined")}
                        if not all(isinstance(value, list) for value in predictions.values()):
                            row["reason"] = "Manifest must provide labelled region predictions for all three baselines."
                        else:
                            reference_set = {str(value).lower() for value in references}
                            row.update(status="SUCCESS", prediction=predictions, ground_truth=references)
                            row["sample_metrics"] = {name + "_class_f1": token_f1(" ".join(map(str, value)), " ".join(sorted(reference_set)))
                                                      for name, value in predictions.items()}
                            row["evidence"] = {"optical_grounding_status": optical.get("status"),
                                               "sar_statistics_status": sar.get("status"),
                                               "comparison_scope": "reference-labelled candidate classes"}
            else:
                row["reason"] = f"Task {task} requires a task-specific evaluator and labels."
        except Exception as error:
            row.update(status="ERROR", error_type=type(error).__name__, error=str(error))
        row["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        rows.append(row)
    successful = [row for row in rows if row["status"] == "SUCCESS"]
    metrics: dict[str, Any] = {"status": "UNAVAILABLE", "reason": "No reference-scored samples completed."}
    if successful and all("exact_match" in r["sample_metrics"] and "token_f1" in r["sample_metrics"] for r in successful):
        metrics = {"status": "MEASURED", "sample_count": len(successful),
                   "exact_match": round(_mean([float(r["sample_metrics"]["exact_match"]) for r in successful]), 4),
                   "token_f1": round(_mean([r["sample_metrics"]["token_f1"] for r in successful]), 4)}
        direction_rows = [r for r in successful if "direction_match" in r["sample_metrics"]]
        if direction_rows:
            metrics["direction_accuracy"] = round(_mean([float(r["sample_metrics"]["direction_match"]) for r in direction_rows]), 4)
        box_rows = [r for r in successful if "grounding_box_iou" in r["sample_metrics"]]
        if box_rows:
            metrics["grounding_box_iou"] = round(_mean([r["sample_metrics"]["grounding_box_iou"] for r in box_rows]), 4)
            metrics["grounding_recall_at_50"] = round(_mean([r["sample_metrics"]["grounding_recall_at_50"] for r in box_rows]), 4)
    elif successful and all("pair_compatibility" in r["sample_metrics"] for r in successful):
        metrics = {"status": "READINESS_VALIDATED", "sample_count": len(successful),
                   "pair_compatibility_rate": round(_mean([float(r["sample_metrics"]["pair_compatibility"]) for r in successful]), 4)}
    elif successful and all("optical_only_class_f1" in r["sample_metrics"] for r in successful):
        metrics = {"status": "MEASURED", "sample_count": len(successful),
                   "optical_only_class_f1": round(_mean([r["sample_metrics"]["optical_only_class_f1"] for r in successful]), 4),
                   "sar_only_class_f1": round(_mean([r["sample_metrics"]["sar_only_class_f1"] for r in successful]), 4),
                   "combined_class_f1": round(_mean([r["sample_metrics"]["combined_class_f1"] for r in successful]), 4)}
    total_seconds = round(sum(float(row.get("latency_ms", 0)) for row in rows) / 1000, 3)
    result = {"benchmark_id": f"{task.lower()}_{int(time.time())}", "task": task,
              "model": "SatQuery AI registered workflow",
              "dataset": {"name": manifest.get("dataset_name", task), "version": manifest.get("version"),
                          "source_url": manifest.get("source_url"), "split": manifest.get("split"),
                          "subset_evaluated": len(rows), "dataset_root": manifest.get("dataset_root")},
              "timestamp": datetime.now(timezone.utc).isoformat(), "seed": manifest.get("seed", 42),
              "hardware": {"gpu_name": "runtime dependent", "total_vram_mb": 0, "free_vram_mb": 0},
              "runtime": {"total_seconds": total_seconds, "average_per_sample_ms": round(total_seconds * 1000 / max(len(rows), 1), 2)},
              "aggregate_metrics": metrics, "sample_results": rows,
              "limitations": ["Scores are only valid for samples with supplied reference annotations.",
                              "A paired model result is not evidence of real-sensor calibration or benchmark generalization."]}
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run reference-scored VRSBench/CDVQA manifest evaluation.")
    parser.add_argument("manifest")
    parser.add_argument("--output", default="results/prescribed_benchmark_result.json")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    result = evaluate(args.manifest, args.output, args.limit)
    print(json.dumps(result["aggregate_metrics"], indent=2))
