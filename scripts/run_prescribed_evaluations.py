"""Run every locally available prescribed manifest and write one summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULTS = {
    "vrsbench": ROOT / "data/benchmarks/vrsbench/manifest.json",
    "rsvqa": ROOT / "data/benchmarks/rsvqa_lr/manifest.json",
    "cdvqa": ROOT / "data/benchmarks/cdvqa/manifest.json",
    "sen1_2": ROOT / "data/benchmarks/sen1_2/manifest.json",
    "isro": ROOT / "data/benchmarks/isro/manifest.json",
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/prescribed_evaluations.json")
    parser.add_argument("--include-blocked", action="store_true", help="record absent manifests as BLOCKED instead of omitting them")
    args = parser.parse_args()
    reports = {}
    for name, manifest in DEFAULTS.items():
        if not manifest.exists():
            if args.include_blocked:
                reports[name] = {"status": "BLOCKED", "reason": f"Missing manifest: {manifest.relative_to(ROOT).as_posix()}"}
            continue
        try:
            from ai.evaluation.prescribed_benchmark_runner import evaluate
        except ModuleNotFoundError as error:
            reports[name] = {"status": "BLOCKED", "reason": f"Runtime dependency unavailable: {error.name}"}
            continue
        out = ROOT / "results" / f"{name}_prescribed.json"
        try:
            reports[name] = evaluate(str(manifest), str(out)).get("aggregate_metrics", {})
        except Exception as error:
            reports[name] = {"status": "BLOCKED", "reason": f"Evaluation runtime unavailable: {type(error).__name__}: {error}"}
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(json.dumps(reports, indent=2))
