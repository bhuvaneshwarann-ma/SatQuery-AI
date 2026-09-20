"""
SatQuery AI — Deterministic Agent Router (Phase 4)
Performs rule-based intent parsing, input asset validation, ambiguity detection,
and strict parameter sanitation against the Predefined Tool Registry.
"""

import re
from typing import Optional, List, Tuple
from .schemas import AnalysisRequest, ToolSelection, TaskType, RoutingStatus
from .registry import is_tool_registered, get_tool, validate_and_filter_parameters


class AgentRouter:
    """
    Deterministic query and task orchestrator.
    Maps natural language queries and explicit task requests to certified specialist AI tools.
    """

    # Grounding intents: Locational, pointing, bounding, detection requests
    GROUNDING_PATTERNS = [
        r"\b(locate|find|detect|where\s+is|where\s+are|point\s+out|bounding\s+box|box\s+the|coordinates\s+of)\b",
        r"\b(show\s+me\s+the\s+location|pinpoint)\b",
    ]

    # Change detection intents: Temporal, delta, differential, before/after
    CHANGE_PATTERNS = [
        r"\b(change|changed|difference|differences|diff|between\s+(these\s+)?(two\s+)?images)\b",
        r"\b(between\s+t1\s+and\s+t2|before\s+and\s+after|new\s+construction|demolished|deforestation)\b",
        r"\b(what\s+changed|identify\s+new|expansion|loss|gain)\b",
    ]

    # Optical-SAR intents: Radar, backscatter, cross-sensor, SAR, microwave, through clouds
    OPTICAL_SAR_PATTERNS = [
        r"\b(sar|radar|microwave|backscatter|cross-modal|optical\s+and\s+sar|sar\s+and\s+optical)\b",
        r"\b(through\s+clouds|cloud\s+penetrat|all-weather|specular\s+reflection)\b",
    ]

    # VQA intents: Descriptive, counting, qualitative, identification
    VQA_PATTERNS = [
        r"\b(what\s+is|what\s+are|what|describe|description|caption|overview|how\s+many|count)\b",
        r"\b(is\s+there|are\s+there|tell\s+me\s+about|scene\s+type|land\s+cover|environment)\b",
    ]

    # Ambiguous phrases lacking analytical direction
    AMBIGUOUS_PATTERNS = [
        r"^(process|process\s+this|run|analyze|analyze\s+this|check|inspect|hello|hi|help|test)$",
        r"^(what|image|satellite|do\s+something|query)$",
    ]

    @classmethod
    def classify_intent(cls, query: str) -> Tuple[Optional[TaskType], str]:
        """
        Deduces task intent from query text using hierarchical, domain-specific rule evaluation.
        Returns: (TaskType or None, rationale_string)
        """
        clean_query = query.strip().lower()

        # 1. Check for ambiguity / non-descriptive commands first
        for pat in cls.AMBIGUOUS_PATTERNS:
            if re.search(pat, clean_query):
                return None, "Query is too generic or ambiguous to identify a concrete analytical task."

        if len(clean_query.split()) <= 1 and clean_query not in ["ships", "boats", "water", "river"]:
            return None, "Single-word query lacks operational intent."

        # 2. Check for Optical-SAR signals
        for pat in cls.OPTICAL_SAR_PATTERNS:
            if re.search(pat, clean_query):
                return TaskType.OPTICAL_SAR, "Query contains multi-sensor radar / optical-SAR keywords."

        # 3. Check for Bi-Temporal Change signals
        for pat in cls.CHANGE_PATTERNS:
            if re.search(pat, clean_query):
                return TaskType.CHANGE_DETECTION, "Query contains temporal delta / change comparison keywords."

        # 4. Check for Visual Grounding / Localization signals
        for pat in cls.GROUNDING_PATTERNS:
            if re.search(pat, clean_query):
                return TaskType.GROUNDING, "Query requests spatial localization, detection, or coordinates."

        # 5. Check for General VQA / Captioning signals
        for pat in cls.VQA_PATTERNS:
            if re.search(pat, clean_query):
                return TaskType.VQA, "Query requests visual question answering, counting, or scene description."

        return None, "Unable to infer analytical intent from query."

    @classmethod
    def route(cls, request: AnalysisRequest) -> ToolSelection:
        """
        Deterministic routing pipeline:
        1. Explicit Task Override validation (if provided)
        2. Query Intent Classification
        3. Input Asset Prerequisite Validation
        4. Parameter Sanitation via Predefined Registry
        5. Emission of verified ToolSelection contract
        """
        # Step 1: Explicit Task Request Handling
        target_task: Optional[TaskType] = None
        routing_reason: str = ""

        if request.task:
            normalized_task_name = request.task.strip().upper()
            if not is_tool_registered(normalized_task_name):
                return ToolSelection(
                    selected_tool=None,
                    task=None,
                    status=RoutingStatus.UNREGISTERED_TOOL,
                    reason=f"Requested task/tool '{request.task}' is not registered in Predefined Tool Registry.",
                    validation_errors=[f"Unregistered tool '{request.task}'. Permitted tools: ['VQA', 'GROUNDING', 'CHANGE_DETECTION', 'OPTICAL_SAR']"]
                )
            target_task = TaskType(normalized_task_name)
            routing_reason = f"Explicitly requested task '{target_task.value}'."
        else:
            # Step 2: Autonomous Intent Classification
            inferred_task, reason = cls.classify_intent(request.query)
            if inferred_task is None:
                return ToolSelection(
                    selected_tool=None,
                    task=None,
                    status=RoutingStatus.NEEDS_CLARIFICATION,
                    reason=reason,
                    clarification_prompt="Please specify your objective: (1) Answer question (VQA), (2) Locate objects (Grounding), (3) Compare bi-temporal changes, or (4) Analyze Optical+SAR."
                )
            target_task = inferred_task
            routing_reason = reason

        # Step 3: Input Asset Prerequisite Validation
        tool_name = target_task.value
        tool_def = get_tool(tool_name)
        if not tool_def:
            return ToolSelection(
                selected_tool=None,
                task=target_task,
                status=RoutingStatus.UNREGISTERED_TOOL,
                reason=f"Tool definition for '{tool_name}' not found in registry."
            )

        validation_errors: List[str] = []
        provided_inputs: List[str] = []

        # Check required inputs specific to each tool
        if tool_name == "VQA":
            if request.image_path:
                provided_inputs.append("image_path")
            else:
                validation_errors.append("VQA requires a valid 'image_path'.")

        elif tool_name == "GROUNDING":
            if request.image_path:
                provided_inputs.append("image_path")
            else:
                validation_errors.append("Grounding requires a valid 'image_path' to localize objects.")

        elif tool_name == "CHANGE_DETECTION":
            if request.image_path:
                provided_inputs.append("image_path")
            else:
                validation_errors.append("Change Detection requires baseline image T1 ('image_path').")

            if request.second_image_path:
                provided_inputs.append("second_image_path")
            else:
                validation_errors.append("Change Detection requires post-event image T2 ('second_image_path').")

        elif tool_name == "OPTICAL_SAR":
            # Optical image can be supplied in optical_image_path or image_path
            opt_path = request.optical_image_path or request.image_path
            if opt_path:
                provided_inputs.append("optical_image_path")
            else:
                validation_errors.append("Optical-SAR analysis requires an optical image ('optical_image_path' or 'image_path').")

            if request.sar_image_path:
                provided_inputs.append("sar_image_path")
            else:
                validation_errors.append("Optical-SAR analysis requires a SAR radar image ('sar_image_path').")

        if validation_errors:
            return ToolSelection(
                selected_tool=tool_name,
                task=target_task,
                status=RoutingStatus.INVALID_INPUT,
                reason=f"Input validation failed for tool '{tool_name}'.",
                required_inputs=tool_def.required_inputs,
                provided_inputs=provided_inputs,
                validation_errors=validation_errors
            )

        # Step 4: Parameter Sanitation against Predefined Registry Schema
        sanitized_params, param_warnings = validate_and_filter_parameters(tool_name, request.parameters)

        return ToolSelection(
            selected_tool=tool_name,
            task=target_task,
            status=RoutingStatus.ROUTED,
            reason=routing_reason,
            required_inputs=tool_def.required_inputs,
            provided_inputs=provided_inputs,
            permitted_parameters=sanitized_params,
            validation_errors=param_warnings
        )
