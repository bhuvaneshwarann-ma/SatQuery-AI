"""
SatQuery AI — Analysis Service (Phase 5A)
Coordinates the end-to-end analytical workflow:
AnalysisRequest -> Input Validation -> Agent Router -> Specialist Tool Executor -> ToolResult
Records strictly observable execution trace entries without hidden reasoning.
"""

import time
from typing import Tuple, List, Optional
from ..agent.schemas import (
    AnalysisRequest,
    ToolSelection,
    ToolResult,
    ExecutionTraceEntry,
    RoutingStatus,
)
from ..agent.router import AgentRouter
from ..agent.registry import get_tool
from .confidence_service import (
    evaluate_grounding_confidence,
    evaluate_change_confidence,
    evaluate_optical_sar_confidence,
)
from ai.inference.vqa import run_vqa
from ai.inference.grounding import run_grounding
from ai.inference.change_detection import run_change_detection
from ai.inference.optical_sar import run_optical_sar


class AnalysisService:
    """
    Central orchestration service bridging user requests, deterministic routing,
    and verified specialist model executors.
    """

    @classmethod
    def analyze(cls, request: AnalysisRequest) -> Tuple[ToolResult, List[ExecutionTraceEntry]]:
        """
        Executes analysis pipeline for an incoming user request:
        1. Routes and validates through AgentRouter
        2. Records router stage in execution trace
        3. Dispatches to verified specialist executor (Phase 5A: VQA connected)
        4. Records execution trace and returns consolidated ToolResult
        """
        trace: List[ExecutionTraceEntry] = []
        t0 = time.perf_counter()

        # Step 1: Route and validate inputs
        selection: ToolSelection = AgentRouter.route(request)
        router_latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        tool_def = get_tool(selection.selected_tool) if selection.selected_tool else None
        model_name = tool_def.model_or_engine if tool_def else "N/A"

        # Step 2: Record Router Observable Trace Entry
        trace.append(
            ExecutionTraceEntry(
                step="ROUTER",
                selected_task=selection.task.value if selection.task else None,
                selected_tool=selection.selected_tool,
                model=model_name,
                permitted_parameters=selection.permitted_parameters,
                input_references=selection.provided_inputs,
                status=selection.status.value,
                latency_ms=router_latency_ms,
                output_reference=f"routing_decision:{selection.status.value}",
                evidence_reference=None,
            )
        )

        # Step 3: Handle Routing Exceptions (Invalid Input, Ambiguity, Unregistered Tool)
        if selection.status != RoutingStatus.ROUTED:
            error_msg = selection.reason
            if selection.validation_errors:
                error_msg += f" Details: {'; '.join(selection.validation_errors)}"
            if selection.clarification_prompt:
                error_msg += f" Clarification: {selection.clarification_prompt}"

            return (
                ToolResult(
                    tool_name=selection.selected_tool or "ROUTER",
                    status=selection.status.value,
                    answer=error_msg,
                    model="AgentRouter",
                    evidence=None,
                    confidence=None,
                    latency_ms=router_latency_ms,
                    metadata={"validation_errors": selection.validation_errors},
                ),
                trace,
            )

        # Step 4: Dispatch to Connected Specialist Executor
        if selection.selected_tool == "VQA":
            # Real VQA forward pass via verified Qwen2.5-VL-3B executor
            vqa_raw = run_vqa(
                image_path=request.image_path,
                query=request.query,
                permitted_parameters=selection.permitted_parameters,
            )

            # Record Execution Trace Entry
            trace.append(
                ExecutionTraceEntry(
                    step="TOOL_EXECUTION",
                    selected_task="VQA",
                    selected_tool="VQA",
                    model=vqa_raw["model"],
                    permitted_parameters=selection.permitted_parameters,
                    input_references=[request.image_path] if request.image_path else [],
                    status=vqa_raw["status"],
                    latency_ms=vqa_raw["latency_ms"],
                    output_reference="vqa_text_output",
                    evidence_reference="vqa_spatial_metadata" if vqa_raw.get("evidence") else None,
                )
            )

            result = ToolResult(
                tool_name="VQA",
                status=vqa_raw["status"],
                answer=vqa_raw["answer"],
                model=vqa_raw["model"],
                evidence=vqa_raw["evidence"][0] if vqa_raw.get("evidence") else None,
                confidence=vqa_raw.get("confidence"),
                image_description=vqa_raw.get("image_description"),
                visual_evidence=vqa_raw.get("visual_evidence"),
                latency_ms=vqa_raw["latency_ms"],
                metadata=vqa_raw["metadata"],
            )
            return result, trace

        elif selection.selected_tool == "GROUNDING":
            # Real Visual Grounding forward pass via verified Grounding DINO executor
            grounding_raw = run_grounding(
                image_path=request.image_path,
                query=request.query,
                permitted_parameters=selection.permitted_parameters,
            )

            # Record Execution Trace Entry
            trace.append(
                ExecutionTraceEntry(
                    step="TOOL_EXECUTION",
                    selected_task="GROUNDING",
                    selected_tool="GROUNDING",
                    model=grounding_raw["model"],
                    permitted_parameters=selection.permitted_parameters,
                    input_references=[request.image_path] if request.image_path else [],
                    status=grounding_raw["status"],
                    latency_ms=grounding_raw["latency_ms"],
                    output_reference="grounding_bounding_boxes",
                    evidence_reference=grounding_raw.get("evidence_reference"),
                )
            )

            gr_evidence = grounding_raw["evidence"][0] if grounding_raw.get("evidence") else None
            box_count = len(gr_evidence.get("bounding_boxes", [])) if gr_evidence else 0
            gr_conf = evaluate_grounding_confidence(grounding_raw.get("confidence"), box_count, request.query)

            result = ToolResult(
                tool_name="GROUNDING",
                status=grounding_raw["status"],
                answer=grounding_raw["answer"],
                model=grounding_raw["model"],
                evidence=gr_evidence,
                confidence=gr_conf,
                image_description=f"Visual grounding scene targeting '{request.query}' with {box_count} localized detection box(es).",
                visual_evidence=[{"category": "localized_target_regions", "description": f"{box_count} spatial bounding box(es) detected."}] if box_count > 0 else [],
                latency_ms=grounding_raw["latency_ms"],
                metadata=grounding_raw["metadata"],
            )
            return result, trace

        elif selection.selected_tool == "CHANGE_DETECTION":
            # Parameter range pre-execution validation
            if "threshold" in request.parameters:
                try:
                    th = float(request.parameters["threshold"])
                    if th < 0.10 or th > 0.90:
                        return (
                            ToolResult(
                                tool_name="CHANGE_DETECTION",
                                status="ERROR",
                                answer=f"Parameter 'threshold' value {th} is outside authorized registry bounds [0.10, 0.90].",
                                model="Siamese-ResNet18-FeatureDifferencer",
                                evidence=None,
                                confidence=None,
                                latency_ms=0.0,
                                metadata={"error_type": "INVALID_PARAMETER", "message": f"Threshold {th} outside [0.10, 0.90]"},
                            ),
                            trace,
                        )
                except (ValueError, TypeError) as th_err:
                    return (
                        ToolResult(
                            tool_name="CHANGE_DETECTION",
                            status="ERROR",
                            answer=f"Parameter 'threshold' must be a valid float: {th_err}",
                            model="Siamese-ResNet18-FeatureDifferencer",
                            evidence=None,
                            confidence=None,
                            latency_ms=0.0,
                            metadata={"error_type": "INVALID_PARAMETER", "message": str(th_err)},
                        ),
                        trace,
                    )

            # Real Change Detection forward pass via verified Siamese-ResNet18 executor
            change_raw = run_change_detection(
                image_path=request.image_path,
                second_image_path=request.second_image_path,
                query=request.query,
                permitted_parameters=selection.permitted_parameters,
            )

            # Record Execution Trace Entry
            trace.append(
                ExecutionTraceEntry(
                    step="TOOL_EXECUTION",
                    selected_task="CHANGE_DETECTION",
                    selected_tool="CHANGE_DETECTION",
                    model=change_raw["model"],
                    permitted_parameters=selection.permitted_parameters,
                    input_references=[p for p in [request.image_path, request.second_image_path] if p],
                    status=change_raw["status"],
                    latency_ms=change_raw["latency_ms"],
                    output_reference="change_mask_statistics",
                    evidence_reference=change_raw.get("evidence_reference"),
                )
            )

            cd_evidence = change_raw["evidence"][0] if change_raw.get("evidence") else None
            changed_px = cd_evidence.get("changed_pixel_count", 0) if cd_evidence else 0
            cd_conf = evaluate_change_confidence(change_raw.get("confidence"), changed_px)

            result = ToolResult(
                tool_name="CHANGE_DETECTION",
                status=change_raw["status"],
                answer=change_raw["answer"],
                model=change_raw["model"],
                evidence=cd_evidence,
                confidence=cd_conf,
                image_description="Bi-temporal paired remote-sensing scene comparison under Siamese feature differencing.",
                visual_evidence=[{"category": "differential_change_regions", "description": f"{changed_px:,} changed pixels identified across the scene."}],
                latency_ms=change_raw["latency_ms"],
                metadata=change_raw["metadata"],
            )
            return result, trace

        elif selection.selected_tool == "OPTICAL_SAR":
            # Parameter range pre-execution validation
            if "high_scatter_threshold" in request.parameters:
                try:
                    th = float(request.parameters["high_scatter_threshold"])
                    if th < 100.0 or th > 250.0:
                        return (
                            ToolResult(
                                tool_name="OPTICAL_SAR",
                                status="ERROR",
                                answer=f"Parameter 'high_scatter_threshold' value {th} is outside authorized registry bounds [100.0, 250.0].",
                                model="Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine",
                                evidence=None,
                                confidence=None,
                                latency_ms=0.0,
                                metadata={"error_type": "INVALID_PARAMETER", "message": f"high_scatter_threshold {th} outside [100.0, 250.0]"},
                            ),
                            trace,
                        )
                except (ValueError, TypeError) as th_err:
                    return (
                        ToolResult(
                            tool_name="OPTICAL_SAR",
                            status="ERROR",
                            answer=f"Parameter 'high_scatter_threshold' must be a valid float: {th_err}",
                            model="Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine",
                            evidence=None,
                            confidence=None,
                            latency_ms=0.0,
                            metadata={"error_type": "INVALID_PARAMETER", "message": str(th_err)},
                        ),
                        trace,
                    )

            # Resolve optical path (can be supplied in optical_image_path or image_path)
            optical_path = request.optical_image_path or request.image_path

            # Real Optical-SAR forward pass
            optical_sar_raw = run_optical_sar(
                optical_image_path=optical_path,
                sar_image_path=request.sar_image_path,
                query=request.query,
                permitted_parameters=selection.permitted_parameters,
            )

            # Record Execution Trace Entry
            trace.append(
                ExecutionTraceEntry(
                    step="TOOL_EXECUTION",
                    selected_task="OPTICAL_SAR",
                    selected_tool="OPTICAL_SAR",
                    model=optical_sar_raw["model"],
                    permitted_parameters=selection.permitted_parameters,
                    input_references=[p for p in [optical_path, request.sar_image_path] if p],
                    status=optical_sar_raw["status"],
                    latency_ms=optical_sar_raw["latency_ms"],
                    output_reference="cross_modal_statistics",
                    evidence_reference=optical_sar_raw.get("evidence_reference"),
                )
            )

            sar_evidence = optical_sar_raw["evidence"][0] if optical_sar_raw.get("evidence") else None
            sar_corr = sar_evidence.get("cross_modal_correlation", 0.574) if sar_evidence else 0.574
            sar_anom = sar_evidence.get("radar_anomaly_pixel_count", 0) if sar_evidence else 0
            sar_conf = evaluate_optical_sar_confidence(sar_corr, sar_anom)

            result = ToolResult(
                tool_name="OPTICAL_SAR",
                status=optical_sar_raw["status"],
                answer=optical_sar_raw["answer"],
                model=optical_sar_raw["model"],
                evidence=sar_evidence,
                confidence=sar_conf,
                image_description="Cross-modal dual-sensor paired analysis correlating optical spectral reflectance and SAR microwave radar backscatter.",
                visual_evidence=[{"category": "radar_backscatter_anomalies", "description": f"{sar_anom:,} high-backscatter radar echo pixels identified across co-registered grid."}],
                latency_ms=optical_sar_raw["latency_ms"],
                metadata=optical_sar_raw["metadata"],
            )
            return result, trace

        # Placeholder for tools scheduled in subsequent phases
        pending_msg = (
            f"Tool '{selection.selected_tool}' was successfully routed and validated. "
            f"Execution pipeline connection is scheduled for subsequent phases."
        )
        return (
            ToolResult(
                tool_name=selection.selected_tool,
                status="PENDING_INTEGRATION",
                answer=pending_msg,
                model=model_name,
                evidence=None,
                confidence=None,
                latency_ms=router_latency_ms,
                metadata={"permitted_parameters": selection.permitted_parameters},
            ),
            trace,
        )

    @classmethod
    def execute_agent_request(cls, request: AnalysisRequest):
        from .orchestration_service import execute_agent_request
        return execute_agent_request(request)

