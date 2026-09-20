"""
SatQuery AI — Bi-Temporal Change Detection Specialist Executor (Phase 5C)
Wraps Siamese-ResNet18-FeatureDifferencer in an isolated, deterministic execution interface.
Enforces multi-image validation, parameter range verification, structured evidence generation, and GPU memory cleanup.
"""

import os
import time
import gc
import traceback
from typing import Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image, ImageDraw, ImageFont


CHANGE_MODEL_ID = "Siamese-ResNet18-FeatureDifferencer"


class SiameseResNetChangeDetector(nn.Module):
    """
    Siamese Deep Feature Difference Architecture for Bi-Temporal Change Detection.
    Uses a shared pre-trained ResNet backbone to extract multi-scale spatial features,
    computing deep differential distance maps between registered timestamps T1 and T2.
    """
    def __init__(self, pretrained: bool = True):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        base_resnet = models.resnet18(weights=weights)
        self.stem = nn.Sequential(
            base_resnet.conv1,
            base_resnet.bn1,
            base_resnet.relu,
            base_resnet.maxpool,
        )
        self.layer1 = base_resnet.layer1
        self.layer2 = base_resnet.layer2

    def extract_features(self, x):
        feat0 = self.stem(x)
        feat1 = self.layer1(feat0)
        feat2 = self.layer2(feat1)
        return feat1, feat2

    def forward(self, t1, t2):
        t1_f1, t1_f2 = self.extract_features(t1)
        t2_f1, t2_f2 = self.extract_features(t2)

        dist1 = torch.norm(t1_f1 - t2_f1, dim=1, keepdim=True)
        dist2 = torch.norm(t1_f2 - t2_f2, dim=1, keepdim=True)

        target_size = (t1.shape[2], t1.shape[3])
        dist1_up = F.interpolate(dist1, size=target_size, mode="bilinear", align_corners=False)
        dist2_up = F.interpolate(dist2, size=target_size, mode="bilinear", align_corners=False)

        fused_dist = 0.5 * dist1_up + 0.5 * dist2_up
        return fused_dist


def render_evidence_composite(
    t1_img: Image.Image,
    t2_img: Image.Image,
    change_mask: np.ndarray,
    output_path: str,
):
    """
    Renders a 3-panel side-by-side evidence visualization:
    Panel 1: Timestamp T1 (Baseline)
    Panel 2: Timestamp T2 (Post-Event)
    Panel 3: Detected Change Overlay (Red highlight mask overlaid on T2)
    """
    w, h = t1_img.size

    t2_np = np.array(t2_img).astype(np.float32)
    overlay_np = t2_np.copy()
    mask_bool = change_mask > 0
    overlay_np[mask_bool] = 0.5 * overlay_np[mask_bool] + 0.5 * np.array([255, 30, 30], dtype=np.float32)
    overlay_img = Image.fromarray(np.clip(overlay_np, 0, 255).astype(np.uint8))

    banner_h = 40
    composite = Image.new("RGB", (w * 3, h + banner_h), color=(20, 24, 30))
    draw = ImageDraw.Draw(composite)

    font = ImageFont.load_default()

    composite.paste(t1_img, (0, banner_h))
    composite.paste(t2_img, (w, banner_h))
    composite.paste(overlay_img, (w * 2, banner_h))

    draw.text((20, 12), "PANEL 1: Image T1 (Baseline)", fill=(255, 255, 255), font=font)
    draw.text((w + 20, 12), "PANEL 2: Image T2 (Post-Event / Controlled)", fill=(255, 255, 255), font=font)
    draw.text((w * 2 + 20, 12), "PANEL 3: Detected Change Mask Overlay (Red)", fill=(255, 80, 80), font=font)

    draw.line([(w, 0), (w, h + banner_h)], fill=(60, 65, 75), width=2)
    draw.line([(w * 2, 0), (w * 2, h + banner_h)], fill=(60, 65, 75), width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    composite.save(output_path, "JPEG", quality=92)


def run_change_detection(
    image_path: str,
    second_image_path: Optional[str] = None,
    query: Optional[str] = None,
    permitted_parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes bi-temporal change detection between registered timestamps T1 and T2.

    Args:
        image_path: Filesystem path to baseline image T1.
        second_image_path: Filesystem path to post-event image T2.
        query: Optional user query string.
        permitted_parameters: Whitelisted parameter dictionary from Agent Router.

    Returns:
        Structured result dictionary conforming to Phase 5C contract.
    """
    t_start = time.perf_counter()
    params = permitted_parameters or {}

    # 1. Input Validation: T1 Path
    if not image_path or not os.path.exists(image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Baseline image T1 not found / does not exist: {image_path}",
            "image_reference_t1": image_path or "",
            "image_reference_t2": second_image_path or "",
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "IMAGE_NOT_FOUND",
                "message": f"Baseline image T1 file does not exist: {image_path}"
            }
        }

    # 2. Input Validation: T2 Path
    if not second_image_path or not os.path.exists(second_image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Post-event image T2 not found / does not exist: {second_image_path}",
            "image_reference_t1": image_path or "",
            "image_reference_t2": second_image_path or "",
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "IMAGE_NOT_FOUND",
                "message": f"Post-event image T2 file does not exist: {second_image_path}"
            }
        }

    # 3. Input Validation: Image Readability & Verification
    t1_img = None
    t2_img = None
    try:
        with Image.open(image_path) as img:
            img.verify()
        t1_img = Image.open(image_path).convert("RGB")
    except Exception as t1_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Unable to read baseline image T1: {image_path}. File is corrupted or unreadable: {t1_err}",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_IMAGE",
                "message": f"Unable to read T1 image: {image_path}. Details: {t1_err}"
            }
        }

    try:
        with Image.open(second_image_path) as img:
            img.verify()
        t2_img = Image.open(second_image_path).convert("RGB")
    except Exception as t2_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Unable to read post-event image T2: {second_image_path}. File is corrupted or unreadable: {t2_err}",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_IMAGE",
                "message": f"Unable to read T2 image: {second_image_path}. Details: {t2_err}"
            }
        }

    # 4. Dimension Compatibility Check
    w1, h1 = t1_img.size
    w2, h2 = t2_img.size
    if (w1, h1) != (w2, h2):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Spatial dimension mismatch: T1 is {w1}x{h1}, T2 is {w2}x{h2}. Images must be coregistered with matching dimensions.",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "DIMENSION_MISMATCH",
                "message": f"Dimension mismatch: T1={w1}x{h1}, T2={w2}x{h2}"
            }
        }

    # 5. Parameter Validation: Threshold
    try:
        raw_threshold = params.get("threshold", 0.42)
        threshold = float(raw_threshold)
        if not (0.10 <= threshold <= 0.90):
            raise ValueError(f"Threshold {threshold} is outside authorized registry bounds [0.10, 0.90].")
    except (ValueError, TypeError) as th_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Invalid threshold parameter: {th_err}",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_PARAMETER",
                "message": str(th_err)
            }
        }

    # 6. Model Loading & Inference Execution
    model = None
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        model = SiameseResNetChangeDetector(pretrained=True).to(device)
        model.eval()

        transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        t1_tensor = transform(t1_img).unsqueeze(0).to(device)
        t2_tensor = transform(t2_img).unsqueeze(0).to(device)

        with torch.inference_mode():
            dist_map = model(t1_tensor, t2_tensor)

        dist_np = dist_map.squeeze().cpu().numpy()
        d_min, d_max = dist_np.min(), dist_np.max()
        norm_dist = (dist_np - d_min) / (d_max - d_min + 1e-8)

        binary_mask = (norm_dist >= threshold).astype(np.uint8)
        total_pixels = int(binary_mask.size)
        changed_pixels = int(np.sum(binary_mask))
        change_pct = round((changed_pixels / total_pixels) * 100.0, 2)

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        # Generate 3-panel evidence composite visualization
        out_dir = os.path.join("docs", "results")
        os.makedirs(out_dir, exist_ok=True)
        visualization_path = os.path.join(out_dir, "change_detection_execution_artifact.jpg")
        render_evidence_composite(t1_img, t2_img, binary_mask, visualization_path)

        answer = (
            f"Bi-temporal change detection detected {changed_pixels:,} changed pixels ({change_pct:.2f}% of scene area) "
            f"between T1 and T2 at differential distance threshold {threshold:.2f} (Controlled synthetic temporal evaluation pair)."
        )

        evidence_dict = {
            "type": "differential_heatmap_mask_composite",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "model": CHANGE_MODEL_ID,
            "threshold": threshold,
            "total_pixels": total_pixels,
            "changed_pixels": changed_pixels,
            "change_percentage": change_pct,
            "dimensions": {"width": w1, "height": h1},
            "annotated_artifact": visualization_path,
            "dataset_note": "Controlled synthetic temporal pair; not an operational accuracy benchmark.",
            "latency_ms": latency_ms,
        }

        return {
            "status": "SUCCESS",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": answer,
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": threshold,
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "change_percentage": change_pct,
            "confidence": round(1.0 - (changed_pixels / total_pixels), 4) if total_pixels > 0 else 1.0,
            "latency_ms": latency_ms,
            "evidence": [evidence_dict],
            "evidence_reference": "differential_heatmap_mask_composite",
            "metadata": {
                "threshold": threshold,
                "total_pixels": total_pixels,
                "changed_pixels": changed_pixels,
                "change_percentage": change_pct,
                "image_reference_t1": image_path,
                "image_reference_t2": second_image_path,
                "data_classification": "Controlled synthetic temporal pair",
            }
        }

    except Exception as exec_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "CHANGE_DETECTION",
            "model": CHANGE_MODEL_ID,
            "answer": f"Change detection execution error: {exec_err}",
            "image_reference_t1": image_path,
            "image_reference_t2": second_image_path,
            "threshold": None,
            "changed_pixels": 0,
            "total_pixels": 0,
            "change_percentage": 0.0,
            "confidence": None,
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
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
