"""
SatQuery AI — Agent Schemas (Phase 3 & Phase 4 Upgrade)
Defines structured, observable data contracts for request ingestion,
structured multi-tool task planning, deterministic tool selection,
tool execution results, evidence fusion, and execution tracing.
Uses Python dataclasses for zero-dependency runtime reliability.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field


class TaskType(str, Enum):
    VQA = "VQA"
    GROUNDING = "GROUNDING"
    CHANGE_DETECTION = "CHANGE_DETECTION"
    OPTICAL_SAR = "OPTICAL_SAR"
    MULTI_TOOL = "MULTI_TOOL"


class RoutingStatus(str, Enum):
    ROUTED = "ROUTED"
    INVALID_INPUT = "INVALID_INPUT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    UNSUPPORTED_TASK = "UNSUPPORTED_TASK"
    UNREGISTERED_TOOL = "UNREGISTERED_TOOL"


@dataclass
class TaskPlanStep:
    """A discrete, certifiable execution step in a structured task plan."""
    tool: str
    purpose: str
    required_inputs: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "purpose": self.purpose,
            "required_inputs": self.required_inputs,
            "parameters": self.parameters,
        }


@dataclass
class StructuredTaskPlan:
    """
    Structured Task Plan produced by Agent Planner and validated by Policy Firewall.
    Conforms to hackathon specification:
    {
        "intent": "CHANGE_ANALYSIS",
        "target": "built_up_area",
        "requires_temporal_pair": true,
        "requires_spatial_evidence": true,
        "plan": [
            {"tool": "CHANGE_DETECTION", "purpose": "identify changed regions"},
            {"tool": "GROUNDING", "purpose": "localize target"},
            {"tool": "VQA", "purpose": "describe change"}
        ]
    }
    """
    intent: str
    target: Optional[str] = None
    requires_temporal_pair: bool = False
    requires_spatial_evidence: bool = False
    plan: List[TaskPlanStep] = field(default_factory=list)
    is_multi_tool: bool = False
    policy_validated: bool = False
    policy_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "target": self.target,
            "requires_temporal_pair": self.requires_temporal_pair,
            "requires_spatial_evidence": self.requires_spatial_evidence,
            "is_multi_tool": self.is_multi_tool,
            "policy_validated": self.policy_validated,
            "policy_notes": self.policy_notes,
            "plan": [step.to_dict() for step in self.plan],
        }


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
    Output of the deterministic Agent Router & Planner.
    Records which tool or multi-tool plan was chosen, the rationale category,
    input checks, sanitized parameters, and the structured task plan.
    """
    status: RoutingStatus
    reason: str
    selected_tool: Optional[str] = None
    task: Optional[TaskType] = None
    task_plan: Optional[StructuredTaskPlan] = None
    required_inputs: List[str] = field(default_factory=list)
    provided_inputs: List[str] = field(default_factory=list)
    permitted_parameters: Dict[str, Any] = field(default_factory=dict)
    clarification_prompt: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Standard output contract for specialist tools."""
    tool_name: str
    status: str
    answer: str
    model: str
    evidence: Optional[Dict[str, Any]] = None
    confidence: Optional[Union[Dict[str, Any], float]] = None
    image_description: Optional[str] = None
    visual_evidence: Optional[List[Dict[str, str]]] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTraceEntry:
    """Observable Execution Trace Entry."""
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
    Unified end-to-end response envelope produced by the Agent Orchestrator.
    Consolidates tool execution output, structured task plan, observable execution trace,
    evidence, confidence metrics, rich image interpretation, and telemetry for auditability.
    """
    status: str
    selected_tool: Optional[str]
    model: str
    answer: str
    confidence: Optional[Union[Dict[str, Any], float]] = None
    evidence: Optional[Dict[str, Any]] = None
    image_description: Optional[str] = None
    visual_evidence: Optional[List[Dict[str, str]]] = None
    task_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    observable_execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    error_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        trace = self.execution_trace if self.execution_trace else self.observable_execution_trace
        tools = self.tools_used if self.tools_used else ([self.selected_tool] if self.selected_tool else [])
        return {
            "query": self.metadata.get("query", ""),
            "status": self.status,
            "selected_tool": self.selected_tool,
            "tools_used": tools,
            "model": self.model,
            "answer": self.answer,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "evidence_items": self.evidence_items,
            "image_description": self.image_description,
            "visual_evidence": self.visual_evidence,
            "task_plan": self.task_plan,
            "execution_trace": trace,
            "observable_execution_trace": trace,
            "limitations": self.limitations,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "error_type": self.error_type,
        }


# Alias for backward compatibility and architectural alignment
AnalysisResponse = OrchestrationResult
