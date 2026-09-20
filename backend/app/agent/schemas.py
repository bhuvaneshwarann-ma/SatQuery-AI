"""
SatQuery AI — Agent Schemas (Phase 4)
Defines structured, observable data contracts for request ingestion,
deterministic tool selection, tool execution results, and execution tracing.
Uses Python dataclasses for zero-dependency runtime reliability.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


class TaskType(str, Enum):
    VQA = "VQA"
    GROUNDING = "GROUNDING"
    CHANGE_DETECTION = "CHANGE_DETECTION"
    OPTICAL_SAR = "OPTICAL_SAR"


class RoutingStatus(str, Enum):
    ROUTED = "ROUTED"
    INVALID_INPUT = "INVALID_INPUT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    UNSUPPORTED_TASK = "UNSUPPORTED_TASK"
    UNREGISTERED_TOOL = "UNREGISTERED_TOOL"


@dataclass
class AnalysisRequest:
    """
    User or API request envelope.
    Contains user query, asset file references, optional explicit task override,
    and optional user parameters (strictly checked against permitted schemas).
    """
    query: str
    task: Optional[str] = None
    image_path: Optional[str] = None
    second_image_path: Optional[str] = None
    optical_image_path: Optional[str] = None
    sar_image_path: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSelection:
    """
    Output of the deterministic Agent Router.
    Records which tool was chosen, the rationale category, input checks,
    and sanitized, validated parameters.
    """
    status: RoutingStatus
    reason: str
    selected_tool: Optional[str] = None
    task: Optional[TaskType] = None
    required_inputs: List[str] = field(default_factory=list)
    provided_inputs: List[str] = field(default_factory=list)
    permitted_parameters: Dict[str, Any] = field(default_factory=dict)
    clarification_prompt: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """
    Standard output contract for specialist tools.
    """
    tool_name: str
    status: str
    answer: str
    model: str
    evidence: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTraceEntry:
    """
    Observable Execution Trace Entry.
    Contains strictly observable pipeline telemetry for auditing.
    DOES NOT contain hidden LLM chain-of-thought, private system prompts, or ungrounded internal reasoning.
    """
    step: str
    status: str
    selected_task: Optional[str] = None
    selected_tool: Optional[str] = None
    model: Optional[str] = None
    permitted_parameters: Dict[str, Any] = field(default_factory=dict)
    input_references: List[str] = field(default_factory=list)
    latency_ms: Optional[float] = None
    output_reference: Optional[str] = None
    evidence_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "status": self.status,
            "selected_task": self.selected_task,
            "selected_tool": self.selected_tool,
            "model": self.model,
            "permitted_parameters": self.permitted_parameters,
            "input_references": self.input_references,
            "latency_ms": self.latency_ms,
            "output_reference": self.output_reference,
            "evidence_reference": self.evidence_reference,
        }


@dataclass
class OrchestrationResult:
    """
    Unified end-to-end response envelope produced by the Agent Orchestrator (Phase 6).
    Consolidates tool execution output, observable execution trace, evidence,
    and operational telemetry for auditability.
    """
    status: str
    selected_tool: Optional[str]
    model: str
    answer: str
    confidence: Optional[float]
    evidence: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    observable_execution_trace: List[Dict[str, Any]]
    latency_ms: float
    error_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "selected_tool": self.selected_tool,
            "model": self.model,
            "answer": self.answer,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "observable_execution_trace": self.observable_execution_trace,
            "latency_ms": self.latency_ms,
            "error_type": self.error_type,
        }
