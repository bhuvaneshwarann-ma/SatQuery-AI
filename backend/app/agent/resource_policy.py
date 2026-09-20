"""
SatQuery AI — Model Resource Policy (Phase 4)
Defines device and memory management policies for the NVIDIA GeForce RTX 5050 Laptop GPU (~8 GB VRAM).
Enforces single-heavy-model residency and sequential execution to prevent CUDA Out-Of-Memory events.
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class ModelWeightCategory(str, Enum):
    HEAVY_VLM = "HEAVY_VLM"       # ~6.2 GB unquantized (Qwen2.5-VL-3B-Instruct)
    MEDIUM_VISION = "MEDIUM_VISION" # ~660 MB - 1.2 GB (Grounding DINO-T)
    LIGHT_DIFF = "LIGHT_DIFF"     # <100 MB (Siamese ResNet Differencer)
    LIGHT_FUSION = "LIGHT_FUSION" # <50 MB (Optical-SAR matrix statistics)


class GPUResourcePolicy:
    TOTAL_VRAM_MB: float = 8150.0
    SAFETY_HEADROOM_MB: float = 1200.0
    MAX_ALLOCATABLE_MB: float = 6950.0

    # Mutex policy: Heavy VLM cannot co-exist with another heavy or medium model in active GPU memory
    MODEL_WEIGHT_MAP: Dict[str, ModelWeightCategory] = {
        "VQA": ModelWeightCategory.HEAVY_VLM,
        "GROUNDING": ModelWeightCategory.MEDIUM_VISION,
        "CHANGE_DETECTION": ModelWeightCategory.LIGHT_DIFF,
        "OPTICAL_SAR": ModelWeightCategory.LIGHT_FUSION,
    }

    @classmethod
    def can_coexist(cls, active_tool: Optional[str], candidate_tool: str) -> bool:
        """
        Determines whether candidate_tool can be loaded without evicting active_tool.
        Rule: If either is HEAVY_VLM, they cannot co-exist in GPU VRAM simultaneously.
        """
        if not active_tool:
            return True

        active_cat = cls.MODEL_WEIGHT_MAP.get(active_tool.upper())
        cand_cat = cls.MODEL_WEIGHT_MAP.get(candidate_tool.upper())

        if active_cat == ModelWeightCategory.HEAVY_VLM or cand_cat == ModelWeightCategory.HEAVY_VLM:
            return False

        # Lightweight and medium models can co-exist if VRAM allows
        return True

    @classmethod
    def get_eviction_plan(cls, active_tool: Optional[str], target_tool: str) -> List[str]:
        """
        Returns which resident tool models must be evicted/unloaded before loading target_tool.
        """
        if not active_tool:
            return []

        if not cls.can_coexist(active_tool, target_tool):
            return [active_tool]

        return []
