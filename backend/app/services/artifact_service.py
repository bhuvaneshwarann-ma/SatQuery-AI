"""Immutable, opaque result artifacts; never overwrite prior evidence."""
from uuid import uuid4
from ..config import ARTIFACT_DIR


def new_artifact_path(tool: str, suffix: str = ".jpg") -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    return str(ARTIFACT_DIR / f"{tool}_{uuid4().hex}{suffix}")
