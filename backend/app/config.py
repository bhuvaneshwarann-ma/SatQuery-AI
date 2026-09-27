"""Shared local deployment limits and absolute storage paths."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
ARTIFACT_DIR = PROJECT_ROOT / "data" / "artifacts"
SAMPLE_DIR = PROJECT_ROOT / "data" / "samples"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_IMAGE_PIXELS = 4_000_000
MAX_QUERY_CHARS = 4000
MAX_PENDING_REQUESTS = 4
DEFAULT_CHANGE_THRESHOLD = float(os.environ.get("DEFAULT_CHANGE_THRESHOLD", "0.30"))
if not 0.1 <= DEFAULT_CHANGE_THRESHOLD <= 0.9:
    raise ValueError("DEFAULT_CHANGE_THRESHOLD must be between 0.10 and 0.90")
