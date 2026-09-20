"""
SatQuery AI — API Endpoints (Phase 7A)
Exposes /api/health, /api/tools, and /api/analyze.
Connects multipart HTTP requests directly to Phase 6 execute_agent_request orchestration.
Enforces GPU execution serialization via asyncio.Lock.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
import torch
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from ..agent.schemas import AnalysisRequest, OrchestrationResult
from ..agent.registry import list_tools
from ..services.orchestration_service import execute_agent_request
from ..services.upload_service import save_upload_file
from .schemas import HealthResponse, ToolDefinitionModel, AnalysisApiResponse

router = APIRouter()

# GPU concurrency lock: prevents simultaneous heavy model residency on 8 GB RTX 5050
_GPU_EXECUTION_LOCK = asyncio.Lock()


def _get_vram_telemetry() -> Dict[str, Any]:
    """Retrieves current GPU device and memory metrics."""
    if not torch.cuda.is_available():
        return {
            "gpu_available": False,
            "gpu_name": "CPU (CUDA unavailable)",
            "free_vram_mb": 0.0,
            "total_vram_mb": 0.0,
        }
    free, total = torch.cuda.mem_get_info()
    return {
        "gpu_available": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "free_vram_mb": round(free / (1024 ** 2), 2),
        "total_vram_mb": round(total / (1024 ** 2), 2),
    }


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Health check endpoint returning system readiness, GPU VRAM status, and registered tools.
    """
    vram = _get_vram_telemetry()
    tools = [t.tool_name for t in list_tools()]
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        gpu_available=vram["gpu_available"],
        gpu_name=vram["gpu_name"],
        free_vram_mb=vram["free_vram_mb"],
        total_vram_mb=vram["total_vram_mb"],
        registered_tools=tools,
    )


@router.get("/tools", response_model=List[ToolDefinitionModel])
async def get_tools():
    """
    Returns full tool registry catalog including schemas and parameter specifications.
    """
    tools = list_tools()
    results = []
    for t in tools:
        param_specs = {}
        for p_name, p_spec in t.permitted_parameters.items():
            param_specs[p_name] = {
                "name": p_spec.name,
                "type": p_spec.type,
                "default": p_spec.default,
                "description": p_spec.description,
                "min_value": p_spec.min_value,
                "max_value": p_spec.max_value,
                "allowed_values": p_spec.allowed_values,
            }
        results.append(
            ToolDefinitionModel(
                tool_name=t.tool_name,
                description=t.description,
                accepted_input_types=t.accepted_input_types,
                required_inputs=t.required_inputs,
                permitted_parameters=param_specs,
                model_or_engine=t.model_or_engine,
                output_type=t.output_type,
                evidence_type=t.evidence_type,
                confidence_supported=t.confidence_supported,
                resource_notes=t.resource_notes,
            )
        )
    return results


@router.post("/analyze", response_model=AnalysisApiResponse)
async def analyze_endpoint(
    query: str = Form(..., description="Natural language analytical question or command"),
    task: Optional[str] = Form(None, description="Optional explicit task override (VQA, GROUNDING, etc.)"),
    image: Optional[UploadFile] = File(None, description="Primary satellite image upload"),
    second_image: Optional[UploadFile] = File(None, description="Post-event image T2 for change detection"),
    sar_image: Optional[UploadFile] = File(None, description="SAR radar backscatter image upload"),
    parameters: Optional[str] = Form(None, description="Optional JSON-encoded tool parameter overrides"),
    image_path: Optional[str] = Form(None, description="Direct server filesystem path for primary image (sample fallback)"),
    second_image_path: Optional[str] = Form(None, description="Direct server filesystem path for second image (sample fallback)"),
    sar_image_path: Optional[str] = Form(None, description="Direct server filesystem path for SAR image (sample fallback)"),
    optical_image_path: Optional[str] = Form(None, description="Direct server filesystem path for Optical image (sample fallback)"),
):
    """
    Unified MVP endpoint for SatQuery AI.
    Accepts multipart/form-data inputs, handles staging, verifies security boundaries,
    and invokes the Phase 6 agent orchestrator under serialized GPU execution.
    """
    resolved_img_path = image_path
    resolved_second_img_path = second_image_path
    resolved_sar_img_path = sar_image_path
    resolved_optical_img_path = optical_image_path

    # Process uploaded files through upload staging service
    try:
        if image and image.filename:
            resolved_img_path = save_upload_file(image)
        if second_image and second_image.filename:
            resolved_second_img_path = save_upload_file(second_image)
        if sar_image and sar_image.filename:
            resolved_sar_img_path = save_upload_file(sar_image)
    except ValueError as val_err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "ERROR",
                "selected_tool": None,
                "model": "UploadValidator",
                "answer": str(val_err),
                "confidence": None,
                "evidence": None,
                "metadata": {"error_type": "INVALID_IMAGE"},
                "observable_execution_trace": [
                    {
                        "step": "INPUT_VALIDATION",
                        "status": "ERROR",
                        "model": "UploadValidator",
                        "latency_ms": 0.5,
                        "error": str(val_err),
                    }
                ],
                "latency_ms": 0.5,
                "error_type": "INVALID_IMAGE",
            },
        )

    # Parse parameters JSON string if supplied
    parsed_params: Dict[str, Any] = {}
    if parameters and parameters.strip():
        try:
            parsed_params = json.loads(parameters.strip())
            if not isinstance(parsed_params, dict):
                raise ValueError("Parameters must be a valid JSON object.")
        except Exception as json_err:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "ERROR",
                    "selected_tool": None,
                    "model": "ParameterParser",
                    "answer": f"Malformed parameters JSON: {json_err}",
                    "confidence": None,
                    "evidence": None,
                    "metadata": {"error_type": "INVALID_PARAMETER"},
                    "observable_execution_trace": [],
                    "latency_ms": 0.2,
                    "error_type": "INVALID_PARAMETER",
                },
            )

    # Construct standard Phase 6 AnalysisRequest
    request = AnalysisRequest(
        query=query,
        task=task,
        image_path=resolved_img_path,
        second_image_path=resolved_second_img_path,
        optical_image_path=resolved_optical_img_path,
        sar_image_path=resolved_sar_img_path,
        parameters=parsed_params,
    )

    # Execute request under GPU serialization lock to prevent concurrent VRAM contention
    async with _GPU_EXECUTION_LOCK:
        try:
            loop = asyncio.get_running_loop()
            result: OrchestrationResult = await loop.run_in_executor(None, execute_agent_request, request)
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "ERROR",
                    "selected_tool": None,
                    "model": "OrchestrationEngine",
                    "answer": f"Internal execution failure: {str(exc)}",
                    "confidence": None,
                    "evidence": None,
                    "metadata": {"error_type": "INTERNAL_ERROR"},
                    "observable_execution_trace": [
                        {
                            "step": "TOOL_EXECUTION",
                            "status": "ERROR",
                            "model": "OrchestrationEngine",
                            "latency_ms": 0.0,
                            "error": str(exc),
                        }
                    ],
                    "latency_ms": 0.0,
                    "error_type": "INTERNAL_ERROR",
                },
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result.to_dict(),
    )
