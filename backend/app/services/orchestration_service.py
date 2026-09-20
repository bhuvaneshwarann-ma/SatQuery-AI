"""
SatQuery AI — Agent Orchestration Service (Phase 6)
Unified end-to-end execution entry point for multi-modal remote-sensing analysis.
Coordinates:
USER REQUEST -> INPUT VALIDATION -> AGENT ROUTER -> AUTHORIZED TOOL SELECTION
-> AUTHORIZED PARAMETERS -> TOOL EXECUTION -> EVIDENCE -> OBSERVABLE EXECUTION TRACE
-> FINAL STRUCTURED RESULT.
"""

import os
import time
from typing import Dict, Any, List, Optional
from ..agent.schemas import (
    AnalysisRequest,
    ToolSelection,
    ToolResult,
    ExecutionTraceEntry,
    RoutingStatus,
    OrchestrationResult,
)
from ..agent.router import AgentRouter
from ..agent.registry import get_tool
from ai.inference.vqa import run_vqa
from ai.inference.grounding import run_grounding
from ai.inference.change_detection import run_change_detection
from ai.inference.optical_sar import run_optical_sar


def execute_agent_request(request: AnalysisRequest) -> OrchestrationResult:
    """
    Executes a complete end-to-end agent analytical request through the controlled pipeline.

    Args:
        request: AnalysisRequest containing query, asset paths, optional task override,
                 and optional parameters.

    Returns:
        Structured OrchestrationResult conforming strictly to Phase 6 contract.
    """
    t_start = time.perf_counter()
    trace: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # Step 1: INPUT_VALIDATION (Pre-Execution Asset & Query Integrity)
    # -------------------------------------------------------------
    t_val_start = time.perf_counter()

    # Query validation
    clean_query = (request.query or "").strip()
    if not clean_query:
        val_latency = round((time.perf_counter() - t_val_start) * 1000, 2)
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        trace.append({
            "step": "INPUT_VALIDATION",
            "status": "ERROR",
            "selected_tool": None,
            "model": "InputValidator",
            "latency_ms": val_latency,
            "error": "Query string cannot be empty.",
        })
        return OrchestrationResult(
            status="ERROR",
            selected_tool=None,
            model="InputValidator",
            answer="Query string cannot be empty. Please provide an analytical query or specify a task.",
            confidence=None,
            evidence=None,
            metadata={"error_type": "VALIDATION_ERROR"},
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="VALIDATION_ERROR",
        )

    # Asset file existence validation (prevent heavy model loading on nonexistent assets)
    asset_checks = [
        ("image_path", request.image_path),
        ("second_image_path", request.second_image_path),
        ("optical_image_path", request.optical_image_path),
        ("sar_image_path", request.sar_image_path),
    ]

    for asset_name, path in asset_checks:
        if path and not os.path.exists(path):
            val_latency = round((time.perf_counter() - t_val_start) * 1000, 2)
            total_latency = round((time.perf_counter() - t_start) * 1000, 2)
            err_msg = f"Image file does not exist: {path}"
            trace.append({
                "step": "INPUT_VALIDATION",
                "status": "ERROR",
                "selected_tool": None,
                "model": "InputValidator",
                "latency_ms": val_latency,
                "error": err_msg,
                "missing_asset": asset_name,
            })
            return OrchestrationResult(
                status="ERROR",
                selected_tool=None,
                model="InputValidator",
                answer=err_msg,
                confidence=None,
                evidence=None,
                metadata={"error_type": "IMAGE_NOT_FOUND", "missing_asset": asset_name, "path": path},
                observable_execution_trace=trace,
                latency_ms=total_latency,
                error_type="IMAGE_NOT_FOUND",
            )

    val_latency = round((time.perf_counter() - t_val_start) * 1000, 2)
    active_inputs = [p for _, p in asset_checks if p]
    trace.append({
        "step": "INPUT_VALIDATION",
        "status": "PASSED",
        "selected_tool": None,
        "model": "InputValidator",
        "latency_ms": val_latency,
        "input_references": active_inputs,
    })

    # -------------------------------------------------------------
    # Step 2: ROUTER (Deterministic Intent Deduction & Parameter Firewall)
    # -------------------------------------------------------------
    t_route_start = time.perf_counter()
    selection: ToolSelection = AgentRouter.route(request)
    t_route_ms = round((time.perf_counter() - t_route_start) * 1000, 2)

    tool_def = get_tool(selection.selected_tool) if selection.selected_tool else None
    model_name = tool_def.model_or_engine if tool_def else "N/A"

    trace.append({
        "step": "ROUTER",
        "status": selection.status.value,
        "selected_task": selection.task.value if selection.task else None,
        "selected_tool": selection.selected_tool,
        "model": model_name,
        "permitted_parameters": selection.permitted_parameters,
        "input_references": selection.provided_inputs,
        "latency_ms": t_route_ms,
        "output_reference": f"routing_decision:{selection.status.value}",
    })

    # Handle Routing Non-Success Outcomes
    if selection.status == RoutingStatus.NEEDS_CLARIFICATION:
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        clarification_msg = (
            f"{selection.reason} {selection.clarification_prompt}"
            if selection.clarification_prompt else selection.reason
        )
        return OrchestrationResult(
            status="NEEDS_CLARIFICATION",
            selected_tool=None,
            model="AgentRouter",
            answer=clarification_msg,
            confidence=None,
            evidence=None,
            metadata={
                "clarification_prompt": selection.clarification_prompt,
                "supported_objectives": [
                    "1. Answer a question about an image (VQA)",
                    "2. Locate objects (Grounding)",
                    "3. Compare two images for temporal change (Change Detection)",
                    "4. Analyze optical + SAR imagery (Optical-SAR)"
                ]
            },
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="NEEDS_CLARIFICATION",
        )

    if selection.status == RoutingStatus.UNREGISTERED_TOOL:
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        return OrchestrationResult(
            status="UNREGISTERED_TOOL",
            selected_tool=None,
            model="AgentRouter",
            answer=selection.reason,
            confidence=None,
            evidence=None,
            metadata={
                "validation_errors": selection.validation_errors,
                "error_type": "UNREGISTERED_TOOL"
            },
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="UNREGISTERED_TOOL",
        )

    if selection.status == RoutingStatus.INVALID_INPUT:
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        err_msg = f"{selection.reason} Details: {'; '.join(selection.validation_errors)}"
        return OrchestrationResult(
            status="INVALID_INPUT",
            selected_tool=selection.selected_tool,
            model=model_name,
            answer=err_msg,
            confidence=None,
            evidence=None,
            metadata={
                "validation_errors": selection.validation_errors,
                "required_inputs": selection.required_inputs,
                "provided_inputs": selection.provided_inputs,
                "error_type": "INVALID_INPUT"
            },
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="INVALID_INPUT",
        )

    # Check for parameter firewall violations before model execution
    if selection.validation_errors and any("unpermitted parameter" in err.lower() for err in selection.validation_errors):
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        err_msg = f"Parameter firewall rejection for tool '{selection.selected_tool}': {'; '.join(selection.validation_errors)}"
        return OrchestrationResult(
            status="INVALID_INPUT",
            selected_tool=selection.selected_tool,
            model=model_name,
            answer=err_msg,
            confidence=None,
            evidence=None,
            metadata={
                "error_type": "INVALID_PARAMETER",
                "validation_errors": selection.validation_errors,
                "permitted_parameters": selection.permitted_parameters,
            },
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="INVALID_PARAMETER",
        )

    # -------------------------------------------------------------
    # Step 3: TOOL_EXECUTION (Authorized Specialist Execution)
    # -------------------------------------------------------------
    tool_raw: Dict[str, Any] = {}

    if selection.selected_tool == "VQA":
        tool_raw = run_vqa(
            image_path=request.image_path,
            query=request.query,
            permitted_parameters=selection.permitted_parameters,
        )

    elif selection.selected_tool == "GROUNDING":
        tool_raw = run_grounding(
            image_path=request.image_path,
            query=request.query,
            permitted_parameters=selection.permitted_parameters,
        )

    elif selection.selected_tool == "CHANGE_DETECTION":
        tool_raw = run_change_detection(
            image_path=request.image_path,
            second_image_path=request.second_image_path,
            query=request.query,
            permitted_parameters=selection.permitted_parameters,
        )

    elif selection.selected_tool == "OPTICAL_SAR":
        optical_path = request.optical_image_path or request.image_path
        tool_raw = run_optical_sar(
            optical_image_path=optical_path,
            sar_image_path=request.sar_image_path,
            query=request.query,
            permitted_parameters=selection.permitted_parameters,
        )

    else:
        total_latency = round((time.perf_counter() - t_start) * 1000, 2)
        return OrchestrationResult(
            status="UNSUPPORTED_TASK",
            selected_tool=selection.selected_tool,
            model="N/A",
            answer=f"Tool '{selection.selected_tool}' is not connected to an executor.",
            confidence=None,
            evidence=None,
            metadata={"error_type": "UNSUPPORTED_TASK"},
            observable_execution_trace=trace,
            latency_ms=total_latency,
            error_type="UNSUPPORTED_TASK",
        )

    # Record TOOL_EXECUTION trace entry
    trace.append({
        "step": "TOOL_EXECUTION",
        "status": tool_raw["status"],
        "selected_task": selection.task.value if selection.task else None,
        "selected_tool": selection.selected_tool,
        "model": tool_raw["model"],
        "permitted_parameters": selection.permitted_parameters,
        "input_references": selection.provided_inputs,
        "latency_ms": tool_raw["latency_ms"],
        "evidence_reference": tool_raw.get("evidence_reference"),
    })

    # -------------------------------------------------------------
    # Step 4: EVIDENCE (Structured Telemetry & Spatial Proof Verification)
    # -------------------------------------------------------------
    evidence_payload = tool_raw["evidence"][0] if tool_raw.get("evidence") else None
    trace.append({
        "step": "EVIDENCE",
        "status": "AVAILABLE" if evidence_payload else "NONE",
        "selected_task": selection.task.value if selection.task else None,
        "selected_tool": selection.selected_tool,
        "model": tool_raw["model"],
        "latency_ms": 0.1,
        "evidence_reference": tool_raw.get("evidence_reference"),
    })

    # -------------------------------------------------------------
    # Step 5: RESULT_COMPOSITION (Consolidated Contract Synthesis)
    # -------------------------------------------------------------
    total_latency = round((time.perf_counter() - t_start) * 1000, 2)
    trace.append({
        "step": "RESULT_COMPOSITION",
        "status": "COMPLETED" if tool_raw["status"] == "SUCCESS" else "ERROR",
        "selected_task": selection.task.value if selection.task else None,
        "selected_tool": selection.selected_tool,
        "model": tool_raw["model"],
        "latency_ms": 0.1,
    })

    error_type = None
    if tool_raw["status"] != "SUCCESS":
        error_type = tool_raw.get("metadata", {}).get("error_type", "EXECUTION_ERROR")

    return OrchestrationResult(
        status=tool_raw["status"],
        selected_tool=selection.selected_tool,
        model=tool_raw["model"],
        answer=tool_raw["answer"],
        confidence=tool_raw.get("confidence"),
        evidence=evidence_payload,
        metadata=tool_raw.get("metadata", {}),
        observable_execution_trace=trace,
        latency_ms=total_latency,
        error_type=error_type,
    )
