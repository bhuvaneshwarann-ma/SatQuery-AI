"""
SatQuery AI — End-to-End Agent Orchestration Test (Phase 6)
Validates the unified execution pipeline across all four specialist remote-sensing capabilities:
USER REQUEST -> INPUT VALIDATION -> AGENT ROUTER -> AUTHORIZED TOOL SELECTION
-> AUTHORIZED PARAMETERS -> TOOL EXECUTION -> EVIDENCE -> OBSERVABLE EXECUTION TRACE
-> FINAL STRUCTURED RESULT.
Evaluates functional execution, ambiguity handling, security boundaries, and GPU VRAM management.
"""

import sys
import os
import torch

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.schemas import AnalysisRequest
from backend.app.services.orchestration_service import execute_agent_request


def get_vram_free_mb() -> float:
    if not torch.cuda.is_available():
        return 0.0
    free, _ = torch.cuda.mem_get_info()
    return round(free / (1024 ** 2), 2)


def main():
    print("=" * 80)
    print("  SatQuery AI - Phase 6: End-to-End Agent Orchestration Integration Test")
    print("=" * 80)

    vram_init = get_vram_free_mb()
    print(f"Initial Free VRAM: {vram_init} MB")

    optical_sample = "data/samples/sample_satellite_port.jpg"
    t2_synthetic_sample = "data/samples/sample_satellite_port_t2_synthetic.jpg"
    sar_proxy_sample = "data/samples/sample_satellite_port_proxy_sar.png"

    all_passed = True

    # -------------------------------------------------------------
    # TEST 1: VQA Orchestration
    # -------------------------------------------------------------
    print("\n--- TEST 1: VQA End-to-End Orchestration ---")
    req1 = AnalysisRequest(
        query="What major objects or structures are visibly present in this satellite image?",
        image_path=optical_sample,
        parameters={"max_new_tokens": 100}
    )
    res1 = execute_agent_request(req1)
    print(f"Tool: {res1.selected_tool} | Model: {res1.model} | Status: {res1.status}")
    print(f"Answer: {res1.answer[:120]}...")
    print(f"Latency: {res1.latency_ms} ms | Trace Steps: {len(res1.observable_execution_trace)}")

    test1_ok = (
        res1.status == "SUCCESS" and
        res1.selected_tool == "VQA" and
        ("Qwen2.5-VL" in res1.model or "AdaptLLM" in res1.model) and
        bool(res1.evidence and res1.evidence.get("type") == "vqa_spatial_metadata") and
        len(res1.observable_execution_trace) >= 4
    )
    if test1_ok:
        print("-> TEST 1 PASSED: VQA orchestrated successfully with verified evidence and trace.")
    else:
        print("-> TEST 1 FAILED: Contract mismatch on VQA orchestration.")
        all_passed = False

    vram_t1 = get_vram_free_mb()
    print(f"VRAM after Test 1: {vram_t1} MB")

    # -------------------------------------------------------------
    # TEST 2: Grounding Orchestration
    # -------------------------------------------------------------
    print("\n--- TEST 2: Grounding End-to-End Orchestration ---")
    req2 = AnalysisRequest(
        query="Locate the ships in this satellite image.",
        image_path=optical_sample,
        parameters={"box_threshold": 0.35, "text_threshold": 0.25}
    )
    res2 = execute_agent_request(req2)
    print(f"Tool: {res2.selected_tool} | Model: {res2.model} | Status: {res2.status}")
    print(f"Answer: {res2.answer}")
    print(f"Confidence: {res2.confidence} | Latency: {res2.latency_ms} ms")

    test2_ok = (
        res2.status == "SUCCESS" and
        res2.selected_tool == "GROUNDING" and
        ("grounding-dino" in res2.model.lower() or "IDEA-Research" in res2.model) and
        bool(res2.evidence and "bounding_boxes" in res2.evidence) and
        len(res2.observable_execution_trace) >= 4
    )
    if test2_ok:
        print("-> TEST 2 PASSED: Grounding orchestrated successfully with spatial box evidence.")
    else:
        print("-> TEST 2 FAILED: Contract mismatch on Grounding orchestration.")
        all_passed = False

    vram_t2 = get_vram_free_mb()
    print(f"VRAM after Test 2: {vram_t2} MB")

    # -------------------------------------------------------------
    # TEST 3: Change Detection Orchestration
    # -------------------------------------------------------------
    print("\n--- TEST 3: Change Detection End-to-End Orchestration ---")
    print("NOTE: T2 is a controlled synthetic temporal pair.")
    req3 = AnalysisRequest(
        query="What changed between these two satellite images?",
        image_path=optical_sample,
        second_image_path=t2_synthetic_sample,
        parameters={"threshold": 0.42}
    )
    res3 = execute_agent_request(req3)
    print(f"Tool: {res3.selected_tool} | Model: {res3.model} | Status: {res3.status}")
    print(f"Answer: {res3.answer}")
    print(f"Latency: {res3.latency_ms} ms")

    test3_ok = (
        res3.status == "SUCCESS" and
        res3.selected_tool == "CHANGE_DETECTION" and
        ("Siamese-ResNet18" in res3.model or "FeatureDifferencer" in res3.model) and
        bool(res3.evidence and res3.evidence.get("type") == "differential_heatmap_mask_composite") and
        "changed_pixels" in res3.metadata and
        "synthetic" in res3.answer.lower() and
        len(res3.observable_execution_trace) >= 4
    )
    if test3_ok:
        print("-> TEST 3 PASSED: Change detection orchestrated successfully with synthetic pair note preserved.")
    else:
        print("-> TEST 3 FAILED: Contract mismatch on Change Detection orchestration.")
        all_passed = False

    vram_t3 = get_vram_free_mb()
    print(f"VRAM after Test 3: {vram_t3} MB")

    # -------------------------------------------------------------
    # TEST 4: Optical-SAR Orchestration
    # -------------------------------------------------------------
    print("\n--- TEST 4: Optical-SAR End-to-End Orchestration ---")
    print("NOTE: SAR input is classified as proxy_sar.")
    req4 = AnalysisRequest(
        query="Analyze these optical and SAR images together.",
        optical_image_path=optical_sample,
        sar_image_path=sar_proxy_sample,
        parameters={"high_scatter_threshold": 180.0}
    )
    res4 = execute_agent_request(req4)
    print(f"Tool: {res4.selected_tool} | Model: {res4.model} | Status: {res4.status}")
    print(f"Answer: {res4.answer}")
    print(f"Latency: {res4.latency_ms} ms")

    test4_ok = (
        res4.status == "SUCCESS" and
        res4.selected_tool == "OPTICAL_SAR" and
        ("Dual-Stream" in res4.model or "Statistics Engine" in res4.model) and
        bool(res4.evidence and res4.evidence.get("type") == "optical_sar_synergy_overlay") and
        res4.metadata.get("sar_data_classification") == "proxy_sar" and
        "proxy" in res4.answer.lower() and
        len(res4.observable_execution_trace) >= 4
    )
    if test4_ok:
        print("-> TEST 4 PASSED: Optical-SAR orchestrated successfully with proxy_sar classification preserved.")
    else:
        print("-> TEST 4 FAILED: Contract mismatch on Optical-SAR orchestration.")
        all_passed = False

    vram_t4 = get_vram_free_mb()
    print(f"VRAM after Test 4: {vram_t4} MB")

    # -------------------------------------------------------------
    # TEST 5: Ambiguous Request Handling
    # -------------------------------------------------------------
    print("\n--- TEST 5: Ambiguous Query Clarification ---")
    req5 = AnalysisRequest(
        query="process this",
        image_path=optical_sample
    )
    res5 = execute_agent_request(req5)
    print(f"Status: {res5.status} | Error Type: {res5.error_type}")
    print(f"Answer: {res5.answer}")

    test5_ok = (
        res5.status == "NEEDS_CLARIFICATION" and
        res5.selected_tool is None and
        bool(res5.answer and len(res5.answer) > 10) and
        res5.metadata.get("clarification_prompt") is not None and
        len(res5.metadata.get("supported_objectives", [])) == 4
    )
    if test5_ok:
        print("-> TEST 5 PASSED: Ambiguous query returned clarification prompt with 4 supported objectives without model execution.")
    else:
        print("-> TEST 5 FAILED: Expected NEEDS_CLARIFICATION for ambiguous query.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 6: Missing Asset Handling (Pre-Execution Validation)
    # -------------------------------------------------------------
    print("\n--- TEST 6: Missing Asset File Pre-Execution Validation ---")
    req6 = AnalysisRequest(
        query="What is visible in this satellite image?",
        image_path="data/samples/non_existent_file_999.jpg"
    )
    res6 = execute_agent_request(req6)
    print(f"Status: {res6.status} | Error Type: {res6.error_type}")
    print(f"Answer: {res6.answer}")

    test6_ok = (
        res6.status == "ERROR" and
        res6.error_type == "IMAGE_NOT_FOUND" and
        "does not exist" in res6.answer.lower()
    )
    if test6_ok:
        print("-> TEST 6 PASSED: Missing asset caught at input validation stage without invoking heavy model.")
    else:
        print("-> TEST 6 FAILED: Expected pre-execution rejection for missing asset.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 7: Input Contract — Missing T2 for Change Detection
    # -------------------------------------------------------------
    print("\n--- TEST 7: Input Contract — Missing Second Image T2 ---")
    req7 = AnalysisRequest(
        query="What changed between these two satellite images?",
        image_path=optical_sample,
        second_image_path=None
    )
    res7 = execute_agent_request(req7)
    print(f"Status: {res7.status} | Error Type: {res7.error_type}")
    print(f"Answer: {res7.answer}")

    test7_ok = (
        res7.status == "INVALID_INPUT" and
        "second_image_path" in res7.answer
    )
    if test7_ok:
        print("-> TEST 7 PASSED: Missing second image T2 rejected by router contract without model execution.")
    else:
        print("-> TEST 7 FAILED: Expected INVALID_INPUT for missing T2.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 8: Input Contract — Missing SAR Image for Optical-SAR
    # -------------------------------------------------------------
    print("\n--- TEST 8: Input Contract — Missing SAR Image ---")
    req8 = AnalysisRequest(
        query="Analyze these optical and SAR images together.",
        optical_image_path=optical_sample,
        sar_image_path=None
    )
    res8 = execute_agent_request(req8)
    print(f"Status: {res8.status} | Error Type: {res8.error_type}")
    print(f"Answer: {res8.answer}")

    test8_ok = (
        res8.status == "INVALID_INPUT" and
        "sar_image_path" in res8.answer
    )
    if test8_ok:
        print("-> TEST 8 PASSED: Missing SAR image rejected by router contract without model execution.")
    else:
        print("-> TEST 8 FAILED: Expected INVALID_INPUT for missing SAR image.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 9: Security — Unregistered Tool Invocation
    # -------------------------------------------------------------
    print("\n--- TEST 9: Security — Unregistered Tool Invocation ---")
    req9 = AnalysisRequest(
        query="Execute arbitrary system commands",
        task="SHELL_EXECUTION",
        image_path=optical_sample
    )
    res9 = execute_agent_request(req9)
    print(f"Status: {res9.status} | Error Type: {res9.error_type}")
    print(f"Answer: {res9.answer}")

    test9_ok = (
        res9.status == "UNREGISTERED_TOOL" and
        res9.selected_tool is None and
        "SHELL_EXECUTION" in res9.answer
    )
    if test9_ok:
        print("-> TEST 9 PASSED: Unregistered tool request rejected cleanly without executing arbitrary code.")
    else:
        print("-> TEST 9 FAILED: Expected UNREGISTERED_TOOL rejection.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 10: Security — Parameter Injection Firewall
    # -------------------------------------------------------------
    print("\n--- TEST 10: Security — Unpermitted Parameter Firewall ---")
    req10 = AnalysisRequest(
        query="What major objects or structures are visibly present in this satellite image?",
        image_path=optical_sample,
        parameters={
            "max_new_tokens": 100,
            "unrecognized_attack_param": "bad"
        }
    )
    res10 = execute_agent_request(req10)
    print(f"Status: {res10.status} | Selected Tool: {res10.selected_tool} | Error Type: {res10.error_type}")
    print(f"Answer: {res10.answer}")
    print(f"Latency: {res10.latency_ms} ms (Pre-model rejection)")

    router_trace_entry = next((e for e in res10.observable_execution_trace if e.get("step") == "ROUTER"), {})
    permitted_in_router = "unrecognized_attack_param" in router_trace_entry.get("permitted_parameters", {})
    in_metadata = "unrecognized_attack_param" in res10.metadata
    tool_execution_occurred = any(e.get("step") == "TOOL_EXECUTION" for e in res10.observable_execution_trace)

    print(f"Authorized tool recognized: {res10.selected_tool} (Expected: VQA)")
    print(f"Attack param in router permitted parameters: {permitted_in_router} (Expected: False)")
    print(f"Attack param in execution metadata: {in_metadata} (Expected: False)")
    print(f"Model execution occurred: {tool_execution_occurred} (Expected: False)")

    test10_ok = (
        res10.selected_tool == "VQA" and
        res10.status in ["INVALID_INPUT", "ERROR"] and
        not permitted_in_router and
        not in_metadata and
        not tool_execution_occurred and
        res10.latency_ms < 500.0
    )
    if test10_ok:
        print("-> TEST 10 PASSED: Unpermitted parameter rejected before model execution.")
    else:
        print("-> TEST 10 FAILED: Unpermitted parameter was not rejected prior to model execution.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 11: Unsupported / Unclear Request (No Guessing)
    # -------------------------------------------------------------
    print("\n--- TEST 11: Unsupported / Unclear Intent Handling (Do Not Guess) ---")
    req11 = AnalysisRequest(
        query="calculate the orbital trajectory of asteroid 99942 through space",
        image_path=optical_sample
    )
    res11 = execute_agent_request(req11)
    print(f"Status: {res11.status} | Error Type: {res11.error_type}")
    print(f"Answer: {res11.answer}")

    test11_ok = (
        res11.status == "NEEDS_CLARIFICATION" and
        res11.selected_tool is None and
        bool(res11.answer and len(res11.answer) > 10)
    )
    if test11_ok:
        print("-> TEST 11 PASSED: Unsupported query returned NEEDS_CLARIFICATION without guessing a specialist tool.")
    else:
        print("-> TEST 11 FAILED: Expected NEEDS_CLARIFICATION without guessing.")
        all_passed = False

    # Final Hardware / VRAM Telemetry
    vram_final = get_vram_free_mb()
    print("\n" + "=" * 80)
    print(f"Hardware VRAM Telemetry:")
    print(f"  * Initial Free VRAM:    {vram_init} MB")
    print(f"  * Free VRAM after runs: {vram_t4} MB")
    print(f"  * Final Free VRAM:      {vram_final} MB")
    print("=" * 80)

    if all_passed:
        print("\nSummary: All 11 Phase 6 Agent Orchestration integration tests PASSED.")
        print("AGENT_ORCHESTRATION_TEST_RESULT=PASS")
    else:
        print("\nSummary: One or more Phase 6 Agent Orchestration integration tests FAILED.")
        print("AGENT_ORCHESTRATION_TEST_RESULT=FAIL")
    print("=" * 80)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
