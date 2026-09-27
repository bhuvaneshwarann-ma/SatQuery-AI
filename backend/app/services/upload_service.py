"""Bounded staging and confinement to approved local image directories."""
from pathlib import Path
from uuid import uuid4
from PIL import Image
from fastapi import UploadFile
from ..config import UPLOAD_DIR, SAMPLE_DIR, PROJECT_ROOT, MAX_UPLOAD_BYTES, MAX_IMAGE_PIXELS

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

def validate_image(path: Path) -> None:
    if path.suffix.lower() not in ALLOWED_EXTENSIONS or not path.is_file():
        raise ValueError("Expected a supported image file.")
    if path.stat().st_size > MAX_UPLOAD_BYTES:
        raise ValueError("Image exceeds the 20 MiB limit.")
    if path.suffix.lower() in {".tif", ".tiff"}:
        from .raster_input_service import read_raster
        read_raster(path)
        return
    with Image.open(path) as img:
        if img.width * img.height > MAX_IMAGE_PIXELS:
            raise ValueError("Image exceeds the 4 million pixel limit; crop or tile it first.")
        img.verify()

def resolve_sample_path(value: str | None) -> str | None:
    if not value:
        return None
    path = Path(value)
    path = (PROJECT_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(SAMPLE_DIR.resolve()):
        raise ValueError("Direct paths are restricted to bundled data/samples images. Upload other images.")
    try:
        validate_image(path)
    except Exception as exc:
        raise ValueError(f"Invalid sample image: {exc}") from exc
    return str(path)

def save_upload_file(upload_file: UploadFile) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = Path(upload_file.filename or "upload.jpg")
    if name.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file extension.")
    path = UPLOAD_DIR / f"{uuid4().hex}{name.suffix.lower()}"
    try:
        size = 0
        with path.open("wb") as out:
            while chunk := upload_file.file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise ValueError("Image exceeds the 20 MiB limit.")
                out.write(chunk)
        validate_image(path)
        return str(path)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise ValueError(f"Invalid image upload: {exc}") from exc

def cleanup_file(file_path: str | None) -> None:
    if file_path:
        path = Path(file_path).resolve()
        if path.is_relative_to(UPLOAD_DIR.resolve()):
            path.unlink(missing_ok=True)
