"""
SatQuery AI — API Endpoints (Phase 7A)
Exposes /api/health, /api/tools, and /api/analyze.
Connects multipart HTTP requests directly to Phase 6 execute_agent_request orchestration.
Enforces GPU execution serialization via asyncio.Lock.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import torch
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse

from ..agent.schemas import AnalysisRequest, OrchestrationResult
from ..agent.registry import list_tools
from ..services.orchestration_service import execute_agent_request
from ..services.upload_service import save_upload_file, cleanup_file, resolve_sample_path
from ..config import MAX_QUERY_CHARS, MAX_PENDING_REQUESTS
from .schemas import HealthResponse, ToolDefinitionModel, AnalysisApiResponse
from ..security import require_public_key
from uuid import uuid4

router = APIRouter()

# GPU concurrency lock: prevents simultaneous heavy model residency on 8 GB RTX 5050
_GPU_EXECUTION_LOCK = asyncio.Lock()
_pending_requests = 0


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
async def get_tools(_owner: str = Depends(require_public_key)):
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
    request: Request,
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
    input_metadata: Optional[str] = Form(None, description="JSON metadata keyed by image_path, second_image_path or sar_image_path; RGB bands are zero-based"),
    evaluation_mode: bool = Form(False, description="Require approved benchmark formats and verified pair grids"),
    _owner: str = Depends(require_public_key),
):
    global _pending_requests
    staged = []
    if len(query) > MAX_QUERY_CHARS:
        raise HTTPException(400, "Query exceeds 4000 characters.")
    if _pending_requests >= MAX_PENDING_REQUESTS:
        raise HTTPException(429, "Analysis queue is full; retry after current work completes.")
    _pending_requests += 1
    try:
        parsed_params = json.loads(parameters) if parameters else {}
        if not isinstance(parsed_params, dict):
            raise ValueError("Parameters must be a JSON object.")
        resolved = {}
        for key, upload, direct in [
            ("image_path", image, image_path),
            ("second_image_path", second_image, second_image_path),
            ("sar_image_path", sar_image, sar_image_path),
        ]:
            if upload and upload.filename:
                path = await asyncio.to_thread(save_upload_file, upload)
                staged.append(path)
            else:
                path = resolve_sample_path(direct)
            resolved[key] = path
        resolved["optical_image_path"] = resolve_sample_path(optical_image_path)
        from ..services.input_policy_service import prepare_inputs
        resolved, provenance = await asyncio.to_thread(prepare_inputs, resolved,
            json.loads(input_metadata) if input_metadata else {}, evaluation_mode, staged)
        request = AnalysisRequest(query=query, task=task, parameters=parsed_params, **resolved)
        async with _GPU_EXECUTION_LOCK:
            work = asyncio.ensure_future(asyncio.to_thread(execute_agent_request, request))
            try:
                result = await asyncio.shield(work)
            except asyncio.CancelledError:
                # Thread inference cannot be cancelled safely. Retain the GPU lock and
                # staged inputs until it finishes, even when the HTTP caller disconnects.
                await work
                raise
        result.metadata["query"] = query
        result.metadata["request_id"] = f"req-{uuid4().hex}"
        result.metadata["owner_id"] = _owner
        result.metadata["client_ip_hash"] = _owner
        result.metadata["input_provenance"] = provenance
        return result.to_dict()
    except (ValueError, TypeError) as exc:
        return JSONResponse(status_code=400, content={
            "status": "INVALID_INPUT", "selected_tool": None, "model": "InputValidator",
            "answer": str(exc), "confidence": None, "evidence": None, "metadata": {},
            "observable_execution_trace": [], "latency_ms": 0, "error_type": "INVALID_INPUT",
        })
    finally:
        for path in staged:
            cleanup_file(path)
        _pending_requests -= 1


@router.get("/evaluation")
async def evaluation_summary(_owner: str = Depends(require_public_key)):
    """Expose completed measured summaries; never use fallback numeric metrics."""
    from ..config import PROJECT_ROOT
    path = PROJECT_ROOT / "results" / "vqa_controlled_comparison.json"
    if not path.is_file():
        return {"status": "UNAVAILABLE", "message": "No completed controlled comparison is available."}
    with path.open(encoding="utf-8") as stream:
        report = json.load(stream)
    return {key: report.get(key) for key in ["status", "timestamp", "benchmark", "model", "adapter",
            "settings", "device", "dtype", "baseline", "adapted", "limitations", "latency_scope"]}


@router.get("/benchmarks/readiness")
async def benchmark_readiness(_owner: str = Depends(require_public_key)):
    """Expose local benchmark availability without claiming evaluation accuracy."""
    from ..config import PROJECT_ROOT
    manifests = {
        "CDVQA": PROJECT_ROOT / "data/benchmarks/cdvqa/manifest.json",
        "SEN1-2": PROJECT_ROOT / "data/benchmarks/sen1_2/manifest.json",
        "ISRO/SAC": PROJECT_ROOT / "data/benchmarks/isro/manifest.json",
    }
    report = {}
    for name, path in manifests.items():
        status_value = "READY" if path.is_file() else "NOT_INSTALLED"
        sample_count = None
        if path.is_file():
            try:
                with path.open(encoding="utf-8") as stream:
                    sample_count = len(json.load(stream).get("samples", []))
            except (OSError, ValueError, TypeError):
                status_value = "INVALID"
        result_key = {"CDVQA": "cdvqa", "SEN1-2": "sen1_2", "ISRO/SAC": "isro"}[name]
        result_path = PROJECT_ROOT / "results" / f"{result_key}_prescribed.json"
        if result_path.is_file():
            status_value = "EVALUATED"
        report[name] = {"status": status_value, "manifest": str(path.relative_to(PROJECT_ROOT)), "sample_count": sample_count}
    return report
