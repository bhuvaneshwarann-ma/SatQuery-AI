"""
SatQuery AI — File Upload & Asset Staging Service (Phase 7A)
Provides secure, collision-free local storage for multipart satellite image uploads.
Validates file extensions, inspects image binary integrity, and rejects unsupported or executable formats.
"""

import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile
from PIL import Image


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/uploads"))


def ensure_upload_dir() -> str:
    """Ensures local uploads directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def save_upload_file(upload_file: UploadFile) -> str:
    """
    Saves an uploaded file to a collision-safe local path after security & format validation.

    Args:
        upload_file: FastAPI UploadFile instance.

    Returns:
        Absolute path to the validated saved image on disk.

    Raises:
        ValueError: If file extension is unsupported or binary data cannot be verified as an image.
    """
    ensure_upload_dir()

    filename = upload_file.filename or "upload.jpg"
    _, ext = os.path.splitext(filename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '{ext}'. Allowed image extensions: {sorted(list(ALLOWED_EXTENSIONS))}"
        )

    # Generate collision-safe filename preserving sanitized original base stem
    stem, ext = os.path.splitext(filename.lower())
    clean_stem = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in stem)[:32]
    safe_filename = f"{clean_stem}_{uuid.uuid4().hex[:12]}{ext}"
    target_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save to disk
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # Verify binary image integrity using Pillow
    try:
        with Image.open(target_path) as img:
            img.verify()
    except Exception as err:
        if os.path.exists(target_path):
            os.remove(target_path)
        raise ValueError(f"Uploaded file is corrupted or not a valid raster image: {err}")

    return target_path


def cleanup_file(file_path: Optional[str]) -> None:
    """Safely removes a temporary file from disk if present."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
