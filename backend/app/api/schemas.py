"""
SatQuery AI — API Request & Response Schemas (Phase 7A)
Pydantic schemas for FastAPI endpoints conforming to the Phase 6 OrchestrationResult contract.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service status (healthy, degraded)")
    version: str = Field("1.0.0", description="API version")
    gpu_available: bool = Field(..., description="Whether CUDA GPU acceleration is available")
    gpu_name: str = Field(..., description="GPU model name")
    free_vram_mb: float = Field(..., description="Currently available GPU VRAM in MB")
    total_vram_mb: float = Field(..., description="Total GPU VRAM in MB")
    registered_tools: List[str] = Field(..., description="List of registered tool names")


class ToolParameterSpecModel(BaseModel):
    name: str
    type: str
    default: Any
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None


class ToolDefinitionModel(BaseModel):
    tool_name: str
    description: str
    accepted_input_types: List[str]
    required_inputs: List[str]
    permitted_parameters: Dict[str, ToolParameterSpecModel]
    model_or_engine: str
    output_type: str
    evidence_type: str
    confidence_supported: bool
    resource_notes: str


class ConfidenceDetailModel(BaseModel):
    level: str = Field(..., description="LOW, MEDIUM, or HIGH evidence strength category")
    score: Optional[float] = Field(None, description="Uncalibrated evidence-strength heuristic score (0.00-1.00)")
    type: str = Field("model-derived-uncalibrated", description="Telemetry classification type")
    explanation: str = Field(..., description="Auditable breakdown of evidence signals and uncertainty boundaries")
    signals: Optional[Dict[str, Any]] = Field(None, description="Granular operational signal metrics")


class AnalysisApiResponse(BaseModel):
    status: str = Field(..., description="Execution status: SUCCESS, ERROR, INVALID_INPUT, NEEDS_CLARIFICATION, UNREGISTERED_TOOL")
    selected_tool: Optional[str] = Field(None, description="Tool selected by AgentRouter (VQA, GROUNDING, CHANGE_DETECTION, OPTICAL_SAR)")
    model: str = Field(..., description="Specialist model or orchestrator name")
    answer: str = Field(..., description="Human-readable analytical answer or error message")
    confidence: Optional[Union[ConfidenceDetailModel, Dict[str, Any], float]] = Field(None, description="Model-derived, uncalibrated evidence strength heuristic or legacy numeric score")
    image_description: Optional[str] = Field(None, description="Concise overall scene description and visual interpretation")
    visual_evidence: Optional[List[Dict[str, str]]] = Field(None, description="Dynamic list of observable or qualified visual evidence features")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Structured spatial evidence payload (boxes, masks, cross-modal stats)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Operational metadata and evaluation notes")
    observable_execution_trace: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step observable pipeline trace")
    latency_ms: float = Field(..., description="Total pipeline latency in milliseconds")
    error_type: Optional[str] = Field(None, description="Diagnostic error category if non-successful")
