"""
SatQuery AI — API Contract Hardening Evaluation (Phase 7B)
Verifies that the live FastAPI /api/analyze endpoint correctly exposes ALL FOUR
validated analytical tools, validates the API parameter firewall, unsupported query handling,
health telemetry, and tools registry schemas.

Tests:
- Test 1: VQA (AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct)
- Test 2: Grounding (IDEA-Research/grounding-dino-tiny)
- Test 3: Change Detection (Siamese-ResNet18-FeatureDifferencer)
- Test 4: Optical-SAR (Dual-Stream Cross-Modal Engine)
- Test 5: Parameter Firewall Through API (Security injection rejection)
- Test 6: Unsupported Query (calculate orbital trajectory -> NEEDS_CLARIFICATION)
- Test 7: Health Endpoint (GET /api/health)
- Test 8: Tools Registry Endpoint (GET /api/tools)

Outputs:
API_CONTRACT_TEST_RESULT=PASS or FAIL
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, Tuple, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Sample assets
OPTICAL_SAMPLE = os.path.join(PROJECT_ROOT, "data/samples/sample_satellite_port.jpg")
T2_SYNTHETIC_SAMPLE = os.path.join(PROJECT_ROOT, "data/samples/sample_satellite_port_t2_synthetic.jpg")
SAR_PROXY_SAMPLE = os.path.join(PROJECT_ROOT, "data/samples/sample_satellite_port_proxy_sar.png")


def check_server(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/api/health", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


def get_health_telemetry(base_url: str) -> Dict[str, Any]:
    try:
        r = requests.get(f"{base_url}/api/health", timeout=5.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"free_vram_mb": 0.0, "total_vram_mb": 0.0, "gpu_name": "Unknown"}


def main():
    print("=" * 80)
    print("  SatQuery AI — Phase 7B: API Contract Hardening Evaluation")
    print("=" * 80)
    print(f"Target Server: {DEFAULT_BASE_URL}")

    if not check_server(DEFAULT_BASE_URL):
        print(f"ERROR: Live server is not responding at {DEFAULT_BASE_URL}.")
        print("Please start the server: python -m uvicorn backend.app.main:app --port 8000")
        print("\nAPI_CONTRACT_TEST_RESULT=FAIL")
        sys.exit(1)

    init_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
    print(f"Initial GPU Device : {init_telemetry.get('gpu_name')}")
    print(f"Initial Free VRAM  : {init_telemetry.get('free_vram_mb')} MB / {init_telemetry.get('total_vram_mb')} MB")
    print(f"Registered Tools   : {init_telemetry.get('registered_tools')}")

    results = {}
    vram_log = {}
    latencies = {}
    all_passed = True

    # -------------------------------------------------------------
    # Test 7: Health Endpoint (Run early for telemetry baseline)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 7] Health Endpoint (GET /api/health) ---")
    t0 = time.perf_counter()
    try:
        r = requests.get(f"{DEFAULT_BASE_URL}/api/health", timeout=5.0)
        dur = round((time.perf_counter() - t0) * 1000, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        h_data = r.json()
        assert h_data.get("status") == "healthy", f"Expected status='healthy', got {h_data.get('status')}"
        assert h_data.get("gpu_available") is True, "GPU availability flag is False"
        assert h_data.get("gpu_name"), "GPU name is empty"
        assert "free_vram_mb" in h_data and "total_vram_mb" in h_data, "Missing VRAM metrics"
        assert len(h_data.get("registered_tools", [])) == 4, f"Expected 4 tools, got {h_data.get('registered_tools')}"

        print(f"PASS: Health check responded with {h_data['status']} ({dur} ms)")
        print(f"      GPU Name       : {h_data.get('gpu_name')}")
        print(f"      Free / Total   : {h_data.get('free_vram_mb')} MB / {h_data.get('total_vram_mb')} MB")
        print(f"      Registered     : {h_data.get('registered_tools')}")
        results["Test 7 (Health)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 7]: {e}")
        results["Test 7 (Health)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 8: Tools Registry Endpoint (GET /api/tools)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 8] Tools Registry Catalog (GET /api/tools) ---")
    t0 = time.perf_counter()
    try:
        r = requests.get(f"{DEFAULT_BASE_URL}/api/tools", timeout=5.0)
        dur = round((time.perf_counter() - t0) * 1000, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        tools_list = r.json()
        assert isinstance(tools_list, list), "Expected list of tool definitions"
        assert len(tools_list) == 4, f"Expected 4 tool definitions, got {len(tools_list)}"

        tool_names = [t.get("tool_name") for t in tools_list]
        for required_tool in ["VQA", "GROUNDING", "CHANGE_DETECTION", "OPTICAL_SAR"]:
            assert required_tool in tool_names, f"Tool '{required_tool}' missing from registry"

        # Verify parameter schema exposure
        for t in tools_list:
            t_name = t["tool_name"]
            assert t.get("model_or_engine"), f"Tool {t_name} missing model_or_engine"
            assert "permitted_parameters" in t, f"Tool {t_name} missing permitted_parameters"
            print(f"      Tool: {t_name:<18} | Model: {t.get('model_or_engine')}")
            for p_name, p_spec in t["permitted_parameters"].items():
                print(f"        - Param '{p_name}': type={p_spec.get('type')}, default={p_spec.get('default')}, range=[{p_spec.get('min_value')}, {p_spec.get('max_value')}]")

        print(f"PASS: Tools registry catalog fully exposes all 4 tools and schemas ({dur} ms).")
        results["Test 8 (Tools Registry)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 8]: {e}")
        results["Test 8 (Tools Registry)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 5: Parameter Firewall Through API
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 5] Parameter Firewall Enforcement (POST /api/analyze) ---")
    t0 = time.perf_counter()
    try:
        injection_payload = json.dumps({"unauthorized_key": "malicious_injection", "eval_exploit": 123})
        r = requests.post(
            f"{DEFAULT_BASE_URL}/api/analyze",
            data={
                "query": "What facility is this in the satellite image?",
                "image_path": OPTICAL_SAMPLE,
                "parameters": injection_payload,
            },
            timeout=10.0,
        )
        dur = round((time.perf_counter() - t0) * 1000, 2)
        assert r.status_code == 200, f"Expected HTTP 200 with rejection envelope, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "INVALID_INPUT", f"Expected status='INVALID_INPUT', got {res.get('status')}"
        assert res.get("error_type") == "INVALID_PARAMETER", f"Expected error_type='INVALID_PARAMETER', got {res.get('error_type')}"
        assert "unauthorized_key" not in str(res.get("metadata", {}).get("permitted_parameters", {})), "Unauthorized parameter leaked to metadata!"
        
        # Verify no specialist model was executed
        trace = res.get("observable_execution_trace", [])
        tool_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_steps) == 0, f"Model was executed despite firewall violation! Trace: {trace}"

        print(f"PASS: Unauthorized parameter rejected at router firewall in {dur} ms.")
        print(f"      Status     : {res.get('status')} | Error Type: {res.get('error_type')}")
        print(f"      Answer     : {res.get('answer')}")
        results["Test 5 (Parameter Firewall)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 5]: {e}")
        results["Test 5 (Parameter Firewall)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 6: Unsupported Query Handling
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 6] Unsupported Query Handling (POST /api/analyze) ---")
    t0 = time.perf_counter()
    try:
        r = requests.post(
            f"{DEFAULT_BASE_URL}/api/analyze",
            data={
                "query": "calculate orbital trajectory from this image",
                "image_path": OPTICAL_SAMPLE,
            },
            timeout=10.0,
        )
        dur = round((time.perf_counter() - t0) * 1000, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "NEEDS_CLARIFICATION", f"Expected status='NEEDS_CLARIFICATION', got {res.get('status')}"
        assert res.get("selected_tool") is None, f"Expected selected_tool=None, got {res.get('selected_tool')}"
        assert res.get("model") == "AgentRouter", f"Expected model='AgentRouter', got {res.get('model')}"

        # Verify no model was executed
        trace = res.get("observable_execution_trace", [])
        tool_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_steps) == 0, f"Model executed on unsupported query! Trace: {trace}"

        print(f"PASS: Query 'calculate orbital trajectory' yielded NEEDS_CLARIFICATION ({dur} ms).")
        print(f"      Answer: {res.get('answer')[:85]}...")
        results["Test 6 (Unsupported Query)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 6]: {e}")
        results["Test 6 (Unsupported Query)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 1: VQA Execution
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 1] VQA End-to-End API Execution ---")
    t0 = time.perf_counter()
    try:
        with open(OPTICAL_SAMPLE, "rb") as f_img:
            r = requests.post(
                f"{DEFAULT_BASE_URL}/api/analyze",
                data={"query": "What type of maritime port or facility is shown in this satellite image?"},
                files={"image": ("sample_satellite_port.jpg", f_img, "image/jpeg")},
                timeout=120.0,
            )
        dur = round(time.perf_counter() - t0, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "SUCCESS", f"Expected status='SUCCESS', got {res.get('status')}"
        assert res.get("selected_tool") == "VQA", f"Expected selected_tool='VQA', got {res.get('selected_tool')}"
        assert res.get("answer"), "Missing answer in VQA response"
        assert res.get("evidence") is not None, "Missing evidence in VQA response"
        
        # Verify trace stages
        trace = res.get("observable_execution_trace", [])
        trace_stages = [s.get("step") for s in trace]
        for stage in ["INPUT_VALIDATION", "ROUTER", "TOOL_EXECUTION", "EVIDENCE", "RESULT_COMPOSITION"]:
            assert stage in trace_stages, f"Missing trace stage '{stage}' in {trace_stages}"

        latencies["VQA"] = f"{dur} s ({res.get('latency_ms')} ms pipeline)"
        t_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
        vram_log["After Test 1 (VQA)"] = f"{t_telemetry.get('free_vram_mb')} MB free"

        print(f"PASS: VQA executed successfully in {dur}s.")
        print(f"      Selected Tool: {res.get('selected_tool')} | Model: {res.get('model')}")
        print(f"      Answer       : {res.get('answer')[:100]}...")
        print(f"      Evidence     : {res.get('evidence', {}).get('type')}")
        print(f"      Trace Stages : {trace_stages}")
        print(f"      Free VRAM    : {t_telemetry.get('free_vram_mb')} MB")
        results["Test 1 (VQA)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 1]: {e}")
        results["Test 1 (VQA)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 2: Grounding Execution
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 2] Grounding End-to-End API Execution ---")
    t0 = time.perf_counter()
    try:
        with open(OPTICAL_SAMPLE, "rb") as f_img:
            r = requests.post(
                f"{DEFAULT_BASE_URL}/api/analyze",
                data={"query": "Locate the ships in this satellite image."},
                files={"image": ("sample_satellite_port.jpg", f_img, "image/jpeg")},
                timeout=60.0,
            )
        dur = round(time.perf_counter() - t0, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "SUCCESS", f"Expected status='SUCCESS', got {res.get('status')}"
        assert res.get("selected_tool") == "GROUNDING", f"Expected selected_tool='GROUNDING', got {res.get('selected_tool')}"
        assert res.get("evidence"), "Missing evidence in Grounding response"
        evidence = res.get("evidence", {})
        assert "bounding_boxes" in evidence, "Missing 'bounding_boxes' in evidence"
        assert "annotated_artifact" in evidence, "Missing 'annotated_artifact' reference in evidence"
        assert res.get("confidence") is not None, "Missing confidence score in Grounding response"

        trace = res.get("observable_execution_trace", [])
        trace_stages = [s.get("step") for s in trace]
        assert "TOOL_EXECUTION" in trace_stages, "Missing TOOL_EXECUTION stage in trace"

        latencies["GROUNDING"] = f"{dur} s ({res.get('latency_ms')} ms pipeline)"
        t_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
        vram_log["After Test 2 (Grounding)"] = f"{t_telemetry.get('free_vram_mb')} MB free"

        print(f"PASS: Grounding executed successfully in {dur}s.")
        print(f"      Selected Tool: {res.get('selected_tool')} | Model: {res.get('model')}")
        print(f"      Detections   : {evidence.get('detections_count')} | Confidence: {res.get('confidence')}")
        print(f"      Bounding Box : {evidence.get('bounding_boxes')[:2]}")
        print(f"      Artifact     : {evidence.get('annotated_artifact')}")
        print(f"      Free VRAM    : {t_telemetry.get('free_vram_mb')} MB")
        results["Test 2 (Grounding)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 2]: {e}")
        results["Test 2 (Grounding)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 3: Change Detection Execution
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 3] Change Detection End-to-End API Execution ---")
    t0 = time.perf_counter()
    try:
        with open(OPTICAL_SAMPLE, "rb") as f1, open(T2_SYNTHETIC_SAMPLE, "rb") as f2:
            r = requests.post(
                f"{DEFAULT_BASE_URL}/api/analyze",
                data={"query": "Identify differences and what changed between these two images"},
                files={
                    "image": ("sample_t1.jpg", f1, "image/jpeg"),
                    "second_image": ("sample_t2_synthetic.jpg", f2, "image/jpeg"),
                },
                timeout=60.0,
            )
        dur = round(time.perf_counter() - t0, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "SUCCESS", f"Expected status='SUCCESS', got {res.get('status')}"
        assert res.get("selected_tool") == "CHANGE_DETECTION", f"Expected selected_tool='CHANGE_DETECTION', got {res.get('selected_tool')}"
        
        evidence = res.get("evidence", {})
        assert "changed_pixels" in evidence, "Missing changed_pixels in evidence"
        assert "change_percentage" in evidence, "Missing change_percentage in evidence"
        assert "annotated_artifact" in evidence, "Missing annotated_artifact in evidence"
        
        # Verify synthetic pair limitation remains explicitly documented
        dataset_note = evidence.get("dataset_note", "") + res.get("metadata", {}).get("data_classification", "")
        assert "synthetic" in dataset_note.lower(), "Missing synthetic temporal pair limitation in evidence/metadata!"

        trace = res.get("observable_execution_trace", [])
        trace_stages = [s.get("step") for s in trace]
        assert "TOOL_EXECUTION" in trace_stages, "Missing TOOL_EXECUTION stage in trace"

        latencies["CHANGE_DETECTION"] = f"{dur} s ({res.get('latency_ms')} ms pipeline)"
        t_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
        vram_log["After Test 3 (Change Detection)"] = f"{t_telemetry.get('free_vram_mb')} MB free"

        print(f"PASS: Change Detection executed successfully in {dur}s.")
        print(f"      Selected Tool: {res.get('selected_tool')} | Model: {res.get('model')}")
        print(f"      Changed Px   : {evidence.get('changed_pixels'):,} ({evidence.get('change_percentage')}%)")
        print(f"      Confidence   : {res.get('confidence')}")
        print(f"      Limitation   : {evidence.get('dataset_note')}")
        print(f"      Artifact     : {evidence.get('annotated_artifact')}")
        print(f"      Free VRAM    : {t_telemetry.get('free_vram_mb')} MB")
        results["Test 3 (Change Detection)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 3]: {e}")
        results["Test 3 (Change Detection)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Test 4: Optical-SAR Execution
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- [TEST 4] Optical-SAR End-to-End API Execution ---")
    t0 = time.perf_counter()
    try:
        with open(OPTICAL_SAMPLE, "rb") as f_opt, open(SAR_PROXY_SAMPLE, "rb") as f_sar:
            r = requests.post(
                f"{DEFAULT_BASE_URL}/api/analyze",
                data={"query": "Analyze optical and SAR radar cross-modal backscatter imagery"},
                files={
                    "image": ("sample_optical.jpg", f_opt, "image/jpeg"),
                    "sar_image": ("sample_proxy_sar.png", f_sar, "image/png"),
                },
                timeout=60.0,
            )
        dur = round(time.perf_counter() - t0, 2)
        assert r.status_code == 200, f"Expected HTTP 200, got {r.status_code}"
        res = r.json()
        assert res.get("status") == "SUCCESS", f"Expected status='SUCCESS', got {res.get('status')}"
        assert res.get("selected_tool") == "OPTICAL_SAR", f"Expected selected_tool='OPTICAL_SAR', got {res.get('selected_tool')}"
        
        evidence = res.get("evidence", {})
        assert "optical_stats" in evidence, "Missing optical_stats in evidence"
        assert "sar_stats" in evidence, "Missing sar_stats in evidence"
        assert "cross_modal_correlation" in evidence, "Missing cross_modal_correlation in evidence"
        assert evidence.get("sar_data_classification") == "proxy_sar", (
            f"Expected sar_data_classification='proxy_sar', got {evidence.get('sar_data_classification')}"
        )

        trace = res.get("observable_execution_trace", [])
        trace_stages = [s.get("step") for s in trace]
        assert "TOOL_EXECUTION" in trace_stages, "Missing TOOL_EXECUTION stage in trace"

        latencies["OPTICAL_SAR"] = f"{dur} s ({res.get('latency_ms')} ms pipeline)"
        t_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
        vram_log["After Test 4 (Optical-SAR)"] = f"{t_telemetry.get('free_vram_mb')} MB free"

        print(f"PASS: Optical-SAR executed successfully in {dur}s.")
        print(f"      Selected Tool: {res.get('selected_tool')} | Model: {res.get('model')}")
        print(f"      Optical Mean : {evidence.get('optical_stats', {}).get('mean')}")
        print(f"      SAR Mean     : {evidence.get('sar_stats', {}).get('mean')}")
        print(f"      Correlation  : {evidence.get('cross_modal_correlation')}")
        print(f"      Classification: {evidence.get('sar_data_classification')}")
        print(f"      Artifact     : {evidence.get('annotated_artifact')}")
        print(f"      Free VRAM    : {t_telemetry.get('free_vram_mb')} MB")
        results["Test 4 (Optical-SAR)"] = "PASS"
    except Exception as e:
        print(f"FAIL [TEST 4]: {e}")
        results["Test 4 (Optical-SAR)"] = "FAIL"
        all_passed = False

    # -------------------------------------------------------------
    # Performance & Resource Telemetry Summary
    # -------------------------------------------------------------
    final_telemetry = get_health_telemetry(DEFAULT_BASE_URL)
    print("\n" + "=" * 80)
    print("  PHASE 7B: EXECUTION PERFORMANCE & VRAM TELEMETRY SUMMARY")
    print("=" * 80)
    print(f"Initial Free VRAM : {init_telemetry.get('free_vram_mb')} MB")
    for k, v in vram_log.items():
        print(f"{k:<32}: {v}")
    print(f"Final Free VRAM   : {final_telemetry.get('free_vram_mb')} MB / {final_telemetry.get('total_vram_mb')} MB")
    print("-" * 80)
    print("Tool Latencies:")
    for tool, lat in latencies.items():
        print(f"  - {tool:<18}: {lat}")
    print("-" * 80)
    print("Test Results:")
    passed_count = sum(1 for v in results.values() if v == "PASS")
    total_count = len(results)
    for test_name, status in results.items():
        print(f"  {status:<5} | {test_name}")
    print("=" * 80)

    if all_passed and passed_count == total_count:
        print("\nAPI_CONTRACT_TEST_RESULT=PASS")
        return 0
    else:
        print("\nAPI_CONTRACT_TEST_RESULT=FAIL")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
