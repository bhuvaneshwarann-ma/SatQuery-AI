"""Compatibility facade; all analytical policy is owned by the orchestrator."""
from dataclasses import fields
from ..agent.schemas import ToolResult, ExecutionTraceEntry
from .orchestration_service import execute_agent_request


class AnalysisService:
    @classmethod
    def analyze(cls, request):
        result = execute_agent_request(request)
        tool_result = ToolResult(
            tool_name=result.selected_tool or "ROUTER", status=result.status,
            model=result.model, answer=result.answer, evidence=result.evidence,
            confidence=result.confidence, image_description=result.image_description,
            visual_evidence=result.visual_evidence, latency_ms=result.latency_ms,
            metadata=result.metadata,
        )
        allowed = {field.name for field in fields(ExecutionTraceEntry)}
        trace = [ExecutionTraceEntry(**{k:v for k,v in entry.items() if k in allowed})
                 for entry in result.observable_execution_trace]
        return tool_result, trace

    execute_agent_request = staticmethod(execute_agent_request)
