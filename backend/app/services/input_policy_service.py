"""Enforce evaluation formats and preserve source provenance before preview conversion."""
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from .raster_input_service import render_raster
from .geospatial_service import extract_raster_metadata, validate_pair_compatibility, GeospatialValidationError
from ..config import PROJECT_ROOT, UPLOAD_DIR


def image_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def approved_benchmark_hashes():
    # Explicit catalog; never trust a user's dataset-name claim as verification.
    catalog = PROJECT_ROOT / "data" / "approved_benchmark_assets.json"
    if not catalog.is_file():
        return {}
    return json.loads(catalog.read_text(encoding="utf-8"))


def prepare_inputs(resolved, metadata, strict, staged):
    if not isinstance(metadata, dict):
        raise ValueError("Input metadata must be a JSON object.")
    if resolved.get("second_image_path") and resolved.get("sar_image_path"):
        raise ValueError("Choose either a temporal pair or an optical/SAR pair for one analysis.")
    prepared, provenance, compatibility = dict(resolved), {}, {}
    for pair_key in ("second_image_path", "sar_image_path"):
        primary = resolved.get("optical_image_path") or resolved.get("image_path")
        if primary and resolved.get(pair_key):
            try:
                check = validate_pair_compatibility(primary, resolved[pair_key])
            except GeospatialValidationError as exc:
                raise ValueError(exc.message) from exc
            compatibility[pair_key] = check
            if strict and check.get("warning"):
                # Public benchmark pairs may be registered without geospatial tags.
                catalog = approved_benchmark_hashes()
                first = catalog.get(image_hash(primary), {})
                second = catalog.get(image_hash(resolved[pair_key]), {})
                if not (first.get("pair_id") and first.get("pair_id") == second.get("pair_id") and
                        first.get("registered") is True and second.get("registered") is True):
                    raise ValueError("Evaluation mode requires matching geospatial grids or a verified registered benchmark pair.")
    for key, path in resolved.items():
        if not path:
            continue
        options = metadata.get(key, {})
        if not isinstance(options, dict):
            raise ValueError(f"Metadata for {key} must be an object.")
        digest = image_hash(path)
        benchmark = approved_benchmark_hashes().get(digest)
        ext = Path(path).suffix.lower()
        if strict and ext in {".jpg", ".jpeg", ".png"} and not benchmark:
            raise ValueError("Evaluation mode accepts PNG/JPEG only when their file hash is in the approved benchmark catalog.")
        modality = options.get("modality", "sar" if key == "sar_image_path" else "optical")
        if modality not in {"sar", "optical", "multispectral"}:
            raise ValueError("Modality must be optical, multispectral, or sar.")
        if key == "sar_image_path" and modality != "sar":
            raise ValueError("The SAR input must have SAR modality.")
        provenance[key] = {"sha256": digest, "declared_metadata": options,
                           "metadata_verification": "benchmark catalog" if benchmark else "user declared; not independently verified",
                           "benchmark": benchmark, "raster": extract_raster_metadata(path)}
        if ext in {".tif", ".tiff"}:
            preview = UPLOAD_DIR / f"{uuid4().hex}.png"
            staged.append(str(preview))
            provenance[key]["conversion"] = render_raster(path, preview, options.get("rgb_bands"), modality)
            prepared[key] = str(preview)
    return prepared, {"inputs": provenance, "original_pair_compatibility": compatibility,
                      "input_policy": "evaluation" if strict else "exploration"}
