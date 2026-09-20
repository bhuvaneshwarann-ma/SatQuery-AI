"""
SatQuery AI — Optical + SAR Paired Analysis Specialist Executor (Phase 5D)
Wraps dual-stream multi-sensor feature ingestion and cross-modal statistics engine in an isolated interface.
Enforces multi-sensor input validation, cross-modal telemetry extraction, proxy/real SAR classification,
and GPU memory cleanup.
"""

import os
import time
import gc
import traceback
from typing import Dict, Any, Optional
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


OPTICAL_SAR_MODEL_ID = "Dual-Stream Multi-Sensor Feature Ingestion & Cross-Modal Statistics Engine"


def classify_sar_modality(sar_path: str) -> str:
    """
    Classifies SAR input asset to explicitly distinguish proxy/simulated radar from spaceborne SAR.
    """
    path_lower = sar_path.lower()
    if "proxy" in path_lower or "synthetic" in path_lower:
        return "proxy_sar"
    elif "sentinel" in path_lower or "terrasar" in path_lower or "radarsat" in path_lower or "nisar" in path_lower:
        return "spaceborne_sar"
    return "proxy_sar" if "sample_satellite_port_proxy_sar" in path_lower else "unverified_sar"


def render_optical_sar_composite(
    optical_img: Image.Image,
    sar_img: Image.Image,
    fusion_overlay: np.ndarray,
    output_path: str,
    sar_classification: str,
):
    """
    Renders a 3-panel evidence visualization:
    Panel 1: Optical RGB Satellite Imagery (Landsat 9)
    Panel 2: SAR Microwave Backscatter (Grayscale with speckle)
    Panel 3: Cross-Modal Synergy (Cyan = Optical base, Magenta = SAR high-backscatter structures)
    """
    w, h = optical_img.size
    banner_h = 40
    composite = Image.new("RGB", (w * 3, h + banner_h), color=(18, 22, 28))
    draw = ImageDraw.Draw(composite)
    font = ImageFont.load_default()

    sar_rgb = sar_img.convert("RGB")
    fusion_img = Image.fromarray(fusion_overlay)

    composite.paste(optical_img, (0, banner_h))
    composite.paste(sar_rgb, (w, banner_h))
    composite.paste(fusion_img, (w * 2, banner_h))

    sar_tag = "[PROXY]" if sar_classification == "proxy_sar" else "[REAL]"
    draw.text((20, 12), "PANEL 1: Optical RGB", fill=(255, 255, 255), font=font)
    draw.text((w + 20, 12), f"PANEL 2: SAR Microwave Backscatter {sar_tag}", fill=(200, 200, 200), font=font)
    draw.text((w * 2 + 20, 12), "PANEL 3: Cross-Modal Synergy (Magenta = Radar Echoes)", fill=(255, 105, 180), font=font)

    draw.line([(w, 0), (w, h + banner_h)], fill=(60, 65, 75), width=2)
    draw.line([(w * 2, 0), (w * 2, h + banner_h)], fill=(60, 65, 75), width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    composite.save(output_path, "JPEG", quality=92)


def run_optical_sar(
    optical_image_path: str,
    sar_image_path: Optional[str] = None,
    query: Optional[str] = None,
    permitted_parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes cross-modal paired analysis between an optical image and a SAR image.

    Args:
        optical_image_path: Filesystem path to the optical image.
        sar_image_path: Filesystem path to the SAR image.
        query: Optional user natural language analytical question.
        permitted_parameters: Whitelisted parameter dictionary from Agent Router.

    Returns:
        Structured result dictionary conforming to Phase 5D contract.
    """
    t_start = time.perf_counter()
    params = permitted_parameters or {}

    # 1. Input Validation: Optical Image Path
    if not optical_image_path or not os.path.exists(optical_image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Optical image file not found / does not exist: {optical_image_path}",
            "optical_image_reference": optical_image_path or "",
            "sar_image_reference": sar_image_path or "",
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "IMAGE_NOT_FOUND",
                "message": f"Optical image file does not exist: {optical_image_path}"
            }
        }

    # 2. Input Validation: SAR Image Path
    if not sar_image_path or not os.path.exists(sar_image_path):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"SAR image file not found / does not exist: {sar_image_path}",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path or "",
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "IMAGE_NOT_FOUND",
                "message": f"SAR image file does not exist: {sar_image_path}"
            }
        }

    # 3. Input Readability & Integrity Verification
    opt_img = None
    sar_img = None
    try:
        with Image.open(optical_image_path) as img:
            img.verify()
        opt_img = Image.open(optical_image_path).convert("RGB")
    except Exception as opt_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Unable to read optical image: {optical_image_path}. File is corrupted or unreadable: {opt_err}",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_IMAGE",
                "message": f"Unable to read optical image: {optical_image_path}. Details: {opt_err}"
            }
        }

    try:
        with Image.open(sar_image_path) as img:
            img.verify()
        sar_img = Image.open(sar_image_path).convert("L")
    except Exception as sar_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Unable to read SAR image: {sar_image_path}. File is corrupted or unreadable: {sar_err}",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_IMAGE",
                "message": f"Unable to read SAR image: {sar_image_path}. Details: {sar_err}"
            }
        }

    # 4. Dimension Compatibility Check
    w_opt, h_opt = opt_img.size
    w_sar, h_sar = sar_img.size
    if (w_opt, h_opt) != (w_sar, h_sar):
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Dimension mismatch: Optical is {w_opt}x{h_opt}, SAR is {w_sar}x{h_sar}. Images must be coregistered.",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "DIMENSION_MISMATCH",
                "message": f"Dimension mismatch: Optical={w_opt}x{h_opt}, SAR={w_sar}x{h_sar}"
            }
        }

    # 5. Parameter Validation: high_scatter_threshold
    try:
        raw_threshold = params.get("high_scatter_threshold", 180.0)
        high_scatter_threshold = float(raw_threshold)
        if not (100.0 <= high_scatter_threshold <= 250.0):
            raise ValueError(f"high_scatter_threshold {high_scatter_threshold} is outside authorized registry bounds [100.0, 250.0].")
    except (ValueError, TypeError) as th_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Invalid high_scatter_threshold parameter: {th_err}",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": "unknown",
            "confidence": None,
            "latency_ms": latency_ms,
            "evidence": [],
            "evidence_reference": None,
            "metadata": {
                "error_type": "INVALID_PARAMETER",
                "message": str(th_err)
            }
        }

    # 6. Modality Classification
    sar_classification = classify_sar_modality(sar_image_path)

    # 7. Cross-Modal Analysis on GPU/CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    opt_tensor = None
    sar_tensor = None

    try:
        opt_tensor = torch.from_numpy(np.array(opt_img, dtype=np.float32)).to(device)
        sar_tensor = torch.from_numpy(np.array(sar_img, dtype=np.float32)).to(device)

        # Optical luminance statistics
        opt_luminance = 0.299 * opt_tensor[:, :, 0] + 0.587 * opt_tensor[:, :, 1] + 0.114 * opt_tensor[:, :, 2]
        opt_mean = round(float(opt_luminance.mean().cpu()), 2)
        opt_std = round(float(opt_luminance.std().cpu()), 2)
        opt_min = round(float(opt_luminance.min().cpu()), 2)
        opt_max = round(float(opt_luminance.max().cpu()), 2)

        # SAR backscatter statistics
        sar_mean = round(float(sar_tensor.mean().cpu()), 2)
        sar_std = round(float(sar_tensor.std().cpu()), 2)
        sar_min = round(float(sar_tensor.min().cpu()), 2)
        sar_max = round(float(sar_tensor.max().cpu()), 2)

        # Approximate dB backscatter
        min_db = round(float(20.0 * np.log10(max(sar_min, 1.0) / 255.0) - 5.0), 1)
        max_db = round(float(20.0 * np.log10(max(sar_max, 1.0) / 255.0) - 5.0), 1)

        # High-backscatter radar targets
        high_scatter_mask = sar_tensor > high_scatter_threshold
        high_scatter_count = int(high_scatter_mask.sum().cpu())
        total_pixels = w_opt * h_opt
        high_scatter_pct = round((high_scatter_count / total_pixels) * 100.0, 2)

        # Cross-modal correlation (Pearson r between optical luminance and radar backscatter)
        opt_flat = opt_luminance.flatten()
        sar_flat = sar_tensor.flatten()
        opt_centered = opt_flat - opt_flat.mean()
        sar_centered = sar_flat - sar_flat.mean()
        cov = (opt_centered * sar_centered).sum()
        std_prod = torch.sqrt((opt_centered ** 2).sum() * (sar_centered ** 2).sum()) + 1e-8
        pearson_r = round(float((cov / std_prod).cpu()), 3)

        # Radar-dominant structural anomalies (high radar backscatter but low optical reflectance)
        radar_dominant_mask = (sar_tensor > high_scatter_threshold) & (opt_luminance < 130.0)
        radar_dominant_count = int(radar_dominant_mask.sum().cpu())

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        # 8. Render Composite Evidence Overlay
        opt_np = np.array(opt_img)
        sar_np = np.array(sar_img)
        fusion_overlay = opt_np.copy()
        high_sar_bool = sar_np > high_scatter_threshold
        fusion_overlay[high_sar_bool] = (
            0.45 * fusion_overlay[high_sar_bool] + 0.55 * np.array([255, 20, 147], dtype=np.float32)
        ).astype(np.uint8)

        out_dir = os.path.join("docs", "results")
        os.makedirs(out_dir, exist_ok=True)
        vis_path = os.path.join(out_dir, "optical_sar_execution_artifact.jpg")
        render_optical_sar_composite(opt_img, sar_img, fusion_overlay, vis_path, sar_classification)

        classification_note = (
            "proxy_sar (simulated radar backscatter; not genuine co-registered spaceborne SAR)"
            if sar_classification == "proxy_sar" else sar_classification
        )

        answer = (
            f"Optical-SAR analysis complete: Optical Mean={opt_mean:.2f} (Std={opt_std:.2f}), "
            f"SAR Mean={sar_mean:.2f} (Std={sar_std:.2f}, Est. dB: [{min_db}, {max_db}]). "
            f"Identified {high_scatter_count:,} high-backscatter pixels ({high_scatter_pct:.2f}%) "
            f"at threshold {high_scatter_threshold:.1f}. "
            f"Cross-modal Pearson r = {pearson_r:.3f}, Radar-dominant anomalies = {radar_dominant_count:,} pixels. "
            f"Data Classification: {classification_note}."
        )

        evidence_dict = {
            "type": "optical_sar_synergy_overlay",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": sar_classification,
            "optical_dimensions": {"width": w_opt, "height": h_opt},
            "sar_dimensions": {"width": w_sar, "height": h_sar},
            "optical_stats": {"mean": opt_mean, "std": opt_std, "min": opt_min, "max": opt_max},
            "sar_stats": {"mean": sar_mean, "std": sar_std, "min_db": min_db, "max_db": max_db},
            "high_backscatter_count": high_scatter_count,
            "high_backscatter_percentage": high_scatter_pct,
            "cross_modal_correlation": pearson_r,
            "radar_dominant_anomalies": radar_dominant_count,
            "annotated_artifact": vis_path,
            "high_scatter_threshold": high_scatter_threshold,
            "latency_ms": latency_ms,
        }

        return {
            "status": "SUCCESS",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": answer,
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": sar_classification,
            "optical_dimensions": {"width": w_opt, "height": h_opt},
            "sar_dimensions": {"width": w_sar, "height": h_sar},
            "optical_mean": opt_mean,
            "optical_std": opt_std,
            "sar_mean": sar_mean,
            "sar_std": sar_std,
            "high_backscatter_count": high_scatter_count,
            "high_backscatter_percentage": high_scatter_pct,
            "cross_modal_correlation": pearson_r,
            "radar_dominant_anomalies": radar_dominant_count,
            "confidence": 1.0,
            "latency_ms": latency_ms,
            "evidence": [evidence_dict],
            "evidence_reference": "optical_sar_synergy_overlay",
            "metadata": {
                "optical_image_reference": optical_image_path,
                "sar_image_reference": sar_image_path,
                "sar_data_classification": sar_classification,
                "optical_dimensions": {"width": w_opt, "height": h_opt},
                "sar_dimensions": {"width": w_sar, "height": h_sar},
                "optical_mean": opt_mean,
                "optical_std": opt_std,
                "sar_mean": sar_mean,
                "sar_std": sar_std,
                "high_backscatter_count": high_scatter_count,
                "high_backscatter_percentage": high_scatter_pct,
                "cross_modal_correlation": pearson_r,
                "radar_dominant_anomalies": radar_dominant_count,
                "high_scatter_threshold": high_scatter_threshold,
            }
        }

    except Exception as exec_err:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return {
            "status": "ERROR",
            "tool": "OPTICAL_SAR",
            "model": OPTICAL_SAR_MODEL_ID,
            "answer": f"Optical-SAR execution error: {exec_err}",
            "optical_image_reference": optical_image_path,
            "sar_image_reference": sar_image_path,
            "sar_data_classification": sar_classification if 'sar_classification' in locals() else "unknown",
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
        if opt_tensor is not None:
            del opt_tensor
        if sar_tensor is not None:
            del sar_tensor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
