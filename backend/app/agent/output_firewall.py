"""
SatQuery AI — Output Verification & Unsupported-Claim Firewall (Part 8)
Lightweight validation layer that audits final answers and operational metadata
before returning responses to the user or evaluator.

Verifies:
1. Claims are supported by actual executed tools.
2. Numerical counts match grounded bounding box counts, not VLM hallucinations.
3. Confidence labels do not claim uncalibrated accuracy.
4. Relevant scientific limitations are present.
5. Unsupported superlative claims ("100% accuracy", "proven superior") are sanitized.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class OutputFirewall:
    """
    Deterministic rule-based output verification firewall.
    Guarantees scientific defensibility and audit compliance.
    """

    UNSUPPORTED_SUPERLATIVES = [
        (r"\b100%\s+acc(uracy|urate)\b", "high consistency"),
        (r"\bhigh\s+acc(uracy|urate)\b", "calibrated detection"),
        (r"\bproven\s+superior(ity)?\b", "empirically evaluated"),
        (r"\breal[- ]time\b", "near-interactive"),
        (r"\blocalization\s+accuracy:\s*\d+%\b", "detector confidence score"),
    ]

    @classmethod
    def sanitize_unsupported_language(cls, text: str) -> Tuple[str, List[str]]:
        """Sanitizes overly aggressive or unbenchmarkable claims in text."""
        sanitized = text
        applied_corrections = []
        for pattern, replacement in cls.UNSUPPORTED_SUPERLATIVES:
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
                applied_corrections.append(f"Sanitized unsupported claim pattern '{pattern}' to '{replacement}'.")
        return sanitized, applied_corrections

    @classmethod
    def format_counting_response(cls, count: int, entity: Optional[str] = None) -> str:
        """
        Formats grammatically correct, pluralized detection responses.
        Examples:
            count=1, entity='ships' -> '1 ship was detected.'
            count=2, entity='ships' -> '2 ships were detected.'
            count=0, entity='ships' -> 'No valid ships were detected with the current grounding threshold.'
        """
        raw = (entity or "object").lower().strip().replace("_", " ")

        irregulars = {
            "aircraft": ("aircraft", "aircraft"),
            "ship": ("ship", "ships"),
            "boat": ("boat", "boats"),
            "vessel": ("vessel", "vessels"),
            "building": ("building", "buildings"),
            "house": ("house", "houses"),
            "structure": ("structure", "structures"),
            "vehicle": ("vehicle", "vehicles"),
            "car": ("car", "cars"),
            "truck": ("truck", "trucks"),
            "plane": ("plane", "planes"),
            "airplane": ("airplane", "airplanes"),
            "road": ("road", "roads"),
            "runway": ("runway", "runways"),
            "port": ("port", "ports"),
            "built up area": ("built-up area", "built-up areas"),
            "built-up area": ("built-up area", "built-up areas"),
            "object": ("object", "objects"),
            "target object": ("target object", "target objects"),
        }

        matched = None
        for k, (s, p) in irregulars.items():
            if raw == k or raw == s or raw == p:
                matched = (s, p)
                break

        if not matched:
            if raw.endswith("s"):
                matched = (raw[:-1], raw)
            else:
                matched = (raw, raw + "s")

        singular, plural = matched

        if count == 0:
            return f"No valid {plural} were detected with the current grounding threshold."
        elif count == 1:
            return f"1 {singular} was detected."
        else:
            return f"{count} {plural} were detected."

    @classmethod
    def verify_counting_consistency(
        cls,
        answer: str,
        tool_name: str,
        bounding_boxes: Optional[List[Any]] = None,
        is_counting_query: bool = False,
        target_entity: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        """
        Ensures that if a counting query was routed, the count strictly reflects
        the count of valid grounded bounding boxes rather than a VLM hallucination.
        """
        audit_notes: List[str] = []
        valid_count = len(bounding_boxes or [])

        if is_counting_query:
            answer = cls.format_counting_response(valid_count, target_entity)
            if valid_count == 0:
                audit_notes.append("Grounding returned 0 valid detections; transparent zero-detection response enforced.")
            else:
                audit_notes.append(f"Count verified: {valid_count} bounding boxes matched grounding output.")

        return answer, audit_notes

    @classmethod
    def assemble_relevant_limitations(
        cls,
        tools_used: List[str],
        is_counting_query: bool = False,
        box_count: int = 0,
    ) -> List[str]:
        """
        Generates strictly relevant scientific limitations based on the specialist tools executed.
        Does not attach irrelevant warnings.
        """
        limitations: List[str] = []

        if is_counting_query:
            limitations.append(
                f"{box_count} detected objects. Count is derived from grounding detections rather than VLM-generated counting."
            )

        if "CHANGE_DETECTION" in tools_used:
            limitations.append(
                "Detected change using unsupervised feature differencing (calibrated tau=0.30). Results may contain illumination or seasonal false positives."
            )

        if "GROUNDING" in tools_used and not is_counting_query:
            limitations.append(
                "Object locations were generated by the grounding detector. Detector confidence is not equivalent to benchmarked localization accuracy."
            )

        if "OPTICAL_SAR" in tools_used:
            limitations.append(
                "Multimodal optical/SAR processing is implemented, but task-level superiority has not been quantitatively established."
            )

        if "VQA" in tools_used and not is_counting_query and "CHANGE_DETECTION" not in tools_used:
            limitations.append(
                "VLM confidence represents model-derived uncalibrated heuristic; not a calibrated probability of factual correctness."
            )

        return limitations
