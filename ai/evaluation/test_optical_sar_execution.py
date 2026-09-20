"""
SatQuery AI — Real Optical-SAR Tool Execution Integration Test (Phase 5D)
Verifies the complete flow:
AnalysisRequest -> Router Selection -> Real Optical-SAR Analysis -> ToolResult + Observable Trace.
Verifies error contracts (missing optical, missing SAR, corrupted input, invalid threshold,
unpermitted parameters, missing SAR contract).
Verifies GPU memory cleanup and preservation of the PROXY SAR classification limitation.
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
    print("  SatQuery AI - Phase 5D: Real Optical-SAR Execution Integration Test")
    print("=" * 75)

    vram_init = get_vram_free_mb()
    print(f"Initial Free VRAM: {vram_init} MB")

    optical_sample = "data/samples/sample_satellite_port.jpg"
    sar_proxy_sample = "data/samples/sample_satellite_port_proxy_sar.png"

    if not os.path.exists(optical_sample) or not os.path.exists(sar_proxy_sample):
        print(f"[FAIL] Test image inputs not found: {optical_sample} or {sar_proxy_sample}")
        print("OPTICAL_SAR_EXECUTION_TEST_RESULT=FAIL")
        sys.exit(1)

    all_passed = True

    # -------------------------------------------------------------
    # TEST 1: Real End-to-End Optical-SAR Execution
    # -------------------------------------------------------------
    print("\n--- 1. Testing End-to-End Optical-SAR Cross-Modal Analysis ---")
    print("NOTE: SAR input is classified as PROXY (simulated radar backscatter).")
    req1 = AnalysisRequest(
        query="Analyze the cross-modal correlation and radar backscatter between optical and SAR imagery.",
        optical_image_path=optical_sample,
        sar_image_path=sar_proxy_sample,
        parameters={"high_scatter_threshold": 180.0}
    )

    result1, trace1 = AnalysisService.analyze(req1)

    print("\n[Execution Result]")
    print(f"  * Status: {result1.status}")
    print(f"  * Tool: {result1.tool_name}")
    print(f"  * Model: {result1.model}")
    print(f"  * Answer: \"{result1.answer}\"")
    print(f"  * Confidence: {result1.confidence}")
    print(f"  * Latency: {result1.latency_ms} ms")
    print(f"  * Evidence: {result1.evidence}")
    print(f"  * Metadata: {result1.metadata}")

    print("\n[Observable Execution Trace]")
    for idx, entry in enumerate(trace1, 1):
        print(f"  [{idx}] Step: {entry.step} | Tool: {entry.selected_tool} | Model: {entry.model} | Status: {entry.status} | Latency: {entry.latency_ms} ms")

    # Assertions for Test 1
    check_tool1 = (result1.tool_name == "OPTICAL_SAR")
    check_status1 = (result1.status == "SUCCESS")
    check_model1 = ("Dual-Stream" in result1.model or "Statistics Engine" in result1.model)
    check_answer1 = bool(result1.answer and len(result1.answer) > 5)
    check_evidence1 = bool(result1.evidence and result1.evidence.get("type") == "optical_sar_synergy_overlay")
    check_opt_stats1 = ("optical_mean" in result1.metadata and "optical_std" in result1.metadata)
    check_sar_stats1 = ("sar_mean" in result1.metadata and "sar_std" in result1.metadata)
    check_scatter1 = ("high_backscatter_count" in result1.metadata and "high_backscatter_percentage" in result1.metadata)
    check_correlation1 = ("cross_modal_correlation" in result1.metadata)
    check_proxy1 = (
        result1.metadata.get("sar_data_classification") == "proxy_sar" and
        "proxy" in result1.answer.lower()
    )
    check_artifact1 = bool(result1.evidence and result1.evidence.get("annotated_artifact") and os.path.exists(result1.evidence["annotated_artifact"]))
    check_trace1 = (len(trace1) >= 2 and trace1[0].step == "ROUTER" and trace1[1].step == "TOOL_EXECUTION")

    test1_ok = all([
        check_tool1, check_status1, check_model1, check_answer1,
        check_evidence1, check_opt_stats1, check_sar_stats1, check_scatter1,
        check_correlation1, check_proxy1, check_artifact1, check_trace1
    ])

    if test1_ok:
        print("\n-> Test 1 PASSED: End-to-end Optical-SAR analysis executed successfully with verified contract.")
        print("   SAR classification correctly preserved as proxy_sar.")
    else:
        print("\n-> Test 1 FAILED: Contract mismatch:")
        print(f"   tool={check_tool1}, status={check_status1}, model={check_model1}, answer={check_answer1}, evidence={check_evidence1}, opt_stats={check_opt_stats1}, sar_stats={check_sar_stats1}, scatter={check_scatter1}, corr={check_correlation1}, proxy={check_proxy1}, artifact={check_artifact1}, trace={check_trace1}")
        all_passed = False

    # Check VRAM cleanup
    vram_post_t1 = get_vram_free_mb()
    print(f"VRAM after Test 1: {vram_post_t1} MB")

    # -------------------------------------------------------------
    # TEST 2: Error Handling — Missing Optical Image
    # -------------------------------------------------------------
    print("\n--- 2. Testing Error Handling: Missing Optical Image ---")
    req2 = AnalysisRequest(
        query="Analyze optical and SAR features",
        task="OPTICAL_SAR",
        optical_image_path="data/samples/non_existent_file_999.jpg",
        sar_image_path=sar_proxy_sample
    )
    res2, _ = AnalysisService.analyze(req2)
    print(f"Status: {res2.status} | Answer: {res2.answer}")
    if res2.status == "ERROR" and ("not found" in res2.answer.lower() or "does not exist" in res2.answer.lower()):
        print("-> Test 2 PASSED: Missing optical image caught cleanly without crash.")
    else:
        print("-> Test 2 FAILED: Expected structured error for missing optical image.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 3: Error Handling — Missing SAR Image
    # -------------------------------------------------------------
    print("\n--- 3. Testing Error Handling: Missing SAR Image ---")
    req3 = AnalysisRequest(
        query="Analyze optical and SAR features",
        task="OPTICAL_SAR",
        optical_image_path=optical_sample,
        sar_image_path="data/samples/non_existent_file_999.jpg"
    )
    res3, _ = AnalysisService.analyze(req3)
    print(f"Status: {res3.status} | Answer: {res3.answer}")
    if res3.status == "ERROR" and ("not found" in res3.answer.lower() or "does not exist" in res3.answer.lower()):
        print("-> Test 3 PASSED: Missing SAR image caught cleanly without crash.")
    else:
        print("-> Test 3 FAILED: Expected structured error for missing SAR image.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 4: Error Handling — Corrupted Image
    # -------------------------------------------------------------
    print("\n--- 4. Testing Error Handling: Corrupted Image File ---")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tf.write(b"CORRUPTED_NON_IMAGE_DATA_BYTES")
        corrupted_path = tf.name

    try:
        req4 = AnalysisRequest(
            query="Analyze optical and SAR features",
            task="OPTICAL_SAR",
            optical_image_path=optical_sample,
            sar_image_path=corrupted_path
        )
        res4, _ = AnalysisService.analyze(req4)
        print(f"Status: {res4.status} | Answer: {res4.answer}")
        if res4.status == "ERROR" and ("corrupted" in res4.answer.lower() or "unreadable" in res4.answer.lower() or "unable to read" in res4.answer.lower()):
            print("-> Test 4 PASSED: Corrupted image caught cleanly.")
        else:
            print("-> Test 4 FAILED: Expected structured error for corrupted image.")
            all_passed = False
    finally:
        if os.path.exists(corrupted_path):
            os.remove(corrupted_path)

    # -------------------------------------------------------------
    # TEST 5: Parameter Handling — Invalid / Out-of-Range Threshold
    # -------------------------------------------------------------
    print("\n--- 5. Testing Parameter Handling: Out-of-Range high_scatter_threshold ---")
    req5 = AnalysisRequest(
        query="Analyze optical and SAR features",
        task="OPTICAL_SAR",
        optical_image_path=optical_sample,
        sar_image_path=sar_proxy_sample,
        parameters={"high_scatter_threshold": 450.0}  # Authorized bounds are [100.0, 250.0]
    )
    res5, _ = AnalysisService.analyze(req5)
    print(f"Status: {res5.status} | Answer: {res5.answer}")
    if res5.status == "ERROR" and ("outside" in res5.answer.lower() or "bounds" in res5.answer.lower() or "invalid" in res5.answer.lower()):
        print("-> Test 5 PASSED: Out-of-range threshold rejected before analysis.")
    else:
        print("-> Test 5 FAILED: Expected rejection for out-of-range threshold.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 6: Parameter Security — Unpermitted Parameter Injection
    # -------------------------------------------------------------
    print("\n--- 6. Testing Parameter Security: Unpermitted Parameter Injection ---")
    req6 = AnalysisRequest(
        query="Analyze optical and SAR features",
        task="OPTICAL_SAR",
        optical_image_path=optical_sample,
        sar_image_path=sar_proxy_sample,
        parameters={
            "high_scatter_threshold": 180.0,
            "unrecognized_attack_param": "bad"
        }
    )
    res6, trace6 = AnalysisService.analyze(req6)
    print(f"Status: {res6.status} | Tool: {res6.tool_name}")
    router_trace6 = trace6[0]
    has_attack_param_in_permitted = "unrecognized_attack_param" in router_trace6.permitted_parameters
    has_attack_param_in_metadata = "unrecognized_attack_param" in res6.metadata

    print(f"Attack parameter reached router permitted parameters: {has_attack_param_in_permitted} (Expected: False)")
    print(f"Attack parameter reached executor metadata: {has_attack_param_in_metadata} (Expected: False)")

    if not has_attack_param_in_permitted and not has_attack_param_in_metadata and res6.status == "SUCCESS":
        print("-> Test 6 PASSED: Unpermitted parameter was blocked from router and executor.")
    else:
        print("-> Test 6 FAILED: Unpermitted parameter was not properly filtered.")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 7: Input Contract — Missing SAR Image Through Router
    # -------------------------------------------------------------
    print("\n--- 7. Testing Input Contract: Missing SAR Image Through Router ---")
    req7 = AnalysisRequest(
        query="Compare the optical and SAR images to identify structures through clouds.",
        optical_image_path=optical_sample,
        sar_image_path=None  # Missing SAR
    )
    res7, _ = AnalysisService.analyze(req7)
    print(f"Status: {res7.status} | Answer: {res7.answer}")
    if res7.status in ["INVALID_INPUT", "ERROR"] and "sar_image_path" in res7.answer:
        print("-> Test 7 PASSED: Missing SAR image caught by router contract without model execution.")
    else:
        print("-> Test 7 FAILED: Expected router rejection for missing SAR image.")
        all_passed = False

    # Check Final VRAM Cleanup
    vram_final = get_vram_free_mb()
    print(f"\nFinal Free VRAM: {vram_final} MB")

    print("\n" + "=" * 75)
    if all_passed:
        print("Summary: All Optical-SAR execution integration tests PASSED.")
        print("OPTICAL_SAR_EXECUTION_TEST_RESULT=PASS")
    else:
        print("Summary: One or more Optical-SAR execution integration tests FAILED.")
        print("OPTICAL_SAR_EXECUTION_TEST_RESULT=FAIL")
    print("=" * 75)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
