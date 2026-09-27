"""Retention cleanup for generated evidence artifacts."""
import time
from .config import ARTIFACT_DIR, ARTIFACT_RETENTION_HOURS


def cleanup_expired_artifacts() -> int:
    cutoff = time.time() - ARTIFACT_RETENTION_HOURS * 3600
    removed = 0
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    for path in ARTIFACT_DIR.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            removed += 1
    return removed
