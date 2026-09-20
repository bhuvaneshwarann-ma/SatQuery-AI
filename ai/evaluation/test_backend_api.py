"""
SatQuery AI — Backend API Integration Evaluation (Phase 7A)
Verifies:
- Test A: VQA request with sample image via multipart upload
- Test B: Ambiguous query (NEEDS_CLARIFICATION, no model execution)
- Test C: Missing image (structured validation error, no model execution)
- Test D: Change Detection without second image (INVALID_INPUT, no model execution)
- Test E: Optical-SAR without SAR image (INVALID_INPUT, no model execution)
- Health check: GET /api/health

Outputs:
API_INTEGRATION_TEST_RESULT=PASS or FAIL
"""

import os
import sys
import time
import requests

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SAMPLE_IMAGE = os.path.join(PROJECT_ROOT, "data/samples/sample_satellite_port.jpg")
DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def get_client():
    """
    Returns a client callable or requests session.
    Tests live server if running, otherwise falls back to TestClient.
    """
    try:
        resp = requests.get(f"{DEFAULT_BASE_URL}/api/health", timeout=1.5)
        if resp.status_code == 200:
            print(f"[Client] Connected to LIVE server at {DEFAULT_BASE_URL}")
            return "LIVE", DEFAULT_BASE_URL
    except Exception:
        pass

    print("[Client] Live server not detected at 8000. Using FastAPI TestClient.")
    from fastapi.testclient import TestClient
    from backend.app.main import app
    return "TEST_CLIENT", TestClient(app)


def make_request(client_type, client, method, endpoint, data=None, files=None):
    """Unified request sender for live server or TestClient."""
    if client_type == "LIVE":
        url = f"{client}{endpoint}"
        if method == "GET":
            return requests.get(url, timeout=300)
        elif method == "POST":
            return requests.post(url, data=data, files=files, timeout=300)
    else:
        if method == "GET":
            return client.get(endpoint)
        elif method == "POST":
            return client.post(endpoint, data=data, files=files)


def run_tests():
    print("=" * 70)
    print("SATQUERY AI — PHASE 7A: BACKEND API INTEGRATION TEST")
    print("=" * 70)

    client_type, client = get_client()
    tests_passed = 0
    total_tests = 6  # Health + Tests A, B, C, D, E

    # -------------------------------------------------------------
    # Test 0: Health Check (/api/health)
    # -------------------------------------------------------------
    print("\n--- [TEST 0] Health Telemetry Endpoint (GET /api/health) ---")
    try:
        res = make_request(client_type, client, "GET", "/api/health")
        assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") == "healthy", f"Expected status='healthy', got {payload.get('status')}"
        assert "registered_tools" in payload, "Missing registered_tools in health response"
        assert "VQA" in payload["registered_tools"], "VQA missing from registered tools"
        print(f"PASS: Health check responded with {payload['status']}")
        print(f"      GPU: {payload.get('gpu_name')} | Free VRAM: {payload.get('free_vram_mb')} MB")
        print(f"      Tools: {payload.get('registered_tools')}")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST 0]: {e}")

    # -------------------------------------------------------------
    # Test B: Ambiguous Query (Fast test before heavy VQA)
    # -------------------------------------------------------------
    print("\n--- [TEST B] Ambiguous Query Handling (POST /api/analyze) ---")
    try:
        with open(SAMPLE_IMAGE, "rb") as img_file:
            res = make_request(
                client_type, client, "POST", "/api/analyze",
                data={"query": "process this"},
                files={"image": ("sample.jpg", img_file, "image/jpeg")}
            )
        assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") == "NEEDS_CLARIFICATION", (
            f"Expected status='NEEDS_CLARIFICATION', got {payload.get('status')}"
        )
        assert payload.get("error_type") == "NEEDS_CLARIFICATION", (
            f"Expected error_type='NEEDS_CLARIFICATION', got {payload.get('error_type')}"
        )
        # Verify no model execution in trace
        trace = payload.get("observable_execution_trace", [])
        tool_exec_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_exec_steps) == 0, f"Model was executed despite ambiguous query! Trace: {trace}"
        print(f"PASS: Query 'process this' yielded status='{payload.get('status')}' without model execution.")
        print(f"      Answer: {payload.get('answer')[:75]}...")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST B]: {e}")

    # -------------------------------------------------------------
    # Test C: Missing Image
    # -------------------------------------------------------------
    print("\n--- [TEST C] Missing Image Handling (POST /api/analyze) ---")
    try:
        # No image file and no image_path provided
        res = make_request(
            client_type, client, "POST", "/api/analyze",
            data={"query": "How many ships are docked in the harbor?"},
        )
        assert res.status_code in [200, 400], f"Expected HTTP 200 or 400, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") in ["INVALID_INPUT", "ERROR"], (
            f"Expected status INVALID_INPUT or ERROR, got {payload.get('status')}"
        )
        # Verify no heavy model executed
        trace = payload.get("observable_execution_trace", [])
        tool_exec_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_exec_steps) == 0, f"Model was executed despite missing image! Trace: {trace}"
        print(f"PASS: Missing image returned structured validation error status='{payload.get('status')}'.")
        print(f"      Answer: {payload.get('answer')}")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST C]: {e}")

    # -------------------------------------------------------------
    # Test D: Change Detection without Second Image
    # -------------------------------------------------------------
    print("\n--- [TEST D] Change Detection Without Second Image (POST /api/analyze) ---")
    try:
        with open(SAMPLE_IMAGE, "rb") as img_file:
            res = make_request(
                client_type, client, "POST", "/api/analyze",
                data={"query": "What changed between these images?"},
                files={"image": ("sample.jpg", img_file, "image/jpeg")}
            )
        assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") == "INVALID_INPUT", (
            f"Expected status='INVALID_INPUT', got {payload.get('status')}"
        )
        assert payload.get("selected_tool") == "CHANGE_DETECTION", (
            f"Expected selected_tool='CHANGE_DETECTION', got {payload.get('selected_tool')}"
        )
        # Verify no model execution in trace
        trace = payload.get("observable_execution_trace", [])
        tool_exec_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_exec_steps) == 0, f"Model was executed despite missing T2! Trace: {trace}"
        print(f"PASS: Change Detection missing T2 correctly rejected with status='{payload.get('status')}'.")
        print(f"      Answer: {payload.get('answer')[:85]}...")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST D]: {e}")

    # -------------------------------------------------------------
    # Test E: Optical-SAR without SAR Image
    # -------------------------------------------------------------
    print("\n--- [TEST E] Optical-SAR Without SAR Image (POST /api/analyze) ---")
    try:
        with open(SAMPLE_IMAGE, "rb") as img_file:
            res = make_request(
                client_type, client, "POST", "/api/analyze",
                data={"query": "Analyze optical and SAR radar backscatter"},
                files={"image": ("sample.jpg", img_file, "image/jpeg")}
            )
        assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") == "INVALID_INPUT", (
            f"Expected status='INVALID_INPUT', got {payload.get('status')}"
        )
        assert payload.get("selected_tool") == "OPTICAL_SAR", (
            f"Expected selected_tool='OPTICAL_SAR', got {payload.get('selected_tool')}"
        )
        # Verify no model execution in trace
        trace = payload.get("observable_execution_trace", [])
        tool_exec_steps = [s for s in trace if s.get("step") == "TOOL_EXECUTION"]
        assert len(tool_exec_steps) == 0, f"Model was executed despite missing SAR! Trace: {trace}"
        print(f"PASS: Optical-SAR missing SAR image correctly rejected with status='{payload.get('status')}'.")
        print(f"      Answer: {payload.get('answer')[:85]}...")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST E]: {e}")

    # -------------------------------------------------------------
    # Test A: Real VQA Analysis via Multipart Upload
    # -------------------------------------------------------------
    print("\n--- [TEST A] Real VQA Analysis (POST /api/analyze) ---")
    t0 = time.perf_counter()
    try:
        with open(SAMPLE_IMAGE, "rb") as img_file:
            res = make_request(
                client_type, client, "POST", "/api/analyze",
                data={"query": "What type of facility or port is shown in this satellite image?"},
                files={"image": ("sample_satellite_port.jpg", img_file, "image/jpeg")}
            )
        duration_s = round(time.perf_counter() - t0, 2)
        assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
        payload = res.json()
        assert payload.get("status") == "SUCCESS", f"Expected status='SUCCESS', got {payload.get('status')}"
        assert payload.get("selected_tool") == "VQA", f"Expected selected_tool='VQA', got {payload.get('selected_tool')}"
        assert payload.get("answer"), "Missing or empty answer in response"
        assert payload.get("evidence") is not None, "Missing evidence in response"
        assert len(payload.get("observable_execution_trace", [])) > 0, "Missing execution trace"
        
        trace_steps = [s.get("step") for s in payload["observable_execution_trace"]]
        assert "INPUT_VALIDATION" in trace_steps, "Trace missing INPUT_VALIDATION"
        assert "ROUTER" in trace_steps, "Trace missing ROUTER"
        assert "TOOL_EXECUTION" in trace_steps, "Trace missing TOOL_EXECUTION"
        assert "EVIDENCE" in trace_steps, "Trace missing EVIDENCE"

        print(f"PASS: VQA Request succeeded in {duration_s}s!")
        print(f"      Selected Tool: {payload.get('selected_tool')}")
        print(f"      Model: {payload.get('model')}")
        print(f"      Answer: {payload.get('answer')[:95]}...")
        print(f"      Confidence: {payload.get('confidence')}")
        print(f"      Evidence Type: {payload.get('evidence', {}).get('type')}")
        print(f"      Trace Steps: {trace_steps}")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL [TEST A]: {e}")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"PHASE 7A API TEST SUMMARY: {tests_passed}/{total_tests} PASSED")
    print("=" * 70)

    if tests_passed == total_tests:
        print("API_INTEGRATION_TEST_RESULT=PASS")
        return 0
    else:
        print("API_INTEGRATION_TEST_RESULT=FAIL")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
