"""
SatQuery AI — Predefined Tool Registry (Phase 4)
Maintains a strictly controlled, inspectable catalog of specialist remote-sensing AI tools.
Arbitrary model loading or unwhitelisted parameters are blocked at the registry boundary.
Uses Python dataclasses for zero-dependency runtime reliability.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ParameterSpec:
    name: str
    type: str
    default: Any
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None


@dataclass
class ToolDefinition:
    tool_name: str
    description: str
    accepted_input_types: List[str]
    required_inputs: List[str]
    permitted_parameters: Dict[str, ParameterSpec]
    model_or_engine: str
    output_type: str
    evidence_type: str
    confidence_supported: bool
    resource_notes: str


# Predefined, immutable registry catalog
TOOL_REGISTRY: Dict[str, ToolDefinition] = {
    "VQA": ToolDefinition(
        tool_name="VQA",
        description="Remote-sensing visual question answering, natural-language counting, and scene captioning.",
        accepted_input_types=["image/jpeg", "image/png", "image/tiff", ".jpg", ".jpeg", ".png", ".tif", ".tiff"],
        required_inputs=["image_path"],
        permitted_parameters={
            "max_new_tokens": ParameterSpec(
                name="max_new_tokens",
                type="int",
                default=100,
                min_value=16,
                max_value=256,
                description="Maximum generation tokens"
            ),
            "do_sample": ParameterSpec(
                name="do_sample",
                type="bool",
                default=False,
                allowed_values=[False],
                description="Greedy decoding enforced for deterministic evaluation"
            ),
            "min_pixels": ParameterSpec(
                name="min_pixels",
                type="int",
                default=200704,
                allowed_values=[200704],
                description="Conservative lower visual token budget (256*28*28)"
            ),
            "max_pixels": ParameterSpec(
                name="max_pixels",
                type="int",
                default=401408,
                allowed_values=[401408],
                description="Conservative upper visual token budget (512*28*28)"
            ),
        },
        model_or_engine="AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
        output_type="text",
        evidence_type="visual_token_attention",
        confidence_supported=True,
        resource_notes="VLM consumes ~6.2 GB in bfloat16; uses automatic CPU layer offloading on 8 GB RTX 5050."
    ),

    "GROUNDING": ToolDefinition(
        tool_name="GROUNDING",
        description="Text-guided open-vocabulary visual object grounding and coordinate localization.",
        accepted_input_types=["image/jpeg", "image/png", "image/tiff", ".jpg", ".jpeg", ".png", ".tif", ".tiff"],
        required_inputs=["image_path"],
        permitted_parameters={
            "box_threshold": ParameterSpec(
                name="box_threshold",
                type="float",
                default=0.35,
                min_value=0.10,
                max_value=0.90,
                description="Bounding box detection confidence threshold"
            ),
            "text_threshold": ParameterSpec(
                name="text_threshold",
                type="float",
                default=0.25,
                min_value=0.10,
                max_value=0.90,
                description="Text-image cross-modal alignment threshold"
            ),
        },
        model_or_engine="IDEA-Research/grounding-dino-tiny",
        output_type="bounding_boxes",
        evidence_type="annotated_bounding_box_overlay",
        confidence_supported=True,
        resource_notes="Lightweight Swin-T backbone; consumes ~660 MB VRAM; runs entirely in GPU memory."
    ),

    "CHANGE_DETECTION": ToolDefinition(
        tool_name="CHANGE_DETECTION",
        description="Bi-temporal comparative analysis between registered timestamps T1 and T2 to detect structural and land-cover changes.",
        accepted_input_types=["image/jpeg", "image/png", "image/tiff", ".jpg", ".jpeg", ".png", ".tif", ".tiff"],
        required_inputs=["image_path", "second_image_path"],
        permitted_parameters={
            "threshold": ParameterSpec(
                name="threshold",
                type="float",
                default=0.40,
                min_value=0.10,
                max_value=0.90,
                description="Normalized differential distance threshold for binary change classification"
            ),
        },
        model_or_engine="Siamese-ResNet18-FeatureDifferencer",
        output_type="change_mask",
        evidence_type="differential_heatmap_mask_composite",
        confidence_supported=True,
        resource_notes="Siamese dual-stream feature difference; consumes <100 MB VRAM; sub-second inference."
    ),

    "OPTICAL_SAR": ToolDefinition(
        tool_name="OPTICAL_SAR",
        description="Cross-modal multi-sensor paired analysis correlating optical spectral reflectance with microwave radar backscatter.",
        accepted_input_types=["image/jpeg", "image/png", "image/tiff", ".jpg", ".jpeg", ".png", ".tif", ".tiff"],
        required_inputs=["optical_image_path", "sar_image_path"],
        permitted_parameters={
            "high_scatter_threshold": ParameterSpec(
                name="high_scatter_threshold",
                type="float",
                default=180.0,
                min_value=100.0,
                max_value=250.0,
                description="Threshold DN for identifying metallic/corner-reflector radar echoes"
            ),
        },
        model_or_engine="Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine",
        output_type="cross_modal_statistics",
        evidence_type="optical_sar_synergy_overlay",
        confidence_supported=True,
        resource_notes="Dual-stream matrix profiling; consumes <50 MB VRAM; sub-second inference."
    ),
}


def get_tool(tool_name: str) -> Optional[ToolDefinition]:
    """Retrieve a registered tool definition by name."""
    return TOOL_REGISTRY.get(tool_name.upper())


def list_tools() -> List[ToolDefinition]:
    """Return all registered tool definitions."""
    return list(TOOL_REGISTRY.values())


def is_tool_registered(tool_name: str) -> bool:
    """Check whether a tool identifier exists in the registry."""
    return tool_name.upper() in TOOL_REGISTRY


def validate_and_filter_parameters(tool_name: str, requested_params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validates user-requested parameters against the tool's permitted parameter schema.
    Rejects unrecognized parameters and clamps/validates numeric ranges.
    Returns: (sanitized_parameters, error_warnings)
    """
    tool = get_tool(tool_name)
    if not tool:
        return {}, [f"Tool '{tool_name}' is not registered."]

    sanitized = {}
    warnings = []

    # First, populate defaults
    for param_name, spec in tool.permitted_parameters.items():
        sanitized[param_name] = spec.default

    # Then, validate and apply user overrides
    for param_name, value in requested_params.items():
        if param_name not in tool.permitted_parameters:
            warnings.append(f"Ignored unpermitted parameter '{param_name}' for tool '{tool_name}'.")
            continue

        spec = tool.permitted_parameters[param_name]

        # Type conversion check
        try:
            if spec.type == "int":
                val = int(value)
            elif spec.type == "float":
                val = float(value)
            elif spec.type == "bool":
                val = bool(value)
            else:
                val = str(value)
        except (ValueError, TypeError):
            warnings.append(f"Parameter '{param_name}' must be of type {spec.type}. Using default {spec.default}.")
            continue

        # Allowed values check
        if spec.allowed_values is not None and val not in spec.allowed_values:
            warnings.append(f"Parameter '{param_name}' value {val} not in allowed set {spec.allowed_values}. Using default {spec.default}.")
            continue

        # Range checks
        if spec.min_value is not None and val < spec.min_value:
            warnings.append(f"Parameter '{param_name}' value {val} below minimum {spec.min_value}. Clamped to {spec.min_value}.")
            val = spec.min_value
        if spec.max_value is not None and val > spec.max_value:
            warnings.append(f"Parameter '{param_name}' value {val} exceeds maximum {spec.max_value}. Clamped to {spec.max_value}.")
            val = spec.max_value

        sanitized[param_name] = val

    return sanitized, warnings
