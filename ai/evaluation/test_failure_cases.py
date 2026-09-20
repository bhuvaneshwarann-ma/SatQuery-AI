"""
SatQuery AI — Failure Case & Robustness Evaluation Suite (Phase 8B)
Verifies input validation boundaries, security parameter firewalls, and ambiguity detection:
1. Corrupted image file
2. Unsupported file extension (.exe/.txt)
3. Missing primary image
4. Missing second image (Change Detection)
5. Missing SAR image (Optical-SAR)
6. Empty query
7. Ambiguous query ('process this')
8. Unsupported task query ('calculate orbital trajectory')
9. Unauthorized parameter injection
10. Unregistered tool request

Measures:
- Rejection correctness
- Absence of specialist model execution
- Diagnostic error type classification
- Sub-millisecond rejection latency
"""

import os
import sys
import io
import time
import json
import requests
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
OPTICAL_SAMPLE = os.path.join(PROJECT_ROOT, "data/samples/sample_satellite_port.jpg")


def run_failure_suite():
    print("=" * 80)
    print("  SatQuery AI — Robustness & Failure Case Evaluation (Phase 8B)")
    print("=" * 80)

    test_cases = [
        {
            "id": "FAIL-01",
            "name": "Corrupted Image Binary",
            "data": {"query": "What facility is this?"},
            "files": {"image": ("corrupted.jpg", io.BytesIO(b"NOT_A_VALID_JPEG_IMAGE_HEADER_CORRUPTED"), "image/jpeg")},
            "expected_status": ["ERROR", "INVALID_INPUT"],
            "expected_error_type": ["INVALID_IMAGE", "VALIDATION_ERROR"],
        },
        {
            "id": "FAIL-02",
            "name": "Unsupported File Extension (.exe)",
            "data": {"query": "What facility is this?"},
            "files": {"image": ("malicious.exe", io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00"), "application/octet-stream")},
            "expected_status": ["ERROR", "INVALID_INPUT"],
            "expected_error_type": ["INVALID_IMAGE", "VALIDATION_ERROR"],
        },
        {
            "id": "FAIL-03",
            "name": "Missing Primary Image",
            "data": {"query": "Locate the ships in this satellite image."},
            "files": None,
            "expected_status": ["INVALID_INPUT", "ERROR"],
            "expected_error_type": ["INVALID_INPUT", "IMAGE_NOT_FOUND"],
        },
        {
            "id": "FAIL-04",
            "name": "Missing T2 for Change Detection",
            "data": {"query": "What changed between these images?"},
            "files": {"image": ("sample.jpg", open(OPTICAL_SAMPLE, "rb"), "image/jpeg")},
            "expected_status": ["INVALID_INPUT"],
            "expected_error_type": ["INVALID_INPUT"],
        },
        {
            "id": "FAIL-05",
            "name": "Missing SAR for Optical-SAR",
            "data": {"query": "Analyze optical and SAR radar cross-modal imagery"},
            "files": {"image": ("sample.jpg", open(OPTICAL_SAMPLE, "rb"), "image/jpeg")},
            "expected_status": ["INVALID_INPUT"],
            "expected_error_type": ["INVALID_INPUT"],
        },
        {
            "id": "FAIL-06",
            "name": "Empty Query String",
            "data": {"query": "   "},
            "files": {"image": ("sample.jpg", open(OPTICAL_SAMPLE, "rb"), "image/jpeg")},
            "expected_status": ["ERROR", "INVALID_INPUT"],
            "expected_error_type": ["VALIDATION_ERROR", "INVALID_INPUT"],
        },
        {
            "id": "FAIL-07",
            "name": "Ambiguous Query ('process this')",
            "data": {"query": "process this"},
            "files": {"image": ("sample.jpg", open(OPTICAL_SAMPLE, "rb"), "image/jpeg")},
            "expected_status": ["NEEDS_CLARIFICATION"],
            "expected_error_type": ["NEEDS_CLARIFICATION"],
        },
        {
            "id": "FAIL-08",
            "name": "Unsupported Task ('calculate orbital trajectory')",
            "data": {"query": "calculate orbital trajectory from this image"},
            "files": {"image": ("sample.jpg", open(OPTICAL_SAMPLE, "rb"), "image/jpeg")},
            "expected_status": ["NEEDS_CLARIFICATION"],
            "expected_error_type": ["NEEDS_CLARIFICATION"],
        },
        {
            "id": "FAIL-09",
            "name": "Unauthorized Parameter Injection",
            "data": {
                "query": "What facility is this in the satellite image?",
                "image_path": OPTICAL_SAMPLE,
                "parameters": json.dumps({"unauthorized_key": "injected_val"}),
            },
            "files": None,
            "expected_status": ["INVALID_INPUT"],
            "expected_error_type": ["INVALID_PARAMETER"],
        },
        {
            "id": "FAIL-10",
            "name": "Unregistered Tool Explicit Request",
            "data": {
                "query": "Perform hyperspectral deconvolution",
                "task": "HYPERSPECTRAL_DECONVOLUTION",
                "image_path": OPTICAL_SAMPLE,
            },
            "files": None,
            "expected_status": ["UNREGISTERED_TOOL"],
            "expected_error_type": ["UNREGISTERED_TOOL"],
        },
    ]

    passed_cases = 0
    records = []

    for tc in test_cases:
        tc_id = tc["id"]
        tc_name = tc["name"]
        print(f"\n--- [{tc_id}] {tc_name} ---")

        t0 = time.perf_counter()
        resp = requests.post(f"{DEFAULT_BASE_URL}/api/analyze", data=tc["data"], files=tc["files"], timeout=10.0)
        dur_ms = round((time.perf_counter() - t0) * 1000, 2)

        try:
            payload = resp.json()
        except Exception as err:
            print(f"FAIL [{tc_id}]: Server returned non-JSON response ({resp.status_code}): {err}")
            records.append({"id": tc_id, "name": tc_name, "status": "FAIL", "latency_ms": dur_ms, "error": str(err)})
            continue

        status = payload.get("status")
        error_type = payload.get("error_type") or payload.get("metadata", {}).get("error_type")
        trace = payload.get("observable_execution_trace", [])

        # Verify no specialist model executed
        model_executed = any(step.get("step") == "TOOL_EXECUTION" for step in trace)

        status_ok = status in tc["expected_status"]
        error_type_ok = any(e in str(error_type) for e in tc["expected_error_type"])
        no_model_ok = not model_executed

        case_passed = status_ok and error_type_ok and no_model_ok

        record = {
            "id": tc_id,
            "name": tc_name,
            "status": "PASS" if case_passed else "FAIL",
            "returned_status": status,
            "error_type": error_type,
            "model_executed": model_executed,
            "latency_ms": dur_ms,
            "answer_preview": str(payload.get("answer", ""))[:70],
        }
        records.append(record)

        if case_passed:
            print(f"PASS: Rejected correctly as status='{status}', error_type='{error_type}' in {dur_ms} ms")
            print(f"      Model Execution: False | Trace Steps: {len(trace)}")
            print(f"      Message: {record['answer_preview']}...")
            passed_cases += 1
        else:
            print(f"FAIL: Expected status in {tc['expected_status']}, error_type in {tc['expected_error_type']}")
            print(f"      Actual: status='{status}', error_type='{error_type}', model_executed={model_executed}")

    print("\n" + "=" * 80)
    print(f"ROBUSTNESS EVALUATION SUMMARY: {passed_cases} / {len(test_cases)} PASSED")
    print("=" * 80)

    return passed_cases == len(test_cases), records


if __name__ == "__main__":
    success, _ = run_failure_suite()
    sys.exit(0 if success else 1)
