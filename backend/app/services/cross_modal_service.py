"""Query-driven optical grounding with co-located SAR measurements and paired VQA."""
import math
import time
import numpy as np
from PIL import Image

from ..agent.schemas import OrchestrationResult
from ai.inference.optical_sar import run_optical_sar
from ai.inference.grounding import run_grounding
from ai.inference.vqa import run_vqa


def region_radar_measurements(sar_path, boxes, labels):
    with Image.open(sar_path) as source:
        radar = np.asarray(source.convert("L"), dtype=np.float32)
    height, width = radar.shape
    regions = []
    for index, box in enumerate(boxes):
        if len(box) != 4 or not all(math.isfinite(float(x)) for x in box):
            continue
        x1, y1, x2, y2 = box
        x1, x2 = max(0, math.floor(x1)), min(width, math.ceil(x2))
        y1, y2 = max(0, math.floor(y1)), min(height, math.ceil(y2))
        if x2 <= x1 or y2 <= y1:
            continue
        patch = radar[y1:y2, x1:x2]
        regions.append({"region_id": f"region-{index + 1}", "box": [x1, y1, x2, y2],
                        "optical_label": labels[index] if index < len(labels) else "candidate region",
                        "sar_display_mean": round(float(patch.mean()), 2),
                        "sar_display_std": round(float(patch.std()), 2),
                        "sar_dark_fraction": round(float((patch < 64).mean()), 4),
                        "sar_bright_fraction": round(float((patch > 192).mean()), 4)})
    return regions


def execute_cross_modal(request, selection, trace, started):
    params = {step.tool: step.parameters for step in selection.task_plan.plan}
    optical = request.optical_image_path or request.image_path
    outputs = []
    regions = []
    for tool in ["OPTICAL_SAR", "GROUNDING", "VQA"]:
        if tool == "OPTICAL_SAR":
            raw = run_optical_sar(optical, request.sar_image_path, request.query, params[tool])
        elif tool == "GROUNDING":
            raw = run_grounding(optical, "buildings. water.", params[tool])
            if raw["status"] == "SUCCESS":
                ev = (raw.get("evidence") or [{}])[0]
                regions = region_radar_measurements(request.sar_image_path,
                    ev.get("bounding_boxes", raw.get("bounding_boxes", [])),
                    ev.get("labels", raw.get("labels", [])))
        else:
            prompt = (f"{request.query}\nUse both supplied images. Identify candidate built-up and water regions "
                      "by position and explain the optical appearance and SAR display evidence separately. "
                      "Dark SAR may also be shadow; bright SAR alone is not proof of a building. "
                      "If the images do not support the requested identification, say so. "
                      f"Co-located region measurements (uncalibrated 8-bit intensities): {regions}. "
                      "Do not infer physical backscatter, sensor identity, or geographic names.")
            raw = run_vqa(optical, prompt, params[tool], second_image_path=request.sar_image_path, pair_kind="optical_sar")
        outputs.append(raw)
        trace.append({"step": f"CROSS_MODAL_{tool}", "status": raw["status"],
                      "selected_tool": tool, "model": raw["model"],
                      "permitted_parameters": params[tool], "latency_ms": raw["latency_ms"]})
        if raw["status"] != "SUCCESS":
            return OrchestrationResult(status="ERROR", selected_tool="MULTI_TOOL", model=raw["model"],
                answer=f"Cross-modal analysis failed at {tool}: {raw.get('answer', '')}",
                task_plan=selection.task_plan.to_dict(), observable_execution_trace=trace,
                error_type="CROSS_MODAL_STAGE_FAILED", latency_ms=round((time.perf_counter()-started)*1000, 2))
    stats, grounding, narrative = outputs
    evidence = dict(grounding["evidence"][0]) if grounding.get("evidence") else {}
    evidence_links = [{
        "region_id": region["region_id"],
        "spatial_source": "GROUNDING.bounding_boxes",
        "sensor_source": "OPTICAL_SAR.region_radar_measurements",
        "text_source": "VQA.paired_answer",
        "box": region["box"],
        "support": "candidate_region_with_co_located_measurement",
    } for region in regions]
    evidence.update(type="cross_modal_region_evidence", regions=regions,
                    optical_sar=(stats.get("evidence") or [{}])[0],
                    paired_vqa=(narrative.get("evidence") or [{}])[0],
                    evidence_links=evidence_links,
                    evidence_contract={"textual_spatial_sensor_join": "explicit",
                                       "calibration_status": "not_calibrated",
                                       "interpretation": "Each link joins one optical box, its co-located SAR display measurements, and the paired VQA answer; it is not a class probability."})
    return OrchestrationResult(status="SUCCESS", selected_tool="MULTI_TOOL",
        model="Optical/SAR statistics + Grounding DINO + paired Qwen2.5-VL",
        answer=narrative["answer"], image_description=narrative.get("image_description"),
        confidence=None, evidence=evidence, task_plan=selection.task_plan.to_dict(),
        metadata={"pair_kind": "optical_sar", "input_image_count": 2, "regions": regions,
                  "evidence_links": evidence_links,
                  "uncertainty": {"status": "uncalibrated", "type": "qualitative_evidence_strength",
                                  "reason": "Display intensities and open-vocabulary detections do not establish physical SAR calibration or class accuracy."}},
        observable_execution_trace=trace, tools_used=["OPTICAL_SAR", "GROUNDING", "VQA"],
        evidence_items=[evidence], execution_trace=[{"tool": x["tool"], "status": "success", "latency_ms": x["latency_ms"]} for x in outputs],
        limitations=["Optical detections and SAR display statistics are uncalibrated. No accuracy improvement or sensor authenticity is inferred.",
                     "Region labels are candidates; SAR shadow and optical appearance can be ambiguous."],
        latency_ms=round((time.perf_counter()-started)*1000, 2))
