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
PUBLIC_DEPLOYMENT = os.environ.get("PUBLIC_DEPLOYMENT", "false").lower() == "true"
PUBLIC_API_KEY = os.environ.get("SATQUERY_API_KEY", "")
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "12"))
ARTIFACT_RETENTION_HOURS = int(os.environ.get("ARTIFACT_RETENTION_HOURS", "72"))
if PUBLIC_DEPLOYMENT and len(PUBLIC_API_KEY) < 32:
    raise ValueError("SATQUERY_API_KEY must contain at least 32 characters in PUBLIC_DEPLOYMENT mode")
DEFAULT_CHANGE_THRESHOLD = float(os.environ.get("DEFAULT_CHANGE_THRESHOLD", "0.30"))
if not 0.1 <= DEFAULT_CHANGE_THRESHOLD <= 0.9:
    raise ValueError("DEFAULT_CHANGE_THRESHOLD must be between 0.10 and 0.90")
