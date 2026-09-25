"""
SatQuery AI — Remote-Sensing VQA Executor (Phase 5A)
Wraps AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct in a clean, isolated execution interface.
Enforces on-demand loading, input validation, structured output telemetry, and GPU resource cleanup.
"""

import os
import time
import gc
import traceback
from typing import Dict, Any, Optional
import torch
from PIL import Image
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from backend.app.services.confidence_service import (
    extract_vqa_rich_evidence,
    evaluate_vqa_confidence,
)


VLM_MODEL_ID = "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct"


def run_vqa(
    image_path: str,
    query: str,
    permitted_parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes a single remote-sensing VQA forward pass on demand.

    Args:
        image_path: Filesystem path to the target satellite image.
        query: User analytical question.
        permitted_parameters: Whitelisted parameter dictionary from Agent Router.

    Returns:
        Structured result dictionary conforming to Phase 5A contract:
        {
            "status": "SUCCESS" | "ERROR",
            "tool": "VQA",
            "model": "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct",
            "answer": "...",
            "confidence": None,
            "latency_ms": float,
            "evidence": list,
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
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": "Query string cannot be empty.",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "metadata": {"error_type": "VALIDATION_ERROR", "message": "Query string cannot be empty."}
        }

    # 2. Input Validation: Image Path & Readability
    if not image_path or not os.path.exists(image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": f"Image file not found / does not exist: {image_path}",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "metadata": {"error_type": "IMAGE_NOT_FOUND", "message": f"Image file does not exist: {image_path}"}
        }

    img_w, img_h = 0, 0
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            img_w, img_h = img.size
    except Exception as img_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": f"Unable to read the image: {image_path}. File is corrupted or unreadable: {img_err}",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "metadata": {"error_type": "INVALID_IMAGE", "message": f"Unable to read the image: {image_path}. Details: {img_err}"}
        }

    # 3. Model Loading & Inference Execution
    model = None
    processor = None
    inputs = None

    # Retrieve sanitized parameters with safe defaults
    max_new_tokens = int(params.get("max_new_tokens", 100))
    do_sample = bool(params.get("do_sample", False))
    min_pixels = int(params.get("min_pixels", 200704))
    max_pixels = int(params.get("max_pixels", 401408))

    try:
        processor = AutoProcessor.from_pretrained(
            VLM_MODEL_ID,
            min_pixels=min_pixels,
            max_pixels=max_pixels,
        )

        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            VLM_MODEL_ID,
            torch_dtype="auto",
            device_map="auto",
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": query.strip()},
                ],
            }
        ]

        text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = processor(
            text=[text_prompt],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(model.device)

        with torch.inference_mode():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        raw_answer = output_text[0].strip() if output_text else ""
        answer, image_description, visual_evidence = extract_vqa_rich_evidence(
            raw_answer, query, image_path, img_w, img_h
        )
        conf_payload = evaluate_vqa_confidence(
            query=query,
            image_path=image_path,
            answer=answer,
            image_description=image_description,
            visual_evidence=visual_evidence,
            metadata={"model": VLM_MODEL_ID},
        )
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        # 4. Evidence Structure (factual metadata and observable evidence features)
        evidence = [
            {
                "type": "vqa_spatial_metadata",
                "image_reference": image_path,
                "dimensions": {"width": img_w, "height": img_h},
                "query": query.strip(),
                "model": VLM_MODEL_ID,
                "latency_ms": latency_ms,
                "visual_evidence_count": len(visual_evidence),
            }
        ]

        return {
            "status": "SUCCESS",
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": answer,
            "image_description": image_description,
            "visual_evidence": visual_evidence,
            "confidence": conf_payload,
            "latency_ms": latency_ms,
            "evidence": evidence,
            "metadata": {
                "max_new_tokens": max_new_tokens,
                "tokens_generated": len(generated_ids_trimmed[0]) if generated_ids_trimmed else 0,
                "visual_token_bounds": f"{min_pixels}-{max_pixels}",
                "confidence_type": conf_payload.get("type"),
                "confidence_level": conf_payload.get("level"),
                "confidence_score": conf_payload.get("score"),
            }
        }

    except torch.cuda.OutOfMemoryError as oom_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": "",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "metadata": {"error_type": "CUDA_OOM", "message": f"GPU Out-Of-Memory during VLM execution: {oom_err}"}
        }

    except Exception as err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "VQA",
            "model": VLM_MODEL_ID,
            "answer": "",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "metadata": {"error_type": "INFERENCE_ERROR", "message": str(err), "traceback": traceback.format_exc()}
        }

    finally:
        # 5. Clean up model and GPU tensors to honor single-heavy-model policy
        if inputs is not None:
            del inputs
        if model is not None:
            del model
        if processor is not None:
            del processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
