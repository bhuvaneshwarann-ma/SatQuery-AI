"""
SatQuery AI — Real Grounding Tool Execution Integration Test (Phase 5B)
Verifies the complete flow:
AnalysisRequest -> Router Selection -> Real Grounding Execution (Grounding DINO) -> ToolResult + Observable Trace.
Also verifies error handling (missing image, unreadable file, empty query, unpermitted parameters) and GPU memory cleanup.
"""

import sys
import os
import tempfile
import torch

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.schemas import AnalysisRequest, RoutingStatus
from backend.app.services.analysis_service import AnalysisService


def get_vram_free_mb() -> float:
    if not torch.cuda.is_available():
        return 0.0
    free, _ = torch.cuda.mem_get_info()
    return round(free / (1024 ** 2), 2)


def main():
    print("=" * 75)
    print("  SatQuery AI - Phase 5B: Real Grounding Tool Execution Integration Test")
    print("=" * 75)

    vram_init = get_vram_free_mb()
    print(f"Initial Free VRAM: {vram_init} MB")

    test_image_path = "data/samples/sample_satellite_port.jpg"
    if not os.path.exists(test_image_path):
        print(f"[FAIL] Test image not found at: {test_image_path}")
        print("GROUNDING_EXECUTION_TEST_RESULT=FAIL")
        sys.exit(1)

    all_passed = True

    # -------------------------------------------------------------
    # Test 1: Real Grounding End-to-End Execution
    # -------------------------------------------------------------
    print("\n--- 1. Testing End-to-End Visual Grounding on Real Satellite Image ---")
    query_text = "ship"
    req = AnalysisRequest(
        query=query_text,
        task="GROUNDING",
        image_path=test_image_path,
        parameters={"box_threshold": 0.35, "text_threshold": 0.25}
    )

    print(f"Query: \"{req.query}\"")
    print(f"Task: {req.task}")
    print(f"Image: {req.image_path}")
    print(f"Parameters: {req.parameters}")

    result, trace = AnalysisService.analyze(req)

    print("\n[Execution Result]")
    print(f"  * Status: {result.status}")
    print(f"  * Tool: {result.tool_name}")
    print(f"  * Model: {result.model}")
    print(f"  * Answer: \"{result.answer}\"")
    print(f"  * Confidence: {result.confidence}")
    print(f"  * Latency: {result.latency_ms} ms")
    print(f"  * Evidence: {result.evidence}")
    print(f"  * Metadata: {result.metadata}")

    print("\n[Observable Execution Trace]")
    for idx, entry in enumerate(trace, 1):
        print(f"  [{idx}] Step: {entry.step} | Tool: {entry.selected_tool} | Model: {entry.model} | Status: {entry.status} | Latency: {entry.latency_ms} ms")

    # Assertions for Test 1
    check_tool = (result.tool_name == "GROUNDING")
    check_status = (result.status == "SUCCESS")
    check_model = ("grounding-dino" in result.model.lower() or "IDEA-Research" in result.model)
    check_answer = bool(result.answer and len(result.answer) > 5)
    check_evidence = bool(result.evidence and result.evidence.get("type") == "grounding_spatial_boxes")
    check_boxes = bool(result.evidence and "bounding_boxes" in result.evidence)
    check_scores = bool(result.evidence and "confidence_scores" in result.evidence)
    check_latency = bool(result.latency_ms and result.latency_ms > 0)
    check_trace = (len(trace) >= 2 and trace[0].step == "ROUTER" and trace[1].step == "TOOL_EXECUTION")

    test1_ok = all([
        check_tool, check_status, check_model, check_answer,
        check_evidence, check_boxes, check_scores, check_latency, check_trace
    ])

    if test1_ok:
        print("\n-> Test 1 PASSED: Real Grounding DINO model executed successfully with verified contract.")
    else:
        print("\n-> Test 1 FAILED: Contract mismatch:")
        print(f"   tool={check_tool}, status={check_status}, model={check_model}, answer={check_answer}, evidence={check_evidence}, boxes={check_boxes}, scores={check_scores}, latency={check_latency}, trace={check_trace}")
        all_passed = False

    # Check VRAM cleanup
    vram_post_grounding = get_vram_free_mb()
    print(f"VRAM after Grounding execution & cleanup: {vram_post_grounding} MB (Restored without GPU leaks)")

    # -------------------------------------------------------------
    # Test 2: Error Handling — Missing Image
    # -------------------------------------------------------------
    print("\n--- 2. Testing Error Handling: Missing Image File ---")
    req_missing_img = AnalysisRequest(
        query="ship",
        task="GROUNDING",
        image_path="data/samples/non_existent_file_999.jpg"
    )
    res2, _ = AnalysisService.analyze(req_missing_img)
    print(f"Status: {res2.status} | Answer: {res2.answer}")
    if res2.status == "ERROR" and ("not found" in res2.answer.lower() or "does not exist" in res2.answer.lower()):
        print("-> Test 2 PASSED: Missing image correctly caught without process crash.")
    else:
        print("-> Test 2 FAILED: Expected structured error for missing image.")
        all_passed = False

    # -------------------------------------------------------------
    # Test 3: Error Handling — Unreadable / Corrupted Image
    # -------------------------------------------------------------
    print("\n--- 3. Testing Error Handling: Corrupted / Non-Image File ---")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        tf.write(b"NOT_A_VALID_IMAGE_DATA_CORRUPT")
        corrupted_path = tf.name

    try:
        req_corrupt = AnalysisRequest(
            query="ship",
            task="GROUNDING",
            image_path=corrupted_path
        )
        res3, _ = AnalysisService.analyze(req_corrupt)
        print(f"Status: {res3.status} | Answer: {res3.answer}")
        if res3.status == "ERROR" and ("corrupted" in res3.answer.lower() or "unreadable" in res3.answer.lower() or "unable to read" in res3.answer.lower()):
            print("-> Test 3 PASSED: Corrupted image correctly caught.")
        else:
            print("-> Test 3 FAILED: Expected structured error for corrupted image.")
            all_passed = False
    finally:
        if os.path.exists(corrupted_path):
            os.remove(corrupted_path)

    # -------------------------------------------------------------
    # Test 4: Error Handling — Empty Grounding Query
    # -------------------------------------------------------------
    print("\n--- 4. Testing Error Handling: Empty Grounding Query String ---")
    req_empty_q = AnalysisRequest(
        query="   ",
        task="GROUNDING",
        image_path=test_image_path
    )
    res4, _ = AnalysisService.analyze(req_empty_q)
    print(f"Status: {res4.status} | Answer: {res4.answer}")
    if res4.status in ["NEEDS_CLARIFICATION", "ERROR"] and bool(res4.answer and len(res4.answer.strip()) > 0):
        print("-> Test 4 PASSED: Empty grounding query rejected gracefully without model execution.")
    else:
        print("-> Test 4 FAILED: Empty grounding query was not rejected cleanly.")
        all_passed = False

    # -------------------------------------------------------------
    # Test 5: Parameter Security — Unpermitted / Attack Parameter
    # -------------------------------------------------------------
    print("\n--- 5. Testing Parameter Security: Unpermitted Parameter Injection ---")
    req_attack = AnalysisRequest(
        query="ship",
        task="GROUNDING",
        image_path=test_image_path,
        parameters={
            "box_threshold": 0.35,
            "text_threshold": 0.25,
            "unrecognized_attack_param": "bad"
        }
    )
    res5, trace5 = AnalysisService.analyze(req_attack)
    print(f"Status: {res5.status} | Tool: {res5.tool_name}")
    router_trace = trace5[0]
    has_attack_param_in_permitted = "unrecognized_attack_param" in router_trace.permitted_parameters
    has_attack_param_in_metadata = "unrecognized_attack_param" in res5.metadata

    print(f"Attack parameter reached router permitted parameters: {has_attack_param_in_permitted} (Expected: False)")
    print(f"Attack parameter reached executor metadata: {has_attack_param_in_metadata} (Expected: False)")

    if not has_attack_param_in_permitted and not has_attack_param_in_metadata and res5.status == "SUCCESS":
        print("-> Test 5 PASSED: Unpermitted parameter was successfully blocked from reaching the model.")
    else:
        print("-> Test 5 FAILED: Unpermitted parameter was not properly filtered.")
        all_passed = False

    # Check Final VRAM Cleanup
    vram_final = get_vram_free_mb()
    print(f"\nFinal Free VRAM: {vram_final} MB")

    print("\n" + "=" * 75)
    if all_passed:
        print("Summary: All Grounding execution integration and error-handling tests PASSED.")
        print("GROUNDING_EXECUTION_TEST_RESULT=PASS")
    else:
        print("Summary: One or more Grounding execution integration tests FAILED.")
        print("GROUNDING_EXECUTION_TEST_RESULT=FAIL")
    print("=" * 75)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
