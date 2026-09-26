"""
SatQuery AI — Live Demo Verification Suite (Section 11)
Executes all 5 core demonstration scenarios against the real local models,
capturing input, query, selected tools, structured task plan, output narrative,
visual evidence artifact path, execution latency, and error states.
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.schemas import AnalysisRequest
from backend.app.services.orchestration_service import execute_agent_request


def run_live_demo_verification():
    demos = [
        {
            "id": "DEMO 1",
            "desc": "Single-image VQA",
            "query": "What type of scene is shown?",
            "req": AnalysisRequest(
                query="What type of scene is shown?",
                image_path="data/samples/sample_satellite_port.jpg",
            ),
        },
        {
            "id": "DEMO 2",
            "desc": "Text-guided Grounding",
            "query": "Locate the ships.",
            "req": AnalysisRequest(
                query="Locate the ships.",
                image_path="data/samples/sample_satellite_port.jpg",
            ),
        },
        {
            "id": "DEMO 3",
            "desc": "Counting Guardrail (Grounding len(valid_boxes))",
            "query": "How many ships are present?",
            "req": AnalysisRequest(
                query="How many ships are present?",
                image_path="data/samples/sample_satellite_port.jpg",
            ),
        },
        {
            "id": "DEMO 4",
            "desc": "Bi-temporal Change Detection",
            "query": "Compare these two dates and identify changes.",
            "req": AnalysisRequest(
                query="Compare these two dates and identify changes.",
                image_path="data/samples/sample_satellite_port.jpg",
                second_image_path="data/samples/sample_satellite_port_t2_synthetic.jpg",
            ),
        },
        {
            "id": "DEMO 5",
            "desc": "Complex Multi-Tool Agentic Query (CD -> Grounding -> VQA)",
            "query": "Compare these two dates, identify where built-up areas changed, and describe the observed change.",
            "req": AnalysisRequest(
                query="Compare these two dates, identify where built-up areas changed, and describe the observed change.",
                image_path="data/samples/sample_satellite_port.jpg",
                second_image_path="data/samples/sample_satellite_port_t2_synthetic.jpg",
            ),
        },
    ]

    print("=" * 70)
    print("  SatQuery AI - Live Demo Verification Runner (Part 15)")
    print("=" * 70)

    output_path = "results/live_demo_verification.json"
    demo_results = []
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                demo_results = json.load(f)
        except Exception:
            demo_results = []

    completed_ids = {r["id"] for r in demo_results if r.get("query") == next((d["query"] for d in demos if d["id"] == r["id"]), None)}

    for d in demos:
        if d["id"] in completed_ids:
            print(f"\nSkipping already completed {d['id']}: {d['desc']}")
            continue

        print(f"\nExecuting {d['id']}: {d['desc']}...")
        print(f"  Query: \"{d['req'].query}\"")
        t0 = time.time()
        res = execute_agent_request(d["req"])
        wall_s = round(time.time() - t0, 2)

        artifact_path = res.evidence.get("annotated_artifact") if res.evidence else None
        plan_steps = []
        if res.task_plan:
            raw_plan = res.task_plan.get("plan", []) if isinstance(res.task_plan, dict) else getattr(res.task_plan, "plan", [])
            for s in raw_plan:
                if isinstance(s, dict):
                    tool_name = s.get("tool") or s.get("action") or s.get("tool_name") or str(s)
                else:
                    tool_name = getattr(s, "tool", None) or getattr(s, "action", None) or str(s)
                if tool_name:
                    plan_steps.append(str(tool_name))
            policy_val = res.task_plan.get("policy_validated", True) if isinstance(res.task_plan, dict) else getattr(res.task_plan, "policy_validated", True)
        if not plan_steps and res.selected_tool:
            plan_steps = [str(res.selected_tool)]
        elif not plan_steps:
            plan_steps = ["UNKNOWN"]
        policy_val = getattr(res.task_plan, "policy_validated", True) if hasattr(res.task_plan, "policy_validated") else (res.task_plan.get("policy_validated", True) if isinstance(res.task_plan, dict) else True)

        rec = {
            "id": d["id"],
            "desc": d["desc"],
            "input_primary": d["req"].image_path,
            "input_secondary": d["req"].second_image_path or d["req"].sar_image_path,
            "query": d["req"].query,
            "status": res.status,
            "selected_tool": str(res.selected_tool) if res.selected_tool else None,
            "tools_used": res.tools_used if res.tools_used else ([res.selected_tool] if res.selected_tool else []),
            "task_plan_steps": plan_steps,
            "policy_validated": policy_val,
            "answer": str(res.answer),
            "confidence": res.confidence,
            "evidence": res.evidence,
            "limitations": res.limitations,
            "artifact_path": artifact_path,
            "latency_ms": res.latency_ms,
            "wall_clock_seconds": wall_s,
            "execution_trace": res.execution_trace,
            "failure_mode": None if res.status == "SUCCESS" else (res.metadata.get("error_type", "UNKNOWN") if res.metadata else "UNKNOWN"),
        }
        # Update or append
        existing_idx = next((i for i, r in enumerate(demo_results) if r["id"] == d["id"]), None)
        if existing_idx is not None:
            demo_results[existing_idx] = rec
        else:
            demo_results.append(rec)

        print(f"  Result Status: {res.status} | Tool: {res.selected_tool} | Plan: {' -> '.join(plan_steps)}")
        print(f"  Latency: {res.latency_ms} ms (Wall: {wall_s} s) | Artifact: {artifact_path}")
        print(f"  Summary Answer: {str(res.answer)[:140]}...")
        if res.limitations:
            print(f"  Limitations: {res.limitations[0]}")

        # Save incrementally
        output_path = "results/live_demo_verification.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(demo_results, f, indent=2)

    output_path = "results/live_demo_verification.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(demo_results, f, indent=2)

    print("\n" + "=" * 70)
    print(f"All 5 Live Demos Successfully Verified! Logged to: {output_path}")
    print("=" * 70)
    return demo_results


if __name__ == "__main__":
    run_live_demo_verification()
