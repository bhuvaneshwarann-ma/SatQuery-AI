"""Reproduce the five SIH representative-query demonstrations.

Default mode validates input slots and routing without loading models. Pass
--run-models to execute the actual specialists; this may take several minutes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.app.agent.router import AgentRouter
from backend.app.agent.schemas import AnalysisRequest

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = str(ROOT / "data/samples/sample_satellite_port.jpg")
TEMPORAL = str(ROOT / "data/samples/sample_satellite_port_t2_synthetic.jpg")
SAR = str(ROOT / "data/samples/sample_satellite_port_proxy_sar.png")

CASES = [
    ("Describe the land-cover and major objects visible in this image.", {}),
    ("Highlight the water body referred to in the query.", {}),
    ("What changed between these two dates, and where did the change occur?", {"second_image_path": TEMPORAL}),
    ("Use the optical and SAR images together to identify built-up and water-covered regions.", {"sar_image_path": SAR}),
    ("Has the built-up area increased, decreased, or remained unchanged?", {"second_image_path": TEMPORAL}),
]


def main(run_models: bool):
    for query, extra in CASES:
        request = AnalysisRequest(query=query, image_path=PRIMARY, **extra)
        selection = AgentRouter.route(request)
        record = {"query": query, "status": selection.status.value,
                  "selected_tool": selection.selected_tool,
                  "task_plan": selection.task_plan.to_dict() if selection.task_plan else None,
                  "validation_errors": selection.validation_errors}
        if run_models and selection.status.value == "ROUTED":
            from backend.app.services.orchestration_service import execute_agent_request
            record["result"] = execute_agent_request(request).to_dict()
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-models", action="store_true")
    main(parser.parse_args().run_models)
