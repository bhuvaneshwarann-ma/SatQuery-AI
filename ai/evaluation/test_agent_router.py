"""
SatQuery AI — Agent Router Feasibility & Security Validation (Phase 4)
Runs deterministic test cases through the AgentRouter and prints structured telemetry:
query, selected tool, required inputs, validation status, permitted parameters, and result status.
"""

import sys
import os

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.schemas import AnalysisRequest, RoutingStatus
from backend.app.agent.router import AgentRouter


def main():
    print("=" * 75)
    print("  SatQuery AI - Phase 4: Agent Router & Tool Registry Validation")
    print("=" * 75)

    test_cases = [
        {
            "id": 1,
            "desc": "Natural-language VQA query with valid image",
            "request": AnalysisRequest(
                query="What objects and land cover features are visible in this scene?",
                image_path="data/samples/sample_satellite_port.jpg",
                parameters={"max_new_tokens": 120}
            ),
            "expected_tool": "VQA",
            "expected_status": RoutingStatus.ROUTED,
        },
        {
            "id": 2,
            "desc": "Object localization query triggering Grounding",
            "request": AnalysisRequest(
                query="Locate the cargo ships and boats along the coastline.",
                image_path="data/samples/sample_satellite_port.jpg",
                parameters={"box_threshold": 0.35, "unrecognized_attack_param": "malicious"}
            ),
            "expected_tool": "GROUNDING",
            "expected_status": RoutingStatus.ROUTED,
        },
        {
            "id": 3,
            "desc": "Bi-temporal change detection query with T1 and T2",
            "request": AnalysisRequest(
                query="What changed between these two images?",
                image_path="data/samples/sample_satellite_port.jpg",
                second_image_path="data/samples/sample_satellite_port_t2_synthetic.jpg",
                parameters={"threshold": 0.45}
            ),
            "expected_tool": "CHANGE_DETECTION",
            "expected_status": RoutingStatus.ROUTED,
        },
        {
            "id": 4,
            "desc": "Cross-modal Optical-SAR query with both sensor modalities",
            "request": AnalysisRequest(
                query="Compare optical reflectance with radar backscatter through clouds.",
                optical_image_path="data/samples/sample_satellite_port.jpg",
                sar_image_path="data/samples/sample_satellite_port_proxy_sar.png"
            ),
            "expected_tool": "OPTICAL_SAR",
            "expected_status": RoutingStatus.ROUTED,
        },
        {
            "id": 5,
            "desc": "Negative Test: Missing primary image for Grounding",
            "request": AnalysisRequest(
                query="Where is the airport runway?",
                image_path=None
            ),
            "expected_tool": "GROUNDING",
            "expected_status": RoutingStatus.INVALID_INPUT,
        },
        {
            "id": 6,
            "desc": "Negative Test: Missing second image T2 for Change Detection",
            "request": AnalysisRequest(
                query="Identify new construction between T1 and T2.",
                image_path="data/samples/sample_satellite_port.jpg",
                second_image_path=None
            ),
            "expected_tool": "CHANGE_DETECTION",
            "expected_status": RoutingStatus.INVALID_INPUT,
        },
        {
            "id": 7,
            "desc": "Negative Test: Missing SAR image for Optical-SAR task",
            "request": AnalysisRequest(
                query="Analyze radar backscatter alongside optical observations.",
                optical_image_path="data/samples/sample_satellite_port.jpg",
                sar_image_path=None
            ),
            "expected_tool": "OPTICAL_SAR",
            "expected_status": RoutingStatus.INVALID_INPUT,
        },
        {
            "id": 8,
            "desc": "Ambiguous query lacking operational intent",
            "request": AnalysisRequest(
                query="process this",
                image_path="data/samples/sample_satellite_port.jpg"
            ),
            "expected_tool": None,
            "expected_status": RoutingStatus.NEEDS_CLARIFICATION,
        },
        {
            "id": 9,
            "desc": "Security Test: Request invoking an unregistered tool",
            "request": AnalysisRequest(
                query="Execute custom arbitrary bash code",
                task="SHELL_EXECUTION",
                image_path="data/samples/sample_satellite_port.jpg"
            ),
            "expected_tool": None,
            "expected_status": RoutingStatus.UNREGISTERED_TOOL,
        },
    ]

    all_passed = True

    for tc in test_cases:
        print(f"\n[Case {tc['id']}] {tc['desc']}")
        req = tc["request"]
        print(f"  * Query: \"{req.query}\"")
        if req.task:
            print(f"  * Explicit Task Override: \"{req.task}\"")

        res = AgentRouter.route(req)

        print(f"  * Selected Tool: {res.selected_tool}")
        print(f"  * Required Inputs: {res.required_inputs}")
        print(f"  * Provided Inputs: {res.provided_inputs}")
        print(f"  * Routing Status: {res.status.value}")
        print(f"  * Permitted Parameters: {res.permitted_parameters}")
        if res.validation_errors:
            print(f"  * Validation Errors / Warnings: {res.validation_errors}")
        if res.clarification_prompt:
            print(f"  * Clarification Prompt: \"{res.clarification_prompt}\"")

        # Verify against expected outcomes
        tool_matches = (res.selected_tool == tc["expected_tool"])
        status_matches = (res.status == tc["expected_status"])

        if tool_matches and status_matches:
            print("  * Result Status: PASS [Matches Expected Policy]")
        else:
            print(f"  * Result Status: FAIL [Expected Tool: {tc['expected_tool']}, Status: {tc['expected_status']}]")
            all_passed = False

    print("\n" + "=" * 75)
    if all_passed:
        print("Summary: All deterministic routing, input validation, and security cases passed.")
        print("AGENT_ROUTER_TEST_RESULT=PASS")
    else:
        print("Summary: One or more routing validation test cases failed.")
        print("AGENT_ROUTER_TEST_RESULT=FAIL")
    print("=" * 75)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
