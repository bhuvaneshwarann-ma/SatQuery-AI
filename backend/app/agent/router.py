"""
SatQuery AI — Deterministic Agent Router & Multi-Tool Planner (Phase 3 Upgrade)
Performs rule-based intent parsing, compound multi-specialist task planning,
input asset validation, ambiguity detection, and strict parameter sanitation
against the Predefined Tool Registry via a deterministic policy engine.
"""

import re
from typing import Optional, List, Tuple, Dict, Any
from .schemas import (
    AnalysisRequest,
    ToolSelection,
    TaskType,
    RoutingStatus,
    TaskPlanStep,
    StructuredTaskPlan,
)
from .registry import is_tool_registered, get_tool, validate_and_filter_parameters


class AgentRouter:
    """
    Deterministic query interpreter, multi-tool planner, and policy firewall.
    Maps natural language queries to structured, certifiable execution plans
    consisting of registered specialist AI tools.
    """

    # Counting guardrail intents: numerical quantification, enumeration requests
    COUNT_PATTERNS = [
        r"\bhow\s+many\b",
        r"\bcount\b",
        r"\bnumber\s+of\b",
        r"\btotal\s+(?:number\s+of\s+)?(ships|buildings|vehicles|aircraft|planes|vessels|cars|structures|boats|ports|runways|targets)\b",
    ]

    # Multi-tool / Compound intents: queries combining temporal delta, spatial target, and description
    COMPOUND_CHANGE_PATTERNS = [
        r"(?=.*\b(what\s+changed|compare|difference|changes?)\b)(?=.*\b(built[- ]?up|buildings?|structures?|urban|infrastructure|area)\b)(?=.*\b(where|locate|describe|between|dates)\b)",
        r"(?=.*\b(compare\s+these\s+two\s+dates|between\s+(these\s+)?(two\s+)?dates)\b)(?=.*\b(where|identify|locate)\b)(?=.*\b(describe|explain|change)\b)",
        r"(?=.*\b(detect\s+change|identify\s+change)\b)(?=.*\b(locate|where|target)\b)(?=.*\b(describe|summary)\b)",
    ]

    # Grounding intents: Locational, pointing, bounding, detection requests
    GROUNDING_PATTERNS = [
        r"\b(locate|find|detect|where\s+is|where\s+are|point\s+out|bounding\s+box|box\s+the|coordinates\s+of)\b",
        r"\b(show\s+me\s+the\s+location|pinpoint)\b",
    ]

    # Change detection intents: Temporal, delta, differential, before/after
    CHANGE_PATTERNS = [
        r"\b(changes?|changed|difference|differences|diff|between\s+(these\s+)?(two\s+)?(images|dates))\b",
        r"\b(between\s+t1\s+and\s+t2|before\s+and\s+after|new\s+construction|demolished|deforestation)\b",
        r"\b(what\s+changed|identify\s+(new|changes?)|expansion|loss|gain|compare\s+(these\s+)?(two\s+)?(images|dates))\b",
    ]

    # Optical-SAR intents: Radar, backscatter, cross-sensor, SAR, microwave, through clouds
    OPTICAL_SAR_PATTERNS = [
        r"\b(sar|radar|microwave|backscatter|cross-modal|optical\s+and\s+sar|sar\s+and\s+optical)\b",
        r"\b(through\s+clouds|cloud\s+penetrat|all-weather|specular\s+reflection)\b",
    ]

    # VQA intents: Descriptive, qualitative, identification
    VQA_PATTERNS = [
        r"\b(what\s+is|what\s+are|what\s+type|describe|description|caption|overview)\b",
        r"\b(is\s+there|are\s+there|tell\s+me\s+about|scene\s+type|land\s+cover|environment)\b",
    ]

    # Ambiguous phrases lacking analytical direction
    AMBIGUOUS_PATTERNS = [
        r"^(process|process\s+this|run|analyze|analyze\s+this|check|inspect|hello|hi|help|test)$",
        r"^(what|image|satellite|do\s+something|query)$",
    ]

    @classmethod
    def extract_target_entity(cls, query: str) -> Optional[str]:
        """Extracts spatial target entity from query (e.g. built_up_area, ships, port, vehicles, aircraft)."""
        clean = query.lower()
        if "built-up" in clean or "built up" in clean:
            return "built_up_area"
        if "building" in clean or "house" in clean or "structure" in clean:
            return "buildings"
        if "ship" in clean or "boat" in clean or "vessel" in clean:
            return "ships"
        if "vehicle" in clean or "car" in clean or "truck" in clean or "automobile" in clean:
            return "vehicles"
        if "aircraft" in clean or "plane" in clean or "airplane" in clean or "jet" in clean:
            return "aircraft"
        if "port" in clean or "berth" in clean or "dock" in clean or "harbor" in clean:
            return "port_infrastructure"
        if "runway" in clean or "airport" in clean:
            return "runway"
        if "road" in clean or "highway" in clean:
            return "roads"
        if "forest" in clean or "tree" in clean or "vegetation" in clean:
            return "vegetation"
        return None

    @classmethod
    def plan_query(cls, request: AnalysisRequest) -> Tuple[Optional[StructuredTaskPlan], str]:
        """
        Interprets natural language query and formulates a structured task plan.
        Supports both simple single-tool queries and complex multi-tool queries.
        """
        clean_query = (request.query or "").strip().lower()

        # 1. Ambiguity check: detect underspecified or vague requests
        clean_text = re.sub(r"[?!.,;:]", "", clean_query).strip()
        if re.search(r"^(what\s+changed(\s+here)?|identify\s+changes?)$", clean_text) and not request.second_image_path:
            return None, "Ambiguous change query: multiple dates are required to analyze changes. Please provide a second temporal image or specify features (buildings, roads, vegetation) to inspect."

        for pat in cls.AMBIGUOUS_PATTERNS:
            if re.search(pat, clean_text):
                return None, "Query is too generic or ambiguous to identify a concrete analytical task."

        if len(clean_query.split()) <= 1 and clean_query not in ["ships", "boats", "water", "river", "buildings"]:
            return None, "Single-word query lacks operational intent."

        # 2. Check for Compound / Multi-Tool queries first
        is_compound = any(re.search(pat, clean_query) for pat in cls.COMPOUND_CHANGE_PATTERNS)
        # Also check if query has both temporal change indicators and localization or description indicators
        has_temporal = bool(re.search(r"\b(change|dates|between|before|after|t1|t2)\b", clean_query))
        has_loc = bool(re.search(r"\b(where|locate|built[- ]?up|buildings?|target)\b", clean_query))
        has_desc = bool(re.search(r"\b(describe|what\s+changed|explain|summary)\b", clean_query))

        if is_compound or (has_temporal and has_loc and has_desc):
            target = cls.extract_target_entity(clean_query) or "built_up_area"
            plan = StructuredTaskPlan(
                intent="CHANGE_ANALYSIS",
                target=target,
                requires_temporal_pair=True,
                requires_spatial_evidence=True,
                is_multi_tool=True,
                plan=[
                    TaskPlanStep(
                        tool="CHANGE_DETECTION",
                        purpose="identify changed regions between temporal pair",
                        required_inputs=["image_path", "second_image_path"],
                    ),
                    TaskPlanStep(
                        tool="GROUNDING",
                        purpose=f"localize target '{target}' in the scene",
                        required_inputs=["image_path"],
                    ),
                    TaskPlanStep(
                        tool="VQA",
                        purpose="describe the observed change across identified regions",
                        required_inputs=["image_path"],
                    ),
                ]
            )
            return plan, "Multi-tool compound query identified: CHANGE_DETECTION -> GROUNDING -> VQA."

        # 3. Check Counting Guardrail: Route numerical queries to GROUNDING to derive count from validated spatial detections
        is_counting = any(re.search(pat, clean_query) for pat in cls.COUNT_PATTERNS)
        if is_counting:
            target = cls.extract_target_entity(clean_query) or "target objects"
            plan = StructuredTaskPlan(
                intent="OBJECT_COUNTING",
                target=target,
                requires_temporal_pair=False,
                requires_spatial_evidence=True,
                is_multi_tool=False,
                plan=[
                    TaskPlanStep(
                        tool="GROUNDING",
                        purpose=f"localize and count target '{target}' via spatial bounding boxes",
                        required_inputs=["image_path"],
                        parameters={"is_counting_query": True, "target_entity": target}
                    )
                ]
            )
            return plan, "Counting guardrail active: routed numerical query to GROUNDING to derive count from validated spatial detections."

        # 3. Check for Optical-SAR signals
        for pat in cls.OPTICAL_SAR_PATTERNS:
            if re.search(pat, clean_query):
                plan = StructuredTaskPlan(
                    intent="OPTICAL_SAR_ANALYSIS",
                    requires_temporal_pair=False,
                    requires_spatial_evidence=False,
                    is_multi_tool=False,
                    plan=[
                        TaskPlanStep(
                            tool="OPTICAL_SAR",
                            purpose="correlate optical reflectance with SAR microwave radar backscatter",
                            required_inputs=["optical_image_path", "sar_image_path"],
                        )
                    ]
                )
                return plan, "Query contains multi-sensor radar / optical-SAR keywords."

        # 4. Check for Bi-Temporal Change signals
        for pat in cls.CHANGE_PATTERNS:
            if re.search(pat, clean_query):
                plan = StructuredTaskPlan(
                    intent="BI_TEMPORAL_CHANGE_DETECTION",
                    requires_temporal_pair=True,
                    requires_spatial_evidence=True,
                    is_multi_tool=False,
                    plan=[
                        TaskPlanStep(
                            tool="CHANGE_DETECTION",
                            purpose="detect differential changes between baseline T1 and post-event T2 rasters",
                            required_inputs=["image_path", "second_image_path"],
                        )
                    ]
                )
                return plan, "Query contains temporal delta / change comparison keywords."

        # 5. Check for Visual Grounding / Localization signals
        for pat in cls.GROUNDING_PATTERNS:
            if re.search(pat, clean_query):
                target = cls.extract_target_entity(clean_query)
                plan = StructuredTaskPlan(
                    intent="OBJECT_LOCALIZATION",
                    target=target,
                    requires_temporal_pair=False,
                    requires_spatial_evidence=True,
                    is_multi_tool=False,
                    plan=[
                        TaskPlanStep(
                            tool="GROUNDING",
                            purpose=f"localize target '{target or clean_query}' with bounding boxes",
                            required_inputs=["image_path"],
                        )
                    ]
                )
                return plan, "Query requests spatial localization, detection, or coordinates."

        # 6. Check for General VQA / Captioning signals
        for pat in cls.VQA_PATTERNS:
            if re.search(pat, clean_query):
                plan = StructuredTaskPlan(
                    intent="VISUAL_QUESTION_ANSWERING",
                    requires_temporal_pair=False,
                    requires_spatial_evidence=False,
                    is_multi_tool=False,
                    plan=[
                        TaskPlanStep(
                            tool="VQA",
                            purpose="answer analytical question regarding remote sensing scene",
                            required_inputs=["image_path"],
                        )
                    ]
                )
                return plan, "Query requests visual question answering, counting, or scene description."

        return None, "Unable to infer analytical intent from query."

    @classmethod
    def route(cls, request: AnalysisRequest) -> ToolSelection:
        """
        Deterministic routing and policy validation pipeline:
        1. Explicit Task Override validation (if provided)
        2. Query Intent Classification & Structured Task Plan Generation
        3. Deterministic Policy Firewall Validation (Tools & Parameters)
        4. Input Asset Prerequisite Verification
        5. Emission of verified ToolSelection contract
        """
        # Step 1: Explicit Task Request Handling
        if request.task:
            normalized_task_name = request.task.strip().upper()
            if not is_tool_registered(normalized_task_name):
                return ToolSelection(
                    selected_tool=None,
                    task=None,
                    status=RoutingStatus.UNREGISTERED_TOOL,
                    reason=f"Requested task/tool '{request.task}' is not registered in Predefined Tool Registry.",
                    validation_errors=[
                        f"Unregistered tool '{request.task}'. Permitted tools: ['VQA', 'GROUNDING', 'CHANGE_DETECTION', 'OPTICAL_SAR']"
                    ],
                )
            target_task = TaskType(normalized_task_name)
            tool_def = get_tool(normalized_task_name)

            # Build single-step plan for explicit task
            plan = StructuredTaskPlan(
                intent=f"EXPLICIT_{normalized_task_name}",
                requires_temporal_pair=(normalized_task_name == "CHANGE_DETECTION"),
                requires_spatial_evidence=(normalized_task_name in ["GROUNDING", "CHANGE_DETECTION"]),
                is_multi_tool=False,
                plan=[
                    TaskPlanStep(
                        tool=normalized_task_name,
                        purpose=f"execute explicitly requested {normalized_task_name} specialist",
                        required_inputs=tool_def.required_inputs if tool_def else ["image_path"],
                    )
                ]
            )
            routing_reason = f"Explicitly requested task '{target_task.value}'."
        else:
            # Step 2: Autonomous Intent Classification & Plan Generation
            plan, routing_reason = cls.plan_query(request)
            if plan is None:
                clean_q = (request.query or "").strip().lower()
                if "change" in clean_q or "diff" in clean_q:
                    prompt = "I can compare the images for changes. Do you want all detectable changes, buildings, roads, vegetation, or another feature?"
                else:
                    prompt = (
                        "Please specify your objective: (1) Answer question (VQA), "
                        "(2) Locate objects (Grounding), (3) Compare bi-temporal changes, or (4) Analyze Optical+SAR."
                    )
                return ToolSelection(
                    selected_tool=None,
                    task=None,
                    status=RoutingStatus.NEEDS_CLARIFICATION,
                    reason=routing_reason,
                    clarification_prompt=prompt,
                )
            
            if plan.is_multi_tool:
                target_task = TaskType.MULTI_TOOL
            else:
                primary_tool = plan.plan[0].tool
                target_task = TaskType(primary_tool)

        # Step 3: Deterministic Policy Firewall Validation
        validation_errors: List[str] = []
        provided_inputs: List[str] = []

        if request.image_path:
            provided_inputs.append("image_path")
        if request.second_image_path:
            provided_inputs.append("second_image_path")
        if request.optical_image_path:
            provided_inputs.append("optical_image_path")
        if request.sar_image_path:
            provided_inputs.append("sar_image_path")

        # Validate each step in the task plan against registry and asset prerequisites
        sanitized_params_per_step: Dict[str, Any] = {}
        all_required_inputs: List[str] = []

        for step in plan.plan:
            tool_name = step.tool
            tool_def = get_tool(tool_name)
            if not tool_def:
                validation_errors.append(f"Tool '{tool_name}' in plan is not registered in Tool Registry.")
                continue

            all_required_inputs.extend(tool_def.required_inputs)

            # Check required inputs
            if tool_name == "VQA" and not request.image_path:
                validation_errors.append("VQA requires a valid 'image_path'.")
            elif tool_name == "GROUNDING" and not request.image_path:
                validation_errors.append("Grounding requires a valid 'image_path' to localize objects.")
            elif tool_name == "CHANGE_DETECTION":
                if not request.image_path:
                    validation_errors.append("Change Detection requires baseline image T1 ('image_path').")
                if not request.second_image_path:
                    validation_errors.append("Change Detection requires post-event image T2 ('second_image_path').")
            elif tool_name == "OPTICAL_SAR":
                opt_path = request.optical_image_path or request.image_path
                if not opt_path:
                    validation_errors.append("Optical-SAR analysis requires an optical image ('optical_image_path' or 'image_path').")
                if not request.sar_image_path:
                    validation_errors.append("Optical-SAR analysis requires a SAR radar image ('sar_image_path').")

            # Validate parameters through firewall
            step_params, param_warnings = validate_and_filter_parameters(tool_name, request.parameters)
            step.parameters = step_params
            sanitized_params_per_step.update(step_params)
            validation_errors.extend(param_warnings)

        all_required_inputs = list(dict.fromkeys(all_required_inputs))

        primary_tool_name = "MULTI_TOOL" if plan.is_multi_tool else plan.plan[0].tool

        fatal_errors = [e for e in validation_errors if not e.startswith("Ignored unpermitted parameter")]
        param_warnings_list = [e for e in validation_errors if e.startswith("Ignored unpermitted parameter")]

        if fatal_errors:
            plan.policy_validated = False
            plan.policy_notes = fatal_errors
            return ToolSelection(
                selected_tool=primary_tool_name,
                task=target_task,
                task_plan=plan,
                status=RoutingStatus.INVALID_INPUT,
                reason=f"Input validation failed for tool '{primary_tool_name}'.",
                required_inputs=all_required_inputs,
                provided_inputs=provided_inputs,
                permitted_parameters=sanitized_params_per_step,
                validation_errors=fatal_errors + param_warnings_list,
            )

        plan.policy_validated = True
        plan.policy_notes = ["All tools and parameters verified against Predefined Registry."]

        return ToolSelection(
            selected_tool=primary_tool_name,
            task=target_task,
            task_plan=plan,
            status=RoutingStatus.ROUTED,
            reason=routing_reason,
            required_inputs=all_required_inputs,
            provided_inputs=provided_inputs,
            permitted_parameters=sanitized_params_per_step,
            validation_errors=param_warnings_list,
        )

