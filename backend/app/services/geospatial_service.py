"""
SatQuery AI — Geospatial & Multi-Raster Validation Service (Phase 8 & 9)
Provides rigorous geospatial raster inspection, metadata extraction,
cross-raster spatial footprint & CRS compatibility verification,
and non-destructive preview rendering for GeoTIFF, TIFF, PNG, and JPEG.
"""

import os
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image
from PIL.TiffTags import TAGS

try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    HAS_TIFFFILE = False


class GeospatialValidationError(Exception):
    """Exception raised when geospatial validation or compatibility checks fail."""
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


def extract_raster_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extracts comprehensive raster properties and geospatial metadata.
    Supports GeoTIFF/TIFF, PNG, JPEG, and multispectral rasters.
    """
    if not os.path.exists(file_path):
        raise GeospatialValidationError(
            f"Raster file not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            details={"path": file_path}
        )

    meta: Dict[str, Any] = {
        "file_path": file_path,
        "filename": os.path.basename(file_path),
        "file_size_bytes": os.path.getsize(file_path),
        "format": None,
        "width": 0,
        "height": 0,
        "bands": 1,
        "dtype": "unknown",
        "is_geotiff": False,
        "crs": None,
        "epsg": None,
        "bounds": None,
        "pixel_resolution": None,
        "affine_transform": None,
        "nodata": None,
        "acquisition_date": None,
        "sensor": None,
    }

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".tif", ".tiff", ".geotiff"]:
        meta["format"] = "GeoTIFF"
        _extract_geotiff_metadata(file_path, meta)
    elif ext in [".png", ".jpg", ".jpeg"]:
        meta["format"] = "PNG" if ext == ".png" else "JPEG"
        _extract_standard_image_metadata(file_path, meta)
    else:
        # Attempt PIL inspection for unfamiliar extensions
        try:
            with Image.open(file_path) as img:
                meta["format"] = img.format
                meta["width"], meta["height"] = img.size
                meta["bands"] = len(img.getbands())
        except Exception as e:
            raise GeospatialValidationError(
                f"Unsupported or unreadable raster format for '{file_path}': {e}",
                error_code="UNSUPPORTED_FORMAT",
                details={"extension": ext, "error": str(e)}
            )

    return meta


def _extract_geotiff_metadata(file_path: str, meta: Dict[str, Any]):
    """Extracts GeoTIFF specific metadata using tifffile and PIL fallback."""
    # Attempt tifffile first if available
    if HAS_TIFFFILE:
        try:
            with tifffile.TiffFile(file_path) as tf:
                page = tf.pages[0]
                meta["width"] = int(page.imagewidth)
                meta["height"] = int(page.imagelength)
                meta["bands"] = int(page.samplesperpixel)
                meta["dtype"] = str(page.dtype)

                # Check GeoTIFF tags
                # 33550: ModelPixelScaleTag
                # 33922: ModelTiepointTag
                # 34264: ModelTransformationTag
                # 34735: GeoKeyDirectoryTag
                geotags = {}
                for tag in page.tags:
                    if tag.code in [33550, 33922, 34264, 34735, 34736, 34737, 306, 50844]:
                        geotags[tag.code] = tag.value

                if any(key in geotags for key in [34735, 33922, 33550, 34264]):
                    meta["is_geotiff"] = True
                    _parse_geokeys(geotags, meta)
                return
        except Exception:
            pass

    # Fallback to PIL
    try:
        with Image.open(file_path) as img:
            meta["width"], meta["height"] = img.size
            meta["bands"] = len(img.getbands())
            meta["dtype"] = img.mode

            if hasattr(img, "tag_v2"):
                tags = img.tag_v2
                geotags = {code: tags[code] for code in [33550, 33922, 34264, 34735] if code in tags}
                if geotags:
                    meta["is_geotiff"] = True
                    _parse_geokeys(geotags, meta)
    except Exception as e:
        raise GeospatialValidationError(
            f"Failed to parse TIFF tags for '{file_path}': {e}",
            error_code="INVALID_TIFF",
            details={"error": str(e)}
        )


def _parse_geokeys(geotags: Dict[int, Any], meta: Dict[str, Any]):
    """Parses GeoKey Directory and Tiepoint/Scale tags to populate CRS and bounds."""
    # 33550: ModelPixelScaleTag [scale_x, scale_y, scale_z]
    scale = geotags.get(33550)
    # 33922: ModelTiepointTag [i, j, k, x, y, z]
    tiepoint = geotags.get(33922)

    if scale and len(scale) >= 2:
        meta["pixel_resolution"] = {
            "x": float(scale[0]),
            "y": float(scale[1]),
            "unit": "CRS units (not inferred)"
        }

    if tiepoint and scale and len(tiepoint) >= 6 and len(scale) >= 2:
        i, j, _, origin_x, origin_y, _ = tiepoint[:6]
        sx, sy = float(scale[0]), float(scale[1])
        w, h = meta["width"], meta["height"]

        min_x = origin_x - (i * sx)
        max_y = origin_y + (j * sy)
        max_x = min_x + (w * sx)
        min_y = max_y - (h * sy)

        meta["bounds"] = {
            "min_x": round(min_x, 6),
            "min_y": round(min_y, 6),
            "max_x": round(max_x, 6),
            "max_y": round(max_y, 6)
        }
        meta["affine_transform"] = [sx, 0.0, min_x, 0.0, -sy, max_y]

    matrix = geotags.get(34264)
    if matrix is not None and len(matrix) == 16:
        a, b, c = float(matrix[0]), float(matrix[1]), float(matrix[3])
        d, e, f = float(matrix[4]), float(matrix[5]), float(matrix[7])
        meta["affine_transform"] = [a, b, c, d, e, f]
        points = [(a*x+b*y+c, d*x+e*y+f) for x,y in
                  [(0,0),(meta["width"],0),(0,meta["height"]),(meta["width"],meta["height"])]]
        meta["bounds"] = dict(min_x=min(x for x,y in points), max_x=max(x for x,y in points),
                              min_y=min(y for x,y in points), max_y=max(y for x,y in points))

    # Parse GeoKeyDirectoryTag (34735) for ProjectedCSTypeGeoKey (3072) or GeographicTypeGeoKey (2048)
    geokey_dir = geotags.get(34735)
    if geokey_dir and len(geokey_dir) >= 4:
        # Standard GeoKey header: [KeyDirectoryVersion, KeyRevision, MinorRevision, NumberOfKeys]
        num_keys = geokey_dir[3]
        for k in range(num_keys):
            idx = 4 + k * 4
            if idx + 3 < len(geokey_dir):
                key_id = geokey_dir[idx]
                key_val = geokey_dir[idx + 3]
                if key_id == 3072:  # ProjectedCSTypeGeoKey
                    meta["epsg"] = int(key_val)
                    meta["crs"] = f"EPSG:{key_val} (Projected)"
                elif key_id == 2048 and meta["epsg"] is None:  # GeographicTypeGeoKey
                    meta["epsg"] = int(key_val)
                    meta["crs"] = f"EPSG:{key_val} (Geographic)"


def _extract_standard_image_metadata(file_path: str, meta: Dict[str, Any]):
    """Extracts standard image dimensions, channels, and simulated grid spacing."""
    try:
        with Image.open(file_path) as img:
            meta["width"], meta["height"] = img.size
            meta["bands"] = len(img.getbands())
            meta["dtype"] = img.mode
            meta["is_geotiff"] = False
            meta["crs"] = "LocalPixelGrid"
            meta["bounds"] = {
                "min_x": 0.0,
                "min_y": 0.0,
                "max_x": float(meta["width"]),
                "max_y": float(meta["height"])
            }
            meta["pixel_resolution"] = {"x": 1.0, "y": 1.0, "unit": "pixels"}
    except Exception as e:
        raise GeospatialValidationError(
            f"Failed to read image file '{file_path}': {e}",
            error_code="INVALID_IMAGE",
            details={"error": str(e)}
        )


def validate_pair_compatibility(
    raster_a_path: str, raster_b_path: str, task_name: str = "CHANGE_DETECTION",
    tolerance_ratio: float = 1e-6,
) -> Dict[str, Any]:
    """Require identical geographic grids, or explicitly report unknown alignment."""
    a, b = extract_raster_metadata(raster_a_path), extract_raster_metadata(raster_b_path)
    if (a["width"], a["height"]) != (b["width"], b["height"]):
        raise GeospatialValidationError("Spatial raster dimension mismatch; co-register inputs first.", "DIMENSION_MISMATCH")
    verified = False
    if a["is_geotiff"] or b["is_geotiff"]:
        if not all(m.get("epsg") and m.get("affine_transform") for m in [a,b]):
            raise GeospatialValidationError("Both geospatial inputs need complete CRS and transform metadata.", "INCOMPLETE_GEOREFERENCE")
        if a["epsg"] != b["epsg"]:
            raise GeospatialValidationError("CRS mismatch; reproject to the same CRS before analysis.", "CRS_MISMATCH")
        ta, tb = a["affine_transform"], b["affine_transform"]
        pixel_size = max(math.hypot(ta[0], ta[3]), math.hypot(ta[1], ta[4]))
        if pixel_size <= 0 or not all(math.isfinite(v) for v in ta+tb):
            raise GeospatialValidationError("Invalid geographic transform.", "INVALID_TRANSFORM")
        if any(not math.isclose(x,y,rel_tol=0,abs_tol=pixel_size*tolerance_ratio) for x,y in zip(ta,tb)):
            raise GeospatialValidationError("Grid origin, resolution or rotation mismatch; resample to the same grid.", "GRID_MISMATCH")
        verified = True
    return {
        "status": "COMPATIBLE" if verified else "PIXEL_DIMENSIONS_MATCH",
        "task": task_name,
        "raster_a": a,
        "raster_b": b,
        "co_registered": True if verified else None,
        "spatial_overlap_percentage": 100.0 if verified else None,
        "warning": None if verified else "Geographic alignment is unknown. Equal dimensions do not verify co-registration.",
    }


def generate_raster_preview(
    raster_path: str,
    output_preview_path: str,
    rgb_bands: Tuple[int, int, int] = (0, 1, 2),
    percentile_min: float = 2.0,
    percentile_max: float = 98.0
) -> str:
    """
    Renders a non-destructive, contrast-normalized RGB preview for visual UI display.
    Handles multispectral rasters, 16-bit uint GeoTIFFs, and single-band SAR without altering the source raster.
    """
    os.makedirs(os.path.dirname(output_preview_path), exist_ok=True)

    # If already standard 8-bit PNG/JPEG, return direct copy or load
    ext = os.path.splitext(raster_path)[1].lower()
    if ext in [".png", ".jpg", ".jpeg"]:
        with Image.open(raster_path) as img:
            rgb = img.convert("RGB")
            rgb.save(output_preview_path, "JPEG", quality=90)
        return output_preview_path

    # Process TIFF / GeoTIFF / Multispectral
    arr: Optional[np.ndarray] = None
    if HAS_TIFFFILE:
        try:
            arr = tifffile.imread(raster_path)
        except Exception:
            arr = None

    if arr is None:
        with Image.open(raster_path) as img:
            arr = np.array(img)

    if arr is None or arr.size == 0:
        raise GeospatialValidationError(
            f"Failed to read raster array for preview: {raster_path}",
            error_code="PREVIEW_GENERATION_FAILED"
        )

    # Normalize shapes: ensure (H, W) or (H, W, C)
    if arr.ndim == 2:
        # Single band (e.g. SAR or grayscale)
        p_lo = np.percentile(arr, percentile_min)
        p_hi = np.percentile(arr, percentile_max)
        norm = np.clip((arr - p_lo) / max(p_hi - p_lo, 1e-6), 0, 1) * 255.0
        preview_img = Image.fromarray(norm.astype(np.uint8), mode="L").convert("RGB")
    elif arr.ndim == 3:
        # Channels might be first (C, H, W) or last (H, W, C)
        if arr.shape[0] < arr.shape[2]:
            arr = np.transpose(arr, (1, 2, 0))
        
        num_c = arr.shape[2]
        b0 = min(rgb_bands[0], num_c - 1)
        b1 = min(rgb_bands[1], num_c - 1)
        b2 = min(rgb_bands[2], num_c - 1)

        rgb_stack = []
        for b_idx in [b0, b1, b2]:
            channel = arr[:, :, b_idx].astype(np.float32)
            p_lo = np.percentile(channel, percentile_min)
            p_hi = np.percentile(channel, percentile_max)
            norm_c = np.clip((channel - p_lo) / max(p_hi - p_lo, 1e-6), 0, 1) * 255.0
            rgb_stack.append(norm_c.astype(np.uint8))

        preview_np = np.stack(rgb_stack, axis=-1)
        preview_img = Image.fromarray(preview_np, mode="RGB")
    else:
        raise GeospatialValidationError(
            f"Unsupported array dimensions ({arr.ndim}D) for preview generation.",
            error_code="INVALID_DIMENSIONS"
        )

    preview_img.save(output_preview_path, "JPEG", quality=90)
    return output_preview_path
