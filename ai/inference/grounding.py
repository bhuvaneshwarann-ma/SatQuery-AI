"""
SatQuery AI — Visual Grounding Specialist Executor (Phase 5B)
Wraps IDEA-Research/grounding-dino-tiny in an isolated, deterministic execution interface.
Enforces on-demand loading, input validation, structured output telemetry, and strict GPU resource cleanup.
"""

import os
import time
import gc
import traceback
from typing import Dict, Any, Optional
import torch
from PIL import Image, ImageDraw
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection


GROUNDING_MODEL_ID = "IDEA-Research/grounding-dino-tiny"


def run_grounding(
    image_path: str,
    query: str,
    permitted_parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes a single visual grounding forward pass on demand.

    Args:
        image_path: Filesystem path to the target satellite image.
        query: User object/target phrase to localize.
        permitted_parameters: Whitelisted parameter dictionary from Agent Router.

    Returns:
        Structured result dictionary conforming to Phase 5B contract:
        {
            "status": "SUCCESS" | "ERROR",
            "tool": "GROUNDING",
            "model": "IDEA-Research/grounding-dino-tiny",
            "query": "...",
            "image_reference": "...",
            "detections": int,
            "bounding_boxes": list,
            "confidence_scores": list,
            "confidence": float | None,
            "answer": "...",
            "latency_ms": float,
            "evidence": list,
            "evidence_reference": str | None,
            "metadata": dict
        }
    """
    t_start = time.perf_counter()
    params = permitted_parameters or {}

    # 1. Input Validation: Query
    if not query or not query.strip():
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "GROUNDING",
            "model": GROUNDING_MODEL_ID,
            "query": query or "",
            "image_reference": image_path or "",
            "detections": 0,
            "bounding_boxes": [],
            "confidence_scores": [],
            "confidence": None,
            "answer": "Query string cannot be empty for visual grounding.",
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "VALIDATION_ERROR",
                "message": "Query string cannot be empty for visual grounding."
            }
        }

    # 2. Input Validation: Image Path & Readability
    if not image_path or not os.path.exists(image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "GROUNDING",
            "model": GROUNDING_MODEL_ID,
            "query": query.strip(),
            "image_reference": image_path or "",
            "detections": 0,
            "bounding_boxes": [],
            "confidence_scores": [],
            "confidence": None,
            "answer": f"Image file not found / does not exist: {image_path}",
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "IMAGE_NOT_FOUND",
                "message": f"Image file does not exist: {image_path}"
            }
        }

    img_w, img_h = 0, 0
    raw_image = None
    try:
        with Image.open(image_path) as img:
            img.verify()
        raw_image = Image.open(image_path).convert("RGB")
        img_w, img_h = raw_image.size
    except Exception as img_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "GROUNDING",
            "model": GROUNDING_MODEL_ID,
            "query": query.strip(),
            "image_reference": image_path,
            "detections": 0,
            "bounding_boxes": [],
            "confidence_scores": [],
            "confidence": None,
            "answer": f"Unable to read the image: {image_path}. File is corrupted or unreadable: {img_err}",
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_IMAGE",
                "message": f"Unable to read the image: {image_path}. Details: {img_err}"
            }
        }

    # 3. Parameter Sanitization
    box_threshold = float(params.get("box_threshold", 0.35))
    text_threshold = float(params.get("text_threshold", 0.25))

    # 4. Model Loading & Inference Execution
    model = None
    processor = None
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        processor = AutoProcessor.from_pretrained(GROUNDING_MODEL_ID)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(GROUNDING_MODEL_ID).to(device)
        model.eval()

        clean_query = query.strip()
        # Grounding DINO expects dot-terminated text phrases
        formatted_text = clean_query if clean_query.endswith(".") else f"{clean_query}."

        inputs = processor(images=raw_image, text=formatted_text, return_tensors="pt").to(device)

        with torch.inference_mode():
            outputs = model(**inputs)

        # Transformers 5.x post-processing uses 'threshold' for the box score threshold
        processed = processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=[(img_h, img_w)],
        )

        det = processed[0]
        raw_scores = det["scores"].detach().cpu().tolist()
        raw_boxes = det["boxes"].detach().cpu().tolist()

        scores = [round(float(s), 4) for s in raw_scores]
        boxes = [[round(float(c), 2) for c in box] for box in raw_boxes]
        num_detections = len(scores)

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        if num_detections > 0:
            answer = f"Detected {num_detections} '{clean_query}' object(s) with confidence ranging from {min(scores):.2f} to {max(scores):.2f}."
            conf = round(max(scores), 4)
        else:
            answer = f"No '{clean_query}' objects detected matching thresholds (box_threshold={box_threshold}, text_threshold={text_threshold})."
            conf = None

        # Generate annotated overlay artifact if detections exist
        annotated_artifact_path = None
        if num_detections > 0:
            try:
                out_dir = os.path.join("docs", "results")
                os.makedirs(out_dir, exist_ok=True)
                annotated_artifact_path = os.path.join(out_dir, "grounding_execution_artifact.jpg")
                annotated = raw_image.copy()
                draw = ImageDraw.Draw(annotated)
                for box, score in zip(boxes, scores):
                    x1, y1, x2, y2 = [int(v) for v in box]
                    draw.rectangle([x1, y1, x2, y2], outline=(255, 69, 0), width=2)
                    draw.text((x1, max(0, y1 - 12)), f"{clean_query}: {score:.2f}", fill=(255, 69, 0))
                annotated.save(annotated_artifact_path, "JPEG", quality=92)
            except Exception:
                annotated_artifact_path = None

        evidence_dict = {
            "type": "grounding_spatial_boxes",
            "image_reference": image_path,
            "query": clean_query,
            "model": GROUNDING_MODEL_ID,
            "dimensions": {"width": img_w, "height": img_h},
            "detections_count": num_detections,
            "bounding_boxes": boxes,
            "confidence_scores": scores,
            "annotated_artifact": annotated_artifact_path,
            "latency_ms": latency_ms,
        }

        return {
            "status": "SUCCESS",
            "tool": "GROUNDING",
            "model": GROUNDING_MODEL_ID,
            "query": clean_query,
            "image_reference": image_path,
            "detections": num_detections,
            "bounding_boxes": boxes,
            "confidence_scores": scores,
            "confidence": conf,
            "answer": answer,
            "latency_ms": latency_ms,
            "evidence": [evidence_dict],
            "evidence_reference": "grounding_spatial_boxes",
            "metadata": {
                "box_threshold": box_threshold,
                "text_threshold": text_threshold,
                "detections_count": num_detections,
                "bounding_boxes": boxes,
                "confidence_scores": scores,
                "image_reference": image_path,
            }
        }

    except Exception as exec_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "GROUNDING",
            "model": GROUNDING_MODEL_ID,
            "query": query,
            "image_reference": image_path,
            "detections": 0,
            "bounding_boxes": [],
            "confidence_scores": [],
            "confidence": None,
            "answer": f"Grounding execution error: {exec_err}",
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "EXECUTION_ERROR",
                "message": str(exec_err),
                "traceback": traceback.format_exc(),
            }
        }

    finally:
        # Strict GPU memory cleanup
        if model is not None:
            del model
        if processor is not None:
            del processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
