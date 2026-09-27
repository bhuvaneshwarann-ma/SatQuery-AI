"""Explicit generated-file retention. Dry-run by default; never follows symlinks."""
import argparse
import re
import time
from .app.config import ARTIFACT_DIR, UPLOAD_DIR


def expired_files(days: int):
    if days < 1:
        raise ValueError("Retention must be at least one day")
    cutoff = time.time() - days * 86400
    pattern = re.compile(r"(?:grounding_|change_detection_|optical_sar_)?[a-f0-9]{32}\.(?:jpg|jpeg|png|tif|tiff)")
    for root in [ARTIFACT_DIR, UPLOAD_DIR]:
        if not root.exists():
            continue
        for path in root.iterdir():
            if path.is_symlink() or not path.is_file() or not pattern.fullmatch(path.name):
                continue
            if path.resolve().parent == root.resolve() and path.stat().st_mtime < cutoff:
                yield path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older-than-days", type=int, default=30)
    parser.add_argument("--apply", action="store_true", help="Delete eligible generated artifacts/uploads")
    args = parser.parse_args()
    for path in expired_files(args.older_than_days):
        print(f"{'Deleting' if args.apply else 'Would delete'} {path}")
        if args.apply:
            path.unlink()
